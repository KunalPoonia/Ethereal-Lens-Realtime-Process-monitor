# ─── Poller ──────────────────────────────────────────────────────────
# Optimised background threads — separate threads for stats and processes.
# Process enumeration runs in a child process to avoid GIL blocking.

import ctypes
import ctypes.wintypes
import multiprocessing as mp
import platform
import subprocess
import psutil
import time
import threading
import queue
import winreg
from config import POLL_INTERVAL_MS
from core.datastore import DataStore
from core.gpu import get_gpus

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
#  Stats Poller (Standard Thread with sleep loop)
# ═══════════════════════════════════════════════════════════════════════

class StatsPoller(threading.Thread):
    """Polls CPU/RAM/Disk/Net stats every second."""

    def __init__(self, store: DataStore):
        super().__init__(daemon=True)
        self._store = store
        self._running = True
        self._cpu_name = self._detect_cpu_name()
        self._prev_nic_sent: dict[str, int] = {}
        self._prev_nic_recv: dict[str, int] = {}
        psutil.cpu_percent(interval=None)  # prime

    @staticmethod
    def _detect_cpu_name() -> str:
        # Most reliable on Windows: registry processor name string.
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                name = str(value).strip()
                if name:
                    return name
        except Exception:
            pass

        try:
            out = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=1.0,
            )
            name = (out or "").strip()
            if name:
                return name
        except Exception:
            pass

        try:
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "Name"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=1.0,
            )
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            names = [l for l in lines if l.lower() != "name"]
            if names:
                return names[0]
        except Exception:
            pass

        return (platform.processor() or "CPU").strip()

    @staticmethod
    def _classify_nic(name: str) -> str | None:
        n = (name or "").lower()
        if any(k in n for k in ["wi-fi", "wifi", "wlan", "wireless"]):
            return "wifi"
        if any(k in n for k in ["ethernet", "eth", "lan", "en"]):
            return "eth"
        return None

    def run(self):
        while self._running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                disk_space = psutil.disk_usage("/")
                disk_io = psutil.disk_io_counters()
                net = psutil.net_io_counters()
                pernic = psutil.net_io_counters(pernic=True)
                gpus = get_gpus()

                eth_sent_kb = 0.0
                eth_recv_kb = 0.0
                wifi_sent_kb = 0.0
                wifi_recv_kb = 0.0
                eth_adapter_name = "Ethernet"
                wifi_adapter_name = "Wi-Fi"
                best_eth_total = -1.0
                best_wifi_total = -1.0
                for nic_name, counters in pernic.items():
                    nic_type = self._classify_nic(nic_name)
                    if nic_type is None:
                        continue
                    prev_s = self._prev_nic_sent.get(nic_name)
                    prev_r = self._prev_nic_recv.get(nic_name)
                    self._prev_nic_sent[nic_name] = counters.bytes_sent
                    self._prev_nic_recv[nic_name] = counters.bytes_recv
                    if prev_s is None or prev_r is None:
                        continue
                    sent_kb = max(0.0, (counters.bytes_sent - prev_s) / 1024.0)
                    recv_kb = max(0.0, (counters.bytes_recv - prev_r) / 1024.0)
                    total_kb = sent_kb + recv_kb
                    if nic_type == "eth":
                        eth_sent_kb += sent_kb
                        eth_recv_kb += recv_kb
                        if total_kb > best_eth_total:
                            best_eth_total = total_kb
                            eth_adapter_name = nic_name
                    elif nic_type == "wifi":
                        wifi_sent_kb += sent_kb
                        wifi_recv_kb += recv_kb
                        if total_kb > best_wifi_total:
                            best_wifi_total = total_kb
                            wifi_adapter_name = nic_name

                # Percent usage heuristic (10,000 KB/s == 100%)
                eth_usage_pct = min(100.0, ((eth_sent_kb + eth_recv_kb) / 10000.0) * 100.0)
                wifi_usage_pct = min(100.0, ((wifi_sent_kb + wifi_recv_kb) / 10000.0) * 100.0)

                self._store.push_performance(
                    cpu, ram.total / (1024**3), ram.used / (1024**3), ram.percent,
                    disk_io.read_bytes, disk_io.write_bytes,
                    disk_space.used / (1024**3), disk_space.total / (1024**3),
                    net.bytes_sent, net.bytes_recv,
                    cpu_name=self._cpu_name,
                    eth_usage_pct=eth_usage_pct,
                    wifi_usage_pct=wifi_usage_pct,
                    eth_sent_rate=eth_sent_kb,
                    eth_recv_rate=eth_recv_kb,
                    wifi_sent_rate=wifi_sent_kb,
                    wifi_recv_rate=wifi_recv_kb,
                    eth_adapter_name=eth_adapter_name,
                    wifi_adapter_name=wifi_adapter_name,
                    gpus=gpus,
                )
            except Exception:
                pass
            time.sleep(POLL_INTERVAL_MS / 1000.0)

    def stop(self):
        self._running = False
        self.join(timeout=2.0)


# ═══════════════════════════════════════════════════════════════════════
#  Process Worker (runs in child process to avoid GIL blocking)
# ═══════════════════════════════════════════════════════════════════════

def _proc_worker(q: mp.Queue, stop_event: mp.Event) -> None:
    """Runs in a child process. Collects process list and sends via queue."""
    PROC_POLL_INTERVAL = 2.0  # seconds between polls
    num_cores = psutil.cpu_count(logical=True) or 1  # For normalizing per-process CPU
    
    while not stop_event.is_set():
        t0 = time.monotonic()
        try:
            windowed = _get_windowed_pids()
            groups = {}
            for p in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "status", "username", "num_threads"]
            ):
                if stop_event.is_set():
                    return
                try:
                    info = p.info
                    raw_name = info["name"]
                    if not raw_name or not raw_name.strip():
                        continue
                    
                    # Remove .exe extension for cleaner display matching Task Manager
                    name = raw_name
                    if name.lower().endswith('.exe'):
                        name = name[:-4]
                    
                    # Some stylistic capitalisation for common ones
                    if name.lower() == 'brave':
                        name = 'Brave Browser'
                    elif name.lower() == 'spotify':
                        name = 'Spotify'
                    elif name.lower() == 'code':
                        name = 'VS Code'
                    elif name.lower() == 'explorer':
                        name = 'Windows Explorer'
                    elif name.lower() == 'taskmgr':
                        name = 'Task Manager'

                    # Normalize CPU: psutil gives per-core %, divide by core count for whole-system %
                    cpu = (info["cpu_percent"] or 0.0) / num_cores
                    
                    # Use private working set (USS) to match Task Manager, fall back to RSS
                    mem = 0.0
                    if info["memory_info"]:
                        try:
                            mem = p.memory_full_info().uss / (1024**2)
                        except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                            mem = info["memory_info"].rss / (1024**2)
                    
                    threads = info["num_threads"] or 0
                    pid = info["pid"]
                    
                    if name not in groups:
                        groups[name] = {
                            "name": name,
                            "cpu": 0.0,
                            "memory": 0.0,
                            "threads": 0,
                            "pids": set(),
                            "status": info["status"] or "",
                            "category": "background"
                        }
                    
                    groups[name]["cpu"] += cpu
                    groups[name]["memory"] += mem
                    groups[name]["threads"] += threads
                    groups[name]["pids"].add(pid)
                    
                    if pid in windowed:
                        groups[name]["category"] = "app"
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied,
                        psutil.ZombieProcess, OSError):
                    continue
            
            apps = []
            bg = []
            for name, g in groups.items():
                g["memory"] = round(g["memory"], 1)
                g["cpu"] = round(g["cpu"], 1)
                
                # Pick the lowest PID consistently so selection stays stable across polls
                g["pid"] = min(g["pids"])
                g["pids"] = list(g["pids"])  # Convert set to list for JSON serialization
                
                if g["category"] == "app":
                    apps.append(g)
                else:
                    bg.append(g)
            
            if not q.full():
                q.put(apps + bg)
        except Exception:
            pass

        elapsed = time.monotonic() - t0
        remaining = max(0.1, PROC_POLL_INTERVAL - elapsed)
        stop_event.wait(timeout=remaining)


class ProcessPoller(threading.Thread):
    """Thin Thread that reads from the child-process queue and updates DataStore."""

    def __init__(self, store: DataStore):
        super().__init__(daemon=True)
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
#  Combined Poller (starts both sub-pollers)
# ═══════════════════════════════════════════════════════════════════════

class Poller:
    """Starts both stats and process pollers."""

    def __init__(self, store: DataStore):
        self._store = store
        self._stats_poller = StatsPoller(store)
        self._proc_poller = ProcessPoller(store)

    def start(self):
        self._stats_poller.start()
        self._proc_poller.start()

    def stop(self):
        self._stats_poller.stop()
        self._proc_poller.stop()
