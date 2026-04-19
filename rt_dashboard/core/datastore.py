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
        self.cpu_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.ram_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.disk_history: deque[float] = deque([0.0] * n, maxlen=n)  # MB/s
        self.net_sent_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.net_recv_history:  deque[float] = deque([0.0] * n, maxlen=n)
        self.eth_total_history: deque[float] = deque([0.0] * n, maxlen=n)
        self.wifi_total_history: deque[float] = deque([0.0] * n, maxlen=n)

        # GPU snapshot (best-effort; may be empty)
        self.gpus: list[dict] = []
        self.cpu_name: str = "CPU"

        # Latest snapshot values
        self.cpu_percent:    float = 0.0
        self.ram_total:      float = 0.0
        self.ram_used:       float = 0.0
        self.ram_percent:    float = 0.0
        self.disk_read_rate: float = 0.0   # MB/s
        self.disk_write_rate:float = 0.0   # MB/s
        self.disk_total_rate:float = 0.0   # MB/s (read+write)
        self.disk_space_used:float = 0.0   # GB (for sub text)
        self.disk_space_total:float = 0.0  # GB
        self.net_sent_rate:  float = 0.0   # KB/s
        self.net_recv_rate:  float = 0.0   # KB/s
        self.eth_usage_pct: float = 0.0
        self.wifi_usage_pct: float = 0.0
        self.eth_sent_rate: float = 0.0
        self.eth_recv_rate: float = 0.0
        self.wifi_sent_rate: float = 0.0
        self.wifi_recv_rate: float = 0.0
        self.eth_adapter_name: str = "Ethernet"
        self.wifi_adapter_name: str = "Wi-Fi"

        # Process list
        self.processes: list[dict] = []

        # Previous counters for delta calculation
        self._prev_net_sent: int | None = None
        self._prev_net_recv: int | None = None
        self._prev_disk_read:  int | None = None
        self._prev_disk_write: int | None = None

    def lock(self):
        return self._lock

    def push_performance(
        self, cpu, ram_total, ram_used, ram_pct,
        disk_read_bytes, disk_write_bytes,
        disk_space_used, disk_space_total,
        net_sent_bytes, net_recv_bytes,
        cpu_name: str | None = None,
        eth_usage_pct: float | None = None,
        wifi_usage_pct: float | None = None,
        eth_sent_rate: float | None = None,
        eth_recv_rate: float | None = None,
        wifi_sent_rate: float | None = None,
        wifi_recv_rate: float | None = None,
        eth_adapter_name: str | None = None,
        wifi_adapter_name: str | None = None,
        gpus: list[dict] | None = None,
    ):
        with self._lock:
            self.cpu_percent  = cpu
            self.ram_total    = ram_total
            self.ram_used     = ram_used
            self.ram_percent  = ram_pct
            self.disk_space_used  = disk_space_used
            self.disk_space_total = disk_space_total

            # Disk I/O rate (MB/s)
            if self._prev_disk_read is not None:
                self.disk_read_rate  = (disk_read_bytes - self._prev_disk_read) / (1024**2)
                self.disk_write_rate = (disk_write_bytes - self._prev_disk_write) / (1024**2)
                self.disk_total_rate = self.disk_read_rate + self.disk_write_rate
            self._prev_disk_read  = disk_read_bytes
            self._prev_disk_write = disk_write_bytes

            # Network rate (KB/s)
            if self._prev_net_sent is not None:
                self.net_sent_rate = (net_sent_bytes - self._prev_net_sent) / 1024
                self.net_recv_rate = (net_recv_bytes - self._prev_net_recv) / 1024
            self._prev_net_sent = net_sent_bytes
            self._prev_net_recv = net_recv_bytes

            if cpu_name:
                self.cpu_name = cpu_name
            if eth_usage_pct is not None:
                self.eth_usage_pct = max(0.0, min(100.0, eth_usage_pct))
            if wifi_usage_pct is not None:
                self.wifi_usage_pct = max(0.0, min(100.0, wifi_usage_pct))
            if eth_sent_rate is not None:
                self.eth_sent_rate = max(0.0, eth_sent_rate)
            if eth_recv_rate is not None:
                self.eth_recv_rate = max(0.0, eth_recv_rate)
            if wifi_sent_rate is not None:
                self.wifi_sent_rate = max(0.0, wifi_sent_rate)
            if wifi_recv_rate is not None:
                self.wifi_recv_rate = max(0.0, wifi_recv_rate)
            if eth_adapter_name:
                self.eth_adapter_name = eth_adapter_name
            if wifi_adapter_name:
                self.wifi_adapter_name = wifi_adapter_name

            # Rolling history
            self.cpu_history.append(cpu)
            self.ram_history.append(ram_pct)
            self.disk_history.append(self.disk_total_rate)
            self.net_sent_history.append(self.net_sent_rate)
            self.net_recv_history.append(self.net_recv_rate)
            self.eth_total_history.append(self.eth_sent_rate + self.eth_recv_rate)
            self.wifi_total_history.append(self.wifi_sent_rate + self.wifi_recv_rate)

            if gpus is not None:
                self.gpus = gpus

    def push_processes(self, proc_list: list[dict]):
        with self._lock:
            self.processes = proc_list
