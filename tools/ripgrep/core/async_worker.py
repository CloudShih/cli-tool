"""
Ripgrep 非同步工作執行緒
處理搜尋操作的非同步執行
"""
import time
import logging
from typing import Optional, List, Dict, Any
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from .data_models import SearchParameters, SearchSummary, SearchStatus, FileResult
from .search_engine import RipgrepEngine
from .result_parser import RipgrepParser

logger = logging.getLogger(__name__)


class SearchProgressTracker:
    """搜尋進度追蹤器"""
    
    def __init__(self):
        self.files_scanned = 0
        self.matches_found = 0
        self.start_time = 0.0
        self.current_file = ""
        self.total_output_lines = 0
    
    def reset(self):
        """重設進度"""
        self.files_scanned = 0
        self.matches_found = 0
        self.start_time = time.time()
        self.current_file = ""
        self.total_output_lines = 0
    
    def update_file_count(self, file_path: str):
        """更新檔案計數"""
        if file_path != self.current_file:
            self.current_file = file_path
            self.files_scanned += 1
    
    def update_match_count(self, count: int = 1):
        """更新匹配計數"""
        self.matches_found += count
    
    def get_elapsed_time(self) -> float:
        """獲取已用時間"""
        return time.time() - self.start_time
    
    def get_progress_info(self) -> tuple[int, int]:
        """獲取進度資訊"""
        return self.files_scanned, self.matches_found


class RipgrepSearchWorker(QThread):
    """Ripgrep 搜尋工作執行緒"""
    
    # 信號定義
    search_started = pyqtSignal()
    progress_updated = pyqtSignal(int, int)  # files_scanned, matches_found
    result_found = pyqtSignal(object)        # FileResult
    search_completed = pyqtSignal(object)    # SearchSummary
    search_error = pyqtSignal(str)          # error_message
    
    def __init__(self, search_params: SearchParameters, executable_path: str = "rg", parent=None):
        super().__init__(parent)
        self.search_params = search_params
        self.executable_path = executable_path
        self.should_cancel = False
        self.search_engine: Optional[RipgrepEngine] = None
        self.parser = RipgrepParser()
        self.progress_tracker = SearchProgressTracker()
        
        # 批次處理設定
        self.batch_size = 10
        self.progress_update_interval = 0.5  # 秒
        self.last_progress_update = 0.0
    
    def run(self):
        """執行搜尋操作"""
        try:
            logger.info(f"Starting ripgrep search for pattern: {self.search_params.pattern}")
            self.progress_tracker.reset()
            self.search_started.emit()
            
            # 初始化搜尋引擎
            self.search_engine = RipgrepEngine(self.executable_path)
            
            # 驗證搜尋參數
            validation_errors = self.search_engine.validate_search_params(self.search_params)
            if validation_errors:
                error_msg = "搜尋參數錯誤: " + "; ".join(validation_errors)
                logger.error(error_msg)
                self.search_error.emit(error_msg)
                return
            
            # 開始搜尋
            process = self.search_engine.search(self.search_params, 'json')
            
            # 處理搜尋結果
            self._process_search_results(process)
            
        except Exception as e:
            error_msg = f"搜尋執行失敗: {str(e)}"
            logger.error(error_msg)
            self.search_error.emit(error_msg)
    
    def _process_search_results(self, process):
        """處理搜尋結果"""
        file_results = {}
        output_buffer = []
        
        try:
            # 即時讀取輸出
            while True:
                if self.should_cancel:
                    logger.info("Search cancelled by user")
                    self.search_engine.cancel_search()
                    break
                
                # 讀取一行輸出
                line = process.stdout.readline()
                
                if not line:
                    # 進程結束
                    if process.poll() is not None:
                        break
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                self.progress_tracker.total_output_lines += 1
                output_buffer.append(line)
                
                # 批次處理輸出
                if len(output_buffer) >= self.batch_size:
                    self._process_output_batch(output_buffer, file_results)
                    output_buffer.clear()
                
                # 更新進度
                self._update_progress_if_needed()
            
            # 處理剩餘的輸出
            if output_buffer:
                self._process_output_batch(output_buffer, file_results)
            
            # 等待進程完成
            stdout, stderr = process.communicate(timeout=5)
            if stdout:
                # 處理可能遺漏的輸出
                remaining_lines = [line.strip() for line in stdout.split('\n') if line.strip()]
                if remaining_lines:
                    self._process_output_batch(remaining_lines, file_results)
            
            # 檢查進程返回碼
            return_code = process.returncode
            
            if return_code != 0 and not self.should_cancel:
                error_output = stderr.strip() if stderr else "Unknown error"
                logger.warning(f"Ripgrep exited with code {return_code}: {error_output}")
                
                # 某些情況下 ripgrep 返回非零值是正常的（如沒找到匹配）
                if return_code == 1:  # No matches found
                    logger.info("No matches found")
                elif return_code == 2:  # Error in search (often due to invalid parameters)
                    # 檢查是否是文件類型不存在的情況
                    if "unrecognized file type" in error_output.lower() or "no files to search" in error_output.lower():
                        logger.info(f"File type or search criteria not found: {error_output}")
                    else:
                        self.search_error.emit(f"搜尋參數錯誤: {error_output}")
                        return
                else:
                    # 其他錯誤情況
                    self.search_error.emit(f"搜尋過程中發生錯誤 (code {return_code}): {error_output}")
                    return
            
            # 生成搜尋摘要
            self._complete_search(file_results)
            
        except Exception as e:
            error_msg = f"處理搜尋結果時發生錯誤: {str(e)}"
            logger.error(error_msg)
            self.search_error.emit(error_msg)
    
    def _process_output_batch(self, lines: List[str], file_results: Dict[str, FileResult]):
        """批次處理輸出行"""
        for line in lines:
            if not line or not line.startswith('{'):
                continue
            
            try:
                # 解析 JSON 行
                import json
                data = json.loads(line)
                
                if data.get('type') == 'match':
                    self._process_match_data(data, file_results)
                
            except Exception as json_error:
                logger.debug(f"Skip non-JSON line: {line[:50]}...")
                continue
            except Exception as e:
                logger.warning(f"Error processing line: {e}")
                continue
    
    def _process_match_data(self, data: dict, file_results: Dict[str, FileResult]):
        """處理匹配資料"""
        try:
            match_data = data.get('data', {})
            file_path = match_data.get('path', {}).get('text', '')
            
            if not file_path:
                return
            
            # 獲取或創建該文件的結果對象
            if file_path not in file_results:
                file_results[file_path] = FileResult(file_path=file_path)
            
            file_result = file_results[file_path]
            
            # 創建匹配項並加入文件結果
            match = self.parser._create_match_from_json(match_data)
            if match:
                file_result.add_match(match)
                
                # 更新進度追蹤
                self.progress_tracker.update_file_count(file_path)
                self.progress_tracker.update_match_count(1)
            
        except Exception as e:
            logger.warning(f"Error processing match data: {e}")
    
    def _update_progress_if_needed(self):
        """根據時間間隔更新進度"""
        current_time = time.time()
        if current_time - self.last_progress_update >= self.progress_update_interval:
            files_scanned, matches_found = self.progress_tracker.get_progress_info()
            self.progress_updated.emit(files_scanned, matches_found)
            self.last_progress_update = current_time
    
    def _complete_search(self, file_results: Dict[str, FileResult]):
        """完成搜尋並發送摘要"""
        elapsed_time = self.progress_tracker.get_elapsed_time()
        
        # 發送聚合後的文件結果給視圖
        for file_result in file_results.values():
            if file_result.matches:  # 只發送有匹配的文件
                self.result_found.emit(file_result)
        
        # 統計最終結果
        total_files = len(file_results)
        total_matches = sum(fr.total_matches for fr in file_results.values())
        
        # 創建摘要
        status = SearchStatus.CANCELLED if self.should_cancel else SearchStatus.COMPLETED
        
        summary = SearchSummary(
            pattern=self.search_params.pattern,
            total_matches=total_matches,
            files_with_matches=total_files,
            files_searched=self.progress_tracker.files_scanned,
            search_time=elapsed_time,
            status=status
        )
        
        logger.info(f"Search completed: {total_matches} matches in {total_files} files ({elapsed_time:.2f}s)")
        self.search_completed.emit(summary)
    
    def cancel_search(self):
        """取消搜尋"""
        logger.info("Cancelling ripgrep search")
        self.should_cancel = True
        
        # 如果搜尋引擎存在，取消當前搜尋
        if self.search_engine:
            self.search_engine.cancel_search()


class SearchResultBuffer:
    """搜尋結果緩衝器 - 用於批次處理和記憶體管理"""
    
    def __init__(self, max_buffer_size: int = 1000, max_memory_mb: int = 100):
        self.max_buffer_size = max_buffer_size
        self.max_memory_mb = max_memory_mb
        self.buffer: List[FileResult] = []
        self.total_results = 0
        
    def add_result(self, result: FileResult) -> List[FileResult]:
        """添加結果，返回需要處理的批次"""
        self.buffer.append(result)
        self.total_results += 1
        
        # 檢查是否需要清空緩衝器
        if (len(self.buffer) >= self.max_buffer_size or 
            self._check_memory_usage()):
            
            batch = self.buffer.copy()
            self.buffer.clear()
            return batch
        
        return []
    
    def flush_buffer(self) -> List[FileResult]:
        """清空緩衝器並返回所有結果"""
        batch = self.buffer.copy()
        self.buffer.clear()
        return batch
    
    def _check_memory_usage(self) -> bool:
        """檢查記憶體使用"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return memory_mb > self.max_memory_mb
        except ImportError:
            # 如果沒有 psutil，使用簡單的計數檢查
            return len(self.buffer) > self.max_buffer_size // 2
        except Exception:
            return False
    
    def get_statistics(self) -> dict:
        """獲取統計資訊"""
        return {
            'buffer_size': len(self.buffer),
            'total_processed': self.total_results,
            'max_buffer_size': self.max_buffer_size,
        }


# 便利函數
def create_search_worker(search_params: SearchParameters, executable_path: str = "rg") -> RipgrepSearchWorker:
    """創建搜尋工作執行緒"""
    return RipgrepSearchWorker(search_params, executable_path)