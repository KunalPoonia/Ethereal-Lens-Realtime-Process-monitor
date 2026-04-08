# ─── Main Window ─────────────────────────────────────────────────────
# Root window — clean, minimal chrome.

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFrame, QLabel, QGraphicsOpacityEffect, QMenu,
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
)
from PyQt6.QtGui import QIcon, QFont, QPainter, QLinearGradient, QColor, QAction

from core.datastore import DataStore
from core.poller import Poller
from ui.processes_tab import ProcessesTab
from ui.performance_tab import PerformanceTab
from ui.dashboard_tab import DashboardTab
from ui.styles import dark_qss, light_qss
from ui.theme_manager import ThemeManager
from config import APP_TITLE, MIN_WIDTH, MIN_HEIGHT, ANIM_FADE_IN, DARK, LIGHT


class GradientWidget(QWidget):
    """Widget with animated gradient background"""
    def __init__(self, is_dark=True, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark
        self._gradient_shift = 0.0
    
    def set_dark(self, is_dark):
        self._is_dark = is_dark
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        c = DARK if self._is_dark else LIGHT
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        start_color = QColor(c['bg_gradient_start'])
        end_color = QColor(c['bg_gradient_end'])
        
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        painter.fillRect(self.rect(), gradient)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._theme_mgr = ThemeManager()
        self._is_dark = self._theme_mgr.is_dark()
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

        # ── Gradient background ──────────────────────────────────────
        self._gradient_bg = GradientWidget(self._is_dark)
        self.setCentralWidget(self._gradient_bg)
        
        central = QWidget(self._gradient_bg)
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        root = QVBoxLayout(self._gradient_bg)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Toolbar — vibrant, elevated ─────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(56)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(28, 0, 28, 0)
        tb.setSpacing(12)

        title = QLabel(APP_TITLE)
        tf = QFont("Segoe UI Variable", 14)
        tf.setWeight(QFont.Weight.DemiBold)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.3)
        title.setFont(tf)
        title.setStyleSheet("background: transparent;")
        tb.addWidget(title)
        tb.addStretch()

        # Theme button with dropdown menu
        self._theme_btn = QPushButton(self._get_theme_icon())
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setToolTip("Theme settings")
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self._show_theme_menu)
        tb.addWidget(self._theme_btn)

        main_layout.addWidget(toolbar)

        # ── Tabs ─────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._proc_tab = ProcessesTab(self._store)
        self._perf_tab = PerformanceTab(self._store)
        self._dash_tab = DashboardTab(self._store)

        self._tabs.addTab(self._proc_tab, "Processes")
        self._tabs.addTab(self._perf_tab, "Performance")
        self._tabs.addTab(self._dash_tab, "Dashboard")
        main_layout.addWidget(self._tabs)

    # ── Fade-in ───────────────────────────────────────────────────────

    def _fade_in(self):
        self._opacity_fx = QGraphicsOpacityEffect(self)
        self._gradient_bg.setGraphicsEffect(self._opacity_fx)
        self._opacity_fx.setOpacity(0.0)

        self._fade_anim = QPropertyAnimation(self._opacity_fx, b"opacity")
        self._fade_anim.setDuration(ANIM_FADE_IN)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_anim.finished.connect(self._on_fade_done)
        self._fade_anim.start()

    def _on_fade_done(self):
        self._gradient_bg.setGraphicsEffect(None)

    # ── Selective refresh ─────────────────────────────────────────────

    def _on_perf_tick(self):
        if self._tabs.currentIndex() == 1:
            self._perf_tab.refresh()

    def _on_proc_tick(self):
        idx = self._tabs.currentIndex()
        if idx == 0:
            self._proc_tab.refresh()
        elif idx == 2:
            self._dash_tab.refresh()

    # ── Theme ─────────────────────────────────────────────────────────

    def _get_theme_icon(self):
        """Get icon based on theme mode"""
        mode = self._theme_mgr.get_mode()
        if mode == ThemeManager.MODE_AUTO:
            return "🌓"  # Auto
        elif mode == ThemeManager.MODE_DARK:
            return "🌙"  # Dark
        else:
            return "☀️"  # Light

    def _show_theme_menu(self):
        """Show theme selection menu"""
        menu = QMenu(self)
        
        # Auto theme
        auto_action = QAction("🌓  Auto (System)", self)
        auto_action.setCheckable(True)
        auto_action.setChecked(self._theme_mgr.get_mode() == ThemeManager.MODE_AUTO)
        auto_action.triggered.connect(lambda: self._set_theme_mode(ThemeManager.MODE_AUTO))
        menu.addAction(auto_action)
        
        menu.addSeparator()
        
        # Dark theme
        dark_action = QAction("🌙  Dark", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self._theme_mgr.get_mode() == ThemeManager.MODE_DARK)
        dark_action.triggered.connect(lambda: self._set_theme_mode(ThemeManager.MODE_DARK))
        menu.addAction(dark_action)
        
        # Light theme
        light_action = QAction("☀️  Light", self)
        light_action.setCheckable(True)
        light_action.setChecked(self._theme_mgr.get_mode() == ThemeManager.MODE_LIGHT)
        light_action.triggered.connect(lambda: self._set_theme_mode(ThemeManager.MODE_LIGHT))
        menu.addAction(light_action)
        
        # Show menu below button
        button_pos = self._theme_btn.mapToGlobal(self._theme_btn.rect().bottomLeft())
        menu.exec(button_pos)

    def _set_theme_mode(self, mode):
        """Change theme mode"""
        self._theme_mgr.set_mode(mode)
        self._is_dark = self._theme_mgr.is_dark()
        self._theme_btn.setText(self._get_theme_icon())
        self._apply_theme()

    def _toggle_theme(self):
        # Legacy toggle - cycles through modes
        current = self._theme_mgr.get_mode()
        if current == ThemeManager.MODE_AUTO:
            new_mode = ThemeManager.MODE_DARK
        elif current == ThemeManager.MODE_DARK:
            new_mode = ThemeManager.MODE_LIGHT
        else:
            new_mode = ThemeManager.MODE_AUTO
        self._set_theme_mode(new_mode)

    def _apply_theme(self):
        self.setStyleSheet(dark_qss() if self._is_dark else light_qss())
        self._gradient_bg.set_dark(self._is_dark)
        self._perf_tab.apply_theme(self._is_dark)
        self._proc_tab.set_dark(self._is_dark)

    def closeEvent(self, event):
        self._poller.stop()
        super().closeEvent(event)
