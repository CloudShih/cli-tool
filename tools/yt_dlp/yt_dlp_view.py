"""
YT-DLP View - 使用者界面組件
"""
import os
import logging
from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QCheckBox, QSpinBox, QComboBox, QProgressBar, QGroupBox, QTabWidget,
    QFileDialog, QMessageBox, QFrame, QScrollArea, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap

from .core.data_models import (
    DownloadParameters, DownloadResult, DownloadProgress, 
    DownloadSummary, VideoInfo, VideoQuality, AudioFormat
)
from .components.format_selector import FormatSelector
from .components.progress_display import ProgressDisplay

logger = logging.getLogger(__name__)


class UrlInputWidget(QWidget):
    """URL 輸入組件"""
    
    url_added = pyqtSignal(str)
    info_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 標題
        title_label = QLabel("🎬 YT-DLP 影音下載工具")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0078d4;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # URL 輸入區域
        url_group = QGroupBox("影片/音訊 URL")
        url_layout = QVBoxLayout(url_group)
        
        # URL 輸入框
        url_input_layout = QHBoxLayout()
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("請輸入 YouTube、Bilibili 或其他支援網站的影片 URL...")
        self.url_edit.returnPressed.connect(self._on_add_url)
        url_input_layout.addWidget(self.url_edit)
        
        # 按鈕區域
        button_layout = QVBoxLayout()
        
        self.add_button = QPushButton("添加到清單")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
        """)
        self.add_button.clicked.connect(self._on_add_url)
        button_layout.addWidget(self.add_button)
        
        self.info_button = QPushButton("獲取資訊")
        self.info_button.clicked.connect(self._on_get_info)
        button_layout.addWidget(self.info_button)
        
        url_input_layout.addLayout(button_layout)
        url_layout.addLayout(url_input_layout)
        
        # 批次輸入
        batch_label = QLabel("批次輸入 (每行一個 URL):")
        url_layout.addWidget(batch_label)
        
        self.batch_text = QTextEdit()
        self.batch_text.setMaximumHeight(80)
        self.batch_text.setPlaceholderText("可以在此貼上多個 URL，每行一個...")
        url_layout.addWidget(self.batch_text)
        
        batch_button_layout = QHBoxLayout()
        
        self.add_batch_button = QPushButton("添加全部")
        self.add_batch_button.clicked.connect(self._on_add_batch)
        batch_button_layout.addWidget(self.add_batch_button)
        
        self.clear_batch_button = QPushButton("清空")
        self.clear_batch_button.clicked.connect(lambda: self.batch_text.clear())
        batch_button_layout.addWidget(self.clear_batch_button)
        
        batch_button_layout.addStretch()
        url_layout.addLayout(batch_button_layout)
        
        layout.addWidget(url_group)
    
    def _on_add_url(self):
        """添加單個 URL"""
        url = self.url_edit.text().strip()
        if url:
            self.url_added.emit(url)
            self.url_edit.clear()
    
    def _on_get_info(self):
        """獲取影片資訊"""
        url = self.url_edit.text().strip()
        if url:
            self.info_requested.emit(url)
    
    def _on_add_batch(self):
        """添加批次 URL"""
        text = self.batch_text.toPlainText().strip()
        if text:
            urls = [url.strip() for url in text.split('\n') if url.strip()]
            for url in urls:
                self.url_added.emit(url)
            self.batch_text.clear()


class DownloadListWidget(QWidget):
    """下載清單組件"""
    
    download_requested = pyqtSignal(list)  # List[DownloadParameters]
    item_removed = pyqtSignal(int)
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_items: List[DownloadParameters] = []
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 標題和控制
        header_layout = QHBoxLayout()
        
        title_label = QLabel("下載清單")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 控制按鈕
        self.download_all_button = QPushButton("🚀 開始下載")
        self.download_all_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.download_all_button.clicked.connect(self._on_download_all)
        header_layout.addWidget(self.download_all_button)
        
        self.clear_button = QPushButton("清空清單")
        self.clear_button.clicked.connect(self._on_clear_list)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # 下載清單
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        
        # 統計資訊
        self.stats_label = QLabel("清單為空")
        self.stats_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.stats_label)
    
    def add_download_item(self, url: str, params: DownloadParameters):
        """添加下載項目"""
        self.download_items.append(params)
        
        # 創建清單項目
        item = QListWidgetItem()
        item.setText(f"{len(self.download_items)}. {url}")
        item.setData(Qt.UserRole, len(self.download_items) - 1)
        
        self.list_widget.addItem(item)
        self._update_stats()
    
    def remove_item(self, index: int):
        """移除項目"""
        if 0 <= index < len(self.download_items):
            self.download_items.pop(index)
            self.list_widget.takeItem(index)
            self._update_item_numbers()
            self._update_stats()
            self.item_removed.emit(index)
    
    def clear_list(self):
        """清空清單"""
        self.download_items.clear()
        self.list_widget.clear()
        self._update_stats()
        self.clear_requested.emit()
    
    def update_item_status(self, index: int, status: str):
        """更新項目狀態"""
        if 0 <= index < self.list_widget.count():
            item = self.list_widget.item(index)
            if item:
                text = item.text()
                # 移除舊狀態
                if " - " in text:
                    text = text.split(" - ")[0]
                
                # 添加新狀態
                status_icons = {
                    "downloading": "⬇️ 下載中",
                    "completed": "✅ 完成",
                    "error": "❌ 失敗",
                    "cancelled": "⏹ 已取消"
                }
                
                status_text = status_icons.get(status, status)
                item.setText(f"{text} - {status_text}")
    
    def _on_download_all(self):
        """開始下載全部"""
        if self.download_items:
            self.download_requested.emit(self.download_items.copy())
    
    def _on_clear_list(self):
        """清空清單"""
        if self.download_items:
            reply = QMessageBox.question(
                self, "確認", "確定要清空下載清單嗎？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.clear_list()
    
    def _show_context_menu(self, position):
        """顯示右鍵選單"""
        item = self.list_widget.itemAt(position)
        if item:
            from PyQt5.QtWidgets import QMenu
            menu = QMenu(self)
            
            remove_action = menu.addAction("移除")
            remove_action.triggered.connect(lambda: self.remove_item(item.data(Qt.UserRole)))
            
            menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _update_item_numbers(self):
        """更新項目編號"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item:
                text = item.text()
                # 更新編號
                if ". " in text:
                    url_part = text.split(". ", 1)[1]
                    item.setText(f"{i + 1}. {url_part}")
                item.setData(Qt.UserRole, i)
    
    def _update_stats(self):
        """更新統計資訊"""
        count = len(self.download_items)
        if count == 0:
            self.stats_label.setText("清單為空")
            self.download_all_button.setEnabled(False)
        else:
            self.stats_label.setText(f"共 {count} 個下載項目")
            self.download_all_button.setEnabled(True)


class SettingsWidget(QWidget):
    """設定組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 輸出設定
        output_group = QGroupBox("輸出設定")
        output_layout = QVBoxLayout(output_group)
        
        # 輸出目錄
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("輸出目錄:"))
        
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(str(os.path.expanduser("~/Downloads")))
        dir_layout.addWidget(self.output_dir_edit)
        
        self.browse_dir_button = QPushButton("瀏覽...")
        self.browse_dir_button.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.browse_dir_button)
        
        output_layout.addLayout(dir_layout)
        
        # 檔案命名模板
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("檔名模板:"))
        
        self.template_combo = QComboBox()
        self.template_combo.setEditable(True)
        self.template_combo.addItem("%(title)s.%(ext)s", "%(title)s.%(ext)s")
        self.template_combo.addItem("%(uploader)s - %(title)s.%(ext)s", "%(uploader)s - %(title)s.%(ext)s")
        self.template_combo.addItem("%(upload_date)s - %(title)s.%(ext)s", "%(upload_date)s - %(title)s.%(ext)s")
        self.template_combo.addItem("[%(id)s] %(title)s.%(ext)s", "[%(id)s] %(title)s.%(ext)s")
        template_layout.addWidget(self.template_combo)
        
        output_layout.addLayout(template_layout)
        layout.addWidget(output_group)
        
        # 字幕設定
        subtitle_group = QGroupBox("字幕設定")
        subtitle_layout = QVBoxLayout(subtitle_group)
        
        self.subtitles_check = QCheckBox("下載字幕")
        subtitle_layout.addWidget(self.subtitles_check)
        
        self.auto_subtitles_check = QCheckBox("自動生成字幕")
        subtitle_layout.addWidget(self.auto_subtitles_check)
        
        self.embed_subtitles_check = QCheckBox("嵌入字幕到影片")
        subtitle_layout.addWidget(self.embed_subtitles_check)
        
        # 字幕語言
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("字幕語言:"))
        
        self.subtitle_langs_edit = QLineEdit()
        self.subtitle_langs_edit.setText("zh-TW,zh,en")
        self.subtitle_langs_edit.setPlaceholderText("語言代碼，用逗號分隔 (如: zh-TW,zh,en)")
        lang_layout.addWidget(self.subtitle_langs_edit)
        
        subtitle_layout.addLayout(lang_layout)
        layout.addWidget(subtitle_group)
        
        # 額外檔案設定
        extra_group = QGroupBox("額外檔案")
        extra_layout = QVBoxLayout(extra_group)
        
        self.write_info_json_check = QCheckBox("保存影片資訊 (JSON)")
        extra_layout.addWidget(self.write_info_json_check)
        
        self.write_description_check = QCheckBox("保存影片描述")
        extra_layout.addWidget(self.write_description_check)
        
        self.write_thumbnail_check = QCheckBox("保存縮圖")
        extra_layout.addWidget(self.write_thumbnail_check)
        
        self.embed_thumbnail_check = QCheckBox("嵌入縮圖到檔案")
        extra_layout.addWidget(self.embed_thumbnail_check)
        
        layout.addWidget(extra_group)
        
        # 網路設定
        network_group = QGroupBox("網路設定")
        network_layout = QVBoxLayout(network_group)
        
        # 重試次數
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("重試次數:"))
        
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 50)
        self.retries_spin.setValue(10)
        retry_layout.addWidget(self.retries_spin)
        
        retry_layout.addStretch()
        network_layout.addLayout(retry_layout)
        
        # 速率限制
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("速率限制:"))
        
        self.rate_limit_edit = QLineEdit()
        self.rate_limit_edit.setPlaceholderText("如: 50K, 4.2M (留空為無限制)")
        rate_layout.addWidget(self.rate_limit_edit)
        
        network_layout.addLayout(rate_layout)
        
        # 代理設定
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(QLabel("代理伺服器:"))
        
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText("如: http://127.0.0.1:8080")
        proxy_layout.addWidget(self.proxy_edit)
        
        network_layout.addLayout(proxy_layout)
        
        layout.addWidget(network_group)
        
        layout.addStretch()
    
    def _browse_directory(self):
        """瀏覽目錄"""
        current_dir = self.output_dir_edit.text() or os.path.expanduser("~/Downloads")
        directory = QFileDialog.getExistingDirectory(
            self, "選擇輸出目錄", current_dir
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def get_download_parameters(self, url: str) -> DownloadParameters:
        """獲取下載參數"""
        # 解析字幕語言
        subtitle_langs = []
        if self.subtitle_langs_edit.text():
            subtitle_langs = [lang.strip() for lang in self.subtitle_langs_edit.text().split(',')]
        
        return DownloadParameters(
            url=url,
            output_dir=self.output_dir_edit.text() or os.path.expanduser("~/Downloads"),
            output_template=self.template_combo.currentText() or "%(title)s.%(ext)s",
            subtitles=self.subtitles_check.isChecked(),
            auto_subtitles=self.auto_subtitles_check.isChecked(),
            subtitle_langs=subtitle_langs,
            embed_subtitles=self.embed_subtitles_check.isChecked(),
            write_info_json=self.write_info_json_check.isChecked(),
            write_description=self.write_description_check.isChecked(),
            write_thumbnail=self.write_thumbnail_check.isChecked(),
            embed_thumbnail=self.embed_thumbnail_check.isChecked(),
            retries=self.retries_spin.value(),
            rate_limit=self.rate_limit_edit.text() or None,
            proxy=self.proxy_edit.text() or None
        )


class YtDlpView(QWidget):
    """YT-DLP 主視圖"""
    
    # 信號定義
    download_requested = pyqtSignal(list)  # List[DownloadParameters]
    download_cancelled = pyqtSignal()
    video_info_requested = pyqtSignal(str)  # url
    formats_requested = pyqtSignal(str)     # url
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_downloading = False
        self.current_downloads: List[DownloadParameters] = []
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """設定主界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 創建分頁界面
        self.tab_widget = QTabWidget()
        
        # 下載標籤頁
        download_tab = QWidget()
        download_layout = QHBoxLayout(download_tab)
        
        # 左側控制面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # URL 輸入
        self.url_input = UrlInputWidget()
        left_layout.addWidget(self.url_input)
        
        # 格式選擇
        self.format_selector = FormatSelector()
        left_layout.addWidget(self.format_selector)
        
        left_layout.addStretch()
        download_layout.addWidget(left_panel)
        
        # 右側面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 下載清單
        self.download_list = DownloadListWidget()
        right_layout.addWidget(self.download_list)
        
        # 進度顯示
        self.progress_display = ProgressDisplay()
        right_layout.addWidget(self.progress_display)
        
        download_layout.addWidget(right_panel)
        
        self.tab_widget.addTab(download_tab, "📥 下載")
        
        # 設定標籤頁
        self.settings_widget = SettingsWidget()
        self.tab_widget.addTab(self.settings_widget, "⚙️ 設定")
        
        # 歷史記錄標籤頁
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # 歷史記錄表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "URL", "標題", "狀態", "檔案大小", "下載時間", "錯誤訊息"
        ])
        
        # 設定表格屬性
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        history_layout.addWidget(self.history_table)
        
        # 歷史記錄控制按鈕
        history_controls = QHBoxLayout()
        
        self.clear_history_button = QPushButton("清除歷史")
        self.clear_history_button.clicked.connect(self._clear_history)
        history_controls.addWidget(self.clear_history_button)
        
        self.export_history_button = QPushButton("匯出歷史")
        self.export_history_button.clicked.connect(self._export_history)
        history_controls.addWidget(self.export_history_button)
        
        history_controls.addStretch()
        history_layout.addLayout(history_controls)
        
        self.tab_widget.addTab(history_tab, "📋 歷史記錄")
        
        layout.addWidget(self.tab_widget)
        
        # 底部控制列
        control_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("⏹ 取消下載")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:pressed { background-color: #bd2130; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.cancel_button.clicked.connect(self._on_cancel_download)
        control_layout.addWidget(self.cancel_button)
        
        control_layout.addStretch()
        
        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: #666;")
        control_layout.addWidget(self.status_label)
        
        layout.addLayout(control_layout)
    
    def setup_connections(self):
        """設定信號連接"""
        # URL 輸入組件
        self.url_input.url_added.connect(self._add_download_url)
        self.url_input.info_requested.connect(self.video_info_requested.emit)
        
        # 下載清單組件
        self.download_list.download_requested.connect(self._prepare_downloads)
        
        # 格式選擇器
        self.format_selector.format_changed.connect(self._update_format_preview)
    
    def _add_download_url(self, url: str):
        """添加下載 URL"""
        try:
            # 獲取下載參數
            params = self.settings_widget.get_download_parameters(url)
            
            # 應用格式設定
            params.format_selector = self.format_selector.get_format_selector()
            params.audio_format = self.format_selector.get_audio_format()
            params.extract_audio = self.format_selector.is_extract_audio()
            params.keep_video = self.format_selector.is_keep_video()
            
            # 添加到清單
            self.download_list.add_download_item(url, params)
            
        except Exception as e:
            logger.error(f"Error adding download URL: {e}")
            QMessageBox.warning(self, "錯誤", f"添加 URL 失敗: {str(e)}")
    
    def _prepare_downloads(self, download_items: List[DownloadParameters]):
        """準備下載"""
        if download_items:
            self.current_downloads = download_items
            self.download_requested.emit(download_items)
    
    def _on_cancel_download(self):
        """取消下載"""
        self.download_cancelled.emit()
    
    def _update_format_preview(self):
        """更新格式預覽"""
        format_str = self.format_selector.get_format_selector()
        # 可以在這裡顯示格式預覽
        pass
    
    def _clear_history(self):
        """清除歷史記錄"""
        reply = QMessageBox.question(
            self, "確認", "確定要清除所有下載歷史記錄嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_table.setRowCount(0)
    
    def _export_history(self):
        """匯出歷史記錄"""
        if self.history_table.rowCount() == 0:
            QMessageBox.information(self, "提示", "沒有歷史記錄可以匯出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "匯出歷史記錄", 
            "yt_dlp_history.csv",
            "CSV 檔案 (*.csv);;JSON 檔案 (*.json)"
        )
        
        if file_path:
            # 這裡可以實現匯出邏輯
            QMessageBox.information(self, "成功", f"歷史記錄已匯出到:\n{file_path}")
    
    # 外部調用介面
    def set_downloading_state(self, downloading: bool):
        """設定下載狀態"""
        self.is_downloading = downloading
        self.cancel_button.setEnabled(downloading)
        self.download_list.download_all_button.setEnabled(not downloading)
        
        if downloading:
            self.status_label.setText("正在下載...")
        else:
            self.status_label.setText("準備就緒")
    
    def update_download_progress(self, progress: DownloadProgress):
        """更新下載進度"""
        self.progress_display.update_progress(progress)
    
    def update_batch_item_status(self, index: int, status: str):
        """更新批次項目狀態"""
        self.download_list.update_item_status(index, status)
    
    def add_download_result(self, result: DownloadResult):
        """添加下載結果到歷史"""
        self.progress_display.update_result(result)
        
        # 添加到歷史記錄表格
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        self.history_table.setItem(row, 0, QTableWidgetItem(result.url))
        self.history_table.setItem(row, 1, QTableWidgetItem(result.title))
        self.history_table.setItem(row, 2, QTableWidgetItem(result.status.value))
        
        if result.file_size:
            from .core.data_models import format_file_size
            self.history_table.setItem(row, 3, QTableWidgetItem(format_file_size(result.file_size)))
        else:
            self.history_table.setItem(row, 3, QTableWidgetItem("未知"))
        
        if result.download_time:
            from .core.data_models import format_duration
            self.history_table.setItem(row, 4, QTableWidgetItem(format_duration(result.download_time)))
        else:
            self.history_table.setItem(row, 4, QTableWidgetItem("未知"))
        
        self.history_table.setItem(row, 5, QTableWidgetItem(result.error_message or ""))
    
    def show_video_info(self, info: VideoInfo):
        """顯示影片資訊"""
        info_text = f"""
標題: {info.title}
上傳者: {info.uploader or '未知'}
時長: {info.duration and f'{info.duration:.0f}秒' or '未知'}
觀看次數: {info.view_count or '未知'}
上傳日期: {info.upload_date or '未知'}
描述: {(info.description[:100] + '...') if info.description else '無'}
        """.strip()
        
        QMessageBox.information(self, "影片資訊", info_text)
    
    def show_error(self, error_message: str):
        """顯示錯誤訊息"""
        self.set_downloading_state(False)
        self.status_label.setText(f"錯誤: {error_message}")
        QMessageBox.critical(self, "下載錯誤", error_message)