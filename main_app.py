import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QMessageBox, QMenuBar, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from config.config_manager import config_manager
from core.plugin_manager import plugin_manager
from ui.theme_manager import theme_manager
from ui.theme_selector import ThemeSelector
from ui.component_showcase import ComponentShowcase

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CLIToolApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLI Tool Integration")
        
        # 從配置讀取窗口設置
        ui_config = config_manager.get_ui_config()
        window_config = ui_config.get('window', {})
        
        self.setGeometry(
            window_config.get('x', 100),
            window_config.get('y', 100),
            window_config.get('width', 800),
            window_config.get('height', 600)
        )
        
        self.initUI()
        self.load_plugins()
        self.apply_theme()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 創建選單欄
        self.create_menu()
        
        # 主要標籤頁
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.setLayout(main_layout)
    
    def create_menu(self):
        """創建應用程式選單"""
        # 注意：QWidget 不直接支援選單欄，所以我們創建一個假的選單按鈕
        # 在完整的 QMainWindow 重構中會有真正的選單欄
        pass

    def load_plugins(self):
        """載入和初始化插件"""
        try:
            logger.info("Loading plugins...")
            plugin_manager.initialize()
            
            # 獲取所有插件視圖並添加到標籤頁
            plugin_views = plugin_manager.get_plugin_views()
            
            for plugin_name, view in plugin_views.items():
                plugin = plugin_manager.get_plugin(plugin_name)
                if plugin:
                    tab_title = f"{plugin.name.title()} - {plugin.description.split(' ')[0]}"
                    self.tabs.addTab(view, tab_title)
                    logger.info(f"Added plugin tab: {tab_title}")
            
            if not plugin_views:
                self.show_no_plugins_message()
            else:
                # 添加主題選擇器標籤頁
                self.add_theme_selector_tab()
                
                # 添加組件展示標籤頁
                self.add_component_showcase_tab()
                
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")
            self.show_plugin_error(str(e))
    
    def add_theme_selector_tab(self):
        """添加主題選擇器標籤頁"""
        try:
            theme_selector = ThemeSelector()
            theme_selector.theme_changed.connect(self.on_theme_changed)
            self.tabs.addTab(theme_selector, "🎨 主題設定")
            logger.info("Added theme selector tab")
        except Exception as e:
            logger.error(f"Error adding theme selector tab: {e}")
    
    def add_component_showcase_tab(self):
        """添加組件展示標籤頁"""
        try:
            showcase = ComponentShowcase()
            self.tabs.addTab(showcase, "🧩 UI 組件")
            logger.info("Added component showcase tab")
        except Exception as e:
            logger.error(f"Error adding component showcase tab: {e}")
    
    def apply_theme(self):
        """套用當前配置的主題"""
        try:
            theme_manager.apply_current_theme()
            logger.info("Applied current theme from configuration")
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
    
    def on_theme_changed(self, theme_name: str):
        """處理主題變更事件"""
        logger.info(f"Theme changed to: {theme_name}")
        # 主題已經由 theme_manager 處理，這裡可以添加額外的處理邏輯

    def show_no_plugins_message(self):
        """顯示無插件可用的訊息"""
        msg = QMessageBox(self)
        msg.setWindowTitle("無可用插件")
        msg.setText("沒有找到可用的插件。請檢查：\n"
                   "1. 所需的命令行工具是否已安裝\n"
                   "2. 插件配置是否正確")
        msg.setIcon(QMessageBox.Warning)
        
        # 延遲顯示，確保主窗口已經顯示
        QTimer.singleShot(500, msg.exec_)

    def show_plugin_error(self, error_message: str):
        """顯示插件載入錯誤"""
        msg = QMessageBox(self)
        msg.setWindowTitle("插件載入錯誤")
        msg.setText(f"載入插件時發生錯誤：\n{error_message}")
        msg.setIcon(QMessageBox.Critical)
        
        # 延遲顯示，確保主窗口已經顯示
        QTimer.singleShot(500, msg.exec_)

    def closeEvent(self, event):
        """窗口關閉事件處理"""
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

def main():
    """主函數 - 應用程式入口點"""
    app = QApplication(sys.argv)
    
    # Set application icon using config manager
    try:
        icon_path = config_manager.get_resource_path("static/favicon/android-chrome-512x512.png")
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        else:
            print(f"Warning: Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Warning: Could not set application icon: {e}")
    
    # 創建並顯示主應用程式
    ex = CLIToolApp()
    ex.show()
    
    # 運行應用程式事件循環
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())