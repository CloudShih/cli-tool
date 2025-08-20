#!/usr/bin/env python3
"""
測試主窗口插件載入過程
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_plugin_loading_process():
    """測試插件載入過程，模擬主窗口行為"""
    print("Testing main window plugin loading process...")
    print("=" * 50)
    
    try:
        # 創建 QApplication（模擬主窗口環境）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("1. Importing plugin manager...")
        from core.plugin_manager import plugin_manager
        
        print("2. Discovering plugins...")
        plugin_manager.discover_plugins()
        
        print("3. Getting available plugins...")
        available_plugins = plugin_manager.get_available_plugins()
        print(f"   Available plugins: {list(available_plugins.keys())}")
        
        print("4. Creating plugin views (simulating main window behavior)...")
        plugin_views = {}
        
        for plugin_name, plugin in available_plugins.items():
            try:
                print(f"   Processing plugin: {plugin_name}")
                
                # 在主線程中創建 MVC 組件（模擬主窗口邏輯）
                model = plugin.create_model()
                print(f"     - Model created: {type(model).__name__}")
                
                view = plugin.create_view()
                print(f"     - View created: {type(view).__name__}")
                
                controller = plugin.create_controller(model, view)
                print(f"     - Controller created: {type(controller).__name__}")
                
                # 保存到插件管理器實例（模擬主窗口邏輯）
                plugin_manager.plugin_instances[plugin_name] = {
                    'plugin': plugin,
                    'model': model,
                    'view': view,
                    'controller': controller
                }
                
                # 添加到主窗口視圖字典（模擬主窗口邏輯）
                plugin_views[plugin_name] = view
                
                print(f"     ✓ {plugin_name} plugin loaded successfully")
                
            except Exception as e:
                print(f"     ✗ Error creating view for plugin {plugin_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n5. Final plugin views count: {len(plugin_views)}")
        print(f"   Plugin views keys: {list(plugin_views.keys())}")
        
        # 檢查 csvkit 是否在其中
        if 'csvkit' in plugin_views:
            print("   ✓ csvkit view successfully added to plugin_views")
            csvkit_view = plugin_views['csvkit']
            print(f"   ✓ csvkit view type: {type(csvkit_view).__name__}")
        else:
            print("   ✗ csvkit view NOT found in plugin_views")
        
        print("\n" + "=" * 50)
        print("Plugin loading simulation completed!")
        
        return 'csvkit' in plugin_views
        
    except Exception as e:
        print(f"Error during plugin loading simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("Main Window Plugin Loading Test")
    print("=" * 50)
    
    success = test_plugin_loading_process()
    
    print("\n" + "=" * 50)
    print("Test Result:")
    if success:
        print("✓ csvkit plugin should be accessible in main window")
        print("  The navigation warning should not occur")
    else:
        print("✗ csvkit plugin loading failed")
        print("  This explains the navigation warning")
    
    print("=" * 50)

if __name__ == "__main__":
    main()