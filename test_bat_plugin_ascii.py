#!/usr/bin/env python3
"""
測試 bat 插件基本功能 - ASCII 友好版本
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
    print("Test bat tool availability")
    print("=" * 60)
    
    model = BatModel()
    available, version, error = model.check_bat_availability()
    
    if available:
        print(f"[PASS] bat tool available")
        print(f"  Version: {version}")
        return True
    else:
        print(f"[FAIL] bat tool not available")
        print(f"  Error: {error}")
        return False


def test_theme_and_language_support():
    """測試主題和語言支持"""
    print("\n" + "=" * 60)
    print("Test theme and language support")
    print("=" * 60)
    
    model = BatModel()
    
    # 測試獲取主題列表
    print("Getting available themes...")
    themes = model.get_available_themes()
    if themes:
        print(f"[PASS] Found {len(themes)} themes")
        print(f"  First 5 themes: {themes[:5]}")
    else:
        print("[FAIL] Cannot get theme list")
    
    # 測試獲取語言列表
    print("\nGetting supported languages...")
    languages = model.get_supported_languages()
    if languages:
        print(f"[PASS] Found {len(languages)} languages")
        print(f"  First 5 languages: {languages[:5]}")
    else:
        print("[FAIL] Cannot get language list")
    
    return len(themes) > 0 and len(languages) > 0


def test_file_highlighting():
    """測試檔案高亮功能"""
    print("\n" + "=" * 60)
    print("Test file highlighting")
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
            print(f"\nTesting file: {os.path.basename(test_file)}")
            
            start_time = time.time()
            success, html_content, error = model.highlight_file(
                test_file, "Monokai Extended", True, True, 4, False, None, False
            )
            end_time = time.time()
            
            if success:
                print(f"  [PASS] Highlighting successful")
                print(f"  [PASS] HTML length: {len(html_content)} chars")
                print(f"  [PASS] Processing time: {end_time - start_time:.2f} seconds")
                print(f"  [PASS] Contains HTML tags: {'<div' in html_content}")
                results.append(True)
            else:
                print(f"  [FAIL] Highlighting failed: {error}")
                results.append(False)
        else:
            print(f"\nSkipped non-existent file: {test_file}")
    
    return all(results) if results else False


def test_text_highlighting():
    """測試文本高亮功能"""
    print("\n" + "=" * 60)
    print("Test text highlighting")
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
        print(f"\nTesting {language.upper()} highlighting...")
        
        start_time = time.time()
        success, html_content, error = model.highlight_text(
            code, language, "Monokai Extended", True, 4, False, False
        )
        end_time = time.time()
        
        if success:
            print(f"  [PASS] {language} highlighting successful")
            print(f"  [PASS] HTML length: {len(html_content)} chars")
            print(f"  [PASS] Processing time: {end_time - start_time:.2f} seconds")
            results.append(True)
        else:
            print(f"  [FAIL] {language} highlighting failed: {error}")
            results.append(False)
    
    return all(results)


def test_cache_functionality():
    """測試快取功能"""
    print("\n" + "=" * 60)
    print("Test cache functionality")
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
    print("First render (create cache)...")
    start_time = time.time()
    success1, html1, error1 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, True
    )
    time1 = time.time() - start_time
    
    if not success1:
        print(f"[FAIL] First render failed: {error1}")
        return False
    
    # 第二次渲染（使用快取）
    print("Second render (use cache)...")
    start_time = time.time()
    success2, html2, error2 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, True
    )
    time2 = time.time() - start_time
    
    if not success2:
        print(f"[FAIL] Second render failed: {error2}")
        return False
    
    # 檢查快取效果
    if html1 == html2:
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"[PASS] Cache working correctly")
        print(f"[PASS] First time: {time1:.3f} seconds")
        print(f"[PASS] Second time: {time2:.3f} seconds")
        print(f"[PASS] Speedup: {speedup:.1f}x")
        
        # 檢查快取信息
        cache_info = model.get_cache_info()
        print(f"[PASS] Cache entries: {cache_info.get('total_entries', 0)}")
        print(f"[PASS] Cache size: {cache_info.get('total_size_mb', 0)} MB")
        
        return True
    else:
        print("[FAIL] Cache content inconsistent")
        return False


def test_plugin_interface():
    """測試插件接口"""
    print("\n" + "=" * 60)
    print("Test plugin interface")
    print("=" * 60)
    
    plugin = BatPlugin()
    
    # 測試基本屬性
    print(f"Plugin name: {plugin.name}")
    print(f"Plugin version: {plugin.version}")
    print(f"Plugin description: {plugin.description}")
    print(f"Required tools: {plugin.required_tools}")
    print(f"Supported file types: {len(plugin.get_supported_file_types())} types")
    
    # 測試工具可用性檢查
    available = plugin.check_tools_availability()
    print(f"Tool availability: {'[PASS] Available' if available else '[FAIL] Not available'}")
    
    # 測試插件初始化
    init_success = plugin.initialize()
    print(f"Plugin initialization: {'[PASS] Success' if init_success else '[FAIL] Failed'}")
    
    if init_success:
        print(f"Plugin initialized: {'[PASS] Yes' if plugin.is_initialized() else '[FAIL] No'}")
        
        # 測試狀態信息
        status_info = plugin.get_status_info()
        print(f"Status info: {status_info}")
        
        # 清理插件
        plugin.cleanup()
        print("[PASS] Plugin cleanup completed")
    
    return available and init_success


def main():
    """主測試函數"""
    print("Bat Plugin Basic Functionality Test")
    print("=" * 60)
    print(f"Test time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Tool availability check", test_bat_availability),
        ("Theme and language support", test_theme_and_language_support),
        ("File highlighting", test_file_highlighting),
        ("Text highlighting", test_text_highlighting),
        ("Cache functionality", test_cache_functionality),
        ("Plugin interface", test_plugin_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n*** ALL BAT PLUGIN BASIC TESTS PASSED ***")
        print("Plugin is ready for next stage development")
        return True
    else:
        print(f"\n*** {len(results) - passed} TESTS NEED ATTENTION ***")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)