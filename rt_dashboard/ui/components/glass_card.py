# ─── Glassmorphic Card Component ────────────────────────────────────
# Translucent card with blur effect, gradients, and smooth animations

from PyQt6.QtWidgets import QFrame, QGraphicsBlurEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush


class GlassCard(QFrame):
    """
    A glassmorphic card with:
    - Semi-transparent background
    - Blur effect (simulated with shadow)
    - Smooth hover animations
    - Optional gradient border
    - Customizable corner radius
    """
    
    def __init__(self, parent=None, blur_radius=12, border_gradient=None):
        super().__init__(parent)
        self._blur_radius = blur_radius
        self._border_gradient = border_gradient
        self._hover_elevation = 0.0
        self._corner_radius = 12
        
        self.setObjectName("glassCard")
        
        # Add subtle shadow for depth
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(20)
        self._shadow.setColor(QColor(0, 0, 0, 60))
        self._shadow.setOffset(0, 4)
        self.setGraphicsEffect(self._shadow)
        
        # Hover animation for elevation
        self._elevation_anim = QPropertyAnimation(self, b"elevation")
        self._elevation_anim.setDuration(250)
        self._elevation_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    @pyqtProperty(float)
    def elevation(self):
        return self._hover_elevation
    
    @elevation.setter
    def elevation(self, value):
        self._hover_elevation = value
        self._shadow.setBlurRadius(20 + value * 10)
        self._shadow.setOffset(0, 4 + value * 4)
        self.update()
    
    def set_corner_radius(self, radius):
        self._corner_radius = radius
        self.update()
    
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
    
    def paintEvent(self, event):
        """Custom paint for gradient border if specified"""
        super().paintEvent(event)
        
        if self._border_gradient:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw gradient border
            rect = self.rect().adjusted(1, 1, -1, -1)
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(self._border_gradient[0]))
            gradient.setColorAt(1, QColor(self._border_gradient[1]))
            
            pen = QPen(QBrush(gradient), 1.5)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)


class GradientBackground(QFrame):
    """
    Animated gradient background for modern look
    """
    
    def __init__(self, color1, color2, parent=None, angle=135):
        super().__init__(parent)
        self._color1 = QColor(color1)
        self._color2 = QColor(color2)
        self._angle = angle
        self._gradient_shift = 0.0
        
        # Optional: Animate gradient shift
        self._shift_anim = QPropertyAnimation(self, b"gradientShift")
        self._shift_anim.setDuration(8000)
        self._shift_anim.setStartValue(0.0)
        self._shift_anim.setEndValue(1.0)
        self._shift_anim.setLoopCount(-1)  # Infinite loop
        self._shift_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    
    @pyqtProperty(float)
    def gradientShift(self):
        return self._gradient_shift
    
    @gradientShift.setter
    def gradientShift(self, value):
        self._gradient_shift = value
        self.update()
    
    def start_animation(self):
        self._shift_anim.start()
    
    def stop_animation(self):
        self._shift_anim.stop()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate gradient points based on angle
        rect = self.rect()
        if self._angle == 135:  # Diagonal
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        elif self._angle == 90:  # Vertical
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        else:  # Horizontal
            gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        
        # Apply animated shift (subtle variation)
        c1 = QColor(self._color1)
        c2 = QColor(self._color2)
        
        shift = int(self._gradient_shift * 20)
        c1.setHsv(c1.hue(), max(0, c1.saturation() - shift), c1.value())
        c2.setHsv(c2.hue(), max(0, c2.saturation() - shift), c2.value())
        
        gradient.setColorAt(0, c1)
        gradient.setColorAt(1, c2)
        
        painter.fillRect(rect, gradient)
