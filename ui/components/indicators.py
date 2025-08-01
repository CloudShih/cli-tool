"""
載入指示器和狀態指示器組件
提供各種載入動畫和狀態反饋
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QProgressBar, QHBoxLayout, QVBoxLayout,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QSize
)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPalette
import math
import logging

logger = logging.getLogger(__name__)


class LoadingSpinner(QWidget):
    """載入旋轉器 - 顯示旋轉的載入動畫"""
    
    def __init__(self, size=32, color=None, parent=None):
        super().__init__(parent)
        self.size = size
        self.color = color or QColor(70, 130, 180)  # 預設藍色
        self.angle = 0
        self.is_spinning = False
        
        self.setFixedSize(size, size)
        self.setup_animation()
    
    def setup_animation(self):
        """設置動畫"""
        self.timer = QTimer(self)  # 設置父對象確保在正確線程中
        self.timer.timeout.connect(self.rotate)
        self.timer.setInterval(50)  # 50ms 間隔
    
    def start_spinning(self):
        """開始旋轉"""
        if not self.is_spinning:
            self.is_spinning = True
            self.timer.start()
            self.show()
    
    def stop_spinning(self):
        """停止旋轉"""
        if self.is_spinning:
            self.is_spinning = False
            self.timer.stop()
            self.hide()
    
    def rotate(self):
        """旋轉步進"""
        self.angle = (self.angle + 30) % 360
        self.update()
    
    def paintEvent(self, event):
        """繪製旋轉器"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 設置畫筆
        pen = QPen(self.color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # 繪製旋轉的線條
        center = self.rect().center()
        radius = self.size // 2 - 4
        
        for i in range(8):
            angle = self.angle + i * 45
            opacity = max(0.1, 1.0 - i * 0.12)  # 漸變透明度
            
            # 計算線條位置
            start_radius = radius * 0.3
            end_radius = radius * 0.8
            
            start_x = int(center.x() + start_radius * math.cos(math.radians(angle)))
            start_y = int(center.y() + start_radius * math.sin(math.radians(angle)))
            end_x = int(center.x() + end_radius * math.cos(math.radians(angle)))
            end_y = int(center.y() + end_radius * math.sin(math.radians(angle)))
            
            # 設置透明度
            color = QColor(self.color)
            color.setAlphaF(opacity)
            pen.setColor(color)
            painter.setPen(pen)
            
            # 繪製線條
            painter.drawLine(start_x, start_y, end_x, end_y)


class ProgressIndicator(QWidget):
    """進度指示器 - 顯示任務進度"""
    
    progress_changed = pyqtSignal(int)  # 進度變更信號
    
    def __init__(self, show_percentage=True, show_text=True, parent=None):
        super().__init__(parent)
        self.show_percentage = show_percentage
        self.show_text = show_text
        self.current_progress = 0
        self.status_text = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """設置 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(self.show_percentage)
        layout.addWidget(self.progress_bar, 1)
        
        # 狀態文字
        if self.show_text:
            self.status_label = QLabel("準備中...")
            self.status_label.setMinimumWidth(100)
            layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def set_progress(self, value: int, text: str = ""):
        """設置進度"""
        self.current_progress = max(0, min(100, value))
        self.progress_bar.setValue(self.current_progress)
        
        if text and hasattr(self, 'status_label'):
            self.status_text = text
            self.status_label.setText(text)
        
        self.progress_changed.emit(self.current_progress)
    
    def set_status(self, text: str):
        """設置狀態文字"""
        if hasattr(self, 'status_label'):
            self.status_text = text
            self.status_label.setText(text)
    
    def reset(self):
        """重設進度"""
        self.set_progress(0, "準備中...")
    
    def complete(self, text: str = "完成"):
        """完成進度"""
        self.set_progress(100, text)


class StatusIndicator(QWidget):
    """狀態指示器 - 顯示系統狀態"""
    
    def __init__(self, initial_status="ready", parent=None):
        super().__init__(parent)
        self.current_status = initial_status
        self.status_colors = {
            "ready": QColor(34, 197, 94),      # 綠色 - 準備就緒
            "processing": QColor(251, 191, 36), # 黃色 - 處理中
            "error": QColor(239, 68, 68),       # 紅色 - 錯誤
            "warning": QColor(245, 158, 11),    # 橙色 - 警告
            "offline": QColor(107, 114, 128),   # 灰色 - 離線
            "success": QColor(34, 197, 94),     # 綠色 - 成功
        }
        
        self.setup_ui()
        self.set_status(initial_status)
    
    def setup_ui(self):
        """設置 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # 狀態點
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(12, 12)
        layout.addWidget(self.status_dot)
        
        # 狀態文字
        self.status_label = QLabel()
        font = QFont()
        font.setPointSize(9)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def set_status(self, status: str, text: str = ""):
        """設置狀態"""
        self.current_status = status
        color = self.status_colors.get(status, QColor(107, 114, 128))
        
        # 更新狀態點
        self.status_dot.setStyleSheet(f"""
            QLabel {{
                background-color: {color.name()};
                border-radius: 6px;
                border: 1px solid {color.darker(120).name()};
            }}
        """)
        
        # 更新狀態文字
        if not text:
            text = self.get_status_text(status)
        self.status_label.setText(text)
        
        # 設置工具提示
        self.setToolTip(f"狀態: {text}")
    
    def get_status_text(self, status: str) -> str:
        """獲取狀態文字"""
        status_texts = {
            "ready": "準備就緒",
            "processing": "處理中",
            "error": "錯誤",
            "warning": "警告",
            "offline": "離線",
            "success": "成功",
        }
        return status_texts.get(status, status.title())


class LoadingOverlay(QWidget):
    """載入覆蓋層 - 覆蓋整個父組件顯示載入狀態"""
    
    def __init__(self, parent=None, message="載入中..."):
        super().__init__(parent)
        self.message = message
        self.spinner = None
        
        self.setup_ui()
        self.hide()  # 初始隱藏
    
    def setup_ui(self):
        """設置 UI"""
        # 設置背景
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 載入容器
        container = QFrame()
        container.setFixedSize(200, 120)
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 8px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(16)
        
        # 旋轉器
        self.spinner = LoadingSpinner(40)
        container_layout.addWidget(self.spinner, 0, Qt.AlignCenter)
        
        # 載入文字
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        self.message_label.setFont(font)
        container_layout.addWidget(self.message_label)
        
        container.setLayout(container_layout)
        layout.addWidget(container, 0, Qt.AlignCenter)
        
        self.setLayout(layout)
    
    def show_loading(self, message: str = ""):
        """顯示載入"""
        if message:
            self.message = message
            self.message_label.setText(message)
        
        if self.parent():
            self.resize(self.parent().size())
        
        self.spinner.start_spinning()
        self.show()
        self.raise_()
    
    def hide_loading(self):
        """隱藏載入"""
        self.spinner.stop_spinning()
        self.hide()
    
    def resizeEvent(self, event):
        """調整大小事件"""
        super().resizeEvent(event)
        if self.parent():
            self.resize(self.parent().size())


class ProgressDialog(QWidget):
    """進度對話框 - 模態進度顯示"""
    
    cancelled = pyqtSignal()  # 取消信號
    
    def __init__(self, title="處理中", message="請稍候...", parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        
        self.setup_ui()
        self.setWindowTitle(title)
        self.setModal(True)
    
    def setup_ui(self):
        """設置 UI"""
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 標題
        title_label = QLabel(self.title)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # 訊息
        self.message_label = QLabel(self.message)
        layout.addWidget(self.message_label)
        
        # 進度指示器
        self.progress_indicator = ProgressIndicator(show_text=False)
        layout.addWidget(self.progress_indicator)
        
        # 取消按鈕（可選）
        from .buttons import ModernButton
        self.cancel_button = ModernButton("取消")
        self.cancel_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(self.cancel_button, 0, Qt.AlignRight)
        
        self.setLayout(layout)
    
    def set_progress(self, value: int, message: str = ""):
        """設置進度"""
        self.progress_indicator.set_progress(value)
        if message:
            self.message_label.setText(message)
    
    def set_indeterminate(self, indeterminate: bool = True):
        """設置不確定進度模式"""
        if indeterminate:
            self.progress_indicator.progress_bar.setRange(0, 0)
        else:
            self.progress_indicator.progress_bar.setRange(0, 100)


# 便利函數
def create_loading_button(button, spinner_size=16):
    """為按鈕添加載入旋轉器"""
    spinner = LoadingSpinner(spinner_size)
    
    def show_loading():
        button.setEnabled(False)
        spinner.start_spinning()
    
    def hide_loading():
        button.setEnabled(True)
        spinner.stop_spinning()
    
    button.show_loading = show_loading
    button.hide_loading = hide_loading
    
    return spinner