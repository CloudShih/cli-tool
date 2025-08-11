#!/usr/bin/env python3
"""
測試工具卡片尺寸修復效果
檢查卡片尺寸是否正確調整為 320x220
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication

# 設置路徑
sys.path.append('.')

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_card_size_fix():
    """測試工具卡片尺寸修復"""
    try:
        # 創建應用程式
        app = QApplication([])
        
        # 導入主窗口類
        from ui.main_window import WelcomePage
        
        # 創建歡迎頁面實例
        welcome_page = WelcomePage()
        
        print("[INFO] 測試工具卡片尺寸修復")
        print("=" * 50)
        
        # 檢查佈局結構
        main_layout = welcome_page.layout()
        
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
            
            print(f"[PASS] 找到網格佈局容器")
            print(f"   - 總卡片數: {grid_layout.count()}")
            
            # 檢查每個卡片的尺寸
            card_sizes = []
            cards_checked = 0
            
            for row in range(2):  # 2 行
                for col in range(3):  # 3 列
                    item = grid_layout.itemAtPosition(row, col)
                    if item and item.widget():
                        card = item.widget()
                        size = card.size()
                        width = size.width()
                        height = size.height()
                        card_sizes.append((width, height))
                        cards_checked += 1
                        print(f"   - 卡片 ({row}, {col}): {width} x {height}")
            
            print(f"[INFO] 檢查了 {cards_checked} 個卡片")
            
            # 驗證尺寸
            expected_width = 320
            expected_height = 220
            
            size_correct = True
            for i, (width, height) in enumerate(card_sizes):
                if width != expected_width or height != expected_height:
                    print(f"[FAIL] 卡片 {i+1} 尺寸錯誤: {width}x{height}, 預期: {expected_width}x{expected_height}")
                    size_correct = False
            
            if size_correct and len(card_sizes) > 0:
                print(f"[SUCCESS] 所有卡片尺寸正確: {expected_width} x {expected_height}")
            elif len(card_sizes) == 0:
                print("[WARNING] 沒有找到任何卡片")
                size_correct = False
            
            # 檢查佈局間距
            vertical_spacing = grid_layout.verticalSpacing()
            horizontal_spacing = grid_layout.horizontalSpacing()
            
            print(f"[INFO] 佈局間距:")
            print(f"   - 垂直間距: {vertical_spacing}px (預期: 40px)")
            print(f"   - 水平間距: {horizontal_spacing}px (預期: 25px)")
            
            spacing_correct = (vertical_spacing == 40 and horizontal_spacing == 25)
            if spacing_correct:
                print("[PASS] 間距設置正確")
            else:
                print("[FAIL] 間距設置不正確")
            
            # 檢查行高設置
            row0_height = grid_layout.rowMinimumHeight(0)
            row1_height = grid_layout.rowMinimumHeight(1)
            
            print(f"[INFO] 行高設置:")
            print(f"   - 第1行最小高度: {row0_height}px (預期: 240px)")
            print(f"   - 第2行最小高度: {row1_height}px (預期: 240px)")
            
            row_height_correct = (row0_height == 240 and row1_height == 240)
            if row_height_correct:
                print("[PASS] 行高設置正確")
            else:
                print("[FAIL] 行高設置不正確")
            
            # 總體結果
            print("\n" + "=" * 50)
            print("修復驗證結果:")
            
            if size_correct and spacing_correct and row_height_correct:
                print("[SUCCESS] 工具卡片尺寸修復成功！")
                print("   - 卡片尺寸: 320x220 ✓")
                print("   - 間距優化: 垂直40px, 水平25px ✓") 
                print("   - 行高調整: 240px ✓")
                return True
            else:
                problems = []
                if not size_correct:
                    problems.append("卡片尺寸")
                if not spacing_correct:
                    problems.append("間距設置")
                if not row_height_correct:
                    problems.append("行高設置")
                    
                print(f"[PARTIAL] 部分修復成功，需要調整: {', '.join(problems)}")
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
    success = test_card_size_fix()
    if success:
        print("[FINAL] 工具卡片尺寸修復測試通過！")
    else:
        print("[FINAL] 工具卡片尺寸修復測試失敗，需要進一步調整。")