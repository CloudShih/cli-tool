#!/usr/bin/env python3
"""
簡化的 bat 插件測試
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """測試基本功能"""
    print("Testing bat plugin basic functionality")
    print("=" * 50)
    
    try:
        from tools.bat.bat_model import BatModel
        print("[PASS] BatModel import successful")
        
        model = BatModel()
        print("[PASS] BatModel initialization successful")
        
        # 檢查工具可用性
        available, version, error = model.check_bat_availability()
        print(f"[INFO] Tool availability: {available}")
        print(f"[INFO] Version: {version}")
        
        if not available:
            print(f"[ERROR] bat tool not available: {error}")
            return False
        
        # 測試簡單的文本高亮
        test_code = "print('Hello, World!')"
        success, html, error = model.highlight_text(test_code, "python", "Monokai Extended", True, 4, False, False)
        
        if success:
            print(f"[PASS] Text highlighting successful ({len(html)} chars)")
            print(f"[INFO] HTML contains styling: {'font' in html.lower()}")
            return True
        else:
            print(f"[ERROR] Text highlighting failed: {error}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plugin_interface():
    """測試插件接口"""
    print("\nTesting plugin interface")
    print("=" * 50)
    
    try:
        from tools.bat.plugin import BatPlugin
        print("[PASS] BatPlugin import successful")
        
        plugin = BatPlugin()
        print("[PASS] BatPlugin initialization successful")
        
        print(f"[INFO] Plugin name: {plugin.name}")
        print(f"[INFO] Plugin version: {plugin.version}")
        print(f"[INFO] Required tools: {plugin.required_tools}")
        
        # 檢查工具可用性
        available = plugin.check_tools_availability()
        print(f"[INFO] Tools available: {available}")
        
        if available:
            # 初始化插件
            init_success = plugin.initialize()
            print(f"[INFO] Plugin initialization: {init_success}")
            
            if init_success:
                print(f"[INFO] Plugin is initialized: {plugin.is_initialized()}")
                
                # 清理
                plugin.cleanup()
                print("[PASS] Plugin cleanup successful")
                return True
        
        return available
        
    except Exception as e:
        print(f"[ERROR] Plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("Bat Plugin Simple Test")
    print("=" * 50)
    
    test1_result = test_basic_functionality()
    test2_result = test_plugin_interface()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Basic functionality: {'PASS' if test1_result else 'FAIL'}")
    print(f"Plugin interface: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        print("\n[SUCCESS] All tests passed!")
        print("Bat plugin basic framework is working correctly.")
        return True
    else:
        print("\n[FAILURE] Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)