# ─── Dashboard Tab — System Overview ────────────────────────────────
# Modern dashboard with hero cards, gauges, and quick stats

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush, QPainterPath

from core.datastore import DataStore
from ui.components.glass_card import GlassCard
from config import DARK, LIGHT


class CircularProgress(QWidget):
    """Circular progress indicator with gradient"""
    
    def __init__(self, color_start, color_end, size=120, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._color_start = QColor(color_start)
        self._color_end = QColor(color_end)
        self.setFixedSize(size, size)
        
        # Animation for smooth value changes
        self._anim = QPropertyAnimation(self, b"value")
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(float)
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = max(0.0, min(100.0, val))
        self.update()
    
    def set_value(self, val):
        """Animate to new value"""
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
        radius = min(width, height) / 2 - 10
        
        # Background circle
        painter.setPen(QPen(QColor("#ffffff10"), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(center, radius, radius)
        
        # Progress arc with gradient
        if self._value > 0:
            gradient = QLinearGradient(0, 0, width, height)
            gradient.setColorAt(0, self._color_start)
            gradient.setColorAt(1, self._color_end)
            
            pen = QPen(QBrush(gradient), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            # Draw arc (starts at top, clockwise)
            start_angle = 90 * 16  # Start at top
            span_angle = -int((self._value / 100.0) * 360 * 16)  # Negative for clockwise
            
            rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
            painter.drawArc(rect, start_angle, span_angle)
        
        # Center text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI Variable", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{int(self._value)}%")


class HeroCard(GlassCard):
    """Large hero card for primary metrics"""
    
    def __init__(self, title, color_start, color_end, icon="", parent=None):
        super().__init__(parent)
        self._title = title
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        
        # Title with icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px; background: transparent;")
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setStyleSheet("font-size: 13px; font-weight: 600; letter-spacing: 0.8px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Circular progress
        self._progress = CircularProgress(color_start, color_end, 100)
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
    """Small stat card for secondary metrics"""
    
    def __init__(self, title, icon="", color="#06b6d4", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        
        # Title
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px; background: transparent;")
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Value
        self._value = QLabel("—")
        self._value.setStyleSheet(f"font-size: 28px; font-weight: 600; color: {color};")
        layout.addWidget(self._value)
        
        # Subtitle
        self._subtitle = QLabel("")
        self._subtitle.setObjectName("cardSub")
        layout.addWidget(self._subtitle)
    
    def update(self, value, subtitle=""):
        self._value.setText(str(value))
        self._subtitle.setText(subtitle)


class DashboardTab(QWidget):
    """System overview dashboard with hero cards and quick stats"""
    
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("System Overview")
        title.setStyleSheet("font-size: 20px; font-weight: 600; background: transparent;")
        layout.addWidget(title)
        
        # Hero cards grid
        hero_grid = QGridLayout()
        hero_grid.setSpacing(20)
        
        self._cpu_hero = HeroCard("CPU", "#06b6d4", "#3b82f6", "🖥️")
        self._ram_hero = HeroCard("Memory", "#a855f7", "#ec4899", "💾")
        self._disk_hero = HeroCard("Disk", "#f59e0b", "#ef4444", "💿")
        self._net_hero = HeroCard("Network", "#10b981", "#06b6d4", "🌐")
        
        hero_grid.addWidget(self._cpu_hero, 0, 0)
        hero_grid.addWidget(self._ram_hero, 0, 1)
        hero_grid.addWidget(self._disk_hero, 1, 0)
        hero_grid.addWidget(self._net_hero, 1, 1)
        
        layout.addLayout(hero_grid, 2)
        
        # Quick stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self._uptime_card = StatCard("System Uptime", "⏱️", "#06b6d4")
        self._processes_card = StatCard("Active Processes", "📊", "#a855f7")
        self._threads_card = StatCard("Threads", "🧵", "#10b981")
        
        stats_layout.addWidget(self._uptime_card)
        stats_layout.addWidget(self._processes_card)
        stats_layout.addWidget(self._threads_card)
        
        layout.addLayout(stats_layout, 1)
        
        layout.addStretch()
    
    def refresh(self):
        """Update all dashboard metrics"""
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
        
        # Update hero cards
        self._cpu_hero.update_value(cpu, f"{cpu:.1f}% utilization")
        self._ram_hero.update_value(ram, f"{ram_used:.1f} / {ram_total:.1f} GB")
        self._disk_hero.update_value(disk_percent, f"{disk_used:.0f} / {disk_total:.0f} GB")
        
        net_total = net_sent + net_recv
        net_percent = min(100, (net_total / 10000) * 100)  # Scale to 10 MB/s = 100%
        self._net_hero.update_value(net_percent, f"↑ {net_sent:.0f} KB/s  ↓ {net_recv:.0f} KB/s")
        
        # Update stat cards
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
