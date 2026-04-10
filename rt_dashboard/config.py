# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Animation durations (ms) ────────────────────────────────────────
ANIM_FADE_IN          = 400
ANIM_CARD_HOVER       = 200
ANIM_TAB_SLIDE        = 200
ANIM_VALUE_TRANSITION = 350

# ── Dark Theme — monochromatic, muted, cohesive ────────────────────
# Philosophy: single-hue accent, quiet surfaces, no glow, no noise
DARK = {
    # Surfaces — layered neutrals
    "bg":              "#111318",
    "bg_secondary":    "#15171d",
    "bg_card":         "#1a1d24",
    "bg_card_hover":   "#1f222a",
    "bg_elevated":     "#1e2129",

    # Gradient backgrounds (kept subtle — same hue, slight shift)
    "bg_gradient_start": "#111318",
    "bg_gradient_end":   "#14161c",

    # Text — restrained hierarchy
    "text":            "#c8cad0",
    "text_secondary":  "#8b8f99",
    "text_muted":      "#5c6070",
    "text_bright":     "#e4e5ea",

    # Accent — single muted slate-blue
    "accent":          "#6e7baa",
    "accent_secondary":"#7d89b5",
    "accent_dim":      "#6e7baa18",
    "accent_hover":    "#8490bf",
    "accent_glow":     "#6e7baa28",

    # Borders — barely visible
    "border":          "#23262f",
    "border_bright":   "#2d313b",
    "card_border":     "#ffffff08",
    "card_glow":       "#6e7baa0c",

    # Graphs — muted, tonal (all within the same cool-grey family)
    "graph_cpu":       "#6e7baa",
    "graph_ram":       "#8a7ba5",
    "graph_disk":      "#7b9aa0",
    "graph_net":       "#7ba58a",
    "graph_fill":      "18",

    # Interactive states
    "selection":       "#6e7baa20",
    "row_hover":       "#ffffff06",
    "scrollbar":       "#2d313b",
    "scrollbar_hover": "#3a3f4b",

    # Tabs
    "tab_active":      "#e4e5ea",
    "tab_inactive":    "#5c6070",

    # Inputs
    "input_bg":        "#15171d",
    "input_focus":     "#1a1d24",
    "input_border":    "#2d313b",

    # Structure
    "header_bg":       "#15171d",
    "grid_line":       "#1e2129",
    "statusbar_bg":    "#111318",

    # Semantic — desaturated
    "danger":          "#b05e5e",
    "danger_glow":     "#b05e5e20",
    "warning":         "#7a7e99",
    "warning_glow":    "#7a7e9920",
    "success":         "#5ea57b",
    "success_glow":    "#5ea57b20",

    "separator":       "#6e7baa18",
    "status_run":      "#5ea57b",
    "status_stop":     "#b05e5e",
    "status_sleep":    "#7a7e8a",
    "mem_highlight":   "#8b8f99",

    # Toolbar
    "toolbar_gradient_start": "#15171d",
    "toolbar_gradient_end":   "#1a1d24",
    "title_glow":      "#6e7baa14",
}

# ── Light Theme — clean, airy, cohesive ────────────────────────────
LIGHT = {
    # Surfaces
    "bg":              "#f6f7f9",
    "bg_secondary":    "#eef0f3",
    "bg_card":         "#ffffff",
    "bg_card_hover":   "#f9fafb",
    "bg_elevated":     "#ffffff",

    # Gradient backgrounds
    "bg_gradient_start": "#f6f7f9",
    "bg_gradient_end":   "#f0f1f4",

    # Text
    "text":            "#2e3038",
    "text_secondary":  "#6b7080",
    "text_muted":      "#9ca0ab",
    "text_bright":     "#1a1c22",

    # Accent
    "accent":          "#5b6894",
    "accent_secondary":"#6b78a4",
    "accent_dim":      "#5b689414",
    "accent_hover":    "#4a577f",
    "accent_glow":     "#5b689424",

    # Borders
    "border":          "#e0e2e7",
    "border_bright":   "#d0d3da",
    "card_border":     "#00000008",
    "card_glow":       "#5b68940c",

    # Graphs
    "graph_cpu":       "#5b6894",
    "graph_ram":       "#7a6b8f",
    "graph_disk":      "#6b8a90",
    "graph_net":       "#6b8f7a",
    "graph_fill":      "14",

    # Interactive states
    "selection":       "#5b689418",
    "row_hover":       "#00000005",
    "scrollbar":       "#d0d3da",
    "scrollbar_hover": "#b8bcc6",

    # Tabs
    "tab_active":      "#1a1c22",
    "tab_inactive":    "#9ca0ab",

    # Inputs
    "input_bg":        "#f0f1f4",
    "input_focus":     "#ffffff",
    "input_border":    "#d0d3da",

    # Structure
    "header_bg":       "#eef0f3",
    "grid_line":       "#e8eaee",
    "statusbar_bg":    "#f6f7f9",

    # Semantic
    "danger":          "#a05050",
    "danger_glow":     "#a0505018",
    "warning":         "#6c7088",
    "warning_glow":    "#6c708818",
    "success":         "#508f6a",
    "success_glow":    "#508f6a18",

    "separator":       "#5b689418",
    "status_run":      "#508f6a",
    "status_stop":     "#a05050",
    "status_sleep":    "#7a7e88",
    "mem_highlight":   "#6b7080",

    # Toolbar
    "toolbar_gradient_start": "#eef0f3",
    "toolbar_gradient_end":   "#e8eaee",
    "title_glow":      "#5b689414",
}

PROCESS_COLUMNS = ["Name" , "PID" , "CPU %", "Memory (MB)", "Status"] 

import psutil 
PRIORITY_CLASSES = {
    "Realtime":      psutil.REALTIME_PRIORITY_CLASS,
    "High":          psutil.HIGH_PRIORITY_CLASS,
    "Above Normal":  psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":        psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal":  psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":    psutil.IDLE_PRIORITY_CLASS,
}       
