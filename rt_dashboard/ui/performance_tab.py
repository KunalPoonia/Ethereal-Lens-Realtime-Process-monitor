# ─── Performance Tab ─────────────────────────────────────────────────
# Minimalistic metric cards with live rolling graphs.

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame,
)
from PyQt6.QtCore import Qt

from core.datastore import DataStore
from config import DARK, LIGHT, HISTORY_LENGTH


class MetricCard(QFrame):
    def __init__(self, title: str, color: str, max_y=100.0, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._color = color

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 16)
        lay.setSpacing(4)

        # Title (uppercase muted)
        self._title = QLabel(title)
        self._title.setObjectName("cardTitle")
        lay.addWidget(self._title)

        # Value row
        val_row = QHBoxLayout()
        val_row.setSpacing(0)
        self._value = QLabel("—")
        self._value.setObjectName("cardValue")
        val_row.addWidget(self._value)
        val_row.addStretch()
        lay.addLayout(val_row)

        lay.addSpacing(6)

        # Graph
        self._pw = pg.PlotWidget()
        self._pw.setBackground(None)
        self._pw.setFixedHeight(110)
        self._pw.showGrid(x=False, y=False)
        self._pw.hideButtons()
        self._pw.setMenuEnabled(False)
        self._pw.setMouseEnabled(x=False, y=False)
        self._pw.getPlotItem().hideAxis("bottom")
        self._pw.getPlotItem().hideAxis("left")
        self._pw.setYRange(0, max_y, padding=0.08)
        self._pw.setXRange(0, HISTORY_LENGTH, padding=0)
        self._pw.getPlotItem().setContentsMargins(0, 0, 0, 0)

        pen = pg.mkPen(color=color, width=2.5)
        self._curve = self._pw.plot([], [], pen=pen)
        self._baseline = pg.PlotDataItem([], [])
        self._fill = pg.FillBetweenItem(
            self._curve, self._baseline,
            brush=pg.mkBrush(color + "18"),
        )
        self._pw.addItem(self._fill)
        lay.addWidget(self._pw)

        # Sub label
        self._sub = QLabel("")
        self._sub.setObjectName("cardSub")
        lay.addWidget(self._sub)

    def update(self, history, value_text, sub_text):
        x = np.arange(len(history))
        y = np.array(history, dtype=float)
        self._curve.setData(x, y)
        self._baseline.setData(x, np.zeros(len(x)))
        self._value.setText(value_text)
        self._sub.setText(sub_text)

    def set_color(self, color):
        self._color = color
        self._curve.setPen(pg.mkPen(color=color, width=2.5))
        self._fill.setBrush(pg.mkBrush(color + "18"))


class PerformanceTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._init_ui()

    def _init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(16)

        c = DARK
        self._cpu  = MetricCard("CPU",     c["graph_cpu"])
        self._ram  = MetricCard("MEMORY",  c["graph_ram"])
        self._disk = MetricCard("DISK",    c["graph_disk"])
        self._net  = MetricCard("NETWORK", c["graph_net"], max_y=500)

        grid.addWidget(self._cpu,  0, 0)
        grid.addWidget(self._ram,  0, 1)
        grid.addWidget(self._disk, 1, 0)
        grid.addWidget(self._net,  1, 1)
        lay.addLayout(grid, 1)

    def refresh(self):
        s = self._store
        with s.lock():
            ch = list(s.cpu_history)
            rh = list(s.ram_history)
            dh = list(s.disk_history)
            nsh = list(s.net_sent_history)
            nrh = list(s.net_recv_history)
            cp = s.cpu_percent; ru = s.ram_used; rt = s.ram_total; rp = s.ram_percent
            du = s.disk_used; dt = s.disk_total; dp = s.disk_percent
            ns = s.net_sent_rate; nr = s.net_recv_rate

        self._cpu.update(ch, f"{cp:.1f}%", "Overall utilisation")
        self._ram.update(rh, f"{rp:.1f}%", f"{ru:.1f} / {rt:.1f} GB")
        self._disk.update(dh, f"{dp:.1f}%", f"{du:.0f} / {dt:.0f} GB")

        combined = [a + b for a, b in zip(nsh, nrh)]
        self._net.update(combined, f"↑{ns:.0f}  ↓{nr:.0f}", "KB/s")
        peak = max(max(combined, default=1), 1) * 1.3
        self._net._pw.setYRange(0, peak, padding=0.08)

    def apply_theme(self, is_dark):
        c = DARK if is_dark else LIGHT
        self._cpu.set_color(c["graph_cpu"])
        self._ram.set_color(c["graph_ram"])
        self._disk.set_color(c["graph_disk"])
        self._net.set_color(c["graph_net"])
