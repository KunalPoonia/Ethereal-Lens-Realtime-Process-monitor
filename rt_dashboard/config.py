# ─── config.py ───────────────────────────────────────────────────────────────
#  Process Monitor — Central Configuration
#  All tunables live here. Do not hardcode values elsewhere.
# ─────────────────────────────────────────────────────────────────────────────

import psutil
from typing import TypedDict


# ══════════════════════════════════════════════════════════════════════════════
#  POLLING & HISTORY
# ══════════════════════════════════════════════════════════════════════════════

POLL_INTERVAL_MS   = 1000   # How often the UI refreshes (ms)
HISTORY_LENGTH     = 60     # Number of data-points kept in rolling graphs
ALERT_CPU_PERCENT  = 85.0   # CPU % above which a process is flagged
ALERT_MEM_MB       = 1024   # Memory (MB) above which a process is flagged
MAX_PROCESSES      = 512    # Upper bound on processes shown in the table


# ══════════════════════════════════════════════════════════════════════════════
#  WINDOW
# ══════════════════════════════════════════════════════════════════════════════

APP_TITLE   = "Process Monitor"
APP_VERSION = "1.0.0"
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

# Columns that are right-aligned (numeric)
RIGHT_ALIGN_COLS = {"PID", "CPU %", "Memory (MB)", "Threads"}


# ══════════════════════════════════════════════════════════════════════════════
#  PRIORITY CLASSES  (Windows — psutil constants)
# ══════════════════════════════════════════════════════════════════════════════

PRIORITY_CLASSES: dict[str, int] = {
    "Realtime":     psutil.REALTIME_PRIORITY_CLASS,
    "High":         psutil.HIGH_PRIORITY_CLASS,
    "Above Normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":       psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":   psutil.IDLE_PRIORITY_CLASS,
}

# Default priority applied when spawning new processes from the UI
DEFAULT_PRIORITY = "Normal"


# ══════════════════════════════════════════════════════════════════════════════
#  HEATMAP THRESHOLDS  (CPU %)
# ══════════════════════════════════════════════════════════════════════════════
#  Ordered list of (threshold, heat_key) pairs.
#  The first threshold the value exceeds determines the cell color.

HEAT_THRESHOLDS: list[tuple[float, str]] = [
    (0.0,  "heat_0"),
    (10.0, "heat_1"),
    (30.0, "heat_2"),
    (50.0, "heat_3"),
    (70.0, "heat_4"),
    (85.0, "heat_5"),
    (95.0, "heat_critical"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  THEME TYPE
# ══════════════════════════════════════════════════════════════════════════════

class Theme(TypedDict):
    # Surfaces
    bg:               str
    surface:          str
    surface2:         str
    surface_elevated: str

    # Text
    text:             str
    text2:            str
    text3:            str

    # Accent
    accent:           str
    accent_subtle:    str

    # Borders
    border:           str
    border_subtle:    str

    # Interactive states
    hover:            str
    selection:        str
    active:           str

    # Danger / destructive actions
    danger:           str
    danger_hover:     str

    # Heatmap
    heat_0:           str
    heat_1:           str
    heat_2:           str
    heat_3:           str
    heat_4:           str
    heat_5:           str
    heat_critical:    str

    # Graph colors
    graph_line:       str
    graph_fill:       int   # alpha (0-255) for the area fill under lines
    graph_cpu:        str
    graph_mem:        str
    graph_disk:       str
    graph_net:        str

    # Badges / status chips
    badge_running:    str
    badge_sleeping:   str
    badge_stopped:    str
    badge_zombie:     str


# ══════════════════════════════════════════════════════════════════════════════
#  LIGHT THEME  — Apple-neutral white canvas
# ══════════════════════════════════════════════════════════════════════════════

LIGHT: Theme = {
    # Surfaces
    "bg":               "#FFFFFF",
    "surface":          "#FFFFFF",
    "surface2":         "#D4D4D4",
    "surface_elevated": "#FFFFFF",

    # Text
    "text":             "#2B2B2B",
    "text2":            "#5A5A5A",
    "text3":            "#B3B3B3",

    # Accent
    "accent":           "#2B2B2B",
    "accent_subtle":    "#D4D4D4",

    # Borders
    "border":           "#B3B3B3",
    "border_subtle":    "#D4D4D4",

    # Interactive
    "hover":            "#EFEFEF",
    "selection":        "#2B2B2B",
    "active":           "#B3B3B3",

    # Danger
    "danger":           "#CC3333",
    "danger_hover":     "#991111",

    # Heatmap — monochrome charcoal
    "heat_0":           "#00000000",
    "heat_1":           "#D4D4D480",
    "heat_2":           "#B3B3B3",
    "heat_3":           "#2B2B2B40",
    "heat_4":           "#2B2B2B80",
    "heat_5":           "#2B2B2BA0",
    "heat_critical":    "#2B2B2B",

    # Graphs
    "graph_line":       "#2B2B2B",
    "graph_fill":       18,
    "graph_cpu":        "#2B2B2B",
    "graph_mem":        "#888888",
    "graph_disk":       "#B3B3B3",
    "graph_net":        "#5A5A5A",

    # Badges
    "badge_running":    "#1A7F3C",   # green
    "badge_sleeping":   "#5A5A5A",   # neutral
    "badge_stopped":    "#CC8800",   # amber
    "badge_zombie":     "#CC3333",   # red
}


# ══════════════════════════════════════════════════════════════════════════════
#  DARK THEME  — True black canvas, warm white text
# ══════════════════════════════════════════════════════════════════════════════

DARK: Theme = {
    # Surfaces
    "bg":               "#000000",
    "surface":          "#1C1C1E",
    "surface2":         "#2C2C2E",
    "surface_elevated": "#1C1C1E",

    # Text
    "text":             "#F5F5F7",
    "text2":            "#98989D",
    "text3":            "#636366",

    # Accent
    "accent":           "#F5F5F7",
    "accent_subtle":    "#FFFFFF0A",

    # Borders
    "border":           "#38383A",
    "border_subtle":    "#2C2C2E",

    # Interactive
    "hover":            "#1C1C1E",
    "selection":        "#2C2C2E",
    "active":           "#3A3A3C",

    # Danger
    "danger":           "#FF453A",
    "danger_hover":     "#E03E35",

    # Heatmap — neutral warm amber progression on dark
    "heat_0":           "#00000000",
    "heat_1":           "#3D2E1F",
    "heat_2":           "#4A3828",
    "heat_3":           "#5C4432",
    "heat_4":           "#6E503C",
    "heat_5":           "#7A5A42",
    "heat_critical":    "#8C6148",

    # Graphs
    "graph_line":       "#F5F5F7",
    "graph_fill":       20,
    "graph_cpu":        "#F5F5F7",
    "graph_mem":        "#98989D",
    "graph_disk":       "#636366",
    "graph_net":        "#48484A",

    # Badges
    "badge_running":    "#30D158",
    "badge_sleeping":   "#636366",
    "badge_stopped":    "#FFD60A",
    "badge_zombie":     "#FF453A",
}


# ══════════════════════════════════════════════════════════════════════════════
#  MID THEME  — Twilight graphite; balanced between Light and Dark
# ══════════════════════════════════════════════════════════════════════════════

MID: Theme = {
    # Surfaces
    "bg":               "#2B2B2B",
    "surface":          "#333333",
    "surface2":         "#3D3D3D",
    "surface_elevated": "#3D3D3D",

    # Text
    "text":             "#FFFFFF",
    "text2":            "#D4D4D4",
    "text3":            "#B3B3B3",

    # Accent
    "accent":           "#FFFFFF",
    "accent_subtle":    "#FFFFFF1A",

    # Borders
    "border":           "#B3B3B3",
    "border_subtle":    "#B3B3B34D",

    # Interactive
    "hover":            "#FFFFFF1A",
    "selection":        "#FFFFFF33",
    "active":           "#FFFFFF4D",

    # Danger
    "danger":           "#FF6B6B",
    "danger_hover":     "#FFFFFF",

    # Heatmap — grey-to-white opacity ramp
    "heat_0":           "#00000000",
    "heat_1":           "#D4D4D41A",
    "heat_2":           "#D4D4D433",
    "heat_3":           "#D4D4D44D",
    "heat_4":           "#D4D4D466",
    "heat_5":           "#D4D4D480",
    "heat_critical":    "#FFFFFF",

    # Graphs
    "graph_line":       "#FFFFFF",
    "graph_fill":       24,
    "graph_cpu":        "#FFFFFF",
    "graph_mem":        "#D4D4D4",
    "graph_disk":       "#B3B3B3",
    "graph_net":        "#FFFFFF",

    # Badges
    "badge_running":    "#4ADE80",
    "badge_sleeping":   "#B3B3B3",
    "badge_stopped":    "#FBBF24",
    "badge_zombie":     "#FF6B6B",
}


# ══════════════════════════════════════════════════════════════════════════════
#  THEME REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

THEMES: dict[str, Theme] = {
    "light": LIGHT,
    "dark":  DARK,
    "mid":   MID,
}

DEFAULT_THEME = "dark"


def get_theme(name: str | None = None) -> Theme:
    """Return a theme dict by name, falling back to DEFAULT_THEME."""
    return THEMES.get(name or DEFAULT_THEME, THEMES[DEFAULT_THEME])


def heat_color(cpu_percent: float, theme: Theme) -> str:
    """
    Map a CPU percentage to the appropriate heatmap color key for the given theme.

    Example:
        color = heat_color(72.5, DARK)  # → DARK["heat_5"]
    """
    key = "heat_0"
    for threshold, heat_key in HEAT_THRESHOLDS:
        if cpu_percent >= threshold:
            key = heat_key
    return theme[key]  # type: ignore[literal-required]
