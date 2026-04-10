# ─── Processes Tab — Clean Minimal Design ───────────────────────────
# Process list with status dots, clean search, and details sidebar

import subprocess
import psutil
from collections import defaultdict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView, QFrame,
    QPushButton, QInputDialog, QMessageBox, QStyledItemDelegate, QDialog,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QSplitter,
)
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QAction, QFont, QColor, QPainter, QPen, QBrush

from core.datastore import DataStore
from ui.components.details_sidebar import ProcessDetailsSidebar
from config import PRIORITY_CLASSES, DARK, LIGHT

COLUMNS = ["", "Name", "PID", "CPU %", "Memory", "Status"]
COL_STATUS_DOT, COL_NAME, COL_PID, COL_CPU, COL_MEM, COL_STATUS = range(6)


class StatusDotDelegate(QStyledItemDelegate):
    """Draws colored status dots"""

    def __init__(self, get_theme, parent=None):
        super().__init__(parent)
        self._get_theme = get_theme

    def paint(self, painter, option, index):
        # Draw separator line
        tree = option.widget
        if tree and hasattr(tree, 'itemFromIndex'):
            item = tree.itemFromIndex(index)
            if item and item.data(0, Qt.ItemDataRole.UserRole + 1) == "separator":
                c = self._get_theme()
                painter.save()
                pen = QPen(QColor(c["separator"]))
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawLine(option.rect.left(), option.rect.top(),
                                 option.rect.right(), option.rect.top())
                painter.restore()

        # Draw status dot
        if index.column() == COL_STATUS_DOT:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            c = self._get_theme()
            status = index.data(Qt.ItemDataRole.UserRole + 2)

            if status:
                if status == "running":
                    color = QColor(c["status_run"])
                elif status == "stopped":
                    color = QColor(c["status_stop"])
                elif status in ("sleeping", "idle"):
                    color = QColor(c["status_sleep"])
                else:
                    color = QColor(c["text_muted"])

                center_x = option.rect.center().x()
                center_y = option.rect.center().y()
                radius = 3

                # Simple dot — no glow
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(center_x - radius, center_y - radius,
                                   radius * 2, radius * 2)

            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if index.column() == COL_STATUS_DOT:
            return QSize(22, option.rect.height())
        return super().sizeHint(option, index)


class ConfirmDialog(QDialog):
    """Clean confirmation dialog"""

    def __init__(self, parent=None, title="", message="", danger=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(380, 180)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._danger = danger
        self._result = False
        self._setup_ui(title, message)

    def _setup_ui(self, title, message):
        container = QFrame(self)
        container.setGeometry(0, 0, 380, 180)
        container.setObjectName("glassDialog")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; background: transparent;")
        layout.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 12px; background: transparent; color: #8b8f99;")
        layout.addWidget(msg_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(90)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("Confirm")
        confirm_btn.setFixedWidth(90)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self._danger:
            confirm_btn.setObjectName("actionButtonDanger")
        confirm_btn.clicked.connect(self._confirm)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

    def _confirm(self):
        self._result = True
        self.accept()

    def get_result(self):
        return self._result


class ProcessesTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._filter = ""
        self._pids: set[int] = set()
        self._expanded: set[str] = set()
        self._is_dark = True
        self._init_ui()

    def _get_theme(self):
        return DARK if self._is_dark else LIGHT

    def set_dark(self, d):
        self._is_dark = d
        self._pids = set()
        self._update_search_style()
        self._sidebar.apply_theme(d)

    def _update_search_style(self):
        c = self._get_theme()
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background: {c['input_bg']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 9px 14px;
                font-size: 13px;
                color: {c['text']};
            }}
            QLineEdit:focus {{
                border-color: {c['accent']};
                background: {c['input_focus']};
            }}
        """)

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QWidget()
        lay = QVBoxLayout(left_panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Search bar ───────────────────────────────────────────────
        bar = QFrame()
        bar.setObjectName("processToolbar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(18, 12, 18, 12)
        bl.setSpacing(12)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search processes...")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter)
        self._search.setFixedHeight(38)
        self._search.setMinimumWidth(280)

        bl.addWidget(self._search, 1)
        bl.addStretch()

        run = QPushButton("Run task")
        run.setCursor(Qt.CursorShape.PointingHandCursor)
        run.clicked.connect(self._run_task)
        run.setFixedHeight(34)
        bl.addWidget(run)

        self._end_btn = QPushButton("End task")
        self._end_btn.setObjectName("actionButtonDanger")
        self._end_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._end_btn.clicked.connect(self._end_selected)
        self._end_btn.setEnabled(False)
        self._end_btn.setFixedHeight(34)
        bl.addWidget(self._end_btn)

        lay.addWidget(bar)

        # ── Tree ─────────────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(COLUMNS)
        self._tree.setRootIsDecorated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(False)
        self._tree.setAlternatingRowColors(False)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._ctx)
        self._tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._tree.setIndentation(18)
        self._tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._tree.itemSelectionChanged.connect(self._sel)
        self._tree.itemExpanded.connect(lambda i: self._expanded.add(self._gk(i)))
        self._tree.itemCollapsed.connect(lambda i: self._expanded.discard(self._gk(i)))

        self._tree.setItemDelegate(StatusDotDelegate(self._get_theme, self._tree))
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        h = self._tree.header()
        h.setStretchLastSection(True)
        h.setSectionResizeMode(COL_STATUS_DOT, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(COL_STATUS_DOT, 24)
        h.setSectionResizeMode(COL_NAME, QHeaderView.ResizeMode.Stretch)
        for col, w in [(COL_PID, 75), (COL_CPU, 80), (COL_MEM, 100), (COL_STATUS, 85)]:
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            h.resizeSection(col, w)
        h.setHighlightSections(False)
        self._tree.headerItem().setText(COL_STATUS_DOT, "")

        lay.addWidget(self._tree, 1)

        # ── Status bar ───────────────────────────────────────────────
        sb = QFrame()
        sb.setObjectName("statusbar")
        sb.setFixedHeight(30)
        sl = QHBoxLayout(sb)
        sl.setContentsMargins(18, 0, 18, 0)
        sl.setSpacing(20)

        self._lp = QLabel("0 processes")
        self._lp.setStyleSheet("font-weight: 500;")
        self._lc = QLabel("CPU 0%")
        self._lm = QLabel("Mem 0%")

        sl.addWidget(self._lp)
        sl.addWidget(self._lc)
        sl.addWidget(self._lm)
        sl.addStretch()

        self._refresh_dot = QLabel("●")
        self._refresh_dot.setStyleSheet("color: #5ea57b; font-size: 7px;")
        sl.addWidget(self._refresh_dot)
        self._last_update = QLabel("Live")
        self._last_update.setStyleSheet("font-size: 11px;")
        sl.addWidget(self._last_update)

        lay.addWidget(sb)

        main_layout.addWidget(left_panel, 1)

        # Details sidebar
        self._sidebar = ProcessDetailsSidebar(self._get_theme, self)
        main_layout.addWidget(self._sidebar)

        self._update_search_style()
        self._sidebar.apply_theme(self._is_dark)

    def _on_item_double_clicked(self, item, column):
        pid = item.data(0, Qt.ItemDataRole.UserRole)
        if pid is not None:
            self._sidebar.show_process(int(pid))

    @staticmethod
    def _gk(item):
        t = item.text(COL_NAME)
        return t[:t.rfind("(")].strip() if "(" in t and t.endswith(")") else t

    def _sel(self):
        s = self._tree.selectedItems()
        self._end_btn.setEnabled(bool(s) and s[0].data(0, Qt.ItemDataRole.UserRole) is not None)

    def _run_task(self):
        cmd, ok = QInputDialog.getText(self, "Run New Task", "Enter command to run:")
        if ok and cmd.strip():
            try:
                subprocess.Popen(cmd.strip(), shell=True)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _end_selected(self):
        s = self._tree.selectedItems()
        if not s: return
        pid = s[0].data(0, Qt.ItemDataRole.UserRole)
        if pid is None: return
        name = s[0].text(COL_NAME)

        dialog = ConfirmDialog(
            self,
            "End Process",
            f"End '{name}' (PID {pid})?\nUnsaved data may be lost.",
            danger=True
        )

        c = self._get_theme()
        dialog.setStyleSheet(f"""
            QFrame#glassDialog {{
                background: {c['bg_elevated']};
                border: 1px solid {c['border']};
                border-radius: 12px;
            }}
            QLabel {{
                color: {c['text']};
            }}
            QPushButton {{
                background: {c['accent_dim']};
                color: {c['text']};
                border: 1px solid {c['border_bright']};
                border-radius: 8px;
                padding: 9px 18px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {c['accent']};
                background: {c['accent_glow']};
            }}
            QPushButton#actionButtonDanger {{
                color: {c['danger']};
                border-color: {c['danger_glow']};
                background: {c['danger_glow']};
            }}
            QPushButton#actionButtonDanger:hover {{
                background: {c['danger']};
                color: white;
            }}
        """)

        if dialog.exec() and dialog.get_result():
            try:
                psutil.Process(int(pid)).terminate()
            except psutil.AccessDenied:
                QMessageBox.warning(self, "Access Denied", "Administrator privileges required.")
            except:
                pass

    # ── Refresh ───────────────────────────────────────────────────────

    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)
            ct = self._store.cpu_percent
            rm = self._store.ram_percent

        if self._filter:
            f = self._filter.lower()
            procs = [p for p in procs if f in p["name"].lower() or f in str(p["pid"])]

        apps = [p for p in procs if p.get("category") == "app"]
        bg = [p for p in procs if p.get("category") != "app"]

        pids = {p["pid"] for p in procs}
        changed = pids != self._pids
        self._pids = pids

        sv = self._tree.verticalScrollBar().value()
        self._tree.setUpdatesEnabled(False)

        if changed:
            self._tree.clear()
            self._build(apps, bg)
        else:
            self._upd(procs)

        self._tree.setUpdatesEnabled(True)
        self._tree.verticalScrollBar().setValue(sv)

        self._lp.setText(f"{len(procs)} processes")
        self._lc.setText(f"CPU {ct:.0f}%")
        self._lm.setText(f"Mem {rm:.0f}%")

        # Subtle pulse
        self._refresh_dot.setStyleSheet("color: #6e7baa; font-size: 7px;")
        QTimer.singleShot(150, lambda: self._refresh_dot.setStyleSheet("color: #5ea57b; font-size: 7px;"))

    def _build(self, apps, bg):
        ag = self._grp(apps)
        bgg = self._grp(bg)
        c = self._get_theme()

        if ag:
            sec = self._sec(f"Apps ({len(apps)})", c)
            for n, g in sorted(ag.items(), key=lambda x: -sum(p["cpu"] for p in x[1])):
                self._add(sec, n, g, c)

        if bgg:
            sec = self._sec(f"Background processes ({len(bg)})", c, separator=True)
            for n, g in sorted(bgg.items(), key=lambda x: -sum(p["cpu"] for p in x[1])):
                self._add(sec, n, g, c)

    def _sec(self, title, c, separator=False):
        s = QTreeWidgetItem(self._tree)
        s.setText(COL_NAME, title)
        s.setFlags(Qt.ItemFlag.ItemIsEnabled)
        f = QFont()
        f.setBold(True)
        f.setPointSize(11)
        s.setFont(COL_NAME, f)
        s.setForeground(COL_NAME, QColor(c["text"]))
        if separator:
            s.setData(0, Qt.ItemDataRole.UserRole + 1, "separator")
        s.setExpanded(True)
        return s

    def _add(self, parent, name, group, c):
        if len(group) == 1:
            it = QTreeWidgetItem(parent)
            self._fill(it, group[0], c)
        else:
            tc = sum(p["cpu"] for p in group)
            tm = sum(p["memory"] for p in group)
            g = QTreeWidgetItem(parent)
            g.setText(COL_NAME, f"{name} ({len(group)})")
            g.setText(COL_CPU, f"{tc:.1f}")
            g.setText(COL_MEM, f"{tm:.1f} MB")
            g.setData(0, Qt.ItemDataRole.UserRole, None)
            g.setTextAlignment(COL_CPU, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            g.setTextAlignment(COL_MEM, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            fn = QFont(); fn.setBold(True); g.setFont(COL_NAME, fn)
            g.setForeground(COL_MEM, QColor(c["mem_highlight"]))
            if name in self._expanded:
                g.setExpanded(True)
            for p in sorted(group, key=lambda x: -x["cpu"]):
                ch = QTreeWidgetItem(g)
                self._fill(ch, p, c)

    @staticmethod
    def _grp(procs):
        g = defaultdict(list)
        for p in procs:
            g[p["name"]].append(p)
        return dict(g)

    def _fill(self, item, p, c):
        item.setText(COL_NAME, p["name"])
        item.setText(COL_PID, str(p["pid"]))
        item.setText(COL_CPU, f"{p['cpu']:.1f}")
        item.setText(COL_MEM, f"{p['memory']:.1f} MB")
        item.setData(0, Qt.ItemDataRole.UserRole, p["pid"])

        for col in (COL_PID, COL_CPU, COL_MEM):
            item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        item.setForeground(COL_MEM, QColor(c["mem_highlight"]))

        st = p["status"].lower()
        item.setData(COL_STATUS_DOT, Qt.ItemDataRole.UserRole + 2, st)

        if st == "running":
            item.setText(COL_STATUS, "Running")
            item.setForeground(COL_STATUS, QColor(c["status_run"]))
        elif st == "stopped":
            item.setText(COL_STATUS, "Stopped")
            item.setForeground(COL_STATUS, QColor(c["status_stop"]))
        elif st in ("sleeping", "idle"):
            item.setText(COL_STATUS, "Sleeping")
            item.setForeground(COL_STATUS, QColor(c["status_sleep"]))
        else:
            item.setText(COL_STATUS, p["status"])
            item.setForeground(COL_STATUS, QColor(c["text_secondary"]))

    def _upd(self, procs):
        c = self._get_theme()
        pm = {p["pid"]: p for p in procs}
        def w(it):
            pid = it.data(0, Qt.ItemDataRole.UserRole)
            if pid is not None and pid in pm:
                p = pm[pid]
                it.setText(COL_CPU, f"{p['cpu']:.1f}")
                it.setText(COL_MEM, f"{p['memory']:.1f} MB")
                st = p["status"].lower()
                it.setData(COL_STATUS_DOT, Qt.ItemDataRole.UserRole + 2, st)
                if st == "running":
                    it.setText(COL_STATUS, "Running")
                    it.setForeground(COL_STATUS, QColor(c["status_run"]))
                elif st == "stopped":
                    it.setText(COL_STATUS, "Stopped")
                    it.setForeground(COL_STATUS, QColor(c["status_stop"]))
                elif st in ("sleeping", "idle"):
                    it.setText(COL_STATUS, "Sleeping")
                    it.setForeground(COL_STATUS, QColor(c["status_sleep"]))
            if it.childCount() > 0 and pid is None:
                tc = tm = 0.0
                for i in range(it.childCount()):
                    ch = it.child(i)
                    cp = ch.data(0, Qt.ItemDataRole.UserRole)
                    if cp and cp in pm:
                        tc += pm[cp]["cpu"]; tm += pm[cp]["memory"]
                    w(ch)
                it.setText(COL_CPU, f"{tc:.1f}")
                it.setText(COL_MEM, f"{tm:.1f} MB")
            else:
                for i in range(it.childCount()): w(it.child(i))
        for i in range(self._tree.topLevelItemCount()):
            w(self._tree.topLevelItem(i))

    def _on_filter(self, t):
        self._filter = t
        self._pids = set()
        self.refresh()

    def _ctx(self, pos):
        it = self._tree.itemAt(pos)
        if not it: return
        pid = it.data(0, Qt.ItemDataRole.UserRole)
        if pid is None: return
        pid = int(pid); name = it.text(COL_NAME)
        m = QMenu(self)

        details = QAction("View Details", self)
        details.triggered.connect(lambda: self._sidebar.show_process(pid))
        m.addAction(details)

        m.addSeparator()

        e = QAction("End Task", self)
        e.triggered.connect(lambda: self._end_selected())
        m.addAction(e)

        m.addSeparator()

        loc = QAction("Open File Location", self)
        loc.triggered.connect(lambda: self._open_location(pid))
        m.addAction(loc)

        m.addSeparator()

        sub = m.addMenu("Set Priority")
        for lbl, val in PRIORITY_CLASSES.items():
            a = QAction(lbl, self)
            a.triggered.connect(lambda _, v=val: self._prio(pid, v))
            sub.addAction(a)

        m.exec(self._tree.viewport().mapToGlobal(pos))

    def _open_location(self, pid):
        try:
            proc = psutil.Process(pid)
            path = proc.exe()
            if path:
                import os
                folder = os.path.dirname(path)
                os.startfile(folder)
        except:
            pass

    def _prio(self, pid, p):
        try: psutil.Process(pid).nice(p)
        except: pass
