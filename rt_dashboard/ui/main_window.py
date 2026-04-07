# ─── Main Window ─────────────────────────────────────────────────────
# Root window — clean, minimal chrome.

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFrame, QLabel, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
)
from PyQt6.QtGui import QIcon, QFont

from core.datastore import DataStore
from core.poller import Poller
from ui.processes_tab import ProcessesTab
from ui.performance_tab import PerformanceTab
from ui.styles import dark_qss, light_qss
from config import APP_TITLE, MIN_WIDTH, MIN_HEIGHT, ANIM_FADE_IN


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._is_dark = True
        self._store = DataStore()
        self._poller = Poller(self._store)
        self._init_ui()
        self._apply_theme()

        self._poller.data_ready.connect(self._on_perf_tick)
        self._poller.procs_ready.connect(self._on_proc_tick)
        self._poller.start()

        self._fade_in()

    def _init_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(1320, 840)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar — minimal, flat ──────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(50)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(24, 0, 24, 0)
        tb.setSpacing(12)

        title = QLabel(APP_TITLE)
        tf = QFont("Segoe UI Variable", 13)
        tf.setWeight(QFont.Weight.Medium)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.2)
        title.setFont(tf)
        title.setStyleSheet("background: transparent;")
        tb.addWidget(title)
        tb.addStretch()

        self._theme_btn = QPushButton("🌙")
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setToolTip("Toggle theme")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        tb.addWidget(self._theme_btn)

        root.addWidget(toolbar)

        # ── Tabs ─────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._proc_tab = ProcessesTab(self._store)
        self._perf_tab = PerformanceTab(self._store)

        self._tabs.addTab(self._proc_tab, "Processes")
        self._tabs.addTab(self._perf_tab, "Performance")
        root.addWidget(self._tabs)

    # ── Fade-in ───────────────────────────────────────────────────────

    def _fade_in(self):
        self._opacity_fx = QGraphicsOpacityEffect(self)
        self.centralWidget().setGraphicsEffect(self._opacity_fx)
        self._opacity_fx.setOpacity(0.0)

        self._fade_anim = QPropertyAnimation(self._opacity_fx, b"opacity")
        self._fade_anim.setDuration(ANIM_FADE_IN)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_anim.finished.connect(self._on_fade_done)
        self._fade_anim.start()

    def _on_fade_done(self):
        self.centralWidget().setGraphicsEffect(None)

    # ── Selective refresh ─────────────────────────────────────────────

    def _on_perf_tick(self):
        if self._tabs.currentIndex() == 1:
            self._perf_tab.refresh()

    def _on_proc_tick(self):
        if self._tabs.currentIndex() == 0:
            self._proc_tab.refresh()

    # ── Theme ─────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(dark_qss() if self._is_dark else light_qss())
        self._theme_btn.setText("🌙" if self._is_dark else "☀️")
        self._perf_tab.apply_theme(self._is_dark)
        self._proc_tab.set_dark(self._is_dark)

    def closeEvent(self, event):
        self._poller.stop()
        super().closeEvent(event)
