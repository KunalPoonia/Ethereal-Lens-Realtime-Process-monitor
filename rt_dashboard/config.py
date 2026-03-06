# ─── Configuration ───────────────────────────────────────────────────
POLL_INTERVAL_MS = 1000
HISTORY_LENGTH   = 60

APP_TITLE  = "Process Monitor"
MIN_WIDTH  = 1100
MIN_HEIGHT = 700

# ── Dark Theme (Task Manager style) ─────────────────────────────────
DARK = {
    "bg":             "#1c1c1c",
    "bg_secondary":   "#202020",
    "bg_card":        "#2d2d2d",
    "bg_card_hover":  "#333333",
    "text":           "#e4e4e4",
    "text_secondary": "#999999",
    "text_muted":     "#707070",
    "accent":         "#4cc2e0",
    "accent_dim":     "#4cc2e018",
    "accent_hover":   "#60d4f0",
    "border":         "#3a3a3a",
    "border_subtle":  "#2f2f2f",
    "card_border":    "#3a3a3a",
    "success":        "#4ec9b0",
    "warning":        "#dcdcaa",
    "danger":         "#f44747",
    "graph_cpu":      "#4cc2e0",
    "graph_ram":      "#b07cd8",
    "graph_disk":     "#dcdcaa",
    "graph_net":      "#4ec9b0",
    "scrollbar":      "#424242",
    "scrollbar_hover":"#555555",
    "selection":      "#264f78",
    "row_hover":      "#2a2d2e",
    "row_alt":        "#252525",
    "section_bg":     "#252525",
    "section_text":   "#e4e4e4",
    "tab_active":     "#4cc2e0",
    "tab_inactive":   "#707070",
    "input_bg":       "#3c3c3c",
    "shadow":         "#00000040",
    "resource_tint":  "#2b4a52",
    "header_bg":      "#252525",
    "header_text":    "#999999",
    "header_value":   "#e4e4e4",
    "grid_line":      "#2f2f2f",
    "statusbar_bg":   "#1c1c1c",
    "tree_arrow":     "#888888",
}

# ── Light Theme (Task Manager style) ────────────────────────────────
LIGHT = {
    "bg":             "#f3f3f3",
    "bg_secondary":   "#e8e8e8",
    "bg_card":        "#ffffff",
    "bg_card_hover":  "#f8f8f8",
    "text":           "#1a1a1a",
    "text_secondary": "#666666",
    "text_muted":     "#999999",
    "accent":         "#0078d4",
    "accent_dim":     "#0078d415",
    "accent_hover":   "#106ebe",
    "border":         "#d6d6d6",
    "border_subtle":  "#e5e5e5",
    "card_border":    "#d6d6d6",
    "success":        "#107c10",
    "warning":        "#ca5010",
    "danger":         "#d13438",
    "graph_cpu":      "#0078d4",
    "graph_ram":      "#881798",
    "graph_disk":     "#ca5010",
    "graph_net":      "#107c10",
    "scrollbar":      "#c8c8c8",
    "scrollbar_hover":"#a0a0a0",
    "selection":      "#cde4f7",
    "row_hover":      "#e8f0f8",
    "row_alt":        "#f9f9f9",
    "section_bg":     "#f3f3f3",
    "section_text":   "#1a1a1a",
    "tab_active":     "#0078d4",
    "tab_inactive":   "#999999",
    "input_bg":       "#ffffff",
    "shadow":         "#00000010",
    "resource_tint":  "#d4e8ee",
    "header_bg":      "#f3f3f3",
    "header_text":    "#666666",
    "header_value":   "#1a1a1a",
    "grid_line":      "#e5e5e5",
    "statusbar_bg":   "#e8e8e8",
    "tree_arrow":     "#666666",
}

# ── Process Table ────────────────────────────────────────────────────
PROCESS_COLUMNS = ["Name", "PID", "Status", "CPU %", "Memory (MB)", "User"]

import psutil
PRIORITY_CLASSES = {
    "Realtime":      psutil.REALTIME_PRIORITY_CLASS,
    "High":          psutil.HIGH_PRIORITY_CLASS,
    "Above Normal":  psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "Normal":        psutil.NORMAL_PRIORITY_CLASS,
    "Below Normal":  psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "Low (Idle)":    psutil.IDLE_PRIORITY_CLASS,
}
