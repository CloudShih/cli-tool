#!/usr/bin/env python3
"""
GUI vs 測試環境差異對比分析
"""

import sys
import os
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.glow.glow_model import GlowModel
from config.config_manager import ConfigManager

# 設置詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_isolated_model():
    """測試隔離的 GlowModel（模擬測試環境）"""
    print("=" * 60)
    print("測試隔離的 GlowModel（模擬測試環境）")
    print("=" * 60)
    
    try:
        # 直接創建 GlowModel
        model = GlowModel()
        
        # 測試檔案路徑
        test_file = "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md"
        
        print(f"模型實例: {model}")
        print(f"版本: {model.html_conversion_version}")
        print(f"快取目錄: {model.cache_dir}")
        
        # 執行渲染
        success, html_content, error = model.render_markdown(
            test_file, "file", "auto", 80, False  # 強制不使用快取
        )
        
        print(f"\n渲染結果:")
        print(f"- 成功: {success}")
        print(f"- HTML 長度: {len(html_content)}")
        print(f"- 錯誤: {error}")
        print(f"- 包含 <html>: {'<html>' in html_content}")
        print(f"- 包含 <h1>: {'<h1' in html_content}")
        print(f"- 包含 <h2>: {'<h2' in html_content}")
        
        if success:
            print(f"\nHTML 前500字符:")
            print(html_content[:500])
            
            # 保存測試結果
            with open("test_isolated_result.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\n測試結果已保存到 test_isolated_result.html")
        
        return success, html_content, error
        
    except Exception as e:
        print(f"測試失敗: {e}")
        return False, "", str(e)

def test_gui_config_model():
    """測試通過 GUI 配置創建的 GlowModel（模擬 GUI 環境）"""
    print("\n" + "=" * 60)
    print("測試通過 GUI 配置創建的 GlowModel（模擬 GUI 環境）")
    print("=" * 60)
    
    try:
        # 使用 ConfigManager 創建（模擬 GUI 環境）
        config_manager = ConfigManager()
        glow_config = config_manager.get_tool_config('glow')
        
        print(f"GUI 配置: {glow_config}")
        
        # 創建 GlowModel (它會自動從 config_manager 獲取配置)
        model = GlowModel()
        
        # 測試檔案路徑
        test_file = "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md"
        
        print(f"模型實例: {model}")
        print(f"版本: {model.html_conversion_version}")
        print(f"快取目錄: {model.cache_dir}")
        
        # 執行渲染
        success, html_content, error = model.render_markdown(
            test_file, "file", "auto", 80, False  # 強制不使用快取
        )
        
        print(f"\n渲染結果:")
        print(f"- 成功: {success}")
        print(f"- HTML 長度: {len(html_content)}")
        print(f"- 錯誤: {error}")
        print(f"- 包含 <html>: {'<html>' in html_content}")
        print(f"- 包含 <h1>: {'<h1' in html_content}")
        print(f"- 包含 <h2>: {'<h2' in html_content}")
        
        if success:
            print(f"\nHTML 前500字符:")
            print(html_content[:500])
            
            # 保存測試結果
            with open("test_gui_config_result.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\n測試結果已保存到 test_gui_config_result.html")
        
        return success, html_content, error
        
    except Exception as e:
        print(f"測試失敗: {e}")
        return False, "", str(e)

def compare_results():
    """對比兩種環境的結果"""
    print("\n" + "=" * 60)
    print("執行對比測試")
    print("=" * 60)
    
    # 執行兩種測試
    isolated_success, isolated_html, isolated_error = test_isolated_model()
    gui_success, gui_html, gui_error = test_gui_config_model()
    
    print("\n" + "=" * 60)
    print("對比結果")
    print("=" * 60)
    
    print(f"隔離測試成功: {isolated_success}")
    print(f"GUI 配置測試成功: {gui_success}")
    
    if isolated_success and gui_success:
        print(f"HTML 長度差異: {len(gui_html) - len(isolated_html)}")
        print(f"HTML 內容相同: {isolated_html == gui_html}")
        
        if isolated_html != gui_html:
            print("⚠️  HTML 內容不同！")
            
            # 保存差異分析
            with open("html_diff_analysis.txt", "w", encoding="utf-8") as f:
                f.write("HTML 內容差異分析\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"隔離測試 HTML 長度: {len(isolated_html)}\n")
                f.write(f"GUI 配置 HTML 長度: {len(gui_html)}\n\n")
                f.write("隔離測試 HTML 前1000字符:\n")
                f.write("-" * 30 + "\n")
                f.write(isolated_html[:1000] + "\n\n")
                f.write("GUI 配置 HTML 前1000字符:\n")
                f.write("-" * 30 + "\n")
                f.write(gui_html[:1000] + "\n\n")
            
            print("差異分析已保存到 html_diff_analysis.txt")
        else:
            print("✅ HTML 內容完全相同")
    
    # 錯誤對比
    if isolated_error or gui_error:
        print(f"\n錯誤對比:")
        print(f"隔離測試錯誤: {isolated_error}")
        print(f"GUI 配置錯誤: {gui_error}")

def check_environment():
    """檢查環境差異"""
    print("\n" + "=" * 60)
    print("檢查環境差異")
    print("=" * 60)
    
    import tempfile
    print(f"臨時目錄: {tempfile.gettempdir()}")
    print(f"當前工作目錄: {os.getcwd()}")
    print(f"Python 版本: {sys.version}")
    print(f"Python 路徑: {sys.path[:3]}...")  # 只顯示前3個路徑
    
    # 檢查 Glow 可用性
    import subprocess
    try:
        result = subprocess.run(['glow', '--version'], capture_output=True, text=True, timeout=5)
        print(f"Glow 版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"Glow 檢查失敗: {e}")

if __name__ == "__main__":
    print("GUI vs 測試環境差異對比分析")
    print("時間:", os.popen('date /t && time /t').read().strip())
    
    check_environment()
    compare_results()
    
    print("\n" + "=" * 60)
    print("分析完成！請檢查生成的檔案:")
    print("- test_isolated_result.html")
    print("- test_gui_config_result.html") 
    print("- html_diff_analysis.txt (如果有差異)")
    print("=" * 60)