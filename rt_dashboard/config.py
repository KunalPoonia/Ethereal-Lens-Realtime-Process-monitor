# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Neutral Dark Theme ──────────────────────────────────────────────
# Pure grey scale — no colored tint on any surface.
DARK = {
    "bg":           "#1c1c1c",
    "surface":      "#282828",
    "surface2":     "#303030",
    "border":       "#383838",
    "text":         "#e0e0e0",
    "text2":        "#a0a0a0",
    "text3":        "#606060",
    "accent":       "#60cdff",
    "accent_dim":   "#60cdff20",
    "selection":    "#60cdff18",
    "hover":        "#ffffff08",
    "danger":       "#e06060",
    "graph_cpu":    "#60cdff",
    "graph_mem":    "#c080e0",
    "graph_disk":   "#60e0a0",
    "graph_net":    "#e0a060",
    "graph_fill":   20,
    "status_run":   "#60e0a0",
    "status_stop":  "#e06060",
    "status_other": "#a0a0a0",
}

# ── Neutral Light Theme ─────────────────────────────────────────────
LIGHT = {
    "bg":           "#f5f5f5",
    "surface":      "#ffffff",
    "surface2":     "#ebebeb",
    "border":       "#d8d8d8",
    "text":         "#1c1c1c",
    "text2":        "#606060",
    "text3":        "#a0a0a0",
    "accent":       "#0078d4",
    "accent_dim":   "#0078d420",
    "selection":    "#0078d418",
    "hover":        "#00000006",
    "danger":       "#d04040",
    "graph_cpu":    "#0078d4",
    "graph_mem":    "#8040b0",
    "graph_disk":   "#20a060",
    "graph_net":    "#d08020",
    "graph_fill":   16,
    "status_run":   "#20a060",
    "status_stop":  "#d04040",
    "status_other": "#606060",
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
