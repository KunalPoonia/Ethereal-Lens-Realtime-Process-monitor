# ─── config.py ───────────────────────────────────────────────────────────────
#  Process Monitor — Central Configuration (Enhanced Version)
# ─────────────────────────────────────────────────────────────────────────────

import psutil
from typing import TypedDict


# ══════════════════════════════════════════════════════════════════════════════
#  POLLING & HISTORY
# ══════════════════════════════════════════════════════════════════════════════

POLL_INTERVAL_MS   = 1000
HISTORY_LENGTH     = 60

POLLING_MODES = {
    "fast":    500,
    "normal":  1000,
    "slow":    2000,
}
DEFAULT_POLLING_MODE = "normal"


# ══════════════════════════════════════════════════════════════════════════════
#  ALERTS
# ══════════════════════════════════════════════════════════════════════════════

# Process-level alerts
ALERT_CPU_PERCENT  = 85.0
ALERT_MEM_MB       = 1024

# System-level alerts
SYSTEM_CPU_ALERT   = 90.0
SYSTEM_MEM_ALERT   = 85.0
SYSTEM_DISK_ALERT  = 90.0


# ══════════════════════════════════════════════════════════════════════════════
#  LIMITS
# ══════════════════════════════════════════════════════════════════════════════

MAX_PROCESSES = 512
MAX_LOG_FILE_SIZE_MB = 5
AUTO_CLEAR_HISTORY   = True


# ══════════════════════════════════════════════════════════════════════════════
#  WINDOW
# ══════════════════════════════════════════════════════════════════════════════

APP_TITLE   = "Process Monitor"
APP_VERSION = "2.0.0"
MIN_WIDTH   = 1100
MIN_HEIGHT  = 700
DEFAULT_W   = 1280
DEFAULT_H   = 800


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESS TABLE
# ══════════════════════════════════════════════════════════════════════════════

PROCESS_COLUMNS = ["Name", "PID", "CPU %", "Memory (MB)", "Threads", "Status"]

COLUMN_WIDTHS = {
    "Name":        220,
    "PID":          70,
    "CPU %":        80,
    "Memory (MB)": 110,
    "Threads":      75,
    "Status":       90,
}

RIGHT_ALIGN_COLS = {"PID", "CPU %", "Memory (MB)", "Threads"}


# ══════════════════════════════════════════════════════════════════════════════
#  SORTING & FILTERING
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_SORT_COLUMN = "CPU %"
DEFAULT_SORT_ORDER  = "desc"

FILTER_SYSTEM_PROCESSES = False
SEARCH_CASE_SENSITIVE   = False


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESS CONTROL
# ══════════════════════════════════════════════════════════════════════════════

ALLOW_PROCESS_KILL      = True
ALLOW_PRIORITY_CHANGE   = True
CONFIRM_BEFORE_KILL     = True


# ══════════════════════════════════════════════════════════════════════════════
#  PRIORITY CLASSES
# ══════════════════════════════════════════════════════════════════════════════

PRIORITY_CLASSES: dict[str, int] = {
    "Realtime":     psutil.REALTIME_PRIORITY_CLASS,
    "High":         psutil.HIGH_PRIORITY_CLASS,
    "Above Normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":       psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":   psutil.IDLE_PRIORITY_CLASS,
}

DEFAULT_PRIORITY = "Normal"


# ══════════════════════════════════════════════════════════════════════════════
#  HEATMAP
# ══════════════════════════════════════════════════════════════════════════════

HEAT_THRESHOLDS = [
    (0.0,  "heat_0"),
    (10.0, "heat_1"),
    (30.0, "heat_2"),
    (50.0, "heat_3"),
    (70.0, "heat_4"),
    (85.0, "heat_5"),
    (95.0, "heat_critical"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  GRAPH SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

GRAPH_SMOOTHING      = True
GRAPH_SHOW_GRID      = True
GRAPH_MAX_POINTS     = 120
GRAPH_UPDATE_INTERVAL_MS = 1000


# ══════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════════════════════

ENABLE_LOGGING = True
LOG_FILE       = "process_monitor.log"
LOG_LEVEL      = "INFO"


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

ENABLE_EXPORT = True
EXPORT_FORMATS = ["csv", "json"]
EXPORT_PATH = "./exports/"


# ══════════════════════════════════════════════════════════════════════════════
#  STATUS COLOR MAP
# ══════════════════════════════════════════════════════════════════════════════

STATUS_COLOR_MAP = {
    "running":    "badge_running",
    "sleeping":   "badge_sleeping",
    "stopped":    "badge_stopped",
    "zombie":     "badge_zombie",
}


# ══════════════════════════════════════════════════════════════════════════════
#  THEME TYPE
# ══════════════════════════════════════════════════════════════════════════════

class Theme(TypedDict):
    bg: str
    surface: str
    surface2: str
    surface_elevated: str
    text: str
    text2: str
    text3: str
    accent: str
    accent_subtle: str
    border: str
    border_subtle: str
    hover: str
    selection: str
    active: str
    danger: str
    danger_hover: str
    heat_0: str
    heat_1: str
    heat_2: str
    heat_3: str
    heat_4: str
    heat_5: str
    heat_critical: str
    graph_line: str
    graph_fill: int
    graph_cpu: str
    graph_mem: str
    graph_disk: str
    graph_net: str
    badge_running: str
    badge_sleeping: str
    badge_stopped: str
    badge_zombie: str


# ══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════════════════════════════

LIGHT: Theme = {
    "bg": "#FFFFFF", "surface": "#FFFFFF", "surface2": "#D4D4D4", "surface_elevated": "#FFFFFF",
    "text": "#2B2B2B", "text2": "#5A5A5A", "text3": "#B3B3B3",
    "accent": "#2B2B2B", "accent_subtle": "#D4D4D4",
    "border": "#B3B3B3", "border_subtle": "#D4D4D4",
    "hover": "#EFEFEF", "selection": "#2B2B2B", "active": "#B3B3B3",
    "danger": "#CC3333", "danger_hover": "#991111",
    "heat_0": "#00000000", "heat_1": "#D4D4D480", "heat_2": "#B3B3B3",
    "heat_3": "#2B2B2B40", "heat_4": "#2B2B2B80", "heat_5": "#2B2B2BA0",
    "heat_critical": "#2B2B2B",
    "graph_line": "#2B2B2B", "graph_fill": 18,
    "graph_cpu": "#2B2B2B", "graph_mem": "#888888",
    "graph_disk": "#B3B3B3", "graph_net": "#5A5A5A",
    "badge_running": "#1A7F3C", "badge_sleeping": "#5A5A5A",
    "badge_stopped": "#CC8800", "badge_zombie": "#CC3333",
}

DARK: Theme = {
    "bg": "#000000", "surface": "#1C1C1E", "surface2": "#2C2C2E", "surface_elevated": "#1C1C1E",
    "text": "#F5F5F7", "text2": "#98989D", "text3": "#636366",
    "accent": "#F5F5F7", "accent_subtle": "#FFFFFF0A",
    "border": "#38383A", "border_subtle": "#2C2C2E",
    "hover": "#1C1C1E", "selection": "#2C2C2E", "active": "#3A3A3C",
    "danger": "#FF453A", "danger_hover": "#E03E35",
    "heat_0": "#00000000", "heat_1": "#3D2E1F", "heat_2": "#4A3828",
    "heat_3": "#5C4432", "heat_4": "#6E503C", "heat_5": "#7A5A42",
    "heat_critical": "#8C6148",
    "graph_line": "#F5F5F7", "graph_fill": 20,
    "graph_cpu": "#F5F5F7", "graph_mem": "#98989D",
    "graph_disk": "#636366", "graph_net": "#48484A",
    "badge_running": "#30D158", "badge_sleeping": "#636366",
    "badge_stopped": "#FFD60A", "badge_zombie": "#FF453A",
}

THEMES = {"light": LIGHT, "dark": DARK}
DEFAULT_THEME = "dark"


# ══════════════════════════════════════════════════════════════════════════════
#  UTIL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_theme(name: str | None = None) -> Theme:
    return THEMES.get(name or DEFAULT_THEME, THEMES[DEFAULT_THEME])


def heat_color(cpu_percent: float, theme: Theme) -> str:
    for threshold, key in reversed(HEAT_THRESHOLDS):
        if cpu_percent >= threshold:
            return theme[key]
    return theme["heat_0"]
