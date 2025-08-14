"""
csvkit 視圖類 - 提供 CSV 工具套件的 GUI 界面
包含常用工具的快速操作面板和自定義命令輸入
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QGroupBox, QTabWidget, QFileDialog,
    QScrollArea, QFrame, QProgressBar, QMessageBox, QSplitter,
    QTextBrowser
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import os
from .csvkit_help import show_csvkit_help


class CsvkitView(QWidget):
    """csvkit 視圖類 - CSV 工具套件的 GUI 界面"""
    
    # 信號定義
    execute_in2csv = pyqtSignal(str, str, str, str, list)  # file, format, sheet, encoding, extra_args
    execute_csvcut = pyqtSignal(str, str, str, bool, list)  # file, columns, exclude, names_only, extra_args
    execute_csvgrep = pyqtSignal(str, str, str, bool, bool, list)  # file, pattern, column, regex, invert, extra_args
    execute_csvstat = pyqtSignal(str, str, str, bool, list)  # file, columns, stats, no_inference, extra_args
    execute_csvlook = pyqtSignal(str, int, int, int, list)  # file, max_rows, max_cols, max_width, extra_args
    execute_csvjson = pyqtSignal(str, int, str, bool, list)  # file, indent, key_col, pretty, extra_args
    execute_csvsql = pyqtSignal(str, str, bool, str, list)  # file, query, create_table, db_url, extra_args
    execute_csvjoin = pyqtSignal(str, str, str, str, str, list)  # left_file, right_file, left_col, right_col, join_type, extra_args
    execute_custom = pyqtSignal(str, list)  # tool, args
    get_tool_help = pyqtSignal(str)  # tool
    save_result = pyqtSignal(str, str)  # content, file_type
    
    def __init__(self):
        super().__init__()
        self.current_result = ""
        self.current_file_type = "csv"
        self.setup_ui()
        
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 標題區域
        title_layout = QHBoxLayout()
        
        # 標題
        title_label = QLabel("csvkit - CSV 處理工具套件")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 幫助按鈕
        help_btn = QPushButton("❓ 使用說明")
        help_btn.setMaximumWidth(100)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        help_btn.clicked.connect(self.show_help)
        title_layout.addWidget(help_btn)
        
        layout.addLayout(title_layout)
        
        # 主要分割器 - 垂直分割（上下堆疊）
        main_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(main_splitter)
        
        # 上方控制面板（橫向排列）
        top_panel = self.create_top_control_panel()
        main_splitter.addWidget(top_panel)
        
        # 下方輸出面板（橫向排列）
        bottom_panel = self.create_bottom_output_panel()
        main_splitter.addWidget(bottom_panel)
        
        # 設置分割器比例 - 上方控制，下方輸出（增加輸出區域高度）
        main_splitter.setStretchFactor(0, 1)  # 上方控制面板
        main_splitter.setStretchFactor(1, 3)  # 下方輸出面板（增加高度）
        
        # 底部狀態欄（保留最下方的）
        self.create_status_bar(layout)
    
    def create_top_control_panel(self) -> QWidget:
        """創建上方控制面板（橫向排列）"""
        panel = QWidget()
        layout = QHBoxLayout(panel)  # 改為橫向佈局
        
        # 創建工具標籤頁
        tab_widget = QTabWidget()
        
        # 輸入工具標籤
        input_tab = self.create_input_tools_tab()
        tab_widget.addTab(input_tab, "輸入工具")
        
        # 處理工具標籤
        processing_tab = self.create_processing_tools_tab()
        tab_widget.addTab(processing_tab, "處理工具")
        
        # 輸出分析標籤
        output_tab = self.create_output_tools_tab()
        tab_widget.addTab(output_tab, "輸出/分析")
        
        # 自定義命令標籤
        custom_tab = self.create_custom_command_tab()
        tab_widget.addTab(custom_tab, "自定義命令")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def create_bottom_output_panel(self) -> QWidget:
        """創建下方輸出面板（橫向排列）"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 輸出標題區域
        header_layout = QHBoxLayout()
        result_label = QLabel("輸出：")
        result_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        result_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        header_layout.addWidget(result_label)
        
        header_layout.addStretch()
        
        # 保存按鈕
        self.save_btn = QPushButton("💾 保存結果")
        self.save_btn.setMaximumWidth(120)
        self.save_btn.setEnabled(False)  # 初始禁用
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.save_btn.clicked.connect(self.save_current_result)
        header_layout.addWidget(self.save_btn)
        
        layout.addLayout(header_layout)
        
        # 輸出顯示區域 - 更大的空間
        self.result_display = QTextBrowser()
        self.result_display.setFont(QFont("Consolas", 11))
        self.result_display.setStyleSheet("""
            QTextBrowser {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.result_display)
        
        return panel
    
    def create_control_panel(self) -> QWidget:
        """創建控制面板"""
        panel = QWidget()
        panel.setMaximumWidth(400)
        layout = QVBoxLayout(panel)
        
        # 創建標籤頁
        tab_widget = QTabWidget()
        
        # 輸入工具標籤
        input_tab = self.create_input_tools_tab()
        tab_widget.addTab(input_tab, "輸入工具")
        
        # 處理工具標籤
        processing_tab = self.create_processing_tools_tab()
        tab_widget.addTab(processing_tab, "處理工具")
        
        # 輸出分析標籤
        output_tab = self.create_output_tools_tab()
        tab_widget.addTab(output_tab, "輸出/分析")
        
        # 自定義命令標籤
        custom_tab = self.create_custom_command_tab()
        tab_widget.addTab(custom_tab, "自定義命令")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def create_input_tools_tab(self) -> QWidget:
        """創建輸入工具標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # in2csv 工具組
        in2csv_group = QGroupBox("in2csv - 格式轉換器")
        in2csv_layout = QVBoxLayout(in2csv_group)
        
        # 添加說明文字
        help_text = QLabel("將各種檔案格式轉換為 CSV。支援 Excel、JSON、DBF 等格式。")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        in2csv_layout.addWidget(help_text)
        
        # 文件選擇
        file_layout = QHBoxLayout()
        self.in2csv_file_edit = QLineEdit()
        self.in2csv_file_edit.setPlaceholderText("選擇輸入檔案...")
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(self.browse_input_file)
        file_layout.addWidget(self.in2csv_file_edit)
        file_layout.addWidget(browse_btn)
        in2csv_layout.addLayout(file_layout)
        
        # 格式選擇
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("格式："))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['auto', 'csv', 'dbf', 'fixed', 'geojson', 'json', 'ndjson', 'xls', 'xlsx'])
        format_layout.addWidget(self.format_combo)
        in2csv_layout.addLayout(format_layout)
        
        # Excel 工作表
        sheet_layout = QHBoxLayout()
        sheet_layout.addWidget(QLabel("工作表："))
        self.sheet_edit = QLineEdit()
        self.sheet_edit.setPlaceholderText("工作表名稱（Excel 檔案適用）")
        sheet_layout.addWidget(self.sheet_edit)
        in2csv_layout.addLayout(sheet_layout)
        
        # 編碼
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("編碼："))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems([
            'utf-8', 'utf-8-sig', 'cp950', 'big5', 'gbk', 
            'utf-16', 'latin-1', 'cp1252', 'iso-8859-1'
        ])
        encoding_layout.addWidget(self.encoding_combo)
        in2csv_layout.addLayout(encoding_layout)
        
        # 執行按鈕
        self.in2csv_btn = QPushButton("轉換為 CSV")
        self.in2csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.in2csv_btn.clicked.connect(self.execute_in2csv_command)
        in2csv_layout.addWidget(self.in2csv_btn)
        
        layout.addWidget(in2csv_group)
        layout.addStretch()
        
        return widget
    
    def create_processing_tools_tab(self) -> QWidget:
        """創建處理工具標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # csvcut 工具組
        csvcut_group = QGroupBox("csvcut - 欄位擷取")
        csvcut_layout = QVBoxLayout(csvcut_group)
        
        # 添加說明文字
        help_text = QLabel("提取和重新排序 CSV 檔案的列。可指定列號或列名。")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        csvcut_layout.addWidget(help_text)
        
        # 文件選擇
        file_layout = QHBoxLayout()
        self.csvcut_file_edit = QLineEdit()
        self.csvcut_file_edit.setPlaceholderText("選擇 CSV 檔案...")
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(lambda: self.browse_csv_file(self.csvcut_file_edit))
        file_layout.addWidget(self.csvcut_file_edit)
        file_layout.addWidget(browse_btn)
        csvcut_layout.addLayout(file_layout)
        
        # 列選擇
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(QLabel("欄位："))
        self.columns_edit = QLineEdit()
        self.columns_edit.setPlaceholderText("1,3,5 或 欄位名1,欄位名2")
        columns_layout.addWidget(self.columns_edit)
        csvcut_layout.addLayout(columns_layout)
        
        # 選項
        self.names_only_cb = QCheckBox("僅顯示欄位名稱")
        csvcut_layout.addWidget(self.names_only_cb)
        
        # 執行按鈕
        self.csvcut_btn = QPushButton("擷取欄位")
        self.csvcut_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.csvcut_btn.clicked.connect(self.execute_csvcut_command)
        csvcut_layout.addWidget(self.csvcut_btn)
        
        layout.addWidget(csvcut_group)
        
        # csvgrep 工具組
        csvgrep_group = QGroupBox("csvgrep - 模式搜尋")
        csvgrep_layout = QVBoxLayout(csvgrep_group)
        
        # 添加說明文字
        help_text = QLabel("在 CSV 檔案中搜索符合模式的行。支援正則表達式和反向匹配。")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        csvgrep_layout.addWidget(help_text)
        
        # 文件選擇
        file_layout = QHBoxLayout()
        self.csvgrep_file_edit = QLineEdit()
        self.csvgrep_file_edit.setPlaceholderText("Select CSV file...")
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(lambda: self.browse_csv_file(self.csvgrep_file_edit))
        file_layout.addWidget(self.csvgrep_file_edit)
        file_layout.addWidget(browse_btn)
        csvgrep_layout.addLayout(file_layout)
        
        # 搜索模式
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("搜尋模式："))
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("輸入搜尋模式...")
        pattern_layout.addWidget(self.pattern_edit)
        csvgrep_layout.addLayout(pattern_layout)
        
        # 列選擇
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("欄位："))
        self.grep_column_edit = QLineEdit()
        self.grep_column_edit.setPlaceholderText("欄位名稱或編號")
        column_layout.addWidget(self.grep_column_edit)
        csvgrep_layout.addLayout(column_layout)
        
        # 選項
        options_layout = QHBoxLayout()
        self.regex_cb = QCheckBox("使用正則表達式")
        self.invert_cb = QCheckBox("反向匹配")
        options_layout.addWidget(self.regex_cb)
        options_layout.addWidget(self.invert_cb)
        csvgrep_layout.addLayout(options_layout)
        
        # 執行按鈕
        self.csvgrep_btn = QPushButton("搜尋")
        self.csvgrep_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.csvgrep_btn.clicked.connect(self.execute_csvgrep_command)
        csvgrep_layout.addWidget(self.csvgrep_btn)
        
        layout.addWidget(csvgrep_group)
        layout.addStretch()
        
        return widget
    
    def create_output_tools_tab(self) -> QWidget:
        """創建輸出分析工具標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # csvstat 工具組
        csvstat_group = QGroupBox("csvstat - 統計分析")
        csvstat_layout = QVBoxLayout(csvstat_group)
        
        # 添加說明文字
        help_text = QLabel("計算 CSV 檔案的描述性統計。包括最大值、最小值、平均值等。")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        csvstat_layout.addWidget(help_text)
        
        # 文件選擇
        file_layout = QHBoxLayout()
        self.csvstat_file_edit = QLineEdit()
        self.csvstat_file_edit.setPlaceholderText("Select CSV file...")
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(lambda: self.browse_csv_file(self.csvstat_file_edit))
        file_layout.addWidget(self.csvstat_file_edit)
        file_layout.addWidget(browse_btn)
        csvstat_layout.addLayout(file_layout)
        
        # 列選擇
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(QLabel("欄位："))
        self.stat_columns_edit = QLineEdit()
        self.stat_columns_edit.setPlaceholderText("所有欄位（留空）")
        columns_layout.addWidget(self.stat_columns_edit)
        csvstat_layout.addLayout(columns_layout)
        
        # 執行按鈕
        self.csvstat_btn = QPushButton("計算統計")
        self.csvstat_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.csvstat_btn.clicked.connect(self.execute_csvstat_command)
        csvstat_layout.addWidget(self.csvstat_btn)
        
        layout.addWidget(csvstat_group)
        
        # csvlook 工具組
        csvlook_group = QGroupBox("csvlook - 表格顯示")
        csvlook_layout = QVBoxLayout(csvlook_group)
        
        # 添加說明文字
        help_text = QLabel("以格式化表格方式顯示 CSV 檔案內容。可設置顯示行數和列數限制。")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        csvlook_layout.addWidget(help_text)
        
        # 文件選擇
        file_layout = QHBoxLayout()
        self.csvlook_file_edit = QLineEdit()
        self.csvlook_file_edit.setPlaceholderText("Select CSV file...")
        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(lambda: self.browse_csv_file(self.csvlook_file_edit))
        file_layout.addWidget(self.csvlook_file_edit)
        file_layout.addWidget(browse_btn)
        csvlook_layout.addLayout(file_layout)
        
        # 顯示選項
        options_layout = QGridLayout()
        options_layout.addWidget(QLabel("最大行數："), 0, 0)
        self.max_rows_spin = QSpinBox()
        self.max_rows_spin.setRange(0, 10000)
        self.max_rows_spin.setValue(100)
        options_layout.addWidget(self.max_rows_spin, 0, 1)
        
        options_layout.addWidget(QLabel("最大欄位數："), 1, 0)
        self.max_cols_spin = QSpinBox()
        self.max_cols_spin.setRange(0, 100)
        self.max_cols_spin.setValue(20)
        options_layout.addWidget(self.max_cols_spin, 1, 1)
        
        csvlook_layout.addLayout(options_layout)
        
        # 執行按鈕
        self.csvlook_btn = QPushButton("顯示表格")
        self.csvlook_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.csvlook_btn.clicked.connect(self.execute_csvlook_command)
        csvlook_layout.addWidget(self.csvlook_btn)
        
        layout.addWidget(csvlook_group)
        layout.addStretch()
        
        return widget
    
    def create_custom_command_tab(self) -> QWidget:
        """創建自定義命令標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 工具選擇
        tool_layout = QHBoxLayout()
        tool_layout.addWidget(QLabel("工具："))
        self.tool_combo = QComboBox()
        tool_layout.addWidget(self.tool_combo)
        
        help_btn = QPushButton("說明")
        help_btn.clicked.connect(self.show_tool_help)
        tool_layout.addWidget(help_btn)
        
        layout.addLayout(tool_layout)
        
        # 參數輸入
        args_label = QLabel("參數：")
        layout.addWidget(args_label)
        
        self.args_edit = QTextEdit()
        self.args_edit.setMaximumHeight(100)
        self.args_edit.setPlaceholderText("輸入命令參數，每行一個...")
        layout.addWidget(self.args_edit)
        
        # 執行按鈕
        self.custom_btn = QPushButton("執行自定義命令")
        self.custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        self.custom_btn.clicked.connect(self.execute_custom_command)
        layout.addWidget(self.custom_btn)
        
        layout.addStretch()
        
        return widget
    
    
    def create_status_bar(self, layout):
        """創建狀態欄"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("準備就緒")
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_frame)
    
    def browse_input_file(self):
        """瀏覽輸入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "選擇輸入檔案",
            "",
            "所有支援格式 (*.csv *.xlsx *.xls *.json *.dbf);;資料庫 CSV 檔案 (*.csv);;Excel 檔案 (*.xlsx *.xls);;JSON 檔案 (*.json);;所有檔案 (*)"
        )
        if file_path:
            self.in2csv_file_edit.setText(file_path)
    
    def browse_csv_file(self, line_edit):
        """瀏覽 CSV 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 CSV 檔案",
            "",
            "CSV 檔案 (*.csv);;文字檔案 (*.txt);;所有檔案 (*)"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def execute_in2csv_command(self):
        """執行 in2csv 命令"""
        file_path = self.in2csv_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "Warning", "請選擇一個輸入檔案。")
            return
            
        format_type = self.format_combo.currentText()
        sheet = self.sheet_edit.text().strip() or None
        encoding = self.encoding_combo.currentText()
        
        self.execute_in2csv.emit(file_path, format_type, sheet or "", encoding, [])
    
    def execute_csvcut_command(self):
        """執行 csvcut 命令"""
        file_path = self.csvcut_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "請選擇一個 CSV 檔案。")
            return
            
        columns = self.columns_edit.text().strip() or None
        names_only = self.names_only_cb.isChecked()
        
        self.execute_csvcut.emit(file_path, columns or "", "", names_only, [])
    
    def execute_csvgrep_command(self):
        """執行 csvgrep 命令"""
        file_path = self.csvgrep_file_edit.text().strip()
        pattern = self.pattern_edit.text().strip()
        
        if not file_path:
            QMessageBox.warning(self, "警告", "請選擇一個 CSV 檔案。")
            return
        if not pattern:
            QMessageBox.warning(self, "警告", "請輸入搜索模式。")
            return
            
        column = self.grep_column_edit.text().strip() or None
        regex = self.regex_cb.isChecked()
        invert = self.invert_cb.isChecked()
        
        self.execute_csvgrep.emit(file_path, pattern, column or "", regex, invert, [])
    
    def execute_csvstat_command(self):
        """執行 csvstat 命令"""
        file_path = self.csvstat_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "請選擇一個 CSV 檔案。")
            return
            
        columns = self.stat_columns_edit.text().strip() or None
        
        self.execute_csvstat.emit(file_path, columns or "", "", False, [])
    
    def execute_csvlook_command(self):
        """執行 csvlook 命令"""
        file_path = self.csvlook_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "請選擇一個 CSV 檔案。")
            return
            
        max_rows = self.max_rows_spin.value() if self.max_rows_spin.value() > 0 else None
        max_cols = self.max_cols_spin.value() if self.max_cols_spin.value() > 0 else None
        
        self.execute_csvlook.emit(file_path, max_rows or 0, max_cols or 0, 0, [])
    
    def execute_custom_command(self):
        """執行自定義命令"""
        tool = self.tool_combo.currentText()
        args_text = self.args_edit.toPlainText().strip()
        
        if not tool:
            QMessageBox.warning(self, "警告", "請選擇一個工具。")
            return
            
        args = [arg.strip() for arg in args_text.split('\n') if arg.strip()] if args_text else []
        
        self.execute_custom.emit(tool, args)
    
    def show_tool_help(self):
        """顯示工具幫助"""
        tool = self.tool_combo.currentText()
        if tool:
            self.get_tool_help.emit(tool)
    
    def update_available_tools(self, tools):
        """更新可用工具列表"""
        self.tool_combo.clear()
        self.tool_combo.addItems(sorted(tools.keys()))
    
    def set_status(self, message):
        """設置狀態訊息"""
        self.status_label.setText(message)
    
    def show_progress(self, show=True):
        """顯示或隱藏進度條"""
        if show:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
    
    def display_result(self, output, error=None):
        """顯示執行結果到下方輸出面板"""
        self.result_display.clear()
        
        # 確定文件類型
        file_type = "csv"
        if "json" in output.lower() or output.strip().startswith('{') or output.strip().startswith('['):
            file_type = "json"
        elif output.strip().startswith('<html') or output.strip().startswith('<!DOCTYPE'):
            file_type = "html"
        elif "statistics" in output.lower() or "Type of data:" in output:
            file_type = "txt"
        
        if output:
            # 設置可保存的內容
            self.set_result_for_saving(output, file_type)
            
            # 檢查是否為 HTML 格式
            if output.strip().startswith('<'):
                self.result_display.setHtml(output)
            else:
                # 純文本格式，保持原始格式
                self.result_display.setPlainText(output)
        else:
            # 沒有輸出時禁用保存按鈕
            self.set_result_for_saving("", "csv")
            self.result_display.setPlainText("無可用的輸出內容。")
        
        # 錯誤信息和狀態消息只顯示在底部狀態欄
        if error:
            self.set_status(f"Error: {error}")
        # 不自動顯示成功消息，由控制器決定
    
    def set_buttons_enabled(self, enabled):
        """設置按鈕啟用狀態"""
        buttons = [
            self.in2csv_btn, self.csvcut_btn, self.csvgrep_btn,
            self.csvstat_btn, self.csvlook_btn, self.custom_btn
        ]
        
        for button in buttons:
            button.setEnabled(enabled)
            if not enabled:
                button.setText("處理中...")
            else:
                # 恢復原始文本
                if button == self.in2csv_btn:
                    button.setText("轉換為 CSV")
                elif button == self.csvcut_btn:
                    button.setText("擷取欄位")
                elif button == self.csvgrep_btn:
                    button.setText("搜尋")
                elif button == self.csvstat_btn:
                    button.setText("計算統計")
                elif button == self.csvlook_btn:
                    button.setText("顯示表格")
                elif button == self.custom_btn:
                    button.setText("執行自定義命令")
    
    def show_help(self):
        """顯示幫助對話框"""
        show_csvkit_help(self)
    
    def save_current_result(self):
        """保存當前結果"""
        if not self.current_result:
            QMessageBox.warning(self, "警告", "沒有可保存的結果。")
            return
        
        self.save_result.emit(self.current_result, self.current_file_type)
    
    def set_result_for_saving(self, content: str, file_type: str = "csv"):
        """設置要保存的結果內容"""
        self.current_result = content
        self.current_file_type = file_type
        self.save_btn.setEnabled(bool(content.strip()))
    
    def display_system_response(self, message: str, is_error: bool = False):
        """顯示系統回應消息到狀態欄"""
        if is_error:
            self.set_status(f"Error: {message}")
        else:
            self.set_status(message)