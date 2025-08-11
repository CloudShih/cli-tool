#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Debug bat plugin")
    try:
        from tools.bat.bat_model import BatModel
        model = BatModel()
        
        # 簡單測試
        available, version, error = model.check_bat_availability()
        print(f"Available: {available}, Version: {version}")
        
        if available:
            success, html, error = model.highlight_text("print('test')", "python")
            print(f"Highlight success: {success}")
            if success:
                print(f"HTML length: {len(html)}")
                print(f"HTML preview: {html[:200]}...")
            else:
                print(f"Error: {error}")
        
        print("Test completed")
        
    except Exception as e:
        import traceback
        print(f"Exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()