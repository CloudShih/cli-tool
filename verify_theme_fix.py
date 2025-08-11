#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證暗色主題修復是否正確應用

非互動式測試，檢查樣式是否正確設置
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from tools.ripgrep.ripgrep_view import SearchResultsWidget

def verify_dark_theme_fix():
    """驗證暗色主題修復"""
    
    app = QApplication(sys.argv)
    
    # 創建搜尋結果組件
    results_widget = SearchResultsWidget()
    
    # 檢查QTreeWidget的樣式
    tree_widget = results_widget.results_tree
    stylesheet = tree_widget.styleSheet()
    
    print("=== Ripgrep Dark Theme Fix Verification ===\n")
    
    # 檢查是否有樣式
    has_stylesheet = bool(stylesheet.strip())
    print(f"[+] QTreeWidget has stylesheet: {'YES' if has_stylesheet else 'NO'}")
    
    if has_stylesheet:
        # 檢查關鍵樣式元素
        checks = {
            'background-color: transparent': 'QTreeWidget transparent background',
            'color: #ffffff': 'White text color',
            'background-color: #0078d4': 'Selected item blue background', 
            'background-color: #404040': 'Hover item gray background',
            'background-color: #2d2d2d': 'Header dark background'
        }
        
        print("\n=== Style Check ===")
        all_passed = True
        for style_rule, description in checks.items():
            found = style_rule in stylesheet
            status = "[+]" if found else "[-]"
            print(f"{status} {description}: {'SET' if found else 'NOT SET'}")
            if not found:
                all_passed = False
        
        print(f"\n=== Fix Status ===")
        if all_passed:
            print("[SUCCESS] Dark theme fix successful! All required styles are set.")
            print("   - QTreeWidget will show transparent background")
            print("   - Text color is white, matching dark theme")
            print("   - Interactive effects (selected, hover) are set")
            print("   - Header style matches dark theme")
        else:
            print("[INCOMPLETE] Dark theme fix incomplete, some styles missing.")
        
        print(f"\n=== Complete Stylesheet ===")
        print(stylesheet)
        
    else:
        print("[ERROR] QTreeWidget has no stylesheet set")
        print("   This means the white background issue is not fixed")
    
    return 0 if has_stylesheet else 1

if __name__ == "__main__":
    sys.exit(verify_dark_theme_fix())