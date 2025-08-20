# PyQt5 現代化深色主題界面實現指南

## 📖 前言

本文將詳細介紹如何在 PyQt5 應用中實現現代化的深色主題界面。通過完整的技術實現、設計思路和程式碼範例，讓不熟悉相關技術的開發者能夠快速複製相同的設計效果。

## 🎯 設計目標與理念

### 設計目標
- **視覺舒適性**：減少眼部疲勞，特別適合長時間使用
- **現代化外觀**：符合當代軟體設計趨勢
- **一致性體驗**：統一的色彩方案和視覺語言
- **可讀性優化**：確保文字和圖示在深色背景下清晰可見
- **專業感**：營造專業、高端的使用體驗

### 設計理念
1. **對比度平衡**：適度的對比度，避免過於刺眼或過於昏暗
2. **色彩分層**：使用不同深淺的灰色建立視覺層次
3. **重點突出**：使用色彩強調重要元素
4. **一致性原則**：所有UI元素遵循統一的設計規範

## 🏗️ 技術架構與實現方式

### 技術選型說明

**選擇 QSS (Qt Style Sheets) 的原因：**
1. **原生支援**：PyQt5 內建支援，無需額外依賴
2. **CSS 語法**：熟悉 CSS 的開發者可以快速上手
3. **完整控制**：可以精確控制每個UI元素的外觀
4. **效能優秀**：原生渲染，效能表現良好
5. **動態切換**：支援運行時主題切換

### 核心技術組件

```python
# 主要技術棧
技術組件:
├── QSS (Qt Style Sheets) - 樣式定義
├── QApplication.setStyleSheet() - 全域樣式應用
├── QWidget.setStyleSheet() - 局部樣式控制
├── QProxyStyle - 自定義樣式行為
└── QColor/QPalette - 色彩管理
```

## 🎨 色彩方案設計

### 主要色彩定義

```css
/* 深色主題色彩方案 */
:root {
    /* 背景色系 */
    --bg-primary: #1e1e1e;        /* 主背景 */
    --bg-secondary: #2d2d2d;      /* 次要背景 */
    --bg-tertiary: #3d3d3d;       /* 第三層背景 */
    --bg-elevated: #404040;       /* 懸浮元素背景 */
    
    /* 文字色系 */
    --text-primary: #ffffff;      /* 主要文字 */
    --text-secondary: #cccccc;    /* 次要文字 */
    --text-disabled: #808080;     /* 禁用文字 */
    --text-muted: #999999;        /* 弱化文字 */
    
    /* 邊框色系 */
    --border-primary: #555555;    /* 主要邊框 */
    --border-secondary: #404040;  /* 次要邊框 */
    --border-focus: #0078d4;      /* 焦點邊框 */
    
    /* 強調色系 */
    --accent-primary: #0078d4;    /* 主強調色 */
    --accent-hover: #106ebe;      /* 懸停效果 */
    --accent-pressed: #005a9e;    /* 按下效果 */
    
    /* 狀態色系 */
    --success: #107c10;           /* 成功色 */
    --warning: #ff8c00;           /* 警告色 */
    --error: #d13438;             /* 錯誤色 */
    --info: #00bcf2;              /* 資訊色 */
}
```

### 色彩應用原則

1. **背景漸層**：從深到淺建立視覺層次
2. **對比度控制**：確保文字可讀性達到 WCAG 標準
3. **強調色節制**：謹慎使用強調色，避免視覺雜亂
4. **狀態反饋**：不同狀態使用對應的色彩

## 🛠️ 核心實現技術

### 1. QSS 樣式表系統

#### 基礎語法結構
```css
/* QSS 基本語法 */
QWidget {
    property: value;
}

/* 偽狀態選擇器 */
QWidget:hover {
    property: value;
}

/* 子元素選擇器 */
QWidget::item {
    property: value;
}

/* 屬性選擇器 */
QWidget[property="value"] {
    property: value;
}
```

#### 完整主題樣式實現

```css
/* dark_professional.qss - 深色專業主題 */

/* =============================================================================
   全域樣式設定
============================================================================= */
QApplication {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 9pt;
}

/* =============================================================================
   主視窗樣式
============================================================================= */
QMainWindow {
    background-color: #1e1e1e;
    border: none;
}

QMainWindow::separator {
    background-color: #555555;
    width: 1px;
    height: 1px;
}

/* =============================================================================
   通用容器樣式
============================================================================= */
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    border: none;
    outline: none;
}

QFrame {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 4px;
}

/* =============================================================================
   按鈕樣式系統
============================================================================= */
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    color: #ffffff;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #0078d4;
}

QPushButton:pressed {
    background-color: #404040;
    border-color: #005a9e;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    border-color: #333333;
    color: #808080;
}

/* 主要按鈕樣式 */
QPushButton[primary="true"] {
    background-color: #0078d4;
    border-color: #0078d4;
    color: #ffffff;
}

QPushButton[primary="true"]:hover {
    background-color: #106ebe;
    border-color: #106ebe;
}

QPushButton[primary="true"]:pressed {
    background-color: #005a9e;
    border-color: #005a9e;
}

/* =============================================================================
   輸入框樣式
============================================================================= */
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 9pt;
    color: #ffffff;
    selection-background-color: #0078d4;
}

QLineEdit:focus {
    border-color: #0078d4;
    background-color: #3d3d3d;
}

QLineEdit:disabled {
    background-color: #1a1a1a;
    border-color: #333333;
    color: #808080;
}

QTextEdit {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    color: #ffffff;
    selection-background-color: #0078d4;
}

/* =============================================================================
   列表和樹狀視圖
============================================================================= */
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    outline: none;
}

QListWidget::item {
    padding: 4px 8px;
    border: none;
    color: #ffffff;
}

QListWidget::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QTreeWidget {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    outline: none;
    show-decoration-selected: 1;
}

QTreeWidget::item {
    height: 24px;
    padding: 2px;
    border: none;
}

QTreeWidget::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QTreeWidget::item:hover {
    background-color: #3d3d3d;
}

/* =============================================================================
   標籤頁樣式
============================================================================= */
QTabWidget::pane {
    border: 1px solid #555555;
    background-color: #1e1e1e;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-bottom: none;
    border-radius: 4px 4px 0px 0px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #cccccc;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
    color: #ffffff;
}

/* =============================================================================
   滾動條樣式
============================================================================= */
QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    border: none;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::handle:vertical:pressed {
    background-color: #777777;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 12px;
    border: none;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 6px;
    min-width: 20px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

QScrollBar::handle:horizontal:pressed {
    background-color: #777777;
}

/* =============================================================================
   進度條樣式
============================================================================= */
QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: 500;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 3px;
}

/* =============================================================================
   選單樣式
============================================================================= */
QMenuBar {
    background-color: #1e1e1e;
    border-bottom: 1px solid #555555;
    color: #ffffff;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
    color: #ffffff;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0078d4;
}

QMenu::separator {
    height: 1px;
    background-color: #555555;
    margin: 4px 8px;
}

/* =============================================================================
   工具提示樣式
============================================================================= */
QToolTip {
    background-color: #404040;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 6px 8px;
    color: #ffffff;
    font-size: 8pt;
}

/* =============================================================================
   狀態欄樣式
============================================================================= */
QStatusBar {
    background-color: #1e1e1e;
    border-top: 1px solid #555555;
    color: #cccccc;
    padding: 4px;
}

QStatusBar::item {
    border: none;
    padding: 2px 8px;
}

/* =============================================================================
   對話框樣式
============================================================================= */
QDialog {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 8px;
}

QDialogButtonBox {
    background-color: transparent;
    padding: 8px;
}

/* =============================================================================
   分隔器樣式
============================================================================= */
QSplitter::handle {
    background-color: #555555;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:pressed {
    background-color: #0078d4;
}
```

### 2. Python 主題管理系統

#### 主題管理器實現

```python
# theme_manager.py - 主題管理系統
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    """主題管理器 - 負責主題載入、切換和管理"""
    
    # 主題變更信號
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.themes_dir = Path(__file__).parent / "themes"
        self.current_theme = "dark_professional"
        self.available_themes = self._discover_themes()
        
    def _discover_themes(self):
        """自動發現可用主題"""
        themes = {}
        if not self.themes_dir.exists():
            return themes
            
        for qss_file in self.themes_dir.glob("*.qss"):
            theme_name = qss_file.stem
            themes[theme_name] = {
                "name": self._format_theme_name(theme_name),
                "file": str(qss_file),
                "description": self._get_theme_description(theme_name)
            }
        return themes
    
    def _format_theme_name(self, theme_name):
        """格式化主題名稱顯示"""
        name_mapping = {
            "dark_professional": "深色專業",
            "light_modern": "淺色現代", 
            "high_contrast": "高對比",
            "blue_corporate": "企業藍調"
        }
        return name_mapping.get(theme_name, theme_name.replace('_', ' ').title())
    
    def _get_theme_description(self, theme_name):
        """獲取主題描述"""
        descriptions = {
            "dark_professional": "專業的深色主題，適合長時間使用",
            "light_modern": "現代化淺色主題，簡潔明亮",
            "high_contrast": "高對比主題，提升可讀性",
            "blue_corporate": "企業風格藍色主題，商務專業"
        }
        return descriptions.get(theme_name, "自定義主題")
    
    def get_available_themes(self):
        """獲取可用主題列表"""
        return self.available_themes
    
    def get_current_theme(self):
        """獲取當前主題"""
        return self.current_theme
    
    def apply_theme(self, theme_name):
        """應用指定主題"""
        if theme_name not in self.available_themes:
            print(f"主題 '{theme_name}' 不存在")
            return False
            
        theme_file = self.available_themes[theme_name]["file"]
        
        try:
            # 讀取QSS檔案
            with open(theme_file, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            # 處理變數替換（如果需要）
            stylesheet = self._process_variables(stylesheet)
            
            # 應用樣式表
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                self.theme_changed.emit(theme_name)
                print(f"已切換到主題: {self.available_themes[theme_name]['name']}")
                return True
            
        except Exception as e:
            print(f"載入主題失敗: {e}")
            return False
        
        return False
    
    def _process_variables(self, stylesheet):
        """處理樣式表中的變數（CSS Variables 模擬）"""
        # 這裡可以實現 CSS 變數的替換邏輯
        # 例如：stylesheet = stylesheet.replace('var(--bg-primary)', '#1e1e1e')
        return stylesheet
    
    def reload_current_theme(self):
        """重新載入當前主題"""
        return self.apply_theme(self.current_theme)
    
    def create_custom_theme(self, base_theme, custom_colors, new_theme_name):
        """基於現有主題創建自定義主題"""
        if base_theme not in self.available_themes:
            return False
            
        try:
            # 讀取基礎主題
            base_file = self.available_themes[base_theme]["file"]
            with open(base_file, 'r', encoding='utf-8') as f:
                base_stylesheet = f.read()
            
            # 應用自定義顏色
            custom_stylesheet = self._apply_custom_colors(base_stylesheet, custom_colors)
            
            # 保存新主題
            new_theme_file = self.themes_dir / f"{new_theme_name}.qss"
            with open(new_theme_file, 'w', encoding='utf-8') as f:
                f.write(custom_stylesheet)
            
            # 更新可用主題列表
            self.available_themes[new_theme_name] = {
                "name": new_theme_name.replace('_', ' ').title(),
                "file": str(new_theme_file),
                "description": "自定義主題"
            }
            
            return True
            
        except Exception as e:
            print(f"創建自定義主題失敗: {e}")
            return False
    
    def _apply_custom_colors(self, stylesheet, custom_colors):
        """應用自定義顏色到樣式表"""
        for color_var, color_value in custom_colors.items():
            # 替換顏色變數
            stylesheet = stylesheet.replace(f"var(--{color_var})", color_value)
        return stylesheet
```

#### 主題選擇器組件

```python
# theme_selector.py - 主題選擇器界面組件
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QFrame,
                             QColorDialog, QGridLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor

class ThemeSelector(QWidget):
    """主題選擇器界面組件"""
    
    theme_selected = pyqtSignal(str)
    
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # 標題
        title_label = QLabel("主題設定")
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title_label)
        
        # 主題選擇區域
        theme_frame = QFrame()
        theme_frame.setFrameStyle(QFrame.StyledPanel)
        theme_layout = QVBoxLayout(theme_frame)
        
        # 主題選擇下拉選單
        theme_layout.addWidget(QLabel("選擇主題:"))
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(32)
        self._populate_theme_combo()
        theme_layout.addWidget(self.theme_combo)
        
        # 主題預覽區域
        preview_label = QLabel("主題預覽:")
        theme_layout.addWidget(preview_label)
        
        self.preview_area = QFrame()
        self.preview_area.setFixedHeight(100)
        self.preview_area.setFrameStyle(QFrame.StyledPanel)
        theme_layout.addWidget(self.preview_area)
        
        layout.addWidget(theme_frame)
        
        # 自定義顏色區域
        custom_frame = QFrame()
        custom_frame.setFrameStyle(QFrame.StyledPanel)
        custom_layout = QVBoxLayout(custom_frame)
        
        custom_layout.addWidget(QLabel("自定義顏色:"))
        
        # 顏色選擇網格
        color_grid = QGridLayout()
        self.color_buttons = {}
        
        color_options = [
            ("主背景", "bg_primary", "#1e1e1e"),
            ("次背景", "bg_secondary", "#2d2d2d"),
            ("強調色", "accent_primary", "#0078d4"),
            ("文字色", "text_primary", "#ffffff")
        ]
        
        for i, (label, key, default_color) in enumerate(color_options):
            row, col = i // 2, (i % 2) * 2
            
            color_grid.addWidget(QLabel(label), row, col)
            
            color_btn = QPushButton()
            color_btn.setFixedSize(40, 24)
            color_btn.setStyleSheet(f"background-color: {default_color}; border: 1px solid #555;")
            color_btn.clicked.connect(lambda checked, k=key, btn=color_btn: self._select_color(k, btn))
            self.color_buttons[key] = color_btn
            
            color_grid.addWidget(color_btn, row, col + 1)
        
        custom_layout.addLayout(color_grid)
        
        # 自定義主題按鈕
        create_theme_btn = QPushButton("創建自定義主題")
        create_theme_btn.clicked.connect(self._create_custom_theme)
        custom_layout.addWidget(create_theme_btn)
        
        layout.addWidget(custom_frame)
        
        # 控制按鈕
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("應用主題")
        self.apply_btn.setProperty("primary", True)
        button_layout.addWidget(self.apply_btn)
        
        reset_btn = QPushButton("重置")
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 連接信號
        self.apply_btn.clicked.connect(self._apply_selected_theme)
        reset_btn.clicked.connect(self._reset_to_default)
    
    def _populate_theme_combo(self):
        """填充主題下拉選單"""
        self.theme_combo.clear()
        themes = self.theme_manager.get_available_themes()
        
        for theme_key, theme_info in themes.items():
            self.theme_combo.addItem(theme_info["name"], theme_key)
        
        # 設定當前主題為選中項
        current_theme = self.theme_manager.get_current_theme()
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def _select_color(self, color_key, button):
        """選擇自定義顏色"""
        color = QColorDialog.getColor(Qt.white, self, "選擇顏色")
        if color.isValid():
            color_hex = color.name()
            button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #555;")
            # 存儲顏色值
            button.setProperty("color_value", color_hex)
    
    def _create_custom_theme(self):
        """創建自定義主題"""
        base_theme = self.theme_combo.currentData()
        custom_colors = {}
        
        # 收集自定義顏色
        for key, button in self.color_buttons.items():
            color_value = button.property("color_value")
            if color_value:
                custom_colors[key] = color_value
        
        if custom_colors:
            # 生成自定義主題名稱
            custom_theme_name = f"custom_{len(self.theme_manager.get_available_themes())}"
            
            if self.theme_manager.create_custom_theme(base_theme, custom_colors, custom_theme_name):
                # 重新填充下拉選單
                self._populate_theme_combo()
                # 選中新創建的主題
                index = self.theme_combo.findData(custom_theme_name)
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
    
    def _apply_selected_theme(self):
        """應用選中的主題"""
        theme_key = self.theme_combo.currentData()
        if theme_key:
            self.theme_manager.apply_theme(theme_key)
            self.theme_selected.emit(theme_key)
    
    def _reset_to_default(self):
        """重置到預設主題"""
        self.theme_manager.apply_theme("dark_professional")
        self._populate_theme_combo()
    
    def connect_signals(self):
        """連接信號"""
        self.theme_combo.currentTextChanged.connect(self._update_preview)
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _update_preview(self):
        """更新主題預覽"""
        # 這裡可以實現主題預覽功能
        # 例如顯示主要顏色的色塊
        pass
    
    def _on_theme_changed(self, theme_name):
        """主題變更時的處理"""
        # 更新界面狀態
        index = self.theme_combo.findData(theme_name)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
```

### 3. 主應用整合

```python
# main_window.py - 主視窗整合主題系統
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QSettings
from theme_manager import ThemeManager
from theme_selector import ThemeSelector

class ModernMainWindow(QMainWindow):
    """整合主題系統的主視窗"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化主題管理器
        self.theme_manager = ThemeManager()
        self.settings = QSettings("YourCompany", "YourApp")
        
        self.init_ui()
        self.load_saved_theme()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("現代化深色主題應用")
        self.setGeometry(100, 100, 1200, 800)
        
        # 創建中央組件
        self.create_central_widget()
        
        # 創建選單欄
        self.create_menu_bar()
        
        # 設定初始主題
        self.theme_manager.apply_theme("dark_professional")
    
    def create_central_widget(self):
        """創建中央組件"""
        # 這裡創建你的主要界面組件
        pass
    
    def create_menu_bar(self):
        """創建選單欄"""
        menubar = self.menuBar()
        
        # 視圖選單
        view_menu = menubar.addMenu("視圖")
        
        # 主題選單
        theme_action = view_menu.addAction("主題設定")
        theme_action.triggered.connect(self.show_theme_selector)
    
    def show_theme_selector(self):
        """顯示主題選擇器"""
        if not hasattr(self, 'theme_selector'):
            self.theme_selector = ThemeSelector(self.theme_manager)
            self.theme_selector.theme_selected.connect(self.save_theme_preference)
        
        self.theme_selector.show()
    
    def load_saved_theme(self):
        """載入保存的主題偏好"""
        saved_theme = self.settings.value("theme", "dark_professional")
        self.theme_manager.apply_theme(saved_theme)
    
    def save_theme_preference(self, theme_name):
        """保存主題偏好"""
        self.settings.setValue("theme", theme_name)
    
    def closeEvent(self, event):
        """視窗關閉事件"""
        # 保存當前主題
        current_theme = self.theme_manager.get_current_theme()
        self.settings.setValue("theme", current_theme)
        event.accept()

# 應用啟動
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 設定應用資訊（用於 QSettings）
    app.setOrganizationName("YourCompany")
    app.setApplicationName("YourApp")
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec_())
```

## 🎯 實現步驟詳解

### 步驟 1：專案結構準備

```
your_project/
├── main.py                    # 主程式入口
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # 主視窗
│   ├── theme_manager.py       # 主題管理器
│   └── theme_selector.py      # 主題選擇器
├── themes/
│   ├── dark_professional.qss  # 深色專業主題
│   ├── light_modern.qss       # 淺色現代主題
│   ├── high_contrast.qss      # 高對比主題
│   └── blue_corporate.qss     # 企業藍調主題
└── resources/
    ├── icons/                 # 圖示資源
    └── fonts/                 # 字體資源
```

### 步驟 2：建立基礎主題檔案

1. **創建 themes 目錄**
```bash
mkdir themes
```

2. **創建深色主題檔案**
```bash
touch themes/dark_professional.qss
```

3. **將完整 QSS 樣式複製到檔案中**（使用上面提供的完整樣式）

### 步驟 3：實現主題管理系統

1. **創建主題管理器**：實現 `ThemeManager` 類
2. **實現主題選擇器**：創建 `ThemeSelector` 組件
3. **整合到主應用**：在主視窗中整合主題系統

### 步驟 4：測試和優化

1. **測試主題切換**：確保所有UI組件都正確應用樣式
2. **測試不同解析度**：確保在不同螢幕解析度下的顯示效果
3. **效能優化**：優化樣式表載入和應用速度

## 🛡️ 常見問題與解決方案

### 問題 1：某些組件樣式不生效

**原因**：QSS 選擇器優先級或組件特殊性
**解決方案**：
```css
/* 使用更具體的選擇器 */
QWidget#specificWidget {
    /* 樣式 */
}

/* 或使用 !important（謹慎使用） */
QWidget {
    background-color: #1e1e1e !important;
}
```

### 問題 2：自定義組件樣式無效

**原因**：自定義組件需要特殊處理
**解決方案**：
```python
class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 設定物件名稱用於QSS選擇
        self.setObjectName("CustomWidget")
    
    def paintEvent(self, event):
        # 確保QSS樣式正確繪製
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
```

### 問題 3：主題切換後某些樣式殘留

**原因**：樣式表未完全覆蓋或清除
**解決方案**：
```python
def apply_theme(self, theme_name):
    # 先清空現有樣式
    app = QApplication.instance()
    app.setStyleSheet("")
    
    # 然後應用新樣式
    with open(theme_file, 'r', encoding='utf-8') as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)
```

### 問題 4：字體在不同系統顯示不一致

**原因**：系統字體差異
**解決方案**：
```css
/* 指定字體回退序列 */
QApplication {
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif;
}

/* 或載入自定義字體 */
@font-face {
    font-family: "CustomFont";
    src: url("fonts/custom-font.ttf");
}
```

## 🔄 替代方案與技術比較

### 1. QSS vs 原生樣式

| 特性 | QSS | 原生樣式 |
|------|-----|----------|
| 學習成本 | 中等（類似CSS） | 高（需了解Qt繪圖API） |
| 靈活性 | 高 | 最高 |
| 效能 | 良好 | 最佳 |
| 維護性 | 好 | 較差 |
| 跨平台 | 優秀 | 優秀 |

**推薦場景**：
- **QSS**：大部分應用場景，特別是需要快速實現的專案
- **原生樣式**：對效能要求極高或需要特殊效果的場景

### 2. 靜態主題 vs 動態主題

```python
# 靜態主題方案（推薦用於大部分場景）
class StaticThemeManager:
    def apply_theme(self, theme_name):
        with open(f"themes/{theme_name}.qss") as f:
            app.setStyleSheet(f.read())

# 動態主題方案（適合需要實時調整的場景）
class DynamicThemeManager:
    def __init__(self):
        self.color_variables = {
            "--bg-primary": "#1e1e1e",
            "--text-primary": "#ffffff"
            # ...更多變數
        }
    
    def update_color(self, variable, color):
        self.color_variables[variable] = color
        self._regenerate_stylesheet()
    
    def _regenerate_stylesheet(self):
        # 動態生成樣式表
        stylesheet = self._base_template
        for var, value in self.color_variables.items():
            stylesheet = stylesheet.replace(f"var({var})", value)
        app.setStyleSheet(stylesheet)
```

### 3. 第三方主題庫

**QDarkStyle**：
```python
# 優點：現成的深色主題，快速實現
# 缺點：客製化靈活性較低
import qdarkstyle
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
```

**Qt Material**：
```python
# 優點：Material Design 風格
# 缺點：可能與現有設計不符
from qt_material import apply_stylesheet
apply_stylesheet(app, theme='dark_teal.xml')
```

## 📈 效能優化建議

### 1. 樣式表優化

```css
/* 避免複雜選擇器 */
/* 不好的寫法 */
QWidget QFrame QLabel:hover {
    color: #ffffff;
}

/* 好的寫法 */
QLabel:hover {
    color: #ffffff;
}

/* 使用高效的屬性 */
/* 避免過度使用陰影和漸層 */
QPushButton {
    /* 簡單的背景色比漸層更高效 */
    background-color: #2d2d2d;
    /* border-radius 適中使用 */
    border-radius: 4px;
}
```

### 2. 載入優化

```python
class OptimizedThemeManager:
    def __init__(self):
        # 預載入常用主題
        self._theme_cache = {}
        self._preload_themes()
    
    def _preload_themes(self):
        """預載入主題到記憶體"""
        for theme in ["dark_professional", "light_modern"]:
            self._theme_cache[theme] = self._load_theme_file(theme)
    
    def apply_theme(self, theme_name):
        """使用快取的主題"""
        if theme_name in self._theme_cache:
            stylesheet = self._theme_cache[theme_name]
        else:
            stylesheet = self._load_theme_file(theme_name)
            self._theme_cache[theme_name] = stylesheet
        
        app = QApplication.instance()
        app.setStyleSheet(stylesheet)
```

### 3. 記憶體管理

```python
class ThemeManager:
    def cleanup_unused_themes(self):
        """清理未使用的主題快取"""
        current_theme = self.get_current_theme()
        for theme_name in list(self._theme_cache.keys()):
            if theme_name != current_theme:
                del self._theme_cache[theme_name]
    
    def __del__(self):
        """析構時清理資源"""
        if hasattr(self, '_theme_cache'):
            self._theme_cache.clear()
```

## 🎨 進階主題特性

### 1. 響應式主題

```python
class ResponsiveThemeManager(ThemeManager):
    def __init__(self):
        super().__init__()
        self.screen_size_changed.connect(self._adapt_theme)
    
    def _adapt_theme(self, screen_size):
        """根據螢幕大小調整主題"""
        if screen_size.width() < 1024:
            # 小螢幕使用更大的觸控友好元素
            self._apply_responsive_adjustments({
                "button_height": "36px",
                "font_size": "10pt",
                "padding": "10px"
            })
        else:
            # 大螢幕使用標準尺寸
            self._apply_responsive_adjustments({
                "button_height": "28px", 
                "font_size": "9pt",
                "padding": "8px"
            })
```

### 2. 動畫過渡主題

```python
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

class AnimatedThemeManager(ThemeManager):
    def apply_theme_with_animation(self, theme_name, duration=300):
        """使用動畫過渡切換主題"""
        
        # 創建淡出動畫
        self.fade_animation = QPropertyAnimation(self.main_widget, b"windowOpacity")
        self.fade_animation.setDuration(duration // 2)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 動畫完成後切換主題並淡入
        self.fade_animation.finished.connect(
            lambda: self._fade_in_with_new_theme(theme_name, duration // 2)
        )
        
        self.fade_animation.start()
    
    def _fade_in_with_new_theme(self, theme_name, duration):
        """應用新主題並淡入"""
        # 應用新主題
        self.apply_theme(theme_name)
        
        # 創建淡入動畫
        self.fade_in_animation = QPropertyAnimation(self.main_widget, b"windowOpacity")
        self.fade_in_animation.setDuration(duration)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_in_animation.start()
```

### 3. 自動主題切換

```python
import time
from PyQt5.QtCore import QTimer

class AutoThemeManager(ThemeManager):
    def __init__(self):
        super().__init__()
        self.auto_switch_enabled = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_time_based_theme)
        
    def enable_auto_switch(self, enabled=True):
        """啟用/停用自動主題切換"""
        self.auto_switch_enabled = enabled
        if enabled:
            self.timer.start(60000)  # 每分鐘檢查一次
        else:
            self.timer.stop()
    
    def _check_time_based_theme(self):
        """根據時間自動切換主題"""
        current_hour = time.localtime().tm_hour
        
        if 6 <= current_hour < 18:
            # 白天使用淺色主題
            target_theme = "light_modern"
        else:
            # 夜晚使用深色主題
            target_theme = "dark_professional"
        
        if self.get_current_theme() != target_theme:
            self.apply_theme(target_theme)
```

## 📚 實用資源與參考

### 官方文檔
- [Qt Style Sheets Reference](https://doc.qt.io/qt-5/stylesheet-reference.html)
- [Qt Style Sheets Examples](https://doc.qt.io/qt-5/stylesheet-examples.html)

### 設計指引
- [Material Design Dark Theme](https://material.io/design/color/dark-theme.html)
- [Apple Human Interface Guidelines - Dark Mode](https://developer.apple.com/design/human-interface-guidelines/macos/visual-design/dark-mode/)

### 工具和資源
- **顏色工具**：[Coolors.co](https://coolors.co/) - 調色盤生成
- **對比度檢查**：[WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- **QSS 編輯器**：Qt Creator 內建編輯器

### 開源專案參考
- [QDarkStyle](https://github.com/ColinDuquesnoy/QDarkStyleSheet)
- [Qt Material](https://github.com/UN-GCPDS/qt-material)

## 🎯 總結

通過本指南，您已經掌握了在 PyQt5 中實現現代化深色主題的完整技術體系：

### 核心要點回顧
1. **QSS 樣式系統**：類似 CSS 的語法，易於學習和使用
2. **模組化設計**：主題管理器、選擇器組件分離，便於維護
3. **動態切換**：支援運行時主題切換和自定義
4. **效能優化**：快取機制和高效的樣式表編寫
5. **擴展性**：支援自定義主題創建和進階特性

### 快速實現檢查清單
- [ ] 創建專案目錄結構
- [ ] 複製基礎主題檔案 (dark_professional.qss)
- [ ] 實現 ThemeManager 類
- [ ] 創建 ThemeSelector 組件
- [ ] 整合到主應用中
- [ ] 測試主題切換功能
- [ ] 根據需要自定義顏色和樣式

### 進階發展方向
- 實現更多主題變體
- 添加動畫過渡效果
- 整合響應式設計
- 開發主題編輯器
- 支援主題匯入/匯出

現代化深色主題不僅提升了應用的視覺品質，更重要的是改善了使用者體驗。通過合理的技術實現和持續的優化，您的應用將能夠提供專業、舒適的使用環境。

---

**作者**: Claude Code SuperClaude  
**版本**: 1.0  
**最後更新**: 2025-08-18  
**適用於**: PyQt5 5.15+, Python 3.7+