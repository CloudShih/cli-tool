"""
Glow Markdown 閱讀器的現代化視圖層
提供直觀的 Markdown 預覽界面
"""

import os
import logging
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QGroupBox, QSplitter, QTabWidget,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit,
    QComboBox, QSlider, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDragEnterEvent, QDropEvent

from ui.components.buttons import ModernButton, PrimaryButton, DirectoryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox, ModernTextEdit
from ui.components.indicators import StatusIndicator, LoadingSpinner
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class GlowView(QWidget):
    """Glow 工具的現代化視圖"""
    
    # 信號定義
    render_requested = pyqtSignal(dict)  # 渲染請求信號
    file_selected = pyqtSignal(str)  # 檔案選擇信號
    url_requested = pyqtSignal(str)  # URL 請求信號
    text_input_requested = pyqtSignal(str)  # 文字輸入請求信號
    check_glow_requested = pyqtSignal()  # 檢查 Glow 可用性信號
    clear_cache_requested = pyqtSignal()  # 清除快取請求信號
    
    def __init__(self):
        super().__init__()
        self.current_source = ""  # 當前來源
        self.current_source_type = "file"  # 當前來源類型
        self.recent_files = []  # 最近檔案列表
        self.setup_ui()
        self.load_settings()
        self.setup_drag_drop()
    
    def setup_ui(self):
        """設置現代化 UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題和狀態區域
        self._setup_header(main_layout)
        
        # 主要內容區域使用分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側：控制面板
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # 右側：預覽面板
        right_panel = self._create_preview_panel()
        splitter.addWidget(right_panel)
        
        # 設定分割比例 (左側:右側 = 2:3，給右側更多空間顯示預覽)
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
        title_label = QLabel("Markdown 閱讀器 (Glow)")
        title_label.setProperty("heading", True)
        
        desc_label = QLabel("美觀的終端 Markdown 預覽工具")
        desc_label.setStyleSheet("color: #666; font-size: 13px;")
        
        title_container.addWidget(title_label)
        title_container.addWidget(desc_label)
        header_layout.addLayout(title_container)
        
        header_layout.addStretch()
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready")
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
    
    def _create_control_panel(self) -> QWidget:
        """創建控制面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 輸入來源選擇區域
        source_group = self._create_source_selection_group()
        layout.addWidget(source_group)
        
        # 顯示選項區域
        display_group = self._create_display_options_group()
        layout.addWidget(display_group)
        
        # 最近檔案區域
        recent_group = self._create_recent_files_group()
        layout.addWidget(recent_group)
        
        # 快取管理區域
        cache_group = self._create_cache_management_group()
        layout.addWidget(cache_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def _create_source_selection_group(self) -> QGroupBox:
        """創建輸入來源選擇群組"""
        group = QGroupBox("輸入來源")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 來源類型選擇標籤頁
        self.source_tabs = QTabWidget()
        
        # 本地檔案標籤頁
        file_tab = self._create_file_tab()
        self.source_tabs.addTab(file_tab, "📄 本地檔案")
        
        # 遠程 URL 標籤頁
        url_tab = self._create_url_tab()
        self.source_tabs.addTab(url_tab, "🌐 遠程 URL")
        
        # 直接輸入標籤頁
        text_tab = self._create_text_tab()
        self.source_tabs.addTab(text_tab, "✏️ 直接輸入")
        
        # 連接標籤頁切換事件
        self.source_tabs.currentChanged.connect(self._on_source_tab_changed)
        
        layout.addWidget(self.source_tabs)
        group.setLayout(layout)
        return group
    
    def _create_file_tab(self) -> QWidget:
        """創建檔案選擇標籤頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 檔案選擇區域
        file_layout = QHBoxLayout()
        
        self.file_path_input = ModernLineEdit()
        self.file_path_input.setPlaceholderText("選擇 Markdown 檔案...")
        self.file_path_input.setReadOnly(True)
        file_layout.addWidget(self.file_path_input, 1)
        
        self.select_file_btn = ModernButton("瀏覽")
        self.select_file_btn.clicked.connect(self._select_file)
        file_layout.addWidget(self.select_file_btn)
        
        layout.addLayout(file_layout)
        
        # 檔案信息顯示
        self.file_info_label = QLabel("未選擇檔案")
        self.file_info_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.file_info_label)
        
        # 拖放提示
        drop_hint = QLabel("💡 提示：可直接拖放 Markdown 檔案到此處")
        drop_hint.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        drop_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(drop_hint)
        
        tab.setLayout(layout)
        return tab
    
    def _create_url_tab(self) -> QWidget:
        """創建 URL 輸入標籤頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # URL 輸入區域
        self.url_input = ModernLineEdit()
        self.url_input.setPlaceholderText("輸入 URL 或 GitHub 快捷方式 (例: user/repo)")
        layout.addWidget(self.url_input)
        
        # GitHub 快捷方式說明
        github_hint = QLabel("""
        <b>支援格式：</b><br>
        • 完整 URL: https://raw.githubusercontent.com/user/repo/main/README.md<br>
        • GitHub 快捷: user/repo (預設載入 README.md)<br>
        • 指定分支: user/repo@branch:path/file.md
        """)
        github_hint.setStyleSheet("color: #666; font-size: 11px; background: #f8f8f8; padding: 8px; border-radius: 4px;")
        github_hint.setWordWrap(True)
        layout.addWidget(github_hint)
        
        tab.setLayout(layout)
        return tab
    
    def _create_text_tab(self) -> QWidget:
        """創建直接文字輸入標籤頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 文字輸入區域
        self.text_input = ModernTextEdit()
        self.text_input.setPlaceholderText("在此直接輸入 Markdown 文字...")
        self.text_input.setMaximumHeight(150)
        layout.addWidget(self.text_input)
        
        # 即時預覽選項
        self.live_preview_check = QCheckBox("即時預覽 (輸入時自動更新)")
        layout.addWidget(self.live_preview_check)
        
        # 設置即時預覽定時器
        self.live_preview_timer = QTimer()
        self.live_preview_timer.setSingleShot(True)
        self.live_preview_timer.timeout.connect(self._on_live_preview_timeout)
        
        # 連接文字變更事件
        self.text_input.textChanged.connect(self._on_text_input_changed)
        
        tab.setLayout(layout)
        return tab
    
    def _create_display_options_group(self) -> QGroupBox:
        """創建顯示選項群組"""
        group = QGroupBox("顯示選項")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # 主題選擇
        layout.addWidget(QLabel("主題:"), 0, 0)
        self.theme_combo = ModernComboBox()
        self.theme_combo.addItem("自動檢測", "auto")
        self.theme_combo.addItem("深色主題", "dark")
        self.theme_combo.addItem("淺色主題", "light")
        self.theme_combo.addItem("粉色主題", "pink")
        self.theme_combo.addItem("Dracula", "dracula")
        self.theme_combo.addItem("無樣式", "notty")
        layout.addWidget(self.theme_combo, 0, 1)
        
        # 寬度設定
        layout.addWidget(QLabel("顯示寬度:"), 1, 0)
        width_layout = QHBoxLayout()
        
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(60, 200)
        self.width_slider.setValue(120)
        self.width_slider.valueChanged.connect(self._on_width_changed)
        width_layout.addWidget(self.width_slider)
        
        self.width_label = QLabel("120")
        self.width_label.setMinimumWidth(30)
        width_layout.addWidget(self.width_label)
        
        width_container = QWidget()
        width_container.setLayout(width_layout)
        layout.addWidget(width_container, 1, 1)
        
        # 快取選項
        self.use_cache_check = QCheckBox("使用快取 (提升重複載入速度)")
        self.use_cache_check.setChecked(True)
        layout.addWidget(self.use_cache_check, 2, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def _create_recent_files_group(self) -> QGroupBox:
        """創建最近檔案群組"""
        group = QGroupBox("最近檔案")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # 最近檔案列表
        self.recent_files_combo = ModernComboBox()
        self.recent_files_combo.setPlaceholderText("選擇最近使用的檔案...")
        self.recent_files_combo.currentTextChanged.connect(self._on_recent_file_selected)
        layout.addWidget(self.recent_files_combo)
        
        # 清除最近檔案按鈕
        self.clear_recent_btn = ModernButton("清除記錄")
        self.clear_recent_btn.clicked.connect(self._clear_recent_files)
        layout.addWidget(self.clear_recent_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_cache_management_group(self) -> QGroupBox:
        """創建快取管理群組"""
        group = QGroupBox("快取管理")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 快取信息顯示
        self.cache_info_label = QLabel("快取信息: 載入中...")
        self.cache_info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.cache_info_label)
        
        # 清除快取按鈕
        self.clear_cache_btn = ModernButton("清除快取")
        self.clear_cache_btn.clicked.connect(self.clear_cache_requested.emit)
        layout.addWidget(self.clear_cache_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_preview_panel(self) -> QWidget:
        """創建預覽面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 標籤頁容器
        tab_widget = QTabWidget()
        
        # Glow 預覽標籤頁
        preview_tab = QWidget()
        preview_layout = QVBoxLayout()
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        preview_layout.addWidget(self.progress_bar)
        
        # 預覽區域
        self.preview_text = ModernTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Markdown 預覽將在此顯示...")
        preview_layout.addWidget(self.preview_text)
        
        preview_tab.setLayout(preview_layout)
        tab_widget.addTab(preview_tab, "📖 Glow 預覽")
        
        # 原始輸出標籤頁
        raw_tab = QWidget()
        raw_layout = QVBoxLayout()
        
        self.raw_output_text = ModernTextEdit()
        self.raw_output_text.setReadOnly(True)
        self.raw_output_text.setPlaceholderText("原始 Glow 輸出將在此顯示...")
        raw_layout.addWidget(self.raw_output_text)
        
        raw_tab.setLayout(raw_layout)
        tab_widget.addTab(raw_tab, "📄 原始輸出")
        
        # 使用說明標籤頁
        help_tab = QWidget()
        help_layout = QVBoxLayout()
        
        # 直接使用 ModernTextEdit，與其他分頁保持一致的結構
        self.help_text = ModernTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setHtml(self._get_help_html_content())
        
        # 設定字體大小以提升可讀性
        font = self.help_text.font()
        font.setPointSize(10)  # 略微增大字體
        self.help_text.setFont(font)
        
        help_layout.addWidget(self.help_text)
        help_tab.setLayout(help_layout)
        tab_widget.addTab(help_tab, "📚 使用說明")
        
        layout.addWidget(tab_widget)
        panel.setLayout(layout)
        return panel
    
    def _setup_action_buttons(self, layout):
        """設置操作按鈕"""
        button_layout = QHBoxLayout()
        
        # 檢查 Glow 可用性
        self.check_glow_btn = ModernButton("檢查 Glow")
        self.check_glow_btn.clicked.connect(self.check_glow_requested.emit)
        button_layout.addWidget(self.check_glow_btn)
        
        # 導出功能按鈕
        self.export_btn = ModernButton("導出 HTML")
        self.export_btn.clicked.connect(self._export_html)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        # 渲染預覽按鈕
        self.render_btn = PrimaryButton("開始預覽")
        self.render_btn.clicked.connect(self._request_render)
        button_layout.addWidget(self.render_btn)
        
        layout.addLayout(button_layout)
    
    def setup_drag_drop(self):
        """設置拖放功能"""
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽進入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                if any(file_path.lower().endswith(ext) for ext in ['.md', '.markdown', '.txt']):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            file_path = urls[0].toLocalFile()
            self._set_file_path(file_path)
            # 切換到檔案標籤頁
            self.source_tabs.setCurrentIndex(0)
            event.acceptProposedAction()
    
    def load_settings(self):
        """載入設定"""
        try:
            glow_config = config_manager.get_tool_config('glow')
            
            if glow_config:
                # 設定預設主題
                default_theme = glow_config.get('default_theme', 'auto')
                self._set_theme_selection(default_theme)
                
                # 設定預設寬度
                default_width = glow_config.get('default_width', 120)
                self.width_slider.setValue(default_width)
                
                # 設定快取選項
                use_cache = glow_config.get('use_cache', True)
                self.use_cache_check.setChecked(use_cache)
                
                # 載入最近檔案
                self.recent_files = glow_config.get('recent_files', [])
                self._update_recent_files_combo()
            
            logger.info("Loaded Glow settings")
            
        except Exception as e:
            logger.warning(f"Could not load Glow settings: {e}")
    
    def _set_theme_selection(self, theme: str):
        """設定主題選擇"""
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme:
                self.theme_combo.setCurrentIndex(i)
                break
    
    def _select_file(self):
        """選擇檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 Markdown 檔案",
            "",
            "Markdown 檔案 (*.md *.markdown *.mdown *.mkd);;文字檔案 (*.txt);;所有檔案 (*.*)"
        )
        
        if file_path:
            self._set_file_path(file_path)
    
    def _set_file_path(self, file_path: str):
        """設定檔案路徑"""
        self.file_path_input.setText(file_path)
        self.current_source = file_path
        self.current_source_type = "file"
        
        # 更新檔案信息
        self._update_file_info(file_path)
        
        # 添加到最近檔案
        self._add_to_recent_files(file_path)
        
        # 發送檔案選擇信號
        self.file_selected.emit(file_path)
    
    def _update_file_info(self, file_path: str):
        """更新檔案信息顯示"""
        try:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                size_mb = file_size / 1024 / 1024
                if size_mb < 1:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{size_mb:.1f} MB"
                
                info_text = f"檔案: {os.path.basename(file_path)} ({size_str})"
                self.file_info_label.setText(info_text)
                self.file_info_label.setStyleSheet("color: #333;")
            else:
                self.file_info_label.setText("檔案不存在")
                self.file_info_label.setStyleSheet("color: #d32f2f;")
        except Exception as e:
            self.file_info_label.setText(f"無法讀取檔案信息: {str(e)}")
            self.file_info_label.setStyleSheet("color: #d32f2f;")
    
    def _add_to_recent_files(self, file_path: str):
        """添加到最近檔案列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # 限制最近檔案數量
        max_recent = 10
        if len(self.recent_files) > max_recent:
            self.recent_files = self.recent_files[:max_recent]
        
        self._update_recent_files_combo()
    
    def _update_recent_files_combo(self):
        """更新最近檔案下拉選單"""
        self.recent_files_combo.clear()
        
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                self.recent_files_combo.addItem(file_name, file_path)
    
    def _on_recent_file_selected(self, file_name: str):
        """最近檔案選擇事件"""
        if file_name:
            file_path = self.recent_files_combo.currentData()
            if file_path:
                self._set_file_path(file_path)
                # 切換到檔案標籤頁
                self.source_tabs.setCurrentIndex(0)
    
    def _clear_recent_files(self):
        """清除最近檔案"""
        self.recent_files.clear()
        self._update_recent_files_combo()
    
    def _on_source_tab_changed(self, index: int):
        """來源標籤頁切換事件"""
        if index == 0:  # 檔案
            self.current_source_type = "file"
        elif index == 1:  # URL
            self.current_source_type = "url"
        elif index == 2:  # 文字
            self.current_source_type = "text"
    
    def _on_width_changed(self, value: int):
        """寬度滑桿變更事件"""
        self.width_label.setText(str(value))
    
    def _on_text_input_changed(self):
        """文字輸入變更事件"""
        if self.live_preview_check.isChecked():
            # 重啟定時器，避免頻繁更新
            self.live_preview_timer.stop()
            self.live_preview_timer.start(1000)  # 1秒延遲
    
    def _on_live_preview_timeout(self):
        """即時預覽超時事件"""
        if self.source_tabs.currentIndex() == 2:  # 文字標籤頁
            self._request_render()
    
    def _request_render(self):
        """請求渲染預覽"""
        # 準備渲染參數
        render_params = {
            'source_type': self.current_source_type,
            'theme': self.theme_combo.currentData(),
            'width': self.width_slider.value(),
            'use_cache': self.use_cache_check.isChecked()
        }
        
        # 根據來源類型設定來源
        if self.current_source_type == "file":
            if not self.file_path_input.text().strip():
                QMessageBox.warning(self, "警告", "請先選擇要預覽的檔案")
                return
            render_params['source'] = self.file_path_input.text().strip()
            
        elif self.current_source_type == "url":
            if not self.url_input.text().strip():
                QMessageBox.warning(self, "警告", "請輸入要預覽的 URL")
                return
            render_params['source'] = self.url_input.text().strip()
            
        elif self.current_source_type == "text":
            text_content = self.text_input.toPlainText().strip()
            if not text_content:
                QMessageBox.warning(self, "警告", "請輸入要預覽的 Markdown 文字")
                return
            render_params['source'] = text_content
        
        # 發送渲染請求信號
        self.render_requested.emit(render_params)
    
    def _export_html(self):
        """導出 HTML"""
        if not hasattr(self, '_last_html_content') or not self._last_html_content:
            QMessageBox.information(self, "提示", "沒有可導出的內容，請先進行預覽")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "導出 HTML 檔案",
            "markdown_preview.html",
            "HTML 檔案 (*.html);;所有檔案 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._last_html_content)
                QMessageBox.information(self, "成功", f"HTML 檔案已導出到:\n{file_path}")
                logger.info(f"HTML exported to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"導出 HTML 時發生錯誤:\n{str(e)}")
                logger.error(f"Failed to export HTML: {e}")
    
    def show_render_progress(self, show: bool):
        """顯示或隱藏渲染進度條"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # 不確定進度
        
        # 禁用/啟用渲染按鈕
        self.render_btn.setEnabled(not show)
        if show:
            self.render_btn.setText("預覽中...")
        else:
            self.render_btn.setText("開始預覽")
    
    def update_preview_display(self, html_content: str, raw_output: str = ""):
        """更新預覽顯示"""
        self.preview_text.setHtml(html_content)
        if raw_output:
            self.raw_output_text.setPlainText(raw_output)
        
        # 保存內容用於導出
        self._last_html_content = html_content
        self.export_btn.setEnabled(True)
    
    def update_cache_info(self, cache_info: Dict):
        """更新快取信息顯示"""
        try:
            count = cache_info.get('count', 0)
            size_mb = cache_info.get('size_mb', 0)
            status = cache_info.get('status', '未知')
            
            info_text = f"快取檔案: {count} 個, 大小: {size_mb} MB, 狀態: {status}"
            self.cache_info_label.setText(info_text)
            
        except Exception as e:
            self.cache_info_label.setText(f"無法獲取快取信息: {str(e)}")
    
    def update_status(self, status: str, message: str = ""):
        """更新狀態指示器"""
        self.status_indicator.set_status(status, message)
    
    def _get_help_html_content(self) -> str:
        """獲取使用說明的 HTML 內容"""
        return """
        <div style='font-family: "Microsoft YaHei", sans-serif; margin: 20px; font-size: 14px;'>
            <h2 style='color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px;'>
                📖 Glow Markdown 閱讀器使用指南
            </h2>
            
            <p style='color: #7f8c8d; margin-bottom: 25px;'>
                Glow 是一個美觀的終端 Markdown 閱讀器，提供高品質的文檔預覽體驗。
            </p>
            
            <h3 style='color: #e74c3c; margin-top: 30px;'>📄 1. 輸入來源</h3>
            <div style='background: #fff5f5; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0;'>
                <p><b>本地檔案：</b></p>
                <ul>
                    <li>點擊「瀏覽」按鈕選擇 Markdown 檔案</li>
                    <li>支援拖放檔案到界面</li>
                    <li>支援格式: .md, .markdown, .txt</li>
                </ul>
                <p><b>遠程 URL：</b></p>
                <ul>
                    <li>完整 URL: https://raw.githubusercontent.com/user/repo/main/README.md</li>
                    <li>GitHub 快捷: user/repo (自動載入 README.md)</li>
                    <li>指定分支和檔案: user/repo@branch:path/file.md</li>
                </ul>
                <p><b>直接輸入：</b></p>
                <ul>
                    <li>在文字框中直接輸入 Markdown 內容</li>
                    <li>支援即時預覽功能</li>
                </ul>
            </div>
            
            <h3 style='color: #f39c12; margin-top: 30px;'>🎨 2. 顯示選項</h3>
            <div style='background: #fffaf0; border-left: 4px solid #f39c12; padding: 15px; margin: 15px 0;'>
                <p><b>主題選擇：</b></p>
                <ul>
                    <li>自動檢測: 根據系統主題自動選擇</li>
                    <li>深色主題: 適合深色環境</li>
                    <li>淺色主題: 適合明亮環境</li>
                    <li>特殊主題: Pink、Dracula 等風格主題</li>
                </ul>
                <p><b>顯示寬度：</b>調整文字換行寬度 (60-200 字符)</p>
                <p><b>快取功能：</b>提升重複載入速度，特別適合遠程內容</p>
            </div>
            
            <h3 style='color: #27ae60; margin-top: 30px;'>📋 3. 功能特色</h3>
            <div style='background: #f0fff4; border-left: 4px solid #27ae60; padding: 15px; margin: 15px 0;'>
                <p><b>預覽模式：</b></p>
                <ul>
                    <li>Glow 預覽: 美觀的樣式化顯示</li>
                    <li>原始輸出: 純文字格式顯示</li>
                    <li>使用說明: 詳細功能介紹</li>
                </ul>
                
                <p><b>便利功能：</b></p>
                <ul>
                    <li>最近檔案記錄</li>
                    <li>拖放檔案支援</li>
                    <li>HTML 導出功能</li>
                    <li>快取管理</li>
                    <li>即時預覽 (文字輸入模式)</li>
                </ul>
            </div>
            
            <h3 style='color: #8e44ad; margin-top: 30px;'>💡 4. 使用技巧</h3>
            
            <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #495057;'>🚀 快速預覽</h4>
                <ul>
                    <li>使用 GitHub 快捷方式快速預覽開源專案文檔</li>
                    <li>啟用快取功能提升重複訪問速度</li>
                    <li>使用拖放功能快速載入本地檔案</li>
                </ul>
            </div>
            
            <div style='background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #495057;'>🎯 效率提升</h4>
                <ul>
                    <li>使用最近檔案快速重新載入</li>
                    <li>調整顯示寬度適應不同螢幕</li>
                    <li>選擇合適主題保護視力</li>
                    <li>導出 HTML 用於分享或存檔</li>
                </ul>
            </div>
            
            <div style='background: #e8f6fd; border: 1px solid #bee5eb; border-radius: 6px; padding: 15px; margin: 20px 0;'>
                <h4 style='margin-top: 0; color: #0c5460;'>⚙️ 系統要求</h4>
                <ol>
                    <li>需要安裝 Glow CLI 工具</li>
                    <li>支援網路連線以載入遠程內容</li>
                    <li>建議使用現代作業系統以獲得最佳體驗</li>
                </ol>
            </div>
            
            <p style='text-align: center; color: #6c757d; font-style: italic; margin-top: 30px;'>
                💡 提示：首次使用前請點擊「檢查 Glow」確認工具已正確安裝
            </p>
        </div>
        """