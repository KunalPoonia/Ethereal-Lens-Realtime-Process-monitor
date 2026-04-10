# ─── Entry Point ─────────────────────────────────────────────────────
# Launch the Real-Time Process Dashboard.

import sys
import os

# Ensure the rt_dashboard package folder is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui.main_window import MainWindow


def main():
    # High-DPI support
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Real-Time Process Dashboard")

    # Build a complete custom palette — prevents ALL OS accent color leakage
    palette = QPalette()
    # Window / base surfaces
    palette.setColor(QPalette.ColorRole.Window, QColor("#111318"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#c8cad0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#15171d"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1a1d24"))
    # Text
    palette.setColor(QPalette.ColorRole.Text, QColor("#c8cad0"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#e4e5ea"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#5c6070"))
    # Buttons
    palette.setColor(QPalette.ColorRole.Button, QColor("#1a1d24"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#c8cad0"))
    # Selection / highlight
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2d3350"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#e4e5ea"))
    # Links
    palette.setColor(QPalette.ColorRole.Link, QColor("#6e7baa"))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#5c6894"))
    # Decorations
    palette.setColor(QPalette.ColorRole.Light, QColor("#2d313b"))
    palette.setColor(QPalette.ColorRole.Midlight, QColor("#23262f"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#1e2129"))
    palette.setColor(QPalette.ColorRole.Dark, QColor("#111318"))
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1e2129"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#c8cad0"))
    # Inactive group (unfocused windows)
    for role, color in [
        (QPalette.ColorRole.Highlight, "#23262f"),
        (QPalette.ColorRole.HighlightedText, "#c8cad0"),
        (QPalette.ColorRole.Button, "#1a1d24"),
        (QPalette.ColorRole.ButtonText, "#8b8f99"),
    ]:
        palette.setColor(QPalette.ColorGroup.Inactive, role, QColor(color))
    # Disabled group
    for role, color in [
        (QPalette.ColorRole.WindowText, "#3a3f4b"),
        (QPalette.ColorRole.Text, "#3a3f4b"),
        (QPalette.ColorRole.ButtonText, "#3a3f4b"),
        (QPalette.ColorRole.Highlight, "#1a1d24"),
        (QPalette.ColorRole.HighlightedText, "#3a3f4b"),
    ]:
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(color))

    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
