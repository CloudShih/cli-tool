"""
Pandoc 文檔轉換工具插件實現
支援 50+ 種文檔格式互相轉換的萬能文檔轉換器
"""

import logging
import subprocess
from typing import List
from core.plugin_manager import PluginInterface
from tools.pandoc.pandoc_model import PandocModel
from tools.pandoc.pandoc_view import PandocView
from tools.pandoc.pandoc_controller import PandocController

logger = logging.getLogger(__name__)


class PandocPlugin(PluginInterface):
    """Pandoc 文檔轉換工具插件"""
    
    @property
    def name(self) -> str:
        return "pandoc"
    
    @property
    def description(self) -> str:
        return "Universal document converter supporting 50+ formats (Markdown, HTML, PDF, DOCX, EPUB, etc.)"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["pandoc"]  # 需要 pandoc 命令行工具
    
    def initialize(self) -> bool:
        """初始化 Pandoc 插件"""
        try:
            logger.info("Initializing pandoc plugin...")
            
            # 檢查 pandoc 工具可用性
            availability = self._check_pandoc_availability()
            if not availability:
                logger.warning("Pandoc tool not available, but plugin will still initialize")
                # 注意：即使 pandoc 不可用，我們仍然初始化插件
                # 這樣用戶可以看到安裝提示和幫助信息
            else:
                logger.info("Pandoc tool is available and ready")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize pandoc plugin: {e}")
            return False
    
    def _check_pandoc_availability(self) -> bool:
        """檢查 pandoc 工具是否可用"""
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False
    
    def create_view(self):
        """創建 Pandoc 插件的視圖"""
        return PandocView()
    
    def create_model(self):
        """創建 Pandoc 插件的模型"""
        return PandocModel()
    
    def create_controller(self, model, view):
        """創建 Pandoc 插件的控制器"""
        return PandocController(view, model)
    
    def cleanup(self):
        """清理 Pandoc 插件資源"""
        logger.info("Cleaning up pandoc plugin...")
        # 這裡可以進行插件特定的清理工作
        # 例如：停止背景線程、保存設定等


def create_plugin() -> PandocPlugin:
    """插件工廠函數"""
    return PandocPlugin()