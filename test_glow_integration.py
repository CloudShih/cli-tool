#!/usr/bin/env python3
"""
測試 Glow 與 QTextBrowser 的集成
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextBrowser, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

def test_glow_integration():
    """測試 Glow 集成效果"""
    
    app = QApplication(sys.argv)
    
    # 創建測試窗口
    window = QWidget()
    window.setWindowTitle("Glow 集成測試")
    window.resize(1000, 700)
    
    layout = QVBoxLayout()
    
    # 創建 QTextBrowser（新）
    browser = QTextBrowser()
    browser.setMaximumHeight(300)
    layout.addWidget(browser)
    
    # 創建 QTextEdit（舊）用於對比
    old_widget = QTextEdit()
    old_widget.setMaximumHeight(300)
    old_widget.setReadOnly(True)
    layout.addWidget(old_widget)
    
    def test_glow_rendering():
        """測試 Glow 渲染"""
        try:
            from tools.glow.glow_model import GlowModel
            
            model = GlowModel()
            
            test_markdown = """# Glow 測試標題

這是一個包含 **粗體文字** 和 *斜體文字* 的測試段落。

## 子標題範例

以下是一個程式碼區塊：

```python
def test_function():
    print("Hello from Glow!")
    return True
```

### 列表範例

- 項目 1：基本文字
- 項目 2：**重要項目**  
- 項目 3：*特殊項目*

> 這是一個引用塊，用來展示重要信息。

**重要提醒**：QTextBrowser 應該能正確顯示這些樣式！

---

這是分隔線上方的文字。
"""
            
            print("正在使用 GlowModel 渲染...")
            success, html_content, error_message = model.render_markdown(
                source=test_markdown,
                source_type="text",
                theme="auto",
                width=80,
                use_cache=False
            )
            
            if success:
                print(f"渲染成功！HTML 長度: {len(html_content)} 字符")
                
                # 顯示在 QTextBrowser (新)
                browser.setHtml(html_content)
                
                # 顯示在 QTextEdit (舊) 用於對比
                old_widget.setHtml(html_content)
                
                # 保存 HTML 到檔案
                with open("D:/ClaudeCode/projects/cli_tool/test_integration.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                print("HTML 已保存到 test_integration.html")
                print("觀察兩個組件的顯示差異...")
                
            else:
                print(f"渲染失敗: {error_message}")
                browser.setPlainText(f"渲染失敗: {error_message}")
                old_widget.setPlainText(f"渲染失敗: {error_message}")
                
        except Exception as e:
            error_text = f"測試失敗: {e}"
            print(error_text)
            import traceback
            traceback.print_exc()
            browser.setPlainText(error_text)
            old_widget.setPlainText(error_text)
    
    # 添加測試按鈕
    button = QPushButton("執行 Glow 渲染測試")
    button.clicked.connect(test_glow_rendering)
    layout.addWidget(button)
    
    # 添加標籤
    from PyQt5.QtWidgets import QLabel
    label1 = QLabel("上方：QTextBrowser (新組件 - 應該支援完整 CSS)")
    label2 = QLabel("下方：QTextEdit (舊組件 - CSS 支援有限)")
    layout.insertWidget(0, label1)
    layout.insertWidget(2, label2)
    
    window.setLayout(layout)
    window.show()
    
    # 自動執行測試
    test_glow_rendering()
    
    print("Glow 集成測試窗口已開啟")
    print("比較上下兩個組件的顯示效果")
    
    return app.exec_()

if __name__ == "__main__":
    test_glow_integration()