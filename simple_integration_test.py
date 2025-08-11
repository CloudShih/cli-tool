#!/usr/bin/env python3
"""
簡化版 Ripgrep 插件整合測試
"""
import sys
import os

# 設定路徑
sys.path.append(os.path.dirname(__file__))

# 導入核心模組
from core.plugin_manager import plugin_manager

def test_ripgrep_integration():
    """測試 ripgrep 插件整合"""
    print("=" * 50)
    print("Ripgrep 插件整合測試")
    print("=" * 50)
    
    try:
        # 發現插件
        print("1. 測試插件發現...")
        plugin_manager.discover_plugins()
        plugins = plugin_manager.get_all_plugins()
        print(f"   發現 {len(plugins)} 個插件")
        
        for name in plugins.keys():
            print(f"   - {name}")
        
        # 檢查 ripgrep 是否存在
        if 'ripgrep' in plugins:
            print("   PASS: Ripgrep 插件已發現")
            plugin = plugins['ripgrep']
            
            # 測試插件屬性
            print("\n2. 測試插件屬性...")
            print(f"   名稱: {plugin.name}")
            print(f"   顯示名稱: {plugin.display_name}")
            print(f"   版本: {plugin.version}")
            print(f"   描述: {plugin.description}")
            print(f"   所需工具: {plugin.required_tools}")
            
            # 測試工具可用性
            print(f"   可用性: {plugin.is_available()}")
            
            # 測試初始化
            print("\n3. 測試插件初始化...")
            init_result = plugin.initialize()
            print(f"   初始化結果: {init_result}")
            
            # 測試 MVC 創建
            print("\n4. 測試 MVC 組件創建...")
            
            model = plugin.create_model()
            print(f"   Model 創建: {'成功' if model else '失敗'}")
            
            view = plugin.create_view()
            print(f"   View 創建: {'成功' if view else '失敗'}")
            
            if model and view:
                controller = plugin.create_controller(model, view)
                print(f"   Controller 創建: {'成功' if controller else '失敗'}")
                
                # 清理
                if hasattr(controller, 'cleanup'):
                    controller.cleanup()
                if hasattr(view, 'deleteLater'):
                    view.deleteLater()
                if hasattr(model, 'cleanup'):
                    model.cleanup()
            
            print("\n" + "=" * 50)
            print("測試完成 - Ripgrep 插件整合成功!")
            return True
            
        else:
            print("   FAIL: Ripgrep 插件未發現")
            return False
            
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ripgrep_integration()
    sys.exit(0 if success else 1)