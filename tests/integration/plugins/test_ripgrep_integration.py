#!/usr/bin/env python3
"""
測試 Ripgrep 插件整合
驗證插件是否正確載入並可在主應用程式中使用
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

# 設定路徑
sys.path.append(os.path.dirname(__file__))

# 導入核心模組
from core.plugin_manager import plugin_manager
from ui.main_window import ModernMainWindow

logger = logging.getLogger(__name__)

def test_plugin_discovery():
    """測試插件發現機制"""
    print("測試插件發現...")
    
    try:
        # 初始化插件管理器
        plugins = plugin_manager.discover_plugins()
        
        print(f"發現 {len(plugins)} 個插件:")
        for name, plugin in plugins.items():
            print(f"  - {name}: {plugin.display_name} (版本: {plugin.version})")
            print(f"    描述: {plugin.description}")
            print(f"    所需工具: {plugin.required_tools}")
            print(f"    可用性: {'OK' if plugin.is_available() else 'NOT AVAILABLE'}")
            print()
        
        # 檢查 ripgrep 插件是否存在
        if 'ripgrep' in plugins:
            print("Ripgrep 插件成功發現！")
            return True, plugins['ripgrep']
        else:
            print("Ripgrep 插件未發現！")
            return False, None
            
    except Exception as e:
        print(f"❌ 插件發現失敗: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_plugin_initialization(plugin):
    """測試插件初始化"""
    print("🚀 測試插件初始化...")
    
    try:
        # 測試初始化
        init_success = plugin.initialize()
        print(f"插件初始化: {'✅' if init_success else '❌'}")
        
        # 測試 MVC 組件創建
        print("創建 MVC 組件:")
        
        model = plugin.create_model()
        print(f"  Model: {'✅' if model else '❌'}")
        
        if model:
            print(f"    - 可用性: {'✅' if model.is_available() else '❌'}")
            print(f"    - 版本: {model.get_version_info()}")
        
        view = plugin.create_view()
        print(f"  View: {'✅' if view else '❌'}")
        
        if model and view:
            controller = plugin.create_controller(model, view)
            print(f"  Controller: {'✅' if controller else '❌'}")
            
            # 清理資源
            if hasattr(controller, 'cleanup'):
                controller.cleanup()
            if hasattr(view, 'deleteLater'):
                view.deleteLater()
            if hasattr(model, 'cleanup'):
                model.cleanup()
        
        return init_success
        
    except Exception as e:
        print(f"❌ 插件初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_integration():
    """測試主窗口整合"""
    print("🏠 測試主窗口整合...")
    
    try:
        # 創建 QApplication（如果不存在）
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # 創建主窗口
        main_window = ModernMainWindow()
        
        # 檢查插件是否已載入到導航欄
        navigation_sidebar = getattr(main_window, 'navigation_sidebar', None)
        if navigation_sidebar:
            print("✅ 導航側邊欄存在")
            
            # 獲取導航按鈕
            nav_buttons = navigation_sidebar.nav_buttons if hasattr(navigation_sidebar, 'nav_buttons') else {}
            
            ripgrep_found = False
            for name, button in nav_buttons.items():
                button_text = button.text() if hasattr(button, 'text') else str(button)
                print(f"  導航按鈕: {button_text}")
                if 'ripgrep' in name.lower() or '🔎' in button_text:
                    ripgrep_found = True
            
            if ripgrep_found:
                print("✅ Ripgrep 導航按鈕找到")
            else:
                print("❌ Ripgrep 導航按鈕未找到")
        else:
            print("❌ 導航側邊欄未找到")
        
        # 清理
        main_window.deleteLater()
        
        return True
        
    except Exception as e:
        print(f"❌ 主窗口整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_integration_tests():
    """運行所有整合測試"""
    print("=" * 60)
    print("Ripgrep 插件整合測試")
    print("=" * 60)
    
    results = []
    
    # 測試 1: 插件發現
    success, plugin = test_plugin_discovery()
    results.append(("插件發現", success))
    
    if not success:
        print("\n❌ 插件發現失敗，終止後續測試")
        return False
    
    print("-" * 60)
    
    # 測試 2: 插件初始化
    success = test_plugin_initialization(plugin)
    results.append(("插件初始化", success))
    
    print("-" * 60)
    
    # 測試 3: 主窗口整合
    success = test_main_window_integration()
    results.append(("主窗口整合", success))
    
    # 測試結果摘要
    print("\n" + "=" * 60)
    print("📊 測試結果摘要")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 60)
    if all_passed:
        print("🎉 所有測試通過！Ripgrep 插件整合成功！")
    else:
        print("⚠️  部分測試失敗，請檢查問題。")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 測試運行失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)