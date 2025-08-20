# PyQt5 分頁式工具整合界面設計指南

## 📖 前言

分頁式工具整合界面是現代桌面應用的核心設計模式之一，它允許將多個功能工具整合到統一的用戶界面中，提供直觀的導航和高效的工作流程。本指南將詳細介紹如何在 PyQt5 中實現專業級的分頁式工具整合界面，包含現代化設計理念、技術實現和最佳實踐。

## 🎯 設計理念與目標

### 核心設計理念

1. **統一體驗**：不同工具在同一界面框架下提供一致的用戶體驗
2. **高效導航**：用戶能夠快速在不同工具間切換，保持工作連續性
3. **上下文保持**：切換工具時保持當前的工作狀態和數據
4. **模組化架構**：每個工具獨立開發，易於擴展和維護
5. **專業外觀**：現代化的視覺設計，提升工具的專業感

### 設計目標

- **工具集成性**：將多個 CLI 工具整合為統一的圖形界面
- **用戶友好性**：降低 CLI 工具的使用門檻，提供直觀操作
- **工作流效率**：支援工具間的數據傳遞和協作
- **界面一致性**：所有工具遵循統一的設計規範
- **擴展性**：支援新工具的動態載入和註冊

## 🏗️ 技術架構設計

### 整體架構圖

```
分頁式工具整合界面架構
├── 界面管理層
│   ├── MainWindow (主視窗)           # QMainWindow 主容器
│   ├── NavigationSidebar (導航欄)    # 側邊欄導航
│   ├── ContentStack (內容堆疊)       # QStackedWidget 頁面管理
│   └── StatusBar (狀態欄)           # 狀態反饋
├── 工具整合層
│   ├── PluginManager (插件管理器)    # 工具註冊和生命週期管理
│   ├── ToolRegistry (工具註冊表)     # 工具元數據和配置
│   └── ViewManager (視圖管理器)      # 工具視圖的創建和管理
├── 工具實現層
│   ├── ToolView (工具視圖基類)       # 統一的工具視圖接口
│   ├── ToolController (工具控制器)   # 工具邏輯控制
│   └── ToolModel (工具模型)         # 工具數據模型
└── 基礎服務層
    ├── ThemeManager (主題管理)       # 統一主題系統
    ├── ConfigManager (配置管理)      # 配置持久化
    └── AnimationManager (動畫管理)   # 界面動畫效果
```

### 核心組件說明

**界面管理層**：
- 負責整體界面佈局和用戶交互
- 提供統一的導航和狀態反饋機制
- 管理不同工具視圖的顯示和切換

**工具整合層**：
- 實現工具的動態載入和註冊
- 管理工具的生命週期和資源
- 提供工具間的通信和協作機制

**工具實現層**：
- 定義統一的工具開發接口
- 實現具體工具的功能邏輯
- 確保所有工具的一致性體驗

## 💻 核心實現技術

### 1. 主視窗架構實現

```python
# main_window_architecture.py - 主視窗架構
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QFrame, QLabel, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ToolIntegrationMainWindow(QMainWindow):
    """
    分頁式工具整合主視窗
    
    核心功能：
    - 統一的界面框架
    - 動態工具載入
    - 導航管理
    - 狀態反饋
    """
    
    # 信號定義
    tool_changed = pyqtSignal(str)              # 工具切換信號
    tool_loaded = pyqtSignal(str, bool)         # 工具載入完成信號
    tool_error = pyqtSignal(str, str)           # 工具錯誤信號
    
    def __init__(self):
        super().__init__()
        
        # 核心屬性
        self.tools = {}                         # 已載入的工具字典
        self.current_tool = None                # 當前活動工具
        self.tool_views = {}                    # 工具視圖字典
        self.tool_configs = {}                  # 工具配置字典
        
        # UI 組件
        self.navigation_sidebar = None          # 導航側邊欄
        self.content_stack = None               # 內容堆疊組件
        self.welcome_page = None                # 歡迎頁面
        self.status_manager = None              # 狀態管理器
        
        # 管理器組件
        self.plugin_manager = None              # 插件管理器
        self.theme_manager = None               # 主題管理器
        self.animation_manager = None           # 動畫管理器
        
        self.setup_architecture()
    
    def setup_architecture(self):
        """設置整體架構"""
        try:
            # 初始化管理器
            self.initialize_managers()
            
            # 設置基礎 UI
            self.setup_basic_ui()
            
            # 設置導航系統
            self.setup_navigation_system()
            
            # 設置內容管理
            self.setup_content_management()
            
            # 設置狀態系統
            self.setup_status_system()
            
            # 載入工具
            self.load_available_tools()
            
            logger.info("Tool integration main window architecture setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up main window architecture: {e}")
            raise
    
    def initialize_managers(self):
        """初始化管理器組件"""
        from core.plugin_manager import PluginManager
        from ui.theme_manager import ThemeManager
        from ui.animation_manager import AnimationManager
        
        self.plugin_manager = PluginManager()
        self.theme_manager = ThemeManager()
        self.animation_manager = AnimationManager()
        
        # 連接管理器信號
        self.plugin_manager.plugin_loaded.connect(self.on_tool_loaded)
        self.plugin_manager.plugin_error.connect(self.on_tool_error)
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def setup_basic_ui(self):
        """設置基礎 UI 結構"""
        # 設置主視窗屬性
        self.setWindowTitle("工具整合平台")
        self.setMinimumSize(1200, 800)
        
        # 創建中央組件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 創建主分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # 設置樣式
        self.apply_main_window_styles()
    
    def setup_navigation_system(self):
        """設置導航系統"""
        # 創建導航側邊欄
        self.navigation_sidebar = ToolNavigationSidebar()
        self.navigation_sidebar.tool_selected.connect(self.switch_to_tool)
        self.navigation_sidebar.home_selected.connect(self.show_welcome_page)
        
        # 添加到主分割器
        self.main_splitter.addWidget(self.navigation_sidebar)
        
        # 設置導航欄寬度
        self.navigation_sidebar.setFixedWidth(250)
        self.navigation_sidebar.setMinimumWidth(200)
        self.navigation_sidebar.setMaximumWidth(300)
    
    def setup_content_management(self):
        """設置內容管理"""
        # 創建內容堆疊組件
        self.content_stack = QStackedWidget()
        
        # 創建歡迎頁面
        self.welcome_page = ToolWelcomePage()
        self.content_stack.addWidget(self.welcome_page)
        
        # 添加到主分割器
        self.main_splitter.addWidget(self.content_stack)
        
        # 設置分割比例
        self.main_splitter.setStretchFactor(0, 0)  # 導航欄固定寬度
        self.main_splitter.setStretchFactor(1, 1)  # 內容區域自適應
        
        # 顯示歡迎頁面
        self.content_stack.setCurrentWidget(self.welcome_page)
    
    def setup_status_system(self):
        """設置狀態系統"""
        # 創建狀態欄
        self.status_bar = self.statusBar()
        
        # 創建狀態管理器
        self.status_manager = StatusManager(self.status_bar)
        
        # 創建選單欄
        self.create_menu_bar()
        
        # 設置初始狀態
        self.status_manager.set_status("準備就緒", "ready")
    
    def load_available_tools(self):
        """載入可用工具"""
        try:
            self.status_manager.set_status("載入工具中...", "loading")
            
            # 獲取可用工具列表
            available_tools = self.plugin_manager.discover_tools()
            
            # 載入每個工具
            for tool_id, tool_info in available_tools.items():
                self.load_tool(tool_id, tool_info)
            
            # 更新導航欄
            self.navigation_sidebar.update_tool_list(self.tools)
            
            self.status_manager.set_status(f"已載入 {len(self.tools)} 個工具", "ready")
            
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
            self.status_manager.set_status(f"載入工具失敗: {e}", "error")
    
    def load_tool(self, tool_id: str, tool_info: Dict[str, Any]):
        """載入單個工具"""
        try:
            # 載入工具插件
            tool_plugin = self.plugin_manager.load_plugin(tool_id, tool_info)
            
            if tool_plugin:
                # 創建工具視圖
                tool_view = tool_plugin.create_view()
                
                # 註冊工具
                self.tools[tool_id] = {
                    'plugin': tool_plugin,
                    'view': tool_view,
                    'info': tool_info,
                    'loaded': True
                }
                
                # 添加到內容堆疊
                self.content_stack.addWidget(tool_view)
                self.tool_views[tool_id] = tool_view
                
                # 發送載入完成信號
                self.tool_loaded.emit(tool_id, True)
                
                logger.info(f"Tool loaded successfully: {tool_id}")
                
            else:
                # 載入失敗
                self.tool_error.emit(tool_id, "Failed to load tool plugin")
                
        except Exception as e:
            logger.error(f"Error loading tool {tool_id}: {e}")
            self.tool_error.emit(tool_id, str(e))
    
    def switch_to_tool(self, tool_id: str):
        """切換到指定工具"""
        try:
            if tool_id in self.tool_views:
                # 獲取工具視圖
                tool_view = self.tool_views[tool_id]
                
                # 切換到工具視圖
                self.content_stack.setCurrentWidget(tool_view)
                
                # 更新當前工具
                old_tool = self.current_tool
                self.current_tool = tool_id
                
                # 更新狀態
                tool_info = self.tools[tool_id]['info']
                tool_name = tool_info.get('name', tool_id)
                self.status_manager.set_status(f"當前工具: {tool_name}", "active")
                
                # 更新導航狀態
                self.navigation_sidebar.set_active_tool(tool_id)
                
                # 觸發工具激活事件
                if hasattr(tool_view, 'on_activated'):
                    tool_view.on_activated()
                
                # 發送工具切換信號
                self.tool_changed.emit(tool_id)
                
                logger.info(f"Switched to tool: {tool_id}")
                
            else:
                logger.warning(f"Tool not found: {tool_id}")
                self.status_manager.set_status(f"工具未找到: {tool_id}", "warning")
                
        except Exception as e:
            logger.error(f"Error switching to tool {tool_id}: {e}")
            self.status_manager.set_status(f"切換工具失敗: {e}", "error")
    
    def show_welcome_page(self):
        """顯示歡迎頁面"""
        try:
            self.content_stack.setCurrentWidget(self.welcome_page)
            self.current_tool = None
            
            # 更新狀態
            self.status_manager.set_status("歡迎使用工具整合平台", "ready")
            
            # 更新導航狀態
            self.navigation_sidebar.set_active_tool(None)
            
            logger.info("Switched to welcome page")
            
        except Exception as e:
            logger.error(f"Error showing welcome page: {e}")
    
    def on_tool_loaded(self, tool_id: str, success: bool):
        """處理工具載入完成"""
        if success:
            logger.info(f"Tool loaded successfully: {tool_id}")
        else:
            logger.error(f"Tool loading failed: {tool_id}")
    
    def on_tool_error(self, tool_id: str, error_message: str):
        """處理工具錯誤"""
        logger.error(f"Tool error [{tool_id}]: {error_message}")
        self.status_manager.set_status(f"工具錯誤 [{tool_id}]: {error_message}", "error")
    
    def on_theme_changed(self, theme_name: str):
        """處理主題變更"""
        logger.info(f"Theme changed to: {theme_name}")
        self.status_manager.set_status(f"主題已切換: {theme_name}", "info")
    
    def create_menu_bar(self):
        """創建選單欄"""
        menubar = self.menuBar()
        
        # 檔案選單
        file_menu = menubar.addMenu('檔案(&F)')
        
        # 新建動作
        new_action = file_menu.addAction('新建(&N)')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        
        # 開啟動作
        open_action = file_menu.addAction('開啟(&O)')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        
        file_menu.addSeparator()
        
        # 退出動作
        exit_action = file_menu.addAction('退出(&X)')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # 工具選單
        tools_menu = menubar.addMenu('工具(&T)')
        
        # 重新載入工具
        reload_action = tools_menu.addAction('重新載入工具(&R)')
        reload_action.setShortcut('F5')
        reload_action.triggered.connect(self.reload_tools)
        
        # 工具設定
        settings_action = tools_menu.addAction('工具設定(&S)')
        settings_action.triggered.connect(self.show_tool_settings)
        
        # 檢視選單
        view_menu = menubar.addMenu('檢視(&V)')
        
        # 主題選擇
        theme_action = view_menu.addAction('主題設定(&T)')
        theme_action.triggered.connect(self.show_theme_settings)
        
        view_menu.addSeparator()
        
        # 全螢幕
        fullscreen_action = view_menu.addAction('全螢幕(&F)')
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        
        # 說明選單
        help_menu = menubar.addMenu('說明(&H)')
        
        # 使用說明
        help_action = help_menu.addAction('使用說明(&H)')
        help_action.setShortcut('F1')
        help_action.triggered.connect(self.show_help)
        
        # 關於
        about_action = help_menu.addAction('關於(&A)')
        about_action.triggered.connect(self.show_about)
    
    def apply_main_window_styles(self):
        """應用主視窗樣式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QMainWindow::separator {
                background-color: #555555;
                width: 2px;
                height: 2px;
            }
            
            QMainWindow::separator:hover {
                background-color: #0078d4;
            }
        """)
    
    # 選單動作實現
    def new_file(self):
        """新建檔案"""
        if self.current_tool and hasattr(self.tool_views[self.current_tool], 'new_file'):
            self.tool_views[self.current_tool].new_file()
    
    def open_file(self):
        """開啟檔案"""
        if self.current_tool and hasattr(self.tool_views[self.current_tool], 'open_file'):
            self.tool_views[self.current_tool].open_file()
    
    def reload_tools(self):
        """重新載入工具"""
        self.load_available_tools()
    
    def show_tool_settings(self):
        """顯示工具設定"""
        # 實現工具設定對話框
        pass
    
    def show_theme_settings(self):
        """顯示主題設定"""
        # 實現主題設定對話框
        pass
    
    def toggle_fullscreen(self):
        """切換全螢幕"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_help(self):
        """顯示使用說明"""
        # 實現使用說明對話框
        pass
    
    def show_about(self):
        """顯示關於對話框"""
        # 實現關於對話框
        pass
    
    def get_current_tool_info(self) -> Optional[Dict[str, Any]]:
        """獲取當前工具資訊"""
        if self.current_tool and self.current_tool in self.tools:
            return self.tools[self.current_tool]
        return None
    
    def get_tool_list(self) -> List[str]:
        """獲取工具列表"""
        return list(self.tools.keys())
    
    def is_tool_loaded(self, tool_id: str) -> bool:
        """檢查工具是否已載入"""
        return tool_id in self.tools and self.tools[tool_id].get('loaded', False)
```

### 2. 導航側邊欄實現

```python
# navigation_sidebar.py - 導航側邊欄
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QWidget, QButtonGroup)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ToolNavigationSidebar(QFrame):
    """
    工具導航側邊欄
    
    功能：
    - 顯示可用工具列表
    - 提供工具間快速切換
    - 顯示工具狀態和圖示
    - 支援分組和搜尋
    """
    
    # 信號定義
    tool_selected = pyqtSignal(str)        # 工具選擇信號
    home_selected = pyqtSignal()           # 首頁選擇信號
    tool_context_menu = pyqtSignal(str)    # 工具右鍵選單信號
    
    def __init__(self):
        super().__init__()
        
        # 狀態屬性
        self.active_tool = None                 # 當前活動工具
        self.tool_buttons = {}                  # 工具按鈕字典
        self.tool_groups = {}                   # 工具分組字典
        self.button_group = QButtonGroup()      # 按鈕組（用於單選）
        
        # UI 組件
        self.search_box = None                  # 搜尋框
        self.tool_list_widget = None            # 工具列表組件
        self.home_button = None                 # 首頁按鈕
        
        self.setup_ui()
        self.setup_styles()
    
    def setup_ui(self):
        """設置 UI 結構"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 頁首區域
        self.setup_header(main_layout)
        
        # 搜尋區域
        self.setup_search_area(main_layout)
        
        # 首頁按鈕
        self.setup_home_button(main_layout)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #555555; height: 1px;")
        main_layout.addWidget(separator)
        
        # 工具列表區域
        self.setup_tool_list_area(main_layout)
        
        # 底部狀態區域
        self.setup_footer(main_layout)
    
    def setup_header(self, layout):
        """設置頁首區域"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 16, 16, 8)
        
        # 標題
        title_label = QLabel("工具導航")
        title_label.setFont(QFont("", 14, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 4px;")
        header_layout.addWidget(title_label)
        
        # 子標題
        subtitle_label = QLabel("選擇要使用的工具")
        subtitle_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_widget)
    
    def setup_search_area(self, layout):
        """設置搜尋區域"""
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(16, 8, 16, 8)
        
        # 搜尋框
        from ui.components.inputs import ModernLineEdit
        self.search_box = ModernLineEdit()
        self.search_box.setPlaceholderText("搜尋工具...")
        self.search_box.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_box)
        
        layout.addWidget(search_widget)
    
    def setup_home_button(self, layout):
        """設置首頁按鈕"""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_layout.setContentsMargins(16, 8, 16, 8)
        
        self.home_button = ToolNavigationButton("🏠", "首頁", "返回首頁歡迎頁面")
        self.home_button.clicked.connect(self.on_home_clicked)
        self.button_group.addButton(self.home_button)
        
        home_layout.addWidget(self.home_button)
        layout.addWidget(home_widget)
    
    def setup_tool_list_area(self, layout):
        """設置工具列表區域"""
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 工具列表容器
        self.tool_list_widget = QWidget()
        self.tool_list_layout = QVBoxLayout(self.tool_list_widget)
        self.tool_list_layout.setContentsMargins(16, 8, 16, 8)
        self.tool_list_layout.setSpacing(4)
        self.tool_list_layout.addStretch()  # 底部彈性空間
        
        scroll_area.setWidget(self.tool_list_widget)
        layout.addWidget(scroll_area, 1)  # 佔用剩餘空間
    
    def setup_footer(self, layout):
        """設置底部狀態區域"""
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(16, 8, 16, 16)
        
        # 狀態標籤
        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        footer_layout.addWidget(self.status_label)
        
        layout.addWidget(footer_widget)
    
    def update_tool_list(self, tools: Dict[str, Any]):
        """更新工具列表"""
        try:
            # 清除現有工具按鈕
            self.clear_tool_buttons()
            
            # 按分類組織工具
            categorized_tools = self.categorize_tools(tools)
            
            # 為每個分類創建工具按鈕
            for category, tool_list in categorized_tools.items():
                self.add_tool_category(category, tool_list)
            
            # 更新狀態
            tool_count = len(tools)
            self.status_label.setText(f"已載入 {tool_count} 個工具")
            
            logger.info(f"Updated tool list with {tool_count} tools")
            
        except Exception as e:
            logger.error(f"Error updating tool list: {e}")
    
    def categorize_tools(self, tools: Dict[str, Any]) -> Dict[str, List]:
        """按分類組織工具"""
        categories = {
            "檔案工具": [],
            "轉換工具": [], 
            "查看工具": [],
            "系統工具": [],
            "其他工具": []
        }
        
        # 工具分類映射
        category_mapping = {
            "fd": "檔案工具",
            "ripgrep": "檔案工具", 
            "pandoc": "轉換工具",
            "glow": "查看工具",
            "bat": "查看工具",
            "dust": "系統工具",
            "glances": "系統工具",
            "csvkit": "轉換工具",
            "poppler": "轉換工具"
        }
        
        for tool_id, tool_data in tools.items():
            category = category_mapping.get(tool_id, "其他工具")
            categories[category].append((tool_id, tool_data))
        
        # 移除空分類
        return {k: v for k, v in categories.items() if v}
    
    def add_tool_category(self, category_name: str, tools: List):
        """添加工具分類"""
        if not tools:
            return
        
        # 分類標題
        category_label = QLabel(category_name)
        category_label.setFont(QFont("", 10, QFont.Bold))
        category_label.setStyleSheet("""
            color: #aaaaaa; 
            margin-top: 8px; 
            margin-bottom: 4px;
            padding-left: 4px;
        """)
        
        # 插入到 stretch 之前
        insert_index = self.tool_list_layout.count() - 1
        self.tool_list_layout.insertWidget(insert_index, category_label)
        
        # 添加該分類下的工具
        for tool_id, tool_data in tools:
            tool_button = self.create_tool_button(tool_id, tool_data)
            self.tool_list_layout.insertWidget(insert_index + 1, tool_button)
            insert_index += 1
    
    def create_tool_button(self, tool_id: str, tool_data: Dict) -> QPushButton:
        """創建工具按鈕"""
        # 獲取工具資訊
        tool_info = tool_data.get('info', {})
        tool_name = tool_info.get('name', tool_id.title())
        tool_description = tool_info.get('description', f"{tool_name} 工具")
        
        # 工具圖示映射
        icon_mapping = {
            "fd": "🔍",
            "ripgrep": "🔎", 
            "pandoc": "🔄",
            "glow": "📖",
            "bat": "🌈",
            "dust": "💾",
            "glances": "📈",
            "csvkit": "📊",
            "poppler": "📄"
        }
        
        icon = icon_mapping.get(tool_id, "🔧")
        
        # 創建按鈕
        button = ToolNavigationButton(icon, tool_name, tool_description)
        button.clicked.connect(lambda: self.on_tool_clicked(tool_id))
        
        # 添加到按鈕組和字典
        self.button_group.addButton(button)
        self.tool_buttons[tool_id] = button
        
        return button
    
    def clear_tool_buttons(self):
        """清除現有工具按鈕"""
        # 移除所有按鈕
        for button in self.tool_buttons.values():
            self.button_group.removeButton(button)
            button.setParent(None)
            button.deleteLater()
        
        # 清除字典
        self.tool_buttons.clear()
        
        # 清除佈局中的所有組件（保留 stretch）
        while self.tool_list_layout.count() > 1:
            child = self.tool_list_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
                child.widget().deleteLater()
    
    def on_home_clicked(self):
        """處理首頁按鈕點擊"""
        self.set_active_tool(None)
        self.home_selected.emit()
        logger.info("Home button clicked")
    
    def on_tool_clicked(self, tool_id: str):
        """處理工具按鈕點擊"""
        self.set_active_tool(tool_id)
        self.tool_selected.emit(tool_id)
        logger.info(f"Tool button clicked: {tool_id}")
    
    def set_active_tool(self, tool_id: Optional[str]):
        """設置活動工具"""
        self.active_tool = tool_id
        
        # 更新按鈕狀態
        if tool_id is None:
            # 選中首頁按鈕
            self.home_button.setChecked(True)
        else:
            # 選中對應工具按鈕
            if tool_id in self.tool_buttons:
                self.tool_buttons[tool_id].setChecked(True)
    
    def filter_tools(self, search_text: str):
        """過濾工具列表"""
        search_text = search_text.lower().strip()
        
        for tool_id, button in self.tool_buttons.items():
            # 檢查工具 ID 和名稱是否匹配
            tool_name = button.text().lower()
            should_show = search_text in tool_id.lower() or search_text in tool_name
            
            button.setVisible(should_show)
    
    def setup_styles(self):
        """設置樣式"""
        self.setStyleSheet("""
            ToolNavigationSidebar {
                background-color: #2d2d2d;
                border-right: 1px solid #555555;
            }
            
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background-color: #3d3d3d;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)

class ToolNavigationButton(QPushButton):
    """工具導航按鈕"""
    
    def __init__(self, icon: str, name: str, description: str):
        super().__init__()
        
        self.tool_name = name
        self.tool_description = description
        
        # 設置按鈕屬性
        self.setText(f"{icon}  {name}")
        self.setCheckable(True)
        self.setToolTip(description)
        
        # 設置樣式
        self.setup_styles()
        
        # 設置動畫
        self.setup_hover_animation()
    
    def setup_styles(self):
        """設置按鈕樣式"""
        self.setStyleSheet("""
            ToolNavigationButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 12px 16px;
                text-align: left;
                font-size: 13px;
                color: #cccccc;
                min-height: 40px;
            }
            
            ToolNavigationButton:hover {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            
            ToolNavigationButton:checked {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            ToolNavigationButton:checked:hover {
                background-color: #106ebe;
            }
        """)
    
    def setup_hover_animation(self):
        """設置懸停動畫"""
        # 這裡可以添加懸停動畫效果
        pass
```

### 3. 工具視圖基類

```python
# tool_view_base.py - 工具視圖基類
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseToolView(QWidget, ABC):
    """
    工具視圖基類
    
    定義所有工具視圖的統一接口和通用功能：
    - 統一的頁首佈局
    - 標準化的狀態管理
    - 一致的錯誤處理
    - 通用的配置管理
    """
    
    # 通用信號定義
    status_changed = pyqtSignal(str, str)       # 狀態變更信號 (message, level)
    error_occurred = pyqtSignal(str)            # 錯誤發生信號
    operation_started = pyqtSignal(str)         # 操作開始信號
    operation_completed = pyqtSignal(str, bool) # 操作完成信號 (operation, success)
    data_changed = pyqtSignal()                 # 數據變更信號
    
    def __init__(self, tool_id: str, tool_name: str, tool_description: str):
        super().__init__()
        
        # 工具屬性
        self.tool_id = tool_id
        self.tool_name = tool_name  
        self.tool_description = tool_description
        
        # 狀態屬性
        self.is_initialized = False
        self.is_active = False
        self.current_operation = None
        self.last_error = None
        
        # UI 組件
        self.header_widget = None
        self.content_widget = None
        self.status_widget = None
        
        # 配置
        self.tool_config = {}
        
        self.setup_base_ui()
        self.setup_tool_ui()
        self.load_tool_config()
        
        # 標記為已初始化
        self.is_initialized = True
        
        logger.info(f"Tool view initialized: {self.tool_id}")
    
    def setup_base_ui(self):
        """設置基礎 UI 結構"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 頁首區域
        self.header_widget = self.create_header_widget()
        main_layout.addWidget(self.header_widget)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #555555; height: 1px;")
        main_layout.addWidget(separator)
        
        # 內容區域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        
        main_layout.addWidget(self.content_widget, 1)  # 內容區域佔用剩餘空間
        
        # 狀態區域
        self.status_widget = self.create_status_widget()
        main_layout.addWidget(self.status_widget)
    
    def create_header_widget(self) -> QWidget:
        """創建頁首組件"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        # 工具資訊
        info_layout = QVBoxLayout()
        
        # 工具名稱
        name_label = QLabel(self.tool_name)
        name_label.setFont(QFont("", 16, QFont.Bold))
        name_label.setStyleSheet("color: #ffffff; margin-bottom: 4px;")
        info_layout.addWidget(name_label)
        
        # 工具描述
        desc_label = QLabel(self.tool_description)
        desc_label.setStyleSheet("color: #cccccc; font-size: 13px;")
        info_layout.addWidget(desc_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # 工具操作按鈕區域
        self.setup_header_actions(header_layout)
        
        # 設置樣式
        header.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 1px solid #555555;
            }
        """)
        
        return header
    
    def create_status_widget(self) -> QWidget:
        """創建狀態組件"""
        status = QWidget()
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(20, 8, 20, 8)
        
        # 狀態標籤
        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # 狀態指示器
        from ui.components.indicators import StatusIndicator
        self.status_indicator = StatusIndicator("ready")
        status_layout.addWidget(self.status_indicator)
        
        # 設置樣式
        status.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top: 1px solid #555555;
            }
        """)
        
        return status
    
    def setup_header_actions(self, layout):
        """設置頁首操作按鈕"""
        # 預設的頁首操作
        from ui.components.buttons import ModernButton
        
        # 重新整理按鈕
        refresh_button = ModernButton("🔄")
        refresh_button.setToolTip("重新整理")
        refresh_button.clicked.connect(self.refresh)
        layout.addWidget(refresh_button)
        
        # 設定按鈕
        settings_button = ModernButton("⚙️")
        settings_button.setToolTip("設定")
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)
        
        # 子類可以重寫此方法來添加自定義按鈕
        self.setup_custom_header_actions(layout)
    
    def setup_custom_header_actions(self, layout):
        """設置自定義頁首操作（子類重寫）"""
        pass
    
    @abstractmethod
    def setup_tool_ui(self):
        """設置工具特定的 UI（子類實現）"""
        pass
    
    def load_tool_config(self):
        """載入工具配置"""
        try:
            from config.config_manager import config_manager
            self.tool_config = config_manager.get_tool_config(self.tool_id)
            self.apply_tool_config()
            
        except Exception as e:
            logger.error(f"Error loading tool config for {self.tool_id}: {e}")
    
    def apply_tool_config(self):
        """應用工具配置（子類可重寫）"""
        pass
    
    def save_tool_config(self):
        """保存工具配置"""
        try:
            from config.config_manager import config_manager
            config_manager.set_tool_config(self.tool_id, self.tool_config)
            
        except Exception as e:
            logger.error(f"Error saving tool config for {self.tool_id}: {e}")
    
    def set_status(self, message: str, level: str = "info"):
        """設置狀態訊息"""
        self.status_label.setText(message)
        self.status_indicator.set_status(level)
        self.status_changed.emit(message, level)
        
        logger.debug(f"Status changed [{self.tool_id}]: {message} ({level})")
    
    def show_error(self, error_message: str):
        """顯示錯誤訊息"""
        self.last_error = error_message
        self.set_status(f"錯誤: {error_message}", "error")
        self.error_occurred.emit(error_message)
        
        logger.error(f"Error in tool {self.tool_id}: {error_message}")
    
    def start_operation(self, operation_name: str):
        """開始操作"""
        self.current_operation = operation_name
        self.set_status(f"正在 {operation_name}...", "processing")
        self.operation_started.emit(operation_name)
        
        logger.info(f"Operation started [{self.tool_id}]: {operation_name}")
    
    def complete_operation(self, operation_name: str, success: bool = True, message: str = ""):
        """完成操作"""
        self.current_operation = None
        
        if success:
            status_message = message or f"{operation_name} 完成"
            self.set_status(status_message, "success")
        else:
            error_message = message or f"{operation_name} 失敗"
            self.show_error(error_message)
        
        self.operation_completed.emit(operation_name, success)
        
        logger.info(f"Operation completed [{self.tool_id}]: {operation_name} (success: {success})")
    
    def on_activated(self):
        """工具被激活時的回調"""
        if not self.is_active:
            self.is_active = True
            self.set_status(f"{self.tool_name} 已激活", "active")
            
            # 子類可以重寫此方法
            self.on_tool_activated()
            
            logger.info(f"Tool activated: {self.tool_id}")
    
    def on_deactivated(self):
        """工具被停用時的回調"""
        if self.is_active:
            self.is_active = False
            
            # 子類可以重寫此方法
            self.on_tool_deactivated()
            
            logger.info(f"Tool deactivated: {self.tool_id}")
    
    def on_tool_activated(self):
        """工具激活回調（子類可重寫）"""
        pass
    
    def on_tool_deactivated(self):
        """工具停用回調（子類可重寫）"""
        pass
    
    def refresh(self):
        """重新整理工具（子類可重寫）"""
        self.set_status("重新整理中...", "processing")
        QTimer.singleShot(500, lambda: self.set_status("重新整理完成", "success"))
    
    def show_settings(self):
        """顯示設定對話框（子類可重寫）"""
        self.set_status("打開設定...", "info")
    
    def get_window_title(self) -> str:
        """獲取視窗標題"""
        return self.tool_name
    
    def get_tool_info(self) -> Dict[str, Any]:
        """獲取工具資訊"""
        return {
            'id': self.tool_id,
            'name': self.tool_name,
            'description': self.tool_description,
            'is_active': self.is_active,
            'current_operation': self.current_operation,
            'last_error': self.last_error
        }
    
    def cleanup(self):
        """清理資源（工具被移除時調用）"""
        self.on_deactivated()
        self.save_tool_config()
        
        logger.info(f"Tool cleanup completed: {self.tool_id}")
```

### 4. 歡迎頁面實現

```python
# welcome_page.py - 歡迎頁面
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QFrame, QScrollArea, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
import logging

logger = logging.getLogger(__name__)

class ToolWelcomePage(QWidget):
    """
    工具整合平台歡迎頁面
    
    功能：
    - 展示平台介紹和特色
    - 提供快速開始指引
    - 顯示最近使用的工具
    - 展示工具功能卡片
    """
    
    # 信號定義
    tool_quick_access = pyqtSignal(str)     # 快速存取工具信號
    tutorial_requested = pyqtSignal()       # 教學請求信號
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """設置 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 滾動內容
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(40)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # 歡迎區域
        self.setup_welcome_section(content_layout)
        
        # 特色介紹區域
        self.setup_features_section(content_layout)
        
        # 快速開始區域
        self.setup_quick_start_section(content_layout)
        
        # 工具展示區域
        self.setup_tools_showcase(content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 設置樣式
        self.setup_styles()
    
    def setup_welcome_section(self, layout):
        """設置歡迎區域"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(20)
        
        # 主標題
        title_label = QLabel("工具整合平台")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("", 28, QFont.Bold))
        title_label.setStyleSheet("""
            color: #ffffff;
            margin-bottom: 16px;
        """)
        welcome_layout.addWidget(title_label)
        
        # 副標題
        subtitle_label = QLabel("整合多種專業工具的現代化圖形界面")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("", 16))
        subtitle_label.setStyleSheet("""
            color: #cccccc;
            margin-bottom: 24px;
        """)
        welcome_layout.addWidget(subtitle_label)
        
        # 版本資訊
        version_label = QLabel("Version 1.0 | 專業版")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            color: #888888;
            font-size: 14px;
        """)
        welcome_layout.addWidget(version_label)
        
        layout.addWidget(welcome_widget)
    
    def setup_features_section(self, layout):
        """設置特色介紹區域"""
        # 區域標題
        section_title = QLabel("平台特色")
        section_title.setFont(QFont("", 20, QFont.Bold))
        section_title.setStyleSheet("color: #ffffff; margin-bottom: 16px;")
        layout.addWidget(section_title)
        
        # 特色卡片網格
        features_widget = QWidget()
        features_grid = QGridLayout(features_widget)
        features_grid.setSpacing(24)
        
        # 定義特色列表
        features = [
            ("🎯", "統一界面", "將多個 CLI 工具整合到統一的圖形界面中，提供一致的用戶體驗。"),
            ("⚡", "高效操作", "直觀的操作界面，大幅降低命令列工具的使用門檻。"),
            ("🔧", "工具豐富", "整合 9+ 種專業工具，涵蓋檔案處理、文檔轉換、系統監控等。"),
            ("🎨", "現代設計", "採用現代化設計理念，支援深色主題和響應式佈局。"),
            ("📈", "實時監控", "提供實時的系統監控和任務進度反饋。"),
            ("⚙️", "靈活配置", "豐富的配置選項，支援個性化定制和工作流程優化。")
        ]
        
        for i, (icon, title, description) in enumerate(features):
            row = i // 2
            col = i % 2
            
            feature_card = self.create_feature_card(icon, title, description)
            features_grid.addWidget(feature_card, row, col)
        
        layout.addWidget(features_widget)
    
    def create_feature_card(self, icon: str, title: str, description: str) -> QFrame:
        """創建特色卡片"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # 圖示
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("", 32))
        card_layout.addWidget(icon_label)
        
        # 標題
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("", 16, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
        card_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #cccccc; line-height: 1.5;")
        card_layout.addWidget(desc_label)
        
        # 設置卡片樣式
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            
            QFrame:hover {
                background-color: #3d3d3d;
                border-color: #0078d4;
            }
        """)
        
        return card
    
    def setup_quick_start_section(self, layout):
        """設置快速開始區域"""
        # 區域標題
        section_title = QLabel("快速開始")
        section_title.setFont(QFont("", 20, QFont.Bold))
        section_title.setStyleSheet("color: #ffffff; margin-bottom: 16px;")
        layout.addWidget(section_title)
        
        # 快速開始內容
        quick_start_widget = QWidget()
        quick_start_layout = QVBoxLayout(quick_start_widget)
        quick_start_layout.setSpacing(16)
        
        # 步驟列表
        steps = [
            "1. 從左側導航欄選擇需要使用的工具",
            "2. 在工具界面中輸入或選擇要處理的檔案",
            "3. 配置工具參數和選項", 
            "4. 執行操作並查看結果",
            "5. 將結果保存或分享到其他工具"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("""
                color: #cccccc;
                font-size: 14px;
                padding: 8px 16px;
                background-color: #2d2d2d;
                border-radius: 4px;
                margin-bottom: 4px;
            """)
            quick_start_layout.addWidget(step_label)
        
        # 操作按鈕
        button_layout = QHBoxLayout()
        
        tutorial_button = QPushButton("📖 查看教學")
        tutorial_button.clicked.connect(self.tutorial_requested.emit)
        tutorial_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        button_layout.addWidget(tutorial_button)
        button_layout.addStretch()
        
        quick_start_layout.addLayout(button_layout)
        
        layout.addWidget(quick_start_widget)
    
    def setup_tools_showcase(self, layout):
        """設置工具展示區域"""
        # 區域標題
        section_title = QLabel("整合工具")
        section_title.setFont(QFont("", 20, QFont.Bold))
        section_title.setStyleSheet("color: #ffffff; margin-bottom: 16px;")
        layout.addWidget(section_title)
        
        # 工具卡片網格
        tools_widget = QWidget()
        tools_grid = QGridLayout(tools_widget)
        tools_grid.setSpacing(20)
        
        # 定義工具列表
        tools = [
            ("🔍", "檔案搜尋 (fd)", "高速檔案和目錄搜尋工具，支援正則表達式和多種過濾選項。", "fd"),
            ("🔎", "文本搜尋 (ripgrep)", "超高速文本搜尋工具，支援正則表達式和多種檔案格式。", "ripgrep"),
            ("📖", "Markdown 閱讀器 (glow)", "美觀的 Markdown 檔案預覽工具，支援多種主題樣式。", "glow"),
            ("🔄", "文檔轉換 (pandoc)", "萬能文檔轉換工具，支援 50+ 種格式互轉。", "pandoc"),
            ("🌈", "語法高亮查看器 (bat)", "檔案內容查看工具，支援語法高亮和 Git 集成。", "bat"),
            ("💾", "磁碟空間分析 (dust)", "快速磁碟使用量分析工具，提供直觀的樹狀視圖。", "dust"),
            ("📈", "系統監控 (glances)", "實時系統監控工具，提供詳細的性能指標。", "glances"),
            ("📊", "CSV 數據處理 (csvkit)", "強大的 CSV 數據處理工具集，支援格式轉換和數據分析。", "csvkit"),
            ("📄", "PDF 處理 (poppler)", "PDF 檔案處理工具集，支援轉換、分割、合併等操作。", "poppler")
        ]
        
        for i, (icon, name, description, tool_id) in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_card = self.create_tool_card(icon, name, description, tool_id)
            tools_grid.addWidget(tool_card, row, col)
        
        layout.addWidget(tools_widget)
    
    def create_tool_card(self, icon: str, name: str, description: str, tool_id: str) -> QFrame:
        """創建工具卡片"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(16, 16, 16, 16)
        
        # 圖示和名稱
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("", 24))
        header_layout.addWidget(icon_label)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("", 14, QFont.Bold))
        name_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #cccccc; font-size: 13px; line-height: 1.4;")
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # 快速啟動按鈕
        launch_button = QPushButton("啟動工具")
        launch_button.clicked.connect(lambda: self.tool_quick_access.emit(tool_id))
        launch_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #666666;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0078d4;
                border-color: #0078d4;
            }
        """)
        card_layout.addWidget(launch_button)
        
        # 設置卡片樣式
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 8px;
                min-height: 140px;
                max-height: 140px;
            }
            
            QFrame:hover {
                background-color: #3d3d3d;
                border-color: #666666;
            }
        """)
        
        return card
    
    def setup_animations(self):
        """設置動畫效果"""
        # 這裡可以添加頁面載入動畫
        pass
    
    def setup_styles(self):
        """設置樣式"""
        self.setStyleSheet("""
            ToolWelcomePage {
                background-color: #1e1e1e;
            }
            
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background-color: #3d3d3d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
```

## 🎯 實際應用範例

### 完整的分頁式工具整合應用

```python
# complete_tabbed_tool_app.py - 完整的分頁式工具整合應用
import sys
import logging
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TabbedToolIntegrationApp:
    """完整的分頁式工具整合應用"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        
    def initialize_application(self):
        """初始化應用程式"""
        try:
            # 創建 QApplication
            self.app = QApplication(sys.argv)
            
            # 設置應用程式屬性
            self.app.setApplicationName("分頁式工具整合平台")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Tool Integration Corp")
            
            # 設置應用程式圖示
            # self.app.setWindowIcon(QIcon("icon.png"))
            
            # 設置樣式
            self.app.setStyle(QStyleFactory.create('Fusion'))
            
            # 啟用高 DPI 支援
            self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing application: {e}")
            raise
    
    def create_main_window(self):
        """創建主視窗"""
        try:
            self.main_window = ToolIntegrationMainWindow()
            
            # 連接應用級信號
            self.main_window.tool_changed.connect(self.on_tool_changed)
            self.main_window.tool_error.connect(self.on_tool_error)
            
            # 顯示主視窗
            self.main_window.show()
            
            # 延遲顯示啟動完成訊息
            QTimer.singleShot(1000, self.show_startup_complete)
            
            logger.info("Main window created and displayed")
            
        except Exception as e:
            logger.error(f"Error creating main window: {e}")
            raise
    
    def show_startup_complete(self):
        """顯示啟動完成訊息"""
        if self.main_window:
            tool_count = len(self.main_window.get_tool_list())
            self.main_window.status_manager.set_status(
                f"應用啟動完成 - 已載入 {tool_count} 個工具", "success"
            )
    
    def on_tool_changed(self, tool_id: str):
        """處理工具切換"""
        logger.info(f"Tool changed to: {tool_id}")
    
    def on_tool_error(self, tool_id: str, error_message: str):
        """處理工具錯誤"""
        logger.error(f"Tool error [{tool_id}]: {error_message}")
    
    def run(self):
        """運行應用程式"""
        try:
            # 初始化應用程式
            self.initialize_application()
            
            # 創建主視窗
            self.create_main_window()
            
            # 運行主循環
            return self.app.exec_()
            
        except Exception as e:
            logger.error(f"Error running application: {e}")
            return 1

def main():
    """主函數"""
    app = TabbedToolIntegrationApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
```

## 📋 實施檢查清單

### 規劃階段
- [ ] 定義工具整合需求和目標用戶
- [ ] 設計統一的界面規範和用戶體驗
- [ ] 規劃工具插件架構和接口
- [ ] 確定技術選型和開發框架

### 架構設計階段
- [ ] 實現主視窗和導航系統
- [ ] 建立工具視圖基類和通用接口
- [ ] 設計插件管理和載入機制
- [ ] 實現配置管理和狀態系統

### 工具整合階段
- [ ] 開發各個工具的視圖組件
- [ ] 實現工具間的數據傳遞機制
- [ ] 整合主題系統和動畫效果
- [ ] 添加錯誤處理和用戶反饋

### 測試優化階段
- [ ] 測試所有工具的載入和切換
- [ ] 驗證界面響應性和性能
- [ ] 檢查錯誤處理和邊界情況
- [ ] 優化用戶體驗和操作流程

## 🚀 最佳實踐建議

### 1. 架構設計原則
- **單一責任**：每個組件專注於特定功能
- **鬆散耦合**：減少組件間的依賴關係
- **高內聚**：相關功能聚集在同一模組
- **可擴展性**：支援新工具的動態添加

### 2. 界面設計原則
- **一致性**：所有工具遵循統一設計規範
- **直觀性**：操作流程清晰易懂
- **效率性**：支援快捷鍵和批次操作
- **包容性**：考慮不同用戶的使用習慣

### 3. 性能優化建議
- **延遲載入**：工具按需載入以提升啟動速度
- **記憶體管理**：及時清理不用的資源
- **快取策略**：合理使用快取提升響應速度
- **非同步處理**：避免阻塞 UI 主線程

## 🎉 總結

分頁式工具整合界面是現代應用開發的重要模式，通過本指南提供的完整技術方案，您可以：

### 核心收獲
1. **掌握整合架構設計**：從主視窗到工具視圖的完整架構
2. **學會模組化開發**：可重用的組件和統一的接口設計
3. **實現專業級 UI**：現代化的界面設計和用戶體驗
4. **獲得可擴展框架**：支援新工具動態載入的靈活架構

### 實踐價值
- **提升開發效率**：統一的開發框架減少重複工作
- **改善用戶體驗**：專業的界面設計提升工具易用性
- **降低維護成本**：模組化架構便於後續維護和擴展
- **增強產品競爭力**：現代化的工具整合提升產品價值

分頁式工具整合界面不僅是技術實現，更是用戶體驗設計的體現。通過合理的架構設計和精心的界面規劃，您的應用將能夠為用戶提供高效、專業的工具使用體驗。

---

**作者**: Claude Code SuperClaude  
**版本**: 1.0  
**最後更新**: 2025-08-18  
**適用於**: PyQt5 5.15+, Python 3.7+  
**依賴**: 無額外依賴，僅使用 PyQt5 原生功能