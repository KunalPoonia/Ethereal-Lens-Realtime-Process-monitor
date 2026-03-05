# ─── DataStore ───────────────────────────────────────────────────────
# Thread-safe shared state with rolling deque history for graphs.

from collections import deque
from threading import Lock
from config import HISTORY_LENGTH


class DataStore:
    """Centralised data container shared between the poller and the UI."""

    def __init__(self):
        n = HISTORY_LENGTH
        self._lock = Lock()

        # Rolling graph history (one value per second)
        self.cpu_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.ram_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.disk_history: deque[float] = deque([0.0] * n, maxlen=n)
        self.net_sent_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.net_recv_history:  deque[float] = deque([0.0] * n, maxlen=n)

        # Latest snapshot values
        self.cpu_percent:   float = 0.0
        self.ram_total:     float = 0.0
        self.ram_used:      float = 0.0
        self.ram_percent:   float = 0.0
        self.disk_total:    float = 0.0
        self.disk_used:     float = 0.0
        self.disk_percent:  float = 0.0
        self.net_sent_rate: float = 0.0   # KB/s
        self.net_recv_rate: float = 0.0   # KB/s

        # Process list (list of dicts)
        self.processes: list[dict] = []

        # Previous net counters for delta calculation
        self._prev_net_sent: int | None = None
        self._prev_net_recv: int | None = None

    # ── Thread-safe update helpers ────────────────────────────────────

    def lock(self):
        return self._lock

    def push_performance(
        self, cpu, ram_total, ram_used, ram_pct,
        disk_total, disk_used, disk_pct,
        net_sent_bytes, net_recv_bytes,
    ):
        """Called by the poller each tick."""
        with self._lock:
            self.cpu_percent  = cpu
            self.ram_total    = ram_total
            self.ram_used     = ram_used
            self.ram_percent  = ram_pct
            self.disk_total   = disk_total
            self.disk_used    = disk_used
            self.disk_percent = disk_pct

            # Calculate network rate (KB/s)
            if self._prev_net_sent is not None:
                self.net_sent_rate = (net_sent_bytes - self._prev_net_sent) / 1024
                self.net_recv_rate = (net_recv_bytes - self._prev_net_recv) / 1024
            self._prev_net_sent = net_sent_bytes
            self._prev_net_recv = net_recv_bytes

            # Append to rolling history
            self.cpu_history.append(cpu)
            self.ram_history.append(ram_pct)
            self.disk_history.append(disk_pct)
            self.net_sent_history.append(self.net_sent_rate)
            self.net_recv_history.append(self.net_recv_rate)

    def push_processes(self, proc_list: list[dict]):
        with self._lock:
            self.processes = proc_list
