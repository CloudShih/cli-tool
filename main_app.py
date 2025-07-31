import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from config.config_manager import config_manager
from ui.main_window import ModernMainWindow

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函數 - 應用程式入口點"""
    app = QApplication(sys.argv)
    
    # Set application icon using config manager
    try:
        icon_path = config_manager.get_resource_path("static/favicon/android-chrome-512x512.png")
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        else:
            logger.warning(f"Icon file not found at {icon_path}")
    except Exception as e:
        logger.warning(f"Could not set application icon: {e}")
    
    # 創建並顯示現代化主應用程式
    try:
        main_window = ModernMainWindow()
        main_window.show()
        logger.info("Main window created and shown successfully")
    except Exception as e:
        logger.error(f"Error creating main window: {e}")
        return 1
    
    # 運行應用程式事件循環
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())