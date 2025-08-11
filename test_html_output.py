#!/usr/bin/env python3
"""
測試 HTML 輸出效果
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_html_conversion():
    """測試 HTML 轉換效果"""
    
    try:
        from tools.glow.glow_model import GlowModel
        
        model = GlowModel()
        
        test_markdown = """# 測試標題

這是一個包含 **粗體文字** 和 *斜體文字* 的段落。

## 子標題

以下是一個程式碼範例：

```python
def hello_world():
    print("Hello, Glow!")
    return "success"
```

### 列表範例

- 項目 1
- 項目 2  
- 項目 3

> 這是一個引用塊，用來展示重要訊息。

**重要提醒**：這個工具現在應該可以正確顯示格式化的內容了！
"""
        
        print("正在測試 Markdown 渲染...")
        
        success, html_content, error_message = model.render_markdown(
            source=test_markdown,
            source_type="text",
            theme="auto",
            width=80,
            use_cache=False
        )
        
        if success:
            print("渲染成功！")
            print(f"HTML 內容長度: {len(html_content)} 字符")
            
            # 保存到檔案以便查看
            with open("D:/ClaudeCode/projects/cli_tool/test_output.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("HTML 檔案已保存到: test_output.html")
            print("\n=== HTML 內容預覽 (前 1000 字符) ===")
            print(html_content[:1000])
            print("...")
            
            # 檢查格式化元素
            format_checks = [
                ("<h1", "H1 標題"),
                ("<h2", "H2 標題"), 
                ("<h3", "H3 標題"),
                ("<strong>", "粗體文字"),
                ("<em>", "斜體文字"),
                ("<div style=", "樣式化區塊"),
                ("background-color", "背景顏色"),
                ("font-family", "字體設定")
            ]
            
            print("\n=== 格式化檢查 ===")
            for check, name in format_checks:
                found = check in html_content
                status = "✓" if found else "✗"
                print(f"{status} {name}")
                
        else:
            print(f"渲染失敗: {error_message}")
            
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_conversion()