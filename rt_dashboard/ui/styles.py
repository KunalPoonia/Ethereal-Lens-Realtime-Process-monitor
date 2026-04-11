# ─── Styles ──────────────────────────────────────────────────────────
# Apple-grade minimalist QSS.
# Philosophy: invisible chrome, perfect typography, breathing room.


def build_stylesheet(theme: dict) -> str:
    """Generate full QSS for the given theme dict."""
    t = theme
    is_dark = t["bg"] in ("#000000", "#0A0A0A")

    # Subtle separator: barely-there 1px line
    sep = t["border_subtle"]

    return f"""

    /* ═══════════════════════════════════════════════════════════
       GLOBAL
       ═══════════════════════════════════════════════════════════ */
    * {{
        font-family: "Segoe UI Variable Display", "Segoe UI", "SF Pro Display", system-ui;
        outline: none;
    }}

    QMainWindow, QWidget#centralWidget {{
        background-color: {t["bg"]};
    }}

    /* ═══════════════════════════════════════════════════════════
       TAB BAR — framing the document
       ═══════════════════════════════════════════════════════════ */
    QTabWidget::pane {{
        border: none;
        background: {t["bg"]};
    }}

    QTabBar {{
        background: {t["bg"]};
        border: none;
        border-bottom: 1px solid {t["border_subtle"]};
    }}

    QTabBar::tab {{
        background: {t["bg"]};
        color: {t["text3"]};
        padding: 10px 20px;
        margin: 0;
        border: none;
        border-bottom: 2px solid transparent;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.2px;
    }}

    QTabBar::tab:selected {{
        color: {t["text"]};
        font-weight: 600;
        border-bottom: 2px solid {t["text"]};
    }}

    QTabBar::tab:hover:!selected {{
        color: {t["text2"]};
    }}

    /* ═══════════════════════════════════════════════════════════
       SEARCH BAR
       ═══════════════════════════════════════════════════════════ */
    QLineEdit#searchBar {{
        background-color: {t["surface"]};
        color: {t["text"]};
        border: 1px solid {t["border_subtle"]};
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 13px;
        selection-background-color: {t["selection"]};
        selection-color: {t["surface"]};
    }}

    QLineEdit#searchBar:focus {{
        border-color: {t["border"]};
    }}

    QLineEdit#searchBar::placeholder {{
        color: {t["text3"]};
    }}

    /* ═══════════════════════════════════════════════════════════
       BUTTONS
       ═══════════════════════════════════════════════════════════ */
    QPushButton#headerBtn {{
        background: transparent;
        color: {t["text"]};
        border: 1px solid {t["border_subtle"]};
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
    }}

    QPushButton#headerBtn:hover {{
        background-color: {t["bg"]};
    }}

    QPushButton#headerBtn:pressed {{
        background-color: {t["border_subtle"]};
    }}

    QPushButton#endTaskBtn {{
        background: transparent;
        color: {t["danger"]};
        border: none;
        border-radius: 6px;
        padding: 6px 16px;
        font-weight: 500;
    }}

    QPushButton#endTaskBtn:hover {{
        background-color: {t["danger"]};
        color: {t["surface"]};
    }}

    /* ═══════════════════════════════════════════════════════════
       TREE WIDGET
       ═══════════════════════════════════════════════════════════ */
    QTreeWidget {{
        background-color: {t["surface"]};
        color: {t["text"]};
        border: none;
        font-size: 12.5px;
    }}

    QTreeWidget::item {{
        padding: 1px 0;
        border: none;
        min-height: 26px;
    }}

    QTreeWidget::item:selected {{
        background-color: {t["selection"]};
        color: #FFFFFF;
        border-radius: 0;
    }}

    QTreeWidget::item:hover:!selected {{
        background-color: {t["hover"]};
    }}

    QTreeWidget::branch {{
        background: transparent;
        border: none;
    }}

    QTreeWidget::branch:has-children:closed,
    QTreeWidget::branch:has-children:open {{
        image: none;
    }}

    /* ═══════════════════════════════════════════════════════════
       HEADER VIEW
       ═══════════════════════════════════════════════════════════ */
    QHeaderView {{
        background: {t["surface"]};
        border: none;
    }}

    QHeaderView::section {{
        background: {t["surface"]};
        color: {t["text"]};
        border: none;
        border-bottom: 1px solid {t["border_subtle"]};
        padding: 8px 10px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ═══════════════════════════════════════════════════════════
       SCROLLBARS
       ═══════════════════════════════════════════════════════════ */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 4px 1px;
    }}

    QScrollBar::handle:vertical {{
        background: {t["border"]};
        border-radius: 3px;
        min-height: 40px;
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
        height: 0;
    }}

    /* ═══════════════════════════════════════════════════════════
       STATUS BAR
       ═══════════════════════════════════════════════════════════ */
    QStatusBar {{
        background: {t["bg"]};
        color: {t["text"]};
        border-top: 1px solid {t["border"]};
        font-size: 11px;
        padding: 2px 12px;
    }}

    /* ═══════════════════════════════════════════════════════════
       PERFORMANCE CARDS
       ═══════════════════════════════════════════════════════════ */
    QFrame#perfCard {{
        background-color: {t["surface"]};
        border: 1px solid {t["border_subtle"]};
        border-radius: 12px;
    }}

    QLabel#perfTitle {{
        color: {t["text"]};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.8px;
    }}

    QLabel#perfValue {{
        color: {t["text"]};
        font-size: 28px;
        font-weight: 300;
        letter-spacing: -0.5px;
    }}

    QLabel#perfSubtext {{
        color: {t["text3"]};
        font-size: 11px;
    }}

    /* ═══════════════════════════════════════════════════════════
       CONTEXT MENU
       ═══════════════════════════════════════════════════════════ */
    QMenu {{
        background-color: {t["surface"]};
        color: {t["text"]};
        border: 1px solid {t["border"]};
        border-radius: 10px;
        padding: 6px 0;
        font-size: 13px;
    }}

    QMenu::item {{
        padding: 7px 28px;
        border-radius: 4px;
        margin: 0 6px;
    }}

    QMenu::item:selected {{
        background-color: {t["selection"]};
        color: #FFFFFF;
    }}

    QMenu::separator {{
        height: 1px;
        background: {t["border_subtle"]};
        margin: 4px 12px;
    }}

    QToolTip {{
        background-color: {t["surface"]};
        color: {t["text"]};
        border: 1px solid {t["border"]};
        padding: 6px 10px;
        border-radius: 6px;
    }}
    """
