# ─── Configuration ───────────────────────────────────────────────────
# Central config for the Real-Time Process Dashboard

POLL_INTERVAL_MS = 1000          # How often to poll (milliseconds)
HISTORY_LENGTH   = 60            # Rolling history size (seconds)

# ── Window ────────────────────────────────────────────────────────────
APP_TITLE  = "Real-Time Process Dashboard"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Dark Theme Colors ────────────────────────────────────────────────
DARK = {
    "bg":            "#1a1b2e",
    "bg_secondary":  "#232540",
    "bg_card":       "#2a2d4a",
    "text":          "#e0e0f0",
    "text_secondary": "#8888aa",
    "accent":        "#7c6ff7",
    "accent_hover":  "#9589ff",
    "border":        "#3a3d5c",
    "success":       "#4ade80",
    "warning":       "#fbbf24",
    "danger":        "#f87171",
    "graph_cpu":     "#7c6ff7",
    "graph_ram":     "#4ade80",
    "graph_disk":    "#fbbf24",
    "graph_net":     "#38bdf8",
    "scrollbar":     "#3a3d5c",
    "scrollbar_hover": "#4a4d6c",
    "selection":     "#7c6ff740",
    "header_bg":     "#232540",
    "row_hover":     "#2e3154",
    "tab_active":    "#7c6ff7",
    "tab_inactive":  "#3a3d5c",
}

# ── Light Theme Colors ───────────────────────────────────────────────
LIGHT = {
    "bg":            "#f0f1f8",
    "bg_secondary":  "#e4e5f0",
    "bg_card":       "#ffffff",
    "text":          "#1a1b2e",
    "text_secondary": "#6b6d85",
    "accent":        "#6c5ce7",
    "accent_hover":  "#5a4bd5",
    "border":        "#d0d1e0",
    "success":       "#22c55e",
    "warning":       "#f59e0b",
    "danger":        "#ef4444",
    "graph_cpu":     "#6c5ce7",
    "graph_ram":     "#22c55e",
    "graph_disk":    "#f59e0b",
    "graph_net":     "#0ea5e9",
    "scrollbar":     "#c0c1d0",
    "scrollbar_hover": "#a0a1b0",
    "selection":     "#6c5ce740",
    "header_bg":     "#e4e5f0",
    "row_hover":     "#e8e9f4",
    "tab_active":    "#6c5ce7",
    "tab_inactive":  "#c0c1d0",
}

# ── Process Table Columns ────────────────────────────────────────────
PROCESS_COLUMNS = ["PID", "Name", "CPU %", "Memory (MB)", "Status", "User"]

# ── Priority Map ─────────────────────────────────────────────────────
import psutil
PRIORITY_CLASSES = {
    "Realtime":      psutil.REALTIME_PRIORITY_CLASS,
    "High":          psutil.HIGH_PRIORITY_CLASS,
    "Above Normal":  psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":        psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal":  psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":    psutil.IDLE_PRIORITY_CLASS,
}
