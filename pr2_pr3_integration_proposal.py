#!/usr/bin/env python3
"""
PR#2 和 PR#3 整合建議實作
展示如何安全地整合環境變數支援和 shutil.which 優化
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class EnhancedToolDetector:
    """
    增強的工具探測器
    整合 PR#2 (環境變數支援) 和 PR#3 (shutil.which 使用) 的改進
    """
    
    @staticmethod
    def find_executable(tool_name: str, 
                       config_path: Optional[str] = None,
                       env_var_name: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        增強的可執行檔案查找邏輯
        
        優先順序:
        1. 環境變數 (如果提供)
        2. 配置檔案路徑 (如果提供且存在)
        3. shutil.which (系統 PATH)
        4. 失敗
        
        Returns:
            Tuple[path, source] - 路徑和來源說明
        """
        
        # 1. 檢查環境變數
        if env_var_name:
            env_path = os.environ.get(env_var_name)
            if env_path:
                path_obj = Path(env_path)
                if path_obj.exists() and path_obj.is_file():
                    logger.info(f"Found {tool_name} via environment variable {env_var_name}: {env_path}")
                    return str(path_obj), f"environment_variable_{env_var_name}"
                else:
                    logger.warning(f"Environment variable {env_var_name} points to non-existent file: {env_path}")
        
        # 2. 檢查配置檔案路徑
        if config_path:
            path_obj = Path(config_path)
            if path_obj.exists() and path_obj.is_file():
                logger.info(f"Found {tool_name} via configuration: {config_path}")
                return str(path_obj), "configuration_file"
            else:
                logger.warning(f"Configuration path for {tool_name} does not exist: {config_path}")
        
        # 3. 使用 shutil.which 在系統 PATH 中查找
        which_path = shutil.which(tool_name)
        if which_path:
            logger.info(f"Found {tool_name} via shutil.which: {which_path}")
            return which_path, "system_path"
        
        # 4. 未找到
        logger.error(f"Could not find executable for {tool_name}")
        return None, "not_found"
    
    @staticmethod
    def check_tool_availability_fast(tool_path: str) -> bool:
        """
        快速檢查工具可用性
        使用 shutil.which 風格的檢查，比 subprocess 更快
        """
        if not tool_path:
            return False
            
        path_obj = Path(tool_path)
        return path_obj.exists() and path_obj.is_file() and os.access(path_obj, os.X_OK)
    
    @staticmethod
    def check_tool_availability_thorough(tool_path: str, timeout: float = 2.0) -> bool:
        """
        全面檢查工具可用性
        實際執行工具以確認其正常工作
        """
        try:
            result = subprocess.run([tool_path, '--help'], 
                                  capture_output=True, 
                                  timeout=timeout,
                                  text=True)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError, OSError):
            return False

class EnhancedFdModel:
    """
    增強的 FdModel 實作範例
    展示如何整合 PR#2 和 PR#3 的改進
    """
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.detector = EnhancedToolDetector()
        
        # 使用增強的工具探測
        config_path = self.config_manager.get('tools.fd.executable_path')
        self.fd_executable_path, self.path_source = self.detector.find_executable(
            tool_name='fd',
            config_path=config_path,
            env_var_name='FD_PATH'  # PR#2: 環境變數支援
        )
        
        if not self.fd_executable_path:
            raise RuntimeError("fd executable not found")
        
        # 驗證工具可用性
        if not self.detector.check_tool_availability_fast(self.fd_executable_path):
            logger.warning(f"fd executable may not be functional: {self.fd_executable_path}")
        
        logger.info(f"FdModel initialized with fd from {self.path_source}: {self.fd_executable_path}")

class EnhancedPluginInterface:
    """
    增強的插件介面實作範例
    展示如何在插件系統中使用改進的工具探測
    """
    
    def __init__(self):
        self.detector = EnhancedToolDetector()
        self.tool_cache = {}  # 簡單的工具路徑快取
    
    def check_tools_availability(self, required_tools: list) -> bool:
        """
        使用增強的工具探測檢查工具可用性
        """
        for tool_name in required_tools:
            if not self._is_tool_available(tool_name):
                logger.warning(f"Required tool '{tool_name}' not available")
                return False
        return True
    
    def _is_tool_available(self, tool_name: str) -> bool:
        """
        檢查單個工具是否可用，使用快取提高效能
        """
        # 檢查快取
        if tool_name in self.tool_cache:
            cached_path = self.tool_cache[tool_name]
            if cached_path and self.detector.check_tool_availability_fast(cached_path):
                return True
        
        # 重新探測
        tool_path, source = self.detector.find_executable(tool_name)
        
        if tool_path:
            # 快速檢查
            if self.detector.check_tool_availability_fast(tool_path):
                self.tool_cache[tool_name] = tool_path
                return True
            
            # 如果快速檢查失敗，嘗試全面檢查
            if self.detector.check_tool_availability_thorough(tool_path):
                self.tool_cache[tool_name] = tool_path
                return True
        
        # 標記為不可用
        self.tool_cache[tool_name] = None
        return False

# 示範使用
def demonstrate_enhancements():
    """示範 PR#2 和 PR#3 整合後的改進效果"""
    
    print("=== PR#2 & PR#3 整合效果示範 ===")
    
    detector = EnhancedToolDetector()
    
    # 測試工具探測
    tools_to_test = [
        {'name': 'fd', 'config': 'C:\\Users\\cloudchshih\\AppData\\Local\\Microsoft\\WinGet\\Packages\\sharkdp.fd_Microsoft.WinGet.Source_8wekyb3d8bbwe\\fd-v10.2.0-x86_64-pc-windows-msvc\\fd.exe', 'env_var': 'FD_PATH'},
        {'name': 'pandoc', 'config': 'pandoc', 'env_var': 'PANDOC_PATH'},
        {'name': 'bat', 'config': 'bat', 'env_var': 'BAT_PATH'},
        {'name': 'rg', 'config': 'rg', 'env_var': 'RG_PATH'},
    ]
    
    for tool_info in tools_to_test:
        path, source = detector.find_executable(
            tool_info['name'],
            tool_info['config'],
            tool_info['env_var']
        )
        
        if path:
            fast_check = detector.check_tool_availability_fast(path)
            print(f"[OK] {tool_info['name']}: {path}")
            print(f"     來源: {source}")
            print(f"     快速檢查: {'通過' if fast_check else '失敗'}")
        else:
            print(f"[FAIL] {tool_info['name']}: 未找到")
    
    # 示範效能改進
    print("\n=== 效能比較 ===")
    import time
    
    # 測試 shutil.which vs subprocess 的效能
    test_tools = ['fd', 'pandoc', 'bat', 'rg']
    
    # shutil.which 方法
    start_time = time.time()
    for tool in test_tools:
        shutil.which(tool)
    shutil_time = time.time() - start_time
    
    # subprocess 方法（模擬當前實作）
    start_time = time.time()
    for tool in test_tools:
        try:
            subprocess.run([tool, '--help'], 
                          capture_output=True, 
                          timeout=1)
        except:
            pass
    subprocess_time = time.time() - start_time
    
    print(f"shutil.which 方法: {shutil_time:.3f}s")
    print(f"subprocess 方法: {subprocess_time:.3f}s") 
    print(f"效能提升: {subprocess_time/shutil_time:.1f}x")

if __name__ == "__main__":
    demonstrate_enhancements()