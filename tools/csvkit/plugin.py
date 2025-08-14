"""
csvkit 插件 - CSV 處理工具套件插件
提供 15 個 csvkit 工具的整合界面，支援 CSV 數據的轉換、處理和分析
"""

from core.plugin_manager import PluginInterface
from .csvkit_model import CsvkitModel
from .csvkit_view import CsvkitView
from .csvkit_controller import CsvkitController
import logging

logger = logging.getLogger(__name__)


class CsvkitPlugin(PluginInterface):
    """csvkit 插件類"""
    
    @property
    def name(self) -> str:
        return "csvkit"
    
    @property
    def description(self) -> str:
        return "CSV processing toolkit with 15 command-line tools for data conversion, cleaning, and analysis"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> list:
        # csvkit 的核心工具，檢查 csvstat 作為代表
        return ["csvstat"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            logger.info("Initializing csvkit plugin...")
            
            # 檢查 csvkit 是否可用
            model = CsvkitModel()
            if not model.csvkit_available:
                logger.warning("csvkit not available")
                return False
            
            logger.info(f"csvkit plugin initialized successfully with {len(model.available_tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize csvkit plugin: {e}")
            return False
    
    def create_model(self):
        """創建模型"""
        return CsvkitModel()
    
    def create_view(self):
        """創建視圖"""
        return CsvkitView()
    
    def create_controller(self, model, view):
        """創建控制器"""
        # 直接使用傳入的 model 和 view 創建控制器
        return CsvkitController(model, view)
    
    def cleanup(self):
        """清理插件資源"""
        logger.info("Cleaning up csvkit plugin...")


def create_plugin():
    """創建插件實例"""
    return CsvkitPlugin()