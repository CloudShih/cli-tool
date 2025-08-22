"""
快速插件載入器
優化插件載入速度的核心實現
"""

import logging
import time
import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass

from core.plugin_manager import PluginInterface, PluginManager
from core.plugin_cache import plugin_cache, PluginCacheEntry
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


@dataclass
class LoadingStrategy:
    """載入策略配置"""
    use_cache: bool = True
    parallel_loading: bool = True
    max_workers: int = 4
    lazy_initialization: bool = True
    preload_critical: bool = True
    skip_tool_checks: bool = False
    cache_duration_hours: int = 24


class FastPluginLoader:
    """快速插件載入器"""
    
    def __init__(self, plugin_manager: PluginManager, strategy: Optional[LoadingStrategy] = None):
        self.plugin_manager = plugin_manager
        self.strategy = strategy or LoadingStrategy()
        self.critical_plugins = {'fd', 'ripgrep', 'poppler'}  # 優先載入的插件
        
    async def load_plugins_async(self) -> Tuple[bool, str, Dict[str, Any]]:
        """異步載入插件"""
        start_time = time.time()
        
        try:
            # 階段1: 快速發現插件
            discovery_start = time.time()
            await self._discover_plugins_fast()
            discovery_time = time.time() - discovery_start
            
            # 階段2: 並行載入插件
            loading_start = time.time()
            success_count, total_count = await self._load_plugins_parallel()
            loading_time = time.time() - loading_start
            
            total_time = time.time() - start_time
            
            stats = {
                'total_time': total_time,
                'discovery_time': discovery_time,
                'loading_time': loading_time,
                'success_count': success_count,
                'total_count': total_count,
                'cache_stats': plugin_cache.get_cache_stats()
            }
            
            success = success_count > 0
            message = f"成功載入 {success_count}/{total_count} 個插件 (耗時: {total_time:.2f}s)"
            
            logger.info(f"Fast plugin loading completed: {message}")
            return success, message, stats
            
        except Exception as e:
            logger.error(f"Fast plugin loading failed: {e}")
            return False, f"載入失敗: {str(e)}", {}
    
    async def _discover_plugins_fast(self):
        """快速發現插件"""
        logger.debug("Starting fast plugin discovery")
        
        # 獲取插件目錄
        tools_dir = config_manager.get_resource_path("tools")
        if not tools_dir.exists():
            logger.warning("Tools directory not found")
            return
        
        # 使用快取資訊快速識別插件
        plugin_dirs = []
        for item in tools_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                plugin_file = item / "plugin.py"
                if plugin_file.exists():
                    plugin_dirs.append((item.name, item))
        
        logger.debug(f"Discovered {len(plugin_dirs)} potential plugins")
        
        # 並行檢查插件
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.strategy.max_workers) as executor:
            tasks = []
            for plugin_name, plugin_path in plugin_dirs:
                if self.strategy.use_cache and plugin_cache.is_plugin_cached(plugin_name, plugin_path):
                    # 使用快取資訊
                    cached_info = plugin_cache.get_cached_plugin_info(plugin_name)
                    if cached_info and cached_info.is_available:
                        task = executor.submit(self._load_plugin_from_cache, plugin_name, plugin_path, cached_info)
                        tasks.append(task)
                else:
                    # 需要重新載入
                    task = executor.submit(self._load_plugin_fresh, plugin_name, plugin_path)
                    tasks.append(task)
            
            # 等待所有任務完成
            for future in concurrent.futures.as_completed(tasks):
                try:
                    await asyncio.wrap_future(future)
                except Exception as e:
                    logger.error(f"Error in plugin discovery task: {e}")
    
    def _load_plugin_from_cache(self, plugin_name: str, plugin_path: Path, cached_info: PluginCacheEntry) -> bool:
        """從快取載入插件"""
        try:
            logger.debug(f"Loading plugin from cache: {plugin_name}")
            
            # 載入插件模組
            import importlib
            plugin_module_path = f"tools.{plugin_name}.plugin"
            module = importlib.import_module(plugin_module_path)
            
            if hasattr(module, 'create_plugin'):
                plugin = module.create_plugin()
                if isinstance(plugin, PluginInterface):
                    # 快速註冊，跳過耗時的初始化檢查
                    self.plugin_manager.register_plugin(plugin)
                    
                    # 如果啟用延遲初始化，稍後再進行完整初始化
                    if not self.strategy.lazy_initialization:
                        if not plugin.initialize():
                            logger.warning(f"Plugin {plugin_name} failed to initialize")
                            return False
                    
                    logger.debug(f"Successfully loaded plugin from cache: {plugin_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name} from cache: {e}")
            # 快取失效，重新載入
            return self._load_plugin_fresh(plugin_name, plugin_path)
    
    def _load_plugin_fresh(self, plugin_name: str, plugin_path: Path) -> bool:
        """重新載入插件"""
        try:
            start_time = time.time()
            logger.debug(f"Loading plugin fresh: {plugin_name}")
            
            # 載入插件模組
            import importlib
            plugin_module_path = f"tools.{plugin_name}.plugin"
            
            # 如果模組已載入，重新載入以獲取最新版本
            if plugin_module_path in importlib.sys.modules:
                module = importlib.reload(importlib.sys.modules[plugin_module_path])
            else:
                module = importlib.import_module(plugin_module_path)
            
            if hasattr(module, 'create_plugin'):
                plugin = module.create_plugin()
                if isinstance(plugin, PluginInterface):
                    # 註冊插件
                    self.plugin_manager.register_plugin(plugin)
                    
                    # 檢查可用性和初始化
                    is_available = True
                    error_message = None
                    
                    if not self.strategy.skip_tool_checks:
                        if not plugin.is_available():
                            is_available = False
                            error_message = "Required tools not available"
                    
                    if is_available and not self.strategy.lazy_initialization:
                        if not plugin.initialize():
                            is_available = False
                            error_message = "Plugin initialization failed"
                    
                    # 更新快取
                    initialization_time = time.time() - start_time
                    if self.strategy.use_cache:
                        metadata = {
                            'version': plugin.version,
                            'description': plugin.description,
                            'required_tools': plugin.required_tools
                        }
                        plugin_cache.cache_plugin_info(
                            plugin_name, plugin_path, is_available, 
                            initialization_time, error_message, metadata
                        )
                    
                    logger.debug(f"Successfully loaded plugin fresh: {plugin_name} (time: {initialization_time:.3f}s)")
                    return is_available
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name} fresh: {e}")
            
            # 記錄到快取
            if self.strategy.use_cache:
                plugin_cache.cache_plugin_info(
                    plugin_name, plugin_path, False, 0.0, str(e)
                )
            
            return False
    
    async def _load_plugins_parallel(self) -> Tuple[int, int]:
        """並行載入插件"""
        plugins = self.plugin_manager.get_all_plugins()
        
        if not plugins:
            return 0, 0
        
        # 分為關鍵插件和一般插件
        critical_plugins = {name: plugin for name, plugin in plugins.items() 
                          if name in self.critical_plugins}
        regular_plugins = {name: plugin for name, plugin in plugins.items() 
                          if name not in self.critical_plugins}
        
        success_count = 0
        
        # 優先載入關鍵插件
        if critical_plugins and self.strategy.preload_critical:
            logger.debug(f"Preloading {len(critical_plugins)} critical plugins")
            for plugin in critical_plugins.values():
                if self.strategy.lazy_initialization or plugin.initialize():
                    success_count += 1
        
        # 並行載入其餘插件
        if regular_plugins and self.strategy.parallel_loading:
            logger.debug(f"Parallel loading {len(regular_plugins)} regular plugins")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.strategy.max_workers) as executor:
                futures = []
                
                for plugin in regular_plugins.values():
                    if self.strategy.lazy_initialization:
                        # 延遲初始化，直接計為成功
                        success_count += 1
                    else:
                        future = executor.submit(plugin.initialize)
                        futures.append(future)
                
                # 等待初始化完成
                for future in concurrent.futures.as_completed(futures):
                    try:
                        if future.result():
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Plugin initialization error: {e}")
        
        return success_count, len(plugins)
    
    async def lazy_initialize_plugin(self, plugin_name: str) -> bool:
        """延遲初始化特定插件"""
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return False
        
        try:
            logger.debug(f"Lazy initializing plugin: {plugin_name}")
            return plugin.initialize()
        except Exception as e:
            logger.error(f"Error lazy initializing plugin {plugin_name}: {e}")
            return False


class OptimizedPluginManager(PluginManager):
    """優化的插件管理器"""
    
    def __init__(self, strategy: Optional[LoadingStrategy] = None):
        super().__init__()
        self.strategy = strategy or LoadingStrategy()
        self.fast_loader = FastPluginLoader(self, self.strategy)
        self.lazy_initialized = set()
    
    async def initialize_async(self) -> Tuple[bool, str, Dict[str, Any]]:
        """異步初始化"""
        if self._initialized:
            return True, "Already initialized", {}
        
        logger.info("Starting optimized plugin initialization")
        success, message, stats = await self.fast_loader.load_plugins_async()
        
        if success:
            self._initialized = True
            logger.info(f"Optimized plugin initialization completed: {message}")
        
        return success, message, stats
    
    def get_plugin_view(self, plugin_name: str):
        """獲取插件視圖，如果尚未初始化則進行延遲初始化"""
        if self.strategy.lazy_initialization and plugin_name not in self.lazy_initialized:
            if self.fast_loader.lazy_initialize_plugin(plugin_name):
                self.lazy_initialized.add(plugin_name)
        
        return super().get_plugin_instance(plugin_name)


# 創建優化的插件管理器實例
def create_optimized_plugin_manager(strategy: Optional[LoadingStrategy] = None) -> OptimizedPluginManager:
    """創建優化的插件管理器"""
    return OptimizedPluginManager(strategy)