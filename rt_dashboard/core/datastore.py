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

        # Rolling graph history
        self.cpu_history       = deque([0.0] * n, maxlen=n)
        self.ram_history       = deque([0.0] * n, maxlen=n)
        self.disk_history      = deque([0.0] * n, maxlen=n)  # MB/s
        self.net_sent_history  = deque([0.0] * n, maxlen=n)
        self.net_recv_history  = deque([0.0] * n, maxlen=n)

        # Latest snapshot values
        self.cpu_percent       = 0.0
        self.ram_total         = 0.0
        self.ram_used          = 0.0
        self.ram_percent       = 0.0
        self.disk_read_rate    = 0.0   # MB/s
        self.disk_write_rate   = 0.0   # MB/s
        self.disk_total_rate   = 0.0   # MB/s (read + write)
        self.disk_space_used   = 0.0   # GB
        self.disk_space_total  = 0.0   # GB
        self.net_sent_rate     = 0.0   # KB/s
        self.net_recv_rate     = 0.0   # KB/s

        # Process list
        self.processes = []

        # Previous counters for delta calculation
        self._prev_net_sent   = None
        self._prev_net_recv   = None
        self._prev_disk_read  = None
        self._prev_disk_write = None

    def lock(self):
        return self._lock

    def push_performance(
        self, cpu, ram_total, ram_used, ram_pct,
        disk_read_bytes, disk_write_bytes,
        disk_space_used, disk_space_total,
        net_sent_bytes, net_recv_bytes,
    ):
        with self._lock:
            self.cpu_percent      = cpu
            self.ram_total        = ram_total
            self.ram_used         = ram_used
            self.ram_percent      = ram_pct
            self.disk_space_used  = disk_space_used
            self.disk_space_total = disk_space_total

            # Disk I/O rate (MB/s)
            if self._prev_disk_read is not None:
                self.disk_read_rate  = (disk_read_bytes  - self._prev_disk_read)  / 1024 ** 2
                self.disk_write_rate = (disk_write_bytes - self._prev_disk_write) / 1024 ** 2
                self.disk_total_rate = self.disk_read_rate + self.disk_write_rate
            self._prev_disk_read  = disk_read_bytes
            self._prev_disk_write = disk_write_bytes

            # Network rate (KB/s)
            if self._prev_net_sent is not None:
                self.net_sent_rate = (net_sent_bytes - self._prev_net_sent) / 1024
                self.net_recv_rate = (net_recv_bytes - self._prev_net_recv) / 1024
            self._prev_net_sent = net_sent_bytes
            self._prev_net_recv = net_recv_bytes

            # Rolling history
            self.cpu_history.append(cpu)
            self.ram_history.append(ram_pct)
            self.disk_history.append(self.disk_total_rate)
            self.net_sent_history.append(self.net_sent_rate)
            self.net_recv_history.append(self.net_recv_rate)

    def push_processes(self, proc_list: list):
        with self._lock:
            self.processes = proc_list
