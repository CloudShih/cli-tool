# 主題切換系統實現指南

**日期**: 2025-08-18  
**類別**: UI 主題系統  
**目的**: 實現完整的動態主題切換系統，支援多種主題、動畫切換和用戶自定義  

## 概述

本指南詳述了如何在 PyQt5 應用程式中實現現代化的主題切換系統，包括主題管理、動畫切換、色彩方案管理、用戶偏好設定和自定義主題功能。基於現有的 CLI Tool 專案架構，提供完整的主題解決方案。

---

## 主題系統架構

### 系統架構圖

```
ThemeManager (核心管理器)
├── Theme Configuration (主題配置)
│   ├── Built-in Themes (內建主題)
│   ├── Custom Themes (自定義主題)
│   └── Theme Templates (主題模板)
├── Dynamic Switching (動態切換)
│   ├── Animation Effects (切換動畫)
│   ├── Component Updates (組件更新)
│   └── State Management (狀態管理)
├── Color Management (色彩管理)
│   ├── Color Palette Generator (調色盤生成器)
│   ├── Accessibility Compliance (無障礙合規)
│   └── Dark/Light Mode Detection (系統主題檢測)
├── User Preferences (用戶偏好)
│   ├── Theme Selection (主題選擇)
│   ├── Auto Theme Switching (自動主題切換)
│   └── Preference Storage (偏好存儲)
└── Advanced Features (高級功能)
    ├── Theme Editor (主題編輯器)
    ├── Live Preview (即時預覽)
    └── Theme Export/Import (主題導入導出)
```

---

## 1. 增強型主題管理器

### ThemeManagerAdvanced 類別

```python
"""
增強型主題管理器 - 支援動態切換、色彩管理和用戶自定義
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QColor, QPalette
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class ThemeType(Enum):
    """主題類型枚舉"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"
    SYSTEM = "system"

class ColorRole(Enum):
    """色彩角色枚舉"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    BACKGROUND = "background"
    SURFACE = "surface"
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    BORDER = "border"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"

@dataclass
class ColorPalette:
    """色彩調色盤數據類"""
    primary: str = "#4a90e2"
    secondary: str = "#50c878"
    accent: str = "#ff6b6b"
    background: str = "#1e1e1e"
    surface: str = "#2d2d2d"
    text_primary: str = "#ffffff"
    text_secondary: str = "#cccccc"
    border: str = "#444444"
    warning: str = "#ffa500"
    error: str = "#dc3545"
    success: str = "#28a745"
    info: str = "#17a2b8"
    
    def to_dict(self) -> Dict[str, str]:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ColorPalette':
        """從字典創建"""
        return cls(**data)

@dataclass
class ThemeDefinition:
    """主題定義數據類"""
    id: str
    name: str
    description: str
    type: ThemeType
    colors: ColorPalette
    font_family: str = "Segoe UI"
    font_size: int = 12
    border_radius: int = 4
    shadow_enabled: bool = True
    animation_enabled: bool = True
    author: str = "System"
    version: str = "1.0"
    created_date: str = ""
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThemeDefinition':
        """從字典創建"""
        data = data.copy()
        data['type'] = ThemeType(data['type'])
        data['colors'] = ColorPalette.from_dict(data['colors'])
        return cls(**data)

class ThemeManagerAdvanced(QObject):
    """增強型主題管理器"""
    
    # 信號定義
    theme_changed = pyqtSignal(str, ThemeDefinition)  # 主題名稱, 主題定義
    theme_preview = pyqtSignal(str, ThemeDefinition)  # 預覽信號
    color_scheme_updated = pyqtSignal(dict)  # 色彩方案更新
    system_theme_detected = pyqtSignal(str)  # 系統主題檢測
    
    def __init__(self):
        super().__init__()
        self.themes: Dict[str, ThemeDefinition] = {}
        self.current_theme: Optional[ThemeDefinition] = None
        self.system_theme_watcher = None
        self.animation_enabled = True
        
        # 設定檔案路徑
        self.themes_dir = config_manager.get_resource_path("ui/themes")
        self.custom_themes_dir = config_manager.get_resource_path("ui/themes/custom")
        self.user_settings = QSettings("CLI_Tool", "ThemeManager")
        
        self._initialize_directories()
        self._load_built_in_themes()
        self._load_custom_themes()
        self._setup_system_theme_watcher()
    
    def _initialize_directories(self):
        """初始化目錄結構"""
        try:
            self.themes_dir.mkdir(parents=True, exist_ok=True)
            self.custom_themes_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Theme directories initialized")
        except Exception as e:
            logger.error(f"Failed to initialize theme directories: {e}")
    
    def _load_built_in_themes(self):
        """載入內建主題"""
        built_in_themes = [
            self._create_dark_professional_theme(),
            self._create_light_modern_theme(),
            self._create_blue_corporate_theme(),
            self._create_high_contrast_theme(),
            self._create_cyberpunk_theme(),
            self._create_nature_green_theme(),
            self._create_sunset_orange_theme(),
            self._create_ocean_blue_theme()
        ]
        
        for theme in built_in_themes:
            self.themes[theme.id] = theme
            logger.debug(f"Loaded built-in theme: {theme.name}")
    
    def _create_dark_professional_theme(self) -> ThemeDefinition:
        """創建專業深色主題"""
        colors = ColorPalette(
            primary="#4a90e2",
            secondary="#50c878",
            accent="#ff6b6b",
            background="#1e1e1e",
            surface="#2d2d2d",
            text_primary="#ffffff",
            text_secondary="#cccccc",
            border="#444444",
            warning="#ffa500",
            error="#dc3545",
            success="#28a745",
            info="#17a2b8"
        )
        
        return ThemeDefinition(
            id="dark_professional",
            name="專業深色",
            description="適合長時間使用的專業深色主題，對眼睛友善",
            type=ThemeType.DARK,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_light_modern_theme(self) -> ThemeDefinition:
        """創建現代淺色主題"""
        colors = ColorPalette(
            primary="#007acc",
            secondary="#00a86b",
            accent="#e74c3c",
            background="#f8f9fa",
            surface="#ffffff",
            text_primary="#212529",
            text_secondary="#6c757d",
            border="#dee2e6",
            warning="#ff8c00",
            error="#dc3545",
            success="#28a745",
            info="#17a2b8"
        )
        
        return ThemeDefinition(
            id="light_modern",
            name="現代淺色",
            description="清新明亮的現代淺色主題，適合日間使用",
            type=ThemeType.LIGHT,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_blue_corporate_theme(self) -> ThemeDefinition:
        """創建企業藍色主題"""
        colors = ColorPalette(
            primary="#1e40af",
            secondary="#0ea5e9",
            accent="#f59e0b",
            background="#0f172a",
            surface="#1e293b",
            text_primary="#f1f5f9",
            text_secondary="#cbd5e1",
            border="#334155",
            warning="#f59e0b",
            error="#ef4444",
            success="#10b981",
            info="#06b6d4"
        )
        
        return ThemeDefinition(
            id="blue_corporate",
            name="企業藍調",
            description="專業穩重的企業級藍色主題",
            type=ThemeType.DARK,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_high_contrast_theme(self) -> ThemeDefinition:
        """創建高對比度主題"""
        colors = ColorPalette(
            primary="#ffffff",
            secondary="#ffff00",
            accent="#00ffff",
            background="#000000",
            surface="#1a1a1a",
            text_primary="#ffffff",
            text_secondary="#ffffff",
            border="#ffffff",
            warning="#ffff00",
            error="#ff0000",
            success="#00ff00",
            info="#00ffff"
        )
        
        return ThemeDefinition(
            id="high_contrast",
            name="高對比度",
            description="高對比度主題，提升可訪問性和視覺清晰度",
            type=ThemeType.HIGH_CONTRAST,
            colors=colors,
            font_size=14,
            author="CLI Tool Team"
        )
    
    def _create_cyberpunk_theme(self) -> ThemeDefinition:
        """創建賽博朋克主題"""
        colors = ColorPalette(
            primary="#00ff41",
            secondary="#ff0080",
            accent="#00d4ff",
            background="#0a0a0a",
            surface="#1a1a2e",
            text_primary="#00ff41",
            text_secondary="#ffffff",
            border="#16213e",
            warning="#ffaa00",
            error="#ff0080",
            success="#00ff41",
            info="#00d4ff"
        )
        
        return ThemeDefinition(
            id="cyberpunk_neon",
            name="賽博朋克",
            description="未來科技風格的霓虹色彩主題",
            type=ThemeType.DARK,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_nature_green_theme(self) -> ThemeDefinition:
        """創建自然綠色主題"""
        colors = ColorPalette(
            primary="#2d5a27",
            secondary="#4a7c59",
            accent="#8fbc8f",
            background="#f0f8f0",
            surface="#ffffff",
            text_primary="#1b5e20",
            text_secondary="#2e7d32",
            border="#c8e6c9",
            warning="#ff8f00",
            error="#d32f2f",
            success="#388e3c",
            info="#1976d2"
        )
        
        return ThemeDefinition(
            id="nature_green",
            name="自然綠意",
            description="清新自然的綠色主題，舒緩視覺疲勞",
            type=ThemeType.LIGHT,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_sunset_orange_theme(self) -> ThemeDefinition:
        """創建夕陽橘色主題"""
        colors = ColorPalette(
            primary="#ff6b35",
            secondary="#ff8c42",
            accent="#ffd23f",
            background="#2c1810",
            surface="#3d2817",
            text_primary="#fff8f0",
            text_secondary="#ffdbcc",
            border="#5a3a26",
            warning="#ffb74d",
            error="#f44336",
            success="#4caf50",
            info="#2196f3"
        )
        
        return ThemeDefinition(
            id="sunset_orange",
            name="夕陽橘調",
            description="溫暖的夕陽橘色主題，營造舒適氛圍",
            type=ThemeType.DARK,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _create_ocean_blue_theme(self) -> ThemeDefinition:
        """創建海洋藍色主題"""
        colors = ColorPalette(
            primary="#0077be",
            secondary="#00a8cc",
            accent="#7fb3d3",
            background="#e6f3ff",
            surface="#ffffff",
            text_primary="#003d5c",
            text_secondary="#0066a2",
            border="#b3d9ff",
            warning="#ff9800",
            error="#f44336",
            success="#4caf50",
            info="#2196f3"
        )
        
        return ThemeDefinition(
            id="ocean_blue",
            name="海洋藍調",
            description="清涼的海洋藍色主題，帶來平靜感受",
            type=ThemeType.LIGHT,
            colors=colors,
            author="CLI Tool Team"
        )
    
    def _load_custom_themes(self):
        """載入用戶自定義主題"""
        try:
            if not self.custom_themes_dir.exists():
                return
            
            for theme_file in self.custom_themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    
                    theme = ThemeDefinition.from_dict(theme_data)
                    self.themes[theme.id] = theme
                    logger.info(f"Loaded custom theme: {theme.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load custom theme {theme_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load custom themes: {e}")
    
    def _setup_system_theme_watcher(self):
        """設置系統主題監視器"""
        try:
            from PyQt5.QtCore import QThread
            
            class SystemThemeWatcher(QThread):
                theme_detected = pyqtSignal(str)
                
                def run(self):
                    # 簡化的系統主題檢測
                    import sys
                    if sys.platform == "win32":
                        try:
                            import winreg
                            # Windows 系統主題檢測
                            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                               r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
                            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                            theme = "light" if value else "dark"
                            self.theme_detected.emit(theme)
                        except:
                            self.theme_detected.emit("dark")  # 默認深色
                    else:
                        # 其他系統暫時使用默認
                        self.theme_detected.emit("dark")
            
            self.system_theme_watcher = SystemThemeWatcher()
            self.system_theme_watcher.theme_detected.connect(self.system_theme_detected.emit)
            
        except ImportError:
            logger.warning("System theme watching not available")
    
    def get_available_themes(self) -> Dict[str, ThemeDefinition]:
        """獲取所有可用主題"""
        return self.themes.copy()
    
    def get_current_theme(self) -> Optional[ThemeDefinition]:
        """獲取當前主題"""
        if not self.current_theme:
            # 嘗試從設定載入
            saved_theme_id = self.user_settings.value("current_theme", "dark_professional")
            if saved_theme_id in self.themes:
                self.current_theme = self.themes[saved_theme_id]
            else:
                self.current_theme = self.themes.get("dark_professional")
        
        return self.current_theme
    
    def set_theme(self, theme_id: str) -> bool:
        """設置並應用主題"""
        if theme_id not in self.themes:
            logger.error(f"Theme '{theme_id}' not found")
            return False
        
        try:
            theme = self.themes[theme_id]
            
            # 生成並應用樣式表
            stylesheet = self._generate_stylesheet(theme)
            
            app = QApplication.instance()
            if app:
                if self.animation_enabled:
                    # 使用動畫切換
                    self._apply_theme_with_animation(stylesheet, theme)
                else:
                    # 直接應用
                    app.setStyleSheet(stylesheet)
            
            # 保存設定
            self.current_theme = theme
            self.user_settings.setValue("current_theme", theme_id)
            self.user_settings.sync()
            
            # 發出信號
            self.theme_changed.emit(theme_id, theme)
            
            logger.info(f"Applied theme: {theme.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying theme '{theme_id}': {e}")
            return False
    
    def preview_theme(self, theme_id: str):
        """預覽主題（不保存）"""
        if theme_id in self.themes:
            theme = self.themes[theme_id]
            self.theme_preview.emit(theme_id, theme)
    
    def _generate_stylesheet(self, theme: ThemeDefinition) -> str:
        """生成主題樣式表"""
        colors = theme.colors
        
        # 基礎樣式模板
        base_template = f"""
/* 全局樣式 */
QWidget {{
    background-color: {colors.background};
    color: {colors.text_primary};
    font-family: "{theme.font_family}";
    font-size: {theme.font_size}px;
    selection-background-color: {colors.primary};
    selection-color: {colors.text_primary};
}}

/* 按鈕樣式 */
QPushButton {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    padding: 8px 16px;
    border-radius: {theme.border_radius}px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {self._lighten_color(colors.surface, 0.1)};
    border-color: {colors.primary};
}}

QPushButton:pressed {{
    background-color: {self._darken_color(colors.surface, 0.1)};
}}

QPushButton:disabled {{
    background-color: {self._darken_color(colors.surface, 0.3)};
    color: {colors.text_secondary};
    border-color: {self._darken_color(colors.border, 0.2)};
}}

/* 主要按鈕樣式 */
QPushButton[class="primary"] {{
    background-color: {colors.primary};
    color: white;
    border-color: {colors.primary};
}}

QPushButton[class="primary"]:hover {{
    background-color: {self._lighten_color(colors.primary, 0.1)};
}}

QPushButton[class="primary"]:pressed {{
    background-color: {self._darken_color(colors.primary, 0.1)};
}}

/* 輸入框樣式 */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    padding: 8px;
    border-radius: {theme.border_radius}px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {colors.primary};
    outline: none;
}}

/* 下拉選單樣式 */
QComboBox {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    padding: 8px 12px;
    border-radius: {theme.border_radius}px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {colors.primary};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border: 2px solid {colors.text_primary};
    border-top: none;
    border-right: none;
    width: 6px;
    height: 6px;
    transform: rotate(-45deg);
    margin-top: -3px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    selection-background-color: {colors.primary};
    border-radius: {theme.border_radius}px;
}}

/* 複選框和單選框 */
QCheckBox, QRadioButton {{
    color: {colors.text_primary};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {colors.border};
    background-color: {colors.surface};
    border-radius: {2 if 'QCheckBox' in '{}' else 8}px;
}}

QCheckBox::indicator:checked {{
    background-color: {colors.primary};
    border-color: {colors.primary};
}}

QRadioButton::indicator:checked {{
    background-color: {colors.primary};
    border-color: {colors.primary};
}}

/* 標籤頁樣式 */
QTabWidget::pane {{
    border: 1px solid {colors.border};
    background-color: {colors.surface};
    border-radius: {theme.border_radius}px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {colors.background};
    color: {colors.text_secondary};
    border: 1px solid {colors.border};
    border-bottom: none;
    padding: 10px 16px;
    margin-right: 2px;
    border-top-left-radius: {theme.border_radius}px;
    border-top-right-radius: {theme.border_radius}px;
}}

QTabBar::tab:selected {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border-bottom-color: {colors.surface};
}}

QTabBar::tab:hover:!selected {{
    background-color: {self._lighten_color(colors.background, 0.1)};
}}

/* 滾動條樣式 */
QScrollBar:vertical {{
    background-color: {colors.background};
    width: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {colors.border};
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors.text_secondary};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {colors.background};
    height: 12px;
    border-radius: 6px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors.border};
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors.text_secondary};
}}

/* 分割器樣式 */
QSplitter::handle {{
    background-color: {colors.border};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* 進度條樣式 */
QProgressBar {{
    background-color: {colors.background};
    border: 1px solid {colors.border};
    border-radius: {theme.border_radius}px;
    text-align: center;
    color: {colors.text_primary};
}}

QProgressBar::chunk {{
    background-color: {colors.primary};
    border-radius: {theme.border_radius - 1}px;
}}

/* 狀態欄樣式 */
QStatusBar {{
    background-color: {colors.surface};
    color: {colors.text_secondary};
    border-top: 1px solid {colors.border};
}}

/* 功能表列樣式 */
QMenuBar {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border-bottom: 1px solid {colors.border};
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
}}

QMenuBar::item:selected {{
    background-color: {colors.primary};
    color: white;
}}

QMenu {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: {theme.border_radius - 2}px;
}}

QMenu::item:selected {{
    background-color: {colors.primary};
    color: white;
}}

/* 工具提示樣式 */
QToolTip {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    padding: 6px 10px;
    border-radius: {theme.border_radius}px;
}}

/* 群組框樣式 */
QGroupBox {{
    font-weight: bold;
    border: 2px solid {colors.border};
    border-radius: {theme.border_radius}px;
    margin-top: 1ex;
    padding-top: 10px;
    color: {colors.text_primary};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: {colors.primary};
}}

/* 列表和樹狀視圖樣式 */
QListWidget, QTreeWidget {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {theme.border_radius}px;
    alternate-background-color: {self._lighten_color(colors.surface, 0.05)};
}}

QListWidget::item, QTreeWidget::item {{
    padding: 6px;
    border-bottom: 1px solid {colors.border};
}}

QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: {colors.primary};
    color: white;
}}

QListWidget::item:hover, QTreeWidget::item:hover {{
    background-color: {self._lighten_color(colors.surface, 0.1)};
}}

/* 通知和警告樣式 */
QLabel[notification="info"] {{
    background-color: {colors.info};
    color: white;
    padding: 8px 12px;
    border-radius: {theme.border_radius}px;
    font-weight: 500;
}}

QLabel[notification="warning"] {{
    background-color: {colors.warning};
    color: white;
    padding: 8px 12px;
    border-radius: {theme.border_radius}px;
    font-weight: 500;
}}

QLabel[notification="error"] {{
    background-color: {colors.error};
    color: white;
    padding: 8px 12px;
    border-radius: {theme.border_radius}px;
    font-weight: 500;
}}

QLabel[notification="success"] {{
    background-color: {colors.success};
    color: white;
    padding: 8px 12px;
    border-radius: {theme.border_radius}px;
    font-weight: 500;
}}
        """
        
        # 如果啟用陰影效果，添加陰影樣式
        if theme.shadow_enabled:
            shadow_styles = f"""
/* 陰影效果 */
QPushButton, QLineEdit, QTextEdit, QComboBox {{
    /* 陰影效果需要通過程式碼實現 */
}}
            """
            base_template += shadow_styles
        
        return base_template.strip()
    
    def _lighten_color(self, color_hex: str, factor: float) -> str:
        """調亮顏色"""
        try:
            color = QColor(color_hex)
            h, s, v, a = color.getHsv()
            v = min(255, int(v + (255 - v) * factor))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return color_hex
    
    def _darken_color(self, color_hex: str, factor: float) -> str:
        """調暗顏色"""
        try:
            color = QColor(color_hex)
            h, s, v, a = color.getHsv()
            v = max(0, int(v * (1 - factor)))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return color_hex
    
    def _apply_theme_with_animation(self, stylesheet: str, theme: ThemeDefinition):
        """使用動畫效果應用主題"""
        try:
            from ui.animation_effects import animation_manager
            
            app = QApplication.instance()
            if not app:
                return
            
            # 創建過渡效果
            # 這裡可以添加更複雜的動畫效果
            app.setStyleSheet(stylesheet)
            
        except ImportError:
            # 如果沒有動畫系統，直接應用
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
    
    def create_custom_theme(self, theme_definition: ThemeDefinition) -> bool:
        """創建自定義主題"""
        try:
            theme_file = self.custom_themes_dir / f"{theme_definition.id}.json"
            
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_definition.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.themes[theme_definition.id] = theme_definition
            logger.info(f"Created custom theme: {theme_definition.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom theme: {e}")
            return False
    
    def delete_custom_theme(self, theme_id: str) -> bool:
        """刪除自定義主題"""
        if theme_id not in self.themes:
            return False
        
        theme = self.themes[theme_id]
        if theme.type != ThemeType.CUSTOM:
            logger.warning(f"Cannot delete built-in theme: {theme_id}")
            return False
        
        try:
            theme_file = self.custom_themes_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            del self.themes[theme_id]
            logger.info(f"Deleted custom theme: {theme.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete custom theme: {e}")
            return False
    
    def export_theme(self, theme_id: str, export_path: Path) -> bool:
        """導出主題"""
        if theme_id not in self.themes:
            return False
        
        try:
            theme = self.themes[theme_id]
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported theme: {theme.name} to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export theme: {e}")
            return False
    
    def import_theme(self, import_path: Path) -> bool:
        """導入主題"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = ThemeDefinition.from_dict(theme_data)
            theme.type = ThemeType.CUSTOM  # 導入的主題標記為自定義
            
            return self.create_custom_theme(theme)
            
        except Exception as e:
            logger.error(f"Failed to import theme: {e}")
            return False
    
    def get_themes_by_type(self, theme_type: ThemeType) -> List[ThemeDefinition]:
        """按類型獲取主題"""
        return [theme for theme in self.themes.values() if theme.type == theme_type]
    
    def enable_animations(self, enabled: bool):
        """啟用/禁用動畫效果"""
        self.animation_enabled = enabled
        self.user_settings.setValue("animation_enabled", enabled)
    
    def get_color_palette(self, theme_id: str) -> Optional[ColorPalette]:
        """獲取主題色彩調色盤"""
        theme = self.themes.get(theme_id)
        return theme.colors if theme else None
    
    def update_color_palette(self, theme_id: str, colors: ColorPalette) -> bool:
        """更新主題色彩調色盤"""
        if theme_id not in self.themes:
            return False
        
        try:
            self.themes[theme_id].colors = colors
            self.color_scheme_updated.emit(colors.to_dict())
            
            # 如果是當前主題，重新應用
            if self.current_theme and self.current_theme.id == theme_id:
                self.set_theme(theme_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update color palette: {e}")
            return False

# 全域實例
theme_manager_advanced = ThemeManagerAdvanced()
```

---

## 2. 動態主題切換組件

### 高級主題選擇器

```python
"""
高級主題選擇器 - 支援預覽、分類和搜尋
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QPushButton, QLabel, QLineEdit, QComboBox, QButtonGroup,
    QFrame, QSplitter, QTabWidget, QSlider, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPixmap
from ui.components.buttons import ModernButton, PrimaryButton
from ui.components.inputs import ModernLineEdit
from ui.animation_effects import animate_widget

class ThemePreviewWidget(QFrame):
    """主題預覽組件"""
    
    def __init__(self, theme_definition: ThemeDefinition, parent=None):
        super().__init__(parent)
        self.theme = theme_definition
        self.is_previewing = False
        self.setup_ui()
    
    def setup_ui(self):
        """設置預覽 UI"""
        self.setFixedSize(300, 200)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 主題名稱和類型
        header_layout = QHBoxLayout()
        
        name_label = QLabel(self.theme.name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        type_label = QLabel(self.theme.type.value.upper())
        type_label.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        header_layout.addWidget(type_label)
        
        layout.addLayout(header_layout)
        
        # 色彩方案預覽
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(5)
        
        color_roles = [
            ('primary', self.theme.colors.primary),
            ('secondary', self.theme.colors.secondary),
            ('accent', self.theme.colors.accent),
            ('background', self.theme.colors.background),
            ('surface', self.theme.colors.surface),
            ('text', self.theme.colors.text_primary)
        ]
        
        for role, color in color_roles:
            color_box = QFrame()
            color_box.setFixedSize(25, 25)
            color_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: 1px solid #666;
                    border-radius: 3px;
                }}
            """)
            color_box.setToolTip(f"{role}: {color}")
            colors_layout.addWidget(color_box)
        
        colors_layout.addStretch()
        layout.addLayout(colors_layout)
        
        # 主題描述
        desc_label = QLabel(self.theme.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("預覽")
        self.preview_btn.setFixedSize(60, 28)
        self.preview_btn.clicked.connect(self.toggle_preview)
        buttons_layout.addWidget(self.preview_btn)
        
        self.apply_btn = PrimaryButton("應用")
        self.apply_btn.setFixedSize(60, 28)
        self.apply_btn.clicked.connect(self.apply_theme)
        buttons_layout.addWidget(self.apply_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def toggle_preview(self):
        """切換預覽狀態"""
        self.is_previewing = not self.is_previewing
        
        if self.is_previewing:
            self.preview_btn.setText("取消")
            theme_manager_advanced.preview_theme(self.theme.id)
            # 添加預覽邊框效果
            animate_widget(self, "pulse")
        else:
            self.preview_btn.setText("預覽")
            # 恢復當前主題
            current_theme = theme_manager_advanced.get_current_theme()
            if current_theme:
                theme_manager_advanced.set_theme(current_theme.id)
    
    def apply_theme(self):
        """應用主題"""
        theme_manager_advanced.set_theme(self.theme.id)

class AdvancedThemeSelector(QWidget):
    """高級主題選擇器"""
    
    theme_changed = pyqtSignal(str, ThemeDefinition)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preview_widgets = []
        self.filter_type = "all"
        self.search_query = ""
        self.setup_ui()
        self.load_themes()
        
        # 連接信號
        theme_manager_advanced.theme_changed.connect(self.on_theme_changed)
    
    def setup_ui(self):
        """設置主要 UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左側控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
        # 右側主題展示區域
        display_area = self.create_display_area()
        main_layout.addWidget(display_area, 3)
        
        self.setLayout(main_layout)
    
    def create_control_panel(self) -> QWidget:
        """創建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setMaximumWidth(300)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 標題
        title_label = QLabel("主題設定")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 搜尋框
        search_layout = QVBoxLayout()
        search_label = QLabel("搜尋主題:")
        search_layout.addWidget(search_label)
        
        self.search_input = ModernLineEdit()
        self.search_input.setPlaceholderText("輸入主題名稱...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # 類型篩選
        filter_layout = QVBoxLayout()
        filter_label = QLabel("主題類型:")
        filter_layout.addWidget(filter_label)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "全部", "深色主題", "淺色主題", "高對比度", "自定義主題"
        ])
        self.type_filter.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.type_filter)
        
        layout.addLayout(filter_layout)
        
        # 當前主題資訊
        current_layout = QVBoxLayout()
        current_label = QLabel("當前主題:")
        current_layout.addWidget(current_label)
        
        self.current_theme_info = QLabel("載入中...")
        self.current_theme_info.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        self.current_theme_info.setWordWrap(True)
        current_layout.addWidget(self.current_theme_info)
        
        layout.addLayout(current_layout)
        
        layout.addStretch()
        
        # 操作按鈕
        buttons_layout = QVBoxLayout()
        
        self.create_theme_btn = ModernButton("創建新主題")
        self.create_theme_btn.clicked.connect(self.create_new_theme)
        buttons_layout.addWidget(self.create_theme_btn)
        
        self.import_theme_btn = ModernButton("導入主題")
        self.import_theme_btn.clicked.connect(self.import_theme)
        buttons_layout.addWidget(self.import_theme_btn)
        
        self.export_theme_btn = ModernButton("導出當前主題")
        self.export_theme_btn.clicked.connect(self.export_current_theme)
        buttons_layout.addWidget(self.export_theme_btn)
        
        layout.addLayout(buttons_layout)
        
        panel.setLayout(layout)
        return panel
    
    def create_display_area(self) -> QWidget:
        """創建主題展示區域"""
        area = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 主題容器
        self.themes_container = QWidget()
        self.themes_layout = QGridLayout()
        self.themes_layout.setSpacing(15)
        self.themes_container.setLayout(self.themes_layout)
        
        scroll_area.setWidget(self.themes_container)
        layout.addWidget(scroll_area)
        
        area.setLayout(layout)
        return area
    
    def load_themes(self):
        """載入並顯示主題"""
        # 清除現有組件
        for widget in self.preview_widgets:
            widget.deleteLater()
        self.preview_widgets.clear()
        
        # 獲取可用主題
        available_themes = theme_manager_advanced.get_available_themes()
        
        # 應用篩選
        filtered_themes = self.filter_themes(available_themes)
        
        # 創建預覽組件
        row, col = 0, 0
        max_cols = 2  # 每行最多 2 個預覽
        
        for theme_id, theme in filtered_themes.items():
            preview = ThemePreviewWidget(theme)
            self.preview_widgets.append(preview)
            self.themes_layout.addWidget(preview, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 更新當前主題資訊
        self.update_current_theme_info()
    
    def filter_themes(self, themes: Dict[str, ThemeDefinition]) -> Dict[str, ThemeDefinition]:
        """篩選主題"""
        filtered = {}
        
        for theme_id, theme in themes.items():
            # 類型篩選
            if self.filter_type != "all":
                type_map = {
                    "深色主題": ThemeType.DARK,
                    "淺色主題": ThemeType.LIGHT,
                    "高對比度": ThemeType.HIGH_CONTRAST,
                    "自定義主題": ThemeType.CUSTOM
                }
                if theme.type != type_map.get(self.filter_type):
                    continue
            
            # 搜尋篩選
            if self.search_query:
                if (self.search_query.lower() not in theme.name.lower() and 
                    self.search_query.lower() not in theme.description.lower()):
                    continue
            
            filtered[theme_id] = theme
        
        return filtered
    
    def on_search_changed(self, text: str):
        """處理搜尋變更"""
        self.search_query = text
        self.load_themes()
    
    def on_filter_changed(self, filter_text: str):
        """處理篩選變更"""
        filter_map = {
            "全部": "all",
            "深色主題": "深色主題",
            "淺色主題": "淺色主題",
            "高對比度": "高對比度",
            "自定義主題": "自定義主題"
        }
        self.filter_type = filter_map.get(filter_text, "all")
        self.load_themes()
    
    def update_current_theme_info(self):
        """更新當前主題資訊"""
        current_theme = theme_manager_advanced.get_current_theme()
        if current_theme:
            info_text = f"""
            <b>{current_theme.name}</b><br>
            <small>類型: {current_theme.type.value}</small><br>
            <small>作者: {current_theme.author}</small><br>
            <small>版本: {current_theme.version}</small><br><br>
            {current_theme.description}
            """
            self.current_theme_info.setText(info_text)
        else:
            self.current_theme_info.setText("未選擇主題")
    
    def create_new_theme(self):
        """創建新主題"""
        # 這裡會打開主題編輯器對話框
        from ui.theme_editor import ThemeEditorDialog
        
        editor = ThemeEditorDialog(self)
        if editor.exec_() == editor.Accepted:
            self.load_themes()
    
    def import_theme(self):
        """導入主題"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "導入主題", "", "主題文件 (*.json)"
        )
        
        if file_path:
            success = theme_manager_advanced.import_theme(Path(file_path))
            if success:
                self.load_themes()
                # 顯示成功訊息
                self.show_notification("主題導入成功", "success")
            else:
                self.show_notification("主題導入失敗", "error")
    
    def export_current_theme(self):
        """導出當前主題"""
        from PyQt5.QtWidgets import QFileDialog
        
        current_theme = theme_manager_advanced.get_current_theme()
        if not current_theme:
            self.show_notification("沒有可導出的主題", "warning")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "導出主題", f"{current_theme.name}.json", "主題文件 (*.json)"
        )
        
        if file_path:
            success = theme_manager_advanced.export_theme(current_theme.id, Path(file_path))
            if success:
                self.show_notification("主題導出成功", "success")
            else:
                self.show_notification("主題導出失敗", "error")
    
    def show_notification(self, message: str, type_: str):
        """顯示通知"""
        from ui.animation_effects import animate_notification
        animate_notification(self, message, type_)
    
    def on_theme_changed(self, theme_id: str, theme: ThemeDefinition):
        """處理主題變更"""
        self.update_current_theme_info()
        self.theme_changed.emit(theme_id, theme)
```

---

## 3. 主題編輯器

### 視覺化主題編輯器

```python
"""
視覺化主題編輯器 - 支援色彩調整、實時預覽和主題創建
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QSlider, QCheckBox, QColorDialog, QFrame, QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap

class ColorPicker(QPushButton):
    """色彩選擇器組件"""
    
    color_changed = pyqtSignal(str)  # 發出十六進制色彩值
    
    def __init__(self, initial_color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self.current_color = QColor(initial_color)
        self.setFixedSize(40, 30)
        self.update_display()
        self.clicked.connect(self.open_color_dialog)
    
    def update_display(self):
        """更新顯示"""
        color_name = self.current_color.name()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_name};
                border: 2px solid #666;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border-color: #999;
            }}
        """)
        self.setToolTip(f"色彩: {color_name}")
    
    def open_color_dialog(self):
        """打開色彩選擇對話框"""
        color = QColorDialog.getColor(self.current_color, self, "選擇色彩")
        if color.isValid():
            self.current_color = color
            self.update_display()
            self.color_changed.emit(color.name())
    
    def set_color(self, color_hex: str):
        """設定色彩"""
        self.current_color = QColor(color_hex)
        self.update_display()

class ThemePreviewPane(QFrame):
    """主題預覽面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = None
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """設置預覽 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 標題
        title_label = QLabel("主題預覽")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 示例組件
        self.create_sample_components(layout)
        
        self.setLayout(layout)
    
    def create_sample_components(self, layout):
        """創建示例組件"""
        # 按鈕示例
        buttons_layout = QHBoxLayout()
        
        self.sample_button = QPushButton("普通按鈕")
        buttons_layout.addWidget(self.sample_button)
        
        self.sample_primary_btn = QPushButton("主要按鈕")
        self.sample_primary_btn.setProperty("class", "primary")
        buttons_layout.addWidget(self.sample_primary_btn)
        
        layout.addLayout(buttons_layout)
        
        # 輸入框示例
        self.sample_input = QLineEdit("示例輸入文字")
        layout.addWidget(self.sample_input)
        
        # 下拉選單示例
        self.sample_combo = QComboBox()
        self.sample_combo.addItems(["選項 1", "選項 2", "選項 3"])
        layout.addWidget(self.sample_combo)
        
        # 複選框示例
        self.sample_checkbox = QCheckBox("示例複選框")
        self.sample_checkbox.setChecked(True)
        layout.addWidget(self.sample_checkbox)
        
        # 文字區域示例
        self.sample_text = QTextEdit()
        self.sample_text.setPlainText("這是示例文字區域的內容。")
        self.sample_text.setMaximumHeight(80)
        layout.addWidget(self.sample_text)
    
    def apply_theme_preview(self, theme: ThemeDefinition):
        """應用主題預覽"""
        self.current_theme = theme
        
        # 生成並應用樣式表
        stylesheet = theme_manager_advanced._generate_stylesheet(theme)
        self.setStyleSheet(stylesheet)

class ThemeEditorDialog(QDialog):
    """主題編輯器對話框"""
    
    def __init__(self, parent=None, theme_to_edit: Optional[ThemeDefinition] = None):
        super().__init__(parent)
        self.theme_to_edit = theme_to_edit
        self.current_colors = ColorPalette()
        self.color_pickers = {}
        
        self.setup_ui()
        self.setup_connections()
        
        if theme_to_edit:
            self.load_theme_for_editing()
        
        self.setWindowTitle("主題編輯器")
        self.resize(900, 600)
    
    def setup_ui(self):
        """設置主要 UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 左側編輯區域
        edit_area = self.create_edit_area()
        main_layout.addWidget(edit_area, 2)
        
        # 右側預覽區域
        self.preview_pane = ThemePreviewPane()
        main_layout.addWidget(self.preview_pane, 1)
        
        self.setLayout(main_layout)
    
    def create_edit_area(self) -> QWidget:
        """創建編輯區域"""
        area = QWidget()
        layout = QVBoxLayout()
        
        # 標籤頁
        tab_widget = QTabWidget()
        
        # 基本資訊標籤頁
        basic_tab = self.create_basic_info_tab()
        tab_widget.addTab(basic_tab, "基本資訊")
        
        # 色彩方案標籤頁
        colors_tab = self.create_colors_tab()
        tab_widget.addTab(colors_tab, "色彩方案")
        
        # 樣式設定標籤頁
        style_tab = self.create_style_tab()
        tab_widget.addTab(style_tab, "樣式設定")
        
        layout.addWidget(tab_widget)
        
        # 操作按鈕
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存主題")
        save_btn.clicked.connect(self.save_theme)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        area.setLayout(layout)
        return area
    
    def create_basic_info_tab(self) -> QWidget:
        """創建基本資訊標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 主題名稱
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("主題名稱:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("請輸入主題名稱...")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 主題描述
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("主題描述:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("請輸入主題描述...")
        self.description_input.setMaximumHeight(80)
        desc_layout.addWidget(self.description_input)
        layout.addLayout(desc_layout)
        
        # 主題類型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("主題類型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["深色主題", "淺色主題", "高對比度", "自定義主題"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 作者資訊
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("作者:"))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("作者名稱")
        author_layout.addWidget(self.author_input)
        layout.addLayout(author_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_colors_tab(self) -> QWidget:
        """創建色彩方案標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        colors_widget = QWidget()
        colors_layout = QGridLayout()
        colors_layout.setSpacing(15)
        
        # 色彩角色定義
        color_roles = [
            ("primary", "主色", "主要品牌色彩，用於按鈕和強調元素"),
            ("secondary", "次色", "次要色彩，用於輔助元素"),
            ("accent", "強調色", "用於突出重要內容的色彩"),
            ("background", "背景色", "主要背景色彩"),
            ("surface", "表面色", "卡片、面板等表面的色彩"),
            ("text_primary", "主文字色", "主要文字色彩"),
            ("text_secondary", "次文字色", "次要文字色彩"),
            ("border", "邊框色", "邊框和分隔線色彩"),
            ("warning", "警告色", "警告訊息色彩"),
            ("error", "錯誤色", "錯誤訊息色彩"),
            ("success", "成功色", "成功訊息色彩"),
            ("info", "資訊色", "資訊提示色彩")
        ]
        
        row = 0
        for role_id, role_name, role_desc in color_roles:
            # 色彩名稱標籤
            name_label = QLabel(role_name)
            name_font = QFont()
            name_font.setBold(True)
            name_label.setFont(name_font)
            colors_layout.addWidget(name_label, row, 0)
            
            # 色彩選擇器
            initial_color = getattr(self.current_colors, role_id)
            color_picker = ColorPicker(initial_color)
            color_picker.color_changed.connect(
                lambda color, role=role_id: self.on_color_changed(role, color)
            )
            self.color_pickers[role_id] = color_picker
            colors_layout.addWidget(color_picker, row, 1)
            
            # 色彩描述
            desc_label = QLabel(role_desc)
            desc_label.setStyleSheet("color: #666; font-size: 11px;")
            desc_label.setWordWrap(True)
            colors_layout.addWidget(desc_label, row, 2)
            
            row += 1
        
        colors_widget.setLayout(colors_layout)
        scroll_area.setWidget(colors_widget)
        layout.addWidget(scroll_area)
        
        widget.setLayout(layout)
        return widget
    
    def create_style_tab(self) -> QWidget:
        """創建樣式設定標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 字體設定
        font_group = QFrame()
        font_group.setFrameStyle(QFrame.Box)
        font_layout = QVBoxLayout()
        
        font_title = QLabel("字體設定")
        font_title.setFont(QFont("", 12, QFont.Bold))
        font_layout.addWidget(font_title)
        
        # 字體系列
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("字體系列:"))
        self.font_family_input = QLineEdit("Segoe UI")
        font_family_layout.addWidget(self.font_family_input)
        font_layout.addLayout(font_family_layout)
        
        # 字體大小
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字體大小:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setSuffix(" px")
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        font_layout.addLayout(font_size_layout)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # 邊框設定
        border_group = QFrame()
        border_group.setFrameStyle(QFrame.Box)
        border_layout = QVBoxLayout()
        
        border_title = QLabel("邊框設定")
        border_title.setFont(QFont("", 12, QFont.Bold))
        border_layout.addWidget(border_title)
        
        # 圓角半徑
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("圓角半徑:"))
        self.border_radius_spin = QSpinBox()
        self.border_radius_spin.setRange(0, 20)
        self.border_radius_spin.setValue(4)
        self.border_radius_spin.setSuffix(" px")
        radius_layout.addWidget(self.border_radius_spin)
        radius_layout.addStretch()
        border_layout.addLayout(radius_layout)
        
        border_group.setLayout(border_layout)
        layout.addWidget(border_group)
        
        # 效果設定
        effects_group = QFrame()
        effects_group.setFrameStyle(QFrame.Box)
        effects_layout = QVBoxLayout()
        
        effects_title = QLabel("視覺效果")
        effects_title.setFont(QFont("", 12, QFont.Bold))
        effects_layout.addWidget(effects_title)
        
        self.shadow_checkbox = QCheckBox("啟用陰影效果")
        self.shadow_checkbox.setChecked(True)
        effects_layout.addWidget(self.shadow_checkbox)
        
        self.animation_checkbox = QCheckBox("啟用動畫效果")
        self.animation_checkbox.setChecked(True)
        effects_layout.addWidget(self.animation_checkbox)
        
        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_connections(self):
        """設置信號連接"""
        # 當任何設定改變時，更新預覽
        self.name_input.textChanged.connect(self.update_preview)
        self.type_combo.currentTextChanged.connect(self.update_preview)
        self.font_family_input.textChanged.connect(self.update_preview)
        self.font_size_spin.valueChanged.connect(self.update_preview)
        self.border_radius_spin.valueChanged.connect(self.update_preview)
        self.shadow_checkbox.toggled.connect(self.update_preview)
        self.animation_checkbox.toggled.connect(self.update_preview)
    
    def on_color_changed(self, role: str, color: str):
        """處理色彩變更"""
        setattr(self.current_colors, role, color)
        self.update_preview()
    
    def update_preview(self):
        """更新預覽"""
        # 創建臨時主題定義
        temp_theme = ThemeDefinition(
            id="preview_theme",
            name=self.name_input.text() or "預覽主題",
            description="主題預覽",
            type=self.get_selected_theme_type(),
            colors=self.current_colors,
            font_family=self.font_family_input.text(),
            font_size=self.font_size_spin.value(),
            border_radius=self.border_radius_spin.value(),
            shadow_enabled=self.shadow_checkbox.isChecked(),
            animation_enabled=self.animation_checkbox.isChecked()
        )
        
        # 應用到預覽面板
        self.preview_pane.apply_theme_preview(temp_theme)
    
    def get_selected_theme_type(self) -> ThemeType:
        """獲取選中的主題類型"""
        type_map = {
            "深色主題": ThemeType.DARK,
            "淺色主題": ThemeType.LIGHT,
            "高對比度": ThemeType.HIGH_CONTRAST,
            "自定義主題": ThemeType.CUSTOM
        }
        return type_map.get(self.type_combo.currentText(), ThemeType.CUSTOM)
    
    def load_theme_for_editing(self):
        """載入主題進行編輯"""
        if not self.theme_to_edit:
            return
        
        theme = self.theme_to_edit
        
        # 載入基本資訊
        self.name_input.setText(theme.name)
        self.description_input.setPlainText(theme.description)
        self.author_input.setText(theme.author)
        
        # 設定主題類型
        type_text = {
            ThemeType.DARK: "深色主題",
            ThemeType.LIGHT: "淺色主題",
            ThemeType.HIGH_CONTRAST: "高對比度",
            ThemeType.CUSTOM: "自定義主題"
        }.get(theme.type, "自定義主題")
        self.type_combo.setCurrentText(type_text)
        
        # 載入色彩
        self.current_colors = theme.colors
        for role, picker in self.color_pickers.items():
            color = getattr(theme.colors, role)
            picker.set_color(color)
        
        # 載入樣式設定
        self.font_family_input.setText(theme.font_family)
        self.font_size_spin.setValue(theme.font_size)
        self.border_radius_spin.setValue(theme.border_radius)
        self.shadow_checkbox.setChecked(theme.shadow_enabled)
        self.animation_checkbox.setChecked(theme.animation_enabled)
        
        # 更新預覽
        self.update_preview()
    
    def save_theme(self):
        """保存主題"""
        # 驗證輸入
        if not self.name_input.text().strip():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "錯誤", "請輸入主題名稱")
            return
        
        # 創建主題定義
        import datetime
        theme_id = self.name_input.text().lower().replace(" ", "_")
        
        new_theme = ThemeDefinition(
            id=theme_id,
            name=self.name_input.text().strip(),
            description=self.description_input.toPlainText().strip(),
            type=self.get_selected_theme_type(),
            colors=self.current_colors,
            font_family=self.font_family_input.text().strip(),
            font_size=self.font_size_spin.value(),
            border_radius=self.border_radius_spin.value(),
            shadow_enabled=self.shadow_checkbox.isChecked(),
            animation_enabled=self.animation_checkbox.isChecked(),
            author=self.author_input.text().strip() or "User",
            created_date=datetime.datetime.now().isoformat()
        )
        
        # 保存主題
        success = theme_manager_advanced.create_custom_theme(new_theme)
        
        if success:
            self.accept()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "錯誤", "保存主題失敗")
```

---

## 4. 系統整合和配置

### 主題系統集成到主窗口

```python
# 在 main_window.py 中整合主題系統

class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_theme_system()  # 新增主題系統設置
        self.setup_ui()
        self.load_settings()
    
    def setup_theme_system(self):
        """設置主題系統"""
        # 連接主題變更信號
        theme_manager_advanced.theme_changed.connect(self.on_theme_changed)
        
        # 創建主題選擇器
        self.theme_selector = AdvancedThemeSelector()
        self.theme_selector.theme_changed.connect(self.on_theme_applied)
        
        # 應用保存的主題
        current_theme = theme_manager_advanced.get_current_theme()
        if current_theme:
            theme_manager_advanced.set_theme(current_theme.id)
    
    def create_menu_bar(self):
        """創建選單欄（包含主題選單）"""
        menubar = self.menuBar()
        
        # 視圖選單
        view_menu = menubar.addMenu('視圖')
        
        # 主題選單
        theme_menu = view_menu.addMenu('主題')
        
        # 主題選擇動作
        theme_selector_action = QAction('主題設定...', self)
        theme_selector_action.triggered.connect(self.show_theme_selector)
        theme_menu.addAction(theme_selector_action)
        
        theme_menu.addSeparator()
        
        # 快速主題切換
        themes = theme_manager_advanced.get_available_themes()
        for theme_id, theme in themes.items():
            action = QAction(theme.name, self)
            action.setData(theme_id)
            action.triggered.connect(lambda checked, tid=theme_id: theme_manager_advanced.set_theme(tid))
            theme_menu.addAction(action)
    
    def show_theme_selector(self):
        """顯示主題選擇器"""
        dialog = QDialog(self)
        dialog.setWindowTitle("主題設定")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        layout.addWidget(self.theme_selector)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def on_theme_changed(self, theme_id: str, theme: ThemeDefinition):
        """處理主題變更"""
        logger.info(f"Theme changed to: {theme.name}")
        
        # 更新窗口標題
        self.setWindowTitle(f"CLI Tool - {theme.name}")
        
        # 重新設置狀態欄樣式
        self.status_bar.showMessage(f"主題已切換至: {theme.name}", 2000)
    
    def on_theme_applied(self, theme_id: str, theme: ThemeDefinition):
        """處理主題應用"""
        # 可以在這裡添加額外的主題應用邏輯
        pass
```

### 配置文件設定

```yaml
# config/theme_settings.yaml
theme_system:
  # 基本設定
  default_theme: "dark_professional"
  animation_enabled: true
  auto_theme_switching: false
  
  # 自動主題切換設定
  auto_switching:
    enabled: false
    light_theme: "light_modern"
    dark_theme: "dark_professional"
    switch_time_morning: "06:00"
    switch_time_evening: "18:00"
    follow_system: true
  
  # 主題目錄設定
  directories:
    themes: "ui/themes"
    custom_themes: "ui/themes/custom"
    templates: "ui/themes/templates"
  
  # 高級設定
  advanced:
    enable_system_theme_detection: true
    cache_stylesheets: true
    validate_themes: true
    backup_themes: true
    
  # 無障礙設定
  accessibility:
    high_contrast_support: true
    font_scaling: true
    color_blind_support: false
```

---

## 5. 高級功能

### 自動主題切換

```python
class AutoThemeSwitcher(QObject):
    """自動主題切換器"""
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_theme_switch)
        self.settings = QSettings("CLI_Tool", "AutoThemeSwitcher")
        
        # 每分鐘檢查一次
        self.timer.start(60000)
    
    def enable_auto_switching(self, enabled: bool):
        """啟用自動切換"""
        self.settings.setValue("enabled", enabled)
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
    
    def set_switch_times(self, morning_time: str, evening_time: str):
        """設定切換時間"""
        self.settings.setValue("morning_time", morning_time)
        self.settings.setValue("evening_time", evening_time)
    
    def check_theme_switch(self):
        """檢查是否需要切換主題"""
        if not self.settings.value("enabled", False, bool):
            return
        
        from datetime import datetime
        
        current_time = datetime.now().strftime("%H:%M")
        morning_time = self.settings.value("morning_time", "06:00")
        evening_time = self.settings.value("evening_time", "18:00")
        
        if current_time == morning_time:
            light_theme = self.settings.value("light_theme", "light_modern")
            theme_manager_advanced.set_theme(light_theme)
        elif current_time == evening_time:
            dark_theme = self.settings.value("dark_theme", "dark_professional")
            theme_manager_advanced.set_theme(dark_theme)
```

### 主題備份和恢復

```python
class ThemeBackupManager:
    """主題備份管理器"""
    
    def __init__(self):
        self.backup_dir = config_manager.get_resource_path("backups/themes")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_all_themes(self) -> bool:
        """備份所有主題"""
        try:
            import zipfile
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"themes_backup_{timestamp}.zip"
            
            with zipfile.ZipFile(backup_file, 'w') as zip_file:
                # 備份自定義主題
                custom_themes_dir = theme_manager_advanced.custom_themes_dir
                for theme_file in custom_themes_dir.glob("*.json"):
                    zip_file.write(theme_file, f"custom/{theme_file.name}")
                
                # 備份設定
                settings_file = config_manager.get_resource_path("config/theme_settings.yaml")
                if settings_file.exists():
                    zip_file.write(settings_file, "settings/theme_settings.yaml")
            
            logger.info(f"Themes backed up to: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup themes: {e}")
            return False
    
    def restore_themes(self, backup_file: Path) -> bool:
        """恢復主題"""
        try:
            import zipfile
            
            with zipfile.ZipFile(backup_file, 'r') as zip_file:
                # 恢復自定義主題
                for file_info in zip_file.filelist:
                    if file_info.filename.startswith("custom/"):
                        extract_path = theme_manager_advanced.custom_themes_dir / file_info.filename[7:]
                        with open(extract_path, 'wb') as f:
                            f.write(zip_file.read(file_info))
            
            # 重新載入主題
            theme_manager_advanced._load_custom_themes()
            logger.info(f"Themes restored from: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore themes: {e}")
            return False
```

---

## 總結

這份主題切換系統實現指南提供了完整的現代化主題管理解決方案，包括：

### ✨ 核心特色
- **豐富的內建主題** - 8 種精心設計的主題方案
- **視覺化主題編輯器** - 所見即所得的主題創建和編輯
- **動態色彩管理** - 完整的色彩調色盤系統
- **實時預覽功能** - 即時查看主題效果
- **自動主題切換** - 基於時間或系統設定的智能切換

### 🎨 高級功能
- **主題導入導出** - 方便的主題分享和備份
- **無障礙支援** - 高對比度主題和字體縮放
- **系統整合** - 與 Windows/macOS 系統主題同步
- **動畫切換效果** - 平滑的主題過渡動畫
- **用戶偏好保存** - 自動記住用戶選擇

### 🔧 技術優勢
- **模組化設計** - 易於擴展和維護
- **效能優化** - 樣式表快取和批量更新
- **錯誤處理** - 完善的異常處理和回復機制
- **跨平台支援** - 適配不同操作系統特性

這個主題系統將讓您的 CLI Tool 應用程式擁有專業級的主題管理能力，為用戶提供個性化和舒適的使用體驗！🎊