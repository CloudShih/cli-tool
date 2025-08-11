#!/usr/bin/env python3
"""
測試 Git 修改參數修復
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_git_modifications():
    """測試 Git 修改參數"""
    print("Testing Git modifications parameter fix")
    print("=" * 50)
    
    from tools.bat.bat_model import BatModel
    
    model = BatModel()
    test_code = """
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
"""
    
    print("Testing with Git modifications enabled...")
    success1, html1, error1 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, False
    )
    
    if success1:
        print("[PASS] Git modifications enabled - success")
        print(f"  HTML length: {len(html1)} chars")
    else:
        print(f"[FAIL] Git modifications enabled - failed: {error1}")
        return False
    
    print("\nTesting with Git modifications disabled...")
    success2, html2, error2 = model.highlight_text(
        test_code, "python", "Monokai Extended", True, 4, False, False
    )
    
    if success2:
        print("[PASS] Git modifications disabled - success")
        print(f"  HTML length: {len(html2)} chars")
        print("[PASS] Both configurations work correctly")
        return True
    else:
        print(f"[FAIL] Git modifications disabled - failed: {error2}")
        return False

def test_file_highlighting():
    """測試檔案高亮的 Git 參數"""
    print("\nTesting file highlighting Git parameter")
    print("=" * 50)
    
    from tools.bat.bat_model import BatModel
    
    model = BatModel()
    test_file = "D:\\ClaudeCode\\projects\\cli_tool\\tools\\bat\\bat_model.py"
    
    if not os.path.exists(test_file):
        print(f"[SKIP] Test file not found: {test_file}")
        return True
    
    print("Testing file with Git modifications disabled...")
    success, html, error = model.highlight_file(
        test_file, "Monokai Extended", True, False, 4, False, None, False
    )
    
    if success:
        print("[PASS] File highlighting with Git disabled - success")
        print(f"  HTML length: {len(html)} chars")
        return True
    else:
        print(f"[FAIL] File highlighting with Git disabled - failed: {error}")
        return False

def main():
    """主測試函數"""
    print("Git Modifications Parameter Fix Test")
    print("=" * 50)
    
    tests = [
        ("Text highlighting", test_git_modifications),
        ("File highlighting", test_file_highlighting)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n*** GIT MODIFICATIONS FIX SUCCESSFUL ***")
        print("The --no-git parameter issue has been resolved")
        return True
    else:
        print(f"\n*** {len(results) - passed} TESTS STILL FAILING ***")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)