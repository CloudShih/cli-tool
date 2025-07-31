#!/usr/bin/env python3
"""
CLI Tool 簡化驗證腳本 (無 emoji 版本)
測試所有優化功能是否正常工作
"""

import sys
import os
import json
import logging
from pathlib import Path

# 確保專案根目錄在 Python 路徑中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_management():
    """測試配置管理系統"""
    print("[CONFIG] 測試配置管理系統...")
    
    try:
        from config.config_manager import config_manager
        
        # 測試基本配置讀取
        fd_config = config_manager.get_tool_config('fd')
        print(f"  [OK] fd 配置讀取成功: {fd_config.get('executable_path', 'N/A')}")
        
        # 測試配置設定和保存
        test_key = 'test.value'
        test_value = 'test_data'
        config_manager.set(test_key, test_value)
        retrieved_value = config_manager.get(test_key)
        
        if retrieved_value == test_value:
            print("  [OK] 配置設定和讀取功能正常")
        else:
            print("  [FAIL] 配置設定功能異常")
            
        # 測試資源路徑處理
        resource_path = config_manager.get_resource_path("config/cli_tool_config.json")
        if resource_path.exists():
            print("  [OK] 資源路徑處理正常")
        else:
            print("  [FAIL] 資源路徑處理異常")
            
        return True
        
    except Exception as e:
        print(f"  [FAIL] 配置管理系統測試失敗: {e}")
        return False

def test_plugin_system():
    """測試插件系統"""
    print("[PLUGIN] 測試插件系統...")
    
    try:
        from core.plugin_manager import plugin_manager
        
        # 測試插件發現（不初始化完整系統）
        plugin_manager.discover_plugins()
        
        # 檢查插件發現
        all_plugins = plugin_manager.get_all_plugins()
        print(f"  [INFO] 發現插件數量: {len(all_plugins)}")
        
        for name, plugin in all_plugins.items():
            print(f"    - {name}: {plugin.description} (v{plugin.version})")
        
        # 測試插件基本屬性
        for name, plugin in all_plugins.items():
            print(f"  [TEST] 測試插件 '{name}':")
            print(f"    版本: {plugin.version}")
            print(f"    描述: {plugin.description}")
            print(f"    所需工具: {', '.join(plugin.required_tools)}")
            
            # 測試工具可用性檢查（不創建視圖）
            is_available = plugin.is_available()
            status = "[OK] 可用" if is_available else "[WARN] 不可用"
            print(f"    狀態: {status}")
        
        if len(all_plugins) > 0:
            print("  [OK] 插件系統基本功能正常")
            return True
        else:
            print("  [FAIL] 沒有發現任何插件")
            return False
            
    except Exception as e:
        print(f"  [FAIL] 插件系統測試失敗: {e}")
        return False

def test_import_fixes():
    """測試匯入修復"""
    print("[IMPORT] 測試絕對匯入...")
    
    try:
        # 測試工具模組匯入
        from tools.fd.fd_model import FdModel
        from tools.fd.fd_view import FdView
        from tools.fd.fd_controller import FdController
        print("  [OK] fd 模組絕對匯入成功")
        
        from tools.poppler.poppler_model import PopplerModel
        from tools.poppler.poppler_view import PopplerView
        from tools.poppler.poppler_controller import PopplerController
        print("  [OK] poppler 模組絕對匯入成功")
        
        # 測試插件匯入
        from tools.fd.plugin import FdPlugin
        from tools.poppler.plugin import PopplerPlugin
        print("  [OK] 插件模組絕對匯入成功")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] 絕對匯入測試失敗: {e}")
        return False

def test_dependencies():
    """測試依賴安裝"""
    print("[DEPS] 測試依賴安裝...")
    
    # 修正的依賴檢測方式
    dependencies = {
        'PyQt5': ['PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui'],
        'ansi2html': ['ansi2html'],
        'pikepdf': ['pikepdf']
    }
    
    all_installed = True
    for package_name, import_names in dependencies.items():
        try:
            # 嘗試匯入主要模組
            for import_name in import_names:
                __import__(import_name)
            print(f"  [OK] {package_name} 已安裝")
        except ImportError as e:
            print(f"  [FAIL] {package_name} 未安裝: {e}")
            all_installed = False
            break
    
    return all_installed

def test_project_structure():
    """測試專案結構"""
    print("[STRUCT] 測試專案結構...")
    
    required_files = [
        'main_app.py',
        'run.py',
        'build.py',
        'cli_tool.spec',
        'setup.py',
        'requirements.txt',
        'config/config_manager.py',
        'config/cli_tool_config.json',
        'core/plugin_manager.py',
        'tools/fd/plugin.py',
        'tools/poppler/plugin.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [FAIL] {file_path}")
            all_exist = False
    
    return all_exist

def test_configuration_files():
    """測試配置文件格式"""
    print("[CONFIG_FILE] 測試配置文件...")
    
    try:
        config_file = project_root / 'config' / 'cli_tool_config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 檢查必需的配置項
        required_sections = ['tools', 'ui', 'general']
        for section in required_sections:
            if section in config_data:
                print(f"  [OK] 配置區段 '{section}' 存在")
            else:
                print(f"  [FAIL] 配置區段 '{section}' 缺失")
                return False
        
        # 檢查工具配置
        if 'fd' in config_data['tools'] and 'poppler' in config_data['tools']:
            print("  [OK] 工具配置完整")
        else:
            print("  [FAIL] 工具配置不完整")
            return False
            
        return True
        
    except Exception as e:
        print(f"  [FAIL] 配置文件測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("CLI Tool 優化驗證開始")
    print("=" * 50)
    
    tests = [
        ('專案結構', test_project_structure),
        ('依賴安裝', test_dependencies),
        ('配置文件', test_configuration_files),
        ('絕對匯入', test_import_fixes),
        ('配置管理', test_config_management),
        ('插件系統', test_plugin_system),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n[TEST] 執行測試: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"[PASS] {test_name} 測試通過")
            else:
                failed += 1
                print(f"[FAIL] {test_name} 測試失敗")
        except Exception as e:
            failed += 1
            print(f"[ERROR] {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"測試結果: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("所有優化測試通過！CLI Tool 已成功優化。")
        return 0
    else:
        print("部分測試失敗，請檢查相關配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main())