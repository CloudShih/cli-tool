"""
主題管理器 - 負責主題的載入、應用和管理
與 config_manager 整合，支援動態主題切換
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """主題管理器 - 負責主題系統的核心功能"""
    
    # 主題變更信號
    theme_changed = pyqtSignal(str)  # 發出新主題名稱
    
    def __init__(self):
        super().__init__()
        self.available_themes: Dict[str, Dict] = {}
        self.current_theme: str = "dark_professional"
        self._load_available_themes()
    
    def _load_available_themes(self):
        """載入所有可用的主題"""
        try:
            themes_dir = config_manager.get_resource_path("ui/themes")
            
            # 定義預設主題
            self.available_themes = {
                "dark_professional": {
                    "name": "Dark Professional",
                    "description": "專業深色主題，適合長時間使用",
                    "file": "dark_professional.qss",
                    "preview_color": "#2e2e2e"
                },
                "light_modern": {
                    "name": "Light Modern", 
                    "description": "現代淺色主題，清晰明亮",
                    "file": "light_modern.qss",
                    "preview_color": "#f8f9fa"
                },
                "blue_corporate": {
                    "name": "Blue Corporate",
                    "description": "企業藍色主題，專業穩重",
                    "file": "blue_corporate.qss", 
                    "preview_color": "#1e3a8a"
                },
                "high_contrast": {
                    "name": "High Contrast",
                    "description": "高對比度主題，提升可訪問性",
                    "file": "high_contrast.qss",
                    "preview_color": "#000000"
                }
            }
            
            # 檢查主題文件是否存在
            for theme_id, theme_info in list(self.available_themes.items()):
                theme_file = themes_dir / theme_info["file"]
                if not theme_file.exists():
                    logger.warning(f"Theme file not found: {theme_file}")
                    # 如果主題文件不存在，我們仍保留主題信息，稍後會創建預設樣式
            
            logger.info(f"Loaded {len(self.available_themes)} themes")
            
        except Exception as e:
            logger.error(f"Error loading themes: {e}")
    
    def get_available_themes(self) -> Dict[str, Dict]:
        """獲取所有可用主題"""
        return self.available_themes.copy()
    
    def get_current_theme(self) -> str:
        """獲取當前主題名稱"""
        return config_manager.get('ui.theme.name', self.current_theme)
    
    def set_theme(self, theme_name: str) -> bool:
        """設置並應用主題"""
        if theme_name not in self.available_themes:
            logger.error(f"Theme '{theme_name}' not found")
            return False
        
        try:
            # 載入主題樣式
            stylesheet = self._load_theme_stylesheet(theme_name)
            
            # 應用主題
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
            
            # 保存配置
            config_manager.set('ui.theme.name', theme_name)
            config_manager.save_config()
            
            # 更新當前主題
            self.current_theme = theme_name
            
            # 發出主題變更信號
            self.theme_changed.emit(theme_name)
            
            logger.info(f"Applied theme: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying theme '{theme_name}': {e}")
            return False
    
    def _load_theme_stylesheet(self, theme_name: str) -> str:
        """載入主題樣式表"""
        try:
            theme_info = self.available_themes[theme_name]
            theme_file = config_manager.get_resource_path("ui/themes") / theme_info["file"]
            
            if theme_file.exists():
                with open(theme_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 如果主題文件不存在，返回預設樣式
                logger.warning(f"Theme file not found, using default style for {theme_name}")
                return self._get_default_stylesheet(theme_name)
                
        except Exception as e:
            logger.error(f"Error loading theme stylesheet: {e}")
            return self._get_default_stylesheet("dark_professional")
    
    def _get_default_stylesheet(self, theme_name: str) -> str:
        """獲取預設樣式表（當主題文件不存在時使用）"""
        if theme_name == "light_modern":
            return """
                QWidget {
                    background-color: #f8f9fa;
                    color: #212529;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #dee2e6;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #ced4da;
                    padding: 8px;
                    border-radius: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #dee2e6;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    border-bottom-color: #ffffff;
                }
            """
        elif theme_name == "blue_corporate":
            return """
                QWidget {
                    background-color: #1e3a8a;
                    color: #f1f5f9;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #3b82f6;
                    color: #ffffff;
                    border: 1px solid #2563eb;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #1e40af;
                    color: #f1f5f9;
                    border: 1px solid #3b82f6;
                    padding: 8px;
                    border-radius: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #3b82f6;
                    background-color: #1e3a8a;
                }
                QTabBar::tab {
                    background: #1e40af;
                    color: #f1f5f9;
                    border: 1px solid #3b82f6;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #1e3a8a;
                    border-bottom-color: #1e3a8a;
                }
            """
        elif theme_name == "high_contrast":
            return """
                QWidget {
                    background-color: #000000;
                    color: #ffffff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #ffffff;
                    padding: 10px 20px;
                    border-radius: 2px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ffff00;
                    color: #000000;
                    border-color: #ffff00;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #ffffff;
                    padding: 10px;
                    border-radius: 2px;
                    font-weight: bold;
                }
                QTabWidget::pane {
                    border: 2px solid #ffffff;
                    background-color: #000000;
                }
                QTabBar::tab {
                    background: #333333;
                    color: #ffffff;
                    border: 2px solid #ffffff;
                    padding: 10px 20px;
                    margin-right: 2px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: #000000;
                    border-bottom-color: #000000;
                }
            """
        else:  # dark_professional (預設)
            return """
                QWidget {
                    background-color: #2e2e2e;
                    color: #f0f0f0;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #555555;
                    color: #f0f0f0;
                    border: 1px solid #666666;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #666666;
                    border-color: #777777;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #3c3c3c;
                    color: #f0f0f0;
                    border: 1px solid #555555;
                    padding: 8px;
                    border-radius: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #444444;
                    background-color: #2e2e2e;
                }
                QTabBar::tab {
                    background: #3c3c3c;
                    color: #f0f0f0;
                    border: 1px solid #444444;
                    border-bottom-color: #3c3c3c;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #2e2e2e;
                    border-bottom-color: #2e2e2e;
                }
                QCheckBox {
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #888888;
                    background-color: #444444;
                    border-radius: 2px;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #007acc;
                    background-color: #007acc;
                    border-radius: 2px;
                }
            """
    
    def apply_current_theme(self):
        """應用當前配置的主題"""
        current_theme = self.get_current_theme()
        self.set_theme(current_theme)
    
    def refresh_themes(self):
        """重新載入所有主題"""
        self._load_available_themes()
        logger.info("Themes refreshed")
    
    def get_theme_preview_color(self, theme_name: str) -> str:
        """獲取主題預覽顏色"""
        theme_info = self.available_themes.get(theme_name, {})
        return theme_info.get("preview_color", "#2e2e2e")


# 全域主題管理器實例
theme_manager = ThemeManager()