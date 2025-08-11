#!/usr/bin/env python3
"""
簡化的 Glow 修復驗證
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_glow_fix():
    """驗證 Glow 修復"""
    print("驗證 Glow 修復...")
    print("=" * 50)
    
    try:
        from tools.glow.glow_model import GlowModel
        
        # 創建模型實例
        model = GlowModel()
        print("[OK] GlowModel 初始化成功")
        
        # 測試簡單的 Markdown
        test_content = """# 修復驗證

這是修復驗證測試。

## 功能檢查

- HTML 生成
- CSS 樣式
- 格式化輸出
"""
        
        print("\n正在渲染測試內容...")
        success, html_content, error_msg = model.render_markdown(
            source=test_content,
            source_type="text",
            theme="auto",
            width=80,
            use_cache=False
        )
        
        if success:
            print("[OK] 渲染成功")
            print(f"[OK] HTML 內容長度: {len(html_content)} 字符")
            
            # 檢查關鍵特徵
            checks = [
                ("<html>", "HTML 結構"),
                ("<style>", "CSS 樣式"),
                ("<h1", "H1 標題"),
                ("color:", "顏色樣式"),
                ("font-family:", "字體設定")
            ]
            
            print("\n功能檢查:")
            all_passed = True
            for check, name in checks:
                found = check in html_content
                status = "[OK]" if found else "[FAIL]"
                print(f"  {status} {name}")
                if not found:
                    all_passed = False
            
            # 保存結果
            with open("D:/ClaudeCode/projects/cli_tool/verify_output.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\n[OK] HTML 結果已保存到 verify_output.html")
            
            if all_passed:
                print("\n[SUCCESS] 所有檢查通過！修復成功！")
                print("[INFO] QTextBrowser 應該能正確顯示樣式化的內容")
                return True
            else:
                print("\n[WARNING] 部分檢查失敗")
                return False
                
        else:
            print(f"[FAIL] 渲染失敗: {error_msg}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 測試異常: {e}")
        return False

if __name__ == "__main__":
    success = verify_glow_fix()
    sys.exit(0 if success else 1)