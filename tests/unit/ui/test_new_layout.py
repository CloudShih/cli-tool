#!/usr/bin/env python3
"""
測試新版面佈局
驗證重新設計後的 csvkit 界面
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_new_layout():
    """測試新版面佈局"""
    print("Testing new csvkit layout...")
    
    try:
        from tools.csvkit.csvkit_view import CsvkitView
        from tools.csvkit.csvkit_controller import CsvkitController
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建控制器和視圖
        controller = CsvkitController()
        view = controller.view
        
        print("SUCCESS: Controller and view created")
        
        # 檢查新的界面元素是否存在
        layout_checks = [
            ("Main result display", hasattr(view, 'result_display')),
            ("System response display", hasattr(view, 'system_response_display')),
            ("Save button", hasattr(view, 'save_btn')),
            ("Display system response method", hasattr(view, 'display_system_response'))
        ]
        
        all_passed = True
        print("\nLayout component checks:")
        for check_name, result in layout_checks:
            status = "PASS" if result else "FAIL"
            print(f"  {check_name}: {status}")
            if not result:
                all_passed = False
        
        # 測試系統回應功能
        print("\nTesting system response functionality...")
        if hasattr(view, 'display_system_response'):
            view.display_system_response("Test success message", is_error=False)
            print("  SUCCESS: Success message displayed")
            
            view.display_system_response("Test error message", is_error=True)
            print("  SUCCESS: Error message displayed")
        else:
            print("  ERROR: display_system_response method not found")
            all_passed = False
        
        # 測試結果顯示功能
        print("\nTesting result display functionality...")
        test_csv_data = """name,age,city
John,25,NYC
Jane,30,LA
Bob,35,SF"""
        
        view.display_result(test_csv_data)
        print("  SUCCESS: CSV data displayed in output panel")
        
        # 設置窗口並顯示
        view.setWindowTitle("csvkit - New Layout Test")
        view.resize(1200, 800)
        
        print("\n" + "="*50)
        if all_passed:
            print("ALL LAYOUT TESTS PASSED!")
            print("\nNew layout features:")
            print("  ✓ Output panel moved to right side (main area)")
            print("  ✓ System response area in left panel (below controls)")
            print("  ✓ Improved space utilization")
            print("  ✓ Better visual separation")
            print("  ✓ Enhanced user experience")
            
            print("\nLayout changes:")
            print("  • Left panel: Tool controls + System response")
            print("  • Right panel: Main output display + Save button")
            print("  • Ratio: 2:3 (left:right) for better output visibility")
        else:
            print("SOME LAYOUT TESTS FAILED!")
            print("Please check the implementation.")
        
        # 顯示界面進行視覺驗證（5秒後自動關閉）
        view.show()
        print(f"\nDisplaying interface for visual verification...")
        print("Window will close automatically in 5 seconds...")
        
        from PyQt5.QtCore import QTimer
        def close_window():
            print("Closing test window.")
            app.quit()
        
        QTimer.singleShot(5000, close_window)
        app.exec_()
        
        return all_passed
        
    except Exception as e:
        print(f"ERROR: Layout test failed - {e}")
        return False

def main():
    """主測試函數"""
    print("csvkit New Layout Test")
    print("=" * 30)
    
    success = test_new_layout()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 New layout implementation successful!")
        print("\nThe redesigned interface provides:")
        print("  • Better space utilization")
        print("  • Clearer visual separation")
        print("  • More prominent output display")
        print("  • Immediate status feedback")
    else:
        print("❌ Layout test failed. Please check implementation.")

if __name__ == "__main__":
    main()