"""
fd 工具插件實現
將 fd 文件搜尋工具包裝為插件
"""

import logging
from typing import List
from core.plugin_manager import PluginInterface
from tools.fd.fd_model import FdModel
from tools.fd.fd_view import FdView
from tools.fd.fd_controller import FdController

logger = logging.getLogger(__name__)


class FdPlugin(PluginInterface):
    """fd 文件搜尋工具插件"""
    
    @property
    def name(self) -> str:
        return "fd"
    
    @property
    def description(self) -> str:
        return "Fast file and directory search tool using fd command"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["fd"]  # 需要 fd 命令行工具
    
    def initialize(self) -> bool:
        """初始化 fd 插件"""
        try:
            logger.info("Initializing fd plugin...")
            # 這裡可以進行插件特定的初始化工作
            return True
        except Exception as e:
            logger.error(f"Failed to initialize fd plugin: {e}")
            return False
    
    def create_view(self):
        """創建 fd 插件的視圖"""
        return FdView()
    
    def create_model(self):
        """創建 fd 插件的模型"""
        return FdModel()
    
    def create_controller(self, model, view):
        """創建 fd 插件的控制器"""
        return FdController(view, model)
    
    def cleanup(self):
        """清理 fd 插件資源"""
        logger.info("Cleaning up fd plugin...")
        # 這裡可以進行插件特定的清理工作


def create_plugin() -> FdPlugin:
    """插件工廠函數"""
    return FdPlugin()