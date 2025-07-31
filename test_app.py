#!/usr/bin/env python3
"""
CLI Tool 應用程式功能測試
在安全的環境中測試 GUI 相關功能
"""

import sys
import os
from pathlib import Path

# 確保專案根目錄在 Python 路徑中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_components():
    """測試 GUI 組件（需要顯示環境）"""
    print("🖥️  測試 GUI 組件...")
    
    try:
        # 檢查是否有顯示環境
        if os.environ.get('DISPLAY') is None and sys.platform.startswith('linux'):
            print("  ⚠️  Linux 環境下未檢測到 DISPLAY，跳過 GUI 測試")
            return True
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        # 創建 QApplication 實例
        app = QApplication(sys.argv)
        
        # 測試配置管理和插件系統
        from config.config_manager import config_manager
        from core.plugin_manager import plugin_manager
        
        print("  ✅ 配置管理器初始化成功")
        
        # 初始化插件管理器
        plugin_manager.initialize()
        print(f"  ✅ 插件管理器初始化成功，載入 {len(plugin_manager.get_all_plugins())} 個插件")
        
        # 測試主應用程式類
        from main_app import CLIToolApp
        
        # 創建主應用程式實例（但不顯示）
        main_window = CLIToolApp()
        print("  ✅ 主應用程式實例創建成功")
        
        # 檢查標籤頁是否正確添加
        tab_count = main_window.tabs.count()
        print(f"  ✅ 標籤頁數量: {tab_count}")
        
        # 清理資源
        plugin_manager.cleanup()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"  ❌ GUI 組件測試失敗: {e}")
        return False

def test_command_line_mode():
    """測試命令行模式功能"""
    print("💻 測試命令行模式...")
    
    try:
        # 測試配置管理器
        from config.config_manager import config_manager
        
        print("  ✅ 配置管理器匯入成功")
        
        # 測試插件發現
        from core.plugin_manager import plugin_manager
        plugin_manager.discover_plugins()
        
        plugins = plugin_manager.get_all_plugins()
        print(f"  ✅ 發現 {len(plugins)} 個插件")
        
        for name, plugin in plugins.items():
            print(f"    - {name}: {plugin.description}")
            print(f"      狀態: {'可用' if plugin.is_available() else '不可用'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 命令行模式測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 CLI Tool 應用程式測試開始")
    print("=" * 50)
    
    tests = [
        ('命令行模式', test_command_line_mode),
    ]
    
    # 只在有GUI環境時測試GUI組件
    if '--gui' in sys.argv or os.environ.get('DISPLAY') is not None or sys.platform == 'win32':
        tests.append(('GUI 組件', test_gui_components))
    else:
        print("💡 提示: 使用 --gui 參數在有顯示環境時測試 GUI 功能")
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📝 執行測試: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                failed += 1
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("🎉 應用程式測試通過！")
        return 0
    else:
        print("⚠️  部分測試失敗，請檢查相關配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main())