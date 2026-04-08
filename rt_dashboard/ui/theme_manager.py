# ─── Theme Utilities ─────────────────────────────────────────────────
# Auto theme detection and management

import sys
from PyQt6.QtCore import QSettings


def get_windows_theme() -> str:
    """
    Detect Windows theme (dark/light) from registry.
    Returns 'dark' or 'light'.
    """
    if sys.platform != 'win32':
        return 'dark'
    
    try:
        import winreg
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(
            registry,
            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        )
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        
        # 0 = Dark, 1 = Light
        return 'light' if value == 1 else 'dark'
    except Exception:
        return 'dark'


class ThemeManager:
    """Manages application theme with auto-detection support"""
    
    MODE_AUTO = 'auto'
    MODE_DARK = 'dark'
    MODE_LIGHT = 'light'
    
    def __init__(self):
        self._settings = QSettings('ProcessMonitor', 'Theme')
        self._mode = self._settings.value('mode', self.MODE_AUTO)
    
    def get_mode(self) -> str:
        """Get current theme mode (auto/dark/light)"""
        return self._mode
    
    def set_mode(self, mode: str):
        """Set theme mode"""
        if mode in (self.MODE_AUTO, self.MODE_DARK, self.MODE_LIGHT):
            self._mode = mode
            self._settings.setValue('mode', mode)
    
    def get_effective_theme(self) -> str:
        """Get the actual theme to use (dark/light)"""
        if self._mode == self.MODE_AUTO:
            return get_windows_theme()
        else:
            return self._mode
    
    def is_dark(self) -> bool:
        """Check if current effective theme is dark"""
        return self.get_effective_theme() == 'dark'
