"""
Ripgrep Controller - 控制器層，協調模型和視圖
"""
import logging
from typing import Optional
from PyQt5.QtCore import QObject, QTimer

from .ripgrep_model import RipgrepModel
from .ripgrep_view import RipgrepView
from .core.data_models import SearchParameters, FileResult, SearchSummary

logger = logging.getLogger(__name__)


class RipgrepController(QObject):
    """Ripgrep 控制器 - 協調模型和視圖的互動"""
    
    def __init__(self, model: RipgrepModel, view: RipgrepView):
        super().__init__()
        self.model = model
        self.view = view
        
        # 設定定時器用於狀態更新
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.setInterval(1000)  # 每秒更新一次
        
        self._setup_connections()
        self._initialize()
    
    def _setup_connections(self):
        """設定信號連接"""
        # 視圖 → 控制器信號
        self.view.search_requested.connect(self._on_search_requested)
        self.view.search_cancelled.connect(self._on_search_cancelled)
        self.view.export_requested.connect(self._on_export_requested)
        
        # 模型 → 控制器信號
        self.model.search_started.connect(self._on_search_started)
        self.model.search_progress.connect(self._on_search_progress)
        self.model.search_result.connect(self._on_search_result)
        self.model.search_completed.connect(self._on_search_completed)
        self.model.search_error.connect(self._on_search_error)
    
    def _initialize(self):
        """初始化控制器"""
        try:
            # 檢查模型可用性
            if not self.model.is_available():
                self.view.show_error("Ripgrep 工具不可用，請確保已安裝 ripgrep")
                return
            
            # 更新搜尋歷史
            history = self.model.get_search_history()
            self.view.update_search_history(history)
            
            # 設定初始狀態
            version_info = self.model.get_version_info()
            logger.info(f"Ripgrep controller initialized with version: {version_info}")
            
        except Exception as e:
            logger.error(f"Error initializing ripgrep controller: {e}")
            self.view.show_error(f"初始化失敗: {str(e)}")
    
    def _on_search_requested(self, search_params: SearchParameters):
        """處理搜尋請求"""
        try:
            logger.info(f"Search requested for pattern: {search_params.pattern}")
            
            # 驗證搜尋參數
            if not self._validate_search_parameters(search_params):
                return
            
            # 清空之前的結果
            self.view.results_widget.clear_results()
            
            # 開始搜尋
            success = self.model.start_search(search_params)
            if not success:
                logger.warning("Failed to start search")
                self.view.show_error("無法啟動搜尋")
                
        except Exception as e:
            logger.error(f"Error handling search request: {e}")
            self.view.show_error(f"搜尋請求處理失敗: {str(e)}")
    
    def _on_search_cancelled(self):
        """處理搜尋取消"""
        try:
            logger.info("Search cancellation requested")
            self.model.cancel_search()
            
        except Exception as e:
            logger.error(f"Error cancelling search: {e}")
            self.view.show_error(f"取消搜尋失敗: {str(e)}")
    
    def _on_export_requested(self, file_path: str, format_type: str):
        """處理匯出請求"""
        try:
            logger.info(f"Export requested: {file_path} ({format_type})")
            
            success = self.model.export_results(file_path, format_type)
            if success:
                self.view.show_export_success(file_path)
            else:
                self.view.show_error("匯出失敗")
                
        except Exception as e:
            logger.error(f"Error handling export request: {e}")
            self.view.show_error(f"匯出請求處理失敗: {str(e)}")
    
    def _on_search_started(self):
        """處理搜尋開始"""
        try:
            logger.info("Search started")
            self.view.set_searching_state(True)
            self.status_timer.start()
            
        except Exception as e:
            logger.error(f"Error handling search started: {e}")
    
    def _on_search_progress(self, files_scanned: int, matches_found: int):
        """處理搜尋進度更新"""
        try:
            self.view.update_progress(files_scanned, matches_found)
            
        except Exception as e:
            logger.error(f"Error handling search progress: {e}")
    
    def _on_search_result(self, file_result: FileResult):
        """處理搜尋結果"""
        try:
            self.view.add_search_result(file_result)
            
        except Exception as e:
            logger.error(f"Error handling search result: {e}")
    
    def _on_search_completed(self, summary: SearchSummary):
        """處理搜尋完成"""
        try:
            logger.info(f"Search completed: {summary.total_matches} matches found")
            
            self.status_timer.stop()
            self.view.update_search_summary(summary)
            
            # 更新搜尋歷史
            history = self.model.get_search_history()
            self.view.update_search_history(history)
            
        except Exception as e:
            logger.error(f"Error handling search completion: {e}")
    
    def _on_search_error(self, error_message: str):
        """處理搜尋錯誤"""
        try:
            logger.error(f"Search error: {error_message}")
            
            self.status_timer.stop()
            self.view.show_error(error_message)
            
        except Exception as e:
            logger.error(f"Error handling search error: {e}")
    
    def _validate_search_parameters(self, params: SearchParameters) -> bool:
        """驗證搜尋參數"""
        try:
            # 檢查模式是否為空
            if not params.pattern or not params.pattern.strip():
                self.view.show_error("搜尋模式不能為空")
                return False
            
            # 檢查搜尋路徑是否存在
            import os
            if not os.path.exists(params.search_path):
                self.view.show_error(f"搜尋路徑不存在: {params.search_path}")
                return False
            
            # 檢查搜尋路徑是否為目錄
            if not os.path.isdir(params.search_path):
                self.view.show_error(f"搜尋路徑必須是目錄: {params.search_path}")
                return False
            
            # 正則表達式語法檢查
            if params.regex_mode:
                try:
                    import re
                    re.compile(params.pattern)
                except re.error as e:
                    self.view.show_error(f"正則表達式語法錯誤: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating search parameters: {e}")
            self.view.show_error(f"參數驗證失敗: {str(e)}")
            return False
    
    def _update_status(self):
        """更新狀態資訊"""
        try:
            if self.model.is_searching:
                # 搜尋進行中的狀態更新
                pass
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def get_model_info(self) -> dict:
        """獲取模型資訊"""
        try:
            return {
                'available': self.model.is_available(),
                'version': self.model.get_version_info(),
                'executable_path': self.model.executable_path,
                'is_searching': self.model.is_searching,
                'results_count': len(self.model.search_results),
                'history_count': len(self.model.search_history)
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """清理控制器資源"""
        try:
            # 停止定時器
            if self.status_timer.isActive():
                self.status_timer.stop()
            
            # 取消當前搜尋
            if self.model.is_searching:
                self.model.cancel_search()
            
            # 清理模型
            self.model.cleanup()
            
            logger.info("Ripgrep controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during controller cleanup: {e}")
    
    # 便利方法
    def start_quick_search(self, pattern: str, path: str = ".") -> bool:
        """快速搜尋便利方法"""
        try:
            params = SearchParameters(pattern=pattern, search_path=path)
            self._on_search_requested(params)
            return True
        except Exception as e:
            logger.error(f"Error starting quick search: {e}")
            return False
    
    def get_current_results_summary(self) -> Optional[dict]:
        """獲取當前結果摘要"""
        try:
            summary = self.model.get_search_summary()
            if summary:
                return {
                    'pattern': summary.pattern,
                    'total_matches': summary.total_matches,
                    'files_with_matches': summary.files_with_matches,
                    'files_searched': summary.files_searched,
                    'search_time': summary.search_time,
                    'status': summary.status.name
                }
            return None
        except Exception as e:
            logger.error(f"Error getting results summary: {e}")
            return None
    
    def clear_search_history(self) -> bool:
        """清除搜尋歷史"""
        try:
            self.model.clear_search_history()
            self.view.update_search_history([])
            logger.info("Search history cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing search history: {e}")
            return False