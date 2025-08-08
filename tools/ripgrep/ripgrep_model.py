"""
Ripgrep Model - 業務邏輯和搜尋操作
"""
import logging
import os
import threading
from typing import List, Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal

from .core.data_models import SearchParameters, SearchSummary, FileResult
from .core.search_engine import RipgrepEngine, validate_ripgrep_available
from .core.async_worker import RipgrepSearchWorker

logger = logging.getLogger(__name__)


class RipgrepModel(QObject):
    """Ripgrep 模型 - 處理搜尋邏輯和資料管理"""
    
    # 信號定義
    search_started = pyqtSignal()
    search_progress = pyqtSignal(int, int)  # files_scanned, matches_found
    search_result = pyqtSignal(object)      # FileResult
    search_completed = pyqtSignal(object)   # SearchSummary
    search_error = pyqtSignal(str)          # error_message
    
    def __init__(self):
        super().__init__()
        self.executable_path = self._find_ripgrep_executable()
        self.current_worker: Optional[RipgrepSearchWorker] = None
        self.search_results: List[FileResult] = []
        self.current_summary: Optional[SearchSummary] = None
        self.is_searching = False
        
        # 搜尋歷史
        self.search_history: List[str] = []
        self.max_history = 50
        
        # 驗證工具可用性
        self._validate_setup()
    
    def _find_ripgrep_executable(self) -> str:
        """尋找 ripgrep 執行檔"""
        # 常見的 ripgrep 安裝位置
        possible_paths = [
            "rg",  # 系統 PATH
            "rg.exe",  # Windows 系統 PATH
            os.path.expanduser("~/.cargo/bin/rg"),  # Cargo 安裝
            "/usr/local/bin/rg",  # Homebrew/Linux
            "/usr/bin/rg",  # 系統包管理器安裝
        ]
        
        for path in possible_paths:
            if validate_ripgrep_available(path):
                logger.info(f"Found ripgrep at: {path}")
                return path
        
        logger.warning("Ripgrep executable not found in common locations")
        return "rg"  # 預設嘗試使用 PATH
    
    def _validate_setup(self) -> bool:
        """驗證設定"""
        try:
            available = validate_ripgrep_available(self.executable_path)
            if available:
                logger.info("Ripgrep model initialized successfully")
            else:
                logger.error("Ripgrep not available")
            return available
        except Exception as e:
            logger.error(f"Error validating ripgrep setup: {e}")
            return False
    
    def is_available(self) -> bool:
        """檢查 ripgrep 是否可用"""
        return validate_ripgrep_available(self.executable_path)
    
    def get_version_info(self) -> str:
        """獲取版本資訊"""
        try:
            engine = RipgrepEngine(self.executable_path)
            return engine.get_version()
        except Exception as e:
            logger.error(f"Error getting version info: {e}")
            return "Unknown"
    
    def start_search(self, search_params: SearchParameters) -> bool:
        """開始搜尋"""
        try:
            # 檢查是否已經在搜尋
            if self.is_searching:
                logger.warning("Search already in progress")
                return False
            
            # 驗證參數
            if not search_params.pattern:
                self.search_error.emit("搜尋模式不能為空")
                return False
            
            if not os.path.exists(search_params.search_path):
                self.search_error.emit(f"搜尋路徑不存在: {search_params.search_path}")
                return False
            
            # 清除之前的結果
            self.search_results.clear()
            self.current_summary = None
            
            # 添加到搜尋歷史
            self._add_to_history(search_params.pattern)
            
            # 創建並配置工作執行緒
            self.current_worker = RipgrepSearchWorker(
                search_params, 
                self.executable_path
            )
            
            # 連接信號
            self.current_worker.search_started.connect(self._on_search_started)
            self.current_worker.progress_updated.connect(self._on_progress_updated)
            self.current_worker.result_found.connect(self._on_result_found)
            self.current_worker.search_completed.connect(self._on_search_completed)
            self.current_worker.search_error.connect(self._on_search_error)
            
            # 開始搜尋
            self.current_worker.start()
            self.is_searching = True
            
            logger.info(f"Started search for pattern: {search_params.pattern}")
            return True
            
        except Exception as e:
            error_msg = f"啟動搜尋失敗: {str(e)}"
            logger.error(error_msg)
            self.search_error.emit(error_msg)
            return False
    
    def cancel_search(self):
        """取消當前搜尋"""
        try:
            if self.current_worker and self.is_searching:
                logger.info("Cancelling current search")
                self.current_worker.cancel_search()
                
                # 等待工作執行緒結束
                if self.current_worker.isRunning():
                    self.current_worker.wait(timeout=3000)  # 3秒超時
                
                self.is_searching = False
                logger.info("Search cancelled successfully")
                
        except Exception as e:
            logger.error(f"Error cancelling search: {e}")
    
    def get_search_results(self) -> List[FileResult]:
        """獲取當前搜尋結果"""
        return self.search_results.copy()
    
    def get_search_summary(self) -> Optional[SearchSummary]:
        """獲取搜尋摘要"""
        return self.current_summary
    
    def get_search_history(self) -> List[str]:
        """獲取搜尋歷史"""
        return self.search_history.copy()
    
    def clear_search_history(self):
        """清除搜尋歷史"""
        self.search_history.clear()
        logger.info("Search history cleared")
    
    def export_results(self, file_path: str, format_type: str = 'json') -> bool:
        """匯出搜尋結果"""
        try:
            if not self.search_results:
                logger.warning("No search results to export")
                return False
            
            # 準備匯出資料
            export_data = {
                'summary': self.current_summary.to_dict() if self.current_summary else None,
                'results': [result.to_dict() for result in self.search_results]
            }
            
            # 根據格式匯出
            if format_type.lower() == 'json':
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            elif format_type.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['File', 'Line', 'Column', 'Content', 'Match Count'])
                    
                    for result in self.search_results:
                        for match in result.matches:
                            writer.writerow([
                                result.file_path,
                                match.line_number,
                                match.column,
                                match.content,
                                len(match.highlights)
                            ])
            
            elif format_type.lower() == 'txt':
                with open(file_path, 'w', encoding='utf-8') as f:
                    if self.current_summary:
                        f.write(f"搜尋摘要\n")
                        f.write(f"搜尋模式: {self.current_summary.pattern}\n")
                        f.write(f"總匹配數: {self.current_summary.total_matches}\n")
                        f.write(f"匹配檔案數: {self.current_summary.files_with_matches}\n")
                        f.write(f"搜尋時間: {self.current_summary.search_time:.2f}秒\n")
                        f.write("\n" + "="*50 + "\n\n")
                    
                    for result in self.search_results:
                        f.write(f"檔案: {result.file_path}\n")
                        f.write(f"匹配數: {result.total_matches}\n")
                        f.write("-" * 30 + "\n")
                        
                        for match in result.matches:
                            f.write(f"  行 {match.line_number}: {match.content}\n")
                        
                        f.write("\n")
            
            logger.info(f"Results exported to: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"匯出結果失敗: {str(e)}"
            logger.error(error_msg)
            self.search_error.emit(error_msg)
            return False
    
    def _add_to_history(self, pattern: str):
        """添加到搜尋歷史"""
        if pattern and pattern not in self.search_history:
            self.search_history.insert(0, pattern)
            
            # 限制歷史記錄數量
            if len(self.search_history) > self.max_history:
                self.search_history = self.search_history[:self.max_history]
    
    # 工作執行緒信號處理器
    def _on_search_started(self):
        """搜尋開始"""
        self.search_started.emit()
    
    def _on_progress_updated(self, files_scanned: int, matches_found: int):
        """進度更新"""
        self.search_progress.emit(files_scanned, matches_found)
    
    def _on_result_found(self, file_result: FileResult):
        """找到搜尋結果"""
        self.search_results.append(file_result)
        self.search_result.emit(file_result)
    
    def _on_search_completed(self, summary: SearchSummary):
        """搜尋完成"""
        self.current_summary = summary
        self.is_searching = False
        self.search_completed.emit(summary)
        
        # 清理工作執行緒
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def _on_search_error(self, error_message: str):
        """搜尋錯誤"""
        self.is_searching = False
        self.search_error.emit(error_message)
        
        # 清理工作執行緒
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def cleanup(self):
        """清理資源"""
        try:
            # 取消當前搜尋
            if self.is_searching:
                self.cancel_search()
            
            # 清理工作執行緒
            if self.current_worker:
                self.current_worker.deleteLater()
                self.current_worker = None
            
            logger.info("RipgrepModel cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")