#!/usr/bin/env python3
"""
CLI Tool 基線驗證測試腳本
用於建立效能基線和功能驗證
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 設置路徑
sys.path.insert(0, '.')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_module_imports():
    """測試核心模組導入"""
    print("=== 模組導入測試 ===")
    
    test_modules = [
        'main_app',
        'config.config_manager', 
        'ui.theme_manager',
        'tools.fd.fd_model',
        'tools.poppler.poppler_model',
        'tools.pandoc.pandoc_model'
    ]
    
    results = {}
    for module in test_modules:
        try:
            start_time = time.time()
            __import__(module)
            import_time = time.time() - start_time
            results[module] = {'success': True, 'time': import_time}
            print(f"[OK] {module}: {import_time:.3f}s")
        except Exception as e:
            results[module] = {'success': False, 'error': str(e)}
            print(f"[FAIL] {module}: {e}")
    
    return results

def test_external_tools():
    """測試外部工具可用性"""
    print("\n=== 外部工具檢查 ===")
    
    tools = {
        'fd': 'C:\\Users\\cloudchshih\\AppData\\Local\\Microsoft\\WinGet\\Packages\\sharkdp.fd_Microsoft.WinGet.Source_8wekyb3d8bbwe\\fd-v10.2.0-x86_64-pc-windows-msvc\\fd.exe',
        'pandoc': 'pandoc',
        'bat': 'bat',
        'rg': 'rg'
    }
    
    results = {}
    for tool, path in tools.items():
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                results[tool] = {'available': True, 'version': version}
                print(f"[OK] {tool}: {version}")
            else:
                results[tool] = {'available': False, 'error': result.stderr}
                print(f"[FAIL] {tool}: Not available")
        except Exception as e:
            results[tool] = {'available': False, 'error': str(e)}
            print(f"[FAIL] {tool}: {e}")
    
    return results

def test_config_system():
    """測試配置系統"""
    print("\n=== 配置系統測試 ===")
    
    try:
        from config.config_manager import config_manager
        
        # 測試配置載入
        config = config_manager.get_config()
        print(f"[OK] 配置載入成功，包含 {len(config)} 個設定項")
        
        # 測試資源路徑解析
        icon_path = config_manager.get_resource_path("static/favicon/favicon.ico")
        if icon_path.exists():
            print(f"[OK] 資源路徑解析正常: {icon_path}")
        else:
            print(f"[WARN] 資源文件不存在: {icon_path}")
        
        return {'success': True, 'config_items': len(config)}
        
    except Exception as e:
        print(f"[FAIL] 配置系統錯誤: {e}")
        return {'success': False, 'error': str(e)}

def test_plugin_system():
    """測試插件系統"""
    print("\n=== 插件系統測試 ===")
    
    try:
        from core.plugin_manager import PluginManager
        
        # 初始化插件管理器
        plugin_manager = PluginManager()
        plugins = plugin_manager.get_available_plugins()
        
        print(f"[OK] 插件管理器初始化成功")
        print(f"[OK] 發現 {len(plugins)} 個插件")
        
        for plugin_name in plugins:
            print(f"  - {plugin_name}")
        
        return {'success': True, 'plugin_count': len(plugins)}
        
    except Exception as e:
        print(f"[FAIL] 插件系統錯誤: {e}")
        return {'success': False, 'error': str(e)}

def run_baseline_tests():
    """運行所有基線測試"""
    print("CLI Tool 基線驗證測試開始")
    print("=" * 50)
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': sys.version,
        'working_directory': os.getcwd()
    }
    
    # 執行各項測試
    results['imports'] = test_module_imports()
    results['external_tools'] = test_external_tools()
    results['config_system'] = test_config_system()
    results['plugin_system'] = test_plugin_system()
    
    print("\n" + "=" * 50)
    print("基線測試完成")
    
    # 統計結果
    total_tests = 0
    passed_tests = 0
    
    if isinstance(results['imports'], dict):
        for module, result in results['imports'].items():
            total_tests += 1
            if result.get('success', False):
                passed_tests += 1
    
    if isinstance(results['external_tools'], dict):
        for tool, result in results['external_tools'].items():
            total_tests += 1
            if result.get('available', False):
                passed_tests += 1
    
    if results['config_system'].get('success', False):
        passed_tests += 1
    total_tests += 1
    
    if results['plugin_system'].get('success', False):
        passed_tests += 1
    total_tests += 1
    
    print(f"\n總測試項目: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"通過率: {passed_tests/total_tests*100:.1f}%")
    
    return results

if __name__ == "__main__":
    baseline_results = run_baseline_tests()