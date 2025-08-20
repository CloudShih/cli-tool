"""
配置管理器 - 統一管理應用程式配置
支援開發和 PyInstaller 打包環境
"""

import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """統一的配置管理器"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self.load_config()
    
    def get_resource_path(self, relative_path: str) -> Path:
        """
        獲取資源文件路徑，支援開發和 PyInstaller 環境
        
        Args:
            relative_path: 相對路徑
            
        Returns:
            Path: 資源文件的絕對路徑
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包環境
            base_path = Path(sys._MEIPASS)
            logger.info(f"PyInstaller environment detected, base path: {base_path}")
        else:
            # 開發環境
            base_path = Path(__file__).parent.parent
            logger.info(f"Development environment detected, base path: {base_path}")
        
        resource_path = base_path / relative_path
        logger.debug(f"Resource path resolved: {resource_path}")
        return resource_path
    
    def load_config(self):
        """載入配置文件"""
        try:
            config_file = self.get_resource_path("config/cli_tool_config.json")
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Configuration loaded from: {config_file}")
            else:
                # 如果配置文件不存在，使用預設配置
                self._config = self._get_default_config()
                logger.info("Using default configuration")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取預設配置"""
        fd_path = os.environ.get("FD_PATH")
        if not fd_path:
            fd_path = self._find_fd_executable()
        return {
            "tools": {
                "fd": {
                    "executable_path": fd_path,
                    "default_search_type": "both",  # both, files, directories
                    "default_hidden": False,
                    "default_case_sensitive": False
                },
                "poppler": {
                    "pdfinfo_path": "pdfinfo",
                    "pdftotext_path": "pdftotext",
                    "pdfimages_path": "pdfimages",
                    "pdfseparate_path": "pdfseparate",
                    "pdfunite_path": "pdfunite",
                    "pdftoppm_path": "pdftoppm",
                    "pdftohtml_path": "pdftohtml",
                    "qpdf_path": "qpdf"
                }
            },
            "ui": {
                "theme": "dark",
                "window": {
                    "width": 800,
                    "height": 600,
                    "x": 100,
                    "y": 100
                },
                "remember_window_state": True,
                "show_tooltips": True
            },
            "general": {
                "auto_save_settings": True,
                "max_output_lines": 1000,
                "enable_logging": True,
                "log_level": "INFO"
            }
        }
    
    def _find_fd_executable(self) -> str:
        """自動尋找 fd 執行檔路徑"""
        env_path = os.environ.get("FD_PATH")
        if env_path and self._check_executable(env_path):
            logger.info(f"Using fd executable from environment: {env_path}")
            return env_path

        config_path = (
            self._config.get("tools", {}).get("fd", {}).get("executable_path")
        )
        if config_path and self._check_executable(config_path):
            logger.info(f"Using fd executable from config: {config_path}")
            return config_path

        # 常見的 fd 安裝路径
        common_paths = [
            "fd",  # 在 PATH 中
            "fd.exe",  # Windows
            "C:\\Users\\cloudchshih\\AppData\\Local\\Microsoft\\WinGet\\Packages\\sharkdp.fd_Microsoft.WinGet.Source_8wekyb3d8bbwe\\fd-v10.2.0-x86_64-pc-windows-msvc\\fd.exe"
        ]

        for path in common_paths:
            if self._check_executable(path):
                logger.info(f"Found fd executable at: {path}")
                return path

        logger.warning("fd executable not found in common paths")
        return "fd"  # 回傳預設值
    
    def _check_executable(self, path: str) -> bool:
        """檢查執行檔是否存在且可執行"""
        try:
            return shutil.which(path) is not None
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key: 配置鍵 (支援點記法，如 'tools.fd.executable_path')
            default: 預設值
            
        Returns:
            配置值或預設值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Configuration key '{key}' not found, using default: {default}")
            return default
    
    def set(self, key: str, value: Any):
        """
        設置配置值
        
        Args:
            key: 配置鍵 (支援點記法)
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 導航到正確的嵌套位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                # 如果值不是字典，轉換為字典
                config[k] = {}
            config = config[k]
        
        # 設置值
        config[keys[-1]] = value
        logger.debug(f"Configuration updated: {key} = {value}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_file = self.get_resource_path("config/cli_tool_config.json")
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """獲取特定工具的配置"""
        return self.get(f"tools.{tool_name}", {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """獲取 UI 配置"""
        return self.get("ui", {})
    
    def get_general_config(self) -> Dict[str, Any]:
        """獲取一般配置"""
        return self.get("general", {})
    
    def get_config(self) -> Dict[str, Any]:
        """獲取完整配置字典"""
        return self._config.copy()


# 全域配置管理器實例
config_manager = ConfigManager()
