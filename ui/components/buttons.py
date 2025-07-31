"""
現代化按鈕組件 - 提供統一的按鈕樣式和行為
支援主要操作、危險操作、圖標按鈕等多種變體
"""

from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont, QPalette
import logging

logger = logging.getLogger(__name__)


class ModernButton(QPushButton):
    """現代化基礎按鈕 - 支援動畫效果和主題適應"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.is_processing = False
        self.original_text = text
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """設置基礎 UI 樣式"""
        self.setMinimumHeight(36)
        self.setMinimumWidth(100)
        self.setCursor(Qt.PointingHandCursor)
        
        # 設置字體
        font = QFont()
        font.setPointSize(10)
        font.setWeight(QFont.Normal)
        self.setFont(font)
        
        # 基礎樣式將由主題系統控制
        self.setProperty("modern_button", True)
    
    def setup_animations(self):
        """設置動畫效果"""
        # 這裡可以添加動畫效果，目前保持簡單
        pass
    
    def set_processing(self, processing: bool, text: str = "處理中..."):
        """設置處理狀態"""
        self.is_processing = processing
        if processing:
            self.setText(text)
            self.setEnabled(False)
        else:
            self.setText(self.original_text)
            self.setEnabled(True)
    
    def set_loading(self, loading: bool):
        """設置載入狀態"""
        if loading:
            self.set_processing(True, "載入中...")
        else:
            self.set_processing(False)


class PrimaryButton(ModernButton):
    """主要操作按鈕 - 用於主要的 CTA (Call to Action)"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setProperty("primary", True)
        self.setObjectName("primary_button")
    
    def setup_ui(self):
        """設置主要按鈕樣式"""
        super().setup_ui()
        
        # 設置字體為粗體
        font = self.font()
        font.setWeight(QFont.DemiBold)
        self.setFont(font)


class DangerButton(ModernButton):
    """危險操作按鈕 - 用於刪除、清除等危險操作"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setProperty("danger", True)
        self.setObjectName("danger_button")


class IconButton(ModernButton):
    """圖標按鈕 - 支援圖標和文字的組合"""
    
    def __init__(self, text="", icon=None, icon_size=16, parent=None):
        super().__init__(text, parent)
        self.icon_size = icon_size
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(Qt.QSize(icon_size, icon_size))
        
        self.setProperty("icon_button", True)
    
    def set_loading_icon(self, loading: bool):
        """設置載入圖標"""
        if loading:
            # 這裡可以設置一個旋轉的載入圖標
            self.setEnabled(False)
        else:
            self.setEnabled(True)


class ButtonGroup(QWidget):
    """按鈕群組 - 用於組織相關按鈕"""
    
    def __init__(self, buttons=None, layout_direction="horizontal", parent=None):
        super().__init__(parent)
        self.buttons = buttons or []
        self.layout_direction = layout_direction
        self.setup_ui()
    
    def setup_ui(self):
        """設置按鈕群組佈局"""
        if self.layout_direction == "horizontal":
            layout = QHBoxLayout()
        else:
            from PyQt5.QtWidgets import QVBoxLayout
            layout = QVBoxLayout()
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        for button in self.buttons:
            layout.addWidget(button)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_button(self, button: ModernButton):
        """添加按鈕到群組"""
        self.buttons.append(button)
        self.layout().insertWidget(len(self.buttons) - 1, button)
    
    def set_all_enabled(self, enabled: bool):
        """設置所有按鈕的啟用狀態"""
        for button in self.buttons:
            button.setEnabled(enabled)


class ActionButton(ModernButton):
    """動作按鈕 - 用於執行特定動作的按鈕"""
    
    action_completed = pyqtSignal(bool)  # 動作完成信號
    
    def __init__(self, text="", action_text="執行中...", parent=None):
        super().__init__(text, parent)
        self.action_text = action_text
        self.is_action_running = False
        
    def execute_action(self, action_func, *args, **kwargs):
        """執行動作"""
        if self.is_action_running:
            return
        
        self.is_action_running = True
        self.set_processing(True, self.action_text)
        
        try:
            # 這裡應該在另一個線程中執行實際動作
            # 目前使用 QTimer 模擬異步操作
            QTimer.singleShot(100, lambda: self._complete_action(True))
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            self._complete_action(False)
    
    def _complete_action(self, success: bool):
        """完成動作"""
        self.is_action_running = False
        self.set_processing(False)
        self.action_completed.emit(success)


class FileButton(IconButton):
    """檔案操作按鈕 - 用於檔案選擇等操作"""
    
    file_selected = pyqtSignal(str)  # 檔案選擇信號
    
    def __init__(self, text="瀏覽...", file_filter="所有檔案 (*)", parent=None):
        super().__init__(text, parent=parent)
        self.file_filter = file_filter
        self.clicked.connect(self.open_file_dialog)
    
    def open_file_dialog(self):
        """開啟檔案對話框"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇檔案",
            "",
            self.file_filter
        )
        
        if file_path:
            self.file_selected.emit(file_path)
            logger.info(f"File selected: {file_path}")


class DirectoryButton(IconButton):
    """目錄選擇按鈕"""
    
    directory_selected = pyqtSignal(str)  # 目錄選擇信號
    
    def __init__(self, text="瀏覽目錄...", parent=None):
        super().__init__(text, parent=parent)
        self.clicked.connect(self.open_directory_dialog)
    
    def open_directory_dialog(self):
        """開啟目錄對話框"""
        from PyQt5.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "選擇目錄",
            ""
        )
        
        if directory:
            self.directory_selected.emit(directory)
            logger.info(f"Directory selected: {directory}")


# 便利函數
def create_button_group(*buttons, direction="horizontal"):
    """創建按鈕群組的便利函數"""
    return ButtonGroup(list(buttons), direction)


def create_action_buttons(actions: dict):
    """根據動作字典創建按鈕群組
    
    Args:
        actions: {"按鈕文字": callback_function, ...}
    """
    buttons = []
    for text, callback in actions.items():
        button = ModernButton(text)
        button.clicked.connect(callback)
        buttons.append(button)
    
    return ButtonGroup(buttons)