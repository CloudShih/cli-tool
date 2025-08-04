"""
插件載入器 - 提供插件載入動畫和進度反饋
"""

import logging
import time
from typing import Dict, List, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QApplication
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QRect, QParallelAnimationGroup
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush

from ui.components.indicators import LoadingSpinner, ProgressIndicator, StatusIndicator
from ui.components.buttons import ModernButton

logger = logging.getLogger(__name__)


class PluginLoadingCard(QFrame):
    """單個插件載入卡片"""
    
    def __init__(self, plugin_name: str, plugin_description: str = "", parent=None):
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.plugin_description = plugin_description
        self.is_loading = False
        self.is_complete = False
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """設置 UI"""
        self.setProperty("plugin-card", True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # 插件信息區域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # 插件名稱
        self.name_label = QLabel(self.plugin_name.title())
        self.name_label.setProperty("plugin-name", True)
        info_layout.addWidget(self.name_label)
        
        # 插件描述
        self.desc_label = QLabel(self.plugin_description or f"{self.plugin_name} plugin")
        self.desc_label.setProperty("plugin-description", True)
        info_layout.addWidget(self.desc_label)
        
        layout.addLayout(info_layout, 1)
        
        # 載入狀態區域
        status_layout = QHBoxLayout()
        status_layout.setSpacing(8)
        
        # 載入旋轉器
        self.spinner = LoadingSpinner(24)
        status_layout.addWidget(self.spinner)
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready")
        status_layout.addWidget(self.status_indicator)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def setup_animations(self):
        """設置動畫"""
        # 淡入動畫
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 滑入動畫
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(400)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def start_loading(self):
        """開始載入動畫"""
        if not self.is_loading:
            self.is_loading = True
            self.is_complete = False
            
            self.spinner.start_spinning()
            self.status_indicator.set_status("processing", "載入中...")
            self.setProperty("loading", True)
            self.style().unpolish(self)
            self.style().polish(self)
            
            logger.debug(f"Started loading animation for plugin: {self.plugin_name}")
    
    def complete_loading(self, success: bool = True, message: str = ""):
        """完成載入"""
        if self.is_loading:
            self.is_loading = False
            self.is_complete = True
            
            self.spinner.stop_spinning()
            
            if success:
                self.status_indicator.set_status("success", message or "載入成功")
                self.setProperty("success", True)
            else:
                self.status_indicator.set_status("error", message or "載入失敗")
                self.setProperty("error", True)
            
            self.setProperty("loading", False)
            self.style().unpolish(self)
            self.style().polish(self)
            
            logger.debug(f"Completed loading for plugin: {self.plugin_name}, success: {success}")
    
    def show_with_animation(self):
        """帶動畫顯示卡片"""
        # 設置初始狀態
        self.setWindowOpacity(0.0)
        self.show()
        
        # 淡入動畫
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()


class PluginLoadingWorker(QThread):
    """插件載入工作線程"""
    
    plugin_loading_started = pyqtSignal(str)  # 插件名稱
    plugin_loading_progress = pyqtSignal(str, int, str)  # 插件名稱, 進度, 訊息
    plugin_loading_completed = pyqtSignal(str, bool, str)  # 插件名稱, 成功, 訊息
    all_plugins_loaded = pyqtSignal(bool, str)  # 成功, 訊息
    
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.should_stop = False
    
    def run(self):
        """執行插件載入"""
        try:
            logger.info("Plugin loading worker started")
            
            # 在工作線程中，只做插件發現和驗證，不創建 UI
            # 初始化插件管理器（僅發現和註冊插件，不創建視圖）
            self.plugin_manager.discover_plugins()
            
            # 獲取所有已註冊的插件
            available_plugins = self.plugin_manager.get_all_plugins()
            
            if not available_plugins:
                self.all_plugins_loaded.emit(False, "沒有找到可用的插件")
                return
            
            total_plugins = len(available_plugins)
            
            for index, (plugin_name, plugin) in enumerate(available_plugins.items()):
                if self.should_stop:
                    break
                
                self.plugin_loading_started.emit(plugin_name)
                
                try:
                    # 在工作線程中進行的階段（不涉及 UI 創建）
                    stages = [
                        (20, "檢查依賴..."),
                        (40, "驗證工具可用性..."),
                        (60, "初始化插件..."),
                        (80, "註冊插件..."),
                        (100, "完成")
                    ]
                    
                    for progress, message in stages:
                        if self.should_stop:
                            break
                            
                        self.plugin_loading_progress.emit(plugin_name, progress, message)
                        
                        # 在特定階段執行實際的檢查
                        if progress == 20:
                            # 檢查工具依賴
                            if not plugin.check_tools_availability():
                                self.plugin_loading_completed.emit(plugin_name, False, "所需工具不可用")
                                break
                        elif progress == 60:
                            # 初始化插件（不創建 UI）
                            if not plugin.initialize():
                                self.plugin_loading_completed.emit(plugin_name, False, "初始化失敗")
                                break
                        
                        self.msleep(200)  # 模擬處理時間
                    
                    if not self.should_stop:
                        # 檢查插件是否可用
                        if plugin.is_available():
                            self.plugin_loading_completed.emit(plugin_name, True, "驗證成功")
                        else:
                            self.plugin_loading_completed.emit(plugin_name, False, "插件不可用")
                
                except Exception as e:
                    logger.error(f"Error loading plugin {plugin_name}: {e}")
                    self.plugin_loading_completed.emit(plugin_name, False, f"錯誤: {str(e)}")
            
            if not self.should_stop:
                # 統計成功驗證的插件數量
                verified_plugins = [name for name, plugin in available_plugins.items() 
                                  if plugin.is_available()]
                verified_count = len(verified_plugins)
                self.all_plugins_loaded.emit(
                    verified_count > 0, 
                    f"成功驗證 {verified_count}/{total_plugins} 個插件"
                )
            
        except Exception as e:
            logger.error(f"Plugin loading worker error: {e}")
            self.all_plugins_loaded.emit(False, f"載入失敗: {str(e)}")
    
    def stop(self):
        """停止載入"""
        self.should_stop = True


class PluginLoadingDialog(QWidget):
    """插件載入對話框"""
    
    loading_completed = pyqtSignal(bool, str)  # 成功, 訊息
    
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.plugin_cards: Dict[str, PluginLoadingCard] = {}
        self.loading_worker = None
        
        self.setup_ui()
        self.setup_worker()
    
    def setup_ui(self):
        """設置 UI"""
        self.setWindowTitle("載入插件")
        self.setFixedSize(500, 400)
        self.setProperty("loading-dialog", True)
        
        # 設置為模態窗口
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 標題區域
        header_layout = QHBoxLayout()
        
        title_label = QLabel("載入插件")
        title_label.setProperty("dialog-title", True)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 整體進度指示器
        self.overall_progress = ProgressIndicator(show_percentage=True, show_text=True)
        header_layout.addWidget(self.overall_progress)
        
        main_layout.addLayout(header_layout)
        
        # 插件卡片滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setProperty("plugin-scroll", True)
        
        # 卡片容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_container.setLayout(self.cards_layout)
        
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area, 1)
        
        # 狀態區域
        status_layout = QHBoxLayout()
        
        self.status_indicator = StatusIndicator("ready")
        status_layout.addWidget(self.status_indicator)
        
        status_layout.addStretch()
        
        # 取消/完成按鈕
        self.action_button = ModernButton("取消")
        self.action_button.clicked.connect(self.on_action_button_clicked)
        status_layout.addWidget(self.action_button)
        
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
    
    def setup_worker(self):
        """設置工作線程"""
        self.loading_worker = PluginLoadingWorker(self.plugin_manager)
        self.loading_worker.plugin_loading_started.connect(self.on_plugin_loading_started)
        self.loading_worker.plugin_loading_progress.connect(self.on_plugin_loading_progress)
        self.loading_worker.plugin_loading_completed.connect(self.on_plugin_loading_completed)
        self.loading_worker.all_plugins_loaded.connect(self.on_all_plugins_loaded)
    
    def start_loading(self):
        """開始載入插件"""
        logger.info("Starting plugin loading dialog")
        
        # 預先創建插件卡片
        self.create_plugin_cards()
        
        # 重置狀態
        self.overall_progress.reset()
        self.status_indicator.set_status("processing", "準備載入插件...")
        self.action_button.setText("取消")
        
        # 啟動工作線程
        self.loading_worker.start()
        
        # 顯示對話框
        self.show()
        self.raise_()
        self.activateWindow()
    
    def create_plugin_cards(self):
        """創建插件卡片"""
        # 清理現有卡片
        for card in self.plugin_cards.values():
            card.deleteLater()
        self.plugin_cards.clear()
        
        # 獲取可用插件信息
        try:
            # 這裡我們需要在不初始化的情況下獲取插件信息
            # 先創建基本的插件卡片
            plugin_info = [
                ("fd", "快速檔案和目錄搜尋工具"),
                ("pandoc", "萬能文檔轉換器，支援 50+ 種格式"),
                ("poppler", "PDF 處理工具集"),
            ]
            
            for plugin_name, description in plugin_info:
                card = PluginLoadingCard(plugin_name, description)
                self.plugin_cards[plugin_name] = card
                self.cards_layout.addWidget(card)
                
                # 添加顯示動畫延遲
                QTimer.singleShot(len(self.plugin_cards) * 100, card.show_with_animation)
            
            # 添加伸縮空間
            self.cards_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error creating plugin cards: {e}")
    
    def on_plugin_loading_started(self, plugin_name: str):
        """處理插件載入開始"""
        if plugin_name in self.plugin_cards:
            self.plugin_cards[plugin_name].start_loading()
        
        self.status_indicator.set_status("processing", f"載入 {plugin_name}...")
    
    def on_plugin_loading_progress(self, plugin_name: str, progress: int, message: str):
        """處理插件載入進度"""
        # 這裡可以添加更詳細的進度反饋
        pass
    
    def on_plugin_loading_completed(self, plugin_name: str, success: bool, message: str):
        """處理插件載入完成"""
        if plugin_name in self.plugin_cards:
            self.plugin_cards[plugin_name].complete_loading(success, message)
        
        # 更新整體進度
        completed_count = sum(1 for card in self.plugin_cards.values() if card.is_complete)
        total_count = len(self.plugin_cards)
        overall_progress = int((completed_count / total_count) * 100) if total_count > 0 else 0
        
        self.overall_progress.set_progress(
            overall_progress, 
            f"已完成 {completed_count}/{total_count} 個插件"
        )
    
    def on_all_plugins_loaded(self, success: bool, message: str):
        """處理所有插件載入完成"""
        if success:
            self.status_indicator.set_status("success", message)
            self.overall_progress.complete("載入完成")
            self.action_button.setText("完成")
        else:
            self.status_indicator.set_status("error", message)
            self.action_button.setText("關閉")
        
        # 延遲一段時間後自動關閉
        QTimer.singleShot(2000, self.auto_close)
    
    def auto_close(self):
        """自動關閉對話框"""
        self.loading_completed.emit(True, "插件載入完成")
        self.accept()
    
    def on_action_button_clicked(self):
        """處理動作按鈕點擊"""
        if self.action_button.text() == "取消":
            # 停止載入
            if self.loading_worker and self.loading_worker.isRunning():
                self.loading_worker.stop()
                self.loading_worker.wait()
            
            self.status_indicator.set_status("warning", "載入已取消")
            self.loading_completed.emit(False, "載入已取消")
            self.reject()
        else:
            # 完成或關閉
            self.loading_completed.emit(True, "插件載入完成")
            self.accept()
    
    def accept(self):
        """接受對話框"""
        self.close()
    
    def reject(self):
        """拒絕對話框"""
        self.close()
    
    def closeEvent(self, event):
        """關閉事件"""
        if self.loading_worker and self.loading_worker.isRunning():
            self.loading_worker.stop()
            self.loading_worker.wait()
        
        super().closeEvent(event)


# 便利函數
def show_plugin_loading_dialog(plugin_manager, parent=None) -> bool:
    """顯示插件載入對話框"""
    dialog = PluginLoadingDialog(plugin_manager, parent)
    
    result = [False]  # 使用列表來在回調中修改值
    
    def on_completed(success, message):
        result[0] = success
        logger.info(f"Plugin loading completed: {success}, {message}")
    
    dialog.loading_completed.connect(on_completed)
    dialog.start_loading()
    
    # 等待對話框關閉
    while dialog.isVisible():
        QApplication.processEvents()
        time.sleep(0.01)
    
    return result[0]