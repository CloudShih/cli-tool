"""
Bat 語法高亮顯示插件實現
實現 PluginInterface 接口，整合到 CLI 工具系統
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import QWidget
from core.plugin_manager import PluginInterface
from .bat_model import BatModel
from .bat_view import BatView
from .bat_controller import BatController

logger = logging.getLogger(__name__)


class BatPlugin(PluginInterface):
    """Bat 語法高亮顯示插件"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._view = None
        self._controller = None
        self._initialized = False
        
        logger.info("BatPlugin initialized")
    
    @property
    def name(self) -> str:
        """插件名稱"""
        return "bat"
    
    @property 
    def description(self) -> str:
        """插件描述"""
        return "使用 bat 工具提供語法高亮的文件查看功能，支援多種程式語言和主題樣式"
    
    @property
    def version(self) -> str:
        """插件版本"""
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        """所需的外部工具列表"""
        return ["bat"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            if self._initialized:
                logger.warning("BatPlugin already initialized")
                return True
            
            # 創建 MVC 組件
            self._model = self.create_model()
            self._view = self.create_view()
            self._controller = self.create_controller(self._model, self._view)
            
            self._initialized = True
            logger.info("BatPlugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize BatPlugin: {e}")
            return False
    
    def create_view(self):
        """創建插件的 GUI 視圖"""
        return BatView()
    
    def create_model(self):
        """創建插件的數據模型"""
        return BatModel()
    
    def create_controller(self, model, view):
        """創建插件的控制器"""
        return BatController(view, model)
    
    def cleanup(self):
        """清理插件資源"""
        try:
            if self._controller:
                self._controller.cleanup()
            
            # 重置組件
            self._controller = None
            self._view = None
            self._model = None
            self._initialized = False
            
            logger.info("BatPlugin cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during BatPlugin cleanup: {e}")
    
    def check_tools_availability(self) -> bool:
        """檢查所需工具是否可用"""
        try:
            # 創建臨時模型實例進行檢查
            temp_model = BatModel()
            available, _, _ = temp_model.check_bat_availability()
            return available
        except Exception as e:
            logger.error(f"Error checking bat tool availability: {e}")
            return False
    
    def get_widget(self) -> Optional[QWidget]:
        """獲取插件的主 widget"""
        if not self._initialized:
            if not self.initialize():
                return None
        
        return self._view
    
    def is_initialized(self) -> bool:
        """檢查插件是否已初始化"""
        return self._initialized
    
    def get_display_name(self) -> str:
        """獲取插件顯示名稱"""
        return "語法高亮查看器"
    
    def get_author(self) -> str:
        """獲取插件作者"""
        return "CLI Tool Developer"
    
    def get_icon_path(self) -> Optional[str]:
        """獲取插件圖標路徑"""
        return None
    
    def get_supported_file_types(self) -> List[str]:
        """獲取支援的檔案類型"""
        return [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".sass",
            ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg",
            ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
            ".java", ".kt", ".scala", ".go", ".rs", ".rb", ".php",
            ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
            ".sql", ".r", ".R", ".m", ".swift", ".dart", ".lua",
            ".md", ".markdown", ".txt", ".log", ".conf", ".config"
        ]
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """獲取配置模式"""
        return {
            "executable_path": {
                "type": "string",
                "default": "bat",
                "description": "bat 執行檔路徑"
            },
            "default_theme": {
                "type": "string", 
                "default": "Monokai Extended",
                "enum": [
                    "1337", "Coldark-Cold", "Coldark-Dark", "DarkNeon", 
                    "Dracula", "GitHub", "Monokai Extended", "Monokai Extended Bright",
                    "Monokai Extended Light", "Monokai Extended Origin", "Nord",
                    "OneHalfDark", "OneHalfLight", "Solarized (dark)", "Solarized (light)",
                    "Sublime Snazzy", "Visual Studio Dark+", "ansi", "base16", "gruvbox-dark"
                ],
                "description": "預設主題樣式"
            },
            "show_line_numbers": {
                "type": "boolean",
                "default": True,
                "description": "顯示行號"
            },
            "show_git_modifications": {
                "type": "boolean",
                "default": True,
                "description": "顯示 Git 修改標記"
            },
            "tab_width": {
                "type": "integer",
                "default": 4,
                "minimum": 1,
                "maximum": 16,
                "description": "Tab 寬度（空格數）"
            },
            "wrap_text": {
                "type": "boolean",
                "default": False,
                "description": "自動換行"
            },
            "use_cache": {
                "type": "boolean",
                "default": True,
                "description": "是否使用快取功能"
            },
            "cache_ttl": {
                "type": "integer",
                "default": 1800,
                "minimum": 300,
                "maximum": 86400,
                "description": "快取存留時間（秒）"
            },
            "max_cache_size": {
                "type": "integer",
                "default": 52428800,
                "minimum": 10485760,
                "maximum": 536870912,
                "description": "最大快取大小（位元組）"
            },
            "recent_files": {
                "type": "array",
                "default": [],
                "description": "最近使用的檔案列表"
            }
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """獲取插件設定"""
        if not self.is_initialized():
            return {}
        
        try:
            # 從 View 獲取當前設定
            return {
                "theme": self._view.theme_combo.currentData() if self._view else "Monokai Extended",
                "show_line_numbers": self._view.line_numbers_check.isChecked() if self._view else True,
                "show_git_modifications": self._view.git_modifications_check.isChecked() if self._view else True,
                "tab_width": self._view.tab_width_spin.value() if self._view else 4,
                "wrap_text": self._view.wrap_text_check.isChecked() if self._view else False,
                "use_cache": self._view.use_cache_check.isChecked() if self._view else True,
                "recent_files": self._view.recent_files if self._view else []
            }
        except Exception as e:
            logger.error(f"Error getting bat settings: {e}")
            return {}
    
    def apply_settings(self, settings: Dict[str, Any]):
        """應用插件設定"""
        if not self.is_initialized():
            return
        
        try:
            if not self._view:
                return
            
            # 應用主題設定
            theme = settings.get("theme", "Monokai Extended")
            self._view._set_theme_selection(theme)
            
            # 應用顯示設定
            show_line_numbers = settings.get("show_line_numbers", True)
            self._view.line_numbers_check.setChecked(show_line_numbers)
            
            show_git_modifications = settings.get("show_git_modifications", True)
            self._view.git_modifications_check.setChecked(show_git_modifications)
            
            tab_width = settings.get("tab_width", 4)
            self._view.tab_width_spin.setValue(tab_width)
            
            wrap_text = settings.get("wrap_text", False)
            self._view.wrap_text_check.setChecked(wrap_text)
            
            # 應用快取設定
            use_cache = settings.get("use_cache", True)
            self._view.use_cache_check.setChecked(use_cache)
            
            # 應用最近檔案設定
            recent_files = settings.get("recent_files", [])
            if isinstance(recent_files, list):
                self._view.recent_files = recent_files
                self._view._update_recent_files_combo()
            
            logger.info("Bat settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying bat settings: {e}")
    
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
            
            logger.info(f"File opened in bat plugin: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling file open in bat plugin: {e}")
            return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """獲取插件狀態信息"""
        try:
            status_info = {
                "initialized": self.is_initialized(),
                "tool_available": self.check_tools_availability(),
                "current_file": "",
                "cache_info": {}
            }
            
            if self.is_initialized() and self._view:
                status_info["current_file"] = getattr(self._view, 'current_file', '')
                
            if self.is_initialized() and self._model:
                status_info["cache_info"] = self._model.get_cache_info()
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting bat status info: {e}")
            return {"error": str(e)}
    
    def execute_command(self, command: str, args: Dict[str, Any] = None) -> Any:
        """執行插件命令"""
        if not self.is_initialized():
            return {"error": "Plugin not initialized"}
        
        args = args or {}
        
        try:
            if command == "highlight":
                # 觸發語法高亮
                self._view._request_highlight()
                return {"status": "highlight_started"}
                
            elif command == "check_tool":
                # 檢查工具
                self._view.check_bat_requested.emit()
                return {"status": "check_started"}
                
            elif command == "clear_cache":
                # 清除快取
                self._view.clear_cache_requested.emit()
                return {"status": "cache_clear_started"}
                
            elif command == "set_theme":
                # 設定主題
                theme = args.get("theme", "Monokai Extended")
                self._view._set_theme_selection(theme)
                return {"status": f"theme_set_to_{theme}"}
                
            elif command == "open_file":
                # 開啟檔案
                file_path = args.get("file_path", "")
                if file_path:
                    self._view._set_file_path(file_path)
                    return {"status": f"file_opened", "file_path": file_path}
                else:
                    return {"error": "No file path provided"}
                    
            else:
                return {"error": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error(f"Error executing bat command '{command}': {e}")
            return {"error": str(e)}


# 插件工廠函式
def create_plugin() -> PluginInterface:
    """創建 bat 插件實例"""
    return BatPlugin()