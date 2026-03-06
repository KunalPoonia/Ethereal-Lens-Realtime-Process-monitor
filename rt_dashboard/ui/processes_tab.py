# ─── Processes Tab (Task Manager style) ──────────────────────────────
# QTreeWidget with process grouping, expand/collapse, status bar.

import psutil
from collections import defaultdict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView, QFrame,
    QStyledItemDelegate, QStyleOptionViewItem,
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QAction, QFont, QColor, QBrush, QPainter, QPen

from core.datastore import DataStore
from config import PROCESS_COLUMNS, PRIORITY_CLASSES, DARK


class SeparatorDelegate(QStyledItemDelegate):
    """Draws a thick top border on items flagged as section separators."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        super().paint(painter, option, index)
        # Check if parent item has separator flag
        item = None
        tree = option.widget
        if tree and hasattr(tree, 'itemFromIndex'):
            item = tree.itemFromIndex(index)
        if item and item.data(0, Qt.ItemDataRole.UserRole + 1) == "separator":
            painter.save()
            pen = QPen(QColor(DARK["accent"]))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(option.rect.left(), option.rect.top(),
                             option.rect.right(), option.rect.top())
            painter.restore()


class ProcessesTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._filter_text = ""
        self._expanded_groups: set[str] = set()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search bar
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 8, 12, 8)
        search_layout.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter)
        self._search.setFixedHeight(32)
        search_layout.addWidget(self._search, 1)
        layout.addWidget(search_frame)

        # Tree widget
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(PROCESS_COLUMNS)
        self._tree.setRootIsDecorated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setAnimated(False)
        self._tree.setAlternatingRowColors(False)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._context_menu)
        self._tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._tree.setIndentation(20)
        self._tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._tree.setStyleSheet("QTreeWidget { border-top: none; }")

        # Install separator delegate
        self._tree.setItemDelegate(SeparatorDelegate(self._tree))

        # Column widths
        h = self._tree.header()
        h.setStretchLastSection(True)
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)     # Name
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)       # PID
        h.resizeSection(1, 70)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)       # Status
        h.resizeSection(2, 80)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)       # CPU
        h.resizeSection(3, 80)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)       # Memory
        h.resizeSection(4, 100)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)     # User
        h.setHighlightSections(False)

        self._tree.itemExpanded.connect(self._on_expand)
        self._tree.itemCollapsed.connect(self._on_collapse)

        layout.addWidget(self._tree, 1)

        # Status bar
        self._statusbar = QFrame()
        self._statusbar.setObjectName("statusbar")
        self._statusbar.setFixedHeight(28)
        sb_layout = QHBoxLayout(self._statusbar)
        sb_layout.setContentsMargins(12, 0, 12, 0)
        sb_layout.setSpacing(20)

        self._sb_procs = QLabel("Processes: 0")
        self._sb_cpu = QLabel("CPU: 0%")
        self._sb_mem = QLabel("Memory: 0%")
        sb_layout.addWidget(self._sb_procs)
        sb_layout.addWidget(self._sb_cpu)
        sb_layout.addWidget(self._sb_mem)
        sb_layout.addStretch()
        layout.addWidget(self._statusbar)

    # ── Refresh ───────────────────────────────────────────────────────

    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)
            cpu_total = self._store.cpu_percent
            ram_pct = self._store.ram_percent

        if self._filter_text:
            ft = self._filter_text.lower()
            procs = [p for p in procs if ft in p["name"].lower() or ft in str(p["pid"])]

        apps = [p for p in procs if p.get("category") == "app"]
        bg   = [p for p in procs if p.get("category") != "app"]

        app_groups = self._group_by_name(apps)
        bg_groups  = self._group_by_name(bg)

        scrollbar = self._tree.verticalScrollBar()
        scroll_pos = scrollbar.value()

        self._tree.setUpdatesEnabled(False)
        self._tree.clear()

        # Section: Apps
        if app_groups:
            section_apps = QTreeWidgetItem(self._tree)
            section_apps.setText(0, f"Apps ({len(apps)})")
            section_apps.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._style_section(section_apps)
            section_apps.setExpanded(True)

            for name, group in sorted(app_groups.items(), key=lambda x: -sum(p["cpu"] for p in x[1])):
                self._add_group(section_apps, name, group)

        # Section: Background — with thick top separator
        if bg_groups:
            section_bg = QTreeWidgetItem(self._tree)
            section_bg.setText(0, f"Background processes ({len(bg)})")
            section_bg.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._style_section(section_bg)
            # Flag this item so the delegate draws a thick top line
            section_bg.setData(0, Qt.ItemDataRole.UserRole + 1, "separator")
            section_bg.setExpanded(True)

            for name, group in sorted(bg_groups.items(), key=lambda x: -sum(p["cpu"] for p in x[1])):
                self._add_group(section_bg, name, group)

        self._tree.setUpdatesEnabled(True)
        scrollbar.setValue(scroll_pos)

        self._sb_procs.setText(f"Processes: {len(procs)}")
        self._sb_cpu.setText(f"CPU: {cpu_total:.0f}%")
        self._sb_mem.setText(f"Memory: {ram_pct:.0f}%")

    # ── Group processes by base name ──────────────────────────────────

    def _group_by_name(self, procs: list[dict]) -> dict[str, list[dict]]:
        groups: dict[str, list[dict]] = defaultdict(list)
        for p in procs:
            base = p["name"]
            if base.lower().endswith(".exe"):
                base = base[:-4]
            groups[base].append(p)
        return dict(groups)

    # ── Build tree items ──────────────────────────────────────────────

    def _add_group(self, parent: QTreeWidgetItem, name: str, group: list[dict]):
        if len(group) == 1:
            p = group[0]
            item = QTreeWidgetItem(parent)
            self._set_proc_data(item, p, display_name=name)
        else:
            total_cpu = sum(p["cpu"] for p in group)
            total_mem = sum(p["memory"] for p in group)
            display = f"{name} ({len(group)})"

            group_item = QTreeWidgetItem(parent)
            group_item.setText(0, display)
            group_item.setText(3, f"{total_cpu:.1f}")
            group_item.setText(4, f"{total_mem:.1f}")
            group_item.setData(0, Qt.ItemDataRole.UserRole, None)

            f = QFont()
            f.setBold(True)
            group_item.setFont(0, f)

            gkey = name
            if gkey in self._expanded_groups:
                group_item.setExpanded(True)

            for p in sorted(group, key=lambda x: -x["cpu"]):
                child = QTreeWidgetItem(group_item)
                self._set_proc_data(child, p)

    def _set_proc_data(self, item: QTreeWidgetItem, p: dict, display_name: str = None):
        name = display_name if display_name else p["name"]
        item.setText(0, name)
        item.setText(1, str(p["pid"]))
        item.setText(2, p["status"])
        item.setText(3, f'{p["cpu"]:.1f}')
        item.setText(4, f'{p["memory"]:.1f}')
        item.setText(5, p["user"])
        item.setData(0, Qt.ItemDataRole.UserRole, p["pid"])
        item.setTextAlignment(3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def _style_section(self, item: QTreeWidgetItem):
        f = QFont()
        f.setBold(True)
        f.setPointSize(11)
        item.setFont(0, f)

    # ── Expand/collapse tracking ──────────────────────────────────────

    def _on_expand(self, item: QTreeWidgetItem):
        text = item.text(0)
        if "(" in text and text.endswith(")"):
            name = text[:text.rfind("(")].strip()
        else:
            name = text
        self._expanded_groups.add(name)

    def _on_collapse(self, item: QTreeWidgetItem):
        text = item.text(0)
        if "(" in text and text.endswith(")"):
            name = text[:text.rfind("(")].strip()
        else:
            name = text
        self._expanded_groups.discard(name)

    # ── Events ────────────────────────────────────────────────────────

    def _on_filter(self, text):
        self._filter_text = text
        self.refresh()

    # ── Context menu ──────────────────────────────────────────────────

    def _context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        pid = item.data(0, Qt.ItemDataRole.UserRole)
        if pid is None:
            return
        pid = int(pid)
        name = item.text(0)

        menu = QMenu(self)
        end = QAction(f"End Task — {name}", self)
        end.triggered.connect(lambda: self._end(pid))
        menu.addAction(end)
        menu.addSeparator()
        sub = menu.addMenu("Set Priority")
        for label, val in PRIORITY_CLASSES.items():
            a = QAction(label, self)
            a.triggered.connect(lambda ck, v=val: self._prio(pid, v))
            sub.addAction(a)
        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _end(self, pid):
        try: psutil.Process(pid).terminate()
        except: pass

    def _prio(self, pid, p):
        try: psutil.Process(pid).nice(p)
        except: pass
