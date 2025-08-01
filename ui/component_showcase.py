"""
UI 組件展示頁面 - 展示所有現代化 UI 組件
用於測試和預覽新組件的外觀和功能
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QLabel, QFrame, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.components.buttons import (
    ModernButton, PrimaryButton, DangerButton, IconButton,
    ButtonGroup, ActionButton, FileButton, DirectoryButton
)
from ui.components.inputs import (
    ModernLineEdit, ModernTextEdit, ModernComboBox,
    ValidatedInputGroup, FilePathInput, DirectoryPathInput
)
from ui.components.indicators import (
    LoadingSpinner, ProgressIndicator, StatusIndicator, LoadingOverlay
)
import logging

logger = logging.getLogger(__name__)


class ComponentShowcase(QWidget):
    """組件展示主頁面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loading_overlay = None
        self.setup_ui()
        self.setup_demo_data()
    
    def setup_ui(self):
        """設置 UI"""
        # 主佈局使用滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 內容組件
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 標題
        title_label = QLabel("現代化 UI 組件展示")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        
        # 按鈕組件展示
        content_layout.addWidget(self.create_buttons_section())
        
        # 輸入組件展示
        content_layout.addWidget(self.create_inputs_section())
        
        # 指示器組件展示
        content_layout.addWidget(self.create_indicators_section())
        
        # 檔案操作組件展示
        content_layout.addWidget(self.create_file_operations_section())
        
        # 組合示例
        content_layout.addWidget(self.create_combination_examples())
        
        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        
        scroll_area.setWidget(content_widget)
        
        # 主佈局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
        # 創建載入覆蓋層
        self.loading_overlay = LoadingOverlay(self, "正在載入組件...")
    
    def create_buttons_section(self):
        """創建按鈕展示區域"""
        group_box = QGroupBox("按鈕組件")
        layout = QVBoxLayout()
        
        # 基礎按鈕
        basic_layout = QHBoxLayout()
        basic_layout.addWidget(QLabel("基礎按鈕:"))
        
        basic_button = ModernButton("標準按鈕")
        basic_button.clicked.connect(lambda: self.show_message("標準按鈕被點擊"))
        basic_layout.addWidget(basic_button)
        
        primary_button = PrimaryButton("主要按鈕")
        primary_button.clicked.connect(lambda: self.show_message("主要按鈕被點擊"))
        basic_layout.addWidget(primary_button)
        
        danger_button = DangerButton("危險按鈕")
        danger_button.clicked.connect(lambda: self.show_message("危險按鈕被點擊"))
        basic_layout.addWidget(danger_button)
        
        basic_layout.addStretch()
        layout.addLayout(basic_layout)
        
        # 按鈕群組
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("按鈕群組:"))
        
        button_group = ButtonGroup([
            ModernButton("選項 1"),
            ModernButton("選項 2"),
            ModernButton("選項 3")
        ])
        group_layout.addWidget(button_group)
        group_layout.addStretch()
        layout.addLayout(group_layout)
        
        # 動作按鈕
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("動作按鈕:"))
        
        self.action_button = ActionButton("執行動作", "正在執行...")
        self.action_button.clicked.connect(self.demo_action)
        action_layout.addWidget(self.action_button)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_inputs_section(self):
        """創建輸入組件展示區域"""
        group_box = QGroupBox("輸入組件")
        layout = QVBoxLayout()
        
        # 基礎輸入框
        input_layout = QGridLayout()
        
        # 標準輸入框
        input_layout.addWidget(QLabel("標準輸入框:"), 0, 0)
        standard_input = ModernLineEdit("請輸入文字...")
        input_layout.addWidget(standard_input, 0, 1)
        
        # 驗證輸入框
        input_layout.addWidget(QLabel("驗證輸入框:"), 1, 0)
        self.validated_input = ModernLineEdit("輸入電子郵件...")
        self.validated_input.set_validation_pattern(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "請輸入有效的電子郵件地址"
        )
        input_layout.addWidget(self.validated_input, 1, 1)
        
        # 下拉選單
        input_layout.addWidget(QLabel("下拉選單:"), 2, 0)
        combo_box = ModernComboBox(["選項 1", "選項 2", "選項 3"])
        input_layout.addWidget(combo_box, 2, 1)
        
        layout.addLayout(input_layout)
        
        # 多行文本
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("多行文本:"))
        text_edit = ModernTextEdit("這是多行文本編輯器...")
        text_edit.setMaximumHeight(100)
        text_layout.addWidget(text_edit)
        layout.addLayout(text_layout)
        
        # 驗證輸入群組
        validated_group = ValidatedInputGroup(
            "必填電子郵件:",
            ModernLineEdit("請輸入電子郵件...")
        )
        validated_group.set_required(True)
        validated_group.set_validation_pattern(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "請輸入有效的電子郵件地址"
        )
        layout.addWidget(validated_group)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_indicators_section(self):
        """創建指示器組件展示區域"""
        group_box = QGroupBox("指示器組件")
        layout = QVBoxLayout()
        
        # 載入旋轉器
        spinner_layout = QHBoxLayout()
        spinner_layout.addWidget(QLabel("載入旋轉器:"))
        
        self.spinner = LoadingSpinner(32)
        spinner_layout.addWidget(self.spinner)
        
        spinner_button = ModernButton("開始/停止")
        spinner_button.clicked.connect(self.toggle_spinner)
        spinner_layout.addWidget(spinner_button)
        
        spinner_layout.addStretch()
        layout.addLayout(spinner_layout)
        
        # 進度指示器
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("進度指示器:"))
        
        self.progress_indicator = ProgressIndicator()
        progress_layout.addWidget(self.progress_indicator)
        
        progress_button_layout = QHBoxLayout()
        start_progress_button = ModernButton("開始進度")
        start_progress_button.clicked.connect(self.start_progress_demo)
        progress_button_layout.addWidget(start_progress_button)
        
        reset_progress_button = ModernButton("重設進度")
        reset_progress_button.clicked.connect(self.progress_indicator.reset)
        progress_button_layout.addWidget(reset_progress_button)
        
        progress_button_layout.addStretch()
        progress_layout.addLayout(progress_button_layout)
        layout.addLayout(progress_layout)
        
        # 狀態指示器
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("狀態指示器:"))
        
        self.status_indicator = StatusIndicator()
        status_layout.addWidget(self.status_indicator)
        
        status_buttons_layout = QHBoxLayout()
        for status in ["ready", "processing", "success", "error", "warning"]:
            button = ModernButton(status.title())
            button.clicked.connect(lambda checked, s=status: self.status_indicator.set_status(s))
            status_buttons_layout.addWidget(button)
        
        status_layout.addLayout(status_buttons_layout)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_file_operations_section(self):
        """創建檔案操作組件展示區域"""
        group_box = QGroupBox("檔案操作組件")
        layout = QVBoxLayout()
        
        # 檔案路徑輸入
        file_path_input = FilePathInput("選擇檔案...", "文本檔案 (*.txt)")
        file_path_input.path_changed.connect(lambda path: self.show_message(f"選擇的檔案: {path}"))
        layout.addWidget(QLabel("檔案路徑輸入:"))
        layout.addWidget(file_path_input)
        
        # 目錄路徑輸入
        dir_path_input = DirectoryPathInput("選擇目錄...")
        dir_path_input.path_changed.connect(lambda path: self.show_message(f"選擇的目錄: {path}"))
        layout.addWidget(QLabel("目錄路徑輸入:"))
        layout.addWidget(dir_path_input)
        
        # 獨立檔案按鈕
        file_button_layout = QHBoxLayout()
        file_button = FileButton("選擇檔案", "所有檔案 (*)")
        file_button.file_selected.connect(lambda path: self.show_message(f"檔案: {path}"))
        file_button_layout.addWidget(file_button)
        
        dir_button = DirectoryButton("選擇目錄")
        dir_button.directory_selected.connect(lambda path: self.show_message(f"目錄: {path}"))
        file_button_layout.addWidget(dir_button)
        
        file_button_layout.addStretch()
        layout.addLayout(file_button_layout)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_combination_examples(self):
        """創建組合示例"""
        group_box = QGroupBox("組合示例")
        layout = QVBoxLayout()
        
        # 表單示例
        form_layout = QGridLayout()
        
        # 姓名輸入
        name_group = ValidatedInputGroup("姓名:", ModernLineEdit("請輸入姓名"))
        name_group.set_required(True, "姓名為必填欄位")
        form_layout.addWidget(name_group, 0, 0)
        
        # 電子郵件輸入
        email_group = ValidatedInputGroup("電子郵件:", ModernLineEdit("請輸入電子郵件"))
        email_group.set_required(True)
        email_group.set_validation_pattern(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "請輸入有效的電子郵件地址"
        )
        form_layout.addWidget(email_group, 0, 1)
        
        # 年齡輸入
        age_group = ValidatedInputGroup("年齡:", ModernLineEdit("請輸入年齡"))
        age_group.set_validation_pattern(r'^\d{1,3}$', "請輸入有效的年齡 (1-999)")
        form_layout.addWidget(age_group, 1, 0)
        
        # 城市選擇
        city_combo = ModernComboBox(["台北", "台中", "台南", "高雄"])
        city_group = ValidatedInputGroup("城市:", city_combo)
        form_layout.addWidget(city_group, 1, 1)
        
        layout.addLayout(form_layout)
        
        # 表單按鈕
        form_buttons = ButtonGroup([
            PrimaryButton("提交"),
            ModernButton("重設"),
            DangerButton("清除")
        ])
        layout.addWidget(form_buttons)
        
        # 載入覆蓋層示例
        overlay_button_layout = QHBoxLayout()
        overlay_button = ModernButton("顯示載入覆蓋層")
        overlay_button.clicked.connect(self.show_loading_overlay)
        overlay_button_layout.addWidget(overlay_button)
        overlay_button_layout.addStretch()
        layout.addLayout(overlay_button_layout)
        
        group_box.setLayout(layout)
        return group_box
    
    def setup_demo_data(self):
        """設置示例數據"""
        pass
    
    @pyqtSlot()
    def show_message(self, message: str):
        """顯示訊息"""
        logger.info(f"Showcase message: {message}")
        # 這裡可以實現實際的訊息顯示，目前只記錄日誌
    
    @pyqtSlot()
    def demo_action(self):
        """示例動作"""
        self.action_button.execute_action(lambda: None)
    
    @pyqtSlot()
    def toggle_spinner(self):
        """切換旋轉器狀態"""
        if self.spinner.is_spinning:
            self.spinner.stop_spinning()
        else:
            self.spinner.start_spinning()
    
    @pyqtSlot()
    def start_progress_demo(self):
        """開始進度示例"""
        from PyQt5.QtCore import QTimer
        
        self.progress_indicator.reset()
        self.progress_timer = QTimer(self)  # 設置父對象確保在正確線程中
        self.progress_value = 0
        
        def update_progress():
            self.progress_value += 10
            if self.progress_value <= 100:
                self.progress_indicator.set_progress(
                    self.progress_value, 
                    f"處理中... {self.progress_value}%"
                )
            else:
                self.progress_indicator.complete("處理完成!")
                self.progress_timer.stop()
        
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(200)  # 每200ms更新一次
    
    @pyqtSlot()
    def show_loading_overlay(self):
        """顯示載入覆蓋層"""
        self.loading_overlay.show_loading("正在載入組件展示...")
        
        # 3秒後自動隱藏
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, self.loading_overlay.hide_loading)