"""
Bat 視圖類 - PyQt5 用戶界面
"""

import os
import logging
from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QCheckBox, QSpinBox, QPushButton, QTextBrowser, QFileDialog,
    QSplitter, QGroupBox, QGridLayout, QProgressBar, QFrame,
    QTextEdit, QTabWidget, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor

logger = logging.getLogger(__name__)


class BatView(QWidget):
    """Bat 工具的視圖類"""
    
    # 信號定義
    file_highlight_requested = pyqtSignal(str, str, bool, bool, int, bool, str, bool)  # 檔案高亮請求
    text_highlight_requested = pyqtSignal(str, str, str, bool, int, bool, bool)  # 文本高亮請求
    check_bat_requested = pyqtSignal()  # 檢查 bat 工具
    clear_cache_requested = pyqtSignal()  # 清除快取請求
    
    def __init__(self):
        super().__init__()
        self.current_file = ""
        self.recent_files = []
        self.max_recent_files = 10
        
        # 初始化界面
        self.init_ui()
        
        # 設置定時器用於狀態更新
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)  # 每5秒更新一次狀態
        
        logger.info("BatView initialized")
    
    def init_ui(self):
        """初始化用戶界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 創建主要分割器
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # 創建控制面板
        control_panel = self._create_control_panel()
        main_splitter.addWidget(control_panel)
        
        # 創建內容顯示區域
        content_area = self._create_content_area()
        main_splitter.addWidget(content_area)
        
        # 設置分割器比例
        main_splitter.setStretchFactor(0, 0)  # 控制面板固定寬度
        main_splitter.setStretchFactor(1, 1)  # 內容區域可伸縮
        main_splitter.setSizes([350, 800])
        
        # 創建狀態欄
        status_layout = QHBoxLayout()
        self.status_label = QLabel("準備就緒")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
    
    def _create_control_panel(self) -> QWidget:
        """創建控制面板"""
        panel = QWidget()
        panel.setMaximumWidth(350)
        panel.setMinimumWidth(300)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # 文件選擇組
        file_group = QGroupBox("檔案選擇")
        file_layout = QVBoxLayout(file_group)
        
        # 最近檔案下拉框
        file_layout.addWidget(QLabel("最近檔案:"))
        self.recent_files_combo = QComboBox()
        self.recent_files_combo.setEditable(True)
        self.recent_files_combo.currentTextChanged.connect(self._on_recent_file_changed)
        file_layout.addWidget(self.recent_files_combo)
        
        # 檔案選擇按鈕
        file_button_layout = QHBoxLayout()
        self.browse_file_btn = QPushButton("瀏覽檔案...")
        self.browse_file_btn.clicked.connect(self._browse_file)
        file_button_layout.addWidget(self.browse_file_btn)
        
        self.highlight_file_btn = QPushButton("高亮顯示")
        self.highlight_file_btn.clicked.connect(self._request_file_highlight)
        file_button_layout.addWidget(self.highlight_file_btn)
        
        file_layout.addLayout(file_button_layout)
        layout.addWidget(file_group)
        
        # 顯示設定組
        display_group = QGroupBox("顯示設定")
        display_layout = QGridLayout(display_group)
        
        # 主題選擇
        display_layout.addWidget(QLabel("主題:"), 0, 0)
        self.theme_combo = QComboBox()
        self._populate_theme_combo()
        display_layout.addWidget(self.theme_combo, 0, 1)
        
        # 行號顯示
        self.line_numbers_check = QCheckBox("顯示行號")
        self.line_numbers_check.setChecked(True)
        display_layout.addWidget(self.line_numbers_check, 1, 0, 1, 2)
        
        # Git 修改標記
        self.git_modifications_check = QCheckBox("顯示 Git 修改")
        self.git_modifications_check.setChecked(True)
        display_layout.addWidget(self.git_modifications_check, 2, 0, 1, 2)
        
        # Tab 寬度
        display_layout.addWidget(QLabel("Tab 寬度:"), 3, 0)
        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(1, 16)
        self.tab_width_spin.setValue(4)
        display_layout.addWidget(self.tab_width_spin, 3, 1)
        
        # 自動換行
        self.wrap_text_check = QCheckBox("自動換行")
        self.wrap_text_check.setChecked(False)
        display_layout.addWidget(self.wrap_text_check, 4, 0, 1, 2)
        
        # 語言覆蓋
        display_layout.addWidget(QLabel("語言:"), 5, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItem("自動檢測", "")
        self._populate_language_combo()
        display_layout.addWidget(self.language_combo, 5, 1)
        
        layout.addWidget(display_group)
        
        # 快取設定組
        cache_group = QGroupBox("快取設定")
        cache_layout = QVBoxLayout(cache_group)
        
        self.use_cache_check = QCheckBox("啟用快取")
        self.use_cache_check.setChecked(True)
        cache_layout.addWidget(self.use_cache_check)
        
        cache_button_layout = QHBoxLayout()
        self.clear_cache_btn = QPushButton("清除快取")
        self.clear_cache_btn.clicked.connect(self._request_clear_cache)
        cache_button_layout.addWidget(self.clear_cache_btn)
        
        self.cache_info_btn = QPushButton("快取信息")
        self.cache_info_btn.clicked.connect(self._show_cache_info)
        cache_button_layout.addWidget(self.cache_info_btn)
        
        cache_layout.addLayout(cache_button_layout)
        layout.addWidget(cache_group)
        
        # 工具狀態組
        tool_group = QGroupBox("工具狀態")
        tool_layout = QVBoxLayout(tool_group)
        
        self.tool_status_label = QLabel("檢查中...")
        tool_layout.addWidget(self.tool_status_label)
        
        self.check_tool_btn = QPushButton("檢查 bat 工具")
        self.check_tool_btn.clicked.connect(self._request_check_tool)
        tool_layout.addWidget(self.check_tool_btn)
        
        layout.addWidget(tool_group)
        
        # 添加彈性空間
        layout.addStretch()
        
        return panel
    
    def _create_content_area(self) -> QWidget:
        """創建內容顯示區域"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 創建標籤頁
        self.content_tabs = QTabWidget()
        
        # 檔案顯示標籤頁
        self.file_display = QTextBrowser()
        self.file_display.setFont(QFont("Consolas", 11))
        self.content_tabs.addTab(self.file_display, "檔案內容")
        
        # 文本輸入標籤頁
        text_input_widget = QWidget()
        text_layout = QVBoxLayout(text_input_widget)
        
        # 語言選擇和控制按鈕
        text_control_layout = QHBoxLayout()
        text_control_layout.addWidget(QLabel("語言:"))
        
        self.text_language_combo = QComboBox()
        self._populate_text_language_combo()
        text_control_layout.addWidget(self.text_language_combo)
        
        text_control_layout.addStretch()
        
        self.highlight_text_btn = QPushButton("高亮文本")
        self.highlight_text_btn.clicked.connect(self._request_text_highlight)
        text_control_layout.addWidget(self.highlight_text_btn)
        
        text_layout.addLayout(text_control_layout)
        
        # 文本輸入區域
        text_splitter = QSplitter(Qt.Vertical)
        
        self.text_input = QTextEdit()
        self.text_input.setFont(QFont("Consolas", 11))
        self.text_input.setPlaceholderText("在此輸入要高亮顯示的程式碼...")
        text_splitter.addWidget(self.text_input)
        
        self.text_display = QTextBrowser()
        self.text_display.setFont(QFont("Consolas", 11))
        text_splitter.addWidget(self.text_display)
        
        text_splitter.setSizes([200, 400])
        text_layout.addWidget(text_splitter)
        
        self.content_tabs.addTab(text_input_widget, "文本高亮")
        
        layout.addWidget(self.content_tabs)
        
        return content_widget
    
    def _populate_theme_combo(self):
        """填充主題下拉框"""
        themes = [
            ("1337", "1337"),
            ("Coldark-Cold", "Coldark-Cold"), 
            ("Coldark-Dark", "Coldark-Dark"),
            ("DarkNeon", "DarkNeon"),
            ("Dracula", "Dracula"),
            ("GitHub", "GitHub"),
            ("Monokai Extended", "Monokai Extended"),
            ("Monokai Extended Bright", "Monokai Extended Bright"),
            ("Monokai Extended Light", "Monokai Extended Light"),
            ("Monokai Extended Origin", "Monokai Extended Origin"),
            ("Nord", "Nord"),
            ("OneHalfDark", "OneHalfDark"),
            ("OneHalfLight", "OneHalfLight"),
            ("Solarized (dark)", "Solarized (dark)"),
            ("Solarized (light)", "Solarized (light)"),
            ("Sublime Snazzy", "Sublime Snazzy"),
            ("Visual Studio Dark+", "Visual Studio Dark+"),
            ("ansi", "ansi"),
            ("base16", "base16"),
            ("gruvbox-dark", "gruvbox-dark")
        ]
        
        for display_name, value in themes:
            self.theme_combo.addItem(display_name, value)
        
        # 設置預設值
        self._set_theme_selection("Monokai Extended")
    
    def _populate_language_combo(self):
        """填充語言下拉框"""
        common_languages = [
            ("Python", "python"),
            ("JavaScript", "javascript"),
            ("TypeScript", "typescript"),
            ("HTML", "html"),
            ("CSS", "css"),
            ("JSON", "json"),
            ("XML", "xml"),
            ("YAML", "yaml"),
            ("C", "c"),
            ("C++", "cpp"),
            ("Java", "java"),
            ("Go", "go"),
            ("Rust", "rust"),
            ("Ruby", "ruby"),
            ("PHP", "php"),
            ("Shell", "bash"),
            ("PowerShell", "powershell"),
            ("SQL", "sql"),
            ("Markdown", "markdown")
        ]
        
        for display_name, value in common_languages:
            self.language_combo.addItem(display_name, value)
    
    def _populate_text_language_combo(self):
        """填充文本語言下拉框"""
        self.text_language_combo.addItem("Python", "python")
        self.text_language_combo.addItem("JavaScript", "javascript")
        self.text_language_combo.addItem("TypeScript", "typescript")
        self.text_language_combo.addItem("HTML", "html")
        self.text_language_combo.addItem("CSS", "css")
        self.text_language_combo.addItem("JSON", "json")
        self.text_language_combo.addItem("XML", "xml")
        self.text_language_combo.addItem("YAML", "yaml")
        self.text_language_combo.addItem("C", "c")
        self.text_language_combo.addItem("C++", "cpp")
        self.text_language_combo.addItem("Java", "java")
        self.text_language_combo.addItem("Go", "go")
        self.text_language_combo.addItem("Rust", "rust")
        self.text_language_combo.addItem("Ruby", "ruby")
        self.text_language_combo.addItem("PHP", "php")
        self.text_language_combo.addItem("Shell", "bash")
        self.text_language_combo.addItem("PowerShell", "powershell")
        self.text_language_combo.addItem("SQL", "sql")
        self.text_language_combo.addItem("Markdown", "markdown")
    
    def _browse_file(self):
        """瀏覽選擇檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇要高亮顯示的檔案",
            "",
            "所有檔案 (*.*)"
        )
        
        if file_path:
            self._set_file_path(file_path)
    
    def _set_file_path(self, file_path: str):
        """設置檔案路徑"""
        self.current_file = file_path
        self.recent_files_combo.setCurrentText(file_path)
        self._add_to_recent_files(file_path)
        
        # 切換到檔案顯示標籤頁
        self.content_tabs.setCurrentIndex(0)
        
        logger.info(f"File path set: {file_path}")
    
    def _add_to_recent_files(self, file_path: str):
        """添加到最近檔案列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # 保持最大數量限制
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
        
        self._update_recent_files_combo()
    
    def _update_recent_files_combo(self):
        """更新最近檔案下拉框"""
        current_text = self.recent_files_combo.currentText()
        
        self.recent_files_combo.clear()
        
        for file_path in self.recent_files:
            self.recent_files_combo.addItem(os.path.basename(file_path), file_path)
        
        # 如果當前文本不在列表中，添加它
        if current_text and current_text not in self.recent_files:
            self.recent_files_combo.setCurrentText(current_text)
    
    def _on_recent_file_changed(self, file_path: str):
        """最近檔案改變時的處理"""
        if file_path and os.path.exists(file_path):
            self.current_file = file_path
    
    def _request_file_highlight(self):
        """請求檔案高亮"""
        file_path = self.recent_files_combo.currentText().strip()
        if not file_path:
            self._show_message("請選擇要高亮顯示的檔案")
            return
        
        if not os.path.exists(file_path):
            self._show_message(f"檔案不存在: {file_path}")
            return
        
        # 獲取設定
        theme = self.theme_combo.currentData() or "Monokai Extended"
        show_line_numbers = self.line_numbers_check.isChecked()
        show_git_modifications = self.git_modifications_check.isChecked()
        tab_width = self.tab_width_spin.value()
        wrap_text = self.wrap_text_check.isChecked()
        language = self.language_combo.currentData() or ""
        use_cache = self.use_cache_check.isChecked()
        
        # 發送信號
        self.file_highlight_requested.emit(
            file_path, theme, show_line_numbers, show_git_modifications,
            tab_width, wrap_text, language, use_cache
        )
        
        # 更新界面狀態
        self._set_processing_state(True, "正在高亮顯示檔案...")
    
    def _request_text_highlight(self):
        """請求文本高亮"""
        text = self.text_input.toPlainText().strip()
        if not text:
            self._show_message("請輸入要高亮顯示的文本")
            return
        
        # 獲取設定
        language = self.text_language_combo.currentData() or "python"
        theme = self.theme_combo.currentData() or "Monokai Extended"
        show_line_numbers = self.line_numbers_check.isChecked()
        tab_width = self.tab_width_spin.value()
        wrap_text = self.wrap_text_check.isChecked()
        use_cache = self.use_cache_check.isChecked()
        
        # 發送信號
        self.text_highlight_requested.emit(
            text, language, theme, show_line_numbers,
            tab_width, wrap_text, use_cache
        )
        
        # 更新界面狀態
        self._set_processing_state(True, "正在高亮顯示文本...")
    
    def _request_check_tool(self):
        """請求檢查工具"""
        self.check_bat_requested.emit()
        self._set_processing_state(True, "正在檢查 bat 工具...")
    
    def _request_clear_cache(self):
        """請求清除快取"""
        self.clear_cache_requested.emit()
        self._show_message("快取已清除")
    
    def _request_highlight(self):
        """請求高亮（通用方法）"""
        if self.content_tabs.currentIndex() == 0:
            # 檔案高亮
            self._request_file_highlight()
        else:
            # 文本高亮
            self._request_text_highlight()
    
    def _show_cache_info(self):
        """顯示快取信息"""
        # 這個方法將由控制器調用來獲取實際的快取信息
        pass
    
    def _set_theme_selection(self, theme: str):
        """設置主題選擇"""
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme:
                self.theme_combo.setCurrentIndex(i)
                break
    
    def _set_processing_state(self, processing: bool, status_text: str = ""):
        """設置處理狀態"""
        if processing:
            self.progress_bar.setVisible(True)
            self.status_label.setText(status_text)
            
            # 禁用相關按鈕
            self.highlight_file_btn.setEnabled(False)
            self.highlight_text_btn.setEnabled(False)
            self.check_tool_btn.setEnabled(False)
            
        else:
            self.progress_bar.setVisible(False)
            if not status_text:
                self.status_label.setText("準備就緒")
            else:
                self.status_label.setText(status_text)
            
            # 啟用按鈕
            self.highlight_file_btn.setEnabled(True)
            self.highlight_text_btn.setEnabled(True)
            self.check_tool_btn.setEnabled(True)
    
    def _update_status(self):
        """更新狀態"""
        # 定期狀態更新（由定時器調用）
        pass
    
    def _show_message(self, message: str):
        """顯示消息"""
        QMessageBox.information(self, "bat 工具", message)
    
    def display_file_content(self, html_content: str):
        """顯示檔案內容"""
        self.file_display.setHtml(html_content)
        self._set_processing_state(False, f"檔案已顯示 ({len(html_content)} 字符)")
    
    def display_text_content(self, html_content: str):
        """顯示文本內容"""
        self.text_display.setHtml(html_content)
        self._set_processing_state(False, f"文本已高亮 ({len(html_content)} 字符)")
    
    def update_tool_status(self, available: bool, version: str, error: str):
        """更新工具狀態"""
        if available:
            self.tool_status_label.setText(f"✓ bat 可用: {version}")
            self.tool_status_label.setStyleSheet("color: green;")
        else:
            self.tool_status_label.setText(f"✗ bat 不可用: {error}")
            self.tool_status_label.setStyleSheet("color: red;")
        
        self._set_processing_state(False)
    
    def show_cache_info_dialog(self, cache_info: dict):
        """顯示快取信息對話框"""
        info_text = f"""
快取統計信息:

總快取項數: {cache_info.get('total_entries', 0)}
有效快取項: {cache_info.get('valid_entries', 0)}
過期快取項: {cache_info.get('expired_entries', 0)}

快取大小: {cache_info.get('total_size_mb', 0)} MB
最大快取大小: {cache_info.get('max_size_mb', 0)} MB
快取生存時間: {cache_info.get('cache_ttl_seconds', 0)} 秒
        """
        
        QMessageBox.information(self, "快取信息", info_text.strip())
    
    def show_error(self, error_message: str):
        """顯示錯誤消息"""
        self.status_label.setText(f"錯誤: {error_message}")
        self._set_processing_state(False)
        QMessageBox.critical(self, "錯誤", error_message)