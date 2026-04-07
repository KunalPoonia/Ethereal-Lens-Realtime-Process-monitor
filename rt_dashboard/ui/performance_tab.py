# ─── Performance Tab ─────────────────────────────────────────────────
# Metric cards with smooth animated values — desaturated, harmonious.

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QObject, pyqtProperty,
)
from PyQt6.QtGui import QColor

from core.datastore import DataStore
from config import DARK, LIGHT, HISTORY_LENGTH, ANIM_VALUE_TRANSITION


class _AnimatedValue(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0

    @pyqtProperty(float)
    def val(self):
        return self._value

    @val.setter
    def val(self, v):
        self._value = v


class MetricCard(QFrame):
    def __init__(self, title, color, fill_alpha=32, max_y=100.0, unit="%", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._color_hex = color
        self._unit = unit

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 14)
        lay.setSpacing(0)

        # ── Title — muted, not colored ───────────────────────────────
        self._title = QLabel(title)
        self._title.setObjectName("cardTitle")
        lay.addWidget(self._title)

        lay.addSpacing(8)

        # ── Value — standard text color, not accent ──────────────────
        self._value = QLabel("—")
        self._value.setObjectName("cardValue")
        lay.addWidget(self._value)

        lay.addSpacing(10)

        # ── Graph — thin line, gentle fill ───────────────────────────
        self._pw = pg.PlotWidget()
        self._pw.setBackground(None)
        self._pw.setFixedHeight(100)
        self._pw.showGrid(x=False, y=False)
        self._pw.hideButtons()
        self._pw.setMenuEnabled(False)
        self._pw.setMouseEnabled(x=False, y=False)
        pi = self._pw.getPlotItem()
        pi.hideAxis("bottom")
        pi.hideAxis("left")
        pi.setContentsMargins(0, 0, 0, 0)
        pi.getViewBox().setDefaultPadding(0)
        self._pw.setYRange(0, max_y, padding=0.05)
        self._pw.setXRange(0, HISTORY_LENGTH - 1, padding=0)

        # Very subtle reference lines
        for frac in [0.50]:
            line = pg.InfiniteLine(pos=max_y * frac, angle=0,
                                   pen=pg.mkPen("#ffffff05", width=1))
            line.setZValue(-10)
            self._pw.addItem(line)

        # Thin curve with soft fill
        self._curve = self._pw.plot([], [],
                                     pen=pg.mkPen(color, width=1.8),
                                     antialias=True)
        self._base = pg.PlotDataItem([], [])
        fc = QColor(color)
        fc.setAlpha(fill_alpha)
        self._fill = pg.FillBetweenItem(self._curve, self._base, brush=pg.mkBrush(fc))
        self._pw.addItem(self._fill)
        lay.addWidget(self._pw)

        lay.addSpacing(4)

        self._sub = QLabel("")
        self._sub.setObjectName("cardSub")
        lay.addWidget(self._sub)

        # ── Value counter animation ──────────────────────────────────
        self._anim_val = _AnimatedValue(self)
        self._val_anim = QPropertyAnimation(self._anim_val, b"val")
        self._val_anim.setDuration(ANIM_VALUE_TRANSITION)
        self._val_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._val_anim.valueChanged.connect(self._on_val_tick)
        self._current_numeric = 0.0

    def _on_val_tick(self):
        v = self._anim_val.val
        self._value.setText(f"{v:.1f}{self._unit}")

    def update(self, hist, val_text, sub, numeric=None):
        x = np.arange(len(hist))
        y = np.array(hist, dtype=float)
        self._curve.setData(x, y)
        self._base.setData(x, np.zeros(len(x)))

        if numeric is not None:
            old = self._current_numeric
            self._current_numeric = numeric
            if abs(numeric - old) > 0.05:
                self._val_anim.stop()
                self._val_anim.setStartValue(old)
                self._val_anim.setEndValue(numeric)
                self._val_anim.start()
            else:
                self._value.setText(val_text)
        else:
            self._value.setText(val_text)

        self._sub.setText(sub)

    def set_color(self, color, alpha=32):
        self._color_hex = color
        self._curve.setPen(pg.mkPen(color, width=1.8))
        fc = QColor(color)
        fc.setAlpha(alpha)
        self._fill.setBrush(pg.mkBrush(fc))


class PerformanceTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._init_ui()

    def _init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(12)

        c = DARK
        fa = int(c["graph_fill"], 16)
        self._cpu  = MetricCard("CPU",      c["graph_cpu"],  fa, unit="%")
        self._ram  = MetricCard("Memory",   c["graph_ram"],  fa, unit="%")
        self._disk = MetricCard("Disk I/O", c["graph_disk"], fa, max_y=50, unit=" MB/s")
        self._net  = MetricCard("Network",  c["graph_net"],  fa, max_y=500, unit=" KB/s")

        grid.addWidget(self._cpu,  0, 0)
        grid.addWidget(self._ram,  0, 1)
        grid.addWidget(self._disk, 1, 0)
        grid.addWidget(self._net,  1, 1)
        lay.addLayout(grid, 1)

    def refresh(self):
        s = self._store
        with s.lock():
            ch = list(s.cpu_history); rh = list(s.ram_history)
            dh = list(s.disk_history)
            nsh = list(s.net_sent_history); nrh = list(s.net_recv_history)
            cp = s.cpu_percent
            ru = s.ram_used; rt = s.ram_total; rp = s.ram_percent
            dr = s.disk_read_rate; dw = s.disk_write_rate; dtr = s.disk_total_rate
            dsu = s.disk_space_used; dst = s.disk_space_total
            ns = s.net_sent_rate; nr = s.net_recv_rate

        self._cpu.update(ch, f"{cp:.1f}%", "Utilisation", numeric=cp)
        self._ram.update(rh, f"{rp:.1f}%", f"{ru:.1f} / {rt:.1f} GB", numeric=rp)
        self._disk.update(dh, f"{dtr:.1f} MB/s",
                          f"R {dr:.1f}  W {dw:.1f}  ·  {dsu:.0f}/{dst:.0f} GB",
                          numeric=dtr)

        dp = max(max(dh, default=1), 1) * 1.3
        self._disk._pw.setYRange(0, dp, padding=0.05)

        comb = [a + b for a, b in zip(nsh, nrh)]
        total_net = ns + nr
        self._net.update(comb, f"↑ {ns:.0f}   ↓ {nr:.0f}", "KB/s", numeric=total_net)
        np2 = max(max(comb, default=1), 1) * 1.3
        self._net._pw.setYRange(0, np2, padding=0.05)

    def apply_theme(self, is_dark):
        c = DARK if is_dark else LIGHT
        fa = int(c["graph_fill"], 16)
        self._cpu.set_color(c["graph_cpu"], fa)
        self._ram.set_color(c["graph_ram"], fa)
        self._disk.set_color(c["graph_disk"], fa)
        self._net.set_color(c["graph_net"], fa)
