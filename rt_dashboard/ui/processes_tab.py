# ─── Processes Tab — clean and minimal ──────────────────────────────
# Flat tree with sections, gentle coloring, smooth expand/collapse.

import subprocess
import psutil
from collections import defaultdict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView, QFrame,
    QPushButton, QInputDialog, QMessageBox, QStyledItemDelegate,
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QAction, QFont, QColor, QPainter, QPen

from core.datastore import DataStore
from config import PRIORITY_CLASSES, DARK, LIGHT

COLUMNS = ["Name", "PID", "CPU %", "Memory", "Status"]
COL_NAME, COL_PID, COL_CPU, COL_MEM, COL_STATUS = range(5)


class SeparatorDelegate(QStyledItemDelegate):
    """Draws a subtle accent line above section separators."""

    def __init__(self, get_theme, parent=None):
        super().__init__(parent)
        self._get_theme = get_theme

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
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

    def _init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Search bar — clean, minimal padding ──────────────────────
        bar = QFrame()
        bar.setObjectName("processToolbar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 8, 16, 8)
        bl.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter)
        self._search.setFixedHeight(32)
        bl.addWidget(self._search, 1)
        bl.addStretch()

        run = QPushButton("Run new task")
        run.setCursor(Qt.CursorShape.PointingHandCursor)
        run.clicked.connect(self._run_task)
        bl.addWidget(run)

        self._end_btn = QPushButton("End task")
        self._end_btn.setObjectName("actionButtonDanger")
        self._end_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._end_btn.clicked.connect(self._end_selected)
        self._end_btn.setEnabled(False)
        bl.addWidget(self._end_btn)

        lay.addWidget(bar)

        # ── Tree — smooth animations enabled ─────────────────────────
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(COLUMNS)
        self._tree.setRootIsDecorated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(True)
        self._tree.setAlternatingRowColors(False)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._ctx)
        self._tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._tree.setIndentation(20)
        self._tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._tree.itemSelectionChanged.connect(self._sel)
        self._tree.itemExpanded.connect(lambda i: self._expanded.add(self._gk(i)))
        self._tree.itemCollapsed.connect(lambda i: self._expanded.discard(self._gk(i)))

        self._tree.setItemDelegate(SeparatorDelegate(self._get_theme, self._tree))

        h = self._tree.header()
        h.setStretchLastSection(True)
        h.setSectionResizeMode(COL_NAME, QHeaderView.ResizeMode.Stretch)
        for col, w in [(COL_PID, 75), (COL_CPU, 80), (COL_MEM, 100), (COL_STATUS, 85)]:
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            h.resizeSection(col, w)
        h.setHighlightSections(False)

        lay.addWidget(self._tree, 1)

        # ── Status bar ───────────────────────────────────────────────
        sb = QFrame()
        sb.setObjectName("statusbar")
        sb.setFixedHeight(28)
        sl = QHBoxLayout(sb)
        sl.setContentsMargins(18, 0, 18, 0)
        sl.setSpacing(20)
        self._lp = QLabel("0 processes")
        self._lc = QLabel("CPU 0%")
        self._lm = QLabel("Mem 0%")
        sl.addWidget(self._lp)
        sl.addWidget(self._lc)
        sl.addWidget(self._lm)
        sl.addStretch()
        lay.addWidget(sb)

    @staticmethod
    def _gk(item):
        t = item.text(0)
        return t[:t.rfind("(")].strip() if "(" in t and t.endswith(")") else t

    def _sel(self):
        s = self._tree.selectedItems()
        self._end_btn.setEnabled(bool(s) and s[0].data(0, Qt.ItemDataRole.UserRole) is not None)

    def _run_task(self):
        cmd, ok = QInputDialog.getText(self, "Run", "Command:")
        if ok and cmd.strip():
            try: subprocess.Popen(cmd.strip(), shell=True)
            except Exception as e: QMessageBox.warning(self, "Error", str(e))

    def _end_selected(self):
        s = self._tree.selectedItems()
        if not s: return
        pid = s[0].data(0, Qt.ItemDataRole.UserRole)
        if pid is None: return
        name = s[0].text(0)
        if QMessageBox.question(self, "End Task", f"End '{name}' (PID {pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            try: psutil.Process(int(pid)).terminate()
            except psutil.AccessDenied:
                QMessageBox.warning(self, "Denied", "Run as Administrator.")
            except: pass

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
        s.setText(0, title)
        s.setFlags(Qt.ItemFlag.ItemIsEnabled)
        f = QFont()
        f.setBold(True)
        f.setPointSize(10)
        s.setFont(0, f)
        s.setForeground(0, QColor(c["text"]))
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
            g.setText(COL_MEM, f"{tm:.1f}")
            g.setData(0, Qt.ItemDataRole.UserRole, None)
            g.setTextAlignment(COL_CPU, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            g.setTextAlignment(COL_MEM, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            fn = QFont(); fn.setBold(True); g.setFont(0, fn)
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
        item.setText(COL_MEM, f"{p['memory']:.1f}")
        item.setData(0, Qt.ItemDataRole.UserRole, p["pid"])
        for col in (COL_PID, COL_CPU, COL_MEM):
            item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Tint memory value with accent — but softly
        item.setForeground(COL_MEM, QColor(c["mem_highlight"]))

        # Status — just text, gentle color
        st = p["status"].lower()
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
                it.setText(COL_MEM, f"{p['memory']:.1f}")
                st = p["status"].lower()
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
                it.setText(COL_MEM, f"{tm:.1f}")
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
        pid = int(pid); name = it.text(0)
        m = QMenu(self)
        e = QAction("End Task", self)
        e.triggered.connect(lambda: self._end_selected())
        m.addAction(e)
        m.addSeparator()
        sub = m.addMenu("Set Priority")
        for lbl, val in PRIORITY_CLASSES.items():
            a = QAction(lbl, self)
            a.triggered.connect(lambda _, v=val: self._prio(pid, v))
            sub.addAction(a)
        m.exec(self._tree.viewport().mapToGlobal(pos))

    def _prio(self, pid, p):
        try: psutil.Process(pid).nice(p)
        except: pass
