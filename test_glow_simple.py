#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glow 插件簡化測試腳本
"""

import sys
import os
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """測試模組匯入"""
    print("測試模組匯入...")
    
    try:
        from tools.glow.glow_model import GlowModel
        print("成功匯入 GlowModel")
        
        from tools.glow.glow_view import GlowView
        print("成功匯入 GlowView")
        
        from tools.glow.glow_controller import GlowController
        print("成功匯入 GlowController")
        
        from tools.glow.plugin import GlowPlugin
        print("成功匯入 GlowPlugin")
        
        return True
        
    except Exception as e:
        print(f"模組匯入失敗: {e}")
        return False

def test_plugin_creation():
    """測試插件創建"""
    print("\n測試插件創建...")
    
    try:
        from tools.glow.plugin import GlowPlugin
        
        plugin = GlowPlugin()
        print(f"插件名稱: {plugin.name}")
        print(f"顯示名稱: {plugin.get_display_name()}")
        print(f"版本: {plugin.version}")
        print(f"描述: {plugin.description}")
        
        # 測試工具檢查
        available = plugin.check_tools_availability()
        print(f"Glow 工具可用性: {available}")
        
        return True
        
    except Exception as e:
        print(f"插件創建失敗: {e}")
        return False

def test_model_basic():
    """測試模型基本功能"""
    print("\n測試模型基本功能...")
    
    try:
        from tools.glow.glow_model import GlowModel
        
        model = GlowModel()
        print("GlowModel 創建成功")
        
        # 測試 Glow 可用性
        available, version, error = model.check_glow_availability()
        if available:
            print(f"Glow 可用: {version}")
        else:
            print(f"Glow 不可用: {error}")
        
        # 測試 URL 驗證
        valid, url, error = model.validate_url("microsoft/terminal")
        if valid:
            print(f"URL 驗證成功: {url}")
        else:
            print(f"URL 驗證失敗: {error}")
        
        return True
        
    except Exception as e:
        print(f"模型測試失敗: {e}")
        return False

def main():
    """主函式"""
    print("Glow 插件測試開始")
    print("=" * 40)
    
    tests = [
        ("模組匯入", test_imports),
        ("插件創建", test_plugin_creation),
        ("模型功能", test_model_basic),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n執行測試: {name}")
        print("-" * 20)
        
        if test_func():
            print(f"{name} 測試通過")
            passed += 1
        else:
            print(f"{name} 測試失敗")
    
    print("\n" + "=" * 40)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("所有測試通過！")
        return 0
    else:
        print("部分測試失敗。")
        return 1

if __name__ == "__main__":
    sys.exit(main())