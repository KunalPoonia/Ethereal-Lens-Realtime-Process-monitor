# ─── Clean Card Component ────────────────────────────────────────────
# Minimal card with subtle shadow and soft hover elevation

from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor


class GlassCard(QFrame):
    """
    Clean card with:
    - Flat background from QSS
    - Subtle shadow for depth
    - Gentle hover elevation
    """

    def __init__(self, parent=None, blur_radius=12, border_gradient=None):
        super().__init__(parent)
        self._hover_elevation = 0.0

        self.setObjectName("glassCard")

        # Subtle shadow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(12)
        self._shadow.setColor(QColor(0, 0, 0, 30))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)

        # Hover animation
        self._elevation_anim = QPropertyAnimation(self, b"elevation")
        self._elevation_anim.setDuration(200)
        self._elevation_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def elevation(self):
        return self._hover_elevation

    @elevation.setter
    def elevation(self, value):
        self._hover_elevation = value
        self._shadow.setBlurRadius(12 + value * 6)
        self._shadow.setOffset(0, 2 + value * 2)

    def set_corner_radius(self, radius):
        pass  # Handled via QSS

    def enterEvent(self, event):
        super().enterEvent(event)
        self._elevation_anim.stop()
        self._elevation_anim.setStartValue(self._hover_elevation)
        self._elevation_anim.setEndValue(1.0)
        self._elevation_anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._elevation_anim.stop()
        self._elevation_anim.setStartValue(self._hover_elevation)
        self._elevation_anim.setEndValue(0.0)
        self._elevation_anim.start()
