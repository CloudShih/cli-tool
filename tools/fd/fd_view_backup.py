from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QSizePolicy, QGroupBox
)
from PyQt5.QtGui import QFont, QIcon
from ui.components.buttons import ModernButton, PrimaryButton, DirectoryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox, ModernTextEdit
from ui.components.indicators import StatusIndicator, LoadingSpinner

class FdView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """設置現代化 UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題和狀態區域
        header_layout = QHBoxLayout()
        
        title_label = QLabel("檔案搜尋工具 (fd)")
        title_label.setProperty("heading", True)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready", "準備搜尋")
        header_layout.addWidget(self.status_indicator)
        
        main_layout.addLayout(header_layout)
        
        # 搜尋參數群組
        search_group = QGroupBox("搜尋參數")
        search_layout = QGridLayout()
        search_layout.setSpacing(12)
        
        row = 0
        
        # 搜尋模式
        search_layout.addWidget(QLabel("搜尋模式:"), row, 0)
        self.fd_pattern_input = ModernLineEdit(placeholder="e.g., *.txt or report")
        self.fd_pattern_input.setToolTip("輸入要搜尋的檔案或目錄名稱模式，支援正則表達式。")
        search_layout.addWidget(self.fd_pattern_input, row, 1, 1, 2)
        row += 1
        
        # 搜尋路徑
        search_layout.addWidget(QLabel("搜尋路徑:"), row, 0)
        
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        
        self.fd_path_input = ModernLineEdit(placeholder="預設為當前目錄")
        self.fd_path_input.setToolTip("指定搜尋的起始路徑，留空則從當前目錄開始搜尋。")
        path_layout.addWidget(self.fd_path_input, 1)
        
        self.fd_browse_button = DirectoryButton(text="瀏覽...")
        self.fd_browse_button.directory_selected.connect(self.fd_path_input.setText)
        path_layout.addWidget(self.fd_browse_button)
        
        search_layout.addLayout(path_layout, row, 1, 1, 2)
        row += 1
        
        # 檔案副檔名
        search_layout.addWidget(QLabel("檔案副檔名:"), row, 0)
        self.fd_extension_input = ModernLineEdit(placeholder="e.g., txt, py")
        self.fd_extension_input.setToolTip("輸入要搜尋的檔案副檔名，例如 'txt' 或 'py'。")
        search_layout.addWidget(self.fd_extension_input, row, 1, 1, 2)
        row += 1
        
        # 搜尋類型
        search_layout.addWidget(QLabel("搜尋類型:"), row, 0)
        self.fd_type_combobox = ModernComboBox(items=[
            "All (files & directories)",
            "Files only (-t f)", 
            "Directories only (-t d)"
        ])
        self.fd_type_combobox.setToolTip("選擇要搜尋的類型：檔案、目錄或兩者。")
        search_layout.addWidget(self.fd_type_combobox, row, 1)
        row += 1
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 選項群組
        options_group = QGroupBox("搜尋選項")
        options_layout = QHBoxLayout()
        
        self.fd_hidden_checkbox = QCheckBox("包含隱藏檔案 (--hidden)")
        self.fd_hidden_checkbox.setToolTip("勾選以包含隱藏檔案和目錄。")
        options_layout.addWidget(self.fd_hidden_checkbox)
        
        self.fd_case_sensitive_checkbox = QCheckBox("大小寫敏感 (--case-sensitive)")
        self.fd_case_sensitive_checkbox.setToolTip("勾選以啟用大小寫敏感搜尋。")
        options_layout.addWidget(self.fd_case_sensitive_checkbox)
        
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # 操作按鈕區域
        button_layout = QHBoxLayout()
        
        self.fd_search_button = PrimaryButton("開始搜尋")
        self.fd_search_button.setMinimumHeight(40)
        button_layout.addWidget(self.fd_search_button)
        
        clear_button = ModernButton("清除結果")
        clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        # 載入指示器
        self.loading_spinner = LoadingSpinner(24)
        button_layout.addWidget(self.loading_spinner)
        
        main_layout.addLayout(button_layout)
        
        # 結果顯示區域
        results_group = QGroupBox("搜尋結果")
        results_layout = QVBoxLayout()
        
        self.fd_results_display = ModernTextEdit(placeholder="搜尋結果將顯示在這裡...")
        self.fd_results_display.set_read_only_style(True)
        self.fd_results_display.setMinimumHeight(300)
        results_layout.addWidget(self.fd_results_display)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)  # 結果區域可擴展
        
        self.setLayout(main_layout)

    def set_search_button_state(self, text, enabled, background_color=None, text_color=None):
        """設置搜尋按鈕狀態 - 更新為使用現代化組件"""
        self.fd_search_button.setText(text)
        self.fd_search_button.setEnabled(enabled)
        
        # 更新狀態指示器
        if enabled:
            if "搜尋" in text:
                self.status_indicator.set_status("ready", "準備搜尋")
                self.loading_spinner.stop_spinning()
            else:
                self.status_indicator.set_status("processing", "搜尋中...")
                self.loading_spinner.start_spinning()
        else:
            self.status_indicator.set_status("processing", "處理中...")
            self.loading_spinner.start_spinning()
    
    def clear_results(self):
        """清除搜尋結果"""
        self.fd_results_display.clear()
        self.status_indicator.set_status("ready", "準備搜尋")
        self.loading_spinner.stop_spinning()
    
    def set_search_completed(self, success=True, message=""):
        """設置搜尋完成狀態"""
        if success:
            self.status_indicator.set_status("success", message or "搜尋完成")
        else:
            self.status_indicator.set_status("error", message or "搜尋失敗")
        
        self.loading_spinner.stop_spinning()
        self.fd_search_button.setText("開始搜尋")
        self.fd_search_button.setEnabled(True)
