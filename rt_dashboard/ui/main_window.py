# ─── Main Window ─────────────────────────────────────────────────────
# Minimal root window — only refreshes the active tab.

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFrame, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from core.datastore import DataStore
from core.poller import Poller
from ui.processes_tab import ProcessesTab
from ui.performance_tab import PerformanceTab
from ui.styles import dark_qss, light_qss
from config import APP_TITLE, MIN_WIDTH, MIN_HEIGHT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._is_dark = True
        self._store = DataStore()
        self._poller = Poller(self._store)
        self._init_ui()
        self._apply_theme()

        # Wire signals — only refresh the visible tab
        self._poller.data_ready.connect(self._on_perf_tick)
        self._poller.procs_ready.connect(self._on_proc_tick)
        self._poller.start()

    def _init_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(1280, 800)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(52)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(24, 0, 24, 0)

        title = QLabel(APP_TITLE)
        title.setStyleSheet(
            "font-size:15px; font-weight:700; letter-spacing:0.5px; "
            "background:transparent;"
        )
        tb.addWidget(title)
        tb.addStretch()

        self._theme_btn = QPushButton("🌙")
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setToolTip("Toggle theme")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        tb.addWidget(self._theme_btn)

        root.addWidget(toolbar)

        # ── Tabs ──────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._proc_tab = ProcessesTab(self._store)
        self._perf_tab = PerformanceTab(self._store)

        self._tabs.addTab(self._proc_tab, "Processes")
        self._tabs.addTab(self._perf_tab, "Performance")
        root.addWidget(self._tabs)

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

    def closeEvent(self, event):
        self._poller.stop()
        super().closeEvent(event)
