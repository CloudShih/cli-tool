"""
Glances 插件入口
實現 PluginInterface 接口，提供系統監控工具的完整整合
"""

import logging
from typing import List
from core.plugin_manager import PluginInterface

logger = logging.getLogger(__name__)


class GlancesPlugin(PluginInterface):
    """Glances 系統監控工具插件"""
    
    def __init__(self):
        self._model = None
        self._view = None
        self._controller = None
        logger.info("GlancesPlugin initialized")
    
    @property
    def name(self) -> str:
        """插件名稱"""
        return "glances"
    
    @property
    def description(self) -> str:
        """插件描述"""
        return "系統資源監控工具 - 實時監控 CPU、記憶體、磁碟、網路等系統指標"
    
    @property
    def version(self) -> str:
        """插件版本"""
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        """需要的外部工具"""
        return ["glances"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            logger.info("Initializing glances plugin...")
            
            # 檢查 glances 工具可用性
            from .glances_model import GlancesModel
            model = GlancesModel()
            
            availability = model.check_glances_availability()
            if not availability["available"]:
                logger.warning("Glances tool not available, but plugin will use fallback mode")
                # 即使 Glances 不可用，我們仍然允許插件初始化（使用 psutil 回退）
            
            logger.info("Glances plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize glances plugin: {e}")
            return False
    
    def create_view(self):
        """創建視圖"""
        if self._view is None:
            from .glances_view import GlancesView
            self._view = GlancesView()
            logger.info("Created glances view")
        return self._view
    
    def create_model(self):
        """創建模型"""
        if self._model is None:
            from .glances_model import GlancesModel
            self._model = GlancesModel()
            logger.info("Created glances model")
        return self._model
    
    def create_controller(self, model=None, view=None):
        """創建控制器"""
        if self._controller is None:
            model = model or self.create_model()
            view = view or self.create_view()
            
            from .glances_controller import GlancesController
            self._controller = GlancesController(model, view)
            logger.info("Created glances controller")
        
        return self._controller
    
    def cleanup(self):
        """清理資源"""
        try:
            if self._controller:
                self._controller.cleanup()
            
            logger.info("GlancesPlugin cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during glances plugin cleanup: {e}")


def create_plugin():
    """創建插件實例"""
    return GlancesPlugin()