# ─── Main Window ──────────────────────────────────────────────────────
# Minimal chrome. Tabs for navigation. Status bar for ambient info.

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from config import APP_TITLE, MIN_WIDTH, MIN_HEIGHT, DARK, LIGHT
from core.datastore import DataStore
from core.poller import Poller
from ui.styles import build_stylesheet
from ui.processes_tab import ProcessesTab
from ui.performance_tab import PerformanceTab


class MainWindow(QMainWindow):
    """Top-level window — tabs + status bar, no toolbar, no menu bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(1200, 800)

        # Icon
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "assets", "icon.ico",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Theme — default to light (neutral Apple style)
        self._theme = LIGHT

        # Data layer
        self._store = DataStore()
        self._poller = Poller(self._store)

        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._proc_tab = ProcessesTab(self._store, self._theme)
        self._perf_tab = PerformanceTab(self._store, self._theme)

        self._tabs.addTab(self._proc_tab, "  Processes  ")
        self._tabs.addTab(self._perf_tab, "  Performance  ")

        root.addWidget(self._tabs)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        # Apply stylesheet
        self.setStyleSheet(build_stylesheet(self._theme))

        # Signals
        self._poller.data_ready.connect(self._on_stats)
        self._poller.procs_ready.connect(self._on_procs)
        self._tabs.currentChanged.connect(self._on_tab_changed)

        # Start
        self._poller.start()

    def _on_stats(self):
        if self._tabs.currentIndex() == 1:
            self._perf_tab.refresh()
        self._update_status()

    def _on_procs(self):
        if self._tabs.currentIndex() == 0:
            self._proc_tab.refresh()
        self._update_status()

    def _update_status(self):
        with self._store.lock():
            n   = len(self._store.processes)
            cpu = self._store.cpu_percent
            ram = self._store.ram_percent
        self._status.showMessage(
            f"   {n} processes   ·   CPU {cpu:.0f}%   ·   Memory {ram:.0f}%"
        )

    def _on_tab_changed(self, idx):
        if idx == 0:
            self._proc_tab.refresh()
        elif idx == 1:
            self._perf_tab.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self._proc_tab.refresh()

    def closeEvent(self, event):
        self._poller.stop()
        super().closeEvent(event)
