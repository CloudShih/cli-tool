#!/usr/bin/env python3
"""
測試 bat 插件基本功能
"""

import sys
import os
import time

# 添加專案根目錄到路徑  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.bat.bat_model import BatModel
from tools.bat.plugin import BatPlugin


def test_bat_availability():
    """測試 bat 工具可用性"""
    print("=" * 60)
    print("測試 bat 工具可用性")
    print("=" * 60)
    
    model = BatModel()
    available, version, error = model.check_bat_availability()
    
    if available:
        print(f"✓ bat 工具可用")
        print(f"  版本信息: {version}")
        return True
    else:
        print(f"✗ bat 工具不可用")
        print(f"  錯誤信息: {error}")
        return False


def test_theme_and_language_support():
    """測試主題和語言支持"""
    print("\n" + "=" * 60)
    print("測試主題和語言支持")
    print("=" * 60)
    
    model = BatModel()
    
    # 測試獲取主題列表
    print("獲取可用主題...")
    themes = model.get_available_themes()
    if themes:
        print(f"✓ 找到 {len(themes)} 個主題")
        print(f"  前5個主題: {themes[:5]}")
    else:
        print("✗ 無法獲取主題列表")
    
    # 測試獲取語言列表
    print("\n獲取支援語言...")
    languages = model.get_supported_languages()
    if languages:
        print(f"✓ 找到 {len(languages)} 種語言")
        print(f"  前5種語言: {languages[:5]}")
    else:
        print("✗ 無法獲取語言列表")
    
    return len(themes) > 0 and len(languages) > 0


def test_file_highlighting():
    """測試檔案高亮功能"""
    print("\n" + "=" * 60)
    print("測試檔案高亮功能")
    print("=" * 60)
    
    model = BatModel()
    
    # 使用專案中的現有檔案進行測試
    test_files = [
        "D:\\ClaudeCode\\projects\\cli_tool\\test_final_result.py",
        "D:\\ClaudeCode\\projects\\cli_tool\\tools\\bat\\bat_model.py",
        "D:\\ClaudeCode\\projects\\cli_tool\\config\\cli_tool_config.json"
    ]
    
    results = []
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n測試檔案: {os.path.basename(test_file)}")
            
            start_time = time.time()
            success, html_content, error = model.highlight_file(
                test_file, "Monokai Extended", True, True, 4, False, None, False
            )
            end_time = time.time()
            
            if success:
                print(f"  ✓ 高亮成功")
                print(f"  ✓ HTML 長度: {len(html_content)} 字符")
                print(f"  ✓ 處理時間: {end_time - start_time:.2f} 秒")
                print(f"  ✓ 包含 HTML 標籤: {'<div' in html_content}")
                results.append(True)
            else:
                print(f"  ✗ 高亮失敗: {error}")
                results.append(False)
        else:
            print(f"\n跳過不存在的檔案: {test_file}")
    
    return all(results) if results else False


def test_text_highlighting():
    """測試文本高亮功能"""
    print("\n" + "=" * 60)
    print("測試文本高亮功能")
    print("=" * 60)
    
    model = BatModel()
    
    # 測試不同語言的代碼片段
    test_cases = [
        ("python", """
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
"""),
        ("javascript", """
function helloWorld() {
    console.log("Hello, World!");
    return true;
}

helloWorld();
"""),
        ("json", """
{
    "name": "test",
    "version": "1.0.0",
    "dependencies": {
        "lodash": "^4.17.21"
    }
}
""")
    ]
    
    results = []
    
    for language, code in test_cases:
        print(f"\n測試 {language.upper()} 高亮...")
        
        start_time = time.time()
        success, html_content, error = model.highlight_text(
            code, language, "Monokai Extended", True, 4, False, False
        )
        end_time = time.time()
        
        if success:
            print(f"  ✓ {language} 高亮成功")
            print(f"  ✓ HTML 長度: {len(html_content)} 字符")
            print(f"  ✓ 處理時間: {end_time - start_time:.2f} 秒")
            results.append(True)
        else:
            print(f"  ✗ {language} 高亮失敗: {error}")
            results.append(False)
    
    return all(results)


def test_cache_functionality():
    """測試快取功能"""
    print("\n" + "=" * 60)
    print("測試快取功能")
    print("=" * 60)
    
    model = BatModel()
    
    # 清除現有快取
    model.clear_cache()
    
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
    
    # 第一次渲染（創建快取）
    print("第一次渲染（創建快取）...")
    start_time = time.time()
    success1, html1, error1 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, True
    )
    time1 = time.time() - start_time
    
    if not success1:
        print(f"✗ 第一次渲染失敗: {error1}")
        return False
    
    # 第二次渲染（使用快取）
    print("第二次渲染（使用快取）...")
    start_time = time.time()
    success2, html2, error2 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, True
    )
    time2 = time.time() - start_time
    
    if not success2:
        print(f"✗ 第二次渲染失敗: {error2}")
        return False
    
    # 檢查快取效果
    if html1 == html2:
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"✓ 快取功能正常")
        print(f"✓ 第一次時間: {time1:.3f} 秒")
        print(f"✓ 第二次時間: {time2:.3f} 秒")
        print(f"✓ 提速倍數: {speedup:.1f}x")
        
        # 檢查快取信息
        cache_info = model.get_cache_info()
        print(f"✓ 快取項目數: {cache_info.get('total_entries', 0)}")
        print(f"✓ 快取大小: {cache_info.get('total_size_mb', 0)} MB")
        
        return True
    else:
        print("✗ 快取內容不一致")
        return False


def test_plugin_interface():
    """測試插件接口"""
    print("\n" + "=" * 60)
    print("測試插件接口")
    print("=" * 60)
    
    plugin = BatPlugin()
    
    # 測試基本屬性
    print(f"插件名稱: {plugin.name}")
    print(f"插件版本: {plugin.version}")
    print(f"插件描述: {plugin.description}")
    print(f"所需工具: {plugin.required_tools}")
    print(f"支援檔案類型: {len(plugin.get_supported_file_types())} 種")
    
    # 測試工具可用性檢查
    available = plugin.check_tools_availability()
    print(f"工具可用性: {'✓ 可用' if available else '✗ 不可用'}")
    
    # 測試插件初始化
    init_success = plugin.initialize()
    print(f"插件初始化: {'✓ 成功' if init_success else '✗ 失敗'}")
    
    if init_success:
        print(f"插件已初始化: {'✓ 是' if plugin.is_initialized() else '✗ 否'}")
        
        # 測試狀態信息
        status_info = plugin.get_status_info()
        print(f"狀態信息: {status_info}")
        
        # 清理插件
        plugin.cleanup()
        print("✓ 插件清理完成")
    
    return available and init_success


def main():
    """主測試函數"""
    print("Bat 插件基本功能測試")
    print("=" * 60)
    print(f"測試時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("工具可用性檢查", test_bat_availability),
        ("主題和語言支持", test_theme_and_language_support),
        ("檔案高亮功能", test_file_highlighting),
        ("文本高亮功能", test_text_highlighting),
        ("快取功能", test_cache_functionality),
        ("插件接口", test_plugin_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} 測試出現異常: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總體結果: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("\n*** bat 插件基本功能測試全部通過 ***")
        print("插件已準備好進行下一階段開發")
        return True
    else:
        print(f"\n*** {len(results) - passed} 項測試需要修復 ***")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)