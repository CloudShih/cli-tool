#!/usr/bin/env python3
"""
測試 Glow 輸出解析
"""

import sys
import os
import subprocess

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from tools.glow.glow_model import GlowModel

def test_glow_actual_output():
    """測試 Glow 實際輸出"""
    print("=== 測試 Glow 實際命令輸出 ===")
    
    # 直接執行 Glow 命令
    try:
        process = subprocess.Popen(
            ['glow', 'D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md', '--width', '80'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"Glow 命令執行結果:")
        print(f"Return code: {process.returncode}")
        print(f"輸出長度: {len(stdout)}")
        print(f"錯誤: {stderr}")
        print("前200字符:")
        print(repr(stdout[:200]))
        print("\n實際顯示:")
        print(stdout[:500])
        
    except Exception as e:
        print(f"執行 Glow 命令失敗: {e}")

def test_model_conversion():
    """測試 Model 轉換"""
    print("\n=== 測試 Model HTML 轉換 ===")
    
    model = GlowModel()
    
    # 測試檔案渲染
    success, html_content, error = model.render_markdown(
        "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md",
        "file",
        "auto",
        80,
        False
    )
    
    print(f"Model 渲染結果:")
    print(f"成功: {success}")
    print(f"HTML 長度: {len(html_content)}")
    print(f"錯誤: {error}")
    
    if success:
        print("HTML 前500字符:")
        print(html_content[:500])
        
        # 保存到檔案
        with open("test_output.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("\nHTML 已保存到 test_output.html")
        
        # 檢查關鍵字
        has_h1 = '<h1' in html_content
        has_h2 = '<h2' in html_content
        has_color = 'color:' in html_content
        has_style = 'style=' in html_content
        
        print(f"\n格式檢查:")
        print(f"包含 H1 標題: {has_h1}")
        print(f"包含 H2 標題: {has_h2}")
        print(f"包含顏色樣式: {has_color}")
        print(f"包含內聯樣式: {has_style}")

if __name__ == "__main__":
    test_glow_actual_output()
    test_model_conversion()