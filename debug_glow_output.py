#!/usr/bin/env python3
"""
調試 Glow 輸出格式的測試腳本
"""

import sys
import os
import subprocess

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_glow_raw_output():
    """測試 Glow 的原始輸出"""
    print("=== 測試 Glow 原始輸出 ===")
    
    test_markdown = """# 測試標題

這是一個 **粗體文字** 和 *斜體文字* 的測試。

## 程式碼區塊

```python
print("Hello, World!")
```

> 這是一個引用塊

- 項目 1
- 項目 2
- 項目 3
"""
    
    try:
        # 設置環境變量模擬終端環境
        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['FORCE_COLOR'] = '1'
        env['COLORTERM'] = 'truecolor'
        
        # 執行 Glow 命令
        process = subprocess.Popen(
            ['glow', '--width', '80', '--style', 'auto', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # 使用 bytes 模式
            env=env      # 使用環境變量
        )
        
        stdout_bytes, stderr_bytes = process.communicate(
            input=test_markdown.encode('utf-8'),
            timeout=10
        )
        
        # 解碼輸出
        stdout = stdout_bytes.decode('utf-8')
        stderr = stderr_bytes.decode('utf-8')
        
        print(f"Return code: {process.returncode}")
        print(f"Stderr: {stderr}")
        print(f"Stdout length: {len(stdout)} characters")
        print("=== Stdout content (first 500 chars) ===")
        print(repr(stdout[:500]))
        print("=== Stdout visual ===")
        print(stdout[:500])
        
        return stdout, stderr, process.returncode
        
    except Exception as e:
        print(f"Error: {e}")
        return None, str(e), -1

def test_ansi_conversion():
    """測試 ANSI 到 HTML 轉換"""
    print("\n=== 測試 ANSI 到 HTML 轉換 ===")
    
    stdout, stderr, returncode = test_glow_raw_output()
    
    if returncode != 0 or not stdout:
        print("Glow 輸出失敗，無法測試轉換")
        return
    
    try:
        from ansi2html import Ansi2HTMLConverter
        
        # 創建轉換器
        converter = Ansi2HTMLConverter(dark_bg=True)
        
        # 轉換 ANSI 到 HTML
        html_content = converter.convert(stdout, full=False)
        
        print(f"HTML content length: {len(html_content)} characters")
        print("=== HTML content (first 500 chars) ===")
        print(html_content[:500])
        
        # 檢查是否包含 HTML 標籤
        has_html_tags = '<' in html_content and '>' in html_content
        print(f"Contains HTML tags: {has_html_tags}")
        
        return html_content
        
    except ImportError as e:
        print(f"ansi2html 不可用: {e}")
        return None
    except Exception as e:
        print(f"轉換錯誤: {e}")
        return None

def test_model_integration():
    """測試 GlowModel 整合"""
    print("\n=== 測試 GlowModel 整合 ===")
    
    try:
        from tools.glow.glow_model import GlowModel
        
        model = GlowModel()
        
        test_markdown = """# 測試標題

這是一個 **粗體** 測試。

```python
print("Hello!")
```
"""
        
        success, html_content, error_message = model.render_markdown(
            source=test_markdown,
            source_type="text",
            theme="auto",
            width=80,
            use_cache=False
        )
        
        print(f"Render success: {success}")
        print(f"Error message: {error_message}")
        print(f"HTML content length: {len(html_content)} characters")
        print("=== HTML content (first 500 chars) ===")
        print(html_content[:500])
        
        # 檢查是否是原始 markdown
        is_raw_markdown = test_markdown.strip() in html_content
        print(f"Contains raw markdown: {is_raw_markdown}")
        
        # 檢查是否包含 HTML 標籤
        has_html_tags = '<' in html_content and '>' in html_content
        print(f"Contains HTML tags: {has_html_tags}")
        
        return success, html_content, error_message
        
    except Exception as e:
        print(f"模型測試錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False, "", str(e)

if __name__ == "__main__":
    print("Glow 輸出調試腳本")
    print("=" * 50)
    
    # 1. 測試原始輸出
    test_glow_raw_output()
    
    # 2. 測試 ANSI 轉換
    test_ansi_conversion()
    
    # 3. 測試模型整合
    test_model_integration()