#!/usr/bin/env python3
"""
低風險 PR 驗證腳本
驗證 PR#2 (環境變數支援) 和 PR#3 (shutil.which 使用) 的改進
"""

import sys
import os
import time
import shutil
import subprocess
from pathlib import Path

# 設置路徑
sys.path.insert(0, '.')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_current_fd_functionality():
    """測試當前 fd 功能是否正常"""
    print("=== 當前 fd 功能測試 ===")
    
    try:
        from tools.fd.fd_model import FdModel
        
        # 建立 FdModel 實例
        fd_model = FdModel()
        print(f"[OK] FdModel 初始化成功")
        print(f"[OK] 當前 fd 路徑: {fd_model.fd_executable_path}")
        
        # 測試簡單的 fd 命令
        # 在當前目錄搜尋 .py 檔案
        result = fd_model.execute_fd_command(
            pattern="*.py", 
            path=".", 
            extension="py",
            search_type_index=1,  # 只搜尋檔案
            hidden=False,
            case_sensitive=False
        )
        
        if result:
            print("[OK] fd 命令執行成功")
            return {'success': True, 'path': fd_model.fd_executable_path}
        else:
            print("[FAIL] fd 命令執行失敗")
            return {'success': False, 'error': 'Command execution failed'}
            
    except Exception as e:
        print(f"[FAIL] fd 測試失敗: {e}")
        return {'success': False, 'error': str(e)}

def test_environment_variable_override():
    """測試 PR#2 - 環境變數覆蓋功能（模擬）"""
    print("\n=== PR#2 環境變數覆蓋測試 ===")
    
    try:
        # 模擬 PR#2 的環境變數支援改進
        original_fd_path = "C:\\Users\\cloudchshih\\AppData\\Local\\Microsoft\\WinGet\\Packages\\sharkdp.fd_Microsoft.WinGet.Source_8wekyb3d8bbwe\\fd-v10.2.0-x86_64-pc-windows-msvc\\fd.exe"
        
        # 測試當前配置系統是否已支援自訂路徑
        from config.config_manager import config_manager
        config = config_manager.get_config()
        
        fd_config_path = config.get('tools', {}).get('fd', {}).get('executable_path')
        
        if fd_config_path:
            print(f"[OK] 配置系統已支援自訂 fd 路徑: {fd_config_path}")
            
            # 檢查環境變數是否能被讀取（模擬）
            test_env_var = os.environ.get('FD_PATH')
            if test_env_var:
                print(f"[OK] 環境變數 FD_PATH 存在: {test_env_var}")
            else:
                print("[INFO] 環境變數 FD_PATH 未設置（這是正常的）")
            
            return {'success': True, 'current_supports_config': True}
        else:
            print("[FAIL] 配置系統不支援自訂 fd 路徑")
            return {'success': False, 'current_supports_config': False}
            
    except Exception as e:
        print(f"[FAIL] 環境變數測試失敗: {e}")
        return {'success': False, 'error': str(e)}

def test_shutil_which_improvement():
    """測試 PR#3 - shutil.which 改進（模擬）"""
    print("\n=== PR#3 shutil.which 改進測試 ===")
    
    # 比較現有實作與 shutil.which 的效果
    tools_to_test = ['fd', 'pandoc', 'bat', 'rg']
    results = {}
    
    for tool in tools_to_test:
        print(f"\n測試工具: {tool}")
        
        # 方法1: 當前實作（subprocess 方式）
        current_method_result = test_tool_current_method(tool)
        
        # 方法2: shutil.which 方式
        shutil_method_result = test_tool_shutil_method(tool)
        
        results[tool] = {
            'current_method': current_method_result,
            'shutil_method': shutil_method_result
        }
        
        # 比較結果
        if current_method_result['available'] == shutil_method_result['available']:
            print(f"[OK] {tool}: 兩種方法結果一致")
        else:
            print(f"[WARN] {tool}: 方法結果不一致")
            print(f"  - 當前方法: {current_method_result['available']}")
            print(f"  - shutil.which: {shutil_method_result['available']}")
    
    return results

def test_tool_current_method(tool):
    """使用當前方法測試工具可用性"""
    try:
        start_time = time.time()
        result = subprocess.run([tool, '--help'], 
                              capture_output=True, 
                              timeout=5)
        execution_time = time.time() - start_time
        available = result.returncode == 0
        
        return {
            'available': available,
            'method': 'subprocess',
            'execution_time': execution_time,
            'error': result.stderr.decode('utf-8', errors='ignore') if not available else None
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
        return {
            'available': False,
            'method': 'subprocess',
            'execution_time': 5.0,  # timeout
            'error': str(e)
        }

def test_tool_shutil_method(tool):
    """使用 shutil.which 方法測試工具可用性"""
    try:
        start_time = time.time()
        tool_path = shutil.which(tool)
        execution_time = time.time() - start_time
        
        available = tool_path is not None
        
        return {
            'available': available,
            'method': 'shutil.which',
            'execution_time': execution_time,
            'tool_path': tool_path,
            'error': None if available else f"Tool '{tool}' not found in PATH"
        }
    except Exception as e:
        return {
            'available': False,
            'method': 'shutil.which',
            'execution_time': 0.0,
            'error': str(e)
        }

def simulate_pr2_enhancement():
    """模擬 PR#2 的環境變數支援增強"""
    print("\n=== PR#2 增強模擬 ===")
    
    def get_fd_path_with_env_support():
        """模擬增強後的 fd 路徑獲取邏輯"""
        # 優先順序: 環境變數 -> 配置檔 -> 預設路徑
        env_path = os.environ.get('FD_PATH')
        if env_path and Path(env_path).exists():
            return env_path, 'environment'
        
        # 從配置檔獲取
        from config.config_manager import config_manager
        config_path = config_manager.get('tools.fd.executable_path')
        if config_path and Path(config_path).exists():
            return config_path, 'config'
        
        # 使用 shutil.which 作為預設
        which_path = shutil.which('fd')
        if which_path:
            return which_path, 'shutil.which'
        
        return None, 'not_found'
    
    fd_path, source = get_fd_path_with_env_support()
    
    if fd_path:
        print(f"[OK] 增強後的路徑解析成功")
        print(f"  - 路徑: {fd_path}")
        print(f"  - 來源: {source}")
        return {'success': True, 'path': fd_path, 'source': source}
    else:
        print("[FAIL] 增強後的路徑解析失敗")
        return {'success': False}

def run_low_risk_pr_validation():
    """運行所有低風險 PR 驗證測試"""
    print("低風險 PR 驗證測試開始")
    print("=" * 60)
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'target_prs': ['PR#2: 環境變數支援', 'PR#3: shutil.which 使用']
    }
    
    # 測試當前 fd 功能
    results['current_fd_test'] = test_current_fd_functionality()
    
    # 測試環境變數覆蓋（PR#2）
    results['env_override_test'] = test_environment_variable_override()
    
    # 測試 shutil.which 改進（PR#3）
    results['shutil_which_test'] = test_shutil_which_improvement()
    
    # 模擬 PR#2 增強
    results['pr2_simulation'] = simulate_pr2_enhancement()
    
    print("\n" + "=" * 60)
    print("低風險 PR 驗證測試完成")
    
    # 統計結果
    success_count = 0
    total_tests = 0
    
    if results['current_fd_test']['success']:
        success_count += 1
    total_tests += 1
    
    if results['env_override_test']['success']:
        success_count += 1
    total_tests += 1
    
    if results['pr2_simulation']['success']:
        success_count += 1
    total_tests += 1
    
    print(f"\n主要驗證測試: {success_count}/{total_tests} 通過")
    
    # shutil.which 測試結果統計
    shutil_results = results['shutil_which_test']
    consistent_tools = 0
    total_tools = len(shutil_results)
    
    for tool, test_result in shutil_results.items():
        if test_result['current_method']['available'] == test_result['shutil_method']['available']:
            consistent_tools += 1
    
    print(f"shutil.which 一致性測試: {consistent_tools}/{total_tools} 工具結果一致")
    
    return results

if __name__ == "__main__":
    validation_results = run_low_risk_pr_validation()