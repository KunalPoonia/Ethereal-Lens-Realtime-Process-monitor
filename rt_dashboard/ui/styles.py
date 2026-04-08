# ─── QSS — Vibrant Glassmorphism Design ─────────────────────────────
# Design rules:
#   • Glassmorphic surfaces with translucency and depth
#   • Vibrant gradients and colors for visual interest
#   • Smooth transitions and hover effects
#   • Modern, clean typography with good contrast

from config import DARK, LIGHT


def _build_qss(c: dict) -> str:
    return f"""
    * {{ outline: none; }}

    QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI Variable', 'Inter', 'Segoe UI', system-ui;
        font-size: 13px;
        border: none;
    }}

    /* ── Tabs — vibrant underline with glow ──────────────────────── */
    QTabWidget::pane {{ border: none; }}
    QTabBar {{
        background: {c['bg_secondary']};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {c['tab_inactive']};
        padding: 14px 36px;
        border: none;
        border-bottom: 3px solid transparent;
        font-weight: 500;
        font-size: 13.5px;
        transition: all 0.2s ease;
    }}
    QTabBar::tab:selected {{
        color: {c['tab_active']};
        border-bottom-color: {c['accent']};
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        color: {c['text']};
        background: {c['accent_dim']};
    }}

    /* ── Tree (process list) — minimal lines ─────────────────────── */
    QTreeWidget {{
        background: {c['bg']};
        border: none;
        selection-background-color: {c['selection']};
        selection-color: {c['text']};
        font-size: 12.5px;
    }}
    QTreeWidget::item {{
        padding: 6px 12px;
        border-bottom: 1px solid {c['grid_line']};
    }}
    QTreeWidget::item:selected {{
        background: {c['selection']};
    }}
    QTreeWidget::item:hover:!selected {{
        background: {c['row_hover']};
    }}
    QTreeWidget::branch {{
        background: transparent;
        border-bottom: 1px solid {c['grid_line']};
    }}
    QTreeWidget::branch:has-children {{ image: none; }}

    QHeaderView {{ background: {c['bg']}; }}
    QHeaderView::section {{
        background: {c['bg']};
        color: {c['text_muted']};
        padding: 10px 12px;
        border: none;
        border-right: 1px solid {c['grid_line']};
        border-bottom: 1px solid {c['border']};
        font-weight: 600;
        font-size: 10.5px;
        letter-spacing: 0.6px;
    }}

    /* ── Inputs — glassmorphic with vibrant focus ────────────────── */
    QLineEdit {{
        background: {c['input_bg']};
        border: 1.5px solid {c['input_border']};
        border-radius: 10px;
        padding: 9px 16px;
        color: {c['text']};
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
        background: {c['input_focus']};
        border-width: 2px;
    }}

    /* ── Buttons — vibrant with glow effects ─────────────────────── */
    QPushButton {{
        background: {c['accent_dim']};
        color: {c['text']};
        border: 1.5px solid {c['border_bright']};
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 500;
        font-size: 12.5px;
    }}
    QPushButton:hover {{
        color: {c['text_bright']};
        border-color: {c['accent']};
        background: {c['accent_glow']};
    }}
    QPushButton:pressed {{
        background: {c['accent']};
        border-color: {c['accent']};
        color: {c['text_bright']};
    }}
    QPushButton:disabled {{
        color: {c['text_muted']};
        border-color: {c['border']};
        background: transparent;
    }}

    /* Theme toggle — circular with glow */
    QPushButton#themeToggle {{
        background: {c['bg_elevated']};
        border: 1.5px solid {c['border_bright']};
        min-width: 40px; max-width: 40px;
        min-height: 40px; max-height: 40px;
        border-radius: 20px;
        font-size: 16px; padding: 0;
    }}
    QPushButton#themeToggle:hover {{
        border-color: {c['accent']};
        background: {c['accent_dim']};
    }}

    /* End task — vibrant danger */
    QPushButton#actionButtonDanger {{
        color: {c['danger']};
        border-color: {c['danger']};
        background: {c['danger_glow']};
    }}
    QPushButton#actionButtonDanger:hover {{
        border-color: {c['danger']};
        background: {c['danger']};
        color: {c['text_bright']};
    }}

    /* ── Labels ───────────────────────────────────────────────────── */
    QLabel {{ background: transparent; }}
    QLabel#cardTitle {{
        font-size: 11px; font-weight: 500;
        color: {c['text_muted']};
        letter-spacing: 0.5px;
    }}
    QLabel#cardValue {{
        font-size: 32px; font-weight: 300;
        color: {c['text_bright']};
        letter-spacing: -0.5px;
    }}
    QLabel#cardSub {{
        font-size: 11px; color: {c['text_muted']};
    }}

    /* ── Cards — glassmorphic with glow ─────────────────────────── */
    QFrame#card {{
        background: {c['bg_card']};
        border: 1px solid {c['card_border']};
        border-radius: 14px;
    }}
    QFrame#card:hover {{
        background: {c['bg_card_hover']};
        border-color: {c['accent_dim']};
    }}
    
    /* Glassmorphic card variant */
    QFrame#glassCard {{
        background: {c['bg_card']};
        border: 1.5px solid {c['card_border']};
        border-radius: 14px;
    }}
    QFrame#glassCard:hover {{
        background: {c['bg_card_hover']};
        border-color: {c['card_glow']};
    }}

    /* ── Toolbar — flat blend ────────────────────────────────────── */
    QFrame#toolbar {{
        background: {c['bg_secondary']};
        border-bottom: 1px solid {c['border']};
    }}
    QFrame#processToolbar {{
        background: {c['bg']};
        border-bottom: 1px solid {c['grid_line']};
    }}

    /* ── Status bar ───────────────────────────────────────────────── */
    QFrame#statusbar {{
        background: {c['statusbar_bg']};
        border-top: 1px solid {c['border']};
    }}
    QFrame#statusbar QLabel {{
        font-size: 11px; color: {c['text_muted']};
    }}

    /* ── Scrollbar — whisper thin ─────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent; width: 5px;
        margin: 6px 1px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        border-radius: 2px;
        min-height: 48px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_hover']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        height: 0; background: transparent;
    }}
    QScrollBar:horizontal {{ height: 0; }}

    /* ── Menus ────────────────────────────────────────────────────── */
    QMenu {{
        background: {c['bg_elevated']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 22px;
        border-radius: 6px;
        color: {c['text']};
    }}
    QMenu::item:selected {{
        background: {c['selection']};
    }}
    QMenu::separator {{
        height: 1px;
        background: {c['border']};
        margin: 4px 10px;
    }}

    /* ── Tooltips ─────────────────────────────────────────────────── */
    QToolTip {{
        background: {c['bg_elevated']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 11px;
    }}
    """


def dark_qss() -> str:
    return _build_qss(DARK)

def light_qss() -> str:
    return _build_qss(LIGHT)
