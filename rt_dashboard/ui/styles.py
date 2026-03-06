# ─── QSS Themes (Task Manager style) ─────────────────────────────────

from config import DARK, LIGHT


def _build_qss(c: dict) -> str:
    return f"""
    * {{ outline: none; }}

    QWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: 'Segoe UI Variable', 'Segoe UI', system-ui;
        font-size: 13px;
        border: none;
    }}

    /* ── Tab Widget ───────────────────────────────────────────────── */
    QTabWidget::pane {{ border: none; background: {c['bg']}; }}
    QTabBar {{ background: {c['bg_secondary']}; border: none; }}
    QTabBar::tab {{
        background: transparent;
        color: {c['tab_inactive']};
        padding: 10px 28px;
        border: none;
        border-bottom: 2px solid transparent;
        font-weight: 600; font-size: 13px;
    }}
    QTabBar::tab:selected {{
        color: {c['text']};
        border-bottom: 2px solid {c['tab_active']};
    }}
    QTabBar::tab:hover:!selected {{ color: {c['text_secondary']}; }}

    /* ── Tree Widget ──────────────────────────────────────────────── */
    QTreeWidget {{
        background-color: {c['bg']};
        alternate-background-color: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 0px;
        gridline-color: {c['grid_line']};
        selection-background-color: {c['selection']};
        selection-color: {c['text']};
        font-size: 12.5px;
    }}
    QTreeWidget::item {{
        padding: 4px 8px;
        border-right: 1px solid {c['grid_line']};
        border-bottom: 1px solid {c['grid_line']};
    }}
    QTreeWidget::item:selected {{
        background-color: {c['selection']};
        color: {c['text']};
    }}
    QTreeWidget::item:hover {{
        background-color: {c['row_hover']};
    }}
    QTreeWidget::branch {{
        background: transparent;
    }}
    QTreeWidget::branch:has-children:!has-siblings:closed,
    QTreeWidget::branch:closed:has-children:has-siblings {{
        image: none;
        border-image: none;
    }}
    QTreeWidget::branch:open:has-children:!has-siblings,
    QTreeWidget::branch:open:has-children:has-siblings {{
        image: none;
        border-image: none;
    }}

    QHeaderView {{
        background: {c['header_bg']};
        border: none;
    }}
    QHeaderView::section {{
        background-color: {c['header_bg']};
        color: {c['header_text']};
        padding: 8px 10px;
        border: none;
        border-right: 1px solid {c['grid_line']};
        border-bottom: 1px solid {c['border']};
        font-weight: 600; font-size: 11px;
    }}

    /* ── Search / Input ───────────────────────────────────────────── */
    QLineEdit {{
        background-color: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 6px 12px;
        color: {c['text']};
        font-size: 13px;
        selection-background-color: {c['accent_dim']};
        selection-color: {c['text']};
    }}
    QLineEdit:focus {{ border-color: {c['accent']}; }}

    /* ── Buttons ──────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {c['accent']};
        color: #ffffff;
        border: none; border-radius: 4px;
        padding: 6px 16px;
        font-weight: 600; font-size: 12px;
    }}
    QPushButton:hover {{ background-color: {c['accent_hover']}; }}
    QPushButton#themeToggle {{
        background-color: transparent;
        color: {c['text_secondary']};
        border: 1px solid {c['border']};
        padding: 0; font-size: 16px;
        min-width: 36px; max-width: 36px;
        min-height: 36px; max-height: 36px;
        border-radius: 18px;
    }}
    QPushButton#themeToggle:hover {{
        background-color: {c['accent_dim']};
        color: {c['accent']};
        border-color: {c['accent']};
    }}

    /* ── Labels ───────────────────────────────────────────────────── */
    QLabel {{ background: transparent; border: none; }}
    QLabel#cardTitle {{
        font-size: 11px; font-weight: 600;
        color: {c['text_muted']};
        text-transform: uppercase; letter-spacing: 1px;
    }}
    QLabel#cardValue {{
        font-size: 28px; font-weight: 700;
        color: {c['text']}; letter-spacing: -0.5px;
    }}
    QLabel#cardSub {{
        font-size: 11.5px; color: {c['text_secondary']};
    }}
    QLabel#statusLabel {{
        font-size: 12px; color: {c['text_muted']};
    }}

    /* ── Card frame ───────────────────────────────────────────────── */
    QFrame#card {{
        background-color: {c['bg_card']};
        border: 1px solid {c['card_border']};
        border-radius: 8px;
    }}

    /* ── Section separator ────────────────────────────────────────── */
    QFrame#sectionSep {{
        background-color: {c['border']};
        min-height: 2px; max-height: 2px;
    }}

    /* ── Toolbar ──────────────────────────────────────────────────── */
    QFrame#toolbar {{
        background-color: {c['bg_secondary']};
        border: none;
        border-bottom: 1px solid {c['border']};
    }}

    /* ── Status bar ───────────────────────────────────────────────── */
    QFrame#statusbar {{
        background-color: {c['statusbar_bg']};
        border-top: 1px solid {c['border']};
    }}
    QFrame#statusbar QLabel {{
        font-size: 11.5px;
        color: {c['text_secondary']};
        padding: 0 8px;
    }}

    /* ── Scrollbars ───────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent; width: 8px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {c['scrollbar']}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['scrollbar_hover']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        height: 0; background: transparent;
    }}
    QScrollBar:horizontal {{ height: 0; }}

    /* ── Context menu ─────────────────────────────────────────────── */
    QMenu {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px; padding: 4px;
    }}
    QMenu::item {{
        padding: 7px 20px; border-radius: 4px;
        color: {c['text']}; font-size: 12.5px;
    }}
    QMenu::item:selected {{
        background-color: {c['selection']};
        color: {c['text']};
    }}
    QMenu::separator {{
        height: 1px; background: {c['border']}; margin: 4px 8px;
    }}
    """


def dark_qss() -> str:
    return _build_qss(DARK)

def light_qss() -> str:
    return _build_qss(LIGHT)
