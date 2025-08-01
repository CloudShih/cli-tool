"""
響應式佈局管理器 - 適應不同螢幕尺寸和解析度
"""

import logging
from typing import Dict, List, Tuple, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSplitter,
    QFrame, QLabel, QSizePolicy, QApplication
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QSize, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt5.QtGui import QFont, QScreen

logger = logging.getLogger(__name__)


class BreakpointManager:
    """斷點管理器 - 定義不同螢幕尺寸的斷點"""
    
    # 斷點定義 (寬度像素)
    BREAKPOINTS = {
        'xs': 0,      # 極小螢幕 (手機直立)
        'sm': 576,    # 小螢幕 (手機橫向)
        'md': 768,    # 中等螢幕 (平板直立)
        'lg': 992,    # 大螢幕 (平板橫向/小筆電)
        'xl': 1200,   # 超大螢幕 (桌面)
        'xxl': 1400   # 超超大螢幕 (大桌面)
    }
    
    @staticmethod
    def get_current_breakpoint(width: int) -> str:
        """根據寬度獲取當前斷點"""
        breakpoints = sorted(BreakpointManager.BREAKPOINTS.items(), key=lambda x: x[1], reverse=True)
        for name, min_width in breakpoints:
            if width >= min_width:
                return name
        return 'xs'
    
    @staticmethod
    def is_mobile(width: int) -> bool:
        """判斷是否為行動裝置尺寸"""
        return width < BreakpointManager.BREAKPOINTS['md']
    
    @staticmethod
    def is_tablet(width: int) -> bool:
        """判斷是否為平板尺寸"""
        return (BreakpointManager.BREAKPOINTS['md'] <= width < 
                BreakpointManager.BREAKPOINTS['lg'])
    
    @staticmethod
    def is_desktop(width: int) -> bool:
        """判斷是否為桌面尺寸"""
        return width >= BreakpointManager.BREAKPOINTS['lg']


class ResponsiveWidget(QWidget):
    """響應式組件基類"""
    
    breakpoint_changed = pyqtSignal(str)  # 斷點變更信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_breakpoint = 'lg'
        self.breakpoint_configs = {}
        self.resize_timer = QTimer(self)  # 設置父對象確保在正確線程中
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._handle_resize)
        self.setup_responsive()
    
    def setup_responsive(self):
        """設置響應式配置"""
        pass  # 子類實現
    
    def add_breakpoint_config(self, breakpoint: str, config: Dict):
        """添加斷點配置"""
        self.breakpoint_configs[breakpoint] = config
    
    def resizeEvent(self, event):
        """視窗大小變更事件"""
        super().resizeEvent(event)
        # 使用計時器防抖，避免頻繁觸發
        self.resize_timer.start(100)
    
    def _handle_resize(self):
        """處理大小變更"""
        current_width = self.width()
        new_breakpoint = BreakpointManager.get_current_breakpoint(current_width)
        
        if new_breakpoint != self.current_breakpoint:
            old_breakpoint = self.current_breakpoint
            self.current_breakpoint = new_breakpoint
            self.on_breakpoint_changed(old_breakpoint, new_breakpoint)
            self.breakpoint_changed.emit(new_breakpoint)
            
            logger.debug(f"Breakpoint changed: {old_breakpoint} -> {new_breakpoint} (width: {current_width})")
    
    def on_breakpoint_changed(self, old_breakpoint: str, new_breakpoint: str):
        """斷點變更回調"""
        self.apply_breakpoint_config(new_breakpoint)
    
    def apply_breakpoint_config(self, breakpoint: str):
        """應用斷點配置"""
        if breakpoint in self.breakpoint_configs:
            config = self.breakpoint_configs[breakpoint]
            self.apply_config(config)
    
    def apply_config(self, config: Dict):
        """應用配置"""
        pass  # 子類實現


class ResponsiveMainWindow(ResponsiveWidget):
    """響應式主窗口"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sidebar_visible = True
        self.setup_responsive()
        self.setup_animations()
    
    def setup_responsive(self):
        """設置響應式配置"""
        # 桌面配置 (xl, xxl)
        desktop_config = {
            'sidebar_width': 200,
            'sidebar_visible': True,
            'content_margins': (20, 20, 20, 20),
            'button_size': 'normal',
            'font_scale': 1.0
        }
        
        # 大螢幕配置 (lg)
        large_config = {
            'sidebar_width': 180,
            'sidebar_visible': True,
            'content_margins': (16, 16, 16, 16),
            'button_size': 'normal',
            'font_scale': 1.0
        }
        
        # 平板配置 (md)
        tablet_config = {
            'sidebar_width': 160,
            'sidebar_visible': True,
            'content_margins': (12, 12, 12, 12),
            'button_size': 'compact',
            'font_scale': 0.9
        }
        
        # 小螢幕配置 (sm)
        small_config = {
            'sidebar_width': 0,
            'sidebar_visible': False,
            'content_margins': (8, 8, 8, 8),
            'button_size': 'compact',
            'font_scale': 0.85
        }
        
        # 極小螢幕配置 (xs)
        tiny_config = {
            'sidebar_width': 0,
            'sidebar_visible': False,
            'content_margins': (4, 4, 4, 4),
            'button_size': 'small',
            'font_scale': 0.8
        }
        
        self.add_breakpoint_config('xxl', desktop_config)
        self.add_breakpoint_config('xl', desktop_config)
        self.add_breakpoint_config('lg', large_config)
        self.add_breakpoint_config('md', tablet_config)
        self.add_breakpoint_config('sm', small_config)
        self.add_breakpoint_config('xs', tiny_config)
    
    def setup_animations(self):
        """設置動畫"""
        try:
            # 側邊欄切換動畫 - 需要指定目標對象和屬性
            if hasattr(self.main_window, 'sidebar'):
                self.sidebar_animation = QPropertyAnimation(self.main_window.sidebar, b"geometry")
                self.sidebar_animation.setDuration(300)
                self.sidebar_animation.setEasingCurve(QEasingCurve.OutCubic)
            else:
                self.sidebar_animation = None
            
            # 內容區域動畫
            if hasattr(self.main_window, 'content_stack'):
                self.content_animation = QPropertyAnimation(self.main_window.content_stack, b"geometry")
                self.content_animation.setDuration(300)
                self.content_animation.setEasingCurve(QEasingCurve.OutCubic)
            else:
                self.content_animation = None
            
            # 並行動畫組
            self.layout_animation_group = QParallelAnimationGroup()
            if self.sidebar_animation:
                self.layout_animation_group.addAnimation(self.sidebar_animation)
            if self.content_animation:
                self.layout_animation_group.addAnimation(self.content_animation)
                
        except Exception as e:
            logger.error(f"Error setting up responsive components: {e}")
            # 設置空的動畫組避免後續錯誤
            self.layout_animation_group = QParallelAnimationGroup()
            self.sidebar_animation = None
            self.content_animation = None
    
    def apply_config(self, config: Dict):
        """應用響應式配置"""
        try:
            sidebar_visible = config.get('sidebar_visible', True)
            sidebar_width = config.get('sidebar_width', 200)
            content_margins = config.get('content_margins', (20, 20, 20, 20))
            font_scale = config.get('font_scale', 1.0)
            
            # 動畫切換側邊欄
            self.animate_sidebar_toggle(sidebar_visible, sidebar_width)
            
            # 更新內容邊距
            self.update_content_margins(content_margins)
            
            # 更新字體縮放
            self.update_font_scale(font_scale)
            
            logger.info(f"Applied responsive config: sidebar={sidebar_visible}, width={sidebar_width}")
            
        except Exception as e:
            logger.error(f"Error applying responsive config: {e}")
    
    def animate_sidebar_toggle(self, visible: bool, width: int):
        """動畫切換側邊欄顯示"""
        if not hasattr(self.main_window, 'sidebar'):
            return
        
        sidebar = self.main_window.sidebar
        current_width = sidebar.width()
        target_width = width if visible else 0
        
        if current_width == target_width:
            return
        
        # 設置動畫目標
        self.sidebar_animation.setTargetObject(sidebar)
        self.sidebar_animation.setPropertyName(b"maximumWidth")
        self.sidebar_animation.setStartValue(current_width)
        self.sidebar_animation.setEndValue(target_width)
        
        # 同時設置最小寬度
        def on_animation_finished():
            sidebar.setMinimumWidth(target_width)
            sidebar.setMaximumWidth(target_width)
            if not visible:
                sidebar.hide()
            else:
                sidebar.show()
        
        self.sidebar_animation.finished.connect(on_animation_finished)
        self.sidebar_animation.start()
        
        self.sidebar_visible = visible
    
    def update_content_margins(self, margins: Tuple[int, int, int, int]):
        """更新內容區域邊距"""
        if hasattr(self.main_window, 'content_stack'):
            # 為內容區域添加動畫更新邊距
            content_widget = self.main_window.content_stack.parentWidget()
            if content_widget and content_widget.layout():
                content_widget.layout().setContentsMargins(*margins)
    
    def update_font_scale(self, scale: float):
        """更新字體縮放"""
        try:
            app = QApplication.instance()
            if app:
                # 獲取默認字體
                default_font = app.font()
                base_size = 12  # 基礎字體大小
                
                # 計算新的字體大小
                new_size = int(base_size * scale)
                new_font = QFont(default_font.family(), new_size)
                
                # 應用到特定組件而不是全局
                self.apply_font_to_components(new_font)
                
        except Exception as e:
            logger.error(f"Error updating font scale: {e}")
    
    def apply_font_to_components(self, font: QFont):
        """將字體應用到特定組件"""
        # 這裡可以選擇性地應用字體到特定組件
        # 避免影響整個應用程式的字體設置
        pass
    
    def toggle_sidebar(self):
        """切換側邊欄顯示狀態"""
        new_visible = not self.sidebar_visible
        current_config = self.breakpoint_configs.get(self.current_breakpoint, {})
        width = current_config.get('sidebar_width', 200)
        
        self.animate_sidebar_toggle(new_visible, width if new_visible else 0)


class ResponsiveSplitter(QSplitter):
    """響應式分割器"""
    
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.responsive_configs = {}
        self.current_breakpoint = 'lg'
        self.setup_responsive()
    
    def setup_responsive(self):
        """設置響應式配置"""
        # 不同斷點的分割比例
        self.responsive_configs = {
            'xxl': [200, 800],    # 側邊欄:內容 = 200:800
            'xl': [200, 600],     # 側邊欄:內容 = 200:600
            'lg': [180, 500],     # 側邊欄:內容 = 180:500
            'md': [160, 400],     # 側邊欄:內容 = 160:400
            'sm': [0, 400],       # 隱藏側邊欄
            'xs': [0, 300]        # 隱藏側邊欄
        }
    
    def apply_responsive_sizes(self, breakpoint: str):
        """應用響應式尺寸"""
        if breakpoint in self.responsive_configs:
            sizes = self.responsive_configs[breakpoint]
            self.setSizes(sizes)
            self.current_breakpoint = breakpoint
            
            logger.debug(f"Applied responsive splitter sizes for {breakpoint}: {sizes}")


class AnimationPresets:
    """動畫預設集合"""
    
    @staticmethod
    def create_fade_animation(target: QWidget, duration: int = 300) -> QPropertyAnimation:
        """創建淡入淡出動畫"""
        animation = QPropertyAnimation(target, b"windowOpacity")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
    
    @staticmethod
    def create_slide_animation(target: QWidget, direction: str = 'right', duration: int = 400) -> QPropertyAnimation:
        """創建滑動動畫"""
        animation = QPropertyAnimation(target, b"pos")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
    
    @staticmethod
    def create_scale_animation(target: QWidget, scale_factor: float = 1.1, duration: int = 200) -> QPropertyAnimation:
        """創建縮放動畫"""
        animation = QPropertyAnimation(target, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        return animation
    
    @staticmethod
    def create_bounce_animation(target: QWidget, intensity: float = 0.1, duration: int = 600) -> QSequentialAnimationGroup:
        """創建彈跳動畫"""
        group = QSequentialAnimationGroup()
        
        # 向上彈跳
        up_animation = QPropertyAnimation(target, b"pos")
        up_animation.setDuration(duration // 3)
        up_animation.setEasingCurve(QEasingCurve.OutQuart)
        
        # 落下
        down_animation = QPropertyAnimation(target, b"pos")
        down_animation.setDuration(duration // 3)
        down_animation.setEasingCurve(QEasingCurve.InQuart)
        
        # 穩定
        settle_animation = QPropertyAnimation(target, b"pos")
        settle_animation.setDuration(duration // 3)
        settle_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        group.addAnimation(up_animation)
        group.addAnimation(down_animation)
        group.addAnimation(settle_animation)
        
        return group


class ResponsiveLayoutManager:
    """響應式佈局管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.responsive_window = None
        self.responsive_splitter = None
        self.setup_responsive_components()
    
    def setup_responsive_components(self):
        """設置響應式組件"""
        try:
            # 創建響應式主窗口管理器
            self.responsive_window = ResponsiveMainWindow(self.main_window)
            
            # 如果主窗口有分割器，設置響應式分割器
            if hasattr(self.main_window, 'centralWidget'):
                central_widget = self.main_window.centralWidget()
                if central_widget:
                    self.setup_responsive_splitter(central_widget)
            
            logger.info("Responsive layout manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up responsive components: {e}")
    
    def setup_responsive_splitter(self, parent_widget):
        """設置響應式分割器"""
        # 這裡可以根據實際的主窗口結構來設置分割器
        pass
    
    def get_current_breakpoint(self) -> str:
        """獲取當前斷點"""
        if self.responsive_window:
            return self.responsive_window.current_breakpoint
        return 'lg'
    
    def is_mobile_layout(self) -> bool:
        """判斷是否為行動佈局"""
        width = self.main_window.width() if self.main_window else 1000
        return BreakpointManager.is_mobile(width)
    
    def is_desktop_layout(self) -> bool:
        """判斷是否為桌面佈局"""
        width = self.main_window.width() if self.main_window else 1000
        return BreakpointManager.is_desktop(width)
    
    def toggle_sidebar(self):
        """切換側邊欄"""
        if self.responsive_window:
            self.responsive_window.toggle_sidebar()


# 便利函數
def create_responsive_layout_manager(main_window) -> ResponsiveLayoutManager:
    """創建響應式佈局管理器"""
    return ResponsiveLayoutManager(main_window)

def get_screen_info() -> Dict:
    """獲取螢幕資訊"""
    app = QApplication.instance()
    if not app:
        return {}
    
    screen = app.primaryScreen()
    if not screen:
        return {}
    
    geometry = screen.geometry()
    available_geometry = screen.availableGeometry()
    
    return {
        'width': geometry.width(),
        'height': geometry.height(),
        'available_width': available_geometry.width(),
        'available_height': available_geometry.height(),
        'dpi': screen.logicalDotsPerInch(),
        'device_pixel_ratio': screen.devicePixelRatio()
    }