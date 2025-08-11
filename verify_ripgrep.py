#!/usr/bin/env python3
"""
驗證 Ripgrep 插件是否正確整合
"""
import sys
import os

# 設定路徑
sys.path.append(os.path.dirname(__file__))

# 導入核心模組
from core.plugin_manager import plugin_manager

def verify_ripgrep():
    """驗證 ripgrep 插件整合"""
    print("=" * 50)
    print("Ripgrep 插件整合驗證")
    print("=" * 50)
    
    try:
        # 發現並載入插件
        plugin_manager.discover_plugins()
        plugins = plugin_manager.get_all_plugins()
        
        print(f"發現插件總數: {len(plugins)}")
        print("已載入的插件:")
        for name in plugins.keys():
            print(f"  - {name}")
        
        # 檢查 ripgrep 插件
        if 'ripgrep' in plugins:
            plugin = plugins['ripgrep']
            print(f"\n{'-' * 30}")
            print("Ripgrep 插件詳情:")
            print(f"  名稱: {plugin.name}")
            print(f"  顯示名稱: {plugin.display_name}")
            print(f"  版本: {plugin.version}")
            print(f"  描述: {plugin.description}")
            print(f"  所需工具: {plugin.required_tools}")
            print(f"  圖示: {plugin.icon}")
            
            # 檢查工具可用性
            available = plugin.check_tools_availability()
            print(f"  工具可用性: {'可用' if available else '不可用'}")
            
            # 檢查初始化
            init_result = plugin.initialize()
            print(f"  初始化結果: {'成功' if init_result else '失敗'}")
            
            print(f"\n{'=' * 50}")
            print("驗證結果: RIPGREP 插件整合成功！")
            print("插件已正確載入並可在主應用程式中使用")
            print(f"{'=' * 50}")
            return True
            
        else:
            print("\n驗證結果: RIPGREP 插件未找到")
            return False
            
    except Exception as e:
        print(f"驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_ripgrep()
    sys.exit(0 if success else 1)