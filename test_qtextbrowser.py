#!/usr/bin/env python3
"""
測試 QTextBrowser 的 HTML/CSS 支援
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextBrowser, QPushButton
from PyQt5.QtCore import Qt

def test_qtextbrowser_css():
    """測試 QTextBrowser 的 CSS 支援"""
    
    app = QApplication(sys.argv)
    
    # 創建測試窗口
    window = QWidget()
    window.setWindowTitle("QTextBrowser CSS 測試")
    window.resize(800, 600)
    
    layout = QVBoxLayout()
    
    # 創建 QTextBrowser
    browser = QTextBrowser()
    
    # 測試 HTML 內容（包含內聯 CSS）
    test_html = """
    <html>
    <head>
        <meta charset="utf-8">
        <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f9f9f9;
        }
        h1 {
            color: #2196F3;
            margin: 20px 0 10px 0;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 5px;
        }
        h2 {
            color: #FF9800;
            margin: 16px 0 8px 0;
        }
        .code-block {
            background-color: #f8f9fa;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #007acc;
            font-family: 'Consolas', monospace;
            border-radius: 4px;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 10px;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            margin: 10px 0;
        }
        strong {
            color: #e74c3c;
            font-weight: bold;
        }
        em {
            color: #9b59b6;
            font-style: italic;
        }
        </style>
    </head>
    <body>
        <h1>測試標題 1</h1>
        <p>這是一個包含 <strong>粗體文字</strong> 和 <em>斜體文字</em> 的段落。</p>
        
        <h2>測試標題 2</h2>
        <div class="highlight">
            <p><strong>重要提醒</strong>：這個區塊應該有黃色背景和邊框。</p>
        </div>
        
        <div class="code-block">
def hello_world():
    print("Hello from QTextBrowser!")
    return "CSS styles should work"
        </div>
        
        <p>如果您能看到：</p>
        <ul>
            <li>藍色的 H1 標題與底線</li>
            <li>橙色的 H2 標題</li>
            <li>紅色的粗體文字</li>
            <li>紫色的斜體文字</li>
            <li>黃色背景的提醒區塊</li>
            <li>灰色背景和藍色左邊框的程式碼區塊</li>
        </ul>
        <p>那麼 <strong>QTextBrowser 支援 CSS 樣式</strong>！</p>
    </body>
    </html>
    """
    
    browser.setHtml(test_html)
    layout.addWidget(browser)
    
    # 添加測試按鈕
    def update_content():
        browser.setHtml(test_html.replace("測試標題 1", "已更新的標題 1"))
    
    button = QPushButton("更新內容測試")
    button.clicked.connect(update_content)
    layout.addWidget(button)
    
    window.setLayout(layout)
    window.show()
    
    print("QTextBrowser CSS 測試窗口已開啟")
    print("如果樣式正確顯示，則表示修復有效")
    
    return app.exec_()

if __name__ == "__main__":
    test_qtextbrowser_css()