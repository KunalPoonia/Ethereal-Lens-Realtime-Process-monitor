# ─── Dashboard Tab — System Overview ────────────────────────────────
# Clean dashboard with circular gauges and stat cards

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from core.datastore import DataStore
from ui.components.glass_card import GlassCard
from config import DARK, LIGHT


class CircularProgress(QWidget):
    """Minimal circular progress indicator"""

    def __init__(self, color, size=100, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._color = QColor(color)
        self.setFixedSize(size, size)

        self._anim = QPropertyAnimation(self, b"value")
        self._anim.setDuration(500)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = max(0.0, min(100.0, val))
        self.update()

    def set_value(self, val):
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(val)
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center = QPointF(width / 2, height / 2)
        radius = min(width, height) / 2 - 8

        # Background track
        track_color = QColor(self._color)
        track_color.setAlpha(20)
        painter.setPen(QPen(track_color, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(center, radius, radius)

        # Progress arc
        if self._value > 0:
            painter.setPen(QPen(self._color, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            start_angle = 90 * 16
            span_angle = -int((self._value / 100.0) * 360 * 16)
            rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
            painter.drawArc(rect, start_angle, span_angle)

        # Center text
        painter.setPen(QColor("#c8cad0"))
        font = QFont("Segoe UI Variable", 20, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self._value)}%")


class HeroCard(GlassCard):
    """Metric card with circular gauge"""

    def __init__(self, title, color, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setStyleSheet("font-size: 12px; font-weight: 600; letter-spacing: 0.5px;")
        layout.addWidget(title_label)

        # Circular progress
        self._progress = CircularProgress(color, 90)
        prog_container = QHBoxLayout()
        prog_container.addStretch()
        prog_container.addWidget(self._progress)
        prog_container.addStretch()
        layout.addLayout(prog_container)

        # Subtitle
        self._subtitle = QLabel("")
        self._subtitle.setObjectName("cardSub")
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._subtitle)

        layout.addStretch()

    def update_value(self, value, subtitle=""):
        self._progress.set_value(value)
        self._subtitle.setText(subtitle)


class StatCard(GlassCard):
    """Small stat card"""

    def __init__(self, title, color="#6e7baa", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        # Value
        self._value = QLabel("—")
        self._value.setStyleSheet(f"font-size: 24px; font-weight: 500; color: {color};")
        layout.addWidget(self._value)

        # Subtitle
        self._subtitle = QLabel("")
        self._subtitle.setObjectName("cardSub")
        layout.addWidget(self._subtitle)

    def update(self, value, subtitle=""):
        self._value.setText(str(value))
        self._subtitle.setText(subtitle)


class DashboardTab(QWidget):
    """System overview dashboard"""

    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        # Title
        title = QLabel("System Overview")
        title.setStyleSheet("font-size: 18px; font-weight: 600; background: transparent;")
        layout.addWidget(title)

        # Hero cards grid
        hero_grid = QGridLayout()
        hero_grid.setSpacing(14)

        c = DARK
        self._cpu_hero = HeroCard("CPU", c["graph_cpu"])
        self._ram_hero = HeroCard("MEMORY", c["graph_ram"])
        self._disk_hero = HeroCard("DISK", c["graph_disk"])
        self._net_hero = HeroCard("NETWORK", c["graph_net"])

        hero_grid.addWidget(self._cpu_hero, 0, 0)
        hero_grid.addWidget(self._ram_hero, 0, 1)
        hero_grid.addWidget(self._disk_hero, 1, 0)
        hero_grid.addWidget(self._net_hero, 1, 1)

        layout.addLayout(hero_grid, 2)

        # Quick stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(14)

        self._uptime_card = StatCard("System Uptime", c["graph_cpu"])
        self._processes_card = StatCard("Active Processes", c["graph_ram"])
        self._threads_card = StatCard("Threads", c["graph_net"])

        stats_layout.addWidget(self._uptime_card)
        stats_layout.addWidget(self._processes_card)
        stats_layout.addWidget(self._threads_card)

        layout.addLayout(stats_layout, 1)

        layout.addStretch()

    def refresh(self):
        with self._store.lock():
            cpu = self._store.cpu_percent
            ram = self._store.ram_percent
            ram_used = self._store.ram_used
            ram_total = self._store.ram_total
            disk_percent = (self._store.disk_space_used / self._store.disk_space_total * 100) if self._store.disk_space_total > 0 else 0
            disk_used = self._store.disk_space_used
            disk_total = self._store.disk_space_total
            net_sent = self._store.net_sent_rate
            net_recv = self._store.net_recv_rate
            processes = list(self._store.processes)

        self._cpu_hero.update_value(cpu, f"{cpu:.1f}% utilization")
        self._ram_hero.update_value(ram, f"{ram_used:.1f} / {ram_total:.1f} GB")
        self._disk_hero.update_value(disk_percent, f"{disk_used:.0f} / {disk_total:.0f} GB")

        net_total = net_sent + net_recv
        net_percent = min(100, (net_total / 10000) * 100)
        self._net_hero.update_value(net_percent, f"↑ {net_sent:.0f}  ↓ {net_recv:.0f} KB/s")

        import psutil
        import datetime

        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            uptime_str = f"{days}d {hours}h"
        else:
            uptime_str = f"{hours}h {minutes}m"

        self._uptime_card.update(uptime_str, f"Since {boot_time.strftime('%b %d, %H:%M')}")

        total_threads = sum(p.get('threads', 0) for p in processes)
        self._processes_card.update(len(processes), f"{total_threads} threads")
        self._threads_card.update(total_threads, f"Across {len(processes)} processes")
