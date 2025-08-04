"""
Glow Markdown 閱讀器插件實現
實現 PluginInterface 接口，整合到 CLI 工具系統
"""

import logging
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QWidget
from core.plugin_manager import PluginInterface
from .glow_model import GlowModel
from .glow_view import GlowView
from .glow_controller import GlowController

logger = logging.getLogger(__name__)


class GlowPlugin(PluginInterface):
    """Glow Markdown 閱讀器插件"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._view = None
        self._controller = None
        self._widget = None
        
        logger.info("GlowPlugin initialized")
    
    def get_name(self) -> str:
        """獲取插件名稱"""
        return "glow"
    
    def get_display_name(self) -> str:
        """獲取插件顯示名稱"""
        return "Markdown 閱讀器"
    
    def get_description(self) -> str:
        """獲取插件描述"""
        return "使用 Glow 工具提供美觀的 Markdown 文檔預覽功能，支援本地檔案和遠程 URL"
    
    def get_version(self) -> str:
        """獲取插件版本"""
        return "1.0.0"
    
    def get_author(self) -> str:
        """獲取插件作者"""
        return "CLI Tool Developer"
    
    def get_icon_path(self) -> Optional[str]:
        """獲取插件圖標路徑"""
        # 返回 None 使用預設圖標，或者提供自訂圖標路徑
        return None
    
    def get_required_tools(self) -> Dict[str, str]:
        """獲取插件所需的外部工具"""
        return {
            "glow": "Glow CLI markdown reader - https://github.com/charmbracelet/glow"
        }
    
    def get_supported_file_types(self) -> list:
        """獲取支援的檔案類型"""
        return [
            ".md",        # Markdown
            ".markdown",  # Markdown 完整擴展名
            ".mdown",     # Markdown 簡化擴展名
            ".mkd",       # Markdown 短擴展名
            ".txt"        # 純文字檔案
        ]
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """獲取配置模式"""
        return {
            "executable_path": {
                "type": "string",
                "default": "glow",
                "description": "Glow 執行檔路徑"
            },
            "default_theme": {
                "type": "string",
                "default": "auto",
                "enum": ["auto", "dark", "light", "pink", "dracula", "notty"],
                "description": "預設主題樣式"
            },
            "default_width": {
                "type": "integer",
                "default": 120,
                "minimum": 60,
                "maximum": 200,
                "description": "預設顯示寬度（字符數）"
            },
            "use_cache": {
                "type": "boolean",
                "default": True,
                "description": "是否使用快取功能"
            },
            "cache_ttl": {
                "type": "integer",
                "default": 3600,
                "minimum": 300,
                "maximum": 86400,
                "description": "快取存留時間（秒）"
            },
            "max_cache_size": {
                "type": "integer",
                "default": 104857600,
                "minimum": 10485760,
                "maximum": 1073741824,
                "description": "最大快取大小（位元組）"
            },
            "recent_files": {
                "type": "array",
                "default": [],
                "description": "最近使用的檔案列表"
            }
        }
    
    def is_available(self) -> bool:
        """檢查插件是否可用"""
        try:
            # 檢查必需的工具是否可用
            return self.check_tools_availability()
        except Exception as e:
            logger.error(f"Error checking Glow plugin availability: {e}")
            return False
    
    def check_tools_availability(self) -> bool:
        """檢查所需工具是否可用 - PluginInterface 要求的方法"""
        try:
            # 創建臨時模型實例進行檢查
            temp_model = GlowModel()
            available, _, _ = temp_model.check_glow_availability()
            return available
        except Exception as e:
            logger.error(f"Error checking Glow tool availability: {e}")
            return False
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            if self._model is not None:
                logger.warning("GlowPlugin already initialized")
                return True
            
            # 創建 MVC 組件
            self._model = GlowModel()
            self._view = GlowView()
            self._controller = GlowController(self._view, self._model)
            
            # 創建主 widget
            self._widget = self._view
            
            logger.info("GlowPlugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GlowPlugin: {e}")
            return False
    
    def get_widget(self) -> Optional[QWidget]:
        """獲取插件的主 widget"""
        if not self.is_initialized():
            if not self.initialize():
                return None
        
        return self._widget
    
    def is_initialized(self) -> bool:
        """檢查插件是否已初始化"""
        return (self._model is not None and 
                self._view is not None and 
                self._controller is not None and 
                self._widget is not None)
    
    def cleanup(self):
        """清理插件資源"""
        try:
            if self._controller:
                self._controller.cleanup()
            
            # 重置組件
            self._controller = None
            self._widget = None
            self._view = None
            self._model = None
            
            logger.info("GlowPlugin cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during GlowPlugin cleanup: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        """獲取插件設定"""
        if not self.is_initialized():
            return {}
        
        try:
            # 從 View 獲取當前設定
            return {
                "theme": self._view.theme_combo.currentData() if self._view else "auto",
                "width": self._view.width_slider.value() if self._view else 120,
                "use_cache": self._view.use_cache_check.isChecked() if self._view else True,
                "recent_files": self._view.recent_files if self._view else []
            }
        except Exception as e:
            logger.error(f"Error getting Glow settings: {e}")
            return {}
    
    def apply_settings(self, settings: Dict[str, Any]):
        """應用插件設定"""
        if not self.is_initialized():
            return
        
        try:
            if not self._view:
                return
            
            # 應用主題設定
            theme = settings.get("theme", "auto")
            self._view._set_theme_selection(theme)
            
            # 應用寬度設定
            width = settings.get("width", 120)
            self._view.width_slider.setValue(width)
            
            # 應用快取設定
            use_cache = settings.get("use_cache", True)
            self._view.use_cache_check.setChecked(use_cache)
            
            # 應用最近檔案設定
            recent_files = settings.get("recent_files", [])
            if isinstance(recent_files, list):
                self._view.recent_files = recent_files
                self._view._update_recent_files_combo()
            
            logger.info("Glow settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying Glow settings: {e}")
    
    def handle_file_open(self, file_path: str) -> bool:
        """處理檔案開啟請求"""
        try:
            if not self.is_initialized():
                if not self.initialize():
                    return False
            
            # 檢查檔案類型是否支援
            supported_types = self.get_supported_file_types()
            if not any(file_path.lower().endswith(ext) for ext in supported_types):
                logger.warning(f"Unsupported file type: {file_path}")
                return False
            
            # 設定檔案路徑
            self._view._set_file_path(file_path)
            
            # 切換到檔案標籤頁
            self._view.source_tabs.setCurrentIndex(0)
            
            logger.info(f"File opened in Glow plugin: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling file open in Glow plugin: {e}")
            return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """獲取插件狀態信息"""
        try:
            status_info = {
                "initialized": self.is_initialized(),
                "tool_available": self.check_tools_availability(),
                "current_source": "",
                "cache_info": {}
            }
            
            if self.is_initialized() and self._view:
                status_info["current_source"] = self._view.current_source
                
            if self.is_initialized() and self._model:
                status_info["cache_info"] = self._model.get_cache_info()
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting Glow status info: {e}")
            return {"error": str(e)}
    
    def execute_command(self, command: str, args: Dict[str, Any] = None) -> Any:
        """執行插件命令"""
        if not self.is_initialized():
            return {"error": "Plugin not initialized"}
        
        args = args or {}
        
        try:
            if command == "render":
                # 觸發渲染
                self._view._request_render()
                return {"status": "render_started"}
                
            elif command == "check_tool":
                # 檢查工具
                self._view.check_glow_requested.emit()
                return {"status": "check_started"}
                
            elif command == "clear_cache":
                # 清除快取
                self._view.clear_cache_requested.emit()
                return {"status": "cache_clear_started"}
                
            elif command == "set_theme":
                # 設定主題
                theme = args.get("theme", "auto")
                self._view._set_theme_selection(theme)
                return {"status": f"theme_set_to_{theme}"}
                
            elif command == "open_url":
                # 開啟 URL
                url = args.get("url", "")
                if url:
                    self._view.url_input.setText(url)
                    self._view.source_tabs.setCurrentIndex(1)  # 切換到 URL 標籤頁
                    return {"status": f"url_set", "url": url}
                else:
                    return {"error": "No URL provided"}
                    
            else:
                return {"error": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error(f"Error executing Glow command '{command}': {e}")
            return {"error": str(e)}


# 插件工廠函式
def create_plugin() -> PluginInterface:
    """創建 Glow 插件實例"""
    return GlowPlugin()