# PyQt5 響應式佈局設計完整實現指南

## 📖 前言

響應式設計已成為現代應用程式開發的標準，不僅限於 Web 應用，桌面應用同樣需要適應不同的螢幕尺寸和使用情境。本指南將詳細介紹如何在 PyQt5 中實現完整的響應式佈局系統，包含斷點管理、動畫過渡和實用的實現技巧。

## 🎯 響應式設計理念

### 核心理念
1. **適應性優先**：界面應能自然適應各種螢幕尺寸
2. **內容為王**：響應式調整不應影響內容的可讀性和功能性
3. **漸進增強**：從最小功能集開始，逐步增強體驗
4. **性能平衡**：響應式功能不應影響應用性能

### 設計原則
- **移動優先**：先考慮小螢幕的使用體驗
- **斷點合理**：選擇符合實際設備的斷點尺寸
- **內容優先**：重要內容在小螢幕上依然可見
- **操作友好**：觸控設備的操作便利性

## 🏗️ 技術架構概述

### 響應式系統架構

```
ResponsiveLayoutSystem
├── BreakpointManager          # 斷點管理器
├── ResponsiveWidget           # 響應式組件基類
├── ResponsiveMainWindow       # 主視窗響應式管理
├── ResponsiveSplitter         # 響應式分割器
├── AnimationPresets           # 動畫預設
└── ResponsiveLayoutManager    # 整體佈局管理器
```

### 核心技術組件
1. **斷點系統**：基於視窗寬度的斷點檢測
2. **配置管理**：不同斷點的界面配置
3. **動畫過渡**：斷點切換時的平滑動畫
4. **狀態同步**：跨組件的響應式狀態管理

## 📐 斷點系統設計

### 斷點定義策略

```python
# breakpoint_definitions.py - 斷點定義
class BreakpointManager:
    """
    斷點管理器 - 定義響應式設計的關鍵尺寸點
    參考 Bootstrap 和 Material Design 的斷點標準
    """
    
    # 標準斷點定義 (寬度像素)
    BREAKPOINTS = {
        'xs': 0,      # 極小螢幕 320-575px (手機直立)
        'sm': 576,    # 小螢幕 576-767px (手機橫向/小平板)
        'md': 768,    # 中等螢幕 768-991px (平板直立)
        'lg': 992,    # 大螢幕 992-1199px (平板橫向/小筆電)
        'xl': 1200,   # 超大螢幕 1200-1399px (桌面)
        'xxl': 1400   # 超超大螢幕 1400px+ (大桌面/4K)
    }
    
    # 設備類型判斷閾值
    DEVICE_THRESHOLDS = {
        'mobile_max': 767,      # 手機設備最大寬度
        'tablet_min': 768,      # 平板設備最小寬度
        'tablet_max': 1199,     # 平板設備最大寬度
        'desktop_min': 1200     # 桌面設備最小寬度
    }
    
    @staticmethod
    def get_current_breakpoint(width: int) -> str:
        """
        根據寬度獲取當前斷點
        
        Args:
            width: 當前視窗寬度
            
        Returns:
            str: 斷點名稱 ('xs', 'sm', 'md', 'lg', 'xl', 'xxl')
        """
        # 按照從大到小的順序檢查斷點
        breakpoints = sorted(BreakpointManager.BREAKPOINTS.items(), 
                           key=lambda x: x[1], reverse=True)
        
        for name, min_width in breakpoints:
            if width >= min_width:
                return name
        return 'xs'  # 默認最小斷點
    
    @staticmethod
    def get_device_type(width: int) -> str:
        """
        判斷設備類型
        
        Args:
            width: 當前視窗寬度
            
        Returns:
            str: 設備類型 ('mobile', 'tablet', 'desktop')
        """
        thresholds = BreakpointManager.DEVICE_THRESHOLDS
        
        if width <= thresholds['mobile_max']:
            return 'mobile'
        elif width <= thresholds['tablet_max']:
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def is_mobile(width: int) -> bool:
        """判斷是否為行動裝置尺寸"""
        return width <= BreakpointManager.DEVICE_THRESHOLDS['mobile_max']
    
    @staticmethod
    def is_tablet(width: int) -> bool:
        """判斷是否為平板尺寸"""
        thresholds = BreakpointManager.DEVICE_THRESHOLDS
        return (thresholds['tablet_min'] <= width <= thresholds['tablet_max'])
    
    @staticmethod
    def is_desktop(width: int) -> bool:
        """判斷是否為桌面尺寸"""
        return width >= BreakpointManager.DEVICE_THRESHOLDS['desktop_min']
    
    @staticmethod
    def get_breakpoint_range(breakpoint: str) -> tuple:
        """
        獲取斷點的尺寸範圍
        
        Args:
            breakpoint: 斷點名稱
            
        Returns:
            tuple: (最小寬度, 最大寬度)，最大寬度為 None 表示無上限
        """
        breakpoints = BreakpointManager.BREAKPOINTS
        if breakpoint not in breakpoints:
            return (0, None)
        
        min_width = breakpoints[breakpoint]
        
        # 找到下一個更大的斷點
        larger_breakpoints = [
            (name, width) for name, width in breakpoints.items() 
            if width > min_width
        ]
        
        if larger_breakpoints:
            max_width = min(larger_breakpoints, key=lambda x: x[1])[1] - 1
            return (min_width, max_width)
        else:
            return (min_width, None)  # 最大斷點沒有上限
```

### 斷點使用範例

```python
# 使用範例
current_width = 1024
breakpoint = BreakpointManager.get_current_breakpoint(current_width)
device_type = BreakpointManager.get_device_type(current_width)

print(f"寬度 {current_width}px -> 斷點: {breakpoint}, 設備: {device_type}")
# 輸出: 寬度 1024px -> 斷點: lg, 設備: tablet
```

## 🧩 響應式組件基類

### ResponsiveWidget 基類實現

```python
# responsive_widget.py - 響應式組件基類
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QResizeEvent
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class ResponsiveWidget(QWidget):
    """
    響應式組件基類
    
    提供基礎的響應式功能：
    - 自動斷點檢測
    - 配置管理和應用
    - 防抖的尺寸變更處理
    - 信號通知機制
    """
    
    # 信號定義
    breakpoint_changed = pyqtSignal(str, str)  # (old_breakpoint, new_breakpoint)
    size_changed = pyqtSignal(int, int)        # (width, height)
    device_type_changed = pyqtSignal(str)      # device_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 響應式狀態
        self.current_breakpoint = 'lg'
        self.current_device_type = 'desktop'
        self.previous_size = (0, 0)
        
        # 配置存儲
        self.breakpoint_configs = {}
        self.device_configs = {}
        self.animation_configs = {}
        
        # 防抖計時器
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_resize_debounced)
        
        # 動畫管理
        self.active_animations = []
        
        # 初始化
        self.setup_responsive()
        self.setup_animations()
        self.detect_initial_breakpoint()
    
    def setup_responsive(self):
        """
        設置響應式配置
        子類應重寫此方法來定義具體的響應式行為
        """
        pass
    
    def setup_animations(self):
        """
        設置動畫配置
        子類可重寫此方法來定義動畫行為
        """
        pass
    
    def detect_initial_breakpoint(self):
        """檢測初始斷點狀態"""
        if self.width() > 0:  # 確保有有效尺寸
            self._update_breakpoint_state(self.width(), self.height())
    
    def add_breakpoint_config(self, breakpoint: str, config: Dict[str, Any]):
        """
        添加斷點配置
        
        Args:
            breakpoint: 斷點名稱
            config: 配置字典
        """
        self.breakpoint_configs[breakpoint] = config.copy()
        logger.debug(f"Added breakpoint config for {breakpoint}: {config}")
    
    def add_device_config(self, device_type: str, config: Dict[str, Any]):
        """
        添加設備類型配置
        
        Args:
            device_type: 設備類型 ('mobile', 'tablet', 'desktop')
            config: 配置字典
        """
        self.device_configs[device_type] = config.copy()
        logger.debug(f"Added device config for {device_type}: {config}")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        獲取當前應該應用的配置
        
        Returns:
            Dict: 合併後的配置
        """
        config = {}
        
        # 優先級：設備配置 > 斷點配置
        if self.current_device_type in self.device_configs:
            config.update(self.device_configs[self.current_device_type])
        
        if self.current_breakpoint in self.breakpoint_configs:
            config.update(self.breakpoint_configs[self.current_breakpoint])
        
        return config
    
    def resizeEvent(self, event: QResizeEvent):
        """
        視窗大小變更事件
        使用防抖機制避免頻繁觸發
        """
        super().resizeEvent(event)
        
        # 重啟防抖計時器
        self.resize_timer.stop()
        self.resize_timer.start(150)  # 150ms 防抖延遲
    
    def _handle_resize_debounced(self):
        """防抖後的尺寸變更處理"""
        current_size = (self.width(), self.height())
        
        # 檢查尺寸是否真的改變了
        if current_size != self.previous_size:
            self._update_breakpoint_state(current_size[0], current_size[1])
            self.previous_size = current_size
            self.size_changed.emit(current_size[0], current_size[1])
    
    def _update_breakpoint_state(self, width: int, height: int):
        """更新斷點狀態"""
        # 檢測新的斷點和設備類型
        new_breakpoint = BreakpointManager.get_current_breakpoint(width)
        new_device_type = BreakpointManager.get_device_type(width)
        
        # 斷點變更處理
        if new_breakpoint != self.current_breakpoint:
            old_breakpoint = self.current_breakpoint
            self.current_breakpoint = new_breakpoint
            
            self.on_breakpoint_changed(old_breakpoint, new_breakpoint)
            self.breakpoint_changed.emit(old_breakpoint, new_breakpoint)
            
            logger.info(f"Breakpoint changed: {old_breakpoint} -> {new_breakpoint} "
                       f"(width: {width}px)")
        
        # 設備類型變更處理
        if new_device_type != self.current_device_type:
            old_device_type = self.current_device_type
            self.current_device_type = new_device_type
            
            self.on_device_type_changed(old_device_type, new_device_type)
            self.device_type_changed.emit(new_device_type)
            
            logger.info(f"Device type changed: {old_device_type} -> {new_device_type}")
    
    def on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """
        斷點變更回調
        子類可重寫此方法來處理斷點變更
        """
        self.apply_current_config(animate=True)
    
    def on_device_type_changed(self, old_device_type: str, new_device_type: str):
        """
        設備類型變更回調
        子類可重寫此方法來處理設備類型變更
        """
        pass
    
    def apply_current_config(self, animate: bool = False):
        """
        應用當前配置
        
        Args:
            animate: 是否使用動畫過渡
        """
        config = self.get_current_config()
        if config:
            if animate and self.supports_animation():
                self.apply_config_animated(config)
            else:
                self.apply_config(config)
    
    def apply_config(self, config: Dict[str, Any]):
        """
        應用配置（無動畫）
        子類應重寫此方法來實現具體的配置應用邏輯
        """
        pass
    
    def apply_config_animated(self, config: Dict[str, Any]):
        """
        應用配置（含動畫）
        子類可重寫此方法來實現動畫配置應用
        """
        # 默認實現：直接應用配置
        self.apply_config(config)
    
    def supports_animation(self) -> bool:
        """
        檢查是否支援動畫
        可以根據系統性能或用戶偏好來決定
        """
        # 檢查是否在應用設定中禁用了動畫
        app = QApplication.instance()
        if app and hasattr(app, 'animation_enabled'):
            return app.animation_enabled
        
        return True  # 默認支援動畫
    
    def create_property_animation(self, target: QWidget, property_name: bytes, 
                                duration: int = 300) -> QPropertyAnimation:
        """
        創建屬性動畫的便利方法
        
        Args:
            target: 目標組件
            property_name: 屬性名稱
            duration: 動畫時長
            
        Returns:
            QPropertyAnimation: 配置好的動畫物件
        """
        animation = QPropertyAnimation(target, property_name)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 動畫完成後自動清理
        animation.finished.connect(lambda: self._cleanup_animation(animation))
        
        # 記錄活動動畫
        self.active_animations.append(animation)
        
        return animation
    
    def _cleanup_animation(self, animation: QPropertyAnimation):
        """清理完成的動畫"""
        if animation in self.active_animations:
            self.active_animations.remove(animation)
        animation.deleteLater()
    
    def cleanup_all_animations(self):
        """清理所有活動動畫"""
        for animation in self.active_animations[:]:  # 複製列表避免修改衝突
            animation.stop()
            self._cleanup_animation(animation)
    
    def get_responsive_info(self) -> Dict[str, Any]:
        """
        獲取響應式狀態資訊
        用於調試或狀態顯示
        """
        return {
            'current_breakpoint': self.current_breakpoint,
            'current_device_type': self.current_device_type,
            'size': (self.width(), self.height()),
            'available_breakpoints': list(self.breakpoint_configs.keys()),
            'available_devices': list(self.device_configs.keys()),
            'active_animations': len(self.active_animations)
        }
    
    def force_breakpoint(self, breakpoint: str):
        """
        強制設定斷點（用於測試）
        
        Args:
            breakpoint: 要強制設定的斷點
        """
        if breakpoint in BreakpointManager.BREAKPOINTS:
            old_breakpoint = self.current_breakpoint
            self.current_breakpoint = breakpoint
            self.on_breakpoint_changed(old_breakpoint, breakpoint)
            logger.debug(f"Forced breakpoint to: {breakpoint}")
```

## 🖼️ 響應式主視窗實現

### ResponsiveMainWindow 完整實現

```python
# responsive_main_window.py - 響應式主視窗
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QFrame, QLabel, QApplication)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QFont
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResponsiveMainWindow(ResponsiveWidget):
    """
    響應式主視窗管理器
    
    管理主視窗的響應式行為：
    - 側邊欄顯示/隱藏
    - 內容區域調整
    - 字體縮放
    - 邊距調整
    """
    
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        super().__init__()
        
        # 響應式狀態
        self.sidebar_visible = True
        self.original_sidebar_width = 200
        
        # 動畫組件
        self.sidebar_animation = None
        self.content_animation = None
        self.layout_animation_group = None
        
        self.setup_components()
    
    def setup_responsive(self):
        """設置響應式配置"""
        
        # 超大桌面配置 (xxl: 1400px+)
        xxl_config = {
            'sidebar_width': 240,
            'sidebar_visible': True,
            'content_margins': (24, 24, 24, 24),
            'toolbar_size': 'large',
            'font_scale': 1.1,
            'spacing': 16
        }
        
        # 大桌面配置 (xl: 1200-1399px)
        xl_config = {
            'sidebar_width': 200,
            'sidebar_visible': True,
            'content_margins': (20, 20, 20, 20),
            'toolbar_size': 'normal',
            'font_scale': 1.0,
            'spacing': 12
        }
        
        # 大螢幕配置 (lg: 992-1199px)
        lg_config = {
            'sidebar_width': 180,
            'sidebar_visible': True,
            'content_margins': (16, 16, 16, 16),
            'toolbar_size': 'normal',
            'font_scale': 0.95,
            'spacing': 10
        }
        
        # 平板配置 (md: 768-991px)
        md_config = {
            'sidebar_width': 160,
            'sidebar_visible': True,
            'content_margins': (12, 12, 12, 12),
            'toolbar_size': 'compact',
            'font_scale': 0.9,
            'spacing': 8
        }
        
        # 小螢幕配置 (sm: 576-767px)
        sm_config = {
            'sidebar_width': 0,
            'sidebar_visible': False,
            'content_margins': (8, 8, 8, 8),
            'toolbar_size': 'compact',
            'font_scale': 0.85,
            'spacing': 6
        }
        
        # 極小螢幕配置 (xs: 0-575px)
        xs_config = {
            'sidebar_width': 0,
            'sidebar_visible': False,
            'content_margins': (4, 4, 4, 4),
            'toolbar_size': 'small',
            'font_scale': 0.8,
            'spacing': 4
        }
        
        # 添加斷點配置
        self.add_breakpoint_config('xxl', xxl_config)
        self.add_breakpoint_config('xl', xl_config)
        self.add_breakpoint_config('lg', lg_config)
        self.add_breakpoint_config('md', md_config)
        self.add_breakpoint_config('sm', sm_config)
        self.add_breakpoint_config('xs', xs_config)
        
        # 設備類型配置
        mobile_config = {
            'touch_friendly': True,
            'button_min_size': 44,  # 觸控友好的最小尺寸
            'gesture_enabled': True
        }
        
        tablet_config = {
            'touch_friendly': True,
            'button_min_size': 40,
            'gesture_enabled': True
        }
        
        desktop_config = {
            'touch_friendly': False,
            'button_min_size': 32,
            'gesture_enabled': False
        }
        
        self.add_device_config('mobile', mobile_config)
        self.add_device_config('tablet', tablet_config)
        self.add_device_config('desktop', desktop_config)
    
    def setup_components(self):
        """設置響應式組件"""
        try:
            self.find_ui_components()
            self.setup_animations()
            self.apply_current_config(animate=False)
            
            logger.info("Responsive main window setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up responsive main window: {e}")
    
    def find_ui_components(self):
        """查找並連結 UI 組件"""
        # 查找側邊欄
        if hasattr(self.main_window, 'sidebar'):
            self.sidebar = self.main_window.sidebar
        else:
            # 嘗試通過物件名稱查找
            self.sidebar = self.main_window.findChild(QFrame, 'sidebar')
        
        # 查找內容區域
        if hasattr(self.main_window, 'content_stack'):
            self.content_area = self.main_window.content_stack
        elif hasattr(self.main_window, 'central_widget'):
            self.content_area = self.main_window.central_widget
        else:
            self.content_area = self.main_window.centralWidget()
        
        # 查找主要佈局
        if self.content_area and self.content_area.layout():
            self.main_layout = self.content_area.layout()
        else:
            self.main_layout = None
        
        logger.debug(f"Found UI components - Sidebar: {self.sidebar is not None}, "
                    f"Content: {self.content_area is not None}")
    
    def setup_animations(self):
        """設置動畫組件"""
        try:
            # 側邊欄寬度動畫
            if self.sidebar:
                self.sidebar_animation = self.create_property_animation(
                    self.sidebar, b"maximumWidth", duration=300
                )
            
            # 並行動畫組
            self.layout_animation_group = QParallelAnimationGroup()
            if self.sidebar_animation:
                self.layout_animation_group.addAnimation(self.sidebar_animation)
            
            logger.debug("Animation components setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up animations: {e}")
            self.layout_animation_group = QParallelAnimationGroup()
    
    def apply_config(self, config: Dict[str, Any]):
        """應用響應式配置（無動畫）"""
        try:
            # 側邊欄配置
            sidebar_visible = config.get('sidebar_visible', True)
            sidebar_width = config.get('sidebar_width', 200)
            self.apply_sidebar_config(sidebar_visible, sidebar_width, animate=False)
            
            # 內容邊距配置
            content_margins = config.get('content_margins', (20, 20, 20, 20))
            self.apply_content_margins(content_margins)
            
            # 字體縮放配置
            font_scale = config.get('font_scale', 1.0)
            self.apply_font_scale(font_scale)
            
            # 間距配置
            spacing = config.get('spacing', 12)
            self.apply_spacing(spacing)
            
            # 工具欄配置
            toolbar_size = config.get('toolbar_size', 'normal')
            self.apply_toolbar_size(toolbar_size)
            
            logger.debug(f"Applied responsive config: {config}")
            
        except Exception as e:
            logger.error(f"Error applying config: {e}")
    
    def apply_config_animated(self, config: Dict[str, Any]):
        """應用響應式配置（含動畫）"""
        try:
            # 側邊欄動畫配置
            sidebar_visible = config.get('sidebar_visible', True)
            sidebar_width = config.get('sidebar_width', 200)
            self.apply_sidebar_config(sidebar_visible, sidebar_width, animate=True)
            
            # 其他配置不需要動畫
            content_margins = config.get('content_margins', (20, 20, 20, 20))
            self.apply_content_margins(content_margins)
            
            font_scale = config.get('font_scale', 1.0)
            self.apply_font_scale(font_scale)
            
            spacing = config.get('spacing', 12)
            self.apply_spacing(spacing)
            
            toolbar_size = config.get('toolbar_size', 'normal')
            self.apply_toolbar_size(toolbar_size)
            
        except Exception as e:
            logger.error(f"Error applying animated config: {e}")
            # 降級到無動畫版本
            self.apply_config(config)
    
    def apply_sidebar_config(self, visible: bool, width: int, animate: bool = True):
        """應用側邊欄配置"""
        if not self.sidebar:
            return
        
        target_width = width if visible else 0
        current_width = self.sidebar.width()
        
        if current_width == target_width:
            return
        
        if animate and self.sidebar_animation:
            # 動畫切換
            self.sidebar_animation.setStartValue(current_width)
            self.sidebar_animation.setEndValue(target_width)
            
            # 動畫完成後的處理
            def on_animation_finished():
                self.sidebar.setMinimumWidth(target_width)
                self.sidebar.setMaximumWidth(target_width)
                if not visible:
                    self.sidebar.hide()
                else:
                    self.sidebar.show()
                self.sidebar_visible = visible
            
            self.sidebar_animation.finished.connect(on_animation_finished)
            self.sidebar_animation.start()
        else:
            # 直接設置
            self.sidebar.setMinimumWidth(target_width)
            self.sidebar.setMaximumWidth(target_width)
            if not visible:
                self.sidebar.hide()
            else:
                self.sidebar.show()
            self.sidebar_visible = visible
    
    def apply_content_margins(self, margins: tuple):
        """應用內容邊距"""
        if self.main_layout:
            self.main_layout.setContentsMargins(*margins)
    
    def apply_font_scale(self, scale: float):
        """應用字體縮放"""
        try:
            # 獲取當前應用的字體
            app = QApplication.instance()
            if app:
                current_font = app.font()
                base_size = 12  # 基礎字體大小
                
                # 計算新的字體大小
                new_size = max(8, int(base_size * scale))  # 最小 8px
                new_font = QFont(current_font.family(), new_size)
                
                # 應用到主視窗（而不是整個應用）
                self.main_window.setFont(new_font)
                
        except Exception as e:
            logger.error(f"Error applying font scale: {e}")
    
    def apply_spacing(self, spacing: int):
        """應用間距設置"""
        if self.main_layout:
            self.main_layout.setSpacing(spacing)
    
    def apply_toolbar_size(self, size: str):
        """應用工具欄大小"""
        # 這裡可以根據實際的工具欄組件來實現
        # 例如調整工具欄按鈕大小、圖示大小等
        pass
    
    def toggle_sidebar(self):
        """切換側邊欄顯示狀態"""
        if not self.sidebar:
            return
        
        new_visible = not self.sidebar_visible
        current_config = self.get_current_config()
        default_width = current_config.get('sidebar_width', 200)
        
        target_width = default_width if new_visible else 0
        self.apply_sidebar_config(new_visible, target_width, animate=True)
    
    def get_responsive_info(self) -> Dict[str, Any]:
        """獲取響應式狀態資訊"""
        base_info = super().get_responsive_info()
        
        # 添加主視窗特定資訊
        base_info.update({
            'sidebar_visible': self.sidebar_visible,
            'sidebar_width': self.sidebar.width() if self.sidebar else 0,
            'window_size': (self.main_window.width(), self.main_window.height()),
            'has_sidebar': self.sidebar is not None,
            'has_content_area': self.content_area is not None
        })
        
        return base_info
```

## 📱 移動端適配策略

### 觸控友好的響應式設計

```python
# mobile_optimizations.py - 移動端優化
class MobileOptimizations:
    """移動端優化配置"""
    
    # 觸控友好的最小尺寸 (依據 Apple 和 Google 設計指引)
    TOUCH_TARGET_SIZES = {
        'minimum': 44,      # 最小觸控目標尺寸 (iOS 標準)
        'comfortable': 48,  # 舒適觸控目標尺寸 (Material Design)
        'generous': 56      # 寬鬆觸控目標尺寸
    }
    
    # 移動端字體縮放建議
    MOBILE_FONT_SCALES = {
        'xs': 0.75,  # 320px 極小螢幕
        'sm': 0.85,  # 576px 小螢幕
        'md': 0.95   # 768px 中等螢幕
    }
    
    # 移動端間距建議
    MOBILE_SPACING = {
        'xs': 4,   # 極小間距
        'sm': 8,   # 小間距
        'md': 12   # 中等間距
    }
    
    @staticmethod
    def apply_touch_friendly_styles(widget: QWidget, device_type: str):
        """應用觸控友好樣式"""
        if device_type in ['mobile', 'tablet']:
            # 設置最小觸控目標尺寸
            min_size = MobileOptimizations.TOUCH_TARGET_SIZES['minimum']
            widget.setMinimumHeight(min_size)
            
            # 應用觸控友好的樣式
            widget.setStyleSheet(f"""
                QPushButton {{
                    min-height: {min_size}px;
                    padding: 8px 16px;
                    font-size: 14px;
                }}
                
                QLineEdit {{
                    min-height: {min_size}px;
                    padding: 8px;
                    font-size: 14px;
                }}
                
                QComboBox {{
                    min-height: {min_size}px;
                    padding: 4px 8px;
                    font-size: 14px;
                }}
            """)
```

### 手勢支援實現

```python
# gesture_support.py - 手勢支援
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QPointF
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget

class GestureDetector(QObject):
    """手勢檢測器"""
    
    # 手勢信號
    swipe_left = pyqtSignal()
    swipe_right = pyqtSignal()
    swipe_up = pyqtSignal()
    swipe_down = pyqtSignal()
    pinch_zoom = pyqtSignal(float)  # 縮放因子
    
    def __init__(self, target_widget: QWidget):
        super().__init__()
        self.target_widget = target_widget
        self.target_widget.installEventFilter(self)
        
        # 手勢參數
        self.min_swipe_distance = 50
        self.max_swipe_time = 500
        
        # 狀態追蹤
        self.start_pos = None
        self.start_time = None
        self.is_swiping = False
        
    def eventFilter(self, obj, event):
        """事件過濾器"""
        if obj == self.target_widget:
            if event.type() == QMouseEvent.MouseButtonPress:
                self.start_pos = event.pos()
                self.start_time = QTimer()
                self.start_time.start()
                self.is_swiping = True
                
            elif event.type() == QMouseEvent.MouseButtonRelease and self.is_swiping:
                if self.start_pos and self.start_time:
                    end_pos = event.pos()
                    elapsed_time = self.start_time.elapsed()
                    
                    if elapsed_time <= self.max_swipe_time:
                        self.detect_swipe(self.start_pos, end_pos)
                
                self.reset_gesture_state()
        
        return super().eventFilter(obj, event)
    
    def detect_swipe(self, start_pos: QPointF, end_pos: QPointF):
        """檢測滑動手勢"""
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance >= self.min_swipe_distance:
            # 判斷主要方向
            if abs(dx) > abs(dy):
                # 水平滑動
                if dx > 0:
                    self.swipe_right.emit()
                else:
                    self.swipe_left.emit()
            else:
                # 垂直滑動
                if dy > 0:
                    self.swipe_down.emit()
                else:
                    self.swipe_up.emit()
    
    def reset_gesture_state(self):
        """重置手勢狀態"""
        self.start_pos = None
        self.start_time = None
        self.is_swiping = False
```

## 🎬 響應式動畫系統

### 動畫預設集合

```python
# responsive_animations.py - 響應式動畫
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QTransform
import math

class ResponsiveAnimations:
    """響應式動畫預設集合"""
    
    # 動畫時長配置
    DURATIONS = {
        'fast': 150,
        'normal': 300,
        'slow': 500,
        'very_slow': 800
    }
    
    # 緩動曲線配置
    EASING_CURVES = {
        'ease_out': QEasingCurve.OutCubic,
        'ease_in': QEasingCurve.InCubic,
        'ease_in_out': QEasingCurve.InOutCubic,
        'bounce': QEasingCurve.OutBounce,
        'elastic': QEasingCurve.OutElastic
    }
    
    @staticmethod
    def create_layout_transition(widget: QWidget, from_size: tuple, to_size: tuple,
                               duration: int = 300) -> QPropertyAnimation:
        """創建佈局過渡動畫"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 設置起始和結束幾何體
        from PyQt5.QtCore import QRect
        start_rect = QRect(widget.x(), widget.y(), from_size[0], from_size[1])
        end_rect = QRect(widget.x(), widget.y(), to_size[0], to_size[1])
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation
    
    @staticmethod
    def create_sidebar_toggle(sidebar: QWidget, visible: bool, 
                            width: int = 200, duration: int = 300) -> QParallelAnimationGroup:
        """創建側邊欄切換動畫"""
        animation_group = QParallelAnimationGroup()
        
        # 寬度動畫
        width_animation = QPropertyAnimation(sidebar, b"maximumWidth")
        width_animation.setDuration(duration)
        width_animation.setEasingCurve(QEasingCurve.OutCubic)
        width_animation.setStartValue(sidebar.width())
        width_animation.setEndValue(width if visible else 0)
        
        # 透明度動畫
        opacity_effect = QGraphicsOpacityEffect()
        sidebar.setGraphicsEffect(opacity_effect)
        
        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        opacity_animation.setStartValue(1.0 if visible else 0.0)
        opacity_animation.setEndValue(1.0 if visible else 0.0)
        
        animation_group.addAnimation(width_animation)
        animation_group.addAnimation(opacity_animation)
        
        return animation_group
    
    @staticmethod
    def create_content_reflow(content_widget: QWidget, 
                            duration: int = 250) -> QPropertyAnimation:
        """創建內容重新排列動畫"""
        # 創建位置動畫
        animation = QPropertyAnimation(content_widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        return animation
    
    @staticmethod
    def create_breakpoint_transition(widget: QWidget, old_breakpoint: str, 
                                   new_breakpoint: str) -> QSequentialAnimationGroup:
        """創建斷點過渡動畫"""
        sequence = QSequentialAnimationGroup()
        
        # 第一階段：輕微縮放準備
        prepare_animation = QPropertyAnimation(widget, b"geometry")
        prepare_animation.setDuration(100)
        prepare_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 第二階段：實際變更
        change_animation = QPropertyAnimation(widget, b"geometry")
        change_animation.setDuration(200)
        change_animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # 第三階段：穩定
        settle_animation = QPropertyAnimation(widget, b"geometry")
        settle_animation.setDuration(100)
        settle_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        sequence.addAnimation(prepare_animation)
        sequence.addAnimation(change_animation)
        sequence.addAnimation(settle_animation)
        
        return sequence
    
    @staticmethod
    def create_mobile_slide_in(widget: QWidget, direction: str = 'left',
                             duration: int = 350) -> QPropertyAnimation:
        """創建移動端滑入動畫"""
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        
        # 根據方向設置起始位置
        current_pos = widget.pos()
        if direction == 'left':
            start_pos = current_pos - widget.size().width()
        elif direction == 'right':
            start_pos = current_pos + widget.size().width()
        elif direction == 'up':
            start_pos = current_pos - widget.size().height()
        else:  # 'down'
            start_pos = current_pos + widget.size().height()
        
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        
        return animation
```

## 🔧 實際應用範例

### 完整的響應式應用範例

```python
# responsive_app_example.py - 完整範例
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import logging

# 設置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResponsiveApp(QMainWindow):
    """響應式應用範例"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_responsive()
    
    def setup_ui(self):
        """設置基礎 UI"""
        self.setWindowTitle("響應式 PyQt5 應用範例")
        self.setGeometry(100, 100, 1200, 800)
        
        # 創建中央組件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 側邊欄
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #555;")
        
        # 內容區域
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #1e1e1e;")
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area, 1)  # 拉伸因子為 1
    
    def setup_responsive(self):
        """設置響應式管理"""
        self.responsive_manager = ResponsiveMainWindow(self)
        
        # 連接響應式事件
        self.responsive_manager.breakpoint_changed.connect(self.on_breakpoint_changed)
        self.responsive_manager.device_type_changed.connect(self.on_device_type_changed)
        
        # 設置初始狀態
        self.responsive_manager.detect_initial_breakpoint()
    
    def on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """斷點變更處理"""
        logger.info(f"Breakpoint changed from {old_breakpoint} to {new_breakpoint}")
        
        # 可以在這裡添加自定義的響應式邏輯
        info = self.responsive_manager.get_responsive_info()
        self.setWindowTitle(f"響應式應用 - {new_breakpoint.upper()} ({info['size'][0]}x{info['size'][1]})")
    
    def on_device_type_changed(self, device_type: str):
        """設備類型變更處理"""
        logger.info(f"Device type changed to {device_type}")
    
    def keyPressEvent(self, event):
        """鍵盤事件 - 用於測試"""
        if event.key() == Qt.Key_S:
            # 按 S 鍵切換側邊欄
            self.responsive_manager.toggle_sidebar()
        elif event.key() == Qt.Key_I:
            # 按 I 鍵顯示響應式資訊
            info = self.responsive_manager.get_responsive_info()
            logger.info(f"Responsive info: {info}")
        
        super().keyPressEvent(event)

def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    # 設置應用屬性
    app.setApplicationName("Responsive PyQt5 Example")
    app.setOrganizationName("Example Corp")
    
    # 創建主視窗
    window = ResponsiveApp()
    window.show()
    
    # 顯示使用說明
    logger.info("響應式應用已啟動")
    logger.info("使用說明：")
    logger.info("- 調整視窗大小觀察響應式效果")
    logger.info("- 按 S 鍵切換側邊欄")
    logger.info("- 按 I 鍵顯示響應式資訊")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
```

## 🎯 最佳實踐與注意事項

### 1. 性能優化建議

```python
# performance_tips.py - 性能優化建議
class PerformanceOptimizations:
    """響應式設計性能優化"""
    
    @staticmethod
    def optimize_resize_handling():
        """優化尺寸變更處理"""
        # 使用防抖機制
        # 推薦防抖延遲：100-200ms
        # 避免在 resizeEvent 中進行重量級操作
        pass
    
    @staticmethod
    def optimize_animations():
        """優化動畫性能"""
        # 使用硬體加速的屬性：geometry, opacity
        # 避免同時運行過多動畫
        # 為低端設備提供動畫降級選項
        pass
    
    @staticmethod
    def optimize_memory_usage():
        """優化記憶體使用"""
        # 及時清理完成的動畫
        # 避免在響應式回調中創建大量物件
        # 使用物件池重用動畫物件
        pass
```

### 2. 調試與測試

```python
# responsive_debugger.py - 響應式調試工具
class ResponsiveDebugger:
    """響應式設計調試工具"""
    
    def __init__(self, responsive_widget):
        self.responsive_widget = responsive_widget
        self.debug_enabled = True
    
    def log_breakpoint_info(self):
        """記錄斷點資訊"""
        if self.debug_enabled:
            info = self.responsive_widget.get_responsive_info()
            print(f"=== Responsive Debug Info ===")
            print(f"Current breakpoint: {info['current_breakpoint']}")
            print(f"Device type: {info['current_device_type']}")
            print(f"Size: {info['size']}")
            print(f"Active animations: {info.get('active_animations', 0)}")
    
    def simulate_device_sizes(self):
        """模擬不同設備尺寸"""
        test_sizes = [
            (320, 568),   # iPhone SE
            (375, 667),   # iPhone 8
            (768, 1024),  # iPad
            (1024, 768),  # iPad Landscape
            (1920, 1080), # Desktop HD
            (2560, 1440)  # Desktop QHD
        ]
        
        for width, height in test_sizes:
            print(f"Testing size: {width}x{height}")
            breakpoint = BreakpointManager.get_current_breakpoint(width)
            device_type = BreakpointManager.get_device_type(width)
            print(f"  -> Breakpoint: {breakpoint}, Device: {device_type}")
```

### 3. 無障礙考量

```python
# accessibility_helpers.py - 無障礙協助
class AccessibilityHelpers:
    """無障礙設計協助"""
    
    @staticmethod
    def respect_system_preferences():
        """尊重系統偏好設定"""
        # 檢查系統是否禁用動畫
        # 檢查高對比度模式
        # 檢查字體大小偏好
        pass
    
    @staticmethod
    def ensure_touch_targets():
        """確保觸控目標大小"""
        # 最小 44x44px 觸控目標
        # 足夠的間距避免誤觸
        pass
    
    @staticmethod
    def maintain_focus_order():
        """維護焦點順序"""
        # 響應式變更不應影響 Tab 順序
        # 隱藏元素應從 Tab 順序中移除
        pass
```

## 📋 實施檢查清單

### 規劃階段
- [ ] 定義目標設備和螢幕尺寸範圍
- [ ] 設計斷點策略和響應式規則
- [ ] 規劃內容優先級和佈局變化
- [ ] 考慮動畫和過渡效果需求

### 實現階段
- [ ] 實現 BreakpointManager 斷點管理器
- [ ] 創建 ResponsiveWidget 基類
- [ ] 實現具體的響應式組件
- [ ] 添加動畫過渡效果
- [ ] 整合到主應用架構

### 測試階段
- [ ] 測試所有斷點的正確觸發
- [ ] 驗證不同尺寸下的佈局正確性
- [ ] 測試動畫效果的流暢度
- [ ] 驗證性能表現
- [ ] 檢查無障礙兼容性

### 優化階段
- [ ] 性能監控和優化
- [ ] 記憶體使用優化
- [ ] 動畫效果調優
- [ ] 用戶體驗改進

## 🚀 進階技巧

### 1. 自適應圖片載入

```python
class ResponsiveImageLoader:
    """響應式圖片載入器"""
    
    def load_appropriate_image(self, base_path: str, breakpoint: str) -> str:
        """根據斷點載入適當的圖片"""
        size_suffixes = {
            'xs': '_small',
            'sm': '_small',
            'md': '_medium',
            'lg': '_large',
            'xl': '_xlarge',
            'xxl': '_xxlarge'
        }
        
        suffix = size_suffixes.get(breakpoint, '_medium')
        return f"{base_path}{suffix}.png"
```

### 2. 響應式字體系統

```python
class ResponsiveFontSystem:
    """響應式字體系統"""
    
    FONT_SCALES = {
        'xs': {'base': 12, 'heading': 18, 'small': 10},
        'sm': {'base': 13, 'heading': 20, 'small': 11},
        'md': {'base': 14, 'heading': 22, 'small': 12},
        'lg': {'base': 14, 'heading': 24, 'small': 12},
        'xl': {'base': 15, 'heading': 26, 'small': 13},
        'xxl': {'base': 16, 'heading': 28, 'small': 14}
    }
    
    def get_font_size(self, breakpoint: str, font_type: str = 'base') -> int:
        """獲取指定斷點和類型的字體大小"""
        return self.FONT_SCALES.get(breakpoint, self.FONT_SCALES['lg']).get(font_type, 14)
```

## 📚 延伸學習資源

### 設計參考
- [Material Design Responsive Layout Grid](https://material.io/design/layout/responsive-layout-grid.html)
- [Bootstrap Responsive Breakpoints](https://getbootstrap.com/docs/5.0/layout/breakpoints/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)

### 技術文檔
- [Qt Documentation - Layouts](https://doc.qt.io/qt-5/layout.html)
- [Qt Documentation - Animation Framework](https://doc.qt.io/qt-5/animation-overview.html)

### 工具和測試
- **響應式測試工具**：模擬不同設備尺寸
- **性能監控工具**：測量動畫性能和記憶體使用
- **無障礙測試工具**：驗證觸控目標和對比度

## 🎉 總結

響應式佈局設計不僅是現代應用的必備特性，更是提升用戶體驗的關鍵因素。通過本指南提供的完整技術方案，您可以：

### 核心收獲
1. **理解響應式設計理念**：從移動優先到漸進增強
2. **掌握 PyQt5 響應式實現**：斷點管理、組件適配、動畫過渡
3. **獲得完整的代碼框架**：可直接使用的響應式組件庫
4. **學會性能優化技巧**：避免常見陷阱，提升應用效能
5. **了解無障礙最佳實踐**：建設包容性的用戶界面

### 實踐價值
- **提升用戶體驗**：在任何設備上都能提供優秀的使用體驗
- **降低維護成本**：統一的響應式框架減少重複開發
- **增強應用競爭力**：現代化的界面適配各種使用情境
- **支援未來擴展**：靈活的架構支援新設備和新需求

響應式設計是一個持續演進的領域，隨著新設備和新交互方式的出現，我們的響應式策略也需要不斷調整和優化。掌握本指南的技術原理和實現方法，將為您的 PyQt5 應用開發提供堅實的基礎。

---

**作者**: Claude Code SuperClaude  
**版本**: 1.0  
**最後更新**: 2025-08-18  
**適用於**: PyQt5 5.15+, Python 3.7+  
**依賴**: 無額外依賴，僅使用 PyQt5 原生功能