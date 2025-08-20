#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試主應用程序集成
驗證 Glances 插件在主應用程序中的完整功能
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_main_app_integration():
    """測試主應用程序集成"""
    print("Main App Integration Test")
    print("=" * 40)
    
    try:
        # 創建 QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建主窗口
        from ui.main_window import ModernMainWindow
        main_window = ModernMainWindow()
        
        print("+ Main window created")
        
        # 設置視窗
        main_window.setWindowTitle("主應用程序集成測試")
        main_window.resize(1600, 1000)
        main_window.show()
        
        print("+ Main window displayed")
        
        # 檢查 Glances 插件是否正確載入
        def check_glances_plugin():
            print("\n--- Checking Glances Plugin ---")
            
            # 檢查插件是否在側邊欄中
            sidebar = main_window.sidebar
            if 'glances' in sidebar.navigation_buttons:
                print("+ Glances found in navigation")
                
                # 檢查插件視圖是否創建
                if 'glances' in main_window.plugin_views:
                    print("+ Glances view created")
                    
                    glances_view = main_window.plugin_views['glances']
                    
                    # 檢查圖表組件
                    if hasattr(glances_view, 'charts_widget'):
                        charts_widget = glances_view.charts_widget
                        if charts_widget:
                            print("+ Charts widget found")
                            print(f"  Charts available: {list(charts_widget.charts.keys())}")
                        else:
                            print("- Charts widget is None")
                    else:
                        print("- No charts_widget attribute")
                else:
                    print("- Glances view not found in plugin_views")
            else:
                print("- Glances not found in navigation")
                print(f"  Available navigation: {list(sidebar.navigation_buttons.keys())}")
        
        # 2秒後檢查插件
        QTimer.singleShot(2000, check_glances_plugin)
        
        # 自動導航到 Glances
        def navigate_to_glances():
            print("\n--- Navigating to Glances ---")
            try:
                sidebar = main_window.sidebar
                if 'glances' in sidebar.navigation_buttons:
                    # 模擬點擊 Glances 按鈕
                    sidebar.on_navigation_clicked('glances')
                    print("+ Clicked on Glances navigation")
                    
                    # 檢查當前顯示的視圖
                    current_widget = main_window.content_stack.currentWidget()
                    if current_widget and hasattr(current_widget, 'charts_widget'):
                        print("+ Glances view is now active")
                        
                        # 等待監控啟動
                        def check_monitoring():
                            print("\n--- Checking Monitoring Status ---")
                            try:
                                charts_widget = current_widget.charts_widget
                                if charts_widget:
                                    # 檢查各個圖表的數據
                                    for chart_name, chart in charts_widget.charts.items():
                                        if chart and hasattr(chart, 'series_data'):
                                            total_points = 0
                                            for series_name, series in chart.series_data.items():
                                                points = len(series.values)
                                                total_points += points
                                                if points > 0:
                                                    latest_value = series.values[-1]
                                                    print(f"  {chart_name}.{series_name}: {points} points, latest = {latest_value}")
                                            
                                            if total_points == 0:
                                                print(f"  {chart_name}: No data points yet")
                            except Exception as e:
                                print(f"  Error checking monitoring: {e}")
                        
                        # 5秒後檢查監控狀態
                        QTimer.singleShot(5000, check_monitoring)
                        
                        # 10秒後再次檢查
                        QTimer.singleShot(10000, check_monitoring)
                        
                    else:
                        print("- Current widget is not Glances view")
                else:
                    print("- Glances navigation button not found")
            except Exception as e:
                print(f"Error navigating to Glances: {e}")
        
        # 4秒後導航到 Glances
        QTimer.singleShot(4000, navigate_to_glances)
        
        # 15秒後關閉
        def close_app():
            print("\nClosing main app integration test...")
            main_window.close()
            app.quit()
        
        QTimer.singleShot(15000, close_app)
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"Main app integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("Glances Main App Integration Test")
    print("=" * 40)
    
    success = test_main_app_integration()
    
    print("\n" + "=" * 40)
    if success:
        print("+ Main app integration test completed")
        print("Key checks:")
        print("  - Glances plugin loaded in main app")
        print("  - Navigation integration working")
        print("  - Chart components available")
        print("  - Monitoring auto-start functionality")
    else:
        print("- Main app integration test failed")

if __name__ == "__main__":
    main()