"""
Bat 控制器類 - 連接視圖和模型
"""

import logging
from typing import Optional
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from .bat_model import BatModel
from .bat_view import BatView

logger = logging.getLogger(__name__)


class FileHighlightWorker(QThread):
    """檔案高亮工作線程"""
    
    # 信號定義
    highlight_completed = pyqtSignal(bool, str, str)  # (成功, HTML內容, 錯誤信息)
    
    def __init__(self, model: BatModel, file_path: str, theme: str, 
                 show_line_numbers: bool, show_git_modifications: bool,
                 tab_width: int, wrap_text: bool, language: str, use_cache: bool):
        super().__init__()
        self.model = model
        self.file_path = file_path
        self.theme = theme
        self.show_line_numbers = show_line_numbers
        self.show_git_modifications = show_git_modifications
        self.tab_width = tab_width
        self.wrap_text = wrap_text
        self.language = language if language else None
        self.use_cache = use_cache
    
    def run(self):
        """執行檔案高亮"""
        try:
            success, html_content, error = self.model.highlight_file(
                self.file_path, self.theme, self.show_line_numbers,
                self.show_git_modifications, self.tab_width, self.wrap_text,
                self.language, self.use_cache
            )
            
            self.highlight_completed.emit(success, html_content, error)
            
        except Exception as e:
            logger.error(f"Error in FileHighlightWorker: {e}")
            self.highlight_completed.emit(False, "", str(e))


class TextHighlightWorker(QThread):
    """文本高亮工作線程"""
    
    # 信號定義
    highlight_completed = pyqtSignal(bool, str, str)  # (成功, HTML內容, 錯誤信息)
    
    def __init__(self, model: BatModel, text: str, language: str, theme: str,
                 show_line_numbers: bool, tab_width: int, wrap_text: bool, use_cache: bool):
        super().__init__()
        self.model = model
        self.text = text
        self.language = language
        self.theme = theme
        self.show_line_numbers = show_line_numbers
        self.tab_width = tab_width
        self.wrap_text = wrap_text
        self.use_cache = use_cache
    
    def run(self):
        """執行文本高亮"""
        try:
            success, html_content, error = self.model.highlight_text(
                self.text, self.language, self.theme, self.show_line_numbers,
                self.tab_width, self.wrap_text, self.use_cache
            )
            
            self.highlight_completed.emit(success, html_content, error)
            
        except Exception as e:
            logger.error(f"Error in TextHighlightWorker: {e}")
            self.highlight_completed.emit(False, "", str(e))


class ToolCheckWorker(QThread):
    """工具檢查工作線程"""
    
    # 信號定義
    check_completed = pyqtSignal(bool, str, str)  # (可用, 版本信息, 錯誤信息)
    
    def __init__(self, model: BatModel):
        super().__init__()
        self.model = model
    
    def run(self):
        """執行工具檢查"""
        try:
            available, version, error = self.model.check_bat_availability()
            self.check_completed.emit(available, version, error)
            
        except Exception as e:
            logger.error(f"Error in ToolCheckWorker: {e}")
            self.check_completed.emit(False, "", str(e))


class BatController(QObject):
    """Bat 工具的控制器類"""
    
    def __init__(self, view: BatView, model: BatModel):
        super().__init__()
        self.view = view
        self.model = model
        
        # 工作線程
        self.file_highlight_worker: Optional[FileHighlightWorker] = None
        self.text_highlight_worker: Optional[TextHighlightWorker] = None
        self.tool_check_worker: Optional[ToolCheckWorker] = None
        
        # 連接信號和槽
        self._connect_signals()
        
        # 初始化檢查工具狀態
        self._check_tool_status()
        
        logger.info("BatController initialized")
    
    def _connect_signals(self):
        """連接視圖信號到控制器方法"""
        self.view.file_highlight_requested.connect(self._handle_file_highlight_request)
        self.view.text_highlight_requested.connect(self._handle_text_highlight_request)
        self.view.check_bat_requested.connect(self._handle_check_tool_request)
        self.view.clear_cache_requested.connect(self._handle_clear_cache_request)
    
    def _handle_file_highlight_request(self, file_path: str, theme: str, 
                                     show_line_numbers: bool, show_git_modifications: bool,
                                     tab_width: int, wrap_text: bool, language: str, use_cache: bool):
        """處理檔案高亮請求"""
        try:
            # 停止正在運行的工作線程
            self._stop_file_highlight_worker()
            
            # 創建新的工作線程
            self.file_highlight_worker = FileHighlightWorker(
                self.model, file_path, theme, show_line_numbers,
                show_git_modifications, tab_width, wrap_text, language, use_cache
            )
            
            # 連接信號
            self.file_highlight_worker.highlight_completed.connect(self._on_file_highlight_completed)
            self.file_highlight_worker.finished.connect(self._on_file_highlight_finished)
            
            # 啟動線程
            self.file_highlight_worker.start()
            
            logger.info(f"Started file highlight for: {file_path}")
            
        except Exception as e:
            logger.error(f"Error handling file highlight request: {e}")
            self.view.show_error(f"檔案高亮請求失敗: {str(e)}")
    
    def _handle_text_highlight_request(self, text: str, language: str, theme: str,
                                     show_line_numbers: bool, tab_width: int, 
                                     wrap_text: bool, use_cache: bool):
        """處理文本高亮請求"""
        try:
            # 停止正在運行的工作線程
            self._stop_text_highlight_worker()
            
            # 創建新的工作線程
            self.text_highlight_worker = TextHighlightWorker(
                self.model, text, language, theme, show_line_numbers,
                tab_width, wrap_text, use_cache
            )
            
            # 連接信號
            self.text_highlight_worker.highlight_completed.connect(self._on_text_highlight_completed)
            self.text_highlight_worker.finished.connect(self._on_text_highlight_finished)
            
            # 啟動線程
            self.text_highlight_worker.start()
            
            logger.info(f"Started text highlight with language: {language}")
            
        except Exception as e:
            logger.error(f"Error handling text highlight request: {e}")
            self.view.show_error(f"文本高亮請求失敗: {str(e)}")
    
    def _handle_check_tool_request(self):
        """處理工具檢查請求"""
        try:
            # 停止正在運行的檢查線程
            self._stop_tool_check_worker()
            
            # 創建新的工作線程
            self.tool_check_worker = ToolCheckWorker(self.model)
            
            # 連接信號
            self.tool_check_worker.check_completed.connect(self._on_tool_check_completed)
            self.tool_check_worker.finished.connect(self._on_tool_check_finished)
            
            # 啟動線程
            self.tool_check_worker.start()
            
            logger.info("Started tool check")
            
        except Exception as e:
            logger.error(f"Error handling tool check request: {e}")
            self.view.show_error(f"工具檢查請求失敗: {str(e)}")
    
    def _handle_clear_cache_request(self):
        """處理清除快取請求"""
        try:
            self.model.clear_cache()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            self.view.show_error(f"清除快取失敗: {str(e)}")
    
    def _on_file_highlight_completed(self, success: bool, html_content: str, error: str):
        """檔案高亮完成處理"""
        if success:
            self.view.display_file_content(html_content)
            logger.info(f"File highlight completed successfully ({len(html_content)} chars)")
        else:
            self.view.show_error(f"檔案高亮失敗: {error}")
            logger.error(f"File highlight failed: {error}")
    
    def _on_text_highlight_completed(self, success: bool, html_content: str, error: str):
        """文本高亮完成處理"""
        if success:
            self.view.display_text_content(html_content)
            logger.info(f"Text highlight completed successfully ({len(html_content)} chars)")
        else:
            self.view.show_error(f"文本高亮失敗: {error}")
            logger.error(f"Text highlight failed: {error}")
    
    def _on_tool_check_completed(self, available: bool, version: str, error: str):
        """工具檢查完成處理"""
        self.view.update_tool_status(available, version, error)
        
        if available:
            logger.info(f"Tool check completed: bat available ({version})")
        else:
            logger.warning(f"Tool check completed: bat not available ({error})")
    
    def _on_file_highlight_finished(self):
        """檔案高亮線程結束處理"""
        self.file_highlight_worker = None
    
    def _on_text_highlight_finished(self):
        """文本高亮線程結束處理"""
        self.text_highlight_worker = None
    
    def _on_tool_check_finished(self):
        """工具檢查線程結束處理"""
        self.tool_check_worker = None
    
    def _stop_file_highlight_worker(self):
        """停止檔案高亮工作線程"""
        if self.file_highlight_worker and self.file_highlight_worker.isRunning():
            self.file_highlight_worker.terminate()
            self.file_highlight_worker.wait(3000)  # 等待3秒
            self.file_highlight_worker = None
    
    def _stop_text_highlight_worker(self):
        """停止文本高亮工作線程"""
        if self.text_highlight_worker and self.text_highlight_worker.isRunning():
            self.text_highlight_worker.terminate()
            self.text_highlight_worker.wait(3000)  # 等待3秒
            self.text_highlight_worker = None
    
    def _stop_tool_check_worker(self):
        """停止工具檢查工作線程"""
        if self.tool_check_worker and self.tool_check_worker.isRunning():
            self.tool_check_worker.terminate()
            self.tool_check_worker.wait(3000)  # 等待3秒
            self.tool_check_worker = None
    
    def _check_tool_status(self):
        """初始化檢查工具狀態"""
        self._handle_check_tool_request()
    
    def show_cache_info(self):
        """顯示快取信息"""
        try:
            cache_info = self.model.get_cache_info()
            self.view.show_cache_info_dialog(cache_info)
        except Exception as e:
            logger.error(f"Error showing cache info: {e}")
            self.view.show_error(f"獲取快取信息失敗: {str(e)}")
    
    def cleanup(self):
        """清理資源"""
        try:
            # 停止所有工作線程
            self._stop_file_highlight_worker()
            self._stop_text_highlight_worker()
            self._stop_tool_check_worker()
            
            logger.info("BatController cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during BatController cleanup: {e}")