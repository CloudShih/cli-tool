"""
Ripgrep View - 使用者界面組件
"""
import os
import logging
from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QSpinBox, QComboBox, QProgressBar, QGroupBox, QTabWidget,
    QFileDialog, QMessageBox, QFrame, QScrollArea, QSizePolicy, QCompleter
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QStringListModel
from PyQt5.QtGui import QFont, QIcon, QPalette, QPixmap

from .core.data_models import SearchParameters, FileResult, SearchMatch, SearchSummary

logger = logging.getLogger(__name__)


class SearchParametersWidget(QWidget):
    """搜尋參數設定面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面 - 緊湊設計"""
        layout = QVBoxLayout(self)
        layout.setSpacing(2)  # 最小組件間距
        layout.setContentsMargins(0, 0, 0, 0)  # 移除外部邊距
        
        # 搜尋輸入區域 - 垂直排列
        search_container = QVBoxLayout()
        search_container.setSpacing(3)
        search_container.setContentsMargins(5, 5, 5, 5)
        
        # 標題行
        title_bar = QHBoxLayout()
        title_icon = QLabel("🔍 Ripgrep 文本搜尋")
        title_icon.setStyleSheet("font-size: 14px; font-weight: bold; color: #0078d4;")
        title_bar.addWidget(title_icon)
        title_bar.addStretch()
        search_container.addLayout(title_bar)
        
        # 搜尋模式欄位
        pattern_bar = QHBoxLayout()
        pattern_bar.addWidget(QLabel("搜尋模式:"))
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("輸入搜尋的文字或正則表達式...")
        self.pattern_completer = QCompleter()
        self.pattern_edit.setCompleter(self.pattern_completer)
        pattern_bar.addWidget(self.pattern_edit)
        search_container.addLayout(pattern_bar)
        
        # 搜尋路徑欄位
        path_bar = QHBoxLayout()
        path_bar.addWidget(QLabel("搜尋路徑:"))
        self.path_edit = QLineEdit()
        self.path_edit.setText(".")
        self.path_edit.setPlaceholderText("輸入搜尋的目錄路徑...")
        path_bar.addWidget(self.path_edit)
        
        self.browse_button = QPushButton("瀏覽...")
        self.browse_button.setMaximumWidth(60)
        self.browse_button.clicked.connect(self._browse_directory)
        path_bar.addWidget(self.browse_button)
        search_container.addLayout(path_bar)
        
        # 檔案類型欄位
        file_type_bar = QHBoxLayout()
        file_type_bar.addWidget(QLabel("檔案類型:"))
        self.file_types_edit = QLineEdit()
        self.file_types_edit.setPlaceholderText("例如: *.py,*.js,*.html")
        file_type_bar.addWidget(self.file_types_edit)
        search_container.addLayout(file_type_bar)
        
        layout.addLayout(search_container)
        
        # 第二行：選項區域 - 垂直排列
        options_container = QVBoxLayout()
        options_container.setSpacing(3)
        options_container.setContentsMargins(5, 5, 5, 5)
        
        # 基本選項 - 垂直排列
        self.case_sensitive_check = QCheckBox("區分大小寫")
        options_container.addWidget(self.case_sensitive_check)
        
        self.whole_words_check = QCheckBox("全詞匹配")
        options_container.addWidget(self.whole_words_check)
        
        self.regex_check = QCheckBox("正則表達式")
        self.regex_check.setChecked(True)
        options_container.addWidget(self.regex_check)
        
        # 上下文設定 - 水平排列
        context_bar = QHBoxLayout()
        context_bar.addWidget(QLabel("上下文:"))
        self.context_spin = QSpinBox()
        self.context_spin.setRange(0, 20)
        self.context_spin.setValue(0)
        self.context_spin.setMaximumWidth(50)
        context_bar.addWidget(self.context_spin)
        context_bar.addStretch()
        
        options_container.addLayout(context_bar)
        
        layout.addLayout(options_container)
        
        # 進階選項（摺疊面板）- 預設摺疊，超緊湊
        self.advanced_group = QGroupBox("進階選項")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)  # 預設摺疊以節省空間
        self.advanced_group.setStyleSheet("""
            QGroupBox { font-weight: bold; padding-top: 4px; font-size: 11px; }
            QGroupBox::title { padding: 0 5px; }
        """)
        advanced_layout = QHBoxLayout(self.advanced_group)  # 改為水平佈局
        advanced_layout.setSpacing(5)
        advanced_layout.setContentsMargins(5, 5, 5, 5)
        
        # 隱藏檔案
        self.hidden_files_check = QCheckBox("隱藏檔案")
        advanced_layout.addWidget(self.hidden_files_check)
        
        # 符號連結
        self.follow_symlinks_check = QCheckBox("符號連結")
        advanced_layout.addWidget(self.follow_symlinks_check)
        
        # gitignore
        self.ignore_gitignore_check = QCheckBox("忽略.gitignore")
        advanced_layout.addWidget(self.ignore_gitignore_check)
        
        advanced_layout.addStretch()
        
        # 編碼設定
        advanced_layout.addWidget(QLabel("編碼:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["auto", "utf-8", "big5"])
        self.encoding_combo.setMaximumWidth(60)
        advanced_layout.addWidget(self.encoding_combo)
        
        # 最大結果數
        advanced_layout.addWidget(QLabel("最大:"))
        self.max_count_spin = QSpinBox()
        self.max_count_spin.setRange(-1, 1000)
        self.max_count_spin.setValue(-1)
        self.max_count_spin.setSpecialValueText("無限制")
        self.max_count_spin.setMaximumWidth(70)
        advanced_layout.addWidget(self.max_count_spin)
        
        layout.addWidget(self.advanced_group)
    
    def _browse_directory(self):
        """瀏覽目錄"""
        current_path = self.path_edit.text() or "."
        directory = QFileDialog.getExistingDirectory(
            self, "選擇搜尋目錄", current_path
        )
        if directory:
            self.path_edit.setText(directory)
    
    def get_search_parameters(self) -> SearchParameters:
        """獲取搜尋參數"""
        # 處理檔案類型
        file_types = []
        if self.file_types_edit.text():
            file_types = [t.strip() for t in self.file_types_edit.text().split(',')]
        
        return SearchParameters(
            pattern=self.pattern_edit.text(),
            search_path=self.path_edit.text() or ".",
            case_sensitive=self.case_sensitive_check.isChecked(),
            whole_words=self.whole_words_check.isChecked(),
            regex_mode=self.regex_check.isChecked(),
            context_lines=self.context_spin.value(),
            file_types=file_types,
            # 新增進階選項
            search_hidden=self.hidden_files_check.isChecked(),
            follow_symlinks=self.follow_symlinks_check.isChecked(),
            max_results=self.max_count_spin.value() if self.max_count_spin.value() > 0 else 1000
        )
    
    def set_search_parameters(self, params: SearchParameters):
        """設定搜尋參數"""
        self.pattern_edit.setText(params.pattern)
        self.path_edit.setText(params.search_path)
        self.case_sensitive_check.setChecked(params.case_sensitive)
        self.whole_words_check.setChecked(params.whole_words)
        self.regex_check.setChecked(params.regex_mode)
        self.context_spin.setValue(params.context_lines)
        
        if params.file_types:
            self.file_types_edit.setText(','.join(params.file_types))
    
    def update_search_history(self, history: List[str]):
        """更新搜尋歷史"""
        model = QStringListModel(history)
        self.pattern_completer.setModel(model)


class SearchResultsWidget(QWidget):
    """搜尋結果顯示區域"""
    
    file_selected = pyqtSignal(str, int)  # file_path, line_number
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_results: List[FileResult] = []
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)  # 減少間距
        layout.setContentsMargins(0, 0, 0, 0)  # 移除外部邊距
        
        # 結果摘要
        self.summary_label = QLabel("準備搜尋...")
        self.summary_label.setStyleSheet("font-weight: bold; padding: 3px 5px;")  # 減少 padding
        layout.addWidget(self.summary_label)
        
        # 結果樹狀檢視
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["檔案", "行號", "內容", "匹配數"])
        self.results_tree.setAlternatingRowColors(False)  # 關閉交替行顏色，避免白色背景
        self.results_tree.setRootIsDecorated(True)
        self.results_tree.itemClicked.connect(self._on_item_clicked)
        
        # 設定暗色主題樣式 - 強制覆蓋所有背景色
        self.results_tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #ffffff;
                outline: none;
            }
            QTreeWidget::item {
                background-color: transparent;
                color: #ffffff;
                padding: 2px;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
                color: #ffffff;
            }
            QTreeWidget::item:alternate {
                background-color: transparent;
            }
            QTreeWidget::item:focus {
                background-color: transparent;
                outline: none;
            }
            QTreeWidget QTreeWidgetItem {
                background-color: transparent;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #404040;
                font-weight: bold;
            }
        """)
        
        # 設定欄位寬度
        self.results_tree.setColumnWidth(0, 300)  # 檔案路徑
        self.results_tree.setColumnWidth(1, 80)   # 行號
        self.results_tree.setColumnWidth(2, 400)  # 內容
        self.results_tree.setColumnWidth(3, 80)   # 匹配數
        
        layout.addWidget(self.results_tree)
        
        # 統計資訊
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: gray; font-size: 10px; padding: 2px 5px;")  # 減少 padding
        layout.addWidget(self.stats_label)
    
    def clear_results(self):
        """清空結果"""
        self.search_results.clear()
        self.results_tree.clear()
        self.summary_label.setText("準備搜尋...")
        self.stats_label.setText("")
    
    def add_result(self, file_result: FileResult):
        """添加搜尋結果"""
        self.search_results.append(file_result)
        
        # 創建檔案項目
        file_item = QTreeWidgetItem(self.results_tree)
        file_item.setText(0, file_result.file_path)
        file_item.setText(3, str(file_result.total_matches))
        
        # 設定檔案項目樣式
        font = QFont()
        font.setBold(True)
        file_item.setFont(0, font)
        
        # 添加匹配項目
        for match in file_result.matches:
            match_item = QTreeWidgetItem(file_item)
            match_item.setText(1, str(match.line_number))
            match_item.setText(2, match.content.strip())
            
            # 儲存原始資料用於點擊處理
            match_item.setData(0, Qt.UserRole, {
                'file_path': file_result.file_path,
                'line_number': match.line_number,
                'match': match
            })
        
        # 展開檔案項目
        file_item.setExpanded(True)
        
        # 更新統計
        self._update_statistics()
    
    def update_summary(self, summary: SearchSummary):
        """更新搜尋摘要"""
        status_text = "搜尋完成" if summary.status.name == "COMPLETED" else "搜尋中止"
        
        self.summary_label.setText(
            f"{status_text}: 找到 {summary.total_matches} 個匹配項，"
            f"分佈在 {summary.files_with_matches} 個檔案中 "
            f"(耗時 {summary.search_time:.2f} 秒)"
        )
    
    def update_progress(self, files_scanned: int, matches_found: int):
        """更新搜尋進度"""
        self.summary_label.setText(
            f"搜尋中... 已掃描 {files_scanned} 個檔案，找到 {matches_found} 個匹配項"
        )
    
    def _update_statistics(self):
        """更新統計資訊"""
        total_files = len(self.search_results)
        total_matches = sum(result.total_matches for result in self.search_results)
        
        self.stats_label.setText(
            f"共 {total_files} 個檔案，{total_matches} 個匹配項"
        )
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """處理項目點擊"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.file_selected.emit(data['file_path'], data['line_number'])
    
    def get_selected_file_info(self) -> Optional[Dict[str, Any]]:
        """獲取當前選中的檔案資訊"""
        current_item = self.results_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            return data
        return None


class RipgrepView(QWidget):
    """Ripgrep 主視圖"""
    
    # 信號定義
    search_requested = pyqtSignal(object)  # SearchParameters
    search_cancelled = pyqtSignal()
    export_requested = pyqtSignal(str, str)  # file_path, format
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_searching = False
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """設定主界面 - 緊湊模式"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)  # 零間距
        layout.setContentsMargins(0, 0, 0, 0)  # 零邊距
        
        # 搜尋參數區域 - 緊湊設計
        self.search_params_widget = SearchParametersWidget()
        layout.addWidget(self.search_params_widget)
        
        # 操作按鈕條
        buttons_bar = QHBoxLayout()
        buttons_bar.setSpacing(5)
        buttons_bar.setContentsMargins(5, 3, 5, 3)
        
        self.search_button = QPushButton("🔍 搜尋")
        self.search_button.setMinimumHeight(24)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
                padding: 2px 8px;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        buttons_bar.addWidget(self.search_button)
        
        self.cancel_button = QPushButton("⏹ 取消")
        self.cancel_button.setMinimumHeight(24)
        self.cancel_button.setEnabled(False)
        buttons_bar.addWidget(self.cancel_button)
        
        self.clear_button = QPushButton("🗑 清空")
        self.clear_button.setMinimumHeight(24)
        buttons_bar.addWidget(self.clear_button)
        
        buttons_bar.addStretch()  # 推到右邊
        
        # 匯出按鈕 - 集成到按鈕條
        buttons_bar.addWidget(QLabel("匯出:"))
        
        self.export_json_button = QPushButton("JSON")
        self.export_json_button.setMaximumWidth(50)
        self.export_json_button.setMinimumHeight(22)
        buttons_bar.addWidget(self.export_json_button)
        
        self.export_csv_button = QPushButton("CSV")
        self.export_csv_button.setMaximumWidth(40)
        self.export_csv_button.setMinimumHeight(22)
        buttons_bar.addWidget(self.export_csv_button)
        
        self.export_txt_button = QPushButton("TXT")
        self.export_txt_button.setMaximumWidth(40)
        self.export_txt_button.setMinimumHeight(22)
        buttons_bar.addWidget(self.export_txt_button)
        
        layout.addLayout(buttons_bar)
        
        # 進度條 - 緊湊版
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(4)  # 超薄進度條
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 搜尋結果區域
        self.results_widget = SearchResultsWidget()
        layout.addWidget(self.results_widget)
        
        # 狀態列 - 底部緊湊狀態
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(5, 2, 5, 2)
        
        self.status_label = QLabel("準備就緒")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        status_bar.addWidget(self.status_label)
        
        status_bar.addStretch()
        layout.addLayout(status_bar)
    
    def setup_connections(self):
        """設定信號連接"""
        # 按鈕連接
        self.search_button.clicked.connect(self._on_search_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        
        # 匯出按鈕
        self.export_json_button.clicked.connect(lambda: self._on_export_clicked('json'))
        self.export_csv_button.clicked.connect(lambda: self._on_export_clicked('csv'))
        self.export_txt_button.clicked.connect(lambda: self._on_export_clicked('txt'))
        
        # Enter 鍵搜尋
        self.search_params_widget.pattern_edit.returnPressed.connect(self._on_search_clicked)
    
    def _on_search_clicked(self):
        """搜尋按鈕點擊"""
        try:
            params = self.search_params_widget.get_search_parameters()
            if not params.pattern.strip():
                QMessageBox.warning(self, "警告", "請輸入搜尋模式")
                return
            
            self.search_requested.emit(params)
            
        except Exception as e:
            logger.error(f"Error starting search: {e}")
            QMessageBox.critical(self, "錯誤", f"啟動搜尋失敗: {str(e)}")
    
    def _on_cancel_clicked(self):
        """取消按鈕點擊"""
        self.search_cancelled.emit()
    
    def _on_clear_clicked(self):
        """清空按鈕點擊"""
        self.results_widget.clear_results()
        self.status_label.setText("準備就緒")
    
    def _on_export_clicked(self, format_type: str):
        """匯出按鈕點擊"""
        if not self.results_widget.search_results:
            QMessageBox.information(self, "提示", "沒有搜尋結果可以匯出")
            return
        
        # 選擇檔案
        file_filter = {
            'json': "JSON 檔案 (*.json)",
            'csv': "CSV 檔案 (*.csv)",
            'txt': "文字檔案 (*.txt)"
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"匯出 {format_type.upper()} 檔案", 
            f"ripgrep_results.{format_type}",
            file_filter[format_type]
        )
        
        if file_path:
            self.export_requested.emit(file_path, format_type)
    
    # 外部調用介面
    def set_searching_state(self, searching: bool):
        """設定搜尋狀態"""
        self.is_searching = searching
        self.search_button.setEnabled(not searching)
        self.cancel_button.setEnabled(searching)
        self.progress_bar.setVisible(searching)
        
        if searching:
            self.search_button.setText("🔍 搜尋中...")
            self.status_label.setText("正在執行搜尋...")
        else:
            self.search_button.setText("🔍 開始搜尋")
            self.status_label.setText("準備就緒")
    
    def update_progress(self, files_scanned: int, matches_found: int):
        """更新搜尋進度"""
        self.results_widget.update_progress(files_scanned, matches_found)
        # 簡單的進度指示器 - 基於掃描的檔案數
        if files_scanned > 0:
            self.progress_bar.setValue((files_scanned * 10) % 100)
    
    def add_search_result(self, file_result: FileResult):
        """添加搜尋結果"""
        self.results_widget.add_result(file_result)
    
    def update_search_summary(self, summary: SearchSummary):
        """更新搜尋摘要"""
        self.results_widget.update_summary(summary)
        self.set_searching_state(False)
    
    def show_error(self, error_message: str):
        """顯示錯誤訊息"""
        self.set_searching_state(False)
        self.status_label.setText(f"錯誤: {error_message}")
        QMessageBox.critical(self, "搜尋錯誤", error_message)
    
    def update_search_history(self, history: List[str]):
        """更新搜尋歷史"""
        self.search_params_widget.update_search_history(history)
    
    def show_export_success(self, file_path: str):
        """顯示匯出成功訊息"""
        QMessageBox.information(self, "匯出成功", f"結果已匯出到:\n{file_path}")
    
    def get_search_parameters(self) -> SearchParameters:
        """獲取當前搜尋參數"""
        return self.search_params_widget.get_search_parameters()