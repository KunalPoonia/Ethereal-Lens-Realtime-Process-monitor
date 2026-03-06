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
    "accent_dim":     "#818cf830",
    "accent_hover":   "#a5b4fc",
    "border":         "#ffffff0a",
    "border_subtle":  "#ffffff06",
    "success":        "#34d399",
    "warning":        "#fbbf24",
    "danger":         "#f87171",
    "graph_cpu":      "#818cf8",
    "graph_ram":      "#34d399",
    "graph_disk":     "#fbbf24",
    "graph_net":      "#38bdf8",
    "scrollbar":      "#2a2a36",
    "scrollbar_hover":"#3a3a48",
    "selection":      "#818cf820",
    "header_bg":      "#13131a",
    "row_hover":      "#ffffff06",
    "row_alt":        "#ffffff03",
    "section_bg":     "#818cf810",
    "tab_active":     "#818cf8",
    "tab_inactive":   "#4a4a5e",
    "input_bg":       "#13131a",
    "shadow":         "#00000040",
}

# ── Light Theme ──────────────────────────────────────────────────────
LIGHT = {
    "bg":             "#f8f9fc",
    "bg_secondary":   "#f0f1f6",
    "bg_card":        "#ffffff",
    "bg_card_hover":  "#fafbfe",
    "text":           "#1a1a2e",
    "text_secondary": "#6b6b80",
    "text_muted":     "#9a9ab0",
    "accent":         "#6366f1",
    "accent_dim":     "#6366f120",
    "accent_hover":   "#4f46e5",
    "border":         "#0000000a",
    "border_subtle":  "#00000006",
    "success":        "#10b981",
    "warning":        "#f59e0b",
    "danger":         "#ef4444",
    "graph_cpu":      "#6366f1",
    "graph_ram":      "#10b981",
    "graph_disk":     "#f59e0b",
    "graph_net":      "#0ea5e9",
    "scrollbar":      "#d4d4e0",
    "scrollbar_hover":"#b0b0c4",
    "selection":      "#6366f118",
    "header_bg":      "#f0f1f6",
    "row_hover":      "#00000004",
    "row_alt":        "#00000002",
    "section_bg":     "#6366f108",
    "tab_active":     "#6366f1",
    "tab_inactive":   "#9a9ab0",
    "input_bg":       "#f0f1f6",
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
