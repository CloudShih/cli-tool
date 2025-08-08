"""
Ripgrep 插件入口點 - 實現 PluginInterface
"""
from core.plugin_manager import PluginInterface
from typing import List
import subprocess
import logging

logger = logging.getLogger(__name__)

class RipgrepPlugin(PluginInterface):
    """Ripgrep 文本搜尋工具插件"""
    
    def __init__(self):
        self._is_available = None
        self._version = None
    
    @property
    def name(self) -> str:
        return "ripgrep"
    
    @property
    def display_name(self) -> str:
        return "文本搜尋"
    
    @property
    def description(self) -> str:
        return "使用 ripgrep 進行高效能文本內容搜尋，支援正則表達式和多種檔案格式"
    
    @property
    def version(self) -> str:
        if self._version is None:
            self._version = self._detect_version()
        return self._version
    
    @property
    def required_tools(self) -> List[str]:
        return ["rg"]  # ripgrep 執行檔
    
    @property
    def icon(self) -> str:
        return "🔍"  # 搜尋圖示
    
    def check_tools_availability(self) -> bool:
        """檢查 ripgrep 工具可用性"""
        if self._is_available is not None:
            return self._is_available
            
        try:
            result = subprocess.run(
                ['rg', '--version'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            self._is_available = result.returncode == 0
            if self._is_available:
                # 提取版本資訊
                version_line = result.stdout.split('\n')[0]
                self._version = version_line.split()[1] if len(version_line.split()) > 1 else "Unknown"
            logger.info(f"Ripgrep availability check: {self._is_available}, version: {self._version}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Ripgrep not found or timeout: {e}")
            self._is_available = False
            
        return self._is_available
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 檢查工具可用性
            if not self.check_tools_availability():
                logger.error("Ripgrep tool not available")
                return False
            
            logger.info(f"Ripgrep plugin initialized successfully (version: {self.version})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ripgrep plugin: {e}")
            return False
    
    def is_available(self) -> bool:
        """檢查插件是否可用"""
        return self.check_tools_availability()
    
    def create_model(self):
        """創建模型實例"""
        try:
            from .ripgrep_model import RipgrepModel
            return RipgrepModel()
        except Exception as e:
            logger.error(f"Error creating ripgrep model: {e}")
            return None
    
    def create_view(self):
        """創建視圖實例"""
        try:
            from .ripgrep_view import RipgrepView
            return RipgrepView()
        except Exception as e:
            logger.error(f"Error creating ripgrep view: {e}")
            return None
    
    def create_controller(self, model, view):
        """創建控制器實例"""
        try:
            from .ripgrep_controller import RipgrepController
            return RipgrepController(model, view)
        except Exception as e:
            logger.error(f"Error creating ripgrep controller: {e}")
            return None
    
    def cleanup(self):
        """清理資源"""
        logger.info("Ripgrep plugin cleanup completed")
    
    def _detect_version(self) -> str:
        """偵測 ripgrep 版本"""
        try:
            if self._is_available:
                return self._version or "Unknown"
            else:
                return "Not Available"
        except:
            return "Unknown"

def create_plugin():
    """插件工廠函數"""
    return RipgrepPlugin()