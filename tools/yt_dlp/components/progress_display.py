"""
進度顯示器組件
顯示下載進度和狀態資訊
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, 
    QLabel, QFrame, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from ..core.data_models import DownloadProgress, DownloadResult, DownloadStatus


class ProgressDisplay(QWidget):
    """進度顯示器組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress: DownloadProgress = None
        self.setup_ui()
        
        # 定時器用於更新顯示
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.setInterval(1000)  # 每秒更新
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 當前下載狀態
        status_group = QGroupBox("下載狀態")
        status_layout = QVBoxLayout(status_group)
        
        # 狀態標籤
        self.status_label = QLabel("準備就緒")
        status_font = QFont()
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # 當前檔案
        self.filename_label = QLabel("")
        self.filename_label.setWordWrap(True)
        self.filename_label.setStyleSheet("color: #666; font-size: 11px;")
        status_layout.addWidget(self.filename_label)
        
        layout.addWidget(status_group)
        
        # 進度條區域
        progress_group = QGroupBox("下載進度")
        progress_layout = QVBoxLayout(progress_group)
        
        # 主進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        # 進度資訊
        info_layout = QHBoxLayout()
        
        # 速度資訊
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("下載速度:"))
        self.speed_label = QLabel("0 B/s")
        self.speed_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        speed_layout.addWidget(self.speed_label)
        info_layout.addLayout(speed_layout)
        
        # 大小資訊
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("檔案大小:"))
        self.size_label = QLabel("未知")
        self.size_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        size_layout.addWidget(self.size_label)
        info_layout.addLayout(size_layout)
        
        # 時間資訊
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel("剩餘時間:"))
        self.eta_label = QLabel("未知")
        self.eta_label.setStyleSheet("font-weight: bold; color: #0078d4;")
        time_layout.addWidget(self.eta_label)
        info_layout.addLayout(time_layout)
        
        progress_layout.addLayout(info_layout)
        layout.addWidget(progress_group)
        
        # 詳細資訊區域
        details_group = QGroupBox("詳細資訊")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        layout.addStretch()
    
    def update_progress(self, progress: DownloadProgress):
        """更新下載進度"""
        self.current_progress = progress
        
        # 更新狀態
        status_text = self._get_status_text(progress.status)
        self.status_label.setText(status_text)
        
        # 更新檔案名
        if progress.filename:
            self.filename_label.setText(f"檔案: {progress.filename}")
        
        # 更新進度條
        if progress.percentage is not None:
            self.progress_bar.setValue(int(progress.percentage))
            self.progress_bar.setFormat(f"{progress.percentage:.1f}%")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("準備中...")
        
        # 更新速度
        self.speed_label.setText(progress.speed_str)
        
        # 更新大小
        if progress.total_bytes:
            from ..core.data_models import format_file_size
            downloaded = format_file_size(progress.downloaded_bytes)
            total = format_file_size(progress.total_bytes)
            self.size_label.setText(f"{downloaded} / {total}")
        else:
            self.size_label.setText("未知")
        
        # 更新剩餘時間
        self.eta_label.setText(progress.eta_str)
        
        # 更新詳細資訊
        self._update_details()
        
        # 啟動更新定時器
        if not self.update_timer.isActive() and progress.status == "downloading":
            self.update_timer.start()
        elif progress.status in ["completed", "error", "cancelled"]:
            self.update_timer.stop()
    
    def update_result(self, result: DownloadResult):
        """更新下載結果"""
        if result.status == DownloadStatus.COMPLETED:
            self.status_label.setText("✅ 下載完成")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("100%")
            
            # 顯示輸出檔案
            if result.output_files:
                files_text = "\n".join(result.output_files)
                self.details_text.setText(f"輸出檔案:\n{files_text}")
            
        elif result.status == DownloadStatus.ERROR:
            self.status_label.setText("❌ 下載失敗")
            self.progress_bar.setFormat("失敗")
            
            # 顯示錯誤訊息
            if result.error_message:
                self.details_text.setText(f"錯誤訊息:\n{result.error_message}")
        
        elif result.status == DownloadStatus.CANCELLED:
            self.status_label.setText("⏹ 已取消")
            self.progress_bar.setFormat("已取消")
        
        # 停止定時器
        self.update_timer.stop()
    
    def reset(self):
        """重置顯示"""
        self.current_progress = None
        self.status_label.setText("準備就緒")
        self.filename_label.setText("")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")
        self.speed_label.setText("0 B/s")
        self.size_label.setText("未知")
        self.eta_label.setText("未知")
        self.details_text.clear()
        self.update_timer.stop()
    
    def _get_status_text(self, status: str) -> str:
        """獲取狀態文字"""
        status_map = {
            "idle": "⏸ 準備就緒",
            "preparing": "🔄 準備中",
            "downloading": "⬇️ 下載中",
            "extracting": "🔧 提取中",
            "post_processing": "⚙️ 後處理",
            "completed": "✅ 完成",
            "cancelled": "⏹ 已取消",
            "error": "❌ 錯誤"
        }
        return status_map.get(status, f"📋 {status}")
    
    def _update_display(self):
        """定時更新顯示"""
        if not self.current_progress:
            return
        
        # 更新經過時間
        if self.current_progress.elapsed:
            elapsed_str = self._format_time(self.current_progress.elapsed)
            
            # 更新詳細資訊中的時間
            details = self.details_text.toPlainText()
            if "經過時間:" not in details:
                if details:
                    details += f"\n經過時間: {elapsed_str}"
                else:
                    details = f"經過時間: {elapsed_str}"
                self.details_text.setText(details)
    
    def _update_details(self):
        """更新詳細資訊"""
        if not self.current_progress:
            return
        
        details = []
        
        # 狀態資訊
        details.append(f"狀態: {self.current_progress.status}")
        
        # 已下載位元組
        if self.current_progress.downloaded_bytes > 0:
            from ..core.data_models import format_file_size
            details.append(f"已下載: {format_file_size(self.current_progress.downloaded_bytes)}")
        
        # 片段資訊
        if (self.current_progress.fragment_index is not None 
            and self.current_progress.fragment_count is not None):
            details.append(f"片段: {self.current_progress.fragment_index}/{self.current_progress.fragment_count}")
        
        # 經過時間
        if self.current_progress.elapsed:
            elapsed_str = self._format_time(self.current_progress.elapsed)
            details.append(f"經過時間: {elapsed_str}")
        
        self.details_text.setText("\n".join(details))
    
    def _format_time(self, seconds: float) -> str:
        """格式化時間"""
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}小時{minutes}分{secs}秒"