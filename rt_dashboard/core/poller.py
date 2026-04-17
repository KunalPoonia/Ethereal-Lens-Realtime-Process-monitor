# ─── Poller ──────────────────────────────────────────────────────────
# Background threads for stats and process polling.
# Process enumeration runs in a child process to avoid GIL blocking.

import ctypes
import ctypes.wintypes
import multiprocessing as mp
import psutil
import time
import threading
import queue
from config import POLL_INTERVAL_MS
from core.datastore import DataStore

# ─── Windows API setup ───────────────────────────────────────────────

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
)

PROC_POLL_INTERVAL = 2.0  # seconds between process polls

# Pretty names for common processes (matched against lowercase stem)
_DISPLAY_NAMES = {
    "brave":    "Brave Browser",
    "spotify":  "Spotify",
    "code":     "VS Code",
    "explorer": "Windows Explorer",
    "taskmgr":  "Task Manager",
}


def _get_windowed_pids() -> set:
    """Return PIDs that own a visible, titled window."""
    pids = set()

    def _cb(hwnd, _):
        if user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            pids.add(pid.value)
        return True

    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return pids


def _display_name(raw: str) -> str:
    """Strip .exe and apply friendly name overrides."""
    stem = raw[:-4] if raw.lower().endswith(".exe") else raw
    return _DISPLAY_NAMES.get(stem.lower(), stem)


# ═══════════════════════════════════════════════════════════════════════
#  Stats Poller
# ═══════════════════════════════════════════════════════════════════════

class StatsPoller(threading.Thread):
    """Polls CPU / RAM / Disk / Net stats on a fixed interval."""

    def __init__(self, store: DataStore):
        super().__init__(daemon=True)
        self._store   = store
        self._running = True
        psutil.cpu_percent(interval=None)  # prime the counter

    def run(self):
        interval = POLL_INTERVAL_MS / 1000.0
        while self._running:
            try:
                cpu        = psutil.cpu_percent(interval=None)
                ram        = psutil.virtual_memory()
                disk_space = psutil.disk_usage("/")
                disk_io    = psutil.disk_io_counters()
                net        = psutil.net_io_counters()
                self._store.push_performance(
                    cpu,
                    ram.total / 1024 ** 3,
                    ram.used  / 1024 ** 3,
                    ram.percent,
                    disk_io.read_bytes,
                    disk_io.write_bytes,
                    disk_space.used  / 1024 ** 3,
                    disk_space.total / 1024 ** 3,
                    net.bytes_sent,
                    net.bytes_recv,
                )
            except Exception:
                pass
            time.sleep(interval)

    def stop(self):
        self._running = False
        self.join(timeout=2.0)


# ═══════════════════════════════════════════════════════════════════════
#  Process Worker  (runs in a child process)
# ═══════════════════════════════════════════════════════════════════════

def _proc_worker(q: mp.Queue, stop_event: mp.Event) -> None:
    """Collect and group processes, then push to queue. Runs in child process."""
    num_cores = psutil.cpu_count(logical=True) or 1

    while not stop_event.is_set():
        t0 = time.monotonic()
        try:
            windowed = _get_windowed_pids()
            groups   = {}

            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "status", "num_threads"]
            ):
                if stop_event.is_set():
                    return
                try:
                    info = proc.info
                    raw  = info["name"]
                    if not raw or not raw.strip():
                        continue

                    name   = _display_name(raw)
                    cpu    = (info["cpu_percent"] or 0.0) / num_cores
                    pid    = info["pid"]
                    status = info["status"] or ""

                    # Prefer USS (matches Task Manager); fall back to RSS
                    mem = 0.0
                    if info["memory_info"]:
                        try:
                            mem = proc.memory_full_info().uss / 1024 ** 2
                        except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                            mem = info["memory_info"].rss / 1024 ** 2

                    if name not in groups:
                        groups[name] = {
                            "name":     name,
                            "cpu":      0.0,
                            "memory":   0.0,
                            "threads":  0,
                            "pids":     set(),
                            "status":   status,
                            "category": "background",
                        }

                    g = groups[name]
                    g["cpu"]     += cpu
                    g["memory"]  += mem
                    g["threads"] += info["num_threads"] or 0
                    g["pids"].add(pid)

                    if pid in windowed:
                        g["category"] = "app"

                except (psutil.NoSuchProcess, psutil.AccessDenied,
                        psutil.ZombieProcess, OSError):
                    continue

            result = []
            for g in groups.values():
                g["cpu"]    = round(g["cpu"],    1)
                g["memory"] = round(g["memory"], 1)
                g["pid"]    = min(g["pids"])           # stable across polls
                g["pids"]   = list(g["pids"])          # JSON-serialisable
                result.append(g)

            # Apps first, then background processes
            result.sort(key=lambda x: (x["category"] != "app", x["name"].lower()))

            if not q.full():
                q.put(result)

        except Exception:
            pass

        elapsed   = time.monotonic() - t0
        remaining = max(0.1, PROC_POLL_INTERVAL - elapsed)
        stop_event.wait(timeout=remaining)


# ═══════════════════════════════════════════════════════════════════════
#  Process Poller
# ═══════════════════════════════════════════════════════════════════════

class ProcessPoller(threading.Thread):
    """Reads from the child-process queue and pushes updates to DataStore."""

    def __init__(self, store: DataStore):
        super().__init__(daemon=True)
        self._store      = store
        self._running    = True
        self._queue      = mp.Queue(maxsize=2)
        self._stop_event = mp.Event()
        self._child      = None

    def run(self):
        self._child = mp.Process(
            target=_proc_worker,
            args=(self._queue, self._stop_event),
            daemon=True,
        )
        self._child.start()

        while self._running:
            try:
                procs = self._queue.get(timeout=0.25)
                self._store.push_processes(procs)
            except queue.Empty:
                pass
            except Exception:
                pass

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._child and self._child.is_alive():
            self._child.join(timeout=2.0)
            if self._child.is_alive():
                self._child.terminate()
        self.join(timeout=2.0)


# ═══════════════════════════════════════════════════════════════════════
#  Combined Poller  (public API)
# ═══════════════════════════════════════════════════════════════════════

class Poller:
    """Starts and stops both the stats and process pollers."""

    def __init__(self, store: DataStore):
        self._stats   = StatsPoller(store)
        self._process = ProcessPoller(store)

    def start(self):
        self._stats.start()
        self._process.start()

    def stop(self):
        self._stats.stop()
        self._process.stop()
