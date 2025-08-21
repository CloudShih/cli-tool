"""
YT-DLP 插件入口點 - 實現 PluginInterface
"""
from core.plugin_manager import PluginInterface
from typing import List
import subprocess
import logging

logger = logging.getLogger(__name__)


class YtDlpPlugin(PluginInterface):
    """YT-DLP 影音下載工具插件"""
    
    def __init__(self):
        self._is_available = None
        self._version = None
    
    @property
    def name(self) -> str:
        return "yt_dlp"
    
    @property
    def display_name(self) -> str:
        return "影音下載"
    
    @property
    def description(self) -> str:
        return "使用 YT-DLP 下載 YouTube、Bilibili 等多平台影音內容，支援多種格式和品質選擇"
    
    @property
    def version(self) -> str:
        if self._version is None:
            self._version = self._detect_version()
        return self._version
    
    @property
    def required_tools(self) -> List[str]:
        return ["yt-dlp"]  # YT-DLP 執行檔
    
    @property
    def icon(self) -> str:
        return "🎬"  # 影片圖示
    
    def check_tools_availability(self) -> bool:
        """檢查 YT-DLP 工具可用性"""
        if self._is_available is not None:
            return self._is_available
            
        try:
            # 嘗試不同的可能路徑
            possible_commands = ["yt-dlp", "yt-dlp.exe"]
            
            for cmd in possible_commands:
                try:
                    result = subprocess.run(
                        [cmd, '--version'], 
                        capture_output=True, 
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        self._is_available = True
                        self._version = result.stdout.strip()
                        logger.info(f"YT-DLP found: {cmd}, version: {self._version}")
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            # 如果所有嘗試都失敗
            self._is_available = False
            logger.warning("YT-DLP not found in system PATH")
            
        except Exception as e:
            logger.warning(f"Error checking YT-DLP availability: {e}")
            self._is_available = False
            
        return self._is_available
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 檢查工具可用性
            if not self.check_tools_availability():
                logger.error("YT-DLP tool not available")
                return False
            
            # 檢查依賴
            try:
                import json
                from pathlib import Path
                from PyQt5.QtCore import QThread, pyqtSignal
                from PyQt5.QtWidgets import QWidget, QMessageBox
            except ImportError as e:
                logger.error(f"Missing required dependencies: {e}")
                return False
            
            logger.info(f"YT-DLP plugin initialized successfully (version: {self.version})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing yt-dlp plugin: {e}")
            return False
    
    def is_available(self) -> bool:
        """檢查插件是否可用"""
        return self.check_tools_availability()
    
    def create_model(self):
        """創建模型實例"""
        try:
            from .yt_dlp_model import YtDlpModel
            return YtDlpModel()
        except Exception as e:
            logger.error(f"Error creating yt-dlp model: {e}")
            return None
    
    def create_view(self):
        """創建視圖實例"""
        try:
            from .yt_dlp_view import YtDlpView
            return YtDlpView()
        except Exception as e:
            logger.error(f"Error creating yt-dlp view: {e}")
            return None
    
    def create_controller(self, model, view):
        """創建控制器實例"""
        try:
            from .yt_dlp_controller import YtDlpController
            return YtDlpController(model, view)
        except Exception as e:
            logger.error(f"Error creating yt-dlp controller: {e}")
            return None
    
    def cleanup(self):
        """清理資源"""
        logger.info("YT-DLP plugin cleanup completed")
    
    def _detect_version(self) -> str:
        """偵測 YT-DLP 版本"""
        try:
            if self._is_available and self._version:
                return self._version
            elif self.check_tools_availability():
                return self._version or "Unknown"
            else:
                return "Not Available"
        except:
            return "Unknown"
    
    def get_supported_sites(self) -> List[str]:
        """獲取支援的網站列表"""
        try:
            if not self.is_available():
                return []
            
            # 獲取支援的網站（常見的一些）
            return [
                "YouTube", "Bilibili", "Twitter", "Facebook", "Instagram",
                "TikTok", "Vimeo", "Dailymotion", "Twitch", "SoundCloud",
                "Spotify", "Netflix", "Prime Video", "Disney+", "Crunchyroll"
            ]
        except Exception as e:
            logger.warning(f"Error getting supported sites: {e}")
            return []
    
    def validate_url(self, url: str) -> bool:
        """驗證 URL 是否受支援"""
        try:
            if not self.is_available():
                return False
            
            # 簡單的 URL 格式檢查
            if not url or not url.strip():
                return False
            
            # 檢查是否包含支援的協議
            url = url.strip().lower()
            if not (url.startswith('http://') or url.startswith('https://')):
                return False
            
            # 基本的 URL 格式驗證
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            return url_pattern.match(url) is not None
            
        except Exception as e:
            logger.warning(f"Error validating URL: {e}")
            return False
    
    def get_installation_guide(self) -> str:
        """獲取安裝指南"""
        return """
YT-DLP 安裝指南：

方法一：使用 pip 安裝
pip install yt-dlp

方法二：下載執行檔
1. 前往 https://github.com/yt-dlp/yt-dlp/releases
2. 下載適合您系統的執行檔
3. 將執行檔放入 PATH 環境變數中

方法三：使用包管理器
Windows (Scoop): scoop install yt-dlp
macOS (Homebrew): brew install yt-dlp
Linux (apt): sudo apt install yt-dlp

建議同時安裝 FFmpeg 以獲得最佳體驗：
https://ffmpeg.org/download.html

安裝完成後重新啟動應用程式即可使用。
        """.strip()


def create_plugin():
    """插件工廠函數"""
    return YtDlpPlugin()