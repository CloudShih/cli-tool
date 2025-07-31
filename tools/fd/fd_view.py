from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QLabel, QCheckBox, QComboBox, QSizePolicy, QFileDialog
)
from PyQt5.QtGui import QFont, QIcon

class FdView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        fd_layout = QGridLayout()

        # Define a common label width for alignment
        label_width = 180 # Adjust this value as needed

        row = 0

        # Search Pattern
        pattern_label = QLabel("Search Pattern:")
        pattern_label.setMinimumWidth(label_width)
        fd_layout.addWidget(pattern_label, row, 0)
        self.fd_pattern_input = QLineEdit()
        self.fd_pattern_input.setPlaceholderText("e.g., *.txt or report")
        self.fd_pattern_input.setToolTip("輸入要搜尋的檔案或目錄名稱模式，支援正則表達式。")
        fd_layout.addWidget(self.fd_pattern_input, row, 1, 1, 10)
        row += 1

        # Start Path
        path_label = QLabel("Start Path:")
        path_label.setMinimumWidth(label_width)
        fd_layout.addWidget(path_label, row, 0)
        self.fd_path_input = QLineEdit()
        self.fd_path_input.setPlaceholderText("e.g., D:\\geminiCLI (defaults to current directory)")
        self.fd_path_input.setToolTip("指定搜尋的起始路徑，留空則從當前目錄開始搜尋。")
        fd_layout.addWidget(self.fd_path_input, row, 1, 1, 10)
        
        self.fd_browse_button = QPushButton("瀏覽...")
        self.fd_browse_button.setToolTip("點擊以透過檔案總管選擇起始路徑。")
        fd_layout.addWidget(self.fd_browse_button, row, 11, 1, 2)
        row += 1

        # File Extension
        extension_label = QLabel("File Extension (-e):")
        extension_label.setMinimumWidth(label_width)
        fd_layout.addWidget(extension_label, row, 0)
        self.fd_extension_input = QLineEdit()
        self.fd_extension_input.setPlaceholderText("e.g., txt or py")
        self.fd_extension_input.setToolTip("輸入要搜尋的檔案副檔名，例如 'txt' 或 'py'。")
        fd_layout.addWidget(self.fd_extension_input, row, 1, 1, 10)
        row += 1

        # Search Type
        type_label = QLabel("Search Type:")
        type_label.setMinimumWidth(label_width)
        fd_layout.addWidget(type_label, row, 0)
        self.fd_type_combobox = QComboBox()
        self.fd_type_combobox.addItem("All (files & directories)")
        self.fd_type_combobox.addItem("Files only (-t f)")
        self.fd_type_combobox.addItem("Directories only (-t d)")
        self.fd_type_combobox.setToolTip("選擇要搜尋的類型：檔案、目錄或兩者。")
        self.fd_type_combobox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.fd_type_combobox.setFixedWidth(200)
        fd_layout.addWidget(self.fd_type_combobox, row, 1)
        fd_layout.setColumnStretch(2, 1)
        row += 1

        # Options
        options_layout = QHBoxLayout()
        self.fd_hidden_checkbox = QCheckBox("Include Hidden Files (--hidden)")
        self.fd_hidden_checkbox.setToolTip("勾選以包含隱藏檔案和目錄。")
        options_layout.addWidget(self.fd_hidden_checkbox)
        self.fd_case_sensitive_checkbox = QCheckBox("Case Sensitive (--case-sensitive)")
        options_layout.addWidget(self.fd_case_sensitive_checkbox)
        options_layout.addStretch(1)
        fd_layout.addLayout(options_layout, row, 0, 1, 12)
        row += 1

        # Search Button
        self.fd_search_button = QPushButton("Search")
        fd_layout.addWidget(self.fd_search_button, row, 0, 1, 12)
        row += 1

        # Results Display
        self.fd_results_display = QTextEdit()
        self.fd_results_display.setReadOnly(True)
        font = QFont("Consolas", 12)
        self.fd_results_display.setFont(font)
        self.fd_results_display.setStyleSheet("background-color: #282c34; color: #abb2bf;")
        fd_layout.addWidget(self.fd_results_display, row, 0, 1, 12)
        row += 1

        self.setLayout(fd_layout)

    def set_search_button_state(self, text, enabled, background_color, text_color):
        self.fd_search_button.setText(text)
        self.fd_search_button.setEnabled(enabled)
        self.fd_search_button.setStyleSheet(f"background-color: {background_color}; color: {text_color}; font-weight: bold;")
