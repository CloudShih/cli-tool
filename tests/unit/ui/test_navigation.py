#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試主應用程序導航中是否包含 Glances
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_navigation():
    """測試導航功能"""
    print("Testing navigation functionality...")
    
    try:
        # 導入並初始化插件管理器
        from core.plugin_manager import plugin_manager
        
        print("1. Initializing plugin manager...")
        plugin_manager.initialize()
        
        print("2. Getting available plugins...")
        available_plugins = plugin_manager.get_available_plugins()
        print(f"   Available plugins: {list(available_plugins.keys())}")
        
        print("3. Getting all plugins...")
        all_plugins = plugin_manager.get_all_plugins()
        print(f"   All plugins: {list(all_plugins.keys())}")
        
        # 檢查 Glances
        if 'glances' in available_plugins:
            print("✅ Glances plugin found in available plugins!")
            glances_plugin = available_plugins['glances']
            print(f"   Name: {glances_plugin.name}")
            print(f"   Version: {glances_plugin.version}")
            print(f"   Description: {glances_plugin.description}")
        else:
            print("❌ Glances plugin NOT found in available plugins")
            
        if 'glances' in all_plugins:
            print("✅ Glances plugin found in all plugins!")
        else:
            print("❌ Glances plugin NOT found in all plugins")
            
        return 'glances' in available_plugins
        
    except Exception as e:
        print(f"❌ Error during navigation test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Navigation Test")
    print("=" * 50)
    success = test_navigation()
    print("=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")