#!/usr/bin/env python3
"""
快速驗證測試
專注於核心功能驗證，避免可能導致卡住的複雜初始化
"""

import sys
import os
import time
import json
from pathlib import Path

# 設置路徑
sys.path.insert(0, '.')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def quick_validation_test():
    """快速驗證測試"""
    print("快速驗證測試開始")
    print("=" * 50)
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'test_results': {}
    }
    
    # 1. 基礎模組導入測試
    print("\n=== 基礎模組導入測試 ===")
    basic_modules = [
        'main_app',
        'config.config_manager',
        'ui.theme_manager'
    ]
    
    module_results = {'passed': 0, 'total': len(basic_modules), 'details': {}}
    
    for module in basic_modules:
        try:
            start_time = time.time()
            __import__(module)
            import_time = time.time() - start_time
            module_results['details'][module] = {'success': True, 'time': import_time}
            module_results['passed'] += 1
            print(f"[OK] {module}: {import_time:.3f}s")
        except Exception as e:
            module_results['details'][module] = {'success': False, 'error': str(e)}
            print(f"[FAIL] {module}: {e}")
    
    results['test_results']['module_imports'] = module_results
    
    # 2. 配置系統測試
    print("\n=== 配置系統測試 ===")
    try:
        from config.config_manager import config_manager
        config = config_manager.get_config()
        
        config_result = {
            'success': True,
            'sections': list(config.keys()) if isinstance(config, dict) else [],
            'total_items': len(config) if isinstance(config, dict) else 0
        }
        print(f"[OK] 配置系統: {len(config)} 項配置")
        
    except Exception as e:
        config_result = {'success': False, 'error': str(e)}
        print(f"[FAIL] 配置系統: {e}")
    
    results['test_results']['config_system'] = config_result
    
    # 3. 工具模型測試（單獨測試，避免插件管理器）
    print("\n=== 工具模型測試 ===")
    tool_models = [
        'tools.fd.fd_model',
        'tools.pandoc.pandoc_model',
        'tools.glow.glow_model'
    ]
    
    tool_results = {'passed': 0, 'total': len(tool_models), 'details': {}}
    
    for tool_module in tool_models:
        try:
            __import__(tool_module)
            tool_results['details'][tool_module] = {'success': True}
            tool_results['passed'] += 1
            print(f"[OK] {tool_module}")
        except Exception as e:
            tool_results['details'][tool_module] = {'success': False, 'error': str(e)}
            print(f"[FAIL] {tool_module}: {e}")
    
    results['test_results']['tool_models'] = tool_results
    
    # 4. 外部工具可用性測試
    print("\n=== 外部工具可用性測試 ===")
    import shutil
    
    tools = ['fd', 'pandoc', 'bat', 'rg']
    tool_availability = {'available': 0, 'total': len(tools), 'details': {}}
    
    for tool in tools:
        tool_path = shutil.which(tool)
        if tool_path:
            tool_availability['details'][tool] = {'available': True, 'path': tool_path}
            tool_availability['available'] += 1
            print(f"[OK] {tool}: {tool_path}")
        else:
            tool_availability['details'][tool] = {'available': False}
            print(f"[FAIL] {tool}: 未找到")
    
    results['test_results']['tool_availability'] = tool_availability
    
    # 5. 效能基準測試
    print("\n=== 效能基準測試 ===")
    
    # 配置載入時間
    config_times = []
    for i in range(3):
        start_time = time.time()
        config_manager.get_config()
        config_times.append(time.time() - start_time)
    
    # 工具探測時間比較
    shutil_start = time.time()
    for tool in tools:
        shutil.which(tool)
    shutil_time = time.time() - shutil_start
    
    performance_results = {
        'config_load_avg_time': sum(config_times) / len(config_times),
        'config_load_times': config_times,
        'tool_detection_time': shutil_time,
        'tools_tested': len(tools)
    }
    
    results['test_results']['performance'] = performance_results
    print(f"[OK] 平均配置載入時間: {performance_results['config_load_avg_time']:.3f}s")
    print(f"[OK] 工具探測時間: {shutil_time:.3f}s")
    
    # 6. 生成摘要
    print("\n=== 測試摘要 ===")
    
    summary = {
        'total_test_categories': len(results['test_results']),
        'module_import_rate': f"{module_results['passed']}/{module_results['total']} ({module_results['passed']/module_results['total']*100:.1f}%)",
        'tool_model_rate': f"{tool_results['passed']}/{tool_results['total']} ({tool_results['passed']/tool_results['total']*100:.1f}%)",
        'tool_availability_rate': f"{tool_availability['available']}/{tool_availability['total']} ({tool_availability['available']/tool_availability['total']*100:.1f}%)",
        'config_system_status': 'OK' if config_result['success'] else 'FAIL',
        'overall_health': 'GOOD' if (module_results['passed'] == module_results['total'] and 
                                   config_result['success'] and 
                                   tool_results['passed'] >= tool_results['total'] * 0.8) else 'NEEDS_ATTENTION'
    }
    
    results['summary'] = summary
    
    print(f"模組導入: {summary['module_import_rate']}")
    print(f"工具模型: {summary['tool_model_rate']}")
    print(f"外部工具: {summary['tool_availability_rate']}")
    print(f"配置系統: {summary['config_system_status']}")
    print(f"整體健康: {summary['overall_health']}")
    
    print("\n" + "=" * 50)
    print("快速驗證測試完成")
    
    # 保存結果
    output_file = 'quick_validation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"結果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    results = quick_validation_test()