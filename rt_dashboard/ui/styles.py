# ─── QSS — Smooth, minimal, low-contrast ────────────────────────────
# Design rules:
#   • Borders are barely visible — structure through spacing, not lines
#   • Single font weight hierarchy — Regular / Medium / SemiBold only
#   • Transitions feel continuous — no jarring color jumps
#   • Hover states are subtle shifts, not color changes

from config import DARK, LIGHT


def _build_qss(c: dict) -> str:
    return f"""
    * {{ outline: none; }}

    QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI Variable', 'Segoe UI', system-ui;
        font-size: 13px;
        border: none;
    }}

    /* ── Tabs — clean underline indicator ─────────────────────────── */
    QTabWidget::pane {{ border: none; }}
    QTabBar {{
        background: {c['bg_secondary']};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {c['tab_inactive']};
        padding: 13px 32px;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 500;
        font-size: 13px;
    }}
    QTabBar::tab:selected {{
        color: {c['tab_active']};
        border-bottom-color: {c['accent']};
    }}
    QTabBar::tab:hover:!selected {{
        color: {c['text_secondary']};
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

    /* ── Inputs — subtle recessed look ───────────────────────────── */
    QLineEdit {{
        background: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 14px;
        color: {c['text']};
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
        background: {c['input_focus']};
    }}

    /* ── Buttons — ghost style, subtle hover ─────────────────────── */
    QPushButton {{
        background: transparent;
        color: {c['text_secondary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 18px;
        font-weight: 500;
        font-size: 12px;
    }}
    QPushButton:hover {{
        color: {c['text']};
        border-color: {c['text_muted']};
        background: {c['accent_dim']};
    }}
    QPushButton:pressed {{
        background: {c['accent_glow']};
    }}
    QPushButton:disabled {{
        color: {c['text_muted']};
        border-color: {c['border']};
    }}

    /* Theme toggle — circular, minimal */
    QPushButton#themeToggle {{
        background: transparent;
        border: 1px solid {c['border']};
        min-width: 36px; max-width: 36px;
        min-height: 36px; max-height: 36px;
        border-radius: 18px;
        font-size: 14px; padding: 0;
    }}
    QPushButton#themeToggle:hover {{
        border-color: {c['text_muted']};
        background: {c['accent_dim']};
    }}

    /* End task — soft danger */
    QPushButton#actionButtonDanger {{
        color: {c['danger']};
        border-color: {c['border']};
    }}
    QPushButton#actionButtonDanger:hover {{
        border-color: {c['danger']};
        background: {c['danger_glow']};
    }}

    /* ── Labels ───────────────────────────────────────────────────── */
    QLabel {{ background: transparent; }}
    QLabel#cardTitle {{
        font-size: 11px; font-weight: 500;
        color: {c['text_muted']};
        letter-spacing: 0.5px;
    }}
    QLabel#cardValue {{
        font-size: 28px; font-weight: 300;
        color: {c['text']};
    }}
    QLabel#cardSub {{
        font-size: 11px; color: {c['text_muted']};
    }}

    /* ── Cards — barely there borders ────────────────────────────── */
    QFrame#card {{
        background: {c['bg_card']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
    }}
    QFrame#card:hover {{
        background: {c['bg_card_hover']};
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
