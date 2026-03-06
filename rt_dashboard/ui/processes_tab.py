# ─── Processes Tab ───────────────────────────────────────────────────
# Live process table with search, sorting, right-click, and
# App / Background process classification.

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QFont, QBrush

from core.datastore import DataStore
from config import PROCESS_COLUMNS, PRIORITY_CLASSES


class ProcessesTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._sort_col = 2          # default sort by CPU%
        self._sort_order = Qt.SortOrder.DescendingOrder
        self._filter_text = ""
        self._prev_pids: list[int] = []   # for diffing
        self._section_rows: set[int] = set()  # rows with spans
        self._init_ui()

    # ── Layout ────────────────────────────────────────────────────────

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Top bar: search + counts
        top = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter_changed)
        self._search.setFixedHeight(38)
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
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.setAlternatingRowColors(False)
        self._table.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )

        # Column sizing
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.sectionClicked.connect(self._on_header_clicked)

        layout.addWidget(self._table)

    # ── Public refresh ────────────────────────────────────────────────

    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)

        # Filter
        if self._filter_text:
            ft = self._filter_text.lower()
            procs = [
                p for p in procs
                if ft in p["name"].lower() or ft in str(p["pid"])
            ]

        # Split into apps and background
        apps = [p for p in procs if p.get("category") == "app"]
        bg   = [p for p in procs if p.get("category") != "app"]

        # Sort each group independently
        key_map = {0: "pid", 1: "name", 2: "cpu", 3: "memory", 4: "status", 5: "user"}
        key = key_map.get(self._sort_col, "pid")
        reverse = self._sort_order == Qt.SortOrder.DescendingOrder
        try:
            apps.sort(key=lambda p: p[key], reverse=reverse)
            bg.sort(key=lambda p: p[key], reverse=reverse)
        except TypeError:
            pass

        # Build the flat row list with section headers
        rows: list[dict | str] = []
        if apps:
            rows.append(f"▸ Apps ({len(apps)})")
            rows.extend(apps)
        if bg:
            rows.append(f"▸ Background Processes ({len(bg)})")
            rows.extend(bg)

        # --- Check if we can do a fast in-place update ---
        current_pids = [r["pid"] for r in rows if isinstance(r, dict)]
        structure_changed = current_pids != self._prev_pids
        self._prev_pids = current_pids

        scroll = self._table.verticalScrollBar().value()
        self._table.setUpdatesEnabled(False)

        if structure_changed:
            # Full rebuild (only when process list changes)
            self._section_rows.clear()
            self._table.setRowCount(len(rows))
            for row_idx, entry in enumerate(rows):
                if isinstance(entry, str):
                    self._set_section_row(row_idx, entry)
                else:
                    self._set_process_row(row_idx, entry)
        else:
            # Fast update — only change cell text for existing rows
            for row_idx, entry in enumerate(rows):
                if isinstance(entry, dict):
                    self._update_process_row(row_idx, entry)

        self._table.setUpdatesEnabled(True)
        self._table.verticalScrollBar().setValue(scroll)
        self._count_label.setText(
            f"{len(apps)} app{'s' if len(apps) != 1 else ''} · "
            f"{len(bg)} background"
        )

    # ── Row builders ──────────────────────────────────────────────────

    def _set_section_row(self, row: int, title: str):
        """Insert a section-header row spanning all columns."""
        item = QTableWidgetItem(title)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        item.setFont(font)
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(QBrush(QColor("#8888bb")))
        self._table.setItem(row, 0, item)
        # Blank remaining columns
        for col in range(1, len(PROCESS_COLUMNS)):
            blank = QTableWidgetItem("")
            blank.setFlags(Qt.ItemFlag.NoItemFlags)
            self._table.setItem(row, col, blank)
        self._table.setSpan(row, 0, 1, len(PROCESS_COLUMNS))
        self._section_rows.add(row)

    def _set_process_row(self, row: int, p: dict):
        """Full write of a process row."""
        # Only clear span if this row was previously a section header
        if row in self._section_rows:
            self._table.setSpan(row, 0, 1, 1)
            self._section_rows.discard(row)
        items = [
            self._numeric_item(p["pid"]),
            QTableWidgetItem(p["name"]),
            self._numeric_item(p["cpu"], fmt="{:.1f}"),
            self._numeric_item(p["memory"], fmt="{:.1f}"),
            QTableWidgetItem(p["status"]),
            QTableWidgetItem(p["user"]),
        ]
        for col, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, col, item)

    def _update_process_row(self, row: int, p: dict):
        """Fast in-place text update (no new QTableWidgetItem objects)."""
        self._table.item(row, 0).setText(str(p["pid"]))
        self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, p["pid"])
        self._table.item(row, 1).setText(p["name"])
        self._table.item(row, 2).setText(f"{p['cpu']:.1f}")
        self._table.item(row, 2).setData(Qt.ItemDataRole.UserRole, p["cpu"])
        self._table.item(row, 3).setText(f"{p['memory']:.1f}")
        self._table.item(row, 3).setData(Qt.ItemDataRole.UserRole, p["memory"])
        self._table.item(row, 4).setText(p["status"])
        self._table.item(row, 5).setText(p["user"])

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _numeric_item(value, fmt=None):
        item = QTableWidgetItem()
        item.setText(fmt.format(value) if fmt else str(value))
        item.setData(Qt.ItemDataRole.UserRole, value)
        return item

    def _on_filter_changed(self, text: str):
        self._filter_text = text
        self._prev_pids = []   # force structure rebuild on filter
        self.refresh()

    def _on_header_clicked(self, col: int):
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
            return  # clicked on a section header
        pid = int(pid_item.data(Qt.ItemDataRole.UserRole))
        name = self._table.item(row, 1).text()

        menu = QMenu(self)

        end_action = QAction(f"⛔  End Task — {name}", self)
        end_action.triggered.connect(lambda: self._end_process(pid))
        menu.addAction(end_action)
        menu.addSeparator()

        prio_menu = menu.addMenu("⚙  Set Priority")
        for label, value in PRIORITY_CLASSES.items():
            act = QAction(label, self)
            act.triggered.connect(
                lambda checked, v=value: self._set_priority(pid, v)
            )
            prio_menu.addAction(act)

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _end_process(self, pid: int):
        try:
            psutil.Process(pid).terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _set_priority(self, pid: int, priority: int):
        try:
            psutil.Process(pid).nice(priority)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
