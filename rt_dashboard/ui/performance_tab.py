# ─── Performance Tab ──────────────────────────────────────────────────
# Apple-clean performance dashboard.
# Big numbers, understated labels, smooth sparklines, generous whitespace.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QFont


class SparklineWidget(QWidget):
    """Minimal sparkline — single-pixel line, subtle fill."""

    def __init__(self, color: str, fill_alpha: int = 10, parent=None):
        super().__init__(parent)
        self._data: list[float] = []
        self._color = QColor(color)
        self._fill_alpha = fill_alpha
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[float]):
        self._data = list(data)
        self.update()

    def paintEvent(self, event):
        if len(self._data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad = 1
        data = self._data
        mx = max(max(data), 0.1)
        n = len(data)
        dx = (w - 2 * pad) / max(n - 1, 1)

        # Build path
        path = QPainterPath()
        for i, v in enumerate(data):
            x = pad + i * dx
            y = h - pad - (v / mx) * (h - 2 * pad)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        # Line
        pen = QPen(self._color, 1.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

        # Fill
        fill = QPainterPath(path)
        fill.lineTo(pad + (n - 1) * dx, h - pad)
        fill.lineTo(pad, h - pad)
        fill.closeSubpath()
        fc = QColor(self._color)
        fc.setAlpha(self._fill_alpha)
        painter.fillPath(fill, fc)

        painter.end()


class PerfCard(QFrame):
    """Single metric card — title (uppercase), big value, subtext, sparkline."""

    def __init__(self, title: str, color: str, fill_alpha: int, theme: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("perfCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(2)

        # Title — small, uppercase, tracked out
        self._title = QLabel(title.upper())
        self._title.setObjectName("perfTitle")
        layout.addWidget(self._title)

        layout.addSpacing(4)

        # Value — large, light weight
        self._value = QLabel("—")
        self._value.setObjectName("perfValue")
        layout.addWidget(self._value)

        # Subtext — very small, muted
        self._subtext = QLabel("")
        self._subtext.setObjectName("perfSubtext")
        layout.addWidget(self._subtext)

        layout.addSpacing(8)

        # Sparkline
        self._sparkline = SparklineWidget(color, fill_alpha)
        layout.addWidget(self._sparkline, stretch=1)

    def update_data(self, value_text: str, sub_text: str, history: list[float]):
        self._value.setText(value_text)
        self._subtext.setText(sub_text)
        self._sparkline.set_data(history)


class PerformanceTab(QWidget):
    """Performance overview — four cards in a 2×2 grid."""

    def __init__(self, store, theme: dict, parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        # Title
        title = QLabel("Performance")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {self._theme['text']};
            letter-spacing: -0.3px;
            padding-bottom: 16px;
        """)
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(14)

        fill = self._theme.get("graph_fill", 10)

        self._cpu_card  = PerfCard("CPU",     self._theme["graph_cpu"],  fill, self._theme)
        self._mem_card  = PerfCard("Memory",  self._theme["graph_mem"],  fill, self._theme)
        self._disk_card = PerfCard("Disk",    self._theme["graph_disk"], fill, self._theme)
        self._net_card  = PerfCard("Network", self._theme["graph_net"],  fill, self._theme)

        grid.addWidget(self._cpu_card,  0, 0)
        grid.addWidget(self._mem_card,  0, 1)
        grid.addWidget(self._disk_card, 1, 0)
        grid.addWidget(self._net_card,  1, 1)

        layout.addLayout(grid, stretch=1)

    def refresh(self):
        with self._store.lock():
            cpu       = self._store.cpu_percent
            ram_used  = self._store.ram_used
            ram_total = self._store.ram_total
            ram_pct   = self._store.ram_percent
            disk_rate = self._store.disk_total_rate
            disk_used = self._store.disk_space_used
            disk_tot  = self._store.disk_space_total
            net_s     = self._store.net_sent_rate
            net_r     = self._store.net_recv_rate

            cpu_h  = list(self._store.cpu_history)
            ram_h  = list(self._store.ram_history)
            disk_h = list(self._store.disk_history)
            net_h  = [a + b for a, b in zip(
                self._store.net_sent_history, self._store.net_recv_history
            )]

        self._cpu_card.update_data(
            f"{cpu:.0f}%",
            "Utilization",
            cpu_h,
        )
        self._mem_card.update_data(
            f"{ram_pct:.0f}%",
            f"{ram_used:.1f} / {ram_total:.1f} GB",
            ram_h,
        )
        self._disk_card.update_data(
            f"{disk_rate:.1f} MB/s",
            f"{disk_used:.0f} / {disk_tot:.0f} GB",
            disk_h,
        )

        nt = net_s + net_r
        self._net_card.update_data(
            f"{nt:.0f} KB/s" if nt < 1024 else f"{nt/1024:.1f} MB/s",
            f"↑ {net_s:.0f}   ↓ {net_r:.0f} KB/s",
            net_h,
        )
