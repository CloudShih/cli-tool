"""
YT-DLP Model - 業務邏輯和下載操作
"""
import logging
import os
import json
import time
from typing import List, Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal
from pathlib import Path

from .core.data_models import (
    DownloadParameters, DownloadResult, DownloadProgress, 
    DownloadSummary, DownloadStatus, DownloadQueue, VideoInfo
)
from .core.download_engine import YtDlpEngine, validate_ytdlp_available
from .core.async_worker import YtDlpDownloadWorker, YtDlpBatchWorker

logger = logging.getLogger(__name__)


class YtDlpModel(QObject):
    """YT-DLP 模型 - 處理下載邏輯和資料管理"""
    
    # 信號定義
    download_started = pyqtSignal()
    download_progress = pyqtSignal(object)      # DownloadProgress
    download_result = pyqtSignal(object)        # DownloadResult
    download_completed = pyqtSignal(object)     # DownloadSummary
    download_error = pyqtSignal(str)            # error_message
    
    # 批次下載信號
    batch_started = pyqtSignal(int)             # total_count
    batch_item_started = pyqtSignal(int, str)   # index, url
    batch_item_progress = pyqtSignal(int, object)  # index, DownloadProgress
    batch_item_completed = pyqtSignal(int, object) # index, DownloadResult
    batch_completed = pyqtSignal(object)        # DownloadSummary
    
    # 信息獲取信號
    video_info_received = pyqtSignal(object)    # VideoInfo
    formats_received = pyqtSignal(list)         # List[Dict]
    
    def __init__(self):
        super().__init__()
        self.executable_path = self._find_ytdlp_executable()
        self.current_worker: Optional[YtDlpDownloadWorker] = None
        self.batch_worker: Optional[YtDlpBatchWorker] = None
        self.download_queue = DownloadQueue()
        self.download_history: List[DownloadResult] = []
        self.is_downloading = False
        self.is_batch_downloading = False
        
        # 下載歷史和設定
        self.max_history = 100
        self.default_output_dir = str(Path.home() / "Downloads")
        self.settings: Dict[str, Any] = {}
        
        # 驗證工具可用性
        self._validate_setup()
        self._load_settings()
    
    def _find_ytdlp_executable(self) -> str:
        """尋找 yt-dlp 執行檔"""
        # 常見的 yt-dlp 安裝位置
        possible_paths = [
            "yt-dlp",  # 系統 PATH
            "yt-dlp.exe",  # Windows 系統 PATH
            os.path.expanduser("~/.local/bin/yt-dlp"),  # pip 用戶安裝
            "/usr/local/bin/yt-dlp",  # Homebrew/Linux
            "/usr/bin/yt-dlp",  # 系統包管理器安裝
        ]
        
        for path in possible_paths:
            if validate_ytdlp_available(path):
                logger.info(f"Found yt-dlp at: {path}")
                return path
        
        logger.warning("YT-DLP executable not found in common locations")
        return "yt-dlp"  # 預設嘗試使用 PATH
    
    def _validate_setup(self) -> bool:
        """驗證設定"""
        try:
            available = validate_ytdlp_available(self.executable_path)
            if available:
                logger.info("YT-DLP model initialized successfully")
            else:
                logger.error("YT-DLP not available")
            return available
        except Exception as e:
            logger.error(f"Error validating yt-dlp setup: {e}")
            return False
    
    def _load_settings(self):
        """載入設定"""
        try:
            settings_file = Path.home() / ".cli_tool" / "yt_dlp_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info("Settings loaded successfully")
            else:
                self._create_default_settings()
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
            self._create_default_settings()
    
    def _create_default_settings(self):
        """創建預設設定"""
        self.settings = {
            'default_output_dir': self.default_output_dir,
            'default_quality': 'best',
            'auto_subtitle': False,
            'embed_subtitle': False,
            'extract_audio': False,
            'audio_format': 'mp3',
            'keep_video': True,
            'write_thumbnail': False,
            'write_info_json': False,
            'max_concurrent_downloads': 3,
            'retry_count': 10
        }
        self._save_settings()
    
    def _save_settings(self):
        """保存設定"""
        try:
            settings_dir = Path.home() / ".cli_tool"
            settings_dir.mkdir(exist_ok=True)
            
            settings_file = settings_dir / "yt_dlp_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            logger.debug("Settings saved successfully")
        except Exception as e:
            logger.warning(f"Could not save settings: {e}")
    
    def is_available(self) -> bool:
        """檢查 yt-dlp 是否可用"""
        return validate_ytdlp_available(self.executable_path)
    
    def get_version_info(self) -> str:
        """獲取版本資訊"""
        try:
            engine = YtDlpEngine(self.executable_path)
            return engine.get_version()
        except Exception as e:
            logger.error(f"Error getting version info: {e}")
            return "Unknown"
    
    def get_supported_sites(self) -> List[str]:
        """獲取支援的網站列表"""
        try:
            engine = YtDlpEngine(self.executable_path)
            return engine.get_supported_sites()
        except Exception as e:
            logger.error(f"Error getting supported sites: {e}")
            return []
    
    def validate_url(self, url: str) -> bool:
        """驗證 URL 是否受支援"""
        try:
            engine = YtDlpEngine(self.executable_path)
            return engine.validate_url(url)
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False
    
    def get_video_info(self, url: str) -> bool:
        """獲取影片資訊 (非同步)"""
        try:
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class InfoWorker(QThread):
                info_received = pyqtSignal(object)
                info_error = pyqtSignal(str)
                
                def __init__(self, executable_path: str, url: str):
                    super().__init__()
                    self.executable_path = executable_path
                    self.url = url
                
                def run(self):
                    try:
                        engine = YtDlpEngine(self.executable_path)
                        info = engine.get_video_info(self.url)
                        if info:
                            self.info_received.emit(info)
                        else:
                            self.info_error.emit("無法獲取影片資訊")
                    except Exception as e:
                        self.info_error.emit(f"獲取影片資訊失敗: {str(e)}")
            
            # 創建工作執行緒
            worker = InfoWorker(self.executable_path, url)
            worker.info_received.connect(self.video_info_received.emit)
            worker.info_error.connect(self.download_error.emit)
            worker.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting video info retrieval: {e}")
            self.download_error.emit(f"啟動影片資訊獲取失敗: {str(e)}")
            return False
    
    def get_available_formats(self, url: str) -> bool:
        """獲取可用格式列表 (非同步)"""
        try:
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class FormatsWorker(QThread):
                formats_received = pyqtSignal(list)
                formats_error = pyqtSignal(str)
                
                def __init__(self, executable_path: str, url: str):
                    super().__init__()
                    self.executable_path = executable_path
                    self.url = url
                
                def run(self):
                    try:
                        engine = YtDlpEngine(self.executable_path)
                        formats = engine.get_available_formats(self.url)
                        self.formats_received.emit(formats)
                    except Exception as e:
                        self.formats_error.emit(f"獲取格式列表失敗: {str(e)}")
            
            # 創建工作執行緒
            worker = FormatsWorker(self.executable_path, url)
            worker.formats_received.connect(self.formats_received.emit)
            worker.formats_error.connect(self.download_error.emit)
            worker.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting formats retrieval: {e}")
            self.download_error.emit(f"啟動格式列表獲取失敗: {str(e)}")
            return False
    
    def start_download(self, download_params: DownloadParameters) -> bool:
        """開始單個下載"""
        try:
            # 檢查是否已經在下載
            if self.is_downloading:
                logger.warning("Download already in progress")
                self.download_error.emit("已有下載任務正在進行中")
                return False
            
            # 驗證參數
            if not self._validate_download_parameters(download_params):
                return False
            
            # 創建並配置工作執行緒
            self.current_worker = YtDlpDownloadWorker(
                download_params, 
                self.executable_path
            )
            
            # 連接信號
            self.current_worker.download_started.connect(self._on_download_started)
            self.current_worker.progress_updated.connect(self._on_progress_updated)
            self.current_worker.download_completed.connect(self._on_download_completed)
            self.current_worker.download_error.connect(self._on_download_error)
            
            # 開始下載
            self.current_worker.start()
            self.is_downloading = True
            
            logger.info(f"Started download for URL: {download_params.url}")
            return True
            
        except Exception as e:
            error_msg = f"啟動下載失敗: {str(e)}"
            logger.error(error_msg)
            self.download_error.emit(error_msg)
            return False
    
    def start_batch_download(self, download_list: List[DownloadParameters]) -> bool:
        """開始批次下載"""
        try:
            # 檢查是否已經在下載
            if self.is_batch_downloading:
                logger.warning("Batch download already in progress")
                self.download_error.emit("已有批次下載任務正在進行中")
                return False
            
            # 驗證參數列表
            for i, params in enumerate(download_list):
                if not self._validate_download_parameters(params):
                    self.download_error.emit(f"第 {i+1} 個下載參數無效")
                    return False
            
            # 創建批次工作執行緒
            self.batch_worker = YtDlpBatchWorker(
                download_list,
                self.executable_path
            )
            
            # 連接信號
            self.batch_worker.batch_started.connect(self._on_batch_started)
            self.batch_worker.item_started.connect(self._on_batch_item_started)
            self.batch_worker.item_progress.connect(self._on_batch_item_progress)
            self.batch_worker.item_completed.connect(self._on_batch_item_completed)
            self.batch_worker.batch_completed.connect(self._on_batch_completed)
            self.batch_worker.batch_error.connect(self._on_download_error)
            
            # 開始批次下載
            self.batch_worker.start()
            self.is_batch_downloading = True
            
            logger.info(f"Started batch download with {len(download_list)} items")
            return True
            
        except Exception as e:
            error_msg = f"啟動批次下載失敗: {str(e)}"
            logger.error(error_msg)
            self.download_error.emit(error_msg)
            return False
    
    def cancel_download(self):
        """取消當前下載"""
        try:
            if self.current_worker and self.is_downloading:
                logger.info("Cancelling current download")
                self.current_worker.cancel_download()
                
                # 等待工作執行緒結束
                if self.current_worker.isRunning():
                    self.current_worker.wait(timeout=5000)  # 5秒超時
                
                self.is_downloading = False
                logger.info("Download cancelled successfully")
            
            if self.batch_worker and self.is_batch_downloading:
                logger.info("Cancelling batch download")
                self.batch_worker.cancel_batch()
                
                # 等待工作執行緒結束
                if self.batch_worker.isRunning():
                    self.batch_worker.wait(timeout=5000)
                
                self.is_batch_downloading = False
                logger.info("Batch download cancelled successfully")
                
        except Exception as e:
            logger.error(f"Error cancelling download: {e}")
    
    def add_to_queue(self, download_params: DownloadParameters):
        """添加到下載佇列"""
        self.download_queue.add(download_params)
        logger.info(f"Added to download queue: {download_params.url}")
    
    def get_queue_status(self) -> Dict[str, int]:
        """獲取佇列狀態"""
        return {
            'pending': self.download_queue.total_pending,
            'active': self.download_queue.total_active,
            'completed': self.download_queue.total_completed
        }
    
    def get_download_history(self) -> List[DownloadResult]:
        """獲取下載歷史"""
        return self.download_history.copy()
    
    def clear_download_history(self):
        """清除下載歷史"""
        self.download_history.clear()
        logger.info("Download history cleared")
    
    def get_settings(self) -> Dict[str, Any]:
        """獲取設定"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """更新設定"""
        self.settings.update(new_settings)
        self._save_settings()
        logger.info("Settings updated")
    
    def export_history(self, file_path: str, format_type: str = 'json') -> bool:
        """匯出下載歷史"""
        try:
            if not self.download_history:
                logger.warning("No download history to export")
                return False
            
            # 準備匯出資料
            export_data = {
                'export_time': time.time(),
                'total_downloads': len(self.download_history),
                'history': [result.to_dict() for result in self.download_history]
            }
            
            # 根據格式匯出
            if format_type.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            elif format_type.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL', 'Title', 'Status', 'File Size', 'Duration', 'Download Time', 'Error'])
                    
                    for result in self.download_history:
                        writer.writerow([
                            result.url,
                            result.title,
                            result.status.value,
                            result.file_size or 0,
                            result.duration or 0,
                            result.download_time or 0,
                            result.error_message or ''
                        ])
            
            logger.info(f"History exported to: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"匯出歷史失敗: {str(e)}"
            logger.error(error_msg)
            self.download_error.emit(error_msg)
            return False
    
    def _validate_download_parameters(self, params: DownloadParameters) -> bool:
        """驗證下載參數"""
        try:
            # 檢查 URL 是否為空
            if not params.url or not params.url.strip():
                self.download_error.emit("URL 不能為空")
                return False
            
            # 檢查輸出目錄是否存在
            output_dir = Path(params.output_dir)
            if not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.download_error.emit(f"無法創建輸出目錄: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating download parameters: {e}")
            self.download_error.emit(f"參數驗證失敗: {str(e)}")
            return False
    
    # 工作執行緒信號處理器
    def _on_download_started(self):
        """下載開始"""
        self.download_started.emit()
    
    def _on_progress_updated(self, progress: DownloadProgress):
        """進度更新"""
        self.download_progress.emit(progress)
    
    def _on_download_completed(self, result: DownloadResult):
        """下載完成"""
        self.download_history.append(result)
        
        # 限制歷史記錄數量
        if len(self.download_history) > self.max_history:
            self.download_history = self.download_history[-self.max_history:]
        
        self.is_downloading = False
        self.download_result.emit(result)
        
        # 創建摘要
        summary = DownloadSummary()
        summary.total_downloads = 1
        if result.status == DownloadStatus.COMPLETED:
            summary.successful_downloads = 1
        else:
            summary.failed_downloads = 1
            if result.error_message:
                summary.errors.append(result.error_message)
        
        self.download_completed.emit(summary)
        
        # 清理工作執行緒
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def _on_download_error(self, error_message: str):
        """下載錯誤"""
        self.is_downloading = False
        self.is_batch_downloading = False
        self.download_error.emit(error_message)
        
        # 清理工作執行緒
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
        
        if self.batch_worker:
            self.batch_worker.deleteLater()
            self.batch_worker = None
    
    # 批次下載信號處理器
    def _on_batch_started(self, total_count: int):
        """批次下載開始"""
        self.batch_started.emit(total_count)
    
    def _on_batch_item_started(self, index: int, url: str):
        """批次項目開始"""
        self.batch_item_started.emit(index, url)
    
    def _on_batch_item_progress(self, index: int, progress: DownloadProgress):
        """批次項目進度"""
        self.batch_item_progress.emit(index, progress)
    
    def _on_batch_item_completed(self, index: int, result: DownloadResult):
        """批次項目完成"""
        self.download_history.append(result)
        self.batch_item_completed.emit(index, result)
    
    def _on_batch_completed(self, summary: DownloadSummary):
        """批次下載完成"""
        self.is_batch_downloading = False
        self.batch_completed.emit(summary)
        
        # 清理工作執行緒
        if self.batch_worker:
            self.batch_worker.deleteLater()
            self.batch_worker = None
    
    def cleanup(self):
        """清理資源"""
        try:
            # 取消當前下載
            if self.is_downloading or self.is_batch_downloading:
                self.cancel_download()
            
            # 清理工作執行緒
            if self.current_worker:
                self.current_worker.deleteLater()
                self.current_worker = None
            
            if self.batch_worker:
                self.batch_worker.deleteLater()
                self.batch_worker = None
            
            # 保存設定
            self._save_settings()
            
            logger.info("YtDlpModel cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")