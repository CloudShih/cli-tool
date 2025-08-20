# 動畫效果實現指南

**日期**: 2025-08-18  
**類別**: UI 動畫系統  
**目的**: 為現代化 PyQt5 應用程式提供豐富的動畫效果系統  

## 概述

本指南詳述了如何在 PyQt5 應用程式中實現現代化的動畫效果系統，包括頁面切換動畫、組件互動效果、視覺反饋和用戶體驗增強。基於現有的 CLI Tool 專案架構，提供完整的動畫解決方案。

---

## 動畫系統架構

### 核心組件架構圖

```
AnimationManager (全域管理器)
├── AnimationEffectFactory (效果工廠)
├── Page Transition System (頁面切換)
├── Component Animations (組件動畫)
│   ├── AnimatedButton (動畫按鈕)
│   ├── PulseAnimation (脈衝效果)
│   ├── ShakeAnimation (搖擺效果)
│   └── TypewriterAnimation (打字機效果)
├── Visual Effects (視覺效果)
│   ├── RippleEffect (漣漪效果)
│   ├── ParticleSystem (粒子系統)
│   └── Progressive Effects (漸進效果)
└── Theme Integration (主題整合)
    ├── Dark Theme Animations (深色主題動畫)
    └── Responsive Animations (響應式動畫)
```

---

## 1. 全域動畫管理系統

### AnimationManager 類別

```python
"""
全域動畫管理器 - 統一管理所有動畫效果
"""

class AnimationManager:
    def __init__(self):
        self.active_animations = {}
        self.animation_queue = []
        self.global_speed_factor = 1.0
        self.animations_enabled = True
        
        # 效能優化設定
        self.max_concurrent_animations = 10
        self.animation_cache = {}
    
    def set_animations_enabled(self, enabled: bool):
        """啟用或禁用動畫"""
        self.animations_enabled = enabled
        if not enabled:
            self.stop_all_animations()
    
    def set_speed_factor(self, factor: float):
        """設置全局動畫速度倍數 (0.1x - 3.0x)"""
        self.global_speed_factor = max(0.1, min(3.0, factor))
    
    def register_animation(self, name: str, animation: QAbstractAnimation):
        """註冊並管理動畫生命週期"""
        if not self.animations_enabled:
            return
        
        # 停止同名動畫避免衝突
        if name in self.active_animations:
            self.active_animations[name].stop()
        
        # 應用全域速度設定
        self._apply_speed_factor(animation)
        
        # 註冊動畫和回調
        self.active_animations[name] = animation
        animation.finished.connect(lambda: self._on_animation_finished(name))
    
    def _apply_speed_factor(self, animation: QAbstractAnimation):
        """遞歸應用速度倍數到動畫群組"""
        try:
            if isinstance(animation, (QSequentialAnimationGroup, QParallelAnimationGroup)):
                for i in range(animation.animationCount()):
                    child_animation = animation.animationAt(i)
                    if child_animation:
                        self._apply_speed_factor(child_animation)
            else:
                if hasattr(animation, 'setDuration') and hasattr(animation, 'duration'):
                    original_duration = animation.duration()
                    new_duration = int(original_duration / self.global_speed_factor)
                    animation.setDuration(max(50, new_duration))  # 最小持續時間 50ms
        except Exception as e:
            logger.warning(f"Failed to apply speed factor: {e}")
    
    def start_animation(self, name: str):
        """啟動指定動畫"""
        if name in self.active_animations and self.animations_enabled:
            # 效能檢查：限制併發動畫數量
            if len([a for a in self.active_animations.values() if a.state() == QAbstractAnimation.Running]) < self.max_concurrent_animations:
                self.active_animations[name].start()
    
    def create_sequential_chain(self, animations: List[QAbstractAnimation]) -> QSequentialAnimationGroup:
        """創建動畫鏈"""
        group = QSequentialAnimationGroup()
        for animation in animations:
            self._apply_speed_factor(animation)
            group.addAnimation(animation)
        return group
    
    def create_parallel_group(self, animations: List[QAbstractAnimation]) -> QParallelAnimationGroup:
        """創建並行動畫群組"""
        group = QParallelAnimationGroup()
        for animation in animations:
            self._apply_speed_factor(animation)
            group.addAnimation(animation)
        return group

# 全域實例
animation_manager = AnimationManager()
```

---

## 2. 頁面切換動畫系統

### 滑動切換動畫

```python
class PageTransitionManager:
    """頁面切換動畫管理器"""
    
    def __init__(self, stacked_widget: QStackedWidget):
        self.stacked_widget = stacked_widget
        self.current_animation = None
        
    def slide_to_page(self, target_index: int, direction: str = 'left'):
        """滑動到指定頁面"""
        if self.current_animation and self.current_animation.state() == QAbstractAnimation.Running:
            return  # 防止動畫重疊
        
        current_index = self.stacked_widget.currentIndex()
        if current_index == target_index:
            return
        
        current_widget = self.stacked_widget.widget(current_index)
        target_widget = self.stacked_widget.widget(target_index)
        
        # 創建滑動動畫
        self.current_animation = self._create_slide_animation(
            current_widget, target_widget, direction
        )
        
        # 動畫完成後切換頁面
        self.current_animation.finished.connect(
            lambda: self._on_transition_finished(target_index)
        )
        
        animation_manager.register_animation("page_transition", self.current_animation)
        animation_manager.start_animation("page_transition")
    
    def _create_slide_animation(self, current_widget: QWidget, target_widget: QWidget, 
                               direction: str) -> QParallelAnimationGroup:
        """創建滑動動畫效果"""
        parent_rect = self.stacked_widget.geometry()
        
        # 計算滑動方向
        if direction == 'left':
            current_end_x = -parent_rect.width()
            target_start_x = parent_rect.width()
        elif direction == 'right':
            current_end_x = parent_rect.width()
            target_start_x = -parent_rect.width()
        elif direction == 'up':
            current_end_x = 0
            current_end_y = -parent_rect.height()
            target_start_x = 0
            target_start_y = parent_rect.height()
        else:  # down
            current_end_x = 0
            current_end_y = parent_rect.height()
            target_start_x = 0
            target_start_y = -parent_rect.height()
        
        # 設置目標頁面初始位置
        if direction in ['left', 'right']:
            target_widget.move(target_start_x, 0)
            current_end_pos = QPoint(current_end_x, 0)
            target_end_pos = QPoint(0, 0)
        else:
            target_widget.move(target_start_x, target_start_y)
            current_end_pos = QPoint(current_end_x, current_end_y)
            target_end_pos = QPoint(target_start_x, 0)
        
        target_widget.show()
        
        # 創建並行動畫
        group = QParallelAnimationGroup()
        
        # 當前頁面滑出動畫
        current_animation = QPropertyAnimation(current_widget, b"pos")
        current_animation.setDuration(400)
        current_animation.setStartValue(current_widget.pos())
        current_animation.setEndValue(current_end_pos)
        current_animation.setEasingCurve(QEasingCurve.OutCubic)
        group.addAnimation(current_animation)
        
        # 目標頁面滑入動畫
        target_animation = QPropertyAnimation(target_widget, b"pos")
        target_animation.setDuration(400)
        target_animation.setStartValue(QPoint(target_start_x, target_start_y if direction in ['up', 'down'] else 0))
        target_animation.setEndValue(target_end_pos)
        target_animation.setEasingCurve(QEasingCurve.OutCubic)
        group.addAnimation(target_animation)
        
        return group
    
    def fade_to_page(self, target_index: int):
        """淡入淡出切換頁面"""
        current_widget = self.stacked_widget.currentWidget()
        target_widget = self.stacked_widget.widget(target_index)
        
        # 創建淡入淡出動畫
        fade_out_effect = QGraphicsOpacityEffect()
        fade_in_effect = QGraphicsOpacityEffect()
        
        current_widget.setGraphicsEffect(fade_out_effect)
        target_widget.setGraphicsEffect(fade_in_effect)
        
        # 淡出當前頁面
        fade_out_animation = QPropertyAnimation(fade_out_effect, b"opacity")
        fade_out_animation.setDuration(300)
        fade_out_animation.setStartValue(1.0)
        fade_out_animation.setEndValue(0.0)
        
        # 淡入目標頁面
        fade_in_animation = QPropertyAnimation(fade_in_effect, b"opacity")
        fade_in_animation.setDuration(300)
        fade_in_animation.setStartValue(0.0)
        fade_in_animation.setEndValue(1.0)
        
        # 創建序列動畫
        sequence = QSequentialAnimationGroup()
        sequence.addAnimation(fade_out_animation)
        sequence.addAnimation(fade_in_animation)
        
        sequence.finished.connect(lambda: self._on_fade_finished(target_index, current_widget, target_widget))
        
        target_widget.show()
        animation_manager.register_animation("page_fade", sequence)
        animation_manager.start_animation("page_fade")
    
    def _on_transition_finished(self, target_index: int):
        """切換完成處理"""
        self.stacked_widget.setCurrentIndex(target_index)
        self.current_animation = None
    
    def _on_fade_finished(self, target_index: int, current_widget: QWidget, target_widget: QWidget):
        """淡入淡出完成處理"""
        self.stacked_widget.setCurrentIndex(target_index)
        current_widget.setGraphicsEffect(None)
        target_widget.setGraphicsEffect(None)
```

### 側邊欄導航動畫

```python
class NavigationSidebarAnimated(QFrame):
    """帶動畫效果的導航側邊欄"""
    
    page_change_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animations()
        self.active_button = None
        
    def setup_animations(self):
        """設置動畫效果"""
        self.expand_animation = QPropertyAnimation(self, b"maximumWidth")
        self.expand_animation.setDuration(300)
        self.expand_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.button_animations = {}
    
    def add_tool_button(self, icon_text: str, tool_name: str, tool_index: int, 
                       category: str = "通用工具"):
        """添加工具按鈕並設置動畫"""
        button = AnimatedToolButton(icon_text, tool_name, tool_index)
        button.clicked.connect(lambda: self._on_button_clicked(button, tool_index))
        
        # 設置按鈕動畫
        self._setup_button_animation(button)
        
        # 添加到對應分類
        category_layout = self._get_or_create_category_layout(category)
        category_layout.addWidget(button)
        
        return button
    
    def _setup_button_animation(self, button: 'AnimatedToolButton'):
        """為按鈕設置動畫效果"""
        # 懸停縮放動畫
        scale_animation = QPropertyAnimation(button, b"geometry")
        scale_animation.setDuration(200)
        scale_animation.setEasingCurve(QEasingCurve.OutBack)
        
        # 點擊漣漪效果
        enable_ripple_effect(button)
        
        # 選中狀態動畫
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(0)
        glow_effect.setColor(QColor(70, 130, 180, 0))
        glow_effect.setOffset(0, 0)
        button.setGraphicsEffect(glow_effect)
        
        self.button_animations[button] = {
            'scale': scale_animation,
            'glow': glow_effect
        }
    
    def _on_button_clicked(self, button: 'AnimatedToolButton', tool_index: int):
        """按鈕點擊處理 - 包含動畫效果"""
        # 如果是同一個按鈕，不處理
        if self.active_button == button:
            return
        
        # 取消之前按鈕的選中狀態
        if self.active_button:
            self._deactivate_button(self.active_button)
        
        # 激活當前按鈕
        self._activate_button(button)
        self.active_button = button
        
        # 發射頁面切換信號
        self.page_change_requested.emit(tool_index)
    
    def _activate_button(self, button: 'AnimatedToolButton'):
        """激活按鈕動畫"""
        glow_effect = self.button_animations[button]['glow']
        
        # 創建發光動畫
        glow_animation = QPropertyAnimation(glow_effect, b"blurRadius")
        glow_animation.setDuration(300)
        glow_animation.setStartValue(0)
        glow_animation.setEndValue(15)
        glow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 同時改變顏色透明度
        color_animation = QTimer()
        color_animation.timeout.connect(
            lambda: glow_effect.setColor(QColor(70, 130, 180, 150))
        )
        color_animation.setSingleShot(True)
        color_animation.start(150)
        
        button.setProperty("selected", True)
        button.style().polish(button)
        
        animation_manager.register_animation(f"button_activate_{id(button)}", glow_animation)
        animation_manager.start_animation(f"button_activate_{id(button)}")
    
    def _deactivate_button(self, button: 'AnimatedToolButton'):
        """取消按鈕激活動畫"""
        glow_effect = self.button_animations[button]['glow']
        
        # 創建褪色動畫
        fade_animation = QPropertyAnimation(glow_effect, b"blurRadius")
        fade_animation.setDuration(200)
        fade_animation.setStartValue(15)
        fade_animation.setEndValue(0)
        fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        button.setProperty("selected", False)
        button.style().polish(button)
        
        animation_manager.register_animation(f"button_deactivate_{id(button)}", fade_animation)
        animation_manager.start_animation(f"button_deactivate_{id(button)}")
```

---

## 3. 高級組件動畫效果

### 動畫按鈕增強版

```python
class AnimatedToolButton(QPushButton):
    """高級動畫工具按鈕"""
    
    def __init__(self, icon_text: str, tool_name: str, tool_index: int):
        super().__init__()
        self.icon_text = icon_text
        self.tool_name = tool_name
        self.tool_index = tool_index
        self.is_selected = False
        
        self.setup_ui()
        self.setup_animations()
        self.setup_effects()
    
    def setup_ui(self):
        """設置基本 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)
        
        # 圖標標籤
        self.icon_label = QLabel(self.icon_text)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setProperty("tool-icon", True)
        layout.addWidget(self.icon_label)
        
        # 工具名稱標籤
        self.name_label = QLabel(self.tool_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setProperty("tool-name", True)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        self.setProperty("tool-button", True)
        
    def setup_animations(self):
        """設置動畫效果"""
        # 懸停動畫
        self.hover_animation = QParallelAnimationGroup()
        
        # 縮放動畫
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(250)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)
        
        # 圖標放大動畫
        self.icon_animation = QPropertyAnimation(self.icon_label, b"font")
        self.icon_animation.setDuration(250)
        self.icon_animation.setEasingCurve(QEasingCurve.OutBack)
        
        self.hover_animation.addAnimation(self.scale_animation)
        self.hover_animation.addAnimation(self.icon_animation)
        
        # 點擊動畫
        self.click_animation = self._create_click_animation()
        
        # 脈衝動畫（用於通知）
        self.notification_animation = self._create_notification_animation()
    
    def _create_click_animation(self) -> QSequentialAnimationGroup:
        """創建點擊動畫"""
        group = QSequentialAnimationGroup()
        
        # 按下效果
        press_animation = QParallelAnimationGroup()
        
        # 輕微縮小
        press_scale = QPropertyAnimation(self, b"geometry")
        press_scale.setDuration(100)
        press_scale.setEasingCurve(QEasingCurve.OutCubic)
        press_animation.addAnimation(press_scale)
        
        # 顏色變化（透過樣式）
        color_timer = QTimer()
        color_timer.timeout.connect(lambda: self.setProperty("pressed", True))
        color_timer.setSingleShot(True)
        
        # 恢復效果
        release_animation = QParallelAnimationGroup()
        
        release_scale = QPropertyAnimation(self, b"geometry")
        release_scale.setDuration(150)
        release_scale.setEasingCurve(QEasingCurve.OutBounce)
        release_animation.addAnimation(release_scale)
        
        group.addAnimation(press_animation)
        group.addAnimation(release_animation)
        
        return group
    
    def _create_notification_animation(self) -> QSequentialAnimationGroup:
        """創建通知脈衝動畫"""
        group = QSequentialAnimationGroup()
        
        for _ in range(3):  # 脈衝 3 次
            # 放大
            expand_animation = QPropertyAnimation(self.icon_label, b"font")
            expand_animation.setDuration(200)
            expand_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # 縮小
            shrink_animation = QPropertyAnimation(self.icon_label, b"font")
            shrink_animation.setDuration(200)
            shrink_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            group.addAnimation(expand_animation)
            group.addAnimation(shrink_animation)
        
        return group
    
    def setup_effects(self):
        """設置視覺效果"""
        # 陰影效果
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor(0, 0, 0, 40))
        self.shadow_effect.setOffset(2, 2)
        self.setGraphicsEffect(self.shadow_effect)
    
    def enterEvent(self, event):
        """滑鼠進入事件 - 懸停動畫"""
        super().enterEvent(event)
        if not animation_manager.animations_enabled:
            return
        
        original_rect = self.geometry()
        hover_rect = QRect(original_rect)
        hover_rect.adjust(-3, -3, 3, 3)
        
        # 設置動畫目標
        self.scale_animation.setStartValue(original_rect)
        self.scale_animation.setEndValue(hover_rect)
        
        # 字體放大效果
        original_font = self.icon_label.font()
        hover_font = QFont(original_font)
        hover_font.setPointSize(original_font.pointSize() + 2)
        
        self.icon_animation.setStartValue(original_font)
        self.icon_animation.setEndValue(hover_font)
        
        # 增強陰影
        self.shadow_effect.setBlurRadius(12)
        self.shadow_effect.setOffset(3, 3)
        
        animation_manager.register_animation(f"hover_{id(self)}", self.hover_animation)
        animation_manager.start_animation(f"hover_{id(self)}")
    
    def leaveEvent(self, event):
        """滑鼠離開事件 - 恢復動畫"""
        super().leaveEvent(event)
        if not animation_manager.animations_enabled:
            return
        
        # 恢復原始狀態
        current_rect = self.geometry()
        original_rect = QRect(current_rect)
        original_rect.adjust(3, 3, -3, -3)
        
        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(original_rect)
        
        # 字體恢復
        current_font = self.icon_label.font()
        original_font = QFont(current_font)
        original_font.setPointSize(max(8, current_font.pointSize() - 2))
        
        self.icon_animation.setStartValue(current_font)
        self.icon_animation.setEndValue(original_font)
        
        # 恢復陰影
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setOffset(2, 2)
        
        animation_manager.register_animation(f"leave_{id(self)}", self.hover_animation)
        animation_manager.start_animation(f"leave_{id(self)}")
    
    def mousePressEvent(self, event):
        """滑鼠按下事件 - 點擊動畫"""
        super().mousePressEvent(event)
        if not animation_manager.animations_enabled:
            return
        
        current_rect = self.geometry()
        press_rect = QRect(current_rect)
        press_rect.adjust(2, 2, -2, -2)
        
        press_animation = self.click_animation.animationAt(0)
        if hasattr(press_animation, 'animationAt'):
            scale_anim = press_animation.animationAt(0)
            scale_anim.setStartValue(current_rect)
            scale_anim.setEndValue(press_rect)
        
        release_animation = self.click_animation.animationAt(1)
        if hasattr(release_animation, 'animationAt'):
            scale_anim = release_animation.animationAt(0)
            scale_anim.setStartValue(press_rect)
            scale_anim.setEndValue(current_rect)
        
        animation_manager.register_animation(f"click_{id(self)}", self.click_animation)
        animation_manager.start_animation(f"click_{id(self)}")
    
    def show_notification(self):
        """顯示通知動畫"""
        if not animation_manager.animations_enabled:
            return
        
        animation_manager.register_animation(f"notification_{id(self)}", self.notification_animation)
        animation_manager.start_animation(f"notification_{id(self)}")
```

### 進度指示器動畫

```python
class AnimatedProgressIndicator(QWidget):
    """動畫進度指示器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        
        self.rotation_angle = 0
        self.progress_value = 0
        self.setup_animations()
    
    def setup_animations(self):
        """設置旋轉動畫"""
        self.rotation_animation = QPropertyAnimation(self, b"rotation_angle")
        self.rotation_animation.setDuration(1000)
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(360)
        self.rotation_animation.setLoopCount(-1)  # 無限循環
        self.rotation_animation.finished.connect(self.rotation_animation.start)
    
    def start_loading(self):
        """開始載入動畫"""
        animation_manager.register_animation(f"loading_{id(self)}", self.rotation_animation)
        animation_manager.start_animation(f"loading_{id(self)}")
    
    def stop_loading(self):
        """停止載入動畫"""
        animation_manager.stop_animation(f"loading_{id(self)}")
    
    def set_progress(self, value: int):
        """設置進度值 (0-100)"""
        self.progress_value = max(0, min(100, value))
        self.update()
    
    @pyqtProperty(int)
    def rotation_angle(self):
        return self._rotation_angle
    
    @rotation_angle.setter
    def rotation_angle(self, angle):
        self._rotation_angle = angle
        self.update()
    
    def paintEvent(self, event):
        """繪製動畫進度指示器"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 設置繪製區域
        rect = self.rect().adjusted(5, 5, -5, -5)
        center = rect.center()
        
        # 背景圓環
        painter.setPen(QPen(QColor(60, 60, 60, 100), 3))
        painter.drawEllipse(rect)
        
        # 進度圓環
        if self.progress_value > 0:
            painter.setPen(QPen(QColor(70, 130, 180), 3))
            span_angle = int(360 * 16 * self.progress_value / 100)
            painter.drawArc(rect, 90 * 16, -span_angle)
        
        # 旋轉載入指示器
        if self.rotation_animation.state() == QAbstractAnimation.Running:
            painter.translate(center)
            painter.rotate(self.rotation_angle)
            
            # 繪製載入點
            for i in range(8):
                alpha = 255 - (i * 30)
                painter.setPen(QPen(QColor(70, 130, 180, max(50, alpha)), 2))
                painter.drawLine(0, -15, 0, -10)
                painter.rotate(45)
```

---

## 4. 主題整合和響應式動畫

### 主題切換動畫

```python
class ThemeTransitionManager:
    """主題切換動畫管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
    def animate_theme_change(self, from_theme: str, to_theme: str):
        """主題切換動畫"""
        # 創建遮罩層
        overlay = QWidget(self.main_window)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        overlay.resize(self.main_window.size())
        overlay.show()
        
        # 淡入遮罩
        overlay_effect = QGraphicsOpacityEffect()
        overlay.setGraphicsEffect(overlay_effect)
        
        fade_in = QPropertyAnimation(overlay_effect, b"opacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(0.8)
        
        # 切換主題
        def switch_theme():
            # 實際的主題切換邏輯
            self.main_window.set_theme(to_theme)
            
            # 淡出遮罩
            fade_out = QPropertyAnimation(overlay_effect, b"opacity")
            fade_out.setDuration(300)
            fade_out.setStartValue(0.8)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(overlay.deleteLater)
            
            animation_manager.register_animation("theme_fade_out", fade_out)
            animation_manager.start_animation("theme_fade_out")
        
        fade_in.finished.connect(switch_theme)
        
        animation_manager.register_animation("theme_fade_in", fade_in)
        animation_manager.start_animation("theme_fade_in")
    
    def animate_component_theme_change(self, components: List[QWidget]):
        """組件主題切換動畫"""
        animations = []
        
        for component in components:
            # 創建閃爍效果
            flash_effect = QGraphicsOpacityEffect()
            component.setGraphicsEffect(flash_effect)
            
            flash_animation = QSequentialAnimationGroup()
            
            # 淡出
            fade_out = QPropertyAnimation(flash_effect, b"opacity")
            fade_out.setDuration(100)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.3)
            
            # 淡入
            fade_in = QPropertyAnimation(flash_effect, b"opacity")
            fade_in.setDuration(100)
            fade_in.setStartValue(0.3)
            fade_in.setEndValue(1.0)
            
            flash_animation.addAnimation(fade_out)
            flash_animation.addAnimation(fade_in)
            
            # 完成後移除效果
            flash_animation.finished.connect(
                lambda comp=component: comp.setGraphicsEffect(None)
            )
            
            animations.append(flash_animation)
        
        # 並行執行所有動畫
        group = animation_manager.create_parallel_group(animations)
        animation_manager.register_animation("components_theme_change", group)
        animation_manager.start_animation("components_theme_change")
```

### 響應式佈局動畫

```python
class ResponsiveAnimationManager:
    """響應式佈局動畫管理器"""
    
    def __init__(self):
        self.breakpoints = {
            'mobile': 600,
            'tablet': 900,
            'desktop': 1200
        }
        self.current_breakpoint = 'desktop'
    
    def animate_layout_change(self, widget: QWidget, from_size: QSize, to_size: QSize):
        """佈局變化動畫"""
        resize_animation = QPropertyAnimation(widget, b"size")
        resize_animation.setDuration(400)
        resize_animation.setStartValue(from_size)
        resize_animation.setEndValue(to_size)
        resize_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        animation_manager.register_animation(f"resize_{id(widget)}", resize_animation)
        animation_manager.start_animation(f"resize_{id(widget)}")
    
    def animate_sidebar_collapse(self, sidebar: QWidget, collapsed: bool):
        """側邊欄收縮/展開動畫"""
        target_width = 60 if collapsed else 240
        
        width_animation = QPropertyAnimation(sidebar, b"maximumWidth")
        width_animation.setDuration(300)
        width_animation.setStartValue(sidebar.width())
        width_animation.setEndValue(target_width)
        width_animation.setEasingCurve(QEasingCurve.OutBack)
        
        # 同時淡入淡出文字標籤
        labels = sidebar.findChildren(QLabel)
        label_animations = []
        
        for label in labels:
            if hasattr(label, 'property') and label.property("tool-name"):
                opacity_effect = QGraphicsOpacityEffect()
                label.setGraphicsEffect(opacity_effect)
                
                opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
                opacity_animation.setDuration(200)
                
                if collapsed:
                    opacity_animation.setStartValue(1.0)
                    opacity_animation.setEndValue(0.0)
                else:
                    opacity_animation.setStartValue(0.0)
                    opacity_animation.setEndValue(1.0)
                
                label_animations.append(opacity_animation)
        
        # 組合動畫
        group = QParallelAnimationGroup()
        group.addAnimation(width_animation)
        
        for label_anim in label_animations:
            group.addAnimation(label_anim)
        
        animation_manager.register_animation("sidebar_toggle", group)
        animation_manager.start_animation("sidebar_toggle")
```

---

## 5. 實用動畫函數庫

### 便利函數集合

```python
def animate_widget_entrance(widget: QWidget, effect_type: str = "slide_up"):
    """組件入場動畫"""
    effects = {
        "slide_up": lambda w: AnimationEffectFactory.create_slide_in(w, "up"),
        "slide_down": lambda w: AnimationEffectFactory.create_slide_in(w, "down"),
        "slide_left": lambda w: AnimationEffectFactory.create_slide_in(w, "left"),
        "slide_right": lambda w: AnimationEffectFactory.create_slide_in(w, "right"),
        "fade_in": lambda w: AnimationEffectFactory.create_fade_in(w),
        "bounce_in": lambda w: AnimationEffectFactory.create_bounce_in(w),
        "zoom_in": lambda w: create_zoom_in_animation(w)
    }
    
    if effect_type in effects:
        animation = effects[effect_type](widget)
        animation_name = f"entrance_{id(widget)}"
        animation_manager.register_animation(animation_name, animation)
        animation_manager.start_animation(animation_name)

def animate_notification(widget: QWidget, message: str, notification_type: str = "info"):
    """通知動畫"""
    colors = {
        "info": QColor(70, 130, 180),
        "success": QColor(40, 167, 69),
        "warning": QColor(255, 193, 7),
        "error": QColor(220, 53, 69)
    }
    
    # 創建通知氣泡
    notification = QLabel(message)
    notification.setParent(widget)
    notification.setStyleSheet(f"""
        QLabel {{
            background-color: {colors.get(notification_type, colors["info"]).name()};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
        }}
    """)
    notification.adjustSize()
    
    # 位置在父組件右上角
    notification.move(widget.width() - notification.width() - 20, 20)
    notification.show()
    
    # 入場動畫
    entrance = AnimationEffectFactory.create_slide_in(notification, "right", 300)
    
    # 停留動畫（輕微浮動）
    float_animation = QSequentialAnimationGroup()
    for _ in range(20):  # 浮動 2 秒
        up = QPropertyAnimation(notification, b"pos")
        up.setDuration(100)
        up.setStartValue(notification.pos())
        up.setEndValue(QPoint(notification.x(), notification.y() - 2))
        
        down = QPropertyAnimation(notification, b"pos")
        down.setDuration(100)
        down.setStartValue(QPoint(notification.x(), notification.y() - 2))
        down.setEndValue(notification.pos())
        
        float_animation.addAnimation(up)
        float_animation.addAnimation(down)
    
    # 退場動畫
    exit_animation = AnimationEffectFactory.create_slide_in(notification, "right", 300)
    exit_animation.finished.connect(notification.deleteLater)
    
    # 組合完整動畫序列
    full_sequence = QSequentialAnimationGroup()
    full_sequence.addAnimation(entrance)
    full_sequence.addAnimation(float_animation)
    full_sequence.addAnimation(exit_animation)
    
    animation_manager.register_animation(f"notification_{id(notification)}", full_sequence)
    animation_manager.start_animation(f"notification_{id(notification)}")

def create_loading_overlay(parent: QWidget, message: str = "載入中...") -> QWidget:
    """創建載入遮罩"""
    overlay = QWidget(parent)
    overlay.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 0.7);
        }
        QLabel {
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
    """)
    overlay.resize(parent.size())
    
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)
    
    # 載入指示器
    loading_indicator = AnimatedProgressIndicator()
    layout.addWidget(loading_indicator, 0, Qt.AlignCenter)
    
    # 載入訊息
    loading_label = QLabel(message)
    loading_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(loading_label)
    
    overlay.setLayout(layout)
    
    # 淡入動畫
    fade_in = AnimationEffectFactory.create_fade_in(overlay, 200)
    animation_manager.register_animation(f"overlay_fade_in_{id(overlay)}", fade_in)
    animation_manager.start_animation(f"overlay_fade_in_{id(overlay)}")
    
    # 開始載入動畫
    loading_indicator.start_loading()
    
    overlay.show()
    return overlay

def dismiss_loading_overlay(overlay: QWidget):
    """關閉載入遮罩"""
    # 停止載入動畫
    loading_indicator = overlay.findChild(AnimatedProgressIndicator)
    if loading_indicator:
        loading_indicator.stop_loading()
    
    # 淡出動畫
    overlay_effect = QGraphicsOpacityEffect()
    overlay.setGraphicsEffect(overlay_effect)
    
    fade_out = QPropertyAnimation(overlay_effect, b"opacity")
    fade_out.setDuration(200)
    fade_out.setStartValue(1.0)
    fade_out.setEndValue(0.0)
    fade_out.finished.connect(overlay.deleteLater)
    
    animation_manager.register_animation(f"overlay_fade_out_{id(overlay)}", fade_out)
    animation_manager.start_animation(f"overlay_fade_out_{id(overlay)}")
```

---

## 6. QSS 樣式整合

### 動畫相關樣式

```css
/* 動畫按鈕樣式 */
QPushButton[tool-button="true"] {
    background-color: #2b2b2b;
    border: 2px solid transparent;
    border-radius: 12px;
    padding: 12px;
    margin: 2px;
    transition: all 0.3s ease;
}

QPushButton[tool-button="true"]:hover {
    background-color: #3b3b3b;
    border-color: #4a90e2;
    transform: translateY(-2px);
}

QPushButton[tool-button="true"][selected="true"] {
    background-color: #4a90e2;
    border-color: #6bb6ff;
    box-shadow: 0 0 15px rgba(74, 144, 226, 0.5);
}

QPushButton[tool-button="true"][pressed="true"] {
    background-color: #1a1a1a;
    transform: scale(0.95);
}

/* 工具圖標樣式 */
QLabel[tool-icon="true"] {
    font-size: 24px;
    color: #ffffff;
    transition: font-size 0.25s ease;
}

QPushButton[tool-button="true"]:hover QLabel[tool-icon="true"] {
    font-size: 28px;
}

/* 工具名稱樣式 */
QLabel[tool-name="true"] {
    font-size: 11px;
    color: #cccccc;
    font-weight: 500;
    transition: color 0.25s ease;
}

QPushButton[tool-button="true"][selected="true"] QLabel[tool-name="true"] {
    color: #ffffff;
    font-weight: 600;
}

/* 動畫過渡效果 */
QWidget {
    transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
}

/* 載入指示器樣式 */
QWidget[loading-overlay="true"] {
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 8px;
}

/* 通知樣式 */
QLabel[notification="true"] {
    background-color: #4a90e2;
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

QLabel[notification="success"] {
    background-color: #28a745;
}

QLabel[notification="warning"] {
    background-color: #ffc107;
    color: #000;
}

QLabel[notification="error"] {
    background-color: #dc3545;
}

/* 頁面切換動畫容器 */
QStackedWidget {
    background-color: transparent;
}

QStackedWidget QWidget {
    background-color: #1e1e1e;
    border-radius: 8px;
}
```

---

## 7. 性能優化和最佳實踐

### 動畫效能優化

```python
class AnimationPerformanceOptimizer:
    """動畫效能優化器"""
    
    @staticmethod
    def enable_hardware_acceleration():
        """啟用硬體加速"""
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    @staticmethod
    def optimize_animations_for_performance(widget: QWidget):
        """為組件優化動畫效能"""
        # 啟用混合模式
        widget.setAttribute(Qt.WA_NoSystemBackground, True)
        widget.setAttribute(Qt.WA_OpaquePaintEvent, True)
        
        # 啟用快速變換
        widget.setAttribute(Qt.WA_DontCreateNativeAncestors, True)
    
    @staticmethod
    def batch_animations(animations: List[QAbstractAnimation]) -> QParallelAnimationGroup:
        """批次處理動畫以提升效能"""
        group = QParallelAnimationGroup()
        
        # 按持續時間分組，避免過多短動畫
        short_animations = [a for a in animations if a.duration() <= 200]
        long_animations = [a for a in animations if a.duration() > 200]
        
        # 合併短動畫
        if short_animations:
            short_group = QParallelAnimationGroup()
            for animation in short_animations:
                short_group.addAnimation(animation)
            group.addAnimation(short_group)
        
        # 添加長動畫
        for animation in long_animations:
            group.addAnimation(animation)
        
        return group
```

### 記憶體管理

```python
class AnimationMemoryManager:
    """動畫記憶體管理器"""
    
    def __init__(self):
        self.animation_cache = {}
        self.max_cache_size = 50
    
    def cache_animation(self, key: str, animation: QAbstractAnimation):
        """快取動畫以重複使用"""
        if len(self.animation_cache) >= self.max_cache_size:
            # 移除最舊的動畫
            oldest_key = next(iter(self.animation_cache))
            del self.animation_cache[oldest_key]
        
        self.animation_cache[key] = animation
    
    def get_cached_animation(self, key: str) -> Optional[QAbstractAnimation]:
        """獲取快取的動畫"""
        return self.animation_cache.get(key)
    
    def clear_cache(self):
        """清除動畫快取"""
        for animation in self.animation_cache.values():
            if animation.state() == QAbstractAnimation.Running:
                animation.stop()
        self.animation_cache.clear()
```

---

## 8. 整合到現有專案

### 主窗口整合

```python
# 在 main_window.py 中的整合範例
class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_animations()  # 新增動畫設置
        self.setup_ui()
        
    def setup_animations(self):
        """設置主窗口動畫系統"""
        # 初始化動畫管理器
        animation_manager.set_animations_enabled(True)
        animation_manager.set_speed_factor(1.0)
        
        # 設置頁面切換動畫
        self.page_transition = PageTransitionManager(self.stacked_widget)
        
        # 設置主題切換動畫
        self.theme_transition = ThemeTransitionManager(self)
        
        # 設置響應式動畫
        self.responsive_animation = ResponsiveAnimationManager()
    
    def switch_to_tool(self, tool_index: int):
        """切換工具頁面 - 添加動畫效果"""
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == tool_index:
            return
        
        # 根據切換方向選擇動畫
        direction = "left" if tool_index > current_index else "right"
        self.page_transition.slide_to_page(tool_index, direction)
    
    def change_theme(self, theme_name: str):
        """切換主題 - 添加動畫效果"""
        current_theme = theme_manager.current_theme
        self.theme_transition.animate_theme_change(current_theme, theme_name)
        
    def resizeEvent(self, event):
        """視窗大小改變事件 - 響應式動畫"""
        super().resizeEvent(event)
        
        # 檢查斷點變化
        new_breakpoint = self.responsive_animation.get_current_breakpoint(event.size().width())
        if new_breakpoint != self.responsive_animation.current_breakpoint:
            self.responsive_animation.animate_layout_change(
                self.central_widget, 
                event.oldSize(), 
                event.size()
            )
```

### 配置文件整合

```yaml
# config/animation_settings.yaml
animation_settings:
  enabled: true
  global_speed_factor: 1.0
  max_concurrent_animations: 10
  
  page_transitions:
    enabled: true
    default_duration: 400
    easing_curve: "OutCubic"
    
  button_effects:
    hover_animation: true
    click_animation: true
    ripple_effect: true
    
  theme_transitions:
    enabled: true
    fade_duration: 300
    component_flash: true
    
  notifications:
    enabled: true
    auto_dismiss_time: 3000
    entrance_effect: "slide_right"
    
  performance:
    hardware_acceleration: true
    animation_caching: true
    batch_animations: true
```

---

## 9. 測試與除錯

### 動畫測試工具

```python
class AnimationDebugger:
    """動畫除錯工具"""
    
    def __init__(self):
        self.debug_mode = False
        self.performance_monitor = {}
        
    def enable_debug_mode(self):
        """啟用除錯模式"""
        self.debug_mode = True
        logger.info("Animation debug mode enabled")
    
    def log_animation_start(self, name: str, animation: QAbstractAnimation):
        """記錄動畫開始"""
        if self.debug_mode:
            import time
            self.performance_monitor[name] = {
                'start_time': time.time(),
                'duration': animation.duration(),
                'state': 'running'
            }
            logger.debug(f"Animation '{name}' started - Duration: {animation.duration()}ms")
    
    def log_animation_finished(self, name: str):
        """記錄動畫完成"""
        if self.debug_mode and name in self.performance_monitor:
            import time
            monitor_data = self.performance_monitor[name]
            actual_duration = (time.time() - monitor_data['start_time']) * 1000
            
            logger.debug(f"Animation '{name}' finished - "
                        f"Expected: {monitor_data['duration']}ms, "
                        f"Actual: {actual_duration:.1f}ms")
            
            del self.performance_monitor[name]
    
    def get_performance_report(self) -> Dict:
        """獲取效能報告"""
        return {
            'active_animations': len(self.performance_monitor),
            'animations': dict(self.performance_monitor)
        }

# 全域除錯器
animation_debugger = AnimationDebugger()
```

---

## 總結

這份動畫效果實現指南提供了完整的現代化動畫系統解決方案，包括：

### ✨ 核心特色
- **統一動畫管理** - 全域動畫控制和生命週期管理
- **豐富視覺效果** - 頁面切換、組件互動、通知反饋等多種動畫
- **效能優化** - 硬體加速、動畫快取、批次處理
- **主題整合** - 與深色主題無縫結合的動畫效果
- **響應式動畫** - 適應不同螢幕尺寸的動態效果

### 🔧 實用功能
- **即插即用** - 可直接整合到現有 CLI Tool 專案
- **高度可定制** - 靈活的配置選項和擴展接口
- **效能監控** - 內建除錯工具和效能分析
- **記憶體安全** - 完善的資源管理和清理機制

### 📱 現代化體驗
- **流暢的頁面切換** - 滑動、淡入淡出等多種過場動畫
- **互動式按鈕效果** - 懸停、點擊、選中狀態動畫
- **智能通知系統** - 帶動畫的訊息提示和反饋
- **載入狀態管理** - 優雅的載入指示器和進度動畫

這個動畫系統將大幅提升 CLI Tool 應用程式的用戶體驗，讓界面更加現代化和吸引人！🎊