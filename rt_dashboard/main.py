# ─── Entry Point ─────────────────────────────────────────────────────

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from config import LIGHT


def _build_palette():
    """Neutral palette for Qt widget-level rendering."""
    p = QPalette()
    d = LIGHT
    p.setColor(QPalette.ColorRole.Window,          QColor(d["bg"]))
    p.setColor(QPalette.ColorRole.WindowText,      QColor(d["text"]))
    p.setColor(QPalette.ColorRole.Base,            QColor(d["surface"]))
    p.setColor(QPalette.ColorRole.AlternateBase,   QColor(d["surface2"]))
    p.setColor(QPalette.ColorRole.Text,            QColor(d["text"]))
    p.setColor(QPalette.ColorRole.BrightText,      QColor("#FFFFFF"))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor(d["text3"]))
    p.setColor(QPalette.ColorRole.Button,          QColor(d["surface"]))
    p.setColor(QPalette.ColorRole.ButtonText,      QColor(d["text"]))
    p.setColor(QPalette.ColorRole.Highlight,       QColor(d["selection"]))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(d["text"]))
    p.setColor(QPalette.ColorRole.Link,            QColor(d["text2"]))
    p.setColor(QPalette.ColorRole.LinkVisited,     QColor(d["text3"]))
    p.setColor(QPalette.ColorRole.Light,           QColor(d["surface"]))
    p.setColor(QPalette.ColorRole.Midlight,        QColor(d["border_subtle"]))
    p.setColor(QPalette.ColorRole.Mid,             QColor(d["border"]))
    p.setColor(QPalette.ColorRole.Dark,            QColor(d["surface2"]))
    p.setColor(QPalette.ColorRole.Shadow,          QColor("#00000020"))
    p.setColor(QPalette.ColorRole.ToolTipBase,     QColor(d["surface"]))
    p.setColor(QPalette.ColorRole.ToolTipText,     QColor(d["text"]))
    # Inactive
    for role, color in [
        (QPalette.ColorRole.Highlight, d["border_subtle"]),
        (QPalette.ColorRole.HighlightedText, d["text"]),
    ]:
        p.setColor(QPalette.ColorGroup.Inactive, role, QColor(color))
    # Disabled
    for role, color in [
        (QPalette.ColorRole.WindowText, d["text3"]),
        (QPalette.ColorRole.Text, d["text3"]),
        (QPalette.ColorRole.ButtonText, d["text3"]),
    ]:
        p.setColor(QPalette.ColorGroup.Disabled, role, QColor(color))
    return p


def main():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    app.setApplicationName("Process Monitor")
    app.setPalette(_build_palette())

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
