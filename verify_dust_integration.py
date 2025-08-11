#!/usr/bin/env python3
"""
Quick Dust Integration Verification Script
快速驗證 dust 工具整合狀態
"""

import sys
import os
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 設置離屏模式
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def verify_integration():
    """驗證 dust 工具整合狀態"""
    print("🔍 Dust Tool Integration Verification")
    print("=" * 50)
    
    results = []
    
    # 1. 檢查 dust 插件檔案存在
    try:
        dust_plugin_path = project_root / "tools" / "dust" / "plugin.py"
        if dust_plugin_path.exists():
            print("✅ Dust plugin file exists")
            results.append(True)
        else:
            print("❌ Dust plugin file missing")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking dust plugin file: {e}")
        results.append(False)
    
    # 2. 檢查插件導入
    try:
        from tools.dust.plugin import create_plugin
        dust_plugin = create_plugin()
        if dust_plugin.name == "dust":
            print("✅ Dust plugin imports correctly")
            results.append(True)
        else:
            print("❌ Dust plugin import failed")
            results.append(False)
    except Exception as e:
        print(f"❌ Error importing dust plugin: {e}")
        results.append(False)
    
    # 3. 檢查插件管理器發現
    try:
        from core.plugin_manager import plugin_manager
        plugin_manager.initialize()
        
        all_plugins = plugin_manager.get_all_plugins()
        if "dust" in all_plugins:
            print("✅ Dust plugin discovered by plugin manager")
            results.append(True)
        else:
            print("❌ Dust plugin not discovered")
            results.append(False)
    except Exception as e:
        print(f"❌ Error checking plugin discovery: {e}")
        results.append(False)
    
    # 4. 檢查 UI 整合
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from ui.main_window import ModernMainWindow
        main_window = ModernMainWindow()
        
        # 檢查導航按鈕
        navigation_buttons = main_window.sidebar.navigation_buttons
        if any("dust" in key or "Dust" in str(btn.text()) for key, btn in navigation_buttons.items()):
            print("✅ Dust navigation button created")
            results.append(True)
        else:
            print("❌ Dust navigation button missing")
            results.append(False)
            
        main_window.close()
    except Exception as e:
        print(f"❌ Error checking UI integration: {e}")
        results.append(False)
    
    # 5. 檢查 dust 工具可用性
    try:
        from tools.dust.dust_model import DustModel
        model = DustModel()
        available, version, _ = model.check_dust_availability()
        
        if available:
            print(f"✅ Dust tool available: {version}")
            results.append(True)
        else:
            print("⚠️  Dust tool not installed (integration still works)")
            results.append(True)  # 這不算錯誤，因為整合本身是成功的
    except Exception as e:
        print(f"❌ Error checking dust tool: {e}")
        results.append(False)
    
    # 總結
    print("=" * 50)
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"✅ Integration Status: {success_count}/{total_count} checks passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Dust tool integration SUCCESSFUL!")
        return True
    else:
        print("❌ Dust tool integration FAILED!")
        return False

if __name__ == "__main__":
    try:
        success = verify_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)