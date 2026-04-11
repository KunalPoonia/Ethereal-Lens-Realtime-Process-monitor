# ─── Processes Tab ────────────────────────────────────────────────────
# Apple-clean process list. Neutral heatmap. Grouped sections.
# No visual noise — spacing and weight do all the work.

import psutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QLabel, QHeaderView, QAbstractItemView,
    QMenu, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QAction, QFont


# ── Neutral heatmap ──────────────────────────────────────────────────
def _parse_heat(hex_str: str, alpha: int) -> QColor:
    c = QColor(hex_str[:7])
    c.setAlpha(alpha)
    return c


def _build_heat_table(theme: dict) -> list[tuple[float, QColor]]:
    return [
        (0,   QColor(0, 0, 0, 0)),
        (2,   _parse_heat(theme["heat_1"], 40)),
        (8,   _parse_heat(theme["heat_1"], 70)),
        (15,  _parse_heat(theme["heat_2"], 90)),
        (30,  _parse_heat(theme["heat_3"], 110)),
        (50,  _parse_heat(theme["heat_4"], 130)),
        (75,  _parse_heat(theme["heat_5"], 150)),
        (90,  _parse_heat(theme["heat_critical"], 170)),
    ]


def _heat_brush(value: float, max_val: float, table: list) -> QBrush:
    if max_val <= 0:
        return QBrush(QColor(0, 0, 0, 0))
    pct = min(100.0, (value / max_val) * 100.0)
    color = table[0][1]
    for threshold, c in table:
        if pct >= threshold:
            color = c
    return QBrush(color)


# Column indices — NO status column
COL_NAME    = 0
COL_CPU     = 1
COL_MEMORY  = 2
COL_DISK    = 3
COL_NETWORK = 4

COLUMNS = ["Name", "CPU", "Memory", "Disk", "Network"]


class ProcessesTab(QWidget):
    """Processes view — search, grouped list, neutral heatmap."""

    def __init__(self, store, theme: dict, parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._heat_table = _build_heat_table(theme)
        self._filter_text = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Search bar ───────────────────────────────────────────────
        search_container = QHBoxLayout()
        search_container.setContentsMargins(20, 14, 20, 0)

        self._search = QLineEdit()
        self._search.setObjectName("searchBar")
        self._search.setPlaceholderText("Search processes…")
        self._search.setClearButtonEnabled(True)
        self._search.setFixedHeight(36)
        self._search.textChanged.connect(self._on_filter_changed)
        search_container.addWidget(self._search)
        layout.addLayout(search_container)

        # ── Header: title + action buttons ───────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(20, 14, 20, 8)

        title = QLabel("Processes")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {self._theme['text']};
            letter-spacing: -0.3px;
        """)
        header.addWidget(title)
        header.addStretch()

        btn_run = QPushButton("Run new task")
        btn_run.setObjectName("headerBtn")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.clicked.connect(self._run_new_task)
        header.addWidget(btn_run)

        self._btn_end = QPushButton("End task")
        self._btn_end.setObjectName("endTaskBtn")
        self._btn_end.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_end.setEnabled(False)
        self._btn_end.clicked.connect(self._end_selected_task)
        header.addWidget(self._btn_end)

        layout.addLayout(header)

        # ── Process tree ─────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setColumnCount(len(COLUMNS))
        self._tree.setHeaderLabels(COLUMNS)
        self._tree.setRootIsDecorated(False)
        self._tree.setIndentation(16)
        self._tree.setAlternatingRowColors(False)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setUniformRowHeights(True)
        self._tree.setSortingEnabled(False)
        self._tree.setAnimated(False)
        self._tree.setExpandsOnDoubleClick(True)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # ── Column sizing — tight, right-aligned numerics ────────────
        h = self._tree.header()
        h.setStretchLastSection(False)
        h.setMinimumSectionSize(50)

        # Name stretches
        h.setSectionResizeMode(COL_NAME, QHeaderView.ResizeMode.Stretch)

        # Fixed-width data columns
        for col, width in [
            (COL_CPU,     70),
            (COL_MEMORY,  100),
            (COL_DISK,    80),
            (COL_NETWORK, 80),
        ]:
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            h.resizeSection(col, width)

        # Right-align header labels for numeric columns
        for col in (COL_CPU, COL_MEMORY, COL_DISK, COL_NETWORK):
            item = self._tree.headerItem()
            item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self._tree)

    # ── Public refresh ───────────────────────────────────────────────
    def refresh(self):
        with self._store.lock():
            procs = list(self._store.processes)

        # Filter
        f = self._filter_text.lower()
        apps, bg = [], []
        for p in procs:
            if f:
                searchable = f"{p['name']} {p['pid']} {p.get('user', '')}".lower()
                if f not in searchable:
                    continue
            if p.get("category") == "app":
                apps.append(p)
            else:
                bg.append(p)

        apps.sort(key=lambda x: x["name"].lower())
        bg.sort(key=lambda x: x["name"].lower())

        # Preserve state
        scrollbar = self._tree.verticalScrollBar()
        scroll_pos = scrollbar.value() if scrollbar else 0
        selected_pid = self._get_selected_pid()

        self._tree.blockSignals(True)
        self._tree.clear()

        # Sections
        self._add_section(f"Apps ({len(apps)})", apps)
        self._add_section(f"Background processes ({len(bg)})", bg)

        self._tree.blockSignals(False)

        if scrollbar:
            scrollbar.setValue(scroll_pos)
        if selected_pid is not None:
            self._select_pid(selected_pid)

    def _add_section(self, label: str, procs: list[dict]):
        section = QTreeWidgetItem(self._tree)
        section.setText(COL_NAME, label)
        section.setFlags(Qt.ItemFlag.ItemIsEnabled)

        font = QFont("Segoe UI Variable Display", 12)
        font.setWeight(QFont.Weight.DemiBold)
        section.setFont(COL_NAME, font)
        section.setForeground(COL_NAME, QBrush(QColor(self._theme["text"])))
        section.setExpanded(True)

        muted = QBrush(QColor(self._theme["text3"]))
        right_v = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        for p in procs:
            item = QTreeWidgetItem(section)
            item.setData(COL_NAME, Qt.ItemDataRole.UserRole, p["pid"])

            # Name
            name = p["name"]
            if name.lower().endswith(".exe"):
                name = name[:-4]
            item.setText(COL_NAME, f"    {name}")

            # CPU — right-aligned
            cpu = p.get("cpu", 0.0)
            item.setText(COL_CPU, f"{cpu:.1f}%  " if cpu >= 0.05 else "0%  ")
            item.setTextAlignment(COL_CPU, right_v)
            item.setBackground(COL_CPU, _heat_brush(cpu, 100.0, self._heat_table))
            if cpu < 0.05:
                item.setForeground(COL_CPU, muted)

            # Memory — right-aligned
            mem = p.get("memory", 0.0)
            if mem >= 1024:
                mem_text = f"{mem/1024:.1f} GB  "
            else:
                mem_text = f"{mem:.1f} MB  "
            item.setText(COL_MEMORY, mem_text)
            item.setTextAlignment(COL_MEMORY, right_v)
            item.setBackground(COL_MEMORY, _heat_brush(mem, 4096.0, self._heat_table))

            # Disk — right-aligned
            item.setText(COL_DISK, "0 MB/s  ")
            item.setTextAlignment(COL_DISK, right_v)
            item.setForeground(COL_DISK, muted)

            # Network — right-aligned
            item.setText(COL_NETWORK, "0 Mbps  ")
            item.setTextAlignment(COL_NETWORK, right_v)
            item.setForeground(COL_NETWORK, muted)

    # ── Selection ────────────────────────────────────────────────────
    def _get_selected_pid(self) -> int | None:
        items = self._tree.selectedItems()
        if items:
            return items[0].data(COL_NAME, Qt.ItemDataRole.UserRole)
        return None

    def _select_pid(self, pid: int):
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            section = root.child(i)
            for j in range(section.childCount()):
                child = section.child(j)
                if child.data(COL_NAME, Qt.ItemDataRole.UserRole) == pid:
                    self._tree.setCurrentItem(child)
                    return

    def _on_selection_changed(self):
        self._btn_end.setEnabled(self._get_selected_pid() is not None)

    def _on_filter_changed(self, text: str):
        self._filter_text = text
        self.refresh()

    # ── Actions ──────────────────────────────────────────────────────
    def _end_selected_task(self):
        pid = self._get_selected_pid()
        if pid is None:
            return
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            reply = QMessageBox.question(
                self, "End Task",
                f"End \"{name}\" (PID {pid})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            QMessageBox.warning(self, "Error", str(e))

    def _run_new_task(self):
        import subprocess
        try:
            subprocess.Popen("cmd.exe", creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception:
            pass

    def _show_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        pid = item.data(COL_NAME, Qt.ItemDataRole.UserRole)
        if pid is None:
            return

        menu = QMenu(self)

        act_end = QAction("End task", self)
        act_end.triggered.connect(self._end_selected_task)
        menu.addAction(act_end)
        menu.addSeparator()

        act_pid = QAction(f"PID: {pid}", self)
        act_pid.setEnabled(False)
        menu.addAction(act_pid)

        try:
            proc = psutil.Process(pid)
            user = proc.username().split("\\")[-1]
            a1 = QAction(f"User: {user}", self)
            a1.setEnabled(False)
            menu.addAction(a1)
            a2 = QAction(f"Threads: {proc.num_threads()}", self)
            a2.setEnabled(False)
            menu.addAction(a2)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        menu.exec(self._tree.viewport().mapToGlobal(pos))
