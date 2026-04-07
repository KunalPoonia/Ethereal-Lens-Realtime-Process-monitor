# ─── Poller ──────────────────────────────────────────────────────────
# Optimised background threads — separate threads for stats and processes.
# Process enumeration runs in a child process to avoid GIL blocking.

import ctypes
import ctypes.wintypes
import multiprocessing as mp
import psutil
import time
from PyQt6.QtCore import QThread, pyqtSignal
from config import POLL_INTERVAL_MS
from core.datastore import DataStore

user32 = ctypes.windll.user32
WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
)


def _get_windowed_pids() -> set[int]:
    """Single EnumWindows pass → set of PIDs that own a visible titled window."""
    pids: set[int] = set()

    def _cb(hwnd, _lp):
        if user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            pids.add(pid.value)
        return True

    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return pids


# ═══════════════════════════════════════════════════════════════════════
#  Stats Poller (QThread with sleep loop)
# ═══════════════════════════════════════════════════════════════════════

class StatsPoller(QThread):
    """Polls CPU/RAM/Disk/Net stats every second."""
    stats_ready = pyqtSignal()

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._running = True
        psutil.cpu_percent(interval=None)  # prime

    def run(self):
        while self._running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                disk_space = psutil.disk_usage("/")
                disk_io = psutil.disk_io_counters()
                net = psutil.net_io_counters()
                self._store.push_performance(
                    cpu, ram.total / (1024**3), ram.used / (1024**3), ram.percent,
                    disk_io.read_bytes, disk_io.write_bytes,
                    disk_space.used / (1024**3), disk_space.total / (1024**3),
                    net.bytes_sent, net.bytes_recv,
                )
                self.stats_ready.emit()
            except Exception:
                pass
            self.msleep(POLL_INTERVAL_MS)

    def stop(self):
        self._running = False
        self.wait(2000)


# ═══════════════════════════════════════════════════════════════════════
#  Process Worker (runs in child process to avoid GIL blocking)
# ═══════════════════════════════════════════════════════════════════════

def _proc_worker(queue: mp.Queue, stop_event: mp.Event) -> None:
    """Runs in a child process. Collects process list and sends via queue."""
    PROC_POLL_INTERVAL = 2.0  # seconds between polls
    
    while not stop_event.is_set():
        t0 = time.monotonic()
        try:
            windowed = _get_windowed_pids()
            apps, bg = [], []
            
            for p in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "status", "username"]
            ):
                if stop_event.is_set():
                    return
                try:
                    info = p.info
                    name = info["name"] or ""
                    # Skip empty-named processes
                    if not name.strip():
                        continue
                    entry = {
                        "pid":    info["pid"],
                        "name":   name,
                        "cpu":    info["cpu_percent"] or 0.0,
                        "memory": round(info["memory_info"].rss / (1024**2), 1)
                                 if info["memory_info"] else 0.0,
                        "status": info["status"] or "",
                        "user":   (info["username"] or "").split("\\")[-1],
                    }
                    if info["pid"] in windowed:
                        entry["category"] = "app"
                        apps.append(entry)
                    else:
                        entry["category"] = "background"
                        bg.append(entry)
                except (psutil.NoSuchProcess, psutil.AccessDenied,
                        psutil.ZombieProcess, OSError):
                    continue
            
            if not queue.full():
                queue.put(apps + bg)
        except Exception:
            pass

        elapsed = time.monotonic() - t0
        remaining = max(0.1, PROC_POLL_INTERVAL - elapsed)
        stop_event.wait(timeout=remaining)


class ProcessPoller(QThread):
    """Thin QThread that reads from the child-process queue and emits a signal."""
    procs_ready = pyqtSignal()

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._running = True
        self._queue: mp.Queue = mp.Queue(maxsize=2)
        self._stop_event: mp.Event = mp.Event()
        self._child: mp.Process | None = None

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
                self.procs_ready.emit()
            except Exception:
                pass

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._child and self._child.is_alive():
            self._child.join(timeout=2)
            if self._child.is_alive():
                self._child.terminate()
        self.wait(2000)


# ═══════════════════════════════════════════════════════════════════════
#  Combined Poller (starts both sub-pollers)
# ═══════════════════════════════════════════════════════════════════════

class Poller(QThread):
    """Starts both stats and process pollers."""
    data_ready  = pyqtSignal()
    procs_ready = pyqtSignal()

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._stats_poller = StatsPoller(store)
        self._proc_poller = ProcessPoller(store)
        
        # Forward signals
        self._stats_poller.stats_ready.connect(self.data_ready.emit)
        self._proc_poller.procs_ready.connect(self.procs_ready.emit)

    def start(self):
        self._stats_poller.start()
        self._proc_poller.start()

    def stop(self):
        self._stats_poller.stop()
        self._proc_poller.stop()
