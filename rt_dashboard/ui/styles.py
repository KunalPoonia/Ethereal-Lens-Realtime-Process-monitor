# ─── QSS Stylesheet Generator ────────────────────────────────────────
# Returns QSS strings for dark / light themes using colour dicts.

from config import DARK, LIGHT


def _build_qss(c: dict) -> str:
    """Build a full QSS stylesheet from a colour palette dict."""
    return f"""
    /* ── Global ───────────────────────────────────────────────────── */
    QWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }}

    /* ── Tab Widget ───────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: none;
        background: {c['bg']};
    }}
    QTabBar {{
        background: {c['bg_secondary']};
    }}
    QTabBar::tab {{
        background: {c['bg_secondary']};
        color: {c['text_secondary']};
        padding: 10px 28px;
        margin: 0px;
        border: none;
        border-bottom: 3px solid transparent;
        font-weight: 600;
        font-size: 14px;
    }}
    QTabBar::tab:selected {{
        color: {c['text']};
        border-bottom: 3px solid {c['tab_active']};
        background: {c['bg']};
    }}
    QTabBar::tab:hover:!selected {{
        color: {c['text']};
        background: {c['bg']};
    }}

    /* ── Table ────────────────────────────────────────────────────── */
    QTableWidget {{
        background-color: {c['bg_card']};
        gridline-color: {c['border']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        selection-background-color: {c['selection']};
    }}
    QTableWidget::item {{
        padding: 6px 10px;
        border: none;
    }}
    QTableWidget::item:hover {{
        background-color: {c['row_hover']};
    }}
    QHeaderView::section {{
        background-color: {c['header_bg']};
        color: {c['text']};
        padding: 8px 10px;
        border: none;
        border-bottom: 2px solid {c['border']};
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ── Search / Line Edit ───────────────────────────────────────── */
    QLineEdit {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 14px;
        color: {c['text']};
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border: 1px solid {c['accent']};
    }}

    /* ── Buttons ──────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {c['accent']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {c['accent_hover']};
    }}
    QPushButton:pressed {{
        background-color: {c['accent']};
    }}
    QPushButton#themeToggle {{
        background-color: {c['bg_card']};
        color: {c['text']};
        border: 1px solid {c['border']};
        padding: 6px 16px;
        font-size: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        border-radius: 18px;
    }}
    QPushButton#themeToggle:hover {{
        background-color: {c['accent']};
        color: #ffffff;
        border-color: {c['accent']};
    }}

    /* ── Labels ───────────────────────────────────────────────────── */
    QLabel {{
        background: transparent;
    }}
    QLabel#cardTitle {{
        font-size: 14px;
        font-weight: 700;
        color: {c['text']};
        letter-spacing: 0.3px;
    }}
    QLabel#cardValue {{
        font-size: 22px;
        font-weight: 700;
        color: {c['accent']};
    }}
    QLabel#cardSub {{
        font-size: 12px;
        color: {c['text_secondary']};
    }}
    QLabel#statusLabel {{
        font-size: 12px;
        color: {c['text_secondary']};
        padding: 4px 0;
    }}

    /* ── Card frames ──────────────────────────────────────────────── */
    QFrame#card {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}

    /* ── Toolbar ──────────────────────────────────────────────────── */
    QFrame#toolbar {{
        background-color: {c['bg_secondary']};
        border-bottom: 1px solid {c['border']};
    }}

    /* ── Scroll bars ──────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['scrollbar_hover']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ── Context menu ─────────────────────────────────────────────── */
    QMenu {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 4px 0;
    }}
    QMenu::item {{
        padding: 8px 24px;
        color: {c['text']};
    }}
    QMenu::item:selected {{
        background-color: {c['accent']};
        color: #ffffff;
    }}
    QMenu::separator {{
        height: 1px;
        background: {c['border']};
        margin: 4px 8px;
    }}
    """


def dark_qss() -> str:
    return _build_qss(DARK)

def light_qss() -> str:
    return _build_qss(LIGHT)
