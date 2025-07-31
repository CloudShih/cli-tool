"""
現代化主窗口設計
包含側邊欄、狀態欄、歡迎頁面的主窗口實現
"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStackedWidget, QFrame, QLabel, QScrollArea, QSizePolicy,
    QStatusBar, QAction, QMenuBar, QMenu, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QLinearGradient, QPalette
from ui.components.buttons import ModernButton, PrimaryButton, IconButton
from ui.components.indicators import StatusIndicator, LoadingSpinner
from ui.components.progress_toast import ToastManager, show_progress_toast
from ui.plugin_loader import PluginLoadingDialog
from ui.responsive_layout import ResponsiveLayoutManager, get_screen_info
from ui.animation_effects import animation_manager, animate_widget, AnimatedButton
from config.config_manager import config_manager
from core.plugin_manager import plugin_manager
from ui.theme_manager import theme_manager

logger = logging.getLogger(__name__)


class WelcomePage(QWidget):
    """歡迎頁面組件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """設置歡迎頁面 UI"""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # 標題區域
        title_label = QLabel("CLI Tool Integration")
        title_label.setProperty("welcome-title", True)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 副標題
        subtitle_label = QLabel("整合多種命令列工具的現代化圖形界面")
        subtitle_label.setProperty("welcome-subtitle", True)
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(40)
        
        # 功能介紹卡片
        features_layout = QHBoxLayout()
        features_layout.setSpacing(20)
        
        # fd 工具卡片
        fd_card = self.create_feature_card(
            "🔍", "檔案搜尋", 
            "使用 fd 工具快速搜尋檔案和目錄，支援正則表達式和各種篩選選項。"
        )
        features_layout.addWidget(fd_card)
        
        # Poppler 工具卡片
        poppler_card = self.create_feature_card(
            "📄", "PDF 處理", 
            "使用 Poppler 工具集處理 PDF 文件，包括轉換、分割、合併等功能。"
        )
        features_layout.addWidget(poppler_card)
        
        # 主題設定卡片
        theme_card = self.create_feature_card(
            "🎨", "主題設定", 
            "豐富的主題選擇，支援深色、淺色和系統主題自動切換。"
        )
        features_layout.addWidget(theme_card)
        
        main_layout.addLayout(features_layout)
        
        main_layout.addStretch()
        
        # 底部信息
        info_label = QLabel("請從左側導航選擇要使用的工具")
        info_label.setProperty("welcome-info", True)
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        self.setLayout(main_layout)
    
    def create_feature_card(self, icon: str, title: str, description: str) -> QFrame:
        """創建功能介紹卡片"""
        card = QFrame()
        card.setProperty("feature-card", True)
        card.setFrameStyle(QFrame.StyledPanel)
        card.setFixedSize(250, 180)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # 圖標
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setProperty("feature-icon", True)
        layout.addWidget(icon_label)
        
        # 標題
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("feature-title", True)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setProperty("feature-description", True)
        layout.addWidget(desc_label)
        
        card.setLayout(layout)
        return card


class NavigationSidebar(QFrame):
    """側邊欄導航組件"""
    
    navigation_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_selection = "welcome"
        self.navigation_buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """設置側邊欄 UI"""
        self.setProperty("sidebar", True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedWidth(200)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 20)
        main_layout.setSpacing(5)
        
        # 應用標題
        app_title = QLabel("CLI Tools")
        app_title.setProperty("sidebar-title", True)
        app_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(app_title)
        
        main_layout.addSpacing(20)
        
        # 導航項目
        self.add_navigation_item(main_layout, "welcome", "🏠", "歡迎頁面", True)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setProperty("sidebar-separator", True)
        main_layout.addWidget(separator)
        
        # 工具區域標題
        tools_label = QLabel("工具")
        tools_label.setProperty("sidebar-section", True)
        main_layout.addWidget(tools_label)
        
        # 載入插件導航項
        self.load_plugin_navigation(main_layout)
        
        # 分隔線
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setProperty("sidebar-separator", True)
        main_layout.addWidget(separator2)
        
        # 設定區域
        settings_label = QLabel("設定")
        settings_label.setProperty("sidebar-section", True)
        main_layout.addWidget(settings_label)
        
        self.add_navigation_item(main_layout, "themes", "🎨", "主題設定")
        self.add_navigation_item(main_layout, "components", "🧩", "UI 組件")
        
        main_layout.addStretch()
        
        # 狀態指示器
        self.sidebar_status = StatusIndicator("ready")
        main_layout.addWidget(self.sidebar_status)
        
        self.setLayout(main_layout)
    
    def add_navigation_item(self, layout: QVBoxLayout, key: str, icon: str, text: str, selected: bool = False):
        """添加導航項目"""
        # 使用動畫按鈕
        button = AnimatedButton(f"{icon} {text}")
        button.setProperty("sidebar-nav", True)
        button.setCheckable(True)
        button.setChecked(selected)
        button.clicked.connect(lambda: self.on_navigation_clicked(key))
        
        # 添加入場動畫
        QTimer.singleShot(len(self.navigation_buttons) * 50, 
                         lambda: animate_widget(button, 'slide_in', direction='left', duration=300))
        
        self.navigation_buttons[key] = button
        layout.addWidget(button)
    
    def load_plugin_navigation(self, main_layout):
        """載入插件導航項目"""
        try:
            plugins = plugin_manager.get_available_plugins()
            
            # 找到工具區域的插入位置（在分隔線後）
            tools_index = -1
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QLabel) and widget.text() == "工具":
                        tools_index = i
                        break
            
            if tools_index == -1:
                return
            
            # 移除舊的插件按鈕（如果有的話）
            plugins_to_remove = []
            for plugin_name in self.navigation_buttons:
                if plugin_name not in ["welcome", "themes", "components"]:
                    plugins_to_remove.append(plugin_name)
            
            for plugin_name in plugins_to_remove:
                if plugin_name in self.navigation_buttons:
                    button = self.navigation_buttons[plugin_name]
                    main_layout.removeWidget(button)
                    button.deleteLater()
                    del self.navigation_buttons[plugin_name]
            
            # 添加新的插件導航項目
            insert_index = tools_index + 1
            for plugin_name, plugin in plugins.items():
                icon = "🔧"  # 預設圖標
                if plugin_name == "fd":
                    icon = "🔍"
                elif plugin_name == "poppler":
                    icon = "📄"
                
                button = ModernButton(f"{icon} {plugin.name.title()}")
                button.setProperty("sidebar-nav", True)
                button.setCheckable(True)
                button.clicked.connect(lambda checked, key=plugin_name: self.on_navigation_clicked(key))
                
                self.navigation_buttons[plugin_name] = button
                main_layout.insertWidget(insert_index, button)
                insert_index += 1
                
                logger.info(f"Added navigation item for plugin: {plugin_name}")
                
        except Exception as e:
            logger.error(f"Error loading plugin navigation: {e}")
    
    def refresh_plugin_navigation(self):
        """刷新插件導航"""
        self.load_plugin_navigation(self.layout())
    
    def on_navigation_clicked(self, key: str):
        """處理導航點擊事件"""
        if key != self.current_selection:
            # 更新按鈕狀態
            for nav_key, button in self.navigation_buttons.items():
                button.setChecked(nav_key == key)
            
            self.current_selection = key
            self.navigation_changed.emit(key)
            logger.info(f"Navigation changed to: {key}")
    
    def set_status(self, status: str, message: str = ""):
        """設置側邊欄狀態"""
        self.sidebar_status.set_status(status, message)


class ModernMainWindow(QMainWindow):
    """現代化主窗口"""
    
    def __init__(self):
        super().__init__()
        self.plugin_views = {}
        self.current_view = None
        self.toast_manager = None
        self.responsive_manager = None
        self.setup_ui()
        self.setup_toast_manager()
        self.setup_responsive_layout()
        self.setup_animations()
        self.load_plugins()
        self.apply_theme()
        self.restore_window_state()
    
    def setup_ui(self):
        """設置主窗口 UI"""
        self.setWindowTitle("CLI Tool Integration")
        self.setMinimumSize(900, 650)
        
        # 創建中央區域
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平分割
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 側邊欄
        self.sidebar = NavigationSidebar()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        main_layout.addWidget(self.sidebar)
        
        # 主內容區域
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)
        
        central_widget.setLayout(main_layout)
        
        # 創建選單欄
        self.create_menu_bar()
        
        # 創建狀態欄
        self.create_status_bar()
        
        # 添加歡迎頁面
        self.welcome_page = WelcomePage()
        self.content_stack.addWidget(self.welcome_page)
    
    def setup_toast_manager(self):
        """設置吐司通知管理器"""
        self.toast_manager = ToastManager(self)
    
    def setup_responsive_layout(self):
        """設置響應式佈局"""
        try:
            self.responsive_manager = ResponsiveLayoutManager(self)
            
            # 記錄螢幕資訊
            screen_info = get_screen_info()
            logger.info(f"Screen info: {screen_info}")
            
            # 根據螢幕尺寸調整初始窗口大小
            if screen_info:
                available_width = screen_info.get('available_width', 1200)
                available_height = screen_info.get('available_height', 800)
                
                # 設置合適的初始大小（螢幕的80%）
                initial_width = min(1200, int(available_width * 0.8))
                initial_height = min(800, int(available_height * 0.8))
                
                self.setMinimumSize(800, 600)  # 設置最小尺寸
                self.resize(initial_width, initial_height)
            
        except Exception as e:
            logger.error(f"Error setting up responsive layout: {e}")
    
    def setup_animations(self):
        """設置動畫系統"""
        try:
            # 啟用動畫並設置速度
            animation_manager.set_animations_enabled(True)
            animation_manager.set_speed_factor(1.0)
            
            # 為主窗口元素添加入場動畫
            QTimer.singleShot(100, self.animate_window_entrance)
            
        except Exception as e:
            logger.error(f"Error setting up animations: {e}")
    
    def animate_window_entrance(self):
        """主窗口入場動畫"""
        try:
            # 側邊欄滑入動畫
            if hasattr(self, 'sidebar'):
                animate_widget(self.sidebar, 'slide_in', direction='left', duration=400)
            
            # 歡迎頁面淡入動畫
            if hasattr(self, 'welcome_page'):
                animate_widget(self.welcome_page, 'fade_in', duration=600)
            
        except Exception as e:
            logger.error(f"Error in window entrance animation: {e}")
    
    def create_menu_bar(self):
        """創建選單欄"""
        menubar = self.menuBar()
        
        # 檔案選單
        file_menu = menubar.addMenu('檔案(&F)')
        
        # 設定動作
        settings_action = QAction('設定(&S)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 退出動作
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 檢視選單
        view_menu = menubar.addMenu('檢視(&V)')
        
        # 重新整理動作
        refresh_action = QAction('重新整理(&R)', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_plugins)
        view_menu.addAction(refresh_action)
        
        # 說明選單
        help_menu = menubar.addMenu('說明(&H)')
        
        # 關於動作
        about_action = QAction('關於(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """創建狀態欄"""
        self.status_bar = self.statusBar()
        
        # 主狀態訊息
        self.status_label = QLabel("準備就緒")
        self.status_bar.addWidget(self.status_label, 1)
        
        # 載入指示器
        self.status_spinner = LoadingSpinner(16)
        self.status_bar.addPermanentWidget(self.status_spinner)
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready")
        self.status_bar.addPermanentWidget(self.status_indicator)
        
        self.set_status("準備就緒", "ready")
    
    def load_plugins(self):
        """載入插件 - 使用進度對話框"""
        try:
            self.set_status("準備載入插件...", "processing")
            
            # 創建並顯示插件載入對話框
            loading_dialog = PluginLoadingDialog(plugin_manager, self)
            loading_dialog.loading_completed.connect(self.on_plugins_loaded)
            
            # 異步啟動載入
            QTimer.singleShot(100, loading_dialog.start_loading)
            
        except Exception as e:
            logger.error(f"Error starting plugin loading: {e}")
            self.set_status(f"插件載入失敗: {str(e)}", "error")
            self.show_plugin_error(str(e))
    
    def on_plugins_loaded(self, success: bool, message: str):
        """處理插件載入完成"""
        try:
            if success:
                # 獲取所有插件視圖並添加到主窗口
                plugin_views = plugin_manager.get_plugin_views()
                
                for plugin_name, view in plugin_views.items():
                    self.plugin_views[plugin_name] = view
                    self.content_stack.addWidget(view)
                    logger.info(f"Added plugin view: {plugin_name}")
                
                # 添加主題選擇器和組件展示
                self.add_special_views()
                
                # 更新側邊欄導航
                self.sidebar.refresh_plugin_navigation()
                
                self.set_status(f"插件載入完成 - {message}", "success")
                logger.info(f"Successfully loaded {len(plugin_views)} plugins")
            else:
                self.set_status(f"插件載入失敗 - {message}", "error")
                # 仍然添加特殊視圖，即使插件載入失敗
                self.add_special_views()
                
        except Exception as e:
            logger.error(f"Error processing loaded plugins: {e}")
            self.set_status(f"插件處理失敗: {str(e)}", "error")
    
    def add_special_views(self):
        """添加特殊視圖（主題選擇器、組件展示）"""
        try:
            # 主題選擇器
            from ui.theme_selector import ThemeSelector
            theme_selector = ThemeSelector()
            theme_selector.theme_changed.connect(self.on_theme_changed)
            self.plugin_views["themes"] = theme_selector
            self.content_stack.addWidget(theme_selector)
            
            # 組件展示
            from ui.component_showcase import ComponentShowcase
            showcase = ComponentShowcase()
            self.plugin_views["components"] = showcase
            self.content_stack.addWidget(showcase)
            
            logger.info("Added special views (themes, components)")
            
        except Exception as e:
            logger.error(f"Error adding special views: {e}")
    
    def on_navigation_changed(self, key: str):
        """處理導航變更"""
        try:
            logger.info(f"Navigation changed to: {key}")
            
            # 顯示切換反饋
            self.show_navigation_toast(key)
            
            if key == "welcome":
                self.content_stack.setCurrentWidget(self.welcome_page)
                self.set_status("歡迎使用 CLI Tool Integration", "ready")
            elif key in self.plugin_views:
                view = self.plugin_views[key]
                self.content_stack.setCurrentWidget(view)
                
                # 更新狀態欄訊息
                if hasattr(view, 'windowTitle') and callable(getattr(view, 'windowTitle', None)):
                    title = view.windowTitle()
                    if title:
                        self.set_status(f"當前工具: {title}", "ready")
                    else:
                        self.set_status(f"當前工具: {key.title()}", "ready")
                else:
                    self.set_status(f"當前工具: {key.title()}", "ready")
            else:
                logger.warning(f"Unknown navigation key: {key}")
                self.set_status(f"未知頁面: {key}", "warning")
                
        except Exception as e:
            logger.error(f"Error changing navigation: {e}")
            self.set_status(f"導航錯誤: {str(e)}", "error")
    
    def show_navigation_toast(self, key: str):
        """顯示導航切換吐司通知"""
        try:
            page_names = {
                "welcome": "歡迎頁面",
                "fd": "檔案搜尋",
                "poppler": "PDF 處理",
                "themes": "主題設定",
                "components": "UI 組件"
            }
            
            page_name = page_names.get(key, key.title())
            icon = "🏠" if key == "welcome" else "🔍" if key == "fd" else "📄" if key == "poppler" else "🎨" if key == "themes" else "🧩" if key == "components" else "🔧"
            
            if self.toast_manager:
                self.toast_manager.show_progress_toast(
                    f"{icon} {page_name}", 
                    "頁面切換中...", 
                    duration=1500
                )
        except Exception as e:
            logger.error(f"Error showing navigation toast: {e}")
            # 不阻塞導航功能，繼續執行
    
    def apply_theme(self):
        """套用主題"""
        try:
            theme_manager.apply_current_theme()
            logger.info("Applied current theme")
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
    
    def on_theme_changed(self, theme_name: str):
        """處理主題變更"""
        logger.info(f"Theme changed to: {theme_name}")
        self.set_status(f"主題已切換至: {theme_name}", "success")
        
        # 顯示主題切換吐司通知
        if self.toast_manager:
            self.toast_manager.show_progress_toast(
                f"🎨 主題已切換", 
                f"當前主題: {theme_name}", 
                duration=2000
            )
    
    def set_status(self, message: str, status: str = "ready"):
        """設置狀態欄訊息"""
        self.status_label.setText(message)
        self.status_indicator.set_status(status)
        
        if status == "processing":
            self.status_spinner.start_spinning()
        else:
            self.status_spinner.stop_spinning()
        
        # 更新側邊欄狀態
        self.sidebar.set_status(status, message)
    
    def show_settings(self):
        """顯示設定對話框"""
        # 切換到主題設定頁面
        self.sidebar.on_navigation_clicked("themes")
    
    def refresh_plugins(self):
        """重新整理插件"""
        try:
            self.set_status("重新整理插件中...", "processing")
            
            # 顯示重新整理吐司通知
            if self.toast_manager:
                self.toast_manager.show_progress_toast(
                    "🔄 重新整理插件", 
                    "正在重新載入插件...", 
                    duration=0  # 手動隱藏
                )
            
            # 清理現有插件
            plugin_manager.cleanup()
            
            # 重新載入
            self.load_plugins()
            
        except Exception as e:
            logger.error(f"Error refreshing plugins: {e}")
            self.set_status(f"重新整理失敗: {str(e)}", "error")
            
            # 顯示錯誤吐司通知
            if self.toast_manager:
                self.toast_manager.show_progress_toast(
                    "❌ 重新整理失敗", 
                    str(e), 
                    duration=3000
                )
    
    def show_about(self):
        """顯示關於對話框"""
        QMessageBox.about(
            self, 
            "關於 CLI Tool Integration",
            "CLI Tool Integration v1.0\n\n"
            "整合多種命令列工具的現代化圖形界面\n\n"
            "支援的工具:\n"
            "• fd - 快速檔案搜尋\n"
            "• Poppler - PDF 處理工具集\n\n"
            "© 2024 CLI Tool Integration"
        )
    
    def show_plugin_error(self, error_message: str):
        """顯示插件錯誤對話框"""
        QMessageBox.critical(
            self,
            "插件載入錯誤",
            f"載入插件時發生錯誤：\n{error_message}"
        )
    
    def restore_window_state(self):
        """恢復窗口狀態"""
        try:
            ui_config = config_manager.get_ui_config()
            window_config = ui_config.get('window', {})
            
            self.setGeometry(
                window_config.get('x', 100),
                window_config.get('y', 100),
                window_config.get('width', 1000),
                window_config.get('height', 700)
            )
            
        except Exception as e:
            logger.error(f"Error restoring window state: {e}")
    
    def closeEvent(self, event):
        """窗口關閉事件"""
        try:
            # 保存窗口狀態
            if config_manager.get('ui.remember_window_state', True):
                geometry = self.geometry()
                config_manager.set('ui.window.x', geometry.x())
                config_manager.set('ui.window.y', geometry.y())
                config_manager.set('ui.window.width', geometry.width())
                config_manager.set('ui.window.height', geometry.height())
                config_manager.save_config()
            
            # 清理插件資源
            plugin_manager.cleanup()
            logger.info("Application closed successfully")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
        
        event.accept()