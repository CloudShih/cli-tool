"""
現代化輸入組件 - 提供統一的輸入框樣式和驗證功能
支援文本輸入、多行文本、下拉選單等
"""

from PyQt5.QtWidgets import (
    QLineEdit, QTextEdit, QComboBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QValidator
import re
import logging

logger = logging.getLogger(__name__)


class ModernLineEdit(QLineEdit):
    """現代化單行輸入框 - 支援驗證和狀態指示"""
    
    validation_changed = pyqtSignal(bool)  # 驗證狀態變更信號
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.validation_pattern = None
        self.validation_message = ""
        self.is_valid = True
        self.required = False
        
        if placeholder:
            self.setPlaceholderText(placeholder)
        
        self.setup_ui()
        self.setup_validation()
    
    def setup_ui(self):
        """設置基礎 UI 樣式"""
        self.setMinimumHeight(36)
        
        # 設置字體
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
        # 樣式將由主題系統控制
        self.setProperty("modern_input", True)
    
    def setup_validation(self):
        """設置驗證機制"""
        self.textChanged.connect(self.validate_input)
        
        # 失焦時也進行驗證
        self.editingFinished.connect(self.validate_input)
    
    def set_validation_pattern(self, pattern: str, message: str = ""):
        """設置驗證模式"""
        self.validation_pattern = pattern
        self.validation_message = message
        self.validate_input()
    
    def set_required(self, required: bool, message: str = "此欄位為必填"):
        """設置必填狀態"""
        self.required = required
        if required and not self.validation_message:
            self.validation_message = message
    
    def validate_input(self):
        """驗證輸入內容"""
        text = self.text().strip()
        
        # 檢查必填
        if self.required and not text:
            self.set_validation_state(False, self.validation_message or "此欄位為必填")
            return
        
        # 檢查模式匹配
        if self.validation_pattern and text:
            if not re.match(self.validation_pattern, text):
                self.set_validation_state(False, self.validation_message or "格式不正確")
                return
        
        # 驗證通過
        self.set_validation_state(True, "")
    
    def set_validation_state(self, is_valid: bool, message: str = ""):
        """設置驗證狀態"""
        if self.is_valid != is_valid:
            self.is_valid = is_valid
            self.validation_changed.emit(is_valid)
            
            # 更新樣式
            if is_valid:
                self.setProperty("validation_state", "valid")
            else:
                self.setProperty("validation_state", "invalid")
            
            # 更新工具提示
            if message:
                self.setToolTip(message)
            else:
                self.setToolTip("")
            
            # 刷新樣式
            self.style().polish(self)
    
    def get_validation_state(self):
        """獲取驗證狀態"""
        return self.is_valid, self.validation_message
    
    def clear_validation(self):
        """清除驗證狀態"""
        self.validation_pattern = None
        self.validation_message = ""
        self.required = False
        self.set_validation_state(True, "")


class ModernTextEdit(QTextEdit):
    """現代化多行文本編輯器"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        
        if placeholder:
            self.setPlaceholderText(placeholder)
        
        self.setup_ui()
    
    def setup_ui(self):
        """設置基礎 UI 樣式"""
        self.setMinimumHeight(100)
        
        # 設置字體
        font = QFont("Consolas", 10)
        self.setFont(font)
        
        # 樣式將由主題系統控制
        self.setProperty("modern_text_edit", True)
        
        # 設置滾動條策略
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    
    def set_read_only_style(self, read_only: bool = True):
        """設置只讀樣式"""
        self.setReadOnly(read_only)
        if read_only:
            self.setProperty("read_only", True)
        else:
            self.setProperty("read_only", False)
        self.style().polish(self)


class ModernComboBox(QComboBox):
    """現代化下拉選單"""
    
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        
        if items:
            self.addItems(items)
        
        self.setup_ui()
    
    def setup_ui(self):
        """設置基礎 UI 樣式"""
        self.setMinimumHeight(36)
        self.setMinimumWidth(120)
        
        # 設置字體
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
        # 樣式將由主題系統控制
        self.setProperty("modern_combo", True)
    
    def add_items_with_data(self, items_data: dict):
        """添加帶數據的項目
        
        Args:
            items_data: {"顯示文字": 實際值, ...}
        """
        for text, data in items_data.items():
            self.addItem(text, data)
    
    def get_current_data(self):
        """獲取當前選中項的數據"""
        return self.currentData()
    
    def set_current_by_data(self, data):
        """根據數據設置當前選中項"""
        for i in range(self.count()):
            if self.itemData(i) == data:
                self.setCurrentIndex(i)
                break


class ValidatedInputGroup(QWidget):
    """驗證輸入群組 - 包含標籤和驗證反饋"""
    
    validation_changed = pyqtSignal(bool)  # 群組驗證狀態變更
    
    def __init__(self, label_text="", input_widget=None, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.input_widget = input_widget or ModernLineEdit()
        self.validation_label = None
        
        self.setup_ui()
        self.setup_validation()
    
    def setup_ui(self):
        """設置 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 標籤
        if self.label_text:
            label = QLabel(self.label_text)
            label.setProperty("input_label", True)
            layout.addWidget(label)
        
        # 輸入框
        layout.addWidget(self.input_widget)
        
        # 驗證反饋標籤
        self.validation_label = QLabel()
        self.validation_label.setProperty("validation_message", True)
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        
        self.setLayout(layout)
    
    def setup_validation(self):
        """設置驗證"""
        if hasattr(self.input_widget, 'validation_changed'):
            self.input_widget.validation_changed.connect(self.on_validation_changed)
    
    def on_validation_changed(self, is_valid: bool):
        """處理驗證狀態變更"""
        if hasattr(self.input_widget, 'validation_message'):
            message = self.input_widget.validation_message
            if is_valid:
                self.validation_label.hide()
            else:
                self.validation_label.setText(message)
                self.validation_label.show()
        
        self.validation_changed.emit(is_valid)
    
    def set_validation_pattern(self, pattern: str, message: str = ""):
        """設置驗證模式"""
        if hasattr(self.input_widget, 'set_validation_pattern'):
            self.input_widget.set_validation_pattern(pattern, message)
    
    def set_required(self, required: bool, message: str = ""):
        """設置必填"""
        if hasattr(self.input_widget, 'set_required'):
            self.input_widget.set_required(required, message)
    
    def get_value(self):
        """獲取輸入值"""
        if hasattr(self.input_widget, 'text'):
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'toPlainText'):
            return self.input_widget.toPlainText()
        elif hasattr(self.input_widget, 'currentText'):
            return self.input_widget.currentText()
        return None
    
    def set_value(self, value):
        """設置輸入值"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value))
        elif hasattr(self.input_widget, 'setPlainText'):
            self.input_widget.setPlainText(str(value))


class FilePathInput(QWidget):
    """檔案路徑輸入組件 - 包含輸入框和瀏覽按鈕"""
    
    path_changed = pyqtSignal(str)  # 路徑變更信號
    
    def __init__(self, placeholder="選擇檔案...", file_filter="所有檔案 (*)", parent=None):
        super().__init__(parent)
        self.file_filter = file_filter
        
        self.path_input = ModernLineEdit(placeholder)
        self.browse_button = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """設置 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 路徑輸入框
        layout.addWidget(self.path_input, 1)
        
        # 瀏覽按鈕
        from .buttons import FileButton
        self.browse_button = FileButton("瀏覽...", self.file_filter)
        layout.addWidget(self.browse_button)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """設置信號連接"""
        self.path_input.textChanged.connect(self.path_changed.emit)
        self.browse_button.file_selected.connect(self.set_path)
    
    def get_path(self):
        """獲取路徑"""
        return self.path_input.text().strip()
    
    def set_path(self, path: str):
        """設置路徑"""
        self.path_input.setText(path)
        self.path_changed.emit(path)
    
    def set_validation_pattern(self, pattern: str, message: str = ""):
        """設置驗證模式"""
        self.path_input.set_validation_pattern(pattern, message)
    
    def set_required(self, required: bool, message: str = ""):
        """設置必填"""
        self.path_input.set_required(required, message)


class DirectoryPathInput(QWidget):
    """目錄路徑輸入組件"""
    
    path_changed = pyqtSignal(str)  # 路徑變更信號
    
    def __init__(self, placeholder="選擇目錄...", parent=None):
        super().__init__(parent)
        
        self.path_input = ModernLineEdit(placeholder)
        self.browse_button = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """設置 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 路徑輸入框
        layout.addWidget(self.path_input, 1)
        
        # 瀏覽按鈕
        from .buttons import DirectoryButton
        self.browse_button = DirectoryButton("瀏覽...")
        layout.addWidget(self.browse_button)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """設置信號連接"""
        self.path_input.textChanged.connect(self.path_changed.emit)
        self.browse_button.directory_selected.connect(self.set_path)
    
    def get_path(self):
        """獲取路徑"""
        return self.path_input.text().strip()
    
    def set_path(self, path: str):
        """設置路徑"""
        self.path_input.setText(path)
        self.path_changed.emit(path)


# 便利函數
def create_form_inputs(fields: dict, parent=None):
    """創建表單輸入組的便利函數
    
    Args:
        fields: {
            "field_name": {
                "label": "標籤文字",
                "type": "line_edit" | "text_edit" | "combo_box",
                "placeholder": "占位符",
                "required": True/False,
                "validation": "正則表達式",
                "validation_message": "錯誤訊息"
            }
        }
    
    Returns:
        dict: {"field_name": ValidatedInputGroup, ...}
    """
    form_inputs = {}
    
    for field_name, config in fields.items():
        # 創建輸入控件
        input_type = config.get("type", "line_edit")
        placeholder = config.get("placeholder", "")
        
        if input_type == "line_edit":
            input_widget = ModernLineEdit(placeholder)
        elif input_type == "text_edit":
            input_widget = ModernTextEdit(placeholder)
        elif input_type == "combo_box":
            items = config.get("items", [])
            input_widget = ModernComboBox(items)
        else:
            input_widget = ModernLineEdit(placeholder)
        
        # 創建驗證輸入組
        group = ValidatedInputGroup(
            label_text=config.get("label", field_name),
            input_widget=input_widget,
            parent=parent
        )
        
        # 設置驗證
        if config.get("required", False):
            group.set_required(True, config.get("required_message", "此欄位為必填"))
        
        if config.get("validation"):
            group.set_validation_pattern(
                config["validation"],
                config.get("validation_message", "格式不正確")
            )
        
        form_inputs[field_name] = group
    
    return form_inputs