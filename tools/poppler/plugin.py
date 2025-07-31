"""
Poppler 工具插件實現
將 Poppler PDF 處理工具包裝為插件
"""

import logging
from typing import List
from core.plugin_manager import PluginInterface
from tools.poppler.poppler_model import PopplerModel
from tools.poppler.poppler_view import PopplerView
from tools.poppler.poppler_controller import PopplerController

logger = logging.getLogger(__name__)


class PopplerPlugin(PluginInterface):
    """Poppler PDF 處理工具插件"""
    
    @property
    def name(self) -> str:
        return "poppler"
    
    @property
    def description(self) -> str:
        return "PDF processing tools using Poppler utilities (pdfinfo, pdftotext, etc.)"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return [
            "pdfinfo",
            "pdftotext", 
            "pdfimages",
            "pdfseparate",
            "pdfunite",
            "pdftoppm",
            "pdftohtml",
            "qpdf"
        ]
    
    def check_tools_availability(self) -> bool:
        """
        覆寫工具可用性檢查
        對於 Poppler，我們只需要其中幾個核心工具即可正常運行
        """
        core_tools = ["pdfinfo", "pdftotext"]  # 核心工具
        optional_tools = ["pdfimages", "pdfseparate", "pdfunite", "pdftoppm", "pdftohtml", "qpdf"]
        
        # 檢查核心工具
        core_available = all(self._check_tool_availability(tool) for tool in core_tools)
        if not core_available:
            logger.warning(f"Core Poppler tools not available for plugin '{self.name}'")
            return False
        
        # 檢查可選工具並記錄
        for tool in optional_tools:
            if not self._check_tool_availability(tool):
                logger.info(f"Optional tool '{tool}' not available, some features may be disabled")
        
        return True
    
    def initialize(self) -> bool:
        """初始化 Poppler 插件"""
        try:
            logger.info("Initializing Poppler plugin...")
            # 這裡可以進行插件特定的初始化工作
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Poppler plugin: {e}")
            return False
    
    def create_view(self):
        """創建 Poppler 插件的視圖"""
        return PopplerView()
    
    def create_model(self):
        """創建 Poppler 插件的模型"""
        return PopplerModel()
    
    def create_controller(self, model, view):
        """創建 Poppler 插件的控制器"""
        return PopplerController(model, view)
    
    def cleanup(self):
        """清理 Poppler 插件資源"""
        logger.info("Cleaning up Poppler plugin...")
        # 這裡可以進行插件特定的清理工作


def create_plugin() -> PopplerPlugin:
    """插件工廠函數"""
    return PopplerPlugin()