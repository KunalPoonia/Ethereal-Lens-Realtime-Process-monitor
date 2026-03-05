# ─── Poller ──────────────────────────────────────────────────────────
# QThread that reads system metrics via psutil every POLL_INTERVAL_MS.

import psutil
from PyQt6.QtCore import QThread, pyqtSignal
from config import POLL_INTERVAL_MS
from core.datastore import DataStore


class Poller(QThread):
    """Background thread that polls psutil and pushes data into the store."""

    data_ready = pyqtSignal()  # emitted after each poll cycle

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._running = True

    # ── Main loop ─────────────────────────────────────────────────────

    def run(self):
        while self._running:
            self._poll_performance()
            self._poll_processes()
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
        procs = []
        for p in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_info", "status", "username"]
        ):
            try:
                info = p.info
                procs.append({
                    "pid":    info["pid"],
                    "name":   info["name"] or "",
                    "cpu":    info["cpu_percent"] or 0.0,
                    "memory": round((info["memory_info"].rss / (1024 ** 2)), 1)
                             if info["memory_info"] else 0.0,
                    "status": info["status"] or "",
                    "user":   (info["username"] or "").split("\\")[-1],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        self._store.push_processes(procs)
