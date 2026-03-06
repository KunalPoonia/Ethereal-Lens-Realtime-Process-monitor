# ─── Processes Tab ───────────────────────────────────────────────────
# Optimised process table with App / Background grouping.

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QFont, QBrush

from core.datastore import DataStore
from config import PROCESS_COLUMNS, PRIORITY_CLASSES, DARK


class ProcessesTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._sort_col = 2
        self._sort_order = Qt.SortOrder.DescendingOrder
        self._filter_text = ""
        self._prev_pids: list[int] = []
        self._section_rows: set[int] = set()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        # Top row
        top = QHBoxLayout()
        top.setSpacing(12)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter_changed)
        self._search.setFixedHeight(40)
        top.addWidget(self._search, 1)

        self._count_label = QLabel("0 apps · 0 background")
        self._count_label.setObjectName("statusLabel")
        self._count_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        top.addWidget(self._count_label)
        layout.addLayout(top)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(PROCESS_COLUMNS))
        self._table.setHorizontalHeaderLabels(PROCESS_COLUMNS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        h = self._table.horizontalHeader()
        h.setHighlightSections(False)
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(0, 70)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(2, 80)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(3, 110)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        h.resizeSection(4, 90)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        h.sectionClicked.connect(self._on_header_clicked)

        self._table.verticalHeader().setDefaultSectionSize(36)
        layout.addWidget(self._table)

    # ── Refresh ───────────────────────────────────────────────────────

    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)

        if self._filter_text:
            ft = self._filter_text.lower()
            procs = [p for p in procs if ft in p["name"].lower() or ft in str(p["pid"])]

        apps = [p for p in procs if p.get("category") == "app"]
        bg   = [p for p in procs if p.get("category") != "app"]

        key_map = {0:"pid", 1:"name", 2:"cpu", 3:"memory", 4:"status", 5:"user"}
        key = key_map.get(self._sort_col, "pid")
        rev = self._sort_order == Qt.SortOrder.DescendingOrder
        try:
            apps.sort(key=lambda p: p[key], reverse=rev)
            bg.sort(key=lambda p: p[key], reverse=rev)
        except TypeError:
            pass

        rows: list[dict | str] = []
        if apps:
            rows.append(f"APPS  ({len(apps)})")
            rows.extend(apps)
        if bg:
            rows.append(f"BACKGROUND PROCESSES  ({len(bg)})")
            rows.extend(bg)

        cur_pids = [r["pid"] for r in rows if isinstance(r, dict)]
        changed = cur_pids != self._prev_pids
        self._prev_pids = cur_pids

        scroll = self._table.verticalScrollBar().value()
        self._table.setUpdatesEnabled(False)

        if changed:
            self._section_rows.clear()
            self._table.setRowCount(len(rows))
            for i, entry in enumerate(rows):
                if isinstance(entry, str):
                    self._write_section(i, entry)
                else:
                    self._write_row(i, entry)
        else:
            for i, entry in enumerate(rows):
                if isinstance(entry, dict):
                    self._update_row(i, entry)

        self._table.setUpdatesEnabled(True)
        self._table.verticalScrollBar().setValue(scroll)
        self._count_label.setText(
            f"{len(apps)} app{'s' if len(apps)!=1 else ''} · {len(bg)} background"
        )

    # ── Row helpers ───────────────────────────────────────────────────

    def _write_section(self, row, title):
        item = QTableWidgetItem(title)
        f = QFont("Segoe UI Variable", 9)
        f.setBold(True)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        item.setFont(f)
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(QBrush(QColor(DARK["text_muted"])))
        self._table.setItem(row, 0, item)
        for c in range(1, len(PROCESS_COLUMNS)):
            b = QTableWidgetItem("")
            b.setFlags(Qt.ItemFlag.NoItemFlags)
            self._table.setItem(row, c, b)
        self._table.setSpan(row, 0, 1, len(PROCESS_COLUMNS))
        self._section_rows.add(row)

    def _write_row(self, row, p):
        if row in self._section_rows:
            self._table.setSpan(row, 0, 1, 1)
            self._section_rows.discard(row)
        vals = [
            (str(p["pid"]),          p["pid"]),
            (p["name"],              None),
            (f'{p["cpu"]:.1f}',      p["cpu"]),
            (f'{p["memory"]:.1f}',   p["memory"]),
            (p["status"],            None),
            (p["user"],              None),
        ]
        for c, (txt, data) in enumerate(vals):
            it = QTableWidgetItem(txt)
            if data is not None:
                it.setData(Qt.ItemDataRole.UserRole, data)
            it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, c, it)

    def _update_row(self, row, p):
        self._table.item(row, 0).setText(str(p["pid"]))
        self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, p["pid"])
        self._table.item(row, 1).setText(p["name"])
        self._table.item(row, 2).setText(f'{p["cpu"]:.1f}')
        self._table.item(row, 2).setData(Qt.ItemDataRole.UserRole, p["cpu"])
        self._table.item(row, 3).setText(f'{p["memory"]:.1f}')
        self._table.item(row, 3).setData(Qt.ItemDataRole.UserRole, p["memory"])
        self._table.item(row, 4).setText(p["status"])
        self._table.item(row, 5).setText(p["user"])

    # ── Events ────────────────────────────────────────────────────────

    def _on_filter_changed(self, text):
        self._filter_text = text
        self._prev_pids = []
        self.refresh()

    def _on_header_clicked(self, col):
        if col == self._sort_col:
            self._sort_order = (
                Qt.SortOrder.DescendingOrder
                if self._sort_order == Qt.SortOrder.AscendingOrder
                else Qt.SortOrder.AscendingOrder
            )
        else:
            self._sort_col = col
            self._sort_order = Qt.SortOrder.AscendingOrder
        self._prev_pids = []
        self.refresh()

    # ── Context menu ──────────────────────────────────────────────────

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        pid_item = self._table.item(row, 0)
        if not pid_item or not pid_item.data(Qt.ItemDataRole.UserRole):
            return
        pid = int(pid_item.data(Qt.ItemDataRole.UserRole))
        name = self._table.item(row, 1).text()

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
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _end(self, pid):
        try: psutil.Process(pid).terminate()
        except: pass

    def _prio(self, pid, p):
        try: psutil.Process(pid).nice(p)
        except: pass
