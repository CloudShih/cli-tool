"""
YT-DLP Controller - 控制器層，協調模型和視圖
"""
import logging
from typing import Optional, List
from PyQt5.QtCore import QObject, QTimer

from .yt_dlp_model import YtDlpModel
from .yt_dlp_view import YtDlpView
from .core.data_models import (
    DownloadParameters, DownloadResult, DownloadProgress, 
    DownloadSummary, VideoInfo
)

logger = logging.getLogger(__name__)


class YtDlpController(QObject):
    """YT-DLP 控制器 - 協調模型和視圖的互動"""
    
    def __init__(self, model: YtDlpModel, view: YtDlpView):
        super().__init__()
        self.model = model
        self.view = view
        
        # 狀態追蹤
        self.current_batch_size = 0
        self.completed_downloads = 0
        
        # 設定定時器用於狀態更新
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.setInterval(1000)  # 每秒更新一次
        
        self._setup_connections()
        self._initialize()
    
    def _setup_connections(self):
        """設定信號連接"""
        # 視圖 → 控制器信號
        self.view.download_requested.connect(self._on_download_requested)
        self.view.download_cancelled.connect(self._on_download_cancelled)
        self.view.video_info_requested.connect(self._on_video_info_requested)
        self.view.formats_requested.connect(self._on_formats_requested)
        
        # 模型 → 控制器信號 (單個下載)
        self.model.download_started.connect(self._on_download_started)
        self.model.download_progress.connect(self._on_download_progress)
        self.model.download_result.connect(self._on_download_result)
        self.model.download_completed.connect(self._on_download_completed)
        self.model.download_error.connect(self._on_download_error)
        
        # 模型 → 控制器信號 (批次下載)
        self.model.batch_started.connect(self._on_batch_started)
        self.model.batch_item_started.connect(self._on_batch_item_started)
        self.model.batch_item_progress.connect(self._on_batch_item_progress)
        self.model.batch_item_completed.connect(self._on_batch_item_completed)
        self.model.batch_completed.connect(self._on_batch_completed)
        
        # 模型 → 控制器信號 (資訊獲取)
        self.model.video_info_received.connect(self._on_video_info_received)
        self.model.formats_received.connect(self._on_formats_received)
    
    def _initialize(self):
        """初始化控制器"""
        try:
            # 檢查模型可用性
            if not self.model.is_available():
                self.view.show_error("YT-DLP 工具不可用，請確保已安裝 yt-dlp")
                return
            
            # 獲取版本資訊
            version_info = self.model.get_version_info()
            logger.info(f"YT-DLP controller initialized with version: {version_info}")
            
            # 載入設定
            settings = self.model.get_settings()
            self._apply_settings_to_view(settings)
            
        except Exception as e:
            logger.error(f"Error initializing yt-dlp controller: {e}")
            self.view.show_error(f"初始化失敗: {str(e)}")
    
    def _apply_settings_to_view(self, settings: dict):
        """將設定應用到視圖"""
        try:
            # 應用輸出目錄設定
            if 'default_output_dir' in settings:
                self.view.settings_widget.output_dir_edit.setText(settings['default_output_dir'])
            
            # 應用格式設定
            if 'default_quality' in settings:
                format_selector = self.view.format_selector
                format_selector.set_format_selector(settings['default_quality'])
            
            # 應用字幕設定
            if 'auto_subtitle' in settings:
                self.view.settings_widget.auto_subtitles_check.setChecked(settings['auto_subtitle'])
            
            if 'embed_subtitle' in settings:
                self.view.settings_widget.embed_subtitles_check.setChecked(settings['embed_subtitle'])
            
            # 應用音訊設定
            if 'extract_audio' in settings:
                self.view.format_selector.extract_audio_check.setChecked(settings['extract_audio'])
            
            if 'keep_video' in settings:
                self.view.format_selector.keep_video_check.setChecked(settings['keep_video'])
            
            # 應用網路設定
            if 'retry_count' in settings:
                self.view.settings_widget.retries_spin.setValue(settings['retry_count'])
            
        except Exception as e:
            logger.warning(f"Error applying settings to view: {e}")
    
    def _on_download_requested(self, download_items: List[DownloadParameters]):
        """處理下載請求"""
        try:
            logger.info(f"Download requested for {len(download_items)} items")
            
            # 檢查是否已經在下載
            if self.model.is_downloading or self.model.is_batch_downloading:
                self.view.show_error("已有下載任務正在進行中")
                return
            
            # 驗證下載項目
            if not download_items:
                self.view.show_error("沒有下載項目")
                return
            
            # 重置進度顯示
            self.view.progress_display.reset()
            self.current_batch_size = len(download_items)
            self.completed_downloads = 0
            
            # 保存當前設定
            self._save_current_settings()
            
            # 開始下載
            if len(download_items) == 1:
                # 單個下載
                success = self.model.start_download(download_items[0])
                if not success:
                    self.view.show_error("無法啟動下載")
            else:
                # 批次下載
                success = self.model.start_batch_download(download_items)
                if not success:
                    self.view.show_error("無法啟動批次下載")
                
        except Exception as e:
            logger.error(f"Error handling download request: {e}")
            self.view.show_error(f"下載請求處理失敗: {str(e)}")
    
    def _on_download_cancelled(self):
        """處理下載取消"""
        try:
            logger.info("Download cancellation requested")
            self.model.cancel_download()
            
        except Exception as e:
            logger.error(f"Error cancelling download: {e}")
            self.view.show_error(f"取消下載失敗: {str(e)}")
    
    def _on_video_info_requested(self, url: str):
        """處理影片資訊請求"""
        try:
            logger.info(f"Video info requested for: {url}")
            
            # 先驗證 URL
            if not self.model.validate_url(url):
                self.view.show_error("URL 不受支援或無效")
                return
            
            # 獲取影片資訊
            success = self.model.get_video_info(url)
            if not success:
                self.view.show_error("無法獲取影片資訊")
                
        except Exception as e:
            logger.error(f"Error handling video info request: {e}")
            self.view.show_error(f"影片資訊請求處理失敗: {str(e)}")
    
    def _on_formats_requested(self, url: str):
        """處理格式列表請求"""
        try:
            logger.info(f"Formats requested for: {url}")
            
            success = self.model.get_available_formats(url)
            if not success:
                self.view.show_error("無法獲取格式列表")
                
        except Exception as e:
            logger.error(f"Error handling formats request: {e}")
            self.view.show_error(f"格式列表請求處理失敗: {str(e)}")
    
    def _save_current_settings(self):
        """保存當前設定"""
        try:
            # 從視圖收集設定
            settings = {}
            
            # 輸出目錄
            settings['default_output_dir'] = self.view.settings_widget.output_dir_edit.text()
            
            # 格式設定
            settings['default_quality'] = self.view.format_selector.get_format_selector()
            settings['extract_audio'] = self.view.format_selector.is_extract_audio()
            settings['keep_video'] = self.view.format_selector.is_keep_video()
            settings['audio_format'] = self.view.format_selector.get_audio_format()
            
            # 字幕設定
            settings['auto_subtitle'] = self.view.settings_widget.auto_subtitles_check.isChecked()
            settings['embed_subtitle'] = self.view.settings_widget.embed_subtitles_check.isChecked()
            
            # 網路設定
            settings['retry_count'] = self.view.settings_widget.retries_spin.value()
            
            # 更新模型設定
            self.model.update_settings(settings)
            
        except Exception as e:
            logger.warning(f"Error saving current settings: {e}")
    
    # 單個下載信號處理器
    def _on_download_started(self):
        """下載開始"""
        try:
            self.view.set_downloading_state(True)
            self.status_timer.start()
            logger.info("Single download started")
            
        except Exception as e:
            logger.error(f"Error handling download started: {e}")
    
    def _on_download_progress(self, progress: DownloadProgress):
        """下載進度更新"""
        try:
            self.view.update_download_progress(progress)
            
        except Exception as e:
            logger.error(f"Error handling download progress: {e}")
    
    def _on_download_result(self, result: DownloadResult):
        """下載結果"""
        try:
            self.view.add_download_result(result)
            
        except Exception as e:
            logger.error(f"Error handling download result: {e}")
    
    def _on_download_completed(self, summary: DownloadSummary):
        """下載完成"""
        try:
            logger.info(f"Single download completed: {summary.total_downloads} total")
            
            self.status_timer.stop()
            self.view.set_downloading_state(False)
            
            # 顯示完成訊息
            if summary.successful_downloads > 0:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.view, "下載完成", 
                    f"下載完成！成功: {summary.successful_downloads}, 失敗: {summary.failed_downloads}"
                )
            
        except Exception as e:
            logger.error(f"Error handling download completion: {e}")
    
    def _on_download_error(self, error_message: str):
        """下載錯誤"""
        try:
            logger.error(f"Download error: {error_message}")
            
            self.status_timer.stop()
            self.view.show_error(error_message)
            
        except Exception as e:
            logger.error(f"Error handling download error: {e}")
    
    # 批次下載信號處理器
    def _on_batch_started(self, total_count: int):
        """批次下載開始"""
        try:
            logger.info(f"Batch download started with {total_count} items")
            
            self.view.set_downloading_state(True)
            self.current_batch_size = total_count
            self.completed_downloads = 0
            self.status_timer.start()
            
        except Exception as e:
            logger.error(f"Error handling batch started: {e}")
    
    def _on_batch_item_started(self, index: int, url: str):
        """批次項目開始"""
        try:
            logger.debug(f"Batch item {index} started: {url}")
            self.view.update_batch_item_status(index, "downloading")
            
        except Exception as e:
            logger.error(f"Error handling batch item started: {e}")
    
    def _on_batch_item_progress(self, index: int, progress: DownloadProgress):
        """批次項目進度"""
        try:
            # 更新當前項目的進度
            self.view.update_download_progress(progress)
            
        except Exception as e:
            logger.error(f"Error handling batch item progress: {e}")
    
    def _on_batch_item_completed(self, index: int, result: DownloadResult):
        """批次項目完成"""
        try:
            logger.debug(f"Batch item {index} completed: {result.status.value}")
            
            # 更新項目狀態
            self.view.update_batch_item_status(index, result.status.value)
            
            # 添加到歷史記錄
            self.view.add_download_result(result)
            
            # 更新完成計數
            self.completed_downloads += 1
            
        except Exception as e:
            logger.error(f"Error handling batch item completed: {e}")
    
    def _on_batch_completed(self, summary: DownloadSummary):
        """批次下載完成"""
        try:
            logger.info(f"Batch download completed: {summary.total_downloads} total, "
                       f"{summary.successful_downloads} successful, {summary.failed_downloads} failed")
            
            self.status_timer.stop()
            self.view.set_downloading_state(False)
            
            # 顯示完成訊息
            from PyQt5.QtWidgets import QMessageBox
            message = f"""批次下載完成！
            
總計: {summary.total_downloads}
成功: {summary.successful_downloads}
失敗: {summary.failed_downloads}
總大小: {self._format_file_size(summary.total_size)}
總時間: {self._format_duration(summary.download_time)}"""
            
            if summary.successful_downloads > 0:
                QMessageBox.information(self.view, "批次下載完成", message)
            else:
                QMessageBox.warning(self.view, "批次下載完成", message)
            
        except Exception as e:
            logger.error(f"Error handling batch completion: {e}")
    
    # 資訊獲取信號處理器
    def _on_video_info_received(self, info: VideoInfo):
        """影片資訊接收"""
        try:
            self.view.show_video_info(info)
            
        except Exception as e:
            logger.error(f"Error handling video info received: {e}")
    
    def _on_formats_received(self, formats: List[dict]):
        """格式列表接收"""
        try:
            # 可以在這裡處理格式列表，例如顯示在對話框中
            logger.info(f"Received {len(formats)} formats")
            
        except Exception as e:
            logger.error(f"Error handling formats received: {e}")
    
    def _update_status(self):
        """更新狀態資訊"""
        try:
            if self.model.is_downloading or self.model.is_batch_downloading:
                # 顯示進度資訊
                if self.current_batch_size > 1:
                    status_text = f"批次下載進行中... ({self.completed_downloads}/{self.current_batch_size})"
                else:
                    status_text = "下載進行中..."
                
                self.view.status_label.setText(status_text)
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    def get_model_info(self) -> dict:
        """獲取模型資訊"""
        try:
            return {
                'available': self.model.is_available(),
                'version': self.model.get_version_info(),
                'executable_path': self.model.executable_path,
                'is_downloading': self.model.is_downloading,
                'is_batch_downloading': self.model.is_batch_downloading,
                'queue_status': self.model.get_queue_status(),
                'history_count': len(self.model.get_download_history())
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
            
            # 取消當前下載
            if self.model.is_downloading or self.model.is_batch_downloading:
                self.model.cancel_download()
            
            # 保存當前設定
            self._save_current_settings()
            
            # 清理模型
            self.model.cleanup()
            
            logger.info("YT-DLP controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during controller cleanup: {e}")
    
    # 便利方法
    def start_quick_download(self, url: str) -> bool:
        """快速下載便利方法"""
        try:
            # 使用當前設定創建下載參數
            params = self.view.settings_widget.get_download_parameters(url)
            
            # 應用格式設定
            params.format_selector = self.view.format_selector.get_format_selector()
            params.audio_format = self.view.format_selector.get_audio_format()
            params.extract_audio = self.view.format_selector.is_extract_audio()
            params.keep_video = self.view.format_selector.is_keep_video()
            
            # 開始下載
            return self.model.start_download(params)
            
        except Exception as e:
            logger.error(f"Error starting quick download: {e}")
            return False
    
    def get_download_statistics(self) -> dict:
        """獲取下載統計"""
        try:
            history = self.model.get_download_history()
            
            total_downloads = len(history)
            successful = sum(1 for result in history if result.status.value == "completed")
            failed = total_downloads - successful
            
            total_size = sum(result.file_size or 0 for result in history)
            total_time = sum(result.download_time or 0 for result in history)
            
            return {
                'total_downloads': total_downloads,
                'successful_downloads': successful,
                'failed_downloads': failed,
                'success_rate': (successful / total_downloads * 100) if total_downloads > 0 else 0,
                'total_size': total_size,
                'total_time': total_time,
                'average_speed': (total_size / total_time) if total_time > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting download statistics: {e}")
            return {}
    
    def export_download_history(self, file_path: str, format_type: str = 'json') -> bool:
        """匯出下載歷史"""
        try:
            return self.model.export_history(file_path, format_type)
        except Exception as e:
            logger.error(f"Error exporting download history: {e}")
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        try:
            from .core.data_models import format_file_size
            return format_file_size(size_bytes)
        except:
            return f"{size_bytes} B"
    
    def _format_duration(self, seconds: float) -> str:
        """格式化時長"""
        try:
            from .core.data_models import format_duration
            return format_duration(seconds)
        except:
            return f"{seconds:.1f}秒"