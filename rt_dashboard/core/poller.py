# ─── Poller ──────────────────────────────────────────────────────────
# Optimised background thread — single EnumWindows pass for classification.

import ctypes
import ctypes.wintypes
import psutil
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


class Poller(QThread):
    data_ready  = pyqtSignal()        # performance tick
    procs_ready = pyqtSignal()        # process list tick (slower)

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._running = True
        self._tick = 0

    def run(self):
        while self._running:
            self._poll_performance()
            self.data_ready.emit()
            # Processes every 3 seconds to stay light
            if self._tick % 3 == 0:
                self._poll_processes()
                self.procs_ready.emit()
            self._tick += 1
            self.msleep(POLL_INTERVAL_MS)

    def stop(self):
        self._running = False
        self.wait()

    def _poll_performance(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        self._store.push_performance(
            cpu, ram.total / (1024**3), ram.used / (1024**3), ram.percent,
            disk.total / (1024**3), disk.used / (1024**3), disk.percent,
            net.bytes_sent, net.bytes_recv,
        )

    def _poll_processes(self):
        windowed = _get_windowed_pids()   # ONE call
        apps, bg = [], []
        for p in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_info", "status", "username"]
        ):
            try:
                info = p.info
                entry = {
                    "pid":    info["pid"],
                    "name":   info["name"] or "",
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
        self._store.push_processes(apps + bg)
