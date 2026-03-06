# ─── Premium QSS Themes ──────────────────────────────────────────────

from config import DARK, LIGHT


def _build_qss(c: dict) -> str:
    return f"""
    /* ── Reset & Base ─────────────────────────────────────────────── */
    * {{
        outline: none;
    }}
    QWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', system-ui;
        font-size: 13px;
        border: none;
    }}

    /* ── Tab Widget ───────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: none;
        background: {c['bg']};
    }}
    QTabBar {{
        background: transparent;
        border: none;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {c['tab_inactive']};
        padding: 12px 32px;
        margin: 0;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 500;
        font-size: 13px;
        letter-spacing: 0.4px;
    }}
    QTabBar::tab:selected {{
        color: {c['text']};
        border-bottom: 2px solid {c['tab_active']};
    }}
    QTabBar::tab:hover:!selected {{
        color: {c['text_secondary']};
    }}

    /* ── Table ────────────────────────────────────────────────────── */
    QTableWidget {{
        background-color: transparent;
        alternate-background-color: transparent;
        gridline-color: transparent;
        border: none;
        selection-background-color: {c['selection']};
        selection-color: {c['text']};
        font-size: 12.5px;
    }}
    QTableWidget::item {{
        padding: 7px 12px;
        border-bottom: 1px solid {c['border_subtle']};
        background-color: transparent;
        color: {c['text']};
    }}
    QTableWidget::item:selected {{
        background-color: {c['selection']};
        color: {c['text']};
    }}
    QTableWidget::item:hover {{
        background-color: {c['row_hover']};
        color: {c['text']};
    }}
    QHeaderView {{
        background: transparent;
        border: none;
    }}
    QHeaderView::section {{
        background-color: transparent;
        color: {c['text_muted']};
        padding: 10px 12px;
        border: none;
        border-bottom: 1px solid {c['border']};
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    /* ── Search / Input ───────────────────────────────────────────── */
    QLineEdit {{
        background-color: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 9px 16px;
        color: {c['text']};
        font-size: 13px;
        selection-background-color: {c['accent_dim']};
        selection-color: {c['text']};
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
    }}

    /* ── Buttons ──────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {c['accent']};
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 9px 22px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {c['accent_hover']};
    }}
    QPushButton#themeToggle {{
        background-color: transparent;
        color: {c['text_secondary']};
        border: 1px solid {c['border']};
        padding: 0;
        font-size: 16px;
        min-width: 38px; max-width: 38px;
        min-height: 38px; max-height: 38px;
        border-radius: 19px;
    }}
    QPushButton#themeToggle:hover {{
        background-color: {c['accent_dim']};
        color: {c['accent']};
        border-color: {c['accent']};
    }}

    /* ── Labels ───────────────────────────────────────────────────── */
    QLabel {{
        background: transparent;
        border: none;
    }}
    QLabel#cardTitle {{
        font-size: 11px;
        font-weight: 600;
        color: {c['text_muted']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    QLabel#cardValue {{
        font-size: 28px;
        font-weight: 700;
        color: {c['text']};
        letter-spacing: -0.5px;
    }}
    QLabel#cardSub {{
        font-size: 11.5px;
        color: {c['text_secondary']};
    }}
    QLabel#statusLabel {{
        font-size: 12px;
        color: {c['text_muted']};
    }}

    /* ── Card frame ───────────────────────────────────────────────── */
    QFrame#card {{
        background-color: {c['bg_card']};
        border: 1px solid {c['card_border']};
        border-radius: 16px;
    }}

    /* ── Toolbar ──────────────────────────────────────────────────── */
    QFrame#toolbar {{
        background-color: {c['bg_secondary']};
        border: none;
        border-bottom: 1px solid {c['border']};
    }}

    /* ── Scrollbars ───────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 4px 0;
    }}
    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        border-radius: 3px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_hover']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        height: 0; background: transparent;
    }}
    QScrollBar:horizontal {{
        height: 0;
    }}

    /* ── Context menu ─────────────────────────────────────────────── */
    QMenu {{
        background-color: {c['bg_card']};
        border: 1px solid {c['card_border']};
        border-radius: 12px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 20px;
        border-radius: 6px;
        color: {c['text']};
        font-size: 12.5px;
    }}
    QMenu::item:selected {{
        background-color: {c['accent_dim']};
        color: {c['accent']};
    }}
    QMenu::separator {{
        height: 1px;
        background: {c['border']};
        margin: 4px 10px;
    }}
    """


def dark_qss() -> str:
    return _build_qss(DARK)

def light_qss() -> str:
    return _build_qss(LIGHT)
