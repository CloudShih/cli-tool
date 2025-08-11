"""
dust 工具插件實現
將 dust 磁碟空間分析工具包裝為插件
"""

import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import QWidget
from core.plugin_manager import PluginInterface
from .dust_model import DustModel
from .dust_view_redesigned import DustViewRedesigned
from .dust_controller import DustController

logger = logging.getLogger(__name__)


class DustPlugin(PluginInterface):
    """dust 磁碟空間分析工具插件"""
    
    def __init__(self):
        super().__init__()
        self._model = None
        self._view = None
        self._controller = None
        self._initialized = False
        
        logger.info("DustPlugin initialized")
    
    @property
    def name(self) -> str:
        """插件名稱"""
        return "dust"
    
    @property
    def description(self) -> str:
        """插件描述"""
        return "使用 dust 工具提供磁碟空間分析功能，支援目錄大小視覺化和詳細檔案統計"
    
    @property
    def version(self) -> str:
        """插件版本"""
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        """所需的外部工具列表"""
        return ["dust"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            if self._initialized:
                logger.warning("DustPlugin already initialized")
                return True
            
            # 創建 MVC 組件
            self._model = self.create_model()
            self._view = self.create_view()
            self._controller = self.create_controller(self._model, self._view)
            
            self._initialized = True
            logger.info("DustPlugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DustPlugin: {e}")
            return False
    
    def create_view(self):
        """創建插件的 GUI 視圖"""
        return DustViewRedesigned()
    
    def create_model(self):
        """創建插件的數據模型"""
        return DustModel()
    
    def create_controller(self, model, view):
        """創建插件的控制器"""
        return DustController(view, model)
    
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
            
            logger.info("DustPlugin cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during DustPlugin cleanup: {e}")
    
    def check_tools_availability(self) -> bool:
        """檢查所需工具是否可用"""
        try:
            # 創建臨時模型實例進行檢查
            temp_model = DustModel()
            available, _, _ = temp_model.check_dust_availability()
            return available
        except Exception as e:
            logger.error(f"Error checking dust tool availability: {e}")
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
        return "磁碟空間分析器"
    
    def get_author(self) -> str:
        """獲取插件作者"""
        return "CLI Tool Developer"
    
    def get_icon_path(self) -> Optional[str]:
        """獲取插件圖標路徑"""
        return None
    
    def get_supported_operations(self) -> List[str]:
        """獲取支援的操作類型"""
        return [
            "disk_usage_analysis", "directory_size", "file_statistics",
            "space_visualization", "tree_view", "detailed_report"
        ]
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """獲取配置模式"""
        return {
            "executable_path": {
                "type": "string",
                "default": "dust",
                "description": "dust 執行檔路徑"
            },
            "default_depth": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 10,
                "description": "預設掃描深度"
            },
            "default_limit": {
                "type": "integer",
                "default": 30,
                "minimum": 5,
                "maximum": 1000,
                "description": "預設顯示項目數量限制"
            },
            "show_full_paths": {
                "type": "boolean",
                "default": False,
                "description": "顯示完整路徑"
            },
            "files_only": {
                "type": "boolean",
                "default": False,
                "description": "只顯示檔案（不含目錄）"
            },
            "apparent_size": {
                "type": "boolean",
                "default": True,
                "description": "使用檔案實際大小而非磁碟佔用空間"
            },
            "output_format": {
                "type": "string",
                "default": "terminal",
                "enum": ["terminal", "json", "csv"],
                "description": "輸出格式"
            },
            "color_scheme": {
                "type": "string",
                "default": "auto",
                "enum": ["auto", "always", "never"],
                "description": "顏色方案"
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
            "recent_directories": {
                "type": "array",
                "default": [],
                "description": "最近分析的目錄列表"
            }
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """獲取插件設定"""
        if not self.is_initialized():
            return {}
        
        try:
            # 從 View 獲取當前設定
            return {
                "max_depth": self._view.dust_max_depth_input.value() if self._view else 3,
                "number_of_lines": self._view.dust_lines_input.value() if self._view else 50,
                "sort_reverse": self._view.dust_reverse_sort_checkbox.isChecked() if self._view else True,
                "apparent_size": self._view.dust_apparent_size_checkbox.isChecked() if self._view else False,
                "min_size": self._view.dust_min_size_input.text() if self._view else "",
                "target_path": self._view.dust_target_path_input.text() if self._view else "",
                "include_types": self._view.dust_include_types_input.text() if self._view else "",
                "exclude_patterns": self._view.dust_exclude_patterns_input.text() if self._view else ""
            }
        except Exception as e:
            logger.error(f"Error getting dust settings: {e}")
            return {}
    
    def apply_settings(self, settings: Dict[str, Any]):
        """應用插件設定"""
        if not self.is_initialized():
            return
        
        try:
            if not self._view:
                return
            
            # 應用深度設定
            max_depth = settings.get("max_depth", 3)
            self._view.dust_max_depth_input.setValue(max_depth)
            
            # 應用顯示行數設定
            number_of_lines = settings.get("number_of_lines", 50)
            self._view.dust_lines_input.setValue(number_of_lines)
            
            # 應用排序設定
            sort_reverse = settings.get("sort_reverse", True)
            self._view.dust_reverse_sort_checkbox.setChecked(sort_reverse)
            
            # 應用表面大小設定
            apparent_size = settings.get("apparent_size", False)
            self._view.dust_apparent_size_checkbox.setChecked(apparent_size)
            
            # 應用最小大小設定
            min_size = settings.get("min_size", "")
            self._view.dust_min_size_input.setText(min_size)
            
            # 應用目標路徑設定
            target_path = settings.get("target_path", "")
            self._view.dust_path_input.setText(target_path)
            
            # 應用包含類型設定
            include_types = settings.get("include_types", "")
            self._view.dust_include_types_input.setText(include_types)
            
            # 應用排除模式設定
            exclude_patterns = settings.get("exclude_patterns", "")
            self._view.dust_exclude_patterns_input.setText(exclude_patterns)
            
            logger.info("Dust settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error applying dust settings: {e}")
    
    def handle_directory_analysis(self, directory_path: str) -> bool:
        """處理目錄分析請求"""
        try:
            if not self.is_initialized():
                if not self.initialize():
                    return False
            
            # 設定分析目錄
            self._view.dust_target_path_input.setText(directory_path)
            
            logger.info(f"Directory analysis started in dust plugin: {directory_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling directory analysis in dust plugin: {e}")
            return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """獲取插件狀態信息"""
        try:
            status_info = {
                "initialized": self.is_initialized(),
                "tool_available": self.check_tools_availability(),
                "current_directory": "",
                "cache_info": {}
            }
            
            if self.is_initialized() and self._view:
                status_info["current_directory"] = self._view.dust_target_path_input.text()
                
            if self.is_initialized() and self._model:
                status_info["cache_info"] = self._model.get_cache_info()
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting dust status info: {e}")
            return {"error": str(e)}
    
    def execute_command(self, command: str, args: Dict[str, Any] = None) -> Any:
        """執行插件命令"""
        if not self.is_initialized():
            return {"error": "Plugin not initialized"}
        
        args = args or {}
        
        try:
            if command == "analyze":
                # 觸發分析
                directory = args.get("directory", "")
                if directory:
                    self._view.dust_target_path_input.setText(directory)
                # 透過控制器執行分析
                self._controller._execute_analysis()
                return {"status": "analysis_started"}
                
            elif command == "check_tool":
                # 檢查工具可用性
                available, version, error = self._model.check_dust_availability()
                return {
                    "status": "tool_checked",
                    "available": available,
                    "version": version,
                    "error": error
                }
                
            elif command == "clear_cache":
                # 清除結果顯示
                self._view.dust_results_display.clear_results()
                return {"status": "cache_clear_started"}
                
            elif command == "set_depth":
                # 設定掃描深度
                depth = args.get("depth", 3)
                self._view.dust_max_depth_input.setValue(depth)
                return {"status": f"depth_set_to_{depth}"}
                
            elif command == "set_limit":
                # 設定顯示行數限制
                limit = args.get("limit", 50)
                self._view.dust_lines_input.setValue(limit)
                return {"status": f"limit_set_to_{limit}"}
                
            elif command == "analyze_directory":
                # 分析指定目錄
                directory_path = args.get("directory_path", "")
                if directory_path:
                    self._view.dust_target_path_input.setText(directory_path)
                    return {"status": f"directory_set", "directory_path": directory_path}
                else:
                    return {"error": "No directory path provided"}
                    
            else:
                return {"error": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error(f"Error executing dust command '{command}': {e}")
            return {"error": str(e)}


def create_plugin() -> PluginInterface:
    """創建 dust 插件實例"""
    return DustPlugin()