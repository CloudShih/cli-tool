"""
QPDF 工具插件實現
將 QPDF PDF 處理工具包裝為插件
"""

import logging
from typing import List
from core.plugin_manager import PluginInterface
from .qpdf_model import QPDFModel
from .qpdf_view import QPDFView
from .qpdf_controller import QPDFController

logger = logging.getLogger(__name__)


class QPDFPlugin(PluginInterface):
    """QPDF PDF 處理工具插件"""
    
    @property
    def name(self) -> str:
        return "qpdf"
    
    @property
    def description(self) -> str:
        return "Advanced PDF processing tools using QPDF (encryption, decryption, linearization, compression, repair, etc.)"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["qpdf"]
    
    def check_tools_availability(self) -> bool:
        """
        檢查 QPDF 工具可用性
        """
        # 使用內建引擎檢查工具可用性
        try:
            from .core.qpdf_engine import QPDFEngine
            engine = QPDFEngine()
            return engine.is_available()
        except Exception as e:
            logger.error(f"Failed to check QPDF availability: {e}")
            return False
    
    def initialize(self) -> bool:
        """初始化 QPDF 插件"""
        try:
            logger.info("Initializing QPDF plugin...")
            
            # 檢查 QPDF 工具是否可用
            if not self.check_tools_availability():
                logger.error("QPDF tool not available, plugin initialization failed")
                return False
            
            # 檢查配置
            from config.config_manager import config_manager
            qpdf_config = config_manager.get_tool_config('qpdf')
            if qpdf_config:
                logger.info(f"QPDF configuration loaded: {qpdf_config}")
            else:
                logger.info("Using default QPDF configuration")
            
            # 測試基本功能
            from .core.qpdf_engine import QPDFEngine
            engine = QPDFEngine(qpdf_config.get('executable_path', 'qpdf') if qpdf_config else 'qpdf')
            version = engine.get_version()
            if version:
                logger.info(f"QPDF plugin initialized successfully - Version: {version}")
                return True
            else:
                logger.error("Failed to get QPDF version")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize QPDF plugin: {e}")
            return False
    
    def create_view(self):
        """創建 QPDF 插件的視圖"""
        try:
            return QPDFView()
        except Exception as e:
            logger.error(f"Failed to create QPDF view: {e}")
            raise
    
    def create_model(self):
        """創建 QPDF 插件的模型"""
        try:
            return QPDFModel()
        except Exception as e:
            logger.error(f"Failed to create QPDF model: {e}")
            raise
    
    def create_controller(self, model, view):
        """創建 QPDF 插件的控制器"""
        try:
            return QPDFController(model, view)
        except Exception as e:
            logger.error(f"Failed to create QPDF controller: {e}")
            raise
    
    def cleanup(self):
        """清理 QPDF 插件資源"""
        try:
            logger.info("Cleaning up QPDF plugin...")
            # 這裡可以進行插件特定的清理工作
            # 例如：保存設定、清理臨時檔案等
        except Exception as e:
            logger.error(f"Error during QPDF plugin cleanup: {e}")
    
    def get_supported_operations(self) -> List[str]:
        """獲取支援的操作類型"""
        return [
            "check",           # 檢查 PDF 完整性
            "decrypt",         # 解密 PDF
            "encrypt",         # 加密 PDF
            "linearize",       # 線性化 PDF
            "split_pages",     # 分割頁面
            "rotate",          # 旋轉頁面
            "compress_streams", # 壓縮
            "repair",          # 修復
            "json_info",       # 獲取 JSON 資訊
            "remove_restrictions" # 移除限制
        ]
    
    def get_supported_formats(self) -> List[str]:
        """獲取支援的檔案格式"""
        return ["pdf"]
    
    def get_plugin_info(self) -> dict:
        """獲取插件詳細資訊"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "required_tools": self.required_tools,
            "supported_operations": self.get_supported_operations(),
            "supported_formats": self.get_supported_formats(),
            "author": "CLI Tool Project",
            "homepage": "https://qpdf.sourceforge.io/",
            "documentation": "https://qpdf.readthedocs.io/"
        }


def create_plugin() -> QPDFPlugin:
    """插件工廠函數"""
    return QPDFPlugin()