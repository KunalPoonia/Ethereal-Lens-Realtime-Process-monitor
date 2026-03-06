# ─── Poller ──────────────────────────────────────────────────────────
# QThread that reads system metrics via psutil every POLL_INTERVAL_MS.

import ctypes
import ctypes.wintypes
import psutil
from PyQt6.QtCore import QThread, pyqtSignal
from config import POLL_INTERVAL_MS
from core.datastore import DataStore

# Windows API for detecting visible windows
user32 = ctypes.windll.user32


def _has_visible_window(pid: int) -> bool:
    """Check if a process has at least one visible top-level window."""
    found = [False]

    def enum_callback(hwnd, _lParam):
        if not user32.IsWindowVisible(hwnd):
            return True
        # Get the PID that owns this window
        win_pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(win_pid))
        if win_pid.value == pid:
            # Check that the window has a non-empty title (real app window)
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                found[0] = True
                return False  # stop enumerating
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
    )
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return found[0]


class Poller(QThread):
    """Background thread that polls psutil and pushes data into the store."""

    data_ready = pyqtSignal()  # emitted after each poll cycle

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._running = True
        self._tick = 0

    # ── Main loop ─────────────────────────────────────────────────────

    def run(self):
        while self._running:
            self._poll_performance()
            # Poll processes every 2 seconds to reduce CPU load
            if self._tick % 2 == 0:
                self._poll_processes()
            self._tick += 1
            self.data_ready.emit()
            self.msleep(POLL_INTERVAL_MS)

    def stop(self):
        self._running = False
        self.wait()

    # ── Performance snapshot ──────────────────────────────────────────

    def _poll_performance(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        self._store.push_performance(
            cpu=cpu,
            ram_total=ram.total / (1024 ** 3),       # GB
            ram_used=ram.used / (1024 ** 3),
            ram_pct=ram.percent,
            disk_total=disk.total / (1024 ** 3),
            disk_used=disk.used / (1024 ** 3),
            disk_pct=disk.percent,
            net_sent_bytes=net.bytes_sent,
            net_recv_bytes=net.bytes_recv,
        )

    # ── Process list snapshot ─────────────────────────────────────────

    def _poll_processes(self):
        apps = []
        background = []
        for p in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_info", "status", "username"]
        ):
            try:
                info = p.info
                entry = {
                    "pid":    info["pid"],
                    "name":   info["name"] or "",
                    "cpu":    info["cpu_percent"] or 0.0,
                    "memory": round((info["memory_info"].rss / (1024 ** 2)), 1)
                             if info["memory_info"] else 0.0,
                    "status": info["status"] or "",
                    "user":   (info["username"] or "").split("\\")[-1],
                }
                # Classify: App if it has a visible window
                if _has_visible_window(info["pid"]):
                    entry["category"] = "app"
                    apps.append(entry)
                else:
                    entry["category"] = "background"
                    background.append(entry)
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess, OSError):
                continue
        self._store.push_processes(apps + background)
