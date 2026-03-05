# ─── Processes Tab ───────────────────────────────────────────────────
# Live process table with search, sorting, and right-click actions.

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QMenu, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from core.datastore import DataStore
from config import PROCESS_COLUMNS, PRIORITY_CLASSES


class ProcessesTab(QWidget):
    def __init__(self, store: DataStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._sort_col = 0
        self._sort_order = Qt.SortOrder.AscendingOrder
        self._filter_text = ""
        self._init_ui()

    # ── Layout ────────────────────────────────────────────────────────

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Top bar: search + count
        top = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_filter_changed)
        self._search.setFixedHeight(38)
        top.addWidget(self._search, 1)

        self._count_label = QLabel("0 processes")
        self._count_label.setObjectName("statusLabel")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        self._table.setSortingEnabled(False)  # manual sort
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        self._table.setAlternatingRowColors(False)
        self._table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Column sizing
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # PID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # CPU
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Memory
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)           # User
        header.sectionClicked.connect(self._on_header_clicked)

        layout.addWidget(self._table)

    # ── Public refresh (called from main window signal) ───────────────

    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)

        # Filter
        if self._filter_text:
            ft = self._filter_text.lower()
            procs = [p for p in procs if ft in p["name"].lower()
                     or ft in str(p["pid"])]

        # Sort
        key_map = {
            0: "pid", 1: "name", 2: "cpu", 3: "memory", 4: "status", 5: "user"
        }
        key = key_map.get(self._sort_col, "pid")
        reverse = self._sort_order == Qt.SortOrder.DescendingOrder
        try:
            procs.sort(key=lambda p: p[key], reverse=reverse)
        except TypeError:
            pass

        # Preserve scroll position
        scroll = self._table.verticalScrollBar().value()

        self._table.setUpdatesEnabled(False)
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(procs))

        for row, p in enumerate(procs):
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

        self._table.setUpdatesEnabled(True)
        self._table.verticalScrollBar().setValue(scroll)
        self._count_label.setText(f"{len(procs)} processes")

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _numeric_item(value, fmt=None):
        """QTableWidgetItem that sorts numerically."""
        item = QTableWidgetItem()
        if fmt:
            item.setText(fmt.format(value))
        else:
            item.setText(str(value))
        item.setData(Qt.ItemDataRole.UserRole, value)
        return item

    def _on_filter_changed(self, text: str):
        self._filter_text = text
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
        self.refresh()

    # ── Context menu ──────────────────────────────────────────────────

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        pid_item = self._table.item(row, 0)
        if not pid_item:
            return
        pid = int(pid_item.data(Qt.ItemDataRole.UserRole))
        name = self._table.item(row, 1).text()

        menu = QMenu(self)

        # End task
        end_action = QAction(f"⛔  End Task — {name}", self)
        end_action.triggered.connect(lambda: self._end_process(pid))
        menu.addAction(end_action)
        menu.addSeparator()

        # Set priority submenu
        prio_menu = menu.addMenu("⚙  Set Priority")
        for label, value in PRIORITY_CLASSES.items():
            act = QAction(label, self)
            act.triggered.connect(lambda checked, v=value: self._set_priority(pid, v))
            prio_menu.addAction(act)

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _end_process(self, pid: int):
        try:
            p = psutil.Process(pid)
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _set_priority(self, pid: int, priority: int):
        try:
            p = psutil.Process(pid)
            p.nice(priority)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
