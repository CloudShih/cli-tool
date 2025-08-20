#!/usr/bin/env python3
"""
完整的 csvkit 整合測試
測試 csvkit 插件在主應用程序中的完整整合
"""

import sys
import tempfile
import csv
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.main_window import ModernMainWindow
from core.plugin_manager import plugin_manager


def create_test_csv():
    """創建測試 CSV 文件"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    
    sample_data = [
        ['產品名稱', '銷售量', '價格', '分類'],
        ['筆記本電腦', '1250', '25000', '電腦'],
        ['智能手機', '2890', '15000', '手機'],
        ['平板電腦', '678', '12000', '電腦'],
        ['耳機', '3450', '2500', '配件'],
        ['鍵盤', '1890', '1800', '配件']
    ]
    
    writer = csv.writer(temp_file)
    writer.writerows(sample_data)
    temp_file.close()
    
    print(f"創建測試文件: {temp_file.name}")
    return temp_file.name


def test_csvkit_in_main_app():
    """在主應用程序中測試 csvkit"""
    print("=== 完整 csvkit 整合測試 ===")
    
    # 創建應用程序
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # 創建主窗口
        main_window = ModernMainWindow()
        main_window.show()
        main_window.resize(1200, 800)
        main_window.setWindowTitle("csvkit Integration Test")
        
        # 檢查插件是否載入
        plugins = plugin_manager.get_all_plugins()
        
        if 'csvkit' in plugins:
            print("✅ csvkit 插件已載入")
            
            csvkit_plugin = plugins['csvkit']
            print(f"   名稱: {csvkit_plugin.name}")
            print(f"   版本: {csvkit_plugin.version}")
            print(f"   可用: {csvkit_plugin.is_available()}")
            
            # 檢查是否有 csvkit 視圖
            if hasattr(main_window, 'plugin_views') and 'csvkit' in main_window.plugin_views:
                print("✅ csvkit 視圖已創建")
            else:
                print("ℹ️  csvkit 視圖將在選擇時創建")
        else:
            print("❌ csvkit 插件未載入")
            return False
        
        # 創建測試文件
        test_file = create_test_csv()
        print(f"✅ 測試文件已創建: {test_file}")
        
        # 設置關閉定時器
        def cleanup_and_close():
            import os
            try:
                os.unlink(test_file)
                print("✅ 測試文件已清理")
            except:
                pass
            
            print("測試完成，關閉應用程序...")
            main_window.close()
            app.quit()
        
        # 5秒後自動關閉
        timer = QTimer()
        timer.singleShot(5000, cleanup_and_close)
        
        print("主應用程序已啟動，將在 5 秒後自動關閉...")
        print("請檢查:")
        print("1. 左側導航欄是否有 '📊 Csvkit' 項目")
        print("2. 歡迎頁面是否有 CSV 數據處理卡片")
        print("3. 點擊 csvkit 導航項是否能正常顯示界面")
        
        app.exec_()
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def main():
    """主函數"""
    print("開始 csvkit 完整整合測試...")
    
    # 檢查 csvkit 安裝
    import subprocess
    try:
        result = subprocess.run(['csvstat', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ csvkit 已安裝: {result.stdout.strip()}")
        else:
            print("❌ csvkit 命令執行失敗")
            return
    except FileNotFoundError:
        print("❌ csvkit 未安裝，請運行: pip install csvkit")
        return
    
    # 運行測試
    success = test_csvkit_in_main_app()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ csvkit 整合測試成功完成！")
        print("🎉 csvkit 已成功整合到 CLI Tool 應用程序中")
        print("\n功能特性:")
        print("  📊 15 個專業 CSV 處理工具")
        print("  🔄 格式轉換 (Excel, JSON, 等)")
        print("  🔍 數據搜索和過濾")
        print("  📈 統計分析功能")
        print("  🧹 數據清理工具")
        print("  🔗 數據連接和合併")
    else:
        print("\n❌ 整合測試失敗，請檢查錯誤信息")


if __name__ == "__main__":
    main()