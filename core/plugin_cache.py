"""
插件快取系統
用於加速插件載入過程
"""

import json
import pickle
import hashlib
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


@dataclass
class PluginCacheEntry:
    """插件快取條目"""
    plugin_name: str
    plugin_path: str
    last_modified: float
    is_available: bool
    initialization_time: float
    dependencies_hash: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PluginCache:
    """插件快取管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # 在專案根目錄創建快取目錄
            project_root = config_manager.get_resource_path(".")
            self.cache_dir = project_root / ".cache" / "plugin_cache"
        self.cache_file = self.cache_dir / "plugin_cache.json"
        self.cache_data: Dict[str, PluginCacheEntry] = {}
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self):
        """確保快取目錄存在"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_cache(self):
        """載入快取資料"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.cache_data = {
                        name: PluginCacheEntry(**data)
                        for name, data in cache_data.items()
                    }
                logger.debug(f"Loaded plugin cache with {len(self.cache_data)} entries")
        except Exception as e:
            logger.warning(f"Failed to load plugin cache: {e}")
            self.cache_data = {}
    
    def _save_cache(self):
        """保存快取資料"""
        try:
            cache_data = {
                name: asdict(entry)
                for name, entry in self.cache_data.items()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved plugin cache with {len(self.cache_data)} entries")
        except Exception as e:
            logger.error(f"Failed to save plugin cache: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """計算檔案雜湊值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _get_dependencies_hash(self, plugin_path: Path) -> str:
        """計算插件依賴的雜湊值"""
        try:
            # 計算插件目錄中主要檔案的雜湊值
            important_files = ['plugin.py', '__init__.py']
            hash_input = []
            
            for filename in important_files:
                file_path = plugin_path / filename
                if file_path.exists():
                    hash_input.append(self._get_file_hash(file_path))
                    hash_input.append(str(file_path.stat().st_mtime))
            
            return hashlib.md5(''.join(hash_input).encode()).hexdigest()
        except Exception:
            return ""
    
    def is_plugin_cached(self, plugin_name: str, plugin_path: Path) -> bool:
        """檢查插件是否已被快取且有效"""
        if plugin_name not in self.cache_data:
            return False
        
        entry = self.cache_data[plugin_name]
        
        # 檢查路徑是否匹配
        if entry.plugin_path != str(plugin_path):
            return False
        
        # 檢查依賴是否變更
        current_hash = self._get_dependencies_hash(plugin_path)
        if entry.dependencies_hash != current_hash:
            return False
        
        # 檢查快取是否過期 (24小時)
        if time.time() - entry.last_modified > 24 * 3600:
            return False
        
        return True
    
    def get_cached_plugin_info(self, plugin_name: str) -> Optional[PluginCacheEntry]:
        """獲取快取的插件資訊"""
        return self.cache_data.get(plugin_name)
    
    def cache_plugin_info(self, plugin_name: str, plugin_path: Path, 
                         is_available: bool, initialization_time: float,
                         error_message: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """快取插件資訊"""
        entry = PluginCacheEntry(
            plugin_name=plugin_name,
            plugin_path=str(plugin_path),
            last_modified=time.time(),
            is_available=is_available,
            initialization_time=initialization_time,
            dependencies_hash=self._get_dependencies_hash(plugin_path),
            error_message=error_message,
            metadata=metadata
        )
        
        self.cache_data[plugin_name] = entry
        self._save_cache()
        logger.debug(f"Cached plugin info: {plugin_name}")
    
    def invalidate_cache(self, plugin_name: Optional[str] = None):
        """使快取失效"""
        if plugin_name:
            if plugin_name in self.cache_data:
                del self.cache_data[plugin_name]
                logger.debug(f"Invalidated cache for plugin: {plugin_name}")
        else:
            self.cache_data.clear()
            logger.debug("Invalidated all plugin cache")
        
        self._save_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取快取統計資訊"""
        available_count = sum(1 for entry in self.cache_data.values() if entry.is_available)
        total_time = sum(entry.initialization_time for entry in self.cache_data.values())
        
        return {
            'total_plugins': len(self.cache_data),
            'available_plugins': available_count,
            'unavailable_plugins': len(self.cache_data) - available_count,
            'total_initialization_time': total_time,
            'average_initialization_time': total_time / len(self.cache_data) if self.cache_data else 0,
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }


# 全域快取實例
plugin_cache = PluginCache()