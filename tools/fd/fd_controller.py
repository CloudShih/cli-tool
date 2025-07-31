from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from tools.fd.fd_model import FdModel
from tools.fd.fd_view import FdView
import logging

logger = logging.getLogger(__name__)


class FdSearchWorker(QThread):
    """fd 搜尋工作線程"""
    
    search_started = pyqtSignal()
    search_progress = pyqtSignal(str)  # 進度訊息
    search_completed = pyqtSignal(str, str, bool)  # output, error, success
    
    def __init__(self, model, pattern, path, extension, search_type_index, hidden, case_sensitive):
        super().__init__()
        self.model = model
        self.pattern = pattern
        self.path = path
        self.extension = extension
        self.search_type_index = search_type_index
        self.hidden = hidden
        self.case_sensitive = case_sensitive
    
    def run(self):
        """執行搜尋"""
        try:
            self.search_started.emit()
            
            # 模擬搜尋進度階段
            self.search_progress.emit("建構搜尋命令...")
            self.msleep(200)
            
            self.search_progress.emit("執行 fd 命令...")
            self.msleep(300)
            
            # 執行實際搜尋
            html_output, html_error = self.model.execute_fd_command(
                self.pattern, self.path, self.extension, 
                self.search_type_index, self.hidden, self.case_sensitive
            )
            
            self.search_progress.emit("處理搜尋結果...")
            self.msleep(200)
            
            success = bool(html_output) or not bool(html_error)
            self.search_completed.emit(html_output or "", html_error or "", success)
            
        except Exception as e:
            logger.error(f"Search worker error: {e}")
            self.search_completed.emit("", f"搜尋錯誤: {str(e)}", False)


class FdController:
    def __init__(self, view: FdView, model: FdModel):
        self.view = view
        self.model = model
        self.search_worker = None
        self._connect_signals()

    def _connect_signals(self):
        self.view.fd_search_button.clicked.connect(self._execute_search)
        # DirectoryButton 的信號已經在 view 中連接

    def _execute_search(self):
        """執行搜尋 - 使用工作線程提供進度反饋"""
        pattern = self.view.fd_pattern_input.text().strip()
        path = self.view.fd_path_input.text().strip()
        extension = self.view.fd_extension_input.text().strip()
        search_type_index = self.view.fd_type_combobox.currentIndex()
        hidden = self.view.fd_hidden_checkbox.isChecked()
        case_sensitive = self.view.fd_case_sensitive_checkbox.isChecked()

        if not pattern and not extension:
            self.view.fd_results_display.setPlainText("請輸入搜尋模式或檔案副檔名。")
            self.view.set_search_completed(False, "需要輸入搜尋條件")
            return

        # 停止之前的搜尋（如果有的話）
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()

        # 設置搜尋狀態
        self.view.set_search_button_state("搜尋中...", False)
        self.view.fd_results_display.setPlainText("準備搜尋...\n")
        
        # 創建並啟動搜尋工作線程
        self.search_worker = FdSearchWorker(
            self.model, pattern, path, extension, 
            search_type_index, hidden, case_sensitive
        )
        
        # 連接信號
        self.search_worker.search_started.connect(self._on_search_started)
        self.search_worker.search_progress.connect(self._on_search_progress)
        self.search_worker.search_completed.connect(self._on_search_completed)
        
        # 啟動搜尋
        self.search_worker.start()
        logger.info("Started fd search with enhanced progress feedback")

    def _on_search_started(self):
        """搜尋開始"""
        self.view.fd_results_display.setPlainText("🔍 開始搜尋...\n")
        logger.debug("Search started")

    def _on_search_progress(self, message: str):
        """搜尋進度更新"""
        current_text = self.view.fd_results_display.toPlainText()
        # 更新最後一行或添加新行
        lines = current_text.split('\n')
        if lines and lines[-1].startswith('🔍'):
            lines[-1] = f"🔍 {message}"
        else:
            lines.append(f"🔍 {message}")
        
        self.view.fd_results_display.setPlainText('\n'.join(lines))
        QApplication.processEvents()
        logger.debug(f"Search progress: {message}")

    def _on_search_completed(self, html_output: str, html_error: str, success: bool):
        """搜尋完成"""
        # 清除進度訊息
        self.view.fd_results_display.clear()
        
        if html_output:
            self.view.fd_results_display.append("=== 🎯 搜尋結果 ===\n")
            self.view.fd_results_display.append(html_output)
            
        if html_error:
            self.view.fd_results_display.append("\n=== ⚠️ 錯誤訊息 ===")
            self.view.fd_results_display.append(html_error)
            
        if not html_output and not html_error:
            self.view.fd_results_display.append("❌ 未找到結果或命令執行失敗。")
            self.view.set_search_completed(False, "未找到結果")
        else:
            # 統計結果數量
            result_count = html_output.count('\n') if html_output else 0
            status_message = f"✅ 找到 {result_count} 個結果" if success else "❌ 搜尋出現錯誤"
            self.view.set_search_completed(success, status_message)
            
        logger.info(f"Search completed: success={success}, results={result_count if html_output else 0}")

    def cleanup(self):
        """清理資源"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
            
    # _browse_folder 方法已由 DirectoryButton 組件替代
