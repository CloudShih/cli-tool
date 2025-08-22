"""
QPDF 視圖層
提供 PyQt5 GUI 介面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QLabel, QCheckBox, QComboBox, QSizePolicy, QFileDialog, 
    QListWidget, QSpinBox, QGroupBox, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer

from .core.data_models import EncryptionLevel, CompressionLevel


class QPDFView(QWidget):
    """QPDF 視圖類"""
    
    def __init__(self):
        super().__init__()
        
        # Common font and stylesheet for results display
        self.results_font = QFont("Consolas", 12)
        self.results_stylesheet = "background-color: #282c34; color: #abb2bf;"
        
        # Main layout
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Initialize tabs
        self._setup_check_tab()
        self._setup_decrypt_tab()
        self._setup_encrypt_tab()
        self._setup_linearize_tab()
        self._setup_split_tab()
        self._setup_rotate_tab()
        self._setup_compress_tab()
        self._setup_repair_tab()
        self._setup_json_info_tab()
        self._setup_batch_tab()
        
        self.setLayout(main_layout)
    
    def _setup_check_tab(self):
        """設置檢查 PDF 分頁"""
        self.check_tab = QWidget()
        self.tabs.addTab(self.check_tab, "檢查 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # PDF Path
        pdf_path_label = QLabel("PDF 檔案路徑:")
        pdf_path_label.setMinimumWidth(label_width)
        layout.addWidget(pdf_path_label, row, 0)
        self.check_path_input = QLineEdit()
        self.check_path_input.setPlaceholderText("例如: D:\\document.pdf")
        self.check_path_input.setToolTip("選擇要檢查的 PDF 檔案")
        layout.addWidget(self.check_path_input, row, 1, 1, 10)
        
        self.check_browse_button = QPushButton("瀏覽...")
        self.check_browse_button.setToolTip("點擊選擇 PDF 檔案")
        layout.addWidget(self.check_browse_button, row, 11, 1, 2)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.check_password_input = QLineEdit()
        self.check_password_input.setEchoMode(QLineEdit.Password)
        self.check_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.check_password_input, row, 1, 1, 11)
        row += 1
        
        # Check Button
        self.check_button = QPushButton("檢查 PDF")
        self.check_button.setToolTip("檢查 PDF 檔案的完整性和資訊")
        layout.addWidget(self.check_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.check_results_display = QTextEdit()
        self.check_results_display.setReadOnly(True)
        self.check_results_display.setFont(self.results_font)
        self.check_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.check_results_display, row, 0, 1, 12)
        
        self.check_tab.setLayout(layout)
    
    def _setup_decrypt_tab(self):
        """設置解密分頁"""
        self.decrypt_tab = QWidget()
        self.tabs.addTab(self.decrypt_tab, "解密 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.decrypt_input_path = QLineEdit()
        self.decrypt_input_path.setPlaceholderText("例如: D:\\encrypted.pdf")
        layout.addWidget(self.decrypt_input_path, row, 1, 1, 10)
        
        self.decrypt_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.decrypt_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.decrypt_output_path = QLineEdit()
        self.decrypt_output_path.setPlaceholderText("例如: D:\\decrypted (系統自動添加.pdf)")
        layout.addWidget(self.decrypt_output_path, row, 1, 1, 10)
        
        self.decrypt_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.decrypt_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Password
        password_label = QLabel("PDF 密碼:")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.decrypt_password_input = QLineEdit()
        self.decrypt_password_input.setEchoMode(QLineEdit.Password)
        self.decrypt_password_input.setPlaceholderText("輸入 PDF 密碼")
        layout.addWidget(self.decrypt_password_input, row, 1, 1, 11)
        row += 1
        
        # Decrypt Button
        self.decrypt_button = QPushButton("解密 PDF")
        layout.addWidget(self.decrypt_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.decrypt_results_display = QTextEdit()
        self.decrypt_results_display.setReadOnly(True)
        self.decrypt_results_display.setFont(self.results_font)
        self.decrypt_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.decrypt_results_display, row, 0, 1, 12)
        
        self.decrypt_tab.setLayout(layout)
    
    def _setup_encrypt_tab(self):
        """設置加密分頁"""
        self.encrypt_tab = QWidget()
        self.tabs.addTab(self.encrypt_tab, "加密 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.encrypt_input_path = QLineEdit()
        self.encrypt_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.encrypt_input_path, row, 1, 1, 10)
        
        self.encrypt_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.encrypt_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.encrypt_output_path = QLineEdit()
        self.encrypt_output_path.setPlaceholderText("例如: D:\\encrypted (系統自動添加.pdf)")
        layout.addWidget(self.encrypt_output_path, row, 1, 1, 10)
        
        self.encrypt_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.encrypt_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # User Password
        user_password_label = QLabel("使用者密碼:")
        user_password_label.setMinimumWidth(label_width)
        layout.addWidget(user_password_label, row, 0)
        self.encrypt_user_password = QLineEdit()
        self.encrypt_user_password.setEchoMode(QLineEdit.Password)
        self.encrypt_user_password.setPlaceholderText("設置使用者密碼")
        layout.addWidget(self.encrypt_user_password, row, 1, 1, 11)
        row += 1
        
        # Owner Password
        owner_password_label = QLabel("擁有者密碼:")
        owner_password_label.setMinimumWidth(label_width)
        layout.addWidget(owner_password_label, row, 0)
        self.encrypt_owner_password = QLineEdit()
        self.encrypt_owner_password.setEchoMode(QLineEdit.Password)
        self.encrypt_owner_password.setPlaceholderText("設置擁有者密碼 (可選，預設與使用者密碼相同)")
        layout.addWidget(self.encrypt_owner_password, row, 1, 1, 11)
        row += 1
        
        # Encryption Level
        encryption_label = QLabel("加密等級:")
        encryption_label.setMinimumWidth(label_width)
        layout.addWidget(encryption_label, row, 0)
        self.encrypt_level_combo = QComboBox()
        self.encrypt_level_combo.addItem("40-bit RC4", EncryptionLevel.RC4_40)
        self.encrypt_level_combo.addItem("128-bit RC4", EncryptionLevel.RC4_128)
        self.encrypt_level_combo.addItem("128-bit AES", EncryptionLevel.AES_128)
        self.encrypt_level_combo.addItem("256-bit AES (推薦)", EncryptionLevel.AES_256)
        self.encrypt_level_combo.setCurrentIndex(3)  # Default to AES 256
        layout.addWidget(self.encrypt_level_combo, row, 1, 1, 5)
        row += 1
        
        # Permissions Group
        permissions_group = QGroupBox("權限設定")
        permissions_layout = QGridLayout()
        
        self.encrypt_allow_print = QCheckBox("允許列印")
        self.encrypt_allow_print.setChecked(True)
        permissions_layout.addWidget(self.encrypt_allow_print, 0, 0)
        
        self.encrypt_allow_modify = QCheckBox("允許修改")
        self.encrypt_allow_modify.setChecked(True)
        permissions_layout.addWidget(self.encrypt_allow_modify, 0, 1)
        
        self.encrypt_allow_extract = QCheckBox("允許提取文字")
        self.encrypt_allow_extract.setChecked(True)
        permissions_layout.addWidget(self.encrypt_allow_extract, 1, 0)
        
        self.encrypt_allow_annotate = QCheckBox("允許註解")
        self.encrypt_allow_annotate.setChecked(True)
        permissions_layout.addWidget(self.encrypt_allow_annotate, 1, 1)
        
        permissions_group.setLayout(permissions_layout)
        layout.addWidget(permissions_group, row, 0, 1, 12)
        row += 1
        
        # Encrypt Button
        self.encrypt_button = QPushButton("加密 PDF")
        layout.addWidget(self.encrypt_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.encrypt_results_display = QTextEdit()
        self.encrypt_results_display.setReadOnly(True)
        self.encrypt_results_display.setFont(self.results_font)
        self.encrypt_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.encrypt_results_display, row, 0, 1, 12)
        
        self.encrypt_tab.setLayout(layout)
    
    def _setup_linearize_tab(self):
        """設置線性化分頁"""
        self.linearize_tab = QWidget()
        self.tabs.addTab(self.linearize_tab, "線性化 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.linearize_input_path = QLineEdit()
        self.linearize_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.linearize_input_path, row, 1, 1, 10)
        
        self.linearize_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.linearize_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.linearize_output_path = QLineEdit()
        self.linearize_output_path.setPlaceholderText("例如: D:\\linearized (系統自動添加.pdf)")
        layout.addWidget(self.linearize_output_path, row, 1, 1, 10)
        
        self.linearize_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.linearize_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.linearize_password_input = QLineEdit()
        self.linearize_password_input.setEchoMode(QLineEdit.Password)
        self.linearize_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.linearize_password_input, row, 1, 1, 11)
        row += 1
        
        # Linearize Button
        self.linearize_button = QPushButton("線性化 PDF")
        self.linearize_button.setToolTip("線性化 PDF 以支援網頁快速載入")
        layout.addWidget(self.linearize_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.linearize_results_display = QTextEdit()
        self.linearize_results_display.setReadOnly(True)
        self.linearize_results_display.setFont(self.results_font)
        self.linearize_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.linearize_results_display, row, 0, 1, 12)
        
        self.linearize_tab.setLayout(layout)
    
    def _setup_split_tab(self):
        """設置分割頁面分頁"""
        self.split_tab = QWidget()
        self.tabs.addTab(self.split_tab, "分割頁面")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.split_input_path = QLineEdit()
        self.split_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.split_input_path, row, 1, 1, 10)
        
        self.split_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.split_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output Pattern
        output_label = QLabel("輸出檔案模式:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.split_output_pattern = QLineEdit()
        self.split_output_pattern.setPlaceholderText("例如: D:\\pages\\page-%d (系統自動添加.pdf)")
        self.split_output_pattern.setToolTip("使用 %d 作為頁碼佔位符")
        layout.addWidget(self.split_output_pattern, row, 1, 1, 10)
        
        self.split_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.split_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Page Range
        page_range_label = QLabel("頁面範圍:")
        page_range_label.setMinimumWidth(label_width)
        layout.addWidget(page_range_label, row, 0)
        self.split_page_range = QLineEdit()
        self.split_page_range.setPlaceholderText("例如: 1-5, 1,3,5, 1- (可選，留空表示所有頁面)")
        self.split_page_range.setToolTip("指定要分割的頁面範圍")
        layout.addWidget(self.split_page_range, row, 1, 1, 11)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.split_password_input = QLineEdit()
        self.split_password_input.setEchoMode(QLineEdit.Password)
        self.split_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.split_password_input, row, 1, 1, 11)
        row += 1
        
        # Split Button
        self.split_button = QPushButton("分割 PDF 頁面")
        layout.addWidget(self.split_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.split_results_display = QTextEdit()
        self.split_results_display.setReadOnly(True)
        self.split_results_display.setFont(self.results_font)
        self.split_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.split_results_display, row, 0, 1, 12)
        
        self.split_tab.setLayout(layout)
    
    def _setup_rotate_tab(self):
        """設置旋轉頁面分頁"""
        self.rotate_tab = QWidget()
        self.tabs.addTab(self.rotate_tab, "旋轉頁面")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.rotate_input_path = QLineEdit()
        self.rotate_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.rotate_input_path, row, 1, 1, 10)
        
        self.rotate_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.rotate_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.rotate_output_path = QLineEdit()
        self.rotate_output_path.setPlaceholderText("例如: D:\\rotated (系統自動添加.pdf)")
        layout.addWidget(self.rotate_output_path, row, 1, 1, 10)
        
        self.rotate_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.rotate_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Rotation Angle
        angle_label = QLabel("旋轉角度:")
        angle_label.setMinimumWidth(label_width)
        layout.addWidget(angle_label, row, 0)
        self.rotate_angle_combo = QComboBox()
        self.rotate_angle_combo.addItem("90° (順時針)", 90)
        self.rotate_angle_combo.addItem("180° (倒轉)", 180)
        self.rotate_angle_combo.addItem("270° (逆時針)", 270)
        layout.addWidget(self.rotate_angle_combo, row, 1, 1, 5)
        row += 1
        
        # Page Range
        page_range_label = QLabel("頁面範圍:")
        page_range_label.setMinimumWidth(label_width)
        layout.addWidget(page_range_label, row, 0)
        self.rotate_page_range = QLineEdit()
        self.rotate_page_range.setPlaceholderText("例如: 1-5, 1,3,5, 1- (預設: 1-，即所有頁面)")
        self.rotate_page_range.setText("1-")
        layout.addWidget(self.rotate_page_range, row, 1, 1, 11)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.rotate_password_input = QLineEdit()
        self.rotate_password_input.setEchoMode(QLineEdit.Password)
        self.rotate_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.rotate_password_input, row, 1, 1, 11)
        row += 1
        
        # Rotate Button
        self.rotate_button = QPushButton("旋轉 PDF 頁面")
        layout.addWidget(self.rotate_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.rotate_results_display = QTextEdit()
        self.rotate_results_display.setReadOnly(True)
        self.rotate_results_display.setFont(self.results_font)
        self.rotate_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.rotate_results_display, row, 0, 1, 12)
        
        self.rotate_tab.setLayout(layout)
    
    def _setup_compress_tab(self):
        """設置壓縮分頁"""
        self.compress_tab = QWidget()
        self.tabs.addTab(self.compress_tab, "壓縮 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.compress_input_path = QLineEdit()
        self.compress_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.compress_input_path, row, 1, 1, 10)
        
        self.compress_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.compress_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.compress_output_path = QLineEdit()
        self.compress_output_path.setPlaceholderText("例如: D:\\compressed (系統自動添加.pdf)")
        layout.addWidget(self.compress_output_path, row, 1, 1, 10)
        
        self.compress_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.compress_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Compression Level
        compression_label = QLabel("壓縮等級:")
        compression_label.setMinimumWidth(label_width)
        layout.addWidget(compression_label, row, 0)
        self.compress_level_combo = QComboBox()
        self.compress_level_combo.addItem("低壓縮", CompressionLevel.LOW)
        self.compress_level_combo.addItem("中等壓縮 (推薦)", CompressionLevel.MEDIUM)
        self.compress_level_combo.addItem("高壓縮", CompressionLevel.HIGH)
        self.compress_level_combo.setCurrentIndex(1)  # Default to medium
        layout.addWidget(self.compress_level_combo, row, 1, 1, 5)
        row += 1
        
        # Options
        self.compress_remove_unreferenced = QCheckBox("移除未引用的資源")
        self.compress_remove_unreferenced.setChecked(True)
        self.compress_remove_unreferenced.setToolTip("移除 PDF 中未使用的物件和資源")
        layout.addWidget(self.compress_remove_unreferenced, row, 0, 1, 6)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.compress_password_input = QLineEdit()
        self.compress_password_input.setEchoMode(QLineEdit.Password)
        self.compress_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.compress_password_input, row, 1, 1, 11)
        row += 1
        
        # Compress Button
        self.compress_button = QPushButton("壓縮 PDF")
        layout.addWidget(self.compress_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.compress_results_display = QTextEdit()
        self.compress_results_display.setReadOnly(True)
        self.compress_results_display.setFont(self.results_font)
        self.compress_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.compress_results_display, row, 0, 1, 12)
        
        self.compress_tab.setLayout(layout)
    
    def _setup_repair_tab(self):
        """設置修復分頁"""
        self.repair_tab = QWidget()
        self.tabs.addTab(self.repair_tab, "修復 PDF")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.repair_input_path = QLineEdit()
        self.repair_input_path.setPlaceholderText("例如: D:\\damaged.pdf")
        layout.addWidget(self.repair_input_path, row, 1, 1, 10)
        
        self.repair_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.repair_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Output PDF Path
        output_label = QLabel("輸出 PDF 檔案:")
        output_label.setMinimumWidth(label_width)
        layout.addWidget(output_label, row, 0)
        self.repair_output_path = QLineEdit()
        self.repair_output_path.setPlaceholderText("例如: D:\\repaired (系統自動添加.pdf)")
        layout.addWidget(self.repair_output_path, row, 1, 1, 10)
        
        self.repair_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.repair_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.repair_password_input = QLineEdit()
        self.repair_password_input.setEchoMode(QLineEdit.Password)
        self.repair_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.repair_password_input, row, 1, 1, 11)
        row += 1
        
        # Repair Button
        self.repair_button = QPushButton("修復 PDF")
        self.repair_button.setToolTip("嘗試修復損壞的 PDF 檔案")
        layout.addWidget(self.repair_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.repair_results_display = QTextEdit()
        self.repair_results_display.setReadOnly(True)
        self.repair_results_display.setFont(self.results_font)
        self.repair_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.repair_results_display, row, 0, 1, 12)
        
        self.repair_tab.setLayout(layout)
    
    def _setup_json_info_tab(self):
        """設置 JSON 資訊分頁"""
        self.json_info_tab = QWidget()
        self.tabs.addTab(self.json_info_tab, "JSON 資訊")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # Input PDF Path
        input_label = QLabel("輸入 PDF 檔案:")
        input_label.setMinimumWidth(label_width)
        layout.addWidget(input_label, row, 0)
        self.json_info_input_path = QLineEdit()
        self.json_info_input_path.setPlaceholderText("例如: D:\\document.pdf")
        layout.addWidget(self.json_info_input_path, row, 1, 1, 10)
        
        self.json_info_browse_input_button = QPushButton("瀏覽...")
        layout.addWidget(self.json_info_browse_input_button, row, 11, 1, 2)
        row += 1
        
        # Password (optional)
        password_label = QLabel("密碼 (可選):")
        password_label.setMinimumWidth(label_width)
        layout.addWidget(password_label, row, 0)
        self.json_info_password_input = QLineEdit()
        self.json_info_password_input.setEchoMode(QLineEdit.Password)
        self.json_info_password_input.setPlaceholderText("如果 PDF 有密碼保護，請輸入密碼")
        layout.addWidget(self.json_info_password_input, row, 1, 1, 11)
        row += 1
        
        # Get JSON Info Button
        self.json_info_button = QPushButton("取得 JSON 資訊")
        self.json_info_button.setToolTip("以 JSON 格式取得 PDF 詳細資訊")
        layout.addWidget(self.json_info_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.json_info_results_display = QTextEdit()
        self.json_info_results_display.setReadOnly(True)
        self.json_info_results_display.setFont(self.results_font)
        self.json_info_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.json_info_results_display, row, 0, 1, 12)
        
        self.json_info_tab.setLayout(layout)
    
    def _setup_batch_tab(self):
        """設置批量操作分頁"""
        self.batch_tab = QWidget()
        self.tabs.addTab(self.batch_tab, "批量操作")
        
        layout = QGridLayout()
        label_width = 180
        row = 0
        
        # File List
        file_list_label = QLabel("PDF 檔案列表:")
        layout.addWidget(file_list_label, row, 0, 1, 12)
        row += 1
        
        self.batch_file_list = QListWidget()
        self.batch_file_list.setToolTip("要處理的 PDF 檔案列表")
        layout.addWidget(self.batch_file_list, row, 0, 1, 12)
        row += 1
        
        # File Management Buttons
        file_button_layout = QHBoxLayout()
        self.batch_add_files_button = QPushButton("新增檔案")
        self.batch_add_files_button.setToolTip("新增要處理的 PDF 檔案")
        file_button_layout.addWidget(self.batch_add_files_button)
        
        self.batch_add_folder_button = QPushButton("新增資料夾")
        self.batch_add_folder_button.setToolTip("新增資料夾中的所有 PDF 檔案")
        file_button_layout.addWidget(self.batch_add_folder_button)
        
        self.batch_remove_button = QPushButton("移除選取")
        self.batch_remove_button.setToolTip("從列表中移除選取的檔案")
        file_button_layout.addWidget(self.batch_remove_button)
        
        self.batch_clear_button = QPushButton("清空列表")
        self.batch_clear_button.setToolTip("清空所有檔案")
        file_button_layout.addWidget(self.batch_clear_button)
        
        layout.addLayout(file_button_layout, row, 0, 1, 12)
        row += 1
        
        # Operation Type
        operation_label = QLabel("批量操作類型:")
        operation_label.setMinimumWidth(label_width)
        layout.addWidget(operation_label, row, 0)
        self.batch_operation_combo = QComboBox()
        self.batch_operation_combo.addItem("檢查 PDF", "check")
        self.batch_operation_combo.addItem("線性化", "linearize")
        self.batch_operation_combo.addItem("壓縮", "compress")
        self.batch_operation_combo.addItem("修復", "repair")
        layout.addWidget(self.batch_operation_combo, row, 1, 1, 5)
        row += 1
        
        # Output Directory
        output_dir_label = QLabel("輸出目錄:")
        output_dir_label.setMinimumWidth(label_width)
        layout.addWidget(output_dir_label, row, 0)
        self.batch_output_dir = QLineEdit()
        self.batch_output_dir.setPlaceholderText("例如: D:\\output")
        layout.addWidget(self.batch_output_dir, row, 1, 1, 10)
        
        self.batch_browse_output_button = QPushButton("瀏覽...")
        layout.addWidget(self.batch_browse_output_button, row, 11, 1, 2)
        row += 1
        
        # Batch Options
        batch_options_group = QGroupBox("批量處理選項")
        batch_options_layout = QGridLayout()
        
        self.batch_parallel = QCheckBox("並行處理")
        self.batch_parallel.setChecked(True)
        self.batch_parallel.setToolTip("同時處理多個檔案以提高速度")
        batch_options_layout.addWidget(self.batch_parallel, 0, 0)
        
        self.batch_continue_on_error = QCheckBox("遇到錯誤時繼續")
        self.batch_continue_on_error.setChecked(True)
        self.batch_continue_on_error.setToolTip("當某個檔案處理失敗時繼續處理其他檔案")
        batch_options_layout.addWidget(self.batch_continue_on_error, 0, 1)
        
        max_workers_label = QLabel("最大並行數:")
        batch_options_layout.addWidget(max_workers_label, 1, 0)
        self.batch_max_workers = QSpinBox()
        self.batch_max_workers.setRange(1, 8)
        self.batch_max_workers.setValue(4)
        self.batch_max_workers.setToolTip("同時處理的檔案數量")
        batch_options_layout.addWidget(self.batch_max_workers, 1, 1)
        
        batch_options_group.setLayout(batch_options_layout)
        layout.addWidget(batch_options_group, row, 0, 1, 12)
        row += 1
        
        # Progress Bar
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setVisible(False)
        layout.addWidget(self.batch_progress_bar, row, 0, 1, 12)
        row += 1
        
        # Execute Button
        self.batch_execute_button = QPushButton("執行批量操作")
        layout.addWidget(self.batch_execute_button, row, 0, 1, 12)
        row += 1
        
        # Results Display
        self.batch_results_display = QTextEdit()
        self.batch_results_display.setReadOnly(True)
        self.batch_results_display.setFont(self.results_font)
        self.batch_results_display.setStyleSheet(self.results_stylesheet)
        layout.addWidget(self.batch_results_display, row, 0, 1, 12)
        
        self.batch_tab.setLayout(layout)
    
    def show_progress(self, visible=True):
        """顯示或隱藏進度條"""
        self.batch_progress_bar.setVisible(visible)
    
    def set_progress(self, value, text=""):
        """設置進度條數值"""
        self.batch_progress_bar.setValue(value)
        if text:
            self.batch_progress_bar.setFormat(f"{text} ({value}%)")
    
    def clear_results(self, tab_name):
        """清空指定分頁的結果顯示"""
        result_displays = {
            'check': self.check_results_display,
            'decrypt': self.decrypt_results_display,
            'encrypt': self.encrypt_results_display,
            'linearize': self.linearize_results_display,
            'split': self.split_results_display,
            'rotate': self.rotate_results_display,
            'compress': self.compress_results_display,
            'repair': self.repair_results_display,
            'json_info': self.json_info_results_display,
            'batch': self.batch_results_display
        }
        
        if tab_name in result_displays:
            result_displays[tab_name].clear()
    
    def display_results(self, tab_name, content):
        """在指定分頁顯示結果"""
        result_displays = {
            'check': self.check_results_display,
            'decrypt': self.decrypt_results_display,
            'encrypt': self.encrypt_results_display,
            'linearize': self.linearize_results_display,
            'split': self.split_results_display,
            'rotate': self.rotate_results_display,
            'compress': self.compress_results_display,
            'repair': self.repair_results_display,
            'json_info': self.json_info_results_display,
            'batch': self.batch_results_display
        }
        
        if tab_name in result_displays:
            result_displays[tab_name].setHtml(content)