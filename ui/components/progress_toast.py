"""
進度吐司通知組件 - 用於顯示非阻塞的進度反饋
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QPoint
)
from PyQt5.QtGui import QFont, QColor

from .indicators import LoadingSpinner, ProgressIndicator

logger = logging.getLogger(__name__)


class ProgressToast(QFrame):
    """進度吐司通知"""
    
    def __init__(self, parent=None, message="處理中...", duration=3000):
        super().__init__(parent)
        self.duration = duration
        self.message = message
        self.is_showing = False
        
        self.setup_ui()
        self.setup_animations()
        self.hide()
    
    def setup_ui(self):
        """設置 UI"""
        self.setProperty("progress-toast", True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # 載入旋轉器
        self.spinner = LoadingSpinner(24)
        layout.addWidget(self.spinner)
        
        # 訊息區域
        message_layout = QVBoxLayout()
        message_layout.setSpacing(4)
        
        # 主要訊息
        self.message_label = QLabel(self.message)
        self.message_label.setProperty("toast-message", True)
        message_layout.addWidget(self.message_label)
        
        # 詳細訊息（可選）
        self.detail_label = QLabel()
        self.detail_label.setProperty("toast-detail", True)
        self.detail_label.hide()
        message_layout.addWidget(self.detail_label)
        
        layout.addLayout(message_layout, 1)
        
        self.setLayout(layout)
    
    def setup_animations(self):
        """設置動畫"""
        # 淡入淡出動畫
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 滑入滑出動畫
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(400)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 自動隱藏計時器
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_with_animation)
    
    def show_toast(self, message: str = "", detail: str = "", duration: int = None):
        """顯示吐司通知"""
        if self.is_showing:
            return
        
        if message:
            self.message = message
            self.message_label.setText(message)
        
        if detail:
            self.detail_label.setText(detail)
            self.detail_label.show()
        else:
            self.detail_label.hide()
        
        if duration is not None:
            self.duration = duration
        
        self.is_showing = True
        
        # 設置初始位置（右下角外側）
        if self.parent():
            parent_rect = self.parent().rect()
            start_pos = QPoint(
                parent_rect.right() - self.width() - 20,
                parent_rect.bottom()  # 開始在底部外側
            )
            end_pos = QPoint(
                parent_rect.right() - self.width() - 20,
                parent_rect.bottom() - self.height() - 20
            )
            
            self.move(start_pos)
        
        # 顯示並開始動畫
        self.show()
        self.raise_()
        
        # 開始載入動畫
        self.spinner.start_spinning()
        
        # 淡入動畫
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
        # 滑入動畫
        if self.parent():
            self.slide_animation.setStartValue(start_pos)
            self.slide_animation.setEndValue(end_pos)
            self.slide_animation.start()
        
        # 設置自動隱藏
        if self.duration > 0:
            self.hide_timer.start(self.duration)
        
        logger.debug(f"Showing progress toast: {message}")
    
    def hide_with_animation(self):
        """帶動畫隱藏吐司通知"""
        if not self.is_showing:
            return
        
        self.is_showing = False
        self.hide_timer.stop()
        
        # 停止載入動畫
        self.spinner.stop_spinning()
        
        # 淡出動畫
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
        logger.debug("Hiding progress toast")
    
    def update_message(self, message: str, detail: str = ""):
        """更新訊息"""
        if self.is_showing:
            self.message_label.setText(message)
            if detail:
                self.detail_label.setText(detail)
                self.detail_label.show()
            else:
                self.detail_label.hide()
    
    def resizeEvent(self, event):
        """調整大小事件 - 確保吐司通知在正確位置"""
        super().resizeEvent(event)
        if self.is_showing and self.parent():
            parent_rect = self.parent().rect()
            new_pos = QPoint(
                parent_rect.right() - self.width() - 20,
                parent_rect.bottom() - self.height() - 20
            )
            self.move(new_pos)


class ToastManager:
    """吐司通知管理器 - 管理多個吐司通知"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.active_toasts = []
        self.toast_spacing = 10
    
    def show_progress_toast(self, message: str, detail: str = "", duration: int = 3000) -> ProgressToast:
        """顯示進度吐司通知"""
        toast = ProgressToast(self.parent, message, duration)
        
        # 計算位置（堆疊顯示）
        if self.parent():
            parent_rect = self.parent().rect()
            y_offset = sum(t.height() + self.toast_spacing for t in self.active_toasts)
            
            toast.move(
                parent_rect.right() - toast.width() - 20,
                parent_rect.bottom() - toast.height() - 20 - y_offset
            )
        
        # 當吐司隱藏時從列表移除
        def on_toast_hidden():
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
                self.reposition_toasts()
        
        toast.fade_animation.finished.connect(on_toast_hidden)
        
        self.active_toasts.append(toast)
        toast.show_toast(message, detail, duration)
        
        return toast
    
    def reposition_toasts(self):
        """重新定位吐司通知"""
        if not self.parent():
            return
        
        parent_rect = self.parent().rect()
        y_offset = 0
        
        for toast in reversed(self.active_toasts):  # 從底部開始
            if toast.is_showing:
                new_pos = QPoint(
                    parent_rect.right() - toast.width() - 20,
                    parent_rect.bottom() - toast.height() - 20 - y_offset
                )
                
                # 使用動畫移動到新位置
                toast.slide_animation.setStartValue(toast.pos())
                toast.slide_animation.setEndValue(new_pos)
                toast.slide_animation.start()
                
                y_offset += toast.height() + self.toast_spacing
    
    def hide_all_toasts(self):
        """隱藏所有吐司通知"""
        for toast in self.active_toasts[:]:  # 複製列表以避免修改時的問題
            toast.hide_with_animation()


# 全域吐司管理器實例
_global_toast_manager = None

def get_toast_manager(parent=None) -> ToastManager:
    """獲取全域吐司管理器"""
    global _global_toast_manager
    if _global_toast_manager is None or (parent and _global_toast_manager.parent != parent):
        _global_toast_manager = ToastManager(parent)
    return _global_toast_manager

def show_progress_toast(message: str, detail: str = "", duration: int = 3000, parent=None) -> ProgressToast:
    """便利函數 - 顯示進度吐司通知"""
    manager = get_toast_manager(parent)
    return manager.show_progress_toast(message, detail, duration)