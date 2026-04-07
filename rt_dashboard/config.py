# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Animation durations (ms) ────────────────────────────────────────
ANIM_FADE_IN          = 600
ANIM_CARD_HOVER       = 200
ANIM_TAB_SLIDE        = 250
ANIM_VALUE_TRANSITION = 400

# ── Dark Theme — soft muted navy, low contrast ─────────────────────
# Philosophy: all surfaces within 2-3 shades of each other.
# Accents are desaturated pastels. Text uses opacity hierarchy.
DARK = {
    # Surfaces — tight tonal range
    "bg":              "#181c24",
    "bg_secondary":    "#1c2028",
    "bg_card":         "#1e222c",
    "bg_card_hover":   "#222630",
    "bg_elevated":     "#242830",

    # Text — opacity-based hierarchy
    "text":            "#b8bcc8",
    "text_secondary":  "#787e90",
    "text_muted":      "#505568",

    # Accent — soft muted teal (not neon)
    "accent":          "#6ba3b8",
    "accent_dim":      "#6ba3b808",
    "accent_hover":    "#7eb4c8",
    "accent_glow":     "#6ba3b812",

    # Borders — barely visible
    "border":          "#262a34",
    "card_border":     "#282c38",
    "card_glow":       "#6ba3b806",

    # Graphs — desaturated, cohesive pastels
    "graph_cpu":       "#6ba3b8",
    "graph_ram":       "#9b8abf",
    "graph_disk":      "#c4a56a",
    "graph_net":       "#6fb894",
    "graph_fill":      "18",

    # Interactive states
    "selection":       "#242e3a",
    "row_hover":       "#1e2430",
    "scrollbar":       "#2a2e3a",
    "scrollbar_hover": "#363a48",

    # Tabs
    "tab_active":      "#b8bcc8",
    "tab_inactive":    "#484e60",

    # Inputs
    "input_bg":        "#161a22",
    "input_focus":     "#1c2028",

    # Structure
    "header_bg":       "#181c24",
    "grid_line":       "#222630",
    "statusbar_bg":    "#161a22",

    # Semantic — soft tones
    "danger":          "#c07070",
    "danger_glow":     "#c0707010",
    "separator":       "#6ba3b830",
    "status_run":      "#6fb894",
    "status_stop":     "#c07070",
    "status_sleep":    "#c4a56a",
    "mem_highlight":   "#6ba3b8",

    # Toolbar
    "toolbar_gradient_start": "#1a1e26",
    "toolbar_gradient_end":   "#1c2028",
    "title_glow":      "#6ba3b818",
}

# ── Light Theme — warm off-white, gentle ────────────────────────────
LIGHT = {
    "bg":              "#f4f5f7",
    "bg_secondary":    "#edeef2",
    "bg_card":         "#ffffff",
    "bg_card_hover":   "#fafbfc",
    "bg_elevated":     "#ffffff",

    "text":            "#2c3040",
    "text_secondary":  "#6a7088",
    "text_muted":      "#9ca0b0",

    "accent":          "#5a8ea8",
    "accent_dim":      "#5a8ea806",
    "accent_hover":    "#4a7e98",
    "accent_glow":     "#5a8ea80e",

    "border":          "#e0e2e8",
    "card_border":     "#e4e6ec",
    "card_glow":       "#5a8ea804",

    "graph_cpu":       "#5a8ea8",
    "graph_ram":       "#7b6ca8",
    "graph_disk":      "#b09040",
    "graph_net":       "#509878",
    "graph_fill":      "14",

    "selection":       "#dce4ee",
    "row_hover":       "#f0f1f5",
    "scrollbar":       "#c8cad2",
    "scrollbar_hover": "#b0b4c0",

    "tab_active":      "#2c3040",
    "tab_inactive":    "#9ca0b0",

    "input_bg":        "#edeef2",
    "input_focus":     "#f4f5f7",

    "header_bg":       "#f4f5f7",
    "grid_line":       "#eaecf0",
    "statusbar_bg":    "#edeef2",

    "danger":          "#b05858",
    "danger_glow":     "#b0585808",
    "separator":       "#5a8ea828",
    "status_run":      "#509878",
    "status_stop":     "#b05858",
    "status_sleep":    "#b09040",
    "mem_highlight":   "#5a8ea8",

    "toolbar_gradient_start": "#f0f1f5",
    "toolbar_gradient_end":   "#edeef2",
    "title_glow":      "#5a8ea810",
}

PROCESS_COLUMNS = ["Name", "PID", "CPU %", "Memory (MB)", "Status"]

import psutil
PRIORITY_CLASSES = {
    "Realtime":      psutil.REALTIME_PRIORITY_CLASS,
    "High":          psutil.HIGH_PRIORITY_CLASS,
    "Above Normal":  psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":        psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal":  psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":    psutil.IDLE_PRIORITY_CLASS,
}
