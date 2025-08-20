"""
插件管理器 - 負責載入、管理和協調各種工具插件
支援動態載入和配置管理
"""

import os
import sys
import importlib
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Type, Optional, Any
from abc import ABC, abstractmethod
from pathlib import Path
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

# Cache for tool availability checks to avoid repeated subprocess calls
_tool_availability_cache: Dict[str, bool] = {}
_cache_lock = threading.Lock()

# Executor for running blocking checks without stalling the main thread
_tool_check_executor = ThreadPoolExecutor(max_workers=4)


class PluginInterface(ABC):
    """插件接口基類 - 所有插件必須實現此接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名稱"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def required_tools(self) -> List[str]:
        """所需的外部工具列表"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件，返回是否成功"""
        pass
    
    @abstractmethod
    def create_view(self):
        """創建插件的 GUI 視圖"""
        pass
    
    @abstractmethod
    def create_model(self):
        """創建插件的數據模型"""
        pass
    
    @abstractmethod
    def create_controller(self, model, view):
        """創建插件的控制器"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件資源"""
        pass
    
    def is_available(self) -> bool:
        """檢查插件是否可用（所需工具是否安裝）"""
        return self.check_tools_availability()
    
    def check_tools_availability(self) -> bool:
        """檢查所需工具是否可用"""
        for tool in self.required_tools:
            if not self._check_tool_availability(tool):
                logger.warning(f"Required tool '{tool}' not available for plugin '{self.name}'")
                return False
        return True
    
    def _check_tool_availability(self, tool: str) -> bool:
        """檢查單個工具是否可用"""
        with _cache_lock:
            if tool in _tool_availability_cache:
                return _tool_availability_cache[tool]

        def _run_check() -> bool:
            try:
                import subprocess
                result = subprocess.run(
                    [tool, '--help'], capture_output=True, timeout=5
                )
                return result.returncode == 0
            except (
                subprocess.TimeoutExpired,
                FileNotFoundError,
                subprocess.CalledProcessError,
            ):
                return False

        future = _tool_check_executor.submit(_run_check)
        available = future.result()

        with _cache_lock:
            _tool_availability_cache[tool] = available

        return available


class PluginManager:
    """插件管理器 - 負責插件的載入、管理和協調"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_instances: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    def initialize(self, async_mode: bool = False):
        """初始化插件管理器

        Args:
            async_mode: 若為 True，初始化將在背景執行緒中進行，
                        以避免阻塞主執行緒。
        """
        if self._initialized:
            return

        if async_mode:
            thread = threading.Thread(target=self._initialize_internal, daemon=True)
            thread.start()
        else:
            self._initialize_internal()

    def _initialize_internal(self):
        logger.info("Initializing Plugin Manager...")
        self.discover_plugins()
        self.load_plugins()
        self._initialized = True
        logger.info(f"Plugin Manager initialized with {len(self.plugins)} plugins")
    
    def discover_plugins(self) -> List[str]:
        """自動發現可用的插件"""
        logger.info("Discovering plugins...")
        
        # 從 tools 目錄載入插件
        tools_dir = config_manager.get_resource_path("tools")
        if tools_dir.exists():
            self._discover_plugins_in_directory(tools_dir)
        
        # 從配置中載入額外的插件路徑
        extra_plugin_paths = config_manager.get('plugins.extra_paths', [])
        for path in extra_plugin_paths:
            plugin_path = Path(path)
            if plugin_path.exists():
                self._discover_plugins_in_directory(plugin_path)
        
        # 返回已發現的插件名稱列表
        return list(self.plugins.keys())
    
    def _discover_plugins_in_directory(self, directory: Path):
        """在指定目錄中發現插件"""
        for item in directory.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin_module_path = f"tools.{item.name}.plugin"
                try:
                    module = importlib.import_module(plugin_module_path)
                    if hasattr(module, 'create_plugin'):
                        plugin = module.create_plugin()
                        if isinstance(plugin, PluginInterface):
                            self.register_plugin(plugin)
                            logger.info(f"Discovered plugin: {plugin.name}")
                        else:
                            logger.warning(f"Invalid plugin in {plugin_module_path}: not implementing PluginInterface")
                except ImportError as e:
                    logger.debug(f"No plugin found in {plugin_module_path}: {e}")
                except Exception as e:
                    logger.error(f"Error loading plugin from {plugin_module_path}: {e}")
    
    def register_plugin(self, plugin: PluginInterface):
        """註冊插件"""
        if plugin.name in self.plugins:
            logger.warning(f"Plugin '{plugin.name}' already registered, replacing...")
        
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
    
    def load_plugins(self):
        """載入和初始化所有插件（不創建 UI 視圖）"""
        logger.info("Loading plugins...")
        
        failed_plugins = []
        for name, plugin in self.plugins.items():
            try:
                if plugin.is_available():
                    if plugin.initialize():
                        # 只創建插件實例記錄，不創建 UI 組件
                        # UI 組件將在主線程中創建
                        logger.info(f"Successfully initialized plugin: {name}")
                    else:
                        failed_plugins.append(name)
                        logger.error(f"Failed to initialize plugin: {name}")
                else:
                    failed_plugins.append(name)
                    logger.warning(f"Plugin '{name}' not available (missing required tools)")
                    
            except Exception as e:
                failed_plugins.append(name)
                logger.error(f"Error loading plugin '{name}': {e}")
        
        # 移除載入失敗的插件
        for name in failed_plugins:
            if name in self.plugins:
                del self.plugins[name]
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """獲取指定的插件"""
        return self.plugins.get(name)
    
    def get_plugin_instance(self, name: str) -> Optional[Dict[str, Any]]:
        """獲取插件實例（包含 model, view, controller）"""
        return self.plugin_instances.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """獲取所有已註冊的插件"""
        return self.plugins.copy()
    
    def get_available_plugins(self) -> Dict[str, PluginInterface]:
        """獲取所有可用的插件"""
        return {name: plugin for name, plugin in self.plugins.items() 
                if plugin.is_available()}
    
    def get_plugin_views(self) -> Dict[str, Any]:
        """獲取所有插件的視圖，用於添加到主界面"""
        views = {}
        for name, instance in self.plugin_instances.items():
            views[name] = instance['view']
        return views
    
    def cleanup(self):
        """清理所有插件資源"""
        logger.info("Cleaning up plugins...")
        for name, plugin in self.plugins.items():
            try:
                plugin.cleanup()
                logger.debug(f"Cleaned up plugin: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin '{name}': {e}")
        
        self.plugins.clear()
        self.plugin_instances.clear()
        self._initialized = False


# 全域插件管理器實例
plugin_manager = PluginManager()