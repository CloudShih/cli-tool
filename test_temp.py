#!/usr/bin/env python3
import subprocess
import sys

# 測試 bat 命令
try:
    print("Testing bat command...")
    result = subprocess.run(['bat', '--version'], capture_output=True, text=True, timeout=10)
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"Error: {e}")

# 測試 bat 高亮
try:
    print("\nTesting bat highlighting...")
    test_code = "print('hello')"
    result = subprocess.run(['bat', '--language', 'python', '--color', 'always'], 
                          input=test_code, capture_output=True, text=True, timeout=10)
    print(f"Return code: {result.returncode}")
    print(f"Stdout length: {len(result.stdout)}")
    print(f"Stderr: {result.stderr}")
    print(f"Output preview (first 200 chars): {result.stdout[:200]}")
except Exception as e:
    print(f"Error: {e}")