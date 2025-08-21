"""
YT-DLP 非同步工作執行緒
處理非同步下載操作
"""
import time
import logging
from typing import Optional, List
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

from .data_models import (
    DownloadParameters, DownloadResult, DownloadProgress, 
    DownloadSummary, DownloadStatus
)
from .download_engine import YtDlpEngine, parse_progress_line

logger = logging.getLogger(__name__)


class YtDlpDownloadWorker(QThread):
    """YT-DLP 下載工作執行緒"""
    
    # 信號定義
    download_started = pyqtSignal()
    progress_updated = pyqtSignal(object)  # DownloadProgress
    download_completed = pyqtSignal(object)  # DownloadResult
    download_error = pyqtSignal(str)  # error_message
    
    def __init__(self, download_params: DownloadParameters, executable_path: str = "yt-dlp"):
        super().__init__()
        self.download_params = download_params
        self.executable_path = executable_path
        self.engine: Optional[YtDlpEngine] = None
        self.is_cancelled = False
        self.mutex = QMutex()
        
        # 下載狀態追蹤
        self.current_progress = DownloadProgress(status="idle")
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def run(self):
        """執行下載任務"""
        try:
            with QMutexLocker(self.mutex):
                if self.is_cancelled:
                    return
            
            # 初始化引擎
            self.engine = YtDlpEngine(self.executable_path)
            self.start_time = time.time()
            
            # 發出開始信號
            self.download_started.emit()
            
            # 開始下載
            self._execute_download()
            
        except Exception as e:
            error_msg = f"下載執行失敗: {str(e)}"
            logger.error(error_msg)
            self.download_error.emit(error_msg)
    
    def _execute_download(self):
        """執行下載過程"""
        try:
            # 更新狀態為準備中
            self.current_progress.status = "preparing"
            self.progress_updated.emit(self.current_progress)
            
            # 檢查是否被取消
            with QMutexLocker(self.mutex):
                if self.is_cancelled:
                    return
            
            # 啟動下載進程
            process = self.engine.download(self.download_params)
            
            # 更新狀態為下載中
            self.current_progress.status = "downloading"
            self.progress_updated.emit(self.current_progress)
            
            # 監控下載進度
            output_lines = []
            error_occurred = False
            
            try:
                while True:
                    # 檢查是否被取消
                    with QMutexLocker(self.mutex):
                        if self.is_cancelled:
                            self.engine.cancel_download()
                            return
                    
                    # 讀取輸出
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    line = line.strip()
                    if line:
                        output_lines.append(line)
                        logger.debug(f"YT-DLP output: {line}")
                        
                        # 解析進度
                        progress_info = parse_progress_line(line)
                        if progress_info:
                            self._update_progress(progress_info)
                        
                        # 檢查錯誤
                        if "ERROR:" in line:
                            error_occurred = True
                            logger.error(f"YT-DLP error: {line}")
                
                # 等待進程完成
                return_code = process.wait()
                self.end_time = time.time()
                
                # 處理結果
                if return_code == 0 and not error_occurred:
                    self._handle_success(output_lines)
                else:
                    self._handle_error(output_lines, return_code)
                    
            except Exception as e:
                logger.error(f"Error monitoring download: {e}")
                self.engine.cancel_download()
                self.download_error.emit(f"下載監控錯誤: {str(e)}")
                
        except Exception as e:
            error_msg = f"下載執行失敗: {str(e)}"
            logger.error(error_msg)
            self.download_error.emit(error_msg)
    
    def _update_progress(self, progress_info: dict):
        """更新下載進度"""
        try:
            # 更新進度物件
            status = progress_info.get('status', 'downloading')
            self.current_progress.status = status
            
            if 'percentage' in progress_info:
                percentage = progress_info['percentage']
                if self.current_progress.total_bytes:
                    self.current_progress.downloaded_bytes = int(
                        (percentage / 100) * self.current_progress.total_bytes
                    )
            
            if 'filename' in progress_info:
                self.current_progress.filename = progress_info['filename']
            
            if 'speed_str' in progress_info:
                # 解析速度字符串並更新
                from .download_engine import estimate_speed
                speed = estimate_speed(progress_info['speed_str'])
                if speed:
                    self.current_progress.speed = speed
            
            if 'total_size_str' in progress_info and not self.current_progress.total_bytes:
                # 解析總大小字符串並更新
                from .download_engine import estimate_total_size
                total_size = estimate_total_size(progress_info['total_size_str'])
                if total_size:
                    self.current_progress.total_bytes = total_size
            
            # 計算 ETA
            if (self.current_progress.speed and self.current_progress.speed > 0 
                and self.current_progress.total_bytes and self.current_progress.downloaded_bytes):
                remaining_bytes = self.current_progress.total_bytes - self.current_progress.downloaded_bytes
                if remaining_bytes > 0:
                    self.current_progress.eta = int(remaining_bytes / self.current_progress.speed)
            
            # 計算經過時間
            if self.start_time:
                self.current_progress.elapsed = time.time() - self.start_time
            
            # 發出進度更新信號
            self.progress_updated.emit(self.current_progress)
            
        except Exception as e:
            logger.warning(f"Error updating progress: {e}")
    
    def _handle_success(self, output_lines: List[str]):
        """處理下載成功"""
        try:
            # 分析輸出以獲取結果檔案
            output_files = []
            for line in output_lines:
                if "[download] Destination:" in line:
                    filename = line.split("Destination:")[1].strip()
                    output_files.append(filename)
                elif "[download] 100%" in line and "has already been downloaded" not in line:
                    # 提取完成的檔案名
                    parts = line.split()
                    for part in parts:
                        if part.endswith(('.mp4', '.mkv', '.webm', '.mp3', '.m4a', '.ogg')):
                            if part not in output_files:
                                output_files.append(part)
            
            # 創建下載結果
            result = DownloadResult(
                url=self.download_params.url,
                title=self.current_progress.filename or "Unknown",
                status=DownloadStatus.COMPLETED,
                output_files=output_files,
                start_time=self.start_time,
                end_time=self.end_time
            )
            
            # 嘗試獲取檔案大小
            if output_files:
                try:
                    import os
                    total_size = 0
                    for file_path in output_files:
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                    if total_size > 0:
                        result.file_size = total_size
                except Exception as e:
                    logger.warning(f"Could not get file size: {e}")
            
            logger.info(f"Download completed successfully: {result.title}")
            self.download_completed.emit(result)
            
        except Exception as e:
            logger.error(f"Error handling success: {e}")
            self.download_error.emit(f"處理下載成功時發生錯誤: {str(e)}")
    
    def _handle_error(self, output_lines: List[str], return_code: int):
        """處理下載錯誤"""
        try:
            # 提取錯誤訊息
            error_messages = []
            for line in output_lines:
                if "ERROR:" in line:
                    error_messages.append(line)
            
            error_message = "\n".join(error_messages) if error_messages else f"下載失敗 (返回碼: {return_code})"
            
            # 創建失敗結果
            result = DownloadResult(
                url=self.download_params.url,
                title=self.current_progress.filename or "Unknown",
                status=DownloadStatus.ERROR,
                error_message=error_message,
                start_time=self.start_time,
                end_time=self.end_time
            )
            
            logger.error(f"Download failed: {error_message}")
            self.download_completed.emit(result)
            
        except Exception as e:
            logger.error(f"Error handling error: {e}")
            self.download_error.emit(f"處理下載錯誤時發生錯誤: {str(e)}")
    
    def cancel_download(self):
        """取消下載"""
        try:
            with QMutexLocker(self.mutex):
                self.is_cancelled = True
            
            if self.engine and self.engine.is_downloading():
                self.engine.cancel_download()
            
            logger.info("Download cancellation requested")
            
        except Exception as e:
            logger.error(f"Error cancelling download: {e}")
    
    def is_download_cancelled(self) -> bool:
        """檢查是否已取消"""
        with QMutexLocker(self.mutex):
            return self.is_cancelled


class YtDlpBatchWorker(QThread):
    """批次下載工作執行緒"""
    
    # 信號定義
    batch_started = pyqtSignal(int)  # total_count
    item_started = pyqtSignal(int, str)  # index, url
    item_progress = pyqtSignal(int, object)  # index, DownloadProgress
    item_completed = pyqtSignal(int, object)  # index, DownloadResult
    batch_completed = pyqtSignal(object)  # DownloadSummary
    batch_error = pyqtSignal(str)  # error_message
    
    def __init__(self, download_list: List[DownloadParameters], executable_path: str = "yt-dlp"):
        super().__init__()
        self.download_list = download_list
        self.executable_path = executable_path
        self.is_cancelled = False
        self.mutex = QMutex()
        
        # 批次處理狀態
        self.current_index = 0
        self.results: List[DownloadResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def run(self):
        """執行批次下載"""
        try:
            with QMutexLocker(self.mutex):
                if self.is_cancelled:
                    return
            
            self.start_time = time.time()
            total_count = len(self.download_list)
            
            # 發出開始信號
            self.batch_started.emit(total_count)
            
            # 逐個處理下載任務
            for i, params in enumerate(self.download_list):
                with QMutexLocker(self.mutex):
                    if self.is_cancelled:
                        break
                
                self.current_index = i
                self._process_single_download(i, params)
            
            # 生成摘要並完成
            self.end_time = time.time()
            summary = self._create_summary()
            self.batch_completed.emit(summary)
            
        except Exception as e:
            error_msg = f"批次下載執行失敗: {str(e)}"
            logger.error(error_msg)
            self.batch_error.emit(error_msg)
    
    def _process_single_download(self, index: int, params: DownloadParameters):
        """處理單個下載任務"""
        try:
            # 發出項目開始信號
            self.item_started.emit(index, params.url)
            
            # 創建工作執行緒
            worker = YtDlpDownloadWorker(params, self.executable_path)
            
            # 連接信號
            result_received = False
            download_result = None
            
            def on_progress(progress):
                self.item_progress.emit(index, progress)
            
            def on_completed(result):
                nonlocal result_received, download_result
                result_received = True
                download_result = result
                self.results.append(result)
                self.item_completed.emit(index, result)
            
            def on_error(error_msg):
                nonlocal result_received, download_result
                result_received = True
                # 創建錯誤結果
                download_result = DownloadResult(
                    url=params.url,
                    title="Unknown",
                    status=DownloadStatus.ERROR,
                    error_message=error_msg
                )
                self.results.append(download_result)
                self.item_completed.emit(index, download_result)
            
            worker.progress_updated.connect(on_progress)
            worker.download_completed.connect(on_completed)
            worker.download_error.connect(on_error)
            
            # 啟動工作執行緒並等待完成
            worker.start()
            
            while not result_received:
                # 檢查是否被取消
                with QMutexLocker(self.mutex):
                    if self.is_cancelled:
                        worker.cancel_download()
                        worker.wait(3000)  # 等待 3 秒
                        return
                
                # 短暫睡眠避免過度消耗 CPU
                self.msleep(100)
                
                # 檢查執行緒是否完成
                if not worker.isRunning():
                    break
            
            # 等待執行緒結束
            worker.wait(5000)  # 最多等待 5 秒
            
        except Exception as e:
            logger.error(f"Error processing download {index}: {e}")
            
            # 創建錯誤結果
            error_result = DownloadResult(
                url=params.url,
                title="Unknown",
                status=DownloadStatus.ERROR,
                error_message=str(e)
            )
            self.results.append(error_result)
            self.item_completed.emit(index, error_result)
    
    def _create_summary(self) -> DownloadSummary:
        """創建下載摘要"""
        summary = DownloadSummary()
        summary.total_downloads = len(self.results)
        
        for result in self.results:
            if result.status == DownloadStatus.COMPLETED:
                summary.successful_downloads += 1
                if result.file_size:
                    summary.total_size += result.file_size
                if result.download_time:
                    summary.download_time += result.download_time
            else:
                summary.failed_downloads += 1
                if result.error_message:
                    summary.errors.append(result.error_message)
        
        if self.start_time and self.end_time:
            summary.download_time = self.end_time - self.start_time
        
        return summary
    
    def cancel_batch(self):
        """取消批次下載"""
        try:
            with QMutexLocker(self.mutex):
                self.is_cancelled = True
            
            logger.info("Batch download cancellation requested")
            
        except Exception as e:
            logger.error(f"Error cancelling batch download: {e}")
    
    def is_batch_cancelled(self) -> bool:
        """檢查批次是否已取消"""
        with QMutexLocker(self.mutex):
            return self.is_cancelled