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
        
        # 設定分割比例 (左側:右側 = 2:3，給右側更多空間顯示使用說明)
        splitter.setStretchFactor(0, 2)  # 左側面板
        splitter.setStretchFactor(1, 3)  # 右側面板
        
        # 設定初始分割尺寸
        splitter.setSizes([400, 600])  # 左側 400px，右側 600px
        
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
        
        # 使用說明標籤頁
        help_tab = QWidget()
        help_layout = QVBoxLayout()
        
        # 創建可滾動的說明文本區域
        help_scroll = QScrollArea()
        help_scroll.setWidgetResizable(True)
        help_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        help_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        help_content = QWidget()
        help_content_layout = QVBoxLayout()
        
        # 使用說明內容
        help_text = self._create_help_content()
        help_content_layout.addWidget(help_text)
        help_content_layout.addStretch()
        
        help_content.setLayout(help_content_layout)
        help_scroll.setWidget(help_content)
        
        help_layout.addWidget(help_scroll)
        help_tab.setLayout(help_layout)
        tab_widget.addTab(help_tab, "使用說明")
        
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
            "Markdown (*.md *.markdown);;HTML (*.html *.htm);;Word 文檔 (*.docx);;OpenDocument (*.odt);;Rich Text (*.rtf);;LaTeX (*.tex *.latex);;EPUB (*.epub);;reStructuredText (*.rst);;純文字 (*.txt);;所有支援的檔案 (*.md *.html *.docx *.odt *.rtf *.tex *.epub *.rst *.txt);;所有檔案 (*.*)"
        )
        
        if files:
            # 檢查是否有不支援的格式
            unsupported_files = []
            supported_files = []
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext == '.pdf':
                    unsupported_files.append(file)
                else:
                    supported_files.append(file)
            
            # 如果有不支援的 PDF 檔案，顯示警告
            if unsupported_files:
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("格式不支援")
                msg.setText("⚠️ 發現不支援的檔案格式")
                
                pdf_files = [os.path.basename(f) for f in unsupported_files if f.endswith('.pdf')]
                if pdf_files:
                    detailed_msg = f"以下 PDF 檔案無法使用 Pandoc 轉換:\n\n"
                    detailed_msg += "\n".join(f"• {f}" for f in pdf_files[:5])  # 只顯示前5個
                    if len(pdf_files) > 5:
                        detailed_msg += f"\n... 以及其他 {len(pdf_files) - 5} 個檔案"
                    
                    detailed_msg += "\n\n💡 建議替代方案:\n"
                    detailed_msg += "• 使用本工具的 Poppler 功能轉換 PDF 為文字\n"
                    detailed_msg += "• 使用其他 PDF 文字提取工具\n"
                    detailed_msg += "• 先將 PDF 轉為 Word 格式再使用 Pandoc"
                    
                    msg.setDetailedText(detailed_msg)
                
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            
            # 只保留支援的檔案
            if supported_files:
                self.input_files = supported_files
                if len(supported_files) == 1:
                    filename = os.path.basename(supported_files[0])
                    self.input_files_label.setText(f"已選擇: {filename}")
                else:
                    self.input_files_label.setText(f"已選擇 {len(supported_files)} 個檔案")
                
                self.input_files_label.setStyleSheet("color: #333;")
            else:
                # 所有檔案都不支援
                self.input_files = []
                self.input_files_label.setText("請選擇支援的檔案格式")
                self.input_files_label.setStyleSheet("color: #d32f2f;")
    
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
    
    def _create_help_content(self) -> QWidget:
        """創建使用說明內容"""
        from ui.components.inputs import ModernTextEdit
        
        help_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 使用 ModernTextEdit 來顯示 HTML 內容
        help_text = ModernTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml(self._get_help_html_content())
        
        # 設定字體大小以提升可讀性
        font = help_text.font()
        font.setPointSize(10)  # 略微增大字體
        help_text.setFont(font)
        
        layout.addWidget(help_text)
        help_widget.setLayout(layout)
        return help_widget
    
    def _get_help_html_content(self) -> str:
        """獲取使用說明的 HTML 內容"""
        return """
        <div style='font-family: "Microsoft YaHei", sans-serif; margin: 20px; font-size: 14px;'>
            <h2 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px;'>
                🔧 Pandoc 進階選項使用指南
            </h2>
            
            <p style='color: #7f8c8d; margin-bottom: 25px;'>
                Pandoc 工具提供了三個主要的進階選項，幫助您創建專業級的文檔輸出。
            </p>
            
            <h3 style='color: #e74c3c; margin-top: 30px;'>📄 1. 自訂模板檔案</h3>
            <div style='background: #fff5f5; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;'>
                <p><b>用途：</b>控制輸出文檔的結構和格式</p>
                <p><b>使用方法：</b></p>
                <ul>
                    <li>點擊「瀏覽」按鈕選擇模板檔案</li>
                    <li>支援 HTML、LaTeX、Word 等模板格式</li>
                </ul>
                <p><b>應用場景：</b></p>
                <ul>
                    <li>學術論文 → IEEE/ACM 模板</li>
                    <li>公司報告 → 企業品牌模板</li>
                    <li>個人部落格 → 自製 HTML 模板</li>
                </ul>
            </div>
            
            <h3 style='color: #f39c12; margin-top: 30px;'>🎨 2. CSS 樣式檔案</h3>
            <div style='background: #fffaf0; border-left: 4px solid #f39c12; padding: 15px; margin: 15px 0;'>
                <p><b>用途：</b>為 HTML 輸出添加視覺樣式</p>
                <p><b>使用方法：</b></p>
                <ul>
                    <li>點擊「瀏覽」按鈕選擇 .css 檔案</li>
                    <li>僅在輸出格式為 HTML 時有效</li>
                </ul>
                <p><b>功能：</b>控制字體、顏色、間距、響應式設計</p>
            </div>
            
            <h3 style='color: #27ae60; margin-top: 30px;'>📋 3. 元數據設定</h3>
            <div style='background: #f0fff4; border-left: 4px solid #27ae60; padding: 15px; margin: 15px 0;'>
                <p><b>用途：</b>為文檔添加標題、作者、日期等資訊</p>
                <p><b>格式：</b>每行一個 key:value 配對</p>
                
                <table style='width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px;'>
                    <tr style='background: #ecf0f1;'>
                        <th style='border: 1px solid #bdc3c7; padding: 6px;'>欄位</th>
                        <th style='border: 1px solid #bdc3c7; padding: 6px;'>說明</th>
                        <th style='border: 1px solid #bdc3c7; padding: 6px;'>範例</th>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>title</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>文檔標題</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>title:我的報告</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>author</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>作者姓名</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>author:張三</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>date</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>創建日期</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>date:2025-01-04</td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>keywords</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>關鍵字</td>
                        <td style='border: 1px solid #bdc3c7; padding: 6px;'>keywords:AI, Python</td>
                    </tr>
                </table>
                
                <p><b>範例輸入：</b></p>
                <pre style='background: #2c3e50; color: white; padding: 10px; border-radius: 4px; font-size: 12px;'>title:CLI工具使用手冊
author:開發團隊
date:2025-01-04
keywords:CLI, 工具, 文檔轉換</pre>
            </div>
            
            <h3 style='color: #8e44ad; margin-top: 30px;'>💡 實用組合範例</h3>
            
            <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #495057;'>📊 專業報告</h4>
                <ul>
                    <li><b>格式：</b>PDF</li>
                    <li><b>模板：</b>公司 LaTeX 模板</li>
                    <li><b>元數據：</b>title:季度報告, author:財務部</li>
                </ul>
            </div>
            
            <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #495057;'>🌐 部落格文章</h4>
                <ul>
                    <li><b>格式：</b>HTML</li>
                    <li><b>CSS：</b>響應式樣式表</li>
                    <li><b>元數據：</b>title:技術教學, author:技術團隊</li>
                </ul>
            </div>
            
            <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #495057;'>📖 學術論文</h4>
                <ul>
                    <li><b>格式：</b>PDF</li>
                    <li><b>模板：</b>IEEE 會議模板</li>
                    <li><b>元數據：</b>title:研究論文, author:研究員</li>
                </ul>
            </div>
            
            <div style='background: #e8f6fd; border: 1px solid #bee5eb; border-radius: 6px; padding: 15px; margin: 20px 0;'>
                <h4 style='margin-top: 0; color: #0c5460;'>🚀 進階技巧</h4>
                <ol>
                    <li>模板變數：使用 $title$、$author$ 引用元數據</li>
                    <li>條件輸出：模板可根據元數據動態調整</li>
                    <li>多語言支援：透過 lang 設定語言格式</li>
                    <li>PDF 中文：系統自動配置 XeLaTeX 和中文字體</li>
                </ol>
            </div>
            
            <p style='text-align: center; color: #6c757d; font-style: italic; margin-top: 30px;'>
                💡 提示：所有進階選項都是可選的，可根據需要靈活組合使用
            </p>
        </div>
        """