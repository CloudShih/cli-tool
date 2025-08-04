"""
Pandoc 文檔轉換工具的現代化視圖層
提供直觀的文檔轉換界面
"""

import os
import logging
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QGroupBox, QSplitter, QTabWidget,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

from ui.components.buttons import ModernButton, PrimaryButton, DirectoryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox, ModernTextEdit
from ui.components.indicators import StatusIndicator, LoadingSpinner
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class PandocView(QWidget):
    """Pandoc 工具的現代化視圖"""
    
    # 信號定義
    convert_requested = pyqtSignal(dict)  # 轉換請求信號
    batch_convert_requested = pyqtSignal(list, dict)  # 批量轉換請求信號
    check_pandoc_requested = pyqtSignal()  # 檢查 pandoc 可用性信號
    
    def __init__(self):
        super().__init__()
        self.input_files = []  # 選中的輸入檔案列表
        self.setup_ui()
        self.load_default_settings()
    
    def setup_ui(self):
        """設置現代化 UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題和狀態區域
        self._setup_header(main_layout)
        
        # 主要內容區域使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側：轉換設定面板
        left_panel = self._create_conversion_panel()
        splitter.addWidget(left_panel)
        
        # 右側：輸出和預覽面板
        right_panel = self._create_output_panel()
        splitter.addWidget(right_panel)
        
        # 設定分割比例
        splitter.setStretchFactor(0, 1)  # 左側面板
        splitter.setStretchFactor(1, 1)  # 右側面板
        
        main_layout.addWidget(splitter)
        
        # 底部操作按鈕
        self._setup_action_buttons(main_layout)
        
        self.setLayout(main_layout)
    
    def _setup_header(self, layout):
        """設置標題和狀態區域"""
        header_layout = QHBoxLayout()
        
        # 標題和描述
        title_container = QVBoxLayout()
        title_label = QLabel("文檔轉換工具 (Pandoc)")
        title_label.setProperty("heading", True)
        
        desc_label = QLabel("支援 50+ 種文檔格式互相轉換")
        desc_label.setStyleSheet("color: #666; font-size: 13px;")
        
        title_container.addWidget(title_label)
        title_container.addWidget(desc_label)
        header_layout.addLayout(title_container)
        
        header_layout.addStretch()
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready")
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
    
    def _create_conversion_panel(self) -> QWidget:
        """創建轉換設定面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 檔案選擇區域
        file_group = self._create_file_selection_group()
        layout.addWidget(file_group)
        
        # 格式選擇區域
        format_group = self._create_format_selection_group()
        layout.addWidget(format_group)
        
        # 進階選項區域
        options_group = self._create_options_group()
        layout.addWidget(options_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def _create_file_selection_group(self) -> QGroupBox:
        """創建檔案選擇群組"""
        group = QGroupBox("檔案選擇")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 輸入檔案區域
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("輸入檔案:"))
        
        self.input_files_label = QLabel("未選擇檔案")
        self.input_files_label.setStyleSheet("color: #888; font-style: italic;")
        input_layout.addWidget(self.input_files_label, 1)
        
        self.select_files_btn = ModernButton("選擇檔案")
        self.select_files_btn.clicked.connect(self._select_input_files)
        input_layout.addWidget(self.select_files_btn)
        
        layout.addLayout(input_layout)
        
        # 輸出目錄區域
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("輸出目錄:"))
        
        self.output_dir_input = ModernLineEdit()
        self.output_dir_input.setPlaceholderText("選擇輸出目錄...")
        output_layout.addWidget(self.output_dir_input, 1)
        
        self.select_output_btn = DirectoryButton("瀏覽")
        self.select_output_btn.clicked.connect(self._select_output_directory)
        output_layout.addWidget(self.select_output_btn)
        
        layout.addLayout(output_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_format_selection_group(self) -> QGroupBox:
        """創建格式選擇群組"""
        group = QGroupBox("轉換格式")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # 輸入格式
        layout.addWidget(QLabel("輸入格式:"), 0, 0)
        self.input_format_combo = ModernComboBox()
        self.input_format_combo.addItem("自動檢測", "")
        layout.addWidget(self.input_format_combo, 0, 1)
        
        # 輸出格式
        layout.addWidget(QLabel("輸出格式:"), 1, 0)
        self.output_format_combo = ModernComboBox()
        layout.addWidget(self.output_format_combo, 1, 1)
        
        # Standalone 模式
        self.standalone_check = QCheckBox("生成獨立文檔")
        self.standalone_check.setChecked(True)
        self.standalone_check.setToolTip("包含完整的頭部和樣式信息")
        layout.addWidget(self.standalone_check, 2, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def _create_options_group(self) -> QGroupBox:
        """創建進階選項群組"""
        group = QGroupBox("進階選項")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 自訂模板
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("模板檔案:"))
        
        self.template_input = ModernLineEdit()
        self.template_input.setPlaceholderText("選擇自訂模板 (可選)")
        template_layout.addWidget(self.template_input, 1)
        
        self.select_template_btn = ModernButton("瀏覽")
        self.select_template_btn.clicked.connect(self._select_template_file)
        template_layout.addWidget(self.select_template_btn)
        
        layout.addLayout(template_layout)
        
        # CSS 樣式檔案
        css_layout = QHBoxLayout()
        css_layout.addWidget(QLabel("CSS 樣式:"))
        
        self.css_input = ModernLineEdit()
        self.css_input.setPlaceholderText("選擇 CSS 樣式檔案 (可選)")
        css_layout.addWidget(self.css_input, 1)
        
        self.select_css_btn = ModernButton("瀏覽")
        self.select_css_btn.clicked.connect(self._select_css_file)
        css_layout.addWidget(self.select_css_btn)
        
        layout.addLayout(css_layout)
        
        # 元數據區域
        metadata_label = QLabel("元數據 (每行一個, 格式: key:value):")
        layout.addWidget(metadata_label)
        
        self.metadata_input = ModernTextEdit()
        self.metadata_input.setPlaceholderText("title:我的文檔\nauthor:作者姓名\ndate:2025-01-01")
        self.metadata_input.setMaximumHeight(80)
        layout.addWidget(self.metadata_input)
        
        group.setLayout(layout)
        return group
    
    def _create_output_panel(self) -> QWidget:
        """創建輸出和預覽面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 標籤頁容器
        tab_widget = QTabWidget()
        
        # 轉換輸出標籤頁
        output_tab = QWidget()
        output_layout = QVBoxLayout()
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        output_layout.addWidget(self.progress_bar)
        
        # 輸出文字區域
        self.output_text = ModernTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("轉換輸出將在此顯示...")
        output_layout.addWidget(self.output_text)
        
        output_tab.setLayout(output_layout)
        tab_widget.addTab(output_tab, "轉換輸出")
        
        # 批量轉換結果標籤頁
        batch_tab = QWidget()
        batch_layout = QVBoxLayout()
        
        self.batch_results_text = ModernTextEdit()
        self.batch_results_text.setReadOnly(True)
        self.batch_results_text.setPlaceholderText("批量轉換結果將在此顯示...")
        batch_layout.addWidget(self.batch_results_text)
        
        batch_tab.setLayout(batch_layout)
        tab_widget.addTab(batch_tab, "批量結果")
        
        layout.addWidget(tab_widget)
        panel.setLayout(layout)
        return panel
    
    def _setup_action_buttons(self, layout):
        """設置操作按鈕"""
        button_layout = QHBoxLayout()
        
        # 檢查 Pandoc 可用性
        self.check_pandoc_btn = ModernButton("檢查 Pandoc")
        self.check_pandoc_btn.clicked.connect(self.check_pandoc_requested.emit)
        button_layout.addWidget(self.check_pandoc_btn)
        
        button_layout.addStretch()
        
        # 單個轉換按鈕
        self.convert_btn = PrimaryButton("開始轉換")
        self.convert_btn.clicked.connect(self._request_conversion)
        button_layout.addWidget(self.convert_btn)
        
        # 批量轉換按鈕
        self.batch_convert_btn = ModernButton("批量轉換")
        self.batch_convert_btn.clicked.connect(self._request_batch_conversion)
        button_layout.addWidget(self.batch_convert_btn)
        
        layout.addLayout(button_layout)
    
    def load_default_settings(self):
        """載入預設設定"""
        try:
            # 載入配置中的預設設定
            pandoc_config = config_manager.get_tool_config('pandoc')
            
            if pandoc_config:
                # 設定預設輸出目錄
                default_output = pandoc_config.get('default_output_dir', '')
                if default_output:
                    self.output_dir_input.setText(default_output)
                
                # 設定預設輸出格式
                default_format = pandoc_config.get('default_output_format', 'html')
                self._set_default_output_format(default_format)
            
            logger.info("Loaded default pandoc settings")
            
        except Exception as e:
            logger.warning(f"Could not load default pandoc settings: {e}")
    
    def populate_formats(self, input_formats: Dict[str, str], output_formats: Dict[str, str]):
        """填充格式選擇下拉選單"""
        # 清空現有選項
        self.input_format_combo.clear()
        self.output_format_combo.clear()
        
        # 添加輸入格式 (包含自動檢測選項)
        self.input_format_combo.addItem("自動檢測", "")
        for key, name in input_formats.items():
            self.input_format_combo.addItem(f"{name} (.{key})", key)
        
        # 添加輸出格式
        for key, name in output_formats.items():
            self.output_format_combo.addItem(f"{name} (.{key})", key)
        
        # 設定預設選項
        self._set_default_output_format('html')
    
    def _set_default_output_format(self, format_key: str):
        """設定預設輸出格式"""
        for i in range(self.output_format_combo.count()):
            if self.output_format_combo.itemData(i) == format_key:
                self.output_format_combo.setCurrentIndex(i)
                break
    
    def _select_input_files(self):
        """選擇輸入檔案"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "選擇要轉換的檔案",
            "",
            "所有支援的檔案 (*.md *.html *.docx *.odt *.rtf *.tex *.epub *.rst *.txt);;所有檔案 (*.*)"
        )
        
        if files:
            self.input_files = files
            if len(files) == 1:
                filename = os.path.basename(files[0])
                self.input_files_label.setText(f"已選擇: {filename}")
            else:
                self.input_files_label.setText(f"已選擇 {len(files)} 個檔案")
            
            self.input_files_label.setStyleSheet("color: #333;")
    
    def _select_output_directory(self):
        """選擇輸出目錄"""
        directory = QFileDialog.getExistingDirectory(self, "選擇輸出目錄")
        if directory:
            self.output_dir_input.setText(directory)
    
    def _select_template_file(self):
        """選擇模板檔案"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 Pandoc 模板檔案",
            "",
            "模板檔案 (*.html *.tex *.xml);;所有檔案 (*.*)"
        )
        if file:
            self.template_input.setText(file)
    
    def _select_css_file(self):
        """選擇 CSS 檔案"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 CSS 樣式檔案",
            "",
            "CSS 檔案 (*.css);;所有檔案 (*.*)"
        )
        if file:
            self.css_input.setText(file)
    
    def _request_conversion(self):
        """請求單個轉換"""
        if not self.input_files:
            QMessageBox.warning(self, "警告", "請先選擇要轉換的檔案")
            return
        
        if not self.output_dir_input.text().strip():
            QMessageBox.warning(self, "警告", "請選擇輸出目錄")
            return
        
        # 準備轉換參數
        conversion_params = self._gather_conversion_parameters()
        
        # 如果只有一個檔案，使用單個轉換
        if len(self.input_files) == 1:
            conversion_params['input_file'] = self.input_files[0]
            self.convert_requested.emit(conversion_params)
        else:
            # 多個檔案使用批量轉換
            self.batch_convert_requested.emit(self.input_files, conversion_params)
    
    def _request_batch_conversion(self):
        """請求批量轉換"""
        if not self.input_files:
            QMessageBox.warning(self, "警告", "請先選擇要轉換的檔案")
            return
        
        if not self.output_dir_input.text().strip():
            QMessageBox.warning(self, "警告", "請選擇輸出目錄")
            return
        
        conversion_params = self._gather_conversion_parameters()
        self.batch_convert_requested.emit(self.input_files, conversion_params)
    
    def _gather_conversion_parameters(self) -> dict:
        """收集轉換參數"""
        params = {
            'output_dir': self.output_dir_input.text().strip(),
            'input_format': self.input_format_combo.currentData() or None,
            'output_format': self.output_format_combo.currentData(),
            'standalone': self.standalone_check.isChecked(),
            'template': self.template_input.text().strip() or None,
            'css_file': self.css_input.text().strip() or None,
            'metadata': self._parse_metadata(),
        }
        return params
    
    def _parse_metadata(self) -> Dict[str, str]:
        """解析元數據輸入"""
        metadata = {}
        text = self.metadata_input.toPlainText().strip()
        
        if text:
            for line in text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        return metadata
    
    def show_conversion_progress(self, show: bool):
        """顯示或隱藏轉換進度條"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # 不確定進度
        
        # 禁用/啟用轉換按鈕
        self.convert_btn.setEnabled(not show)
        self.batch_convert_btn.setEnabled(not show)
    
    def update_output_display(self, content: str, is_html: bool = True):
        """更新輸出顯示"""
        if is_html:
            self.output_text.setHtml(content)
        else:
            self.output_text.setPlainText(content)
    
    def update_batch_results_display(self, results: List[tuple]):
        """更新批量轉換結果顯示"""
        html_content = "<h3>批量轉換結果</h3><table border='1' cellpadding='5' cellspacing='0' style='width: 100%;'>"
        html_content += "<tr style='background-color: #f0f0f0;'><th>檔案名稱</th><th>狀態</th><th>訊息</th></tr>"
        
        for filename, success, message in results:
            status_color = "#28a745" if success else "#dc3545"
            status_text = "成功" if success else "失敗"
            
            html_content += f"""
            <tr>
                <td>{filename}</td>
                <td style='color: {status_color}; font-weight: bold;'>{status_text}</td>
                <td>{message}</td>
            </tr>
            """
        
        html_content += "</table>"
        self.batch_results_text.setHtml(html_content)
    
    def update_status(self, status: str, message: str = ""):
        """更新狀態指示器"""
        self.status_indicator.set_status(status, message)