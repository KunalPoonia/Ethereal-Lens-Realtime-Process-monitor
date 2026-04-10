# ─── Process Details Sidebar ─────────────────────────────────────────
# Sliding sidebar with process information

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt6.QtGui import QColor, QFont

from config import DARK, LIGHT


class InfoRow(QFrame):
    """A row displaying label: value"""

    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)

        self._label = QLabel(label)
        self._label.setStyleSheet("color: #5c6070; font-size: 11.5px; font-weight: 500;")
        self._label.setFixedWidth(90)
        layout.addWidget(self._label)

        self._value = QLabel("—")
        self._value.setStyleSheet("font-size: 11.5px; font-weight: 400;")
        self._value.setWordWrap(True)
        layout.addWidget(self._value, 1)

    def set_value(self, value):
        self._value.setText(str(value))

    def set_value_style(self, style):
        self._value.setStyleSheet(f"font-size: 11.5px; {style}")


class ProcessDetailsSidebar(QFrame):
    """Sliding sidebar showing process details"""

    def __init__(self, get_theme, parent=None):
        super().__init__(parent)
        self._get_theme = get_theme
        self._current_pid = None
        self._is_visible = False
        self._width = 300

        self.setFixedWidth(0)
        self.setObjectName("detailsSidebar")

        # Animation
        self._anim = QPropertyAnimation(self, b"sidebarWidth")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(-3, 0)
        self.setGraphicsEffect(shadow)

        self._setup_ui()

        # Refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_data)

    @pyqtProperty(int)
    def sidebarWidth(self):
        return self.width()

    @sidebarWidth.setter
    def sidebarWidth(self, value):
        self.setFixedWidth(value)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 14, 14)

        self._title = QLabel("Process Details")
        self._title.setStyleSheet("font-size: 14px; font-weight: 600;")
        header_layout.addWidget(self._title)
        header_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
                border-radius: 13px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.06);
            }
        """)
        close_btn.clicked.connect(self.hide_sidebar)
        header_layout.addWidget(close_btn)

        layout.addWidget(header)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 14, 18, 18)
        content_layout.setSpacing(3)

        # Process name
        self._process_name = QLabel("")
        self._process_name.setStyleSheet("font-size: 16px; font-weight: 600;")
        self._process_name.setWordWrap(True)
        content_layout.addWidget(self._process_name)
        content_layout.addSpacing(14)

        # Basic info
        section1 = QLabel("BASIC INFO")
        section1.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 0.8px; color: #5c6070;")
        content_layout.addWidget(section1)
        content_layout.addSpacing(6)

        self._pid_row = InfoRow("PID")
        self._status_row = InfoRow("Status")
        self._user_row = InfoRow("User")
        self._cpu_row = InfoRow("CPU")
        self._memory_row = InfoRow("Memory")
        self._threads_row = InfoRow("Threads")

        content_layout.addWidget(self._pid_row)
        content_layout.addWidget(self._status_row)
        content_layout.addWidget(self._user_row)
        content_layout.addWidget(self._cpu_row)
        content_layout.addWidget(self._memory_row)
        content_layout.addWidget(self._threads_row)

        content_layout.addSpacing(18)

        # File info
        section2 = QLabel("FILE INFO")
        section2.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 0.8px; color: #5c6070;")
        content_layout.addWidget(section2)
        content_layout.addSpacing(6)

        self._path_row = InfoRow("Path")
        self._cmdline_row = InfoRow("Command")
        self._cwd_row = InfoRow("Working Dir")

        content_layout.addWidget(self._path_row)
        content_layout.addWidget(self._cmdline_row)
        content_layout.addWidget(self._cwd_row)

        content_layout.addSpacing(18)

        # Resource usage
        section3 = QLabel("RESOURCE USAGE")
        section3.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 0.8px; color: #5c6070;")
        content_layout.addWidget(section3)
        content_layout.addSpacing(6)

        self._handles_row = InfoRow("Handles")
        self._io_read_row = InfoRow("I/O Read")
        self._io_write_row = InfoRow("I/O Write")

        content_layout.addWidget(self._handles_row)
        content_layout.addWidget(self._io_read_row)
        content_layout.addWidget(self._io_write_row)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Action buttons
        actions = QFrame()
        actions.setObjectName("sidebarActions")
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(18, 10, 18, 14)
        actions_layout.setSpacing(8)

        end_btn = QPushButton("End Process")
        end_btn.setObjectName("actionButtonDanger")
        end_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        end_btn.clicked.connect(self._end_process)
        actions_layout.addWidget(end_btn)

        open_btn = QPushButton("Open Location")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(self._open_location)
        actions_layout.addWidget(open_btn)

        layout.addWidget(actions)

    def show_process(self, pid):
        self._current_pid = pid
        self._refresh_data()

        if not self._is_visible:
            self._anim.stop()
            self._anim.setStartValue(0)
            self._anim.setEndValue(self._width)
            self._anim.start()
            self._is_visible = True
            self._refresh_timer.start(1000)

    def hide_sidebar(self):
        if self._is_visible:
            self._anim.stop()
            self._anim.setStartValue(self._width)
            self._anim.setEndValue(0)
            self._anim.start()
            self._is_visible = False
            self._refresh_timer.stop()
            self._current_pid = None

    def _refresh_data(self):
        if self._current_pid is None:
            return

        try:
            proc = psutil.Process(self._current_pid)
            info = proc.as_dict(attrs=[
                'name', 'pid', 'status', 'username', 'cpu_percent',
                'memory_info', 'num_threads', 'exe', 'cmdline', 'cwd',
                'num_handles', 'io_counters'
            ])

            c = self._get_theme()

            self._process_name.setText(info['name'] or "Unknown")
            self._pid_row.set_value(info['pid'])

            status = info['status'] or "Unknown"
            self._status_row.set_value(status.capitalize())
            if status == "running":
                self._status_row.set_value_style(f"color: {c['status_run']};")
            elif status == "stopped":
                self._status_row.set_value_style(f"color: {c['status_stop']};")
            else:
                self._status_row.set_value_style(f"color: {c['status_sleep']};")

            self._user_row.set_value((info['username'] or "").split("\\")[-1] or "—")

            cpu = info['cpu_percent'] or 0
            self._cpu_row.set_value(f"{cpu:.1f}%")
            if cpu > 50:
                self._cpu_row.set_value_style(f"color: {c['danger']}; font-weight: 600;")
            elif cpu > 20:
                self._cpu_row.set_value_style(f"color: {c['warning']}; font-weight: 500;")
            else:
                self._cpu_row.set_value_style("")

            mem = info['memory_info']
            if mem:
                mem_mb = mem.rss / (1024**2)
                mem_str = f"{mem_mb:.1f} MB"
                if mem_mb > 1024:
                    mem_str = f"{mem_mb/1024:.2f} GB"
                self._memory_row.set_value(mem_str)
            else:
                self._memory_row.set_value("—")

            self._threads_row.set_value(info['num_threads'] or "—")

            self._path_row.set_value(info['exe'] or "—")

            cmdline = info['cmdline']
            if cmdline:
                self._cmdline_row.set_value(" ".join(cmdline)[:200])
            else:
                self._cmdline_row.set_value("—")

            self._cwd_row.set_value(info['cwd'] or "—")

            handles = info.get('num_handles')
            self._handles_row.set_value(handles if handles else "—")

            io = info.get('io_counters')
            if io:
                read_mb = io.read_bytes / (1024**2)
                write_mb = io.write_bytes / (1024**2)
                self._io_read_row.set_value(f"{read_mb:.1f} MB")
                self._io_write_row.set_value(f"{write_mb:.1f} MB")
            else:
                self._io_read_row.set_value("—")
                self._io_write_row.set_value("—")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.hide_sidebar()

    def _end_process(self):
        if self._current_pid:
            try:
                psutil.Process(self._current_pid).terminate()
                self.hide_sidebar()
            except:
                pass

    def _open_location(self):
        if self._current_pid:
            try:
                proc = psutil.Process(self._current_pid)
                path = proc.exe()
                if path:
                    import os
                    folder = os.path.dirname(path)
                    os.startfile(folder)
            except:
                pass

    def apply_theme(self, is_dark):
        c = DARK if is_dark else LIGHT
        self.setStyleSheet(f"""
            QFrame#detailsSidebar {{
                background: {c['bg_elevated']};
                border-left: 1px solid {c['border']};
            }}
            QFrame#sidebarHeader {{
                background: {c['bg_secondary']};
                border-bottom: 1px solid {c['border']};
            }}
            QFrame#sidebarActions {{
                background: {c['bg_secondary']};
                border-top: 1px solid {c['border']};
            }}
            QLabel {{
                color: {c['text']};
                background: transparent;
            }}
        """)
