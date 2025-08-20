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
from .dust_service import IDustAnalyzer, DustService

logger = logging.getLogger(__name__)


class DustPlugin(PluginInterface):
    """dust 磁碟空間分析工具插件"""

    def __init__(self, analyzer: Optional[IDustAnalyzer] = None):
        super().__init__()
        self._model: Optional[DustModel] = None
        self._view: Optional[DustViewRedesigned] = None
        self._controller: Optional[DustController] = None
        self._service: Optional[IDustAnalyzer] = analyzer
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
            self._model = DustModel()
            self._view = DustViewRedesigned()
            self._controller = DustController(self._view, self._model)

            # 綁定服務層
            if not self._service:
                self._service = DustService(self._model, self._view, self._controller)

            self._initialized = True
            logger.info("DustPlugin initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize DustPlugin: {e}")
            return False

    def cleanup(self):
        """清理插件資源"""
        try:
            if self._controller:
                self._controller.cleanup()

            self._controller = None
            self._view = None
            self._model = None
            self._service = None
            self._initialized = False

            logger.info("DustPlugin cleanup completed")

        except Exception as e:
            logger.error(f"Error during DustPlugin cleanup: {e}")

    def check_tools_availability(self) -> bool:
        """檢查所需工具是否可用"""
        try:
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
        if not self._service:
            return {}
        return self._service.get_configuration_schema()

    def get_settings(self) -> Dict[str, Any]:
        """獲取插件設定"""
        if not self.is_initialized() or not self._service:
            return {}
        return self._service.get_settings()

    def apply_settings(self, settings: Dict[str, Any]):
        """應用插件設定"""
        if self.is_initialized() and self._service:
            self._service.apply_settings(settings)

    def handle_directory_analysis(self, directory_path: str) -> bool:
        """處理目錄分析請求"""
        if not self.is_initialized():
            if not self.initialize():
                return False
        if not self._service:
            return False
        return self._service.handle_directory_analysis(directory_path)

    def get_status_info(self) -> Dict[str, Any]:
        """獲取插件狀態信息"""
        if self._service:
            info = self._service.get_status_info()
            info["initialized"] = self.is_initialized()
            return info
        return {"initialized": self.is_initialized()}

    def execute_command(self, command: str, args: Dict[str, Any] = None) -> Any:
        """執行插件命令"""
        if not self.is_initialized() or not self._service:
            return {"error": "Plugin not initialized"}
        return self._service.execute_command(command, args)


def create_plugin() -> PluginInterface:
    """創建 dust 插件實例"""
    return DustPlugin()
