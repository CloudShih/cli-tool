#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
暗色主題修復驗證測試

測試 QTreeWidget 的暗色主題樣式是否正確應用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from tools.ripgrep.ripgrep_view import SearchResultsWidget, RipgrepView
from tools.ripgrep.core.data_models import FileResult, SearchMatch, SearchSummary, SearchStatus

def test_dark_theme_styling():
    """測試暗色主題樣式是否正確應用"""
    
    app = QApplication(sys.argv)
    
    # 創建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("Ripgrep 暗色主題測試")
    main_window.setGeometry(100, 100, 800, 600)
    
    # 設置暗色主題背景
    main_window.setStyleSheet("""
        QMainWindow {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
    """)
    
    # 創建 Ripgrep 視圖
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # 創建搜尋結果組件
    results_widget = SearchResultsWidget()
    layout.addWidget(results_widget)
    
    # 添加一些測試數據來驗證樣式
    # 創建測試匹配項
    test_match1 = SearchMatch(
        line_number=15,
        column=8,
        content="    def search_function(self, pattern):"
    )
    
    test_match2 = SearchMatch(
        line_number=32,
        column=20,
        content="        return self.search_engine.execute(pattern)"
    )
    
    # 創建測試文件結果
    test_file = FileResult("D:/test/example.py")
    test_file.add_match(test_match1)
    test_file.add_match(test_match2)
    
    # 添加結果到界面
    results_widget.add_result(test_file)
    
    # 創建搜尋摘要
    summary = SearchSummary(
        pattern="test_pattern",
        status=SearchStatus.COMPLETED,
        total_matches=2,
        files_with_matches=1,
        search_time=0.15,
        files_searched=5
    )
    
    results_widget.update_summary(summary)
    
    main_window.setCentralWidget(central_widget)
    main_window.show()
    
    print("=== 暗色主題測試 ===")
    print("1. 檢查搜尋結果區域是否有透明背景")
    print("2. 檢查文字顏色是否為白色")
    print("3. 檢查選中項目是否有藍色背景")
    print("4. 檢查懸停效果是否為灰色背景")
    print("5. 檢查表頭是否為暗色主題")
    print("\n請檢查界面是否符合暗色主題設計...")
    print("如果看到白色背景，表示樣式修復失敗")
    print("如果背景透明且文字為白色，表示修復成功")
    
    # 檢查樣式是否已經應用
    tree_widget = results_widget.results_tree
    stylesheet = tree_widget.styleSheet()
    
    print(f"\n=== 樣式檢查 ===")
    print(f"QTreeWidget 是否有樣式: {'是' if stylesheet else '否'}")
    if stylesheet:
        print("已應用的樣式內容:")
        print(stylesheet[:200] + "..." if len(stylesheet) > 200 else stylesheet)
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_dark_theme_styling())