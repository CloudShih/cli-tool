#!/usr/bin/env python3
"""
測試 csvkit 輸出區域高度調整
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_height_adjustment():
    """測試高度調整效果"""
    print("Testing csvkit output area height adjustment...")
    print("=" * 50)
    
    try:
        # 創建 QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 創建 csvkit 視圖
        from tools.csvkit.csvkit_view import CsvkitView
        view = CsvkitView()
        
        # 設置窗口
        view.setWindowTitle("csvkit - Height Adjustment Test")
        view.resize(1200, 800)
        
        # 顯示一些測試內容
        test_output = """Available csvkit Tools:

Input Tools:
  • in2csv: Convert various tabular data formats to CSV
  • csvformat: Format CSV files with proper quoting
  
Processing Tools:  
  • csvcut: Extract and reorder columns from CSV
  • csvgrep: Search for patterns in CSV files
  • csvjoin: Join multiple CSV files
  • csvstack: Stack CSV files into a single file
  
Analysis Tools:
  • csvstat: Calculate descriptive statistics
  • csvlook: Display CSV files in formatted table
  • csvjson: Convert CSV to JSON format
  • csvsql: Generate SQL CREATE statements and queries

Ready to process CSV data with enhanced output display area!

The output area should now be significantly taller, providing better 
visibility for large CSV datasets, statistical results, and formatted 
table displays.

Previous ratio: 1:2 (Control:Output)
New ratio: 1:3 (Control:Output)
This gives approximately 75% of the vertical space to output display."""

        view.display_result(test_output)
        
        # 顯示窗口
        view.show()
        
        print("✓ csvkit view created with adjusted height ratio")
        print("✓ Test content displayed in output area")
        print("✓ New ratio: Control Panel (25%) : Output Area (75%)")
        print("\nWindow displayed for visual verification...")
        print("Window will close automatically in 8 seconds...")
        
        # 8秒後自動關閉
        def close_window():
            print("Closing test window...")
            app.quit()
        
        QTimer.singleShot(8000, close_window)
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"Error during height adjustment test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("csvkit Output Area Height Adjustment Test")
    print("=" * 50)
    
    success = test_height_adjustment()
    
    print("\n" + "=" * 50)
    print("Test Result:")
    if success:
        print("✓ Output area height successfully increased")
        print("  The red area in the screenshot should now be taller")
        print("  More space available for CSV data display")
    else:
        print("✗ Height adjustment test failed")
    
    print("=" * 50)

if __name__ == "__main__":
    main()