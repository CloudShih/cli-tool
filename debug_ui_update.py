#!/usr/bin/env python3
"""
調試 UI 更新問題
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextBrowser, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt

def test_ui_components():
    """測試 UI 組件更新"""
    
    app = QApplication(sys.argv)
    
    # 創建測試窗口
    window = QWidget()
    window.setWindowTitle("UI 組件測試")
    window.resize(1200, 800)
    
    layout = QVBoxLayout()
    
    # 標籤
    layout.addWidget(QLabel("QTextBrowser 測試"))
    
    # 創建 QTextBrowser
    browser = QTextBrowser()
    browser.setMaximumHeight(300)
    layout.addWidget(browser)
    
    layout.addWidget(QLabel("QTextEdit 對比"))
    
    # 創建 QTextEdit 用於對比
    text_edit = QTextEdit()
    text_edit.setMaximumHeight(300)
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)
    
    def test_simple_html():
        """測試簡單 HTML"""
        simple_html = """
        <h1 style="color: blue;">測試標題</h1>
        <p>這是 <strong style="color: red;">粗體文字</strong> 和 <em style="color: green;">斜體文字</em>。</p>
        <div style="background-color: yellow; padding: 10px;">
            背景顏色區塊
        </div>
        """
        browser.setHtml(simple_html)
        text_edit.setHtml(simple_html)
        print("設置簡單 HTML")
    
    def test_glow_html():
        """測試 Glow HTML"""
        try:
            from tools.glow.glow_model import GlowModel
            
            model = GlowModel()
            test_content = """# 測試標題
            
這是一個 **粗體** 和 *斜體* 的測試。

## 子標題

- 列表項目 1
- 列表項目 2

```python
print("程式碼區塊")
```
"""
            
            success, html_content, error = model.render_markdown(
                test_content, "text", "auto", 80, False
            )
            
            if success:
                browser.setHtml(html_content)
                text_edit.setHtml(html_content)
                print(f"設置 Glow HTML，長度: {len(html_content)}")
                print(f"HTML 預覽: {html_content[:200]}...")
                
                # 保存到檔案
                with open("D:/ClaudeCode/projects/cli_tool/debug_html.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("HTML 已保存到 debug_html.html")
            else:
                print(f"Glow 渲染失敗: {error}")
                browser.setPlainText(f"渲染失敗: {error}")
                text_edit.setPlainText(f"渲染失敗: {error}")
                
        except Exception as e:
            print(f"測試失敗: {e}")
            browser.setPlainText(f"測試失敗: {e}")
            text_edit.setPlainText(f"測試失敗: {e}")
    
    def test_plain_text():
        """測試純文本"""
        plain_text = "這是純文本，沒有任何格式。"
        browser.setPlainText(plain_text)
        text_edit.setPlainText(plain_text)
        print("設置純文本")
    
    # 添加測試按鈕
    button1 = QPushButton("測試簡單 HTML")
    button1.clicked.connect(test_simple_html)
    layout.addWidget(button1)
    
    button2 = QPushButton("測試 Glow HTML")
    button2.clicked.connect(test_glow_html)
    layout.addWidget(button2)
    
    button3 = QPushButton("測試純文本")
    button3.clicked.connect(test_plain_text)
    layout.addWidget(button3)
    
    window.setLayout(layout)
    window.show()
    
    # 自動執行 Glow 測試
    test_glow_html()
    
    print("UI 組件測試窗口已開啟")
    print("觀察 QTextBrowser 和 QTextEdit 的差異")
    
    return app.exec_()

if __name__ == "__main__":
    test_ui_components()