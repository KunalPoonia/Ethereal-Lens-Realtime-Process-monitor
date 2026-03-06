# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Dark Theme ───────────────────────────────────────────────────────
DARK = {
    "bg":             "#0f0f14",
    "bg_secondary":   "#16161e",
    "bg_card":        "#1a1a24",
    "bg_card_hover":  "#1f1f2a",
    "text":           "#e8e8f0",
    "text_secondary": "#6e6e82",
    "text_muted":     "#4a4a5e",
    "accent":         "#818cf8",
    "accent_dim":     "#818cf820",
    "accent_hover":   "#a5b4fc",
    "border":         "#ffffff0d",
    "border_subtle":  "#ffffff06",
    "card_border":    "#ffffff0f",
    "success":        "#34d399",
    "warning":        "#fbbf24",
    "danger":         "#f87171",
    "graph_cpu":      "#818cf8",
    "graph_ram":      "#34d399",
    "graph_disk":     "#fbbf24",
    "graph_net":      "#38bdf8",
    "scrollbar":      "#2a2a36",
    "scrollbar_hover":"#3a3a48",
    "selection":      "#818cf825",
    "row_hover":      "#ffffff08",
    "row_alt":        "#ffffff03",
    "section_bg":     "#818cf810",
    "tab_active":     "#818cf8",
    "tab_inactive":   "#4a4a5e",
    "input_bg":       "#13131a",
    "shadow":         "#00000040",
}

# ── Light Theme ──────────────────────────────────────────────────────
LIGHT = {
    "bg":             "#f5f6fa",
    "bg_secondary":   "#ecedf4",
    "bg_card":        "#ffffff",
    "bg_card_hover":  "#fafbfe",
    "text":           "#1e1e30",
    "text_secondary": "#6b6b80",
    "text_muted":     "#9090a8",
    "accent":         "#6366f1",
    "accent_dim":     "#6366f118",
    "accent_hover":   "#4f46e5",
    "border":         "#d8d9e4",
    "border_subtle":  "#e8e9f0",
    "card_border":    "#d0d1de",
    "success":        "#10b981",
    "warning":        "#f59e0b",
    "danger":         "#ef4444",
    "graph_cpu":      "#6366f1",
    "graph_ram":      "#10b981",
    "graph_disk":     "#f59e0b",
    "graph_net":      "#0ea5e9",
    "scrollbar":      "#c8c9d6",
    "scrollbar_hover":"#a8a9b8",
    "selection":      "#6366f120",
    "row_hover":      "#f0f1fa",
    "row_alt":        "#f8f9fc",
    "section_bg":     "#6366f108",
    "tab_active":     "#6366f1",
    "tab_inactive":   "#9090a8",
    "input_bg":       "#ecedf4",
    "shadow":         "#00000010",
}

# ── Process Table ────────────────────────────────────────────────────
PROCESS_COLUMNS = ["PID", "Name", "CPU %", "Memory (MB)", "Status", "User"]

import psutil
PRIORITY_CLASSES = {
    "Realtime":      psutil.REALTIME_PRIORITY_CLASS,
    "High":          psutil.HIGH_PRIORITY_CLASS,
    "Above Normal":  psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":        psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal":  psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":    psutil.IDLE_PRIORITY_CLASS,
}
