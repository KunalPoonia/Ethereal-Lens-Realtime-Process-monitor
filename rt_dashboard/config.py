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

# ── Dark Theme — vibrant glassmorphism design ──────────────────────
# Philosophy: rich gradients, translucent surfaces, vibrant accents
DARK = {
    # Surfaces — glassmorphic layers
    "bg":              "#0a0e17",
    "bg_secondary":    "#0f1419",
    "bg_card":         "#1a1f2ecc",  # Semi-transparent for glass effect
    "bg_card_hover":   "#1f2535dd",
    "bg_elevated":     "#232936ee",
    
    # Gradient backgrounds
    "bg_gradient_start": "#0a0e17",
    "bg_gradient_end":   "#151a28",
    
    # Text — high contrast with vibrant accents
    "text":            "#e8eaed",
    "text_secondary":  "#9ca3af",
    "text_muted":      "#6b7280",
    "text_bright":     "#ffffff",

    # Accent — vibrant cyan/blue gradient
    "accent":          "#06b6d4",
    "accent_secondary":"#3b82f6",
    "accent_dim":      "#06b6d420",
    "accent_hover":    "#22d3ee",
    "accent_glow":     "#06b6d440",
    
    # Vibrant gradients for visual interest
    "gradient_cyan":   ["#06b6d4", "#3b82f6"],
    "gradient_purple": ["#a855f7", "#ec4899"],
    "gradient_green":  ["#10b981", "#06b6d4"],
    "gradient_orange": ["#f59e0b", "#ef4444"],

    # Borders — subtle with glow
    "border":          "#1f2937",
    "border_bright":   "#374151",
    "card_border":     "#ffffff10",
    "card_glow":       "#06b6d410",

    # Graphs — vibrant, distinct colors
    "graph_cpu":       "#06b6d4",
    "graph_ram":       "#a855f7",
    "graph_disk":      "#f59e0b",
    "graph_net":       "#10b981",
    "graph_fill":      "32",
    
    # Gradient versions for charts
    "graph_cpu_gradient":   ["#06b6d4", "#0891b2"],
    "graph_ram_gradient":   ["#a855f7", "#9333ea"],
    "graph_disk_gradient":  ["#f59e0b", "#d97706"],
    "graph_net_gradient":   ["#10b981", "#059669"],

    # Interactive states
    "selection":       "#1e3a8a40",
    "row_hover":       "#1f293780",
    "scrollbar":       "#374151",
    "scrollbar_hover": "#4b5563",

    # Tabs
    "tab_active":      "#e8eaed",
    "tab_inactive":    "#6b7280",

    # Inputs
    "input_bg":        "#111827cc",
    "input_focus":     "#1f2937ee",
    "input_border":    "#374151",

    # Structure
    "header_bg":       "#0f1419",
    "grid_line":       "#1f2937",
    "statusbar_bg":    "#0a0e17",

    # Semantic — vibrant, clear
    "danger":          "#ef4444",
    "danger_glow":     "#ef444430",
    "warning":         "#f59e0b",
    "warning_glow":    "#f59e0b30",
    "success":         "#10b981",
    "success_glow":    "#10b98130",
    
    "separator":       "#06b6d430",
    "status_run":      "#10b981",
    "status_stop":     "#ef4444",
    "status_sleep":    "#f59e0b",
    "mem_highlight":   "#a855f7",

    # Toolbar
    "toolbar_gradient_start": "#0f1419",
    "toolbar_gradient_end":   "#1a1f2e",
    "title_glow":      "#06b6d420",
    
    # Blur amounts for glassmorphism
    "blur_light":      8,
    "blur_medium":     12,
    "blur_heavy":      16,
}

# ── Light Theme — bright glassmorphism design ──────────────────────
LIGHT = {
    # Surfaces — glassmorphic layers
    "bg":              "#f8f9fb",
    "bg_secondary":    "#f3f4f6",
    "bg_card":         "#ffffffdd",  # Semi-transparent for glass effect
    "bg_card_hover":   "#ffffffee",
    "bg_elevated":     "#fffffff8",
    
    # Gradient backgrounds
    "bg_gradient_start": "#f8f9fb",
    "bg_gradient_end":   "#e5e7eb",

    # Text — sharp contrast
    "text":            "#111827",
    "text_secondary":  "#6b7280",
    "text_muted":      "#9ca3af",
    "text_bright":     "#000000",

    # Accent — vibrant blue
    "accent":          "#3b82f6",
    "accent_secondary":"#06b6d4",
    "accent_dim":      "#3b82f620",
    "accent_hover":    "#2563eb",
    "accent_glow":     "#3b82f640",
    
    # Vibrant gradients
    "gradient_cyan":   ["#06b6d4", "#3b82f6"],
    "gradient_purple": ["#a855f7", "#ec4899"],
    "gradient_green":  ["#10b981", "#06b6d4"],
    "gradient_orange": ["#f59e0b", "#ef4444"],

    # Borders — clean with subtle shadows
    "border":          "#e5e7eb",
    "border_bright":   "#d1d5db",
    "card_border":     "#00000010",
    "card_glow":       "#3b82f610",

    # Graphs — vibrant, clear
    "graph_cpu":       "#3b82f6",
    "graph_ram":       "#a855f7",
    "graph_disk":      "#f59e0b",
    "graph_net":       "#10b981",
    "graph_fill":      "24",
    
    # Gradient versions
    "graph_cpu_gradient":   ["#3b82f6", "#2563eb"],
    "graph_ram_gradient":   ["#a855f7", "#9333ea"],
    "graph_disk_gradient":  ["#f59e0b", "#d97706"],
    "graph_net_gradient":   ["#10b981", "#059669"],

    # Interactive states
    "selection":       "#dbeafe",
    "row_hover":       "#f3f4f6",
    "scrollbar":       "#d1d5db",
    "scrollbar_hover": "#9ca3af",

    # Tabs
    "tab_active":      "#111827",
    "tab_inactive":    "#9ca3af",

    # Inputs
    "input_bg":        "#f3f4f6dd",
    "input_focus":     "#ffffffee",
    "input_border":    "#d1d5db",

    # Structure
    "header_bg":       "#f3f4f6",
    "grid_line":       "#e5e7eb",
    "statusbar_bg":    "#f8f9fb",

    # Semantic — vibrant
    "danger":          "#ef4444",
    "danger_glow":     "#ef444430",
    "warning":         "#f59e0b",
    "warning_glow":    "#f59e0b30",
    "success":         "#10b981",
    "success_glow":    "#10b98130",
    
    "separator":       "#3b82f630",
    "status_run":      "#10b981",
    "status_stop":     "#ef4444",
    "status_sleep":    "#f59e0b",
    "mem_highlight":   "#a855f7",

    # Toolbar
    "toolbar_gradient_start": "#f3f4f6",
    "toolbar_gradient_end":   "#e5e7eb",
    "title_glow":      "#3b82f620",
    
    # Blur amounts
    "blur_light":      6,
    "blur_medium":     10,
    "blur_heavy":      14,
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
