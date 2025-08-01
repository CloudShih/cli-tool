"""
動畫效果系統 - 為 UI 組件提供豐富的動畫效果
"""

import logging
import math
from typing import List, Dict, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFrame, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSize, QParallelAnimationGroup, QSequentialAnimationGroup,
    QAbstractAnimation
)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush

logger = logging.getLogger(__name__)


class AnimationManager:
    """動畫管理器 - 管理全局動畫效果"""
    
    def __init__(self):
        self.active_animations = {}
        self.animation_queue = []
        self.global_speed_factor = 1.0
        self.animations_enabled = True
    
    def set_animations_enabled(self, enabled: bool):
        """啟用或禁用動畫"""
        self.animations_enabled = enabled
        if not enabled:
            self.stop_all_animations()
    
    def set_speed_factor(self, factor: float):
        """設置全局動畫速度倍數"""
        self.global_speed_factor = max(0.1, min(3.0, factor))
    
    def register_animation(self, name: str, animation: QAbstractAnimation):
        """註冊動畫"""
        if not self.animations_enabled:
            return
        
        if name in self.active_animations:
            self.active_animations[name].stop()
        
        # 應用速度倍數
        original_duration = animation.duration()
        new_duration = int(original_duration / self.global_speed_factor)
        animation.setDuration(new_duration)
        
        self.active_animations[name] = animation
        animation.finished.connect(lambda: self._on_animation_finished(name))
    
    def start_animation(self, name: str):
        """啟動動畫"""
        if name in self.active_animations and self.animations_enabled:
            self.active_animations[name].start()
    
    def stop_animation(self, name: str):
        """停止動畫"""
        if name in self.active_animations:
            self.active_animations[name].stop()
    
    def stop_all_animations(self):
        """停止所有動畫"""
        for animation in self.active_animations.values():
            animation.stop()
    
    def _on_animation_finished(self, name: str):
        """動畫完成回調"""
        if name in self.active_animations:
            del self.active_animations[name]


# 全局動畫管理器實例
animation_manager = AnimationManager()


class AnimatedButton(QPushButton):
    """帶動畫效果的按鈕"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.original_geometry = None
        self.hover_animation = None
        self.click_animation = None
        self.setup_animations()
        self.setup_effects()
    
    def setup_animations(self):
        """設置動畫"""
        # 懸停動畫
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 點擊動畫
        self.click_animation = QSequentialAnimationGroup()
        
        # 按下效果
        press_animation = QPropertyAnimation(self, b"geometry")
        press_animation.setDuration(100)
        press_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 彈起效果
        release_animation = QPropertyAnimation(self, b"geometry")
        release_animation.setDuration(150)
        release_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        self.click_animation.addAnimation(press_animation)
        self.click_animation.addAnimation(release_animation)
    
    def setup_effects(self):
        """設置視覺效果"""
        # 陰影效果
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(2, 2)
        self.setGraphicsEffect(self.shadow_effect)
    
    def enterEvent(self, event):
        """滑鼠進入事件"""
        super().enterEvent(event)
        if not animation_manager.animations_enabled:
            return
        
        if not self.original_geometry:
            self.original_geometry = self.geometry()
        
        # 輕微放大效果
        target_rect = QRect(self.original_geometry)
        target_rect.adjust(-2, -2, 2, 2)
        
        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(target_rect)
        
        animation_manager.register_animation("button_hover", self.hover_animation)
        animation_manager.start_animation("button_hover")
        
        # 增強陰影效果
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setOffset(3, 3)
    
    def leaveEvent(self, event):
        """滑鼠離開事件"""
        super().leaveEvent(event)
        if not animation_manager.animations_enabled or not self.original_geometry:
            return
        
        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(self.original_geometry)
        
        animation_manager.register_animation("button_hover", self.hover_animation)
        animation_manager.start_animation("button_hover")
        
        # 恢復陰影效果
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setOffset(2, 2)
    
    def mousePressEvent(self, event):
        """滑鼠按下事件"""
        super().mousePressEvent(event)
        if not animation_manager.animations_enabled or not self.original_geometry:
            return
        
        # 按下縮小效果
        current_rect = self.geometry()
        press_rect = QRect(current_rect)
        press_rect.adjust(1, 1, -1, -1)
        
        press_animation = self.click_animation.animationAt(0)
        press_animation.setStartValue(current_rect)
        press_animation.setEndValue(press_rect)
        
        # 彈起效果
        release_animation = self.click_animation.animationAt(1)
        release_animation.setStartValue(press_rect)
        release_animation.setEndValue(current_rect)
        
        animation_manager.register_animation("button_click", self.click_animation)
        animation_manager.start_animation("button_click")


class PulseAnimation(QPropertyAnimation):
    """脈衝動畫 - 用於吸引注意力"""
    
    def __init__(self, target: QWidget, property_name: bytes = b"windowOpacity"):
        super().__init__(target, property_name)
        self.setDuration(1000)
        self.setStartValue(1.0)
        self.setEndValue(0.3)
        self.setEasingCurve(QEasingCurve.InOutQuad)
        self.setLoopCount(-1)  # 無限循環
        self.setDirection(QAbstractAnimation.Alternate)  # 來回播放


class ShakeAnimation(QSequentialAnimationGroup):
    """搖擺動畫 - 用於錯誤提示"""
    
    def __init__(self, target: QWidget, intensity: int = 10):
        super().__init__()
        original_pos = target.pos()
        
        # 創建搖擺序列
        shake_positions = [
            QPoint(original_pos.x() + intensity, original_pos.y()),
            QPoint(original_pos.x() - intensity, original_pos.y()),
            QPoint(original_pos.x() + intensity//2, original_pos.y()),
            QPoint(original_pos.x() - intensity//2, original_pos.y()),
            original_pos
        ]
        
        for i, pos in enumerate(shake_positions):
            animation = QPropertyAnimation(target, b"pos")
            animation.setDuration(50)
            animation.setStartValue(original_pos if i == 0 else shake_positions[i-1])
            animation.setEndValue(pos)
            animation.setEasingCurve(QEasingCurve.OutBounce if i == len(shake_positions)-1 else QEasingCurve.Linear)
            self.addAnimation(animation)


class TypewriterAnimation(QTimer):
    """打字機動畫 - 逐字顯示文字"""
    
    text_updated = pyqtSignal(str)
    animation_finished = pyqtSignal()
    
    def __init__(self, text: str, speed: int = 50, parent=None):
        super().__init__(parent)
        self.full_text = text
        self.current_text = ""
        self.current_index = 0
        self.speed = speed
        
        self.timeout.connect(self._update_text)
        self.setSingleShot(False)
        self.setInterval(speed)
    
    def start_animation(self):
        """開始打字機動畫"""
        self.current_text = ""
        self.current_index = 0
        self.start()
    
    def _update_text(self):
        """更新文字"""
        if self.current_index < len(self.full_text):
            self.current_text += self.full_text[self.current_index]
            self.current_index += 1
            self.text_updated.emit(self.current_text)
        else:
            self.stop()
            self.animation_finished.emit()


class RippleEffect(QWidget):
    """漣漪效果 - 點擊時的擴散動畫"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.ripples = []
        self.animation_timer = QTimer(self)  # 設置父對象確保在正確線程中
        self.animation_timer.timeout.connect(self.update_ripples)
        # 延遲啟動計時器，確保在主線程中啟動，但首先檢查是否在主線程中
        def start_timer_safely():
            try:
                if self.animation_timer and not self.animation_timer.isActive():
                    self.animation_timer.start(16)
            except Exception as e:
                logger.warning(f"Failed to start ripple timer: {e}")
        
        QTimer.singleShot(0, start_timer_safely)
    
    def add_ripple(self, center: QPoint, max_radius: int = 100):
        """添加漣漪"""
        ripple = {
            'center': center,
            'radius': 0,
            'max_radius': max_radius,
            'opacity': 1.0,
            'growing': True
        }
        self.ripples.append(ripple)
        self.update()
    
    def update_ripples(self):
        """更新漣漪狀態"""
        if not self.ripples:
            return
        
        updated_ripples = []
        for ripple in self.ripples:
            if ripple['growing']:
                ripple['radius'] += 3
                if ripple['radius'] >= ripple['max_radius']:
                    ripple['growing'] = False
            else:
                ripple['opacity'] -= 0.05
            
            if ripple['opacity'] > 0:
                updated_ripples.append(ripple)
        
        self.ripples = updated_ripples
        self.update()
    
    def paintEvent(self, event):
        """繪製漣漪"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for ripple in self.ripples:
            color = QColor(70, 130, 180, int(255 * ripple['opacity'] * 0.3))
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(QColor(70, 130, 180, int(255 * ripple['opacity'] * 0.1))))
            
            center = ripple['center']
            radius = ripple['radius']
            painter.drawEllipse(center.x() - radius, center.y() - radius, 
                              radius * 2, radius * 2)


class ParticleSystem(QWidget):
    """粒子系統 - 創建粒子效果"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.particles = []
        self.animation_timer = QTimer(self)  # 設置父對象確保在正確線程中
        self.animation_timer.timeout.connect(self.update_particles)
        # 延遲啟動計時器，確保在主線程中啟動，但首先檢查是否在主線程中
        def start_timer_safely():
            try:
                if self.animation_timer and not self.animation_timer.isActive():
                    self.animation_timer.start(16)
            except Exception as e:
                logger.warning(f"Failed to start particle timer: {e}")
        
        QTimer.singleShot(0, start_timer_safely)
    
    def emit_particles(self, position: QPoint, count: int = 10, 
                      color: QColor = QColor(70, 130, 180)):
        """發射粒子"""
        for _ in range(count):
            particle = {
                'pos': QPoint(position),
                'velocity': QPoint(
                    (self._random() - 0.5) * 4,
                    (self._random() - 0.5) * 4
                ),
                'life': 1.0,
                'decay': 0.02,
                'color': color,
                'size': self._random() * 4 + 2
            }
            self.particles.append(particle)
    
    def _random(self) -> float:
        """簡單的隨機數生成"""
        import random
        return random.random()
    
    def update_particles(self):
        """更新粒子狀態"""
        if not self.particles:
            return
        
        updated_particles = []
        for particle in self.particles:
            # 更新位置
            particle['pos'] += particle['velocity']
            
            # 更新生命值
            particle['life'] -= particle['decay']
            
            # 添加重力效果
            particle['velocity'].setY(particle['velocity'].y() + 0.1)
            
            if particle['life'] > 0:
                updated_particles.append(particle)
        
        self.particles = updated_particles
        self.update()
    
    def paintEvent(self, event):
        """繪製粒子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = QColor(particle['color'])
            color.setAlpha(alpha)
            
            painter.setPen(QPen(color))
            painter.setBrush(QBrush(color))
            
            size = particle['size'] * particle['life']
            pos = particle['pos']
            painter.drawEllipse(pos.x() - size/2, pos.y() - size/2, size, size)


class AnimationEffectFactory:
    """動畫效果工廠 - 創建各種動畫效果"""
    
    @staticmethod
    def create_fade_in(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
        """創建淡入動畫"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        return animation
    
    @staticmethod
    def create_slide_in(widget: QWidget, direction: str = 'left', 
                       duration: int = 400) -> QPropertyAnimation:
        """創建滑入動畫"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        original_pos = widget.pos()
        
        if direction == 'left':
            start_pos = QPoint(original_pos.x() - widget.width(), original_pos.y())
        elif direction == 'right':
            start_pos = QPoint(original_pos.x() + widget.width(), original_pos.y())
        elif direction == 'up':
            start_pos = QPoint(original_pos.x(), original_pos.y() - widget.height())
        else:  # down
            start_pos = QPoint(original_pos.x(), original_pos.y() + widget.height())
        
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        
        return animation
    
    @staticmethod
    def create_bounce_in(widget: QWidget, duration: int = 600) -> QSequentialAnimationGroup:
        """創建彈跳入場動畫"""
        group = QSequentialAnimationGroup()
        
        # 縮放動畫序列
        scales = [0.0, 1.2, 0.9, 1.05, 0.95, 1.0]
        scale_duration = duration // len(scales)
        
        original_size = widget.size()
        
        for i, scale in enumerate(scales):
            animation = QPropertyAnimation(widget, b"size")
            animation.setDuration(scale_duration)
            
            if i == 0:
                animation.setStartValue(QSize(0, 0))
            else:
                prev_scale = scales[i-1]
                animation.setStartValue(QSize(
                    int(original_size.width() * prev_scale),
                    int(original_size.height() * prev_scale)
                ))
            
            animation.setEndValue(QSize(
                int(original_size.width() * scale),
                int(original_size.height() * scale)
            ))
            
            if i < len(scales) - 1:
                animation.setEasingCurve(QEasingCurve.OutBounce)
            else:
                animation.setEasingCurve(QEasingCurve.OutCubic)
            
            group.addAnimation(animation)
        
        return group
    
    @staticmethod
    def create_attention_seeker(widget: QWidget, effect_type: str = 'pulse') -> QAbstractAnimation:
        """創建吸引注意力的動畫"""
        if effect_type == 'pulse':
            return PulseAnimation(widget)
        elif effect_type == 'shake':
            return ShakeAnimation(widget)
        else:
            # 默認脈衝動畫
            return PulseAnimation(widget)


# 便利函數
def animate_widget(widget: QWidget, effect: str, **kwargs):
    """為組件添加動畫效果"""
    if not animation_manager.animations_enabled:
        return
    
    factory = AnimationEffectFactory()
    animation = None
    
    if effect == 'fade_in':
        animation = factory.create_fade_in(widget, kwargs.get('duration', 300))
    elif effect == 'slide_in':
        animation = factory.create_slide_in(
            widget, 
            kwargs.get('direction', 'left'), 
            kwargs.get('duration', 400)
        )
    elif effect == 'bounce_in':
        animation = factory.create_bounce_in(widget, kwargs.get('duration', 600))
    elif effect == 'pulse':
        animation = factory.create_attention_seeker(widget, 'pulse')
    elif effect == 'shake':
        animation = factory.create_attention_seeker(widget, 'shake')
    
    if animation:
        animation_name = f"{widget.__class__.__name__}_{id(widget)}_{effect}"
        animation_manager.register_animation(animation_name, animation)
        animation_manager.start_animation(animation_name)

def enable_ripple_effect(widget: QWidget):
    """為組件啟用漣漪效果"""
    ripple_widget = RippleEffect(widget)
    ripple_widget.resize(widget.size())
    
    original_mouse_press = widget.mousePressEvent
    
    def enhanced_mouse_press(event):
        ripple_widget.add_ripple(event.pos())
        original_mouse_press(event)
    
    widget.mousePressEvent = enhanced_mouse_press
    widget.ripple_effect = ripple_widget  # 保持引用