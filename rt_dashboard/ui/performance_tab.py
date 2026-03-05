# ─── Performance Tab ─────────────────────────────────────────────────
# Live rolling graphs for CPU, RAM, Disk, Network with summary stats.

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt

from core.datastore import DataStore
from config import DARK, LIGHT, HISTORY_LENGTH


class MetricCard(QFrame):
    """A card containing a graph and summary text for one metric."""

    def __init__(self, title: str, color: str, unit: str = "%",
                 max_y: float = 100.0, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._color = color
        self._unit = unit
        self._max_y = max_y

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Title row
        top_row = QHBoxLayout()
        self._title_label = QLabel(title)
        self._title_label.setObjectName("cardTitle")
        top_row.addWidget(self._title_label)
        top_row.addStretch()

        self._value_label = QLabel("0" + unit)
        self._value_label.setObjectName("cardValue")
        top_row.addWidget(self._value_label)
        layout.addLayout(top_row)

        # Graph
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(None)
        self._plot_widget.setFixedHeight(130)
        self._plot_widget.showGrid(x=False, y=True, alpha=0.15)
        self._plot_widget.hideButtons()
        self._plot_widget.setMenuEnabled(False)
        self._plot_widget.setMouseEnabled(x=False, y=False)
        self._plot_widget.getPlotItem().hideAxis("bottom")
        self._plot_widget.getPlotItem().hideAxis("left")
        self._plot_widget.setYRange(0, max_y, padding=0.05)
        self._plot_widget.setXRange(0, HISTORY_LENGTH, padding=0)

        pen = pg.mkPen(color=color, width=2)
        self._curve = self._plot_widget.plot([], [], pen=pen)

        # Fill under curve
        self._fill = pg.FillBetweenItem(
            self._curve,
            pg.PlotDataItem([0], [0]),
            brush=pg.mkBrush(color + "30"),
        )
        self._plot_widget.addItem(self._fill)

        layout.addWidget(self._plot_widget)

        # Sub text
        self._sub_label = QLabel("")
        self._sub_label.setObjectName("cardSub")
        layout.addWidget(self._sub_label)

    def update_data(self, history, value_text: str, sub_text: str):
        data = list(history)
        x = np.arange(len(data))
        y = np.array(data, dtype=float)
        self._curve.setData(x, y)

        # Rebuild fill
        self._plot_widget.removeItem(self._fill)
        baseline = pg.PlotDataItem(x, np.zeros(len(x)))
        self._fill = pg.FillBetweenItem(
            self._curve, baseline,
            brush=pg.mkBrush(self._color + "25"),
        )
        self._plot_widget.addItem(self._fill)

        self._value_label.setText(value_text)
        self._sub_label.setText(sub_text)

    def update_colors(self, color: str):
        self._color = color
        pen = pg.mkPen(color=color, width=2)
        self._curve.setPen(pen)


class PerformanceTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._is_dark = True
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Section title
        header = QLabel("📊  System Performance")
        header.setStyleSheet("font-size:18px; font-weight:700; padding:4px 0;")
        layout.addWidget(header)

        # 2×2 grid of cards
        grid = QGridLayout()
        grid.setSpacing(14)

        colors = DARK  # default, updated on theme switch

        self._cpu_card = MetricCard("CPU Usage", colors["graph_cpu"], "%", 100)
        self._ram_card = MetricCard("Memory Usage", colors["graph_ram"], "%", 100)
        self._disk_card = MetricCard("Disk Usage", colors["graph_disk"], "%", 100)
        self._net_card = MetricCard("Network I/O", colors["graph_net"], " KB/s", 1000)

        grid.addWidget(self._cpu_card, 0, 0)
        grid.addWidget(self._ram_card, 0, 1)
        grid.addWidget(self._disk_card, 1, 0)
        grid.addWidget(self._net_card, 1, 1)

        layout.addLayout(grid, 1)

    # ── Public refresh ────────────────────────────────────────────────

    def refresh(self):
        s = self._store

        with s.lock():
            cpu_hist = list(s.cpu_history)
            ram_hist = list(s.ram_history)
            disk_hist = list(s.disk_history)
            net_s_hist = list(s.net_sent_history)
            net_r_hist = list(s.net_recv_history)

            cpu_pct   = s.cpu_percent
            ram_used  = s.ram_used
            ram_total = s.ram_total
            ram_pct   = s.ram_percent
            disk_used  = s.disk_used
            disk_total = s.disk_total
            disk_pct   = s.disk_percent
            net_s      = s.net_sent_rate
            net_r      = s.net_recv_rate

        self._cpu_card.update_data(
            cpu_hist,
            f"{cpu_pct:.1f}%",
            "Overall CPU utilisation",
        )
        self._ram_card.update_data(
            ram_hist,
            f"{ram_pct:.1f}%",
            f"{ram_used:.1f} GB / {ram_total:.1f} GB used",
        )
        self._disk_card.update_data(
            disk_hist,
            f"{disk_pct:.1f}%",
            f"{disk_used:.1f} GB / {disk_total:.1f} GB used",
        )

        # Network: combined view
        combined = [a + b for a, b in zip(net_s_hist, net_r_hist)]
        self._net_card.update_data(
            combined,
            f"↑ {net_s:.0f}  ↓ {net_r:.0f} KB/s",
            f"Send + Receive",
        )

        # Auto-scale network Y axis
        peak = max(max(combined, default=1), 1) * 1.2
        self._net_card._plot_widget.setYRange(0, peak, padding=0.05)

    # ── Theme switch ──────────────────────────────────────────────────

    def apply_theme(self, is_dark: bool):
        self._is_dark = is_dark
        c = DARK if is_dark else LIGHT
        self._cpu_card.update_colors(c["graph_cpu"])
        self._ram_card.update_colors(c["graph_ram"])
        self._disk_card.update_colors(c["graph_disk"])
        self._net_card.update_colors(c["graph_net"])
