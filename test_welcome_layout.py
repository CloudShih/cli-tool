#!/usr/bin/env python3
"""
測試歡迎頁面新佈局
檢查工具卡片是否正確排列為 3x2 網格
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 設置路徑
sys.path.append('.')

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_welcome_layout():
    """測試歡迎頁面佈局"""
    try:
        # 創建應用程式
        app = QApplication([])
        
        # 導入主窗口類
        from ui.welcome_page import WelcomePage
        
        # 創建歡迎頁面實例
        welcome_page = WelcomePage()
        
        # 檢查佈局結構
        main_layout = welcome_page.layout()
        print("[PASS] 歡迎頁面創建成功")
        
        # 查找功能卡片容器
        features_container = None
        for i in range(main_layout.count()):
            item = main_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.layout() and hasattr(widget.layout(), 'rowCount'):
                    features_container = widget
                    break
        
        if features_container:
            grid_layout = features_container.layout()
            print("[PASS] 找到網格佈局容器")
            print(f"   - 行數: {grid_layout.rowCount()}")
            print(f"   - 列數: {grid_layout.columnCount()}")
            print(f"   - 總卡片數: {grid_layout.count()}")
            
            # 檢查預期的 3x2 佈局
            expected_rows = 2
            expected_cols = 3
            expected_cards = 6
            
            actual_rows = grid_layout.rowCount()
            actual_cols = grid_layout.columnCount() 
            actual_cards = grid_layout.count()
            
            if actual_rows == expected_rows:
                print(f"[PASS] 行數正確: {actual_rows}")
            else:
                print(f"[FAIL] 行數錯誤: 預期 {expected_rows}, 實際 {actual_rows}")
                
            if actual_cols == expected_cols:
                print(f"[PASS] 列數正確: {actual_cols}")
            else:
                print(f"[FAIL] 列數錯誤: 預期 {expected_cols}, 實際 {actual_cols}")
                
            if actual_cards == expected_cards:
                print(f"[PASS] 卡片數正確: {actual_cards}")
            else:
                print(f"[FAIL] 卡片數錯誤: 預期 {expected_cards}, 實際 {actual_cards}")
            
            # 檢查間距設置
            vertical_spacing = grid_layout.verticalSpacing()
            horizontal_spacing = grid_layout.horizontalSpacing()
            print("[PASS] 佈局間距:")
            print(f"   - 垂直間距: {vertical_spacing}px")
            print(f"   - 水平間距: {horizontal_spacing}px")
            
            # 檢查每個卡片的位置
            print("[PASS] 卡片位置檢查:")
            card_titles = ["檔案搜尋", "Markdown 閱讀器", "文檔轉換", "PDF 處理", "語法高亮查看器", "主題設定"]
            
            for i in range(min(actual_cards, 6)):
                row = i // 3
                col = i % 3
                item = grid_layout.itemAtPosition(row, col)
                if item and item.widget():
                    widget = item.widget()
                    print(f"   - 位置 ({row}, {col}): 卡片存在 [PASS]")
                else:
                    print(f"   - 位置 ({row}, {col}): 卡片缺失 [FAIL]")
            
            print("\n[INFO] 佈局測試完成！")
            print("=" * 50)
            print("總結:")
            if (actual_rows == expected_rows and 
                actual_cols == expected_cols and 
                actual_cards == expected_cards):
                print("[SUCCESS] 所有佈局檢查通過 - 新的 3x2 網格佈局運作正常!")
                return True
            else:
                print("[FAILURE] 部分佈局檢查失敗")
                return False
        else:
            print("[FAIL] 未找到網格佈局容器")
            return False
            
    except Exception as e:
        print(f"[ERROR] 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("歡迎頁面佈局測試")
    print("=" * 50)
    success = test_welcome_layout()
    if success:
        print("[SUCCESS] 測試成功！新的分行佈局已正確實現。")
    else:
        print("[FAILURE] 測試失敗，需要檢查佈局實現。")