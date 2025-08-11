#!/usr/bin/env python3
"""
Glow 插件最終測試腳本
移除所有 emoji 字符，適用於 Windows 終端
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_glow_model():
    """測試 GlowModel 功能"""
    print("[TEST] 測試 GlowModel...")
    
    try:
        from tools.glow.glow_model import GlowModel
        
        # 創建模型實例
        model = GlowModel()
        print("[PASS] GlowModel 創建成功")
        
        # 測試工具可用性檢查
        print("\n[INFO] 檢查 Glow 工具可用性...")
        available, version_info, error_message = model.check_glow_availability()
        
        if available:
            print(f"[PASS] Glow 工具可用: {version_info}")
        else:
            print(f"[WARN] Glow 工具不可用: {error_message}")
            print("[INFO] 請安裝 Glow 工具: https://github.com/charmbracelet/glow")
        
        # 測試 URL 驗證
        print("\n[INFO] 測試 URL 驗證...")
        test_urls = [
            "microsoft/terminal",
            "https://raw.githubusercontent.com/microsoft/terminal/main/README.md",
            "invalid-url",
            "microsoft/terminal@main:README.md"
        ]
        
        for url in test_urls:
            is_valid, processed_url, error_msg = model.validate_url(url)
            if is_valid:
                print(f"[PASS] URL 有效: {url} -> {processed_url[:80]}...")
            else:
                print(f"[FAIL] URL 無效: {url} - {error_msg}")
        
        # 測試快取功能
        print("\n[INFO] 測試快取功能...")
        cache_info = model.get_cache_info()
        print(f"[PASS] 快取信息: {cache_info}")
        
        # 測試文字渲染（如果 Glow 可用）
        if available:
            print("\n[INFO] 測試 Markdown 渲染...")
            test_markdown = """# 測試標題

這是一個**測試 Markdown**文檔。

## 功能列表

- 支援本地檔案
- 支援遠程 URL
- 支援直接文字輸入

> 這是一個引用塊

```python
print("Hello, Glow!")
```
"""
            
            success, html_content, error_msg = model.render_markdown(
                source=test_markdown,
                source_type="text",
                theme="auto",
                width=80,
                use_cache=False
            )
            
            if success:
                print("[PASS] Markdown 渲染成功")
                print(f"[INFO] HTML 內容長度: {len(html_content)} 字符")
            else:
                print(f"[FAIL] Markdown 渲染失敗: {error_msg}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] GlowModel 測試失敗: {e}")
        return False

def test_glow_plugin():
    """測試 GlowPlugin 功能"""
    print("\n[TEST] 測試 GlowPlugin...")
    
    try:
        from tools.glow.plugin import GlowPlugin
        
        # 創建插件實例
        plugin = GlowPlugin()
        print("[PASS] GlowPlugin 創建成功")
        
        # 測試插件信息
        print(f"[INFO] 插件名稱: {plugin.name}")
        print(f"[INFO] 顯示名稱: {plugin.get_display_name()}")
        print(f"[INFO] 版本: {plugin.version}")
        print(f"[INFO] 描述: {plugin.description}")
        
        # 測試工具可用性
        tool_available = plugin.check_tools_availability()
        print(f"[INFO] 工具可用性: {'可用' if tool_available else '不可用'}")
        
        # 測試插件可用性
        plugin_available = plugin.is_available()
        print(f"[INFO] 插件可用性: {'可用' if plugin_available else '不可用'}")
        
        # 測試配置模式
        config_schema = plugin.get_configuration_schema()
        print(f"[INFO] 配置選項數量: {len(config_schema)}")
        
        # 測試支援的檔案類型
        file_types = plugin.get_supported_file_types()
        print(f"[INFO] 支援檔案類型: {', '.join(file_types)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] GlowPlugin 測試失敗: {e}")
        return False

def test_file_operations():
    """測試檔案操作"""
    print("\n[TEST] 測試檔案操作...")
    
    try:
        from tools.glow.glow_model import GlowModel
        
        model = GlowModel()
        
        # 創建測試 Markdown 檔案
        test_content = """# 測試檔案

這是一個測試用的 Markdown 檔案。

## 特性

- [x] 支援檢查列表
- [ ] 待辦事項
- 支援 emoji

### 程式碼範例

```python
def hello_world():
    print("Hello from Glow plugin!")
```

**粗體文字** 和 *斜體文字*
"""
        
        # 使用臨時檔案
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # 測試檔案信息獲取
            file_info = model.get_file_info(temp_file)
            print(f"[PASS] 檔案信息: {file_info}")
            
            # 測試檔案渲染（如果 Glow 可用）
            available, _, _ = model.check_glow_availability()
            if available:
                success, html_content, error_msg = model.render_markdown(
                    source=temp_file,
                    source_type="file",
                    theme="light",
                    width=100,
                    use_cache=False
                )
                
                if success:
                    print("[PASS] 檔案渲染成功")
                    print(f"[INFO] HTML 內容長度: {len(html_content)} 字符")
                else:
                    print(f"[FAIL] 檔案渲染失敗: {error_msg}")
            
        finally:
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                print("[INFO] 已清理臨時檔案")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 檔案操作測試失敗: {e}")
        return False

def test_error_handling():
    """測試錯誤處理"""
    print("\n[TEST] 測試錯誤處理...")
    
    try:
        from tools.glow.glow_model import GlowModel
        
        model = GlowModel()
        
        # 測試不存在的檔案
        print("[INFO] 測試不存在的檔案...")
        file_info = model.get_file_info("nonexistent_file.md")
        if not file_info.get('exists', True):
            print("[PASS] 正確檢測到不存在的檔案")
        else:
            print("[FAIL] 未能正確檢測不存在的檔案")
        
        # 測試無效的 URL
        print("[INFO] 測試無效的 URL...")
        is_valid, _, error_msg = model.validate_url("invalid://url")
        if not is_valid:
            print(f"[PASS] 正確檢測到無效 URL: {error_msg}")
        else:
            print("[FAIL] 未能正確檢測無效 URL")
        
        # 測試空內容渲染
        print("[INFO] 測試空內容渲染...")
        success, _, error_msg = model.render_markdown(
            source="",
            source_type="text",
            theme="auto",
            width=80,
            use_cache=False
        )
        
        # 空內容應該不會導致崩潰，但可能會有警告
        print(f"[INFO] 空內容渲染結果: {'成功' if success else f'失敗 - {error_msg}'}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 錯誤處理測試失敗: {e}")
        return False

def main():
    """主測試函式"""
    print("開始 Glow 插件測試...")
    print("=" * 50)
    
    tests = [
        ("GlowModel 功能", test_glow_model),
        ("GlowPlugin 功能", test_glow_plugin),
        ("檔案操作", test_file_operations),
        ("錯誤處理", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] 執行測試: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"[PASS] {test_name} 測試通過")
                passed += 1
            else:
                print(f"[FAIL] {test_name} 測試失敗")
        except Exception as e:
            print(f"[ERROR] {test_name} 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"[RESULT] 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("[SUCCESS] 所有測試通過！Glow 插件準備就緒。")
        return 0
    else:
        print("[WARNING] 部分測試失敗，請檢查相關功能。")
        return 1

if __name__ == "__main__":
    sys.exit(main())