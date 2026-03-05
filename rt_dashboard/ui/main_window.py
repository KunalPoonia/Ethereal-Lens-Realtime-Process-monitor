# ─── Main Window ─────────────────────────────────────────────────────
# Root window with tab bar, theme toggle, and event wiring.

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
        self._poller.data_ready.connect(self._on_data_ready)
        self._poller.start()

    # ── UI Setup ──────────────────────────────────────────────────────

    def _init_ui(self):
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(1280, 800)

        # Try to load icon
        try:
            self.setWindowIcon(QIcon("assets/icon.ico"))
        except Exception:
            pass

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(56)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        app_label = QLabel(f"⚡  {APP_TITLE}")
        app_label.setStyleSheet("font-size:16px; font-weight:700; background:transparent;")
        tb_layout.addWidget(app_label)
        tb_layout.addStretch()

        self._theme_btn = QPushButton("🌙")
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setToolTip("Toggle Dark / Light mode")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._toggle_theme)
        tb_layout.addWidget(self._theme_btn)

        root.addWidget(toolbar)

        # ── Tab widget ────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._proc_tab = ProcessesTab(self._store)
        self._perf_tab = PerformanceTab(self._store)

        self._tabs.addTab(self._proc_tab, "📋  Processes")
        self._tabs.addTab(self._perf_tab, "📈  Performance")

        root.addWidget(self._tabs)

    # ── Data refresh (runs every poll tick) ────────────────────────────

    def _on_data_ready(self):
        self._proc_tab.refresh()
        self._perf_tab.refresh()

    # ── Theme toggle ──────────────────────────────────────────────────

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self._apply_theme()

    def _apply_theme(self):
        if self._is_dark:
            self.setStyleSheet(dark_qss())
            self._theme_btn.setText("🌙")
        else:
            self.setStyleSheet(light_qss())
            self._theme_btn.setText("☀️")
        self._perf_tab.apply_theme(self._is_dark)

    # ── Cleanup ───────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._poller.stop()
        super().closeEvent(event)
