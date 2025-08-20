#!/usr/bin/env python3
"""
測試 bat 插件整合到主應用程式
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

def test_plugin_discovery():
    """測試插件發現功能"""
    print("Testing plugin discovery...")
    
    from core.plugin_manager import plugin_manager
    
    # 初始化插件管理器
    plugin_manager.initialize()
    
    # 檢查可用插件
    available_plugins = plugin_manager.get_available_plugins()
    print(f"Available plugins: {list(available_plugins.keys())}")
    
    # 檢查 bat 插件是否被發現
    if 'bat' in available_plugins:
        bat_plugin = available_plugins['bat']
        print(f"[PASS] bat plugin discovered")
        print(f"  Name: {bat_plugin.name}")
        print(f"  Version: {bat_plugin.version}")
        print(f"  Description: {bat_plugin.description}")
        print(f"  Required tools: {bat_plugin.required_tools}")
        print(f"  Tool available: {bat_plugin.check_tools_availability()}")
        
        return True
    else:
        print("[FAIL] bat plugin not discovered")
        return False

def test_plugin_initialization():
    """測試插件初始化"""
    print("\nTesting plugin initialization...")
    
    from core.plugin_manager import plugin_manager
    from tools.bat.plugin import create_plugin
    
    # 創建插件實例
    plugin = create_plugin()
    
    # 檢查初始化
    init_success = plugin.initialize()
    print(f"Plugin initialization: {'PASS' if init_success else 'FAIL'}")
    
    if init_success:
        print(f"  Plugin initialized: {plugin.is_initialized()}")
        
        # 獲取 widget
        widget = plugin.get_widget()
        print(f"  Widget available: {widget is not None}")
        
        if widget:
            print(f"  Widget type: {type(widget).__name__}")
        
        # 清理
        plugin.cleanup()
        print("  Plugin cleanup completed")
        
        return True
    
    return False

def test_main_window_integration():
    """測試主窗口整合"""
    print("\nTesting main window integration...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import ModernMainWindow
        
        # 創建應用程式（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建主窗口（但不顯示）
        main_window = ModernMainWindow()
        
        # 檢查插件視圖是否正確載入
        if hasattr(main_window, 'plugin_views'):
            plugin_views = main_window.plugin_views
            print(f"Plugin views: {list(plugin_views.keys())}")
            
            if 'bat' in plugin_views:
                print("[PASS] bat plugin integrated into main window")
                bat_view = plugin_views['bat']
                print(f"  View type: {type(bat_view).__name__}")
                return True
            else:
                print("[FAIL] bat plugin not found in main window")
                return False
        else:
            print("[FAIL] No plugin views found in main window")
            return False
            
    except Exception as e:
        print(f"[ERROR] Main window integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("Bat Plugin Integration Test")
    print("=" * 50)
    
    tests = [
        ("Plugin Discovery", test_plugin_discovery),
        ("Plugin Initialization", test_plugin_initialization),
        ("Main Window Integration", test_main_window_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Integration Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n*** BAT PLUGIN INTEGRATION SUCCESSFUL ***")
        print("Plugin is ready for production use")
        return True
    else:
        print(f"\n*** {len(results) - passed} INTEGRATION ISSUES NEED ATTENTION ***")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)