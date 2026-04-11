# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Light Theme — Apple-neutral ─────────────────────────────────────
# True neutral palette. White canvas. Charcoal ink. No decorative color.
LIGHT = {
    # Surfaces
    "bg":               "#FFFFFF",
    "surface":          "#FFFFFF",
    "surface2":         "#D4D4D4",
    "surface_elevated": "#FFFFFF",

    # Text
    "text":             "#2B2B2B",
    "text2":            "#2B2B2B",
    "text3":            "#B3B3B3",

    # Accent (used sparingly — selection, active tab underline only)
    "accent":           "#2B2B2B",
    "accent_subtle":    "#D4D4D4",

    # Borders
    "border":           "#B3B3B3",
    "border_subtle":    "#D4D4D4",

    # Interactive
    "hover":            "#D4D4D4",
    "selection":        "#2B2B2B",
    "active":           "#B3B3B3",

    # Danger
    "danger":           "#B3B3B3",
    "danger_hover":     "#2B2B2B",

    # Heatmap (monochrome charcoal — strictly within approved palette)
    "heat_0":           "#00000000",
    "heat_1":           "#D4D4D480",
    "heat_2":           "#B3B3B3",
    "heat_3":           "#2B2B2B40",
    "heat_4":           "#2B2B2B80",
    "heat_5":           "#2B2B2BA0",
    "heat_critical":    "#2B2B2B",

    # Graphs
    "graph_line":       "#2B2B2B",
    "graph_fill":       8,
    "graph_cpu":        "#2B2B2B",
    "graph_mem":        "#B3B3B3",
    "graph_disk":       "#D4D4D4",
    "graph_net":        "#2B2B2B",
}

# ── Dark Theme — Apple-neutral ──────────────────────────────────────
# True black canvas. Warm white text. Zero chromatic noise.
DARK = {
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

    # Heatmap (neutral warm progression — transparent → warm amber on dark)
    "heat_0":           "#00000000",
    "heat_1":           "#3D2E1F",
    "heat_2":           "#4A3828",
    "heat_3":           "#5C4432",
    "heat_4":           "#6E503C",
    "heat_5":           "#7A5A42",
    "heat_critical":    "#8C6148",

    # Graphs
    "graph_line":       "#F5F5F7",
    "graph_fill":       12,
    "graph_cpu":        "#F5F5F7",
    "graph_mem":        "#98989D",
    "graph_disk":       "#636366",
    "graph_net":        "#48484A",
}

# ── Mid Theme — Between Light and Dark ──────────────────────────────
# A sleek, neutral twilight graphite.
MID = {
    # Base Layout (Dark Charcoal Base)
    "bg":               "#2B2B2B",
    "surface":          "#2B2B2B",
    "surface2":         "#FFFFFF1A",
    "surface_elevated": "#2B2B2B",

    # Text Elements (Crisp White & Grey)
    "text":             "#FFFFFF",
    "text2":            "#D4D4D4",
    "text3":            "#B3B3B3",

    # Theme Accent
    "accent":           "#FFFFFF",
    "accent_subtle":    "#FFFFFF1A",

    # Structural Lines
    "border":           "#B3B3B3",
    "border_subtle":    "#B3B3B34D",

    # States
    "hover":            "#FFFFFF1A",
    "selection":        "#FFFFFF33",
    "active":           "#FFFFFF4D",

    # Danger Fallback
    "danger":           "#B3B3B3",
    "danger_hover":     "#FFFFFF",

    # Monochromatic Heatmap (Grey to White Opacities)
    "heat_0":           "#00000000",
    "heat_1":           "#D4D4D41A",
    "heat_2":           "#D4D4D433",
    "heat_3":           "#D4D4D44D",
    "heat_4":           "#D4D4D466",
    "heat_5":           "#D4D4D480",
    "heat_critical":    "#FFFFFF",

    # Monochromatic Graphs
    "graph_line":       "#FFFFFF",
    "graph_fill":       15,
    "graph_cpu":        "#FFFFFF",
    "graph_mem":        "#D4D4D4",
    "graph_disk":       "#B3B3B3",
    "graph_net":        "#FFFFFF",
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
