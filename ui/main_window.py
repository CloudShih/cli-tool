"""
現代化主窗口設計
負責組合各個 UI 組件並提供高層控制邏輯
"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QAction, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from ui.components.progress_toast import ToastManager
from ui.responsive_layout import ResponsiveLayoutManager, get_screen_info
from ui.animation_effects import animation_manager, animate_widget
from config.config_manager import config_manager
from ui.theme_manager import theme_manager
from .welcome_page import WelcomePage
from .sidebar import NavigationSidebar
from .status_bar import StatusBarController
from .plugin_host import PluginHost

logger = logging.getLogger(__name__)


class ModernMainWindow(QMainWindow):
    """現代化主窗口"""

    def __init__(self):
        super().__init__()
        self.toast_manager = None
        self.responsive_manager = None
        self.content_stack = None
        self.sidebar = None
        self.welcome_page = None
        self.status_bar = None
        self.plugin_host = None
        self.setup_ui()
        self.setup_toast_manager()
        self.plugin_host = PluginHost(self)
        self.plugin_views = self.plugin_host.plugin_views
        self.setup_responsive_layout()
        self.setup_animations()
        self.plugin_host.load_plugins()
        self.apply_theme()
        self.restore_window_state()

    def setup_ui(self):
        """設置主窗口 UI"""
        self.setWindowTitle("CLI Tool Integration")
        self.setMinimumSize(900, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = NavigationSidebar()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        main_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        central_widget.setLayout(main_layout)

        self.create_menu_bar()
        self.status_bar = StatusBarController(self, self.sidebar)

        self.welcome_page = WelcomePage()
        self.content_stack.addWidget(self.welcome_page)

    def setup_toast_manager(self):
        """設置吐司通知管理器"""
        self.toast_manager = ToastManager(self)

    def setup_responsive_layout(self):
        """設置響應式佈局"""
        try:
            self.responsive_manager = ResponsiveLayoutManager(self)
            screen_info = get_screen_info()
            if screen_info:
                available_width = screen_info.get('available_width', 1200)
                available_height = screen_info.get('available_height', 800)
                initial_width = min(1600, int(available_width * 0.8))
                initial_height = min(1200, int(available_height * 0.8))
                self.setMinimumSize(1200, 900)
                self.resize(initial_width, initial_height)
        except Exception as e:
            logger.error(f"Error setting up responsive layout: {e}")

    def setup_animations(self):
        """設置動畫系統"""
        try:
            animation_manager.set_animations_enabled(True)
            animation_manager.set_speed_factor(1.0)
            QTimer.singleShot(100, self.animate_window_entrance)
        except Exception as e:
            logger.error(f"Error setting up animations: {e}")

    def animate_window_entrance(self):
        """主窗口入場動畫"""
        try:
            if hasattr(self, 'sidebar'):
                animate_widget(self.sidebar, 'slide_in', direction='left', duration=400)
            if hasattr(self, 'welcome_page'):
                animate_widget(self.welcome_page, 'fade_in', duration=600)
        except Exception as e:
            logger.error(f"Error in window entrance animation: {e}")

    def create_menu_bar(self):
        """創建選單欄"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu('檔案(&F)')
        settings_action = QAction('設定(&S)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        file_menu.addSeparator()
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('檢視(&V)')
        refresh_action = QAction('重新整理(&R)', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_plugins)
        view_menu.addAction(refresh_action)

        help_menu = menubar.addMenu('說明(&H)')
        about_action = QAction('關於(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_navigation_changed(self, key: str):
        """處理導航變更"""
        try:
            logger.info(f"Navigation changed to: {key}")
            self.show_navigation_toast(key)
            if key == "welcome":
                self.content_stack.setCurrentWidget(self.welcome_page)
                self.status_bar.set_status("歡迎使用 CLI Tool Integration", "ready")
            elif key in self.plugin_host.plugin_views:
                view = self.plugin_host.plugin_views[key]
                self.content_stack.setCurrentWidget(view)
                if hasattr(view, 'windowTitle') and callable(getattr(view, 'windowTitle', None)):
                    title = view.windowTitle()
                    if title:
                        self.status_bar.set_status(f"當前工具: {title}", "ready")
                    else:
                        self.status_bar.set_status(f"當前工具: {key.title()}", "ready")
                else:
                    self.status_bar.set_status(f"當前工具: {key.title()}", "ready")
            else:
                logger.warning(f"Unknown navigation key: {key}")
                self.status_bar.set_status(f"未知頁面: {key}", "warning")
        except Exception as e:
            logger.error(f"Error changing navigation: {e}")
            self.status_bar.set_status(f"導航錯誤: {str(e)}", "error")

    def show_navigation_toast(self, key: str):
        """顯示導航切換吐司通知"""
        try:
            page_names = {
                "welcome": "歡迎頁面",
                "fd": "檔案搜尋",
                "ripgrep": "文本搜尋",
                "poppler": "PDF 處理",
                "glow": "Markdown 閱讀器",
                "pandoc": "文檔轉換",
                "bat": "語法高亮查看器",
                "dust": "磁碟空間分析器",
                "csvkit": "CSV 數據處理",
                "themes": "主題設定",
                "components": "UI 組件"
            }
            page_name = page_names.get(key, key.title())
            icon_map = {
                "welcome": "🏠",
                "fd": "🔍",
                "ripgrep": "🔎",
                "poppler": "📄",
                "glow": "📖",
                "pandoc": "🔄",
                "bat": "🌈",
                "dust": "💾",
                "csvkit": "📊",
                "themes": "🎨",
                "components": "🧩"
            }
            icon = icon_map.get(key, "🔧")
            if self.toast_manager:
                self.toast_manager.show_progress_toast(
                    f"{icon} {page_name}",
                    "頁面切換中...",
                    duration=1500
                )
        except Exception as e:
            logger.error(f"Error showing navigation toast: {e}")

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
        self.status_bar.set_status(f"主題已切換至: {theme_name}", "success")
        if self.toast_manager:
            self.toast_manager.show_progress_toast(
                f"🎨 主題已切換",
                f"當前主題: {theme_name}",
                duration=2000
            )

    def show_settings(self):
        """顯示設定對話框"""
        self.sidebar.on_navigation_clicked("themes")

    def refresh_plugins(self):
        """重新整理插件"""
        self.plugin_host.refresh_plugins()

    def show_about(self):
        """顯示關於對話框"""
        QMessageBox.about(
            self,
            "關於 CLI Tool Integration",
            "CLI Tool Integration v1.0\n\n"
            "整合多種命令列工具的現代化圖形界面\n\n"
            "支援的工具:\n"
            "• fd - 快速檔案搜尋\n"
            "• Ripgrep - 高效能文本搜尋\n"
            "• Glow - Markdown 文檔預覽\n"
            "• Pandoc - 萬能文檔轉換器\n"
            "• Poppler - PDF 處理工具集\n"
            "• bat - 語法高亮查看器\n"
            "• dust - 磁碟空間分析器\n\n"
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
            if config_manager.get('ui.remember_window_state', True):
                geometry = self.geometry()
                config_manager.set('ui.window.x', geometry.x())
                config_manager.set('ui.window.y', geometry.y())
                config_manager.set('ui.window.width', geometry.width())
                config_manager.set('ui.window.height', geometry.height())
                config_manager.save_config()
            self.plugin_host.cleanup()
            logger.info("Application closed successfully")
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
        event.accept()
