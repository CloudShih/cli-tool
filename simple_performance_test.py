#!/usr/bin/env python3
"""
簡化版 Ripgrep 插件性能測試
"""
import sys
import os
import time
from pathlib import Path

# 設定路徑
sys.path.append(os.path.dirname(__file__))

from core.plugin_manager import plugin_manager

def test_plugin_performance():
    """測試插件性能"""
    print("=" * 50)
    print("Ripgrep 插件性能測試")
    print("=" * 50)
    
    results = {}
    
    # 1. 插件載入性能測試
    print("\n1. 插件載入性能測試")
    
    load_times = []
    for i in range(3):
        start_time = time.time()
        plugin_manager.discover_plugins()
        plugins = plugin_manager.get_all_plugins()
        load_time = time.time() - start_time
        load_times.append(load_time)
        
        if i == 0:
            print(f"   發現 {len(plugins)} 個插件")
            ripgrep_found = 'ripgrep' in plugins
            print(f"   Ripgrep 插件: {'找到' if ripgrep_found else '未找到'}")
    
    avg_load_time = sum(load_times) / len(load_times)
    results['plugin_loading'] = {
        'average_time': avg_load_time,
        'times': load_times,
        'status': 'PASS' if avg_load_time < 3.0 else 'SLOW'
    }
    
    print(f"   平均載入時間: {avg_load_time:.3f}s")
    print(f"   性能評估: {results['plugin_loading']['status']}")
    
    # 2. MVC 組件創建性能測試
    print("\n2. MVC 組件創建性能測試")
    
    try:
        plugin = plugins.get('ripgrep')
        if plugin:
            try:
                from PyQt5.QtWidgets import QApplication
                if not QApplication.instance():
                    app = QApplication(sys.argv)
                
                start_time = time.time()
                
                model = plugin.create_model()
                view = plugin.create_view()
                
                if model and view:
                    controller = plugin.create_controller(model, view)
                    creation_time = time.time() - start_time
                    
                    results['mvc_creation'] = {
                        'time': creation_time,
                        'status': 'PASS' if creation_time < 5.0 else 'SLOW'
                    }
                    
                    print(f"   MVC 創建時間: {creation_time:.3f}s")
                    print(f"   性能評估: {results['mvc_creation']['status']}")
                    
                    # 清理
                    if hasattr(controller, 'cleanup'):
                        controller.cleanup()
                    if hasattr(view, 'deleteLater'):
                        view.deleteLater()
                    if hasattr(model, 'cleanup'):
                        model.cleanup()
                
                else:
                    print("   MVC 組件創建失敗")
                    results['mvc_creation'] = {'status': 'FAIL'}
                    
            except ImportError:
                print("   跳過: PyQt5 不可用")
                results['mvc_creation'] = {'status': 'SKIP'}
        else:
            print("   跳過: Ripgrep 插件不可用")
            results['mvc_creation'] = {'status': 'SKIP'}
            
    except Exception as e:
        print(f"   錯誤: {e}")
        results['mvc_creation'] = {'status': 'ERROR', 'error': str(e)}
    
    # 3. 資料模型性能測試
    print("\n3. 資料模型性能測試")
    
    try:
        from tools.ripgrep.core.data_models import SearchParameters, FileResult, SearchMatch
        
        start_time = time.time()
        
        # 創建多個搜尋參數
        for i in range(100):
            params = SearchParameters(
                pattern=f"test_pattern_{i}",
                search_path=".",
                case_sensitive=(i % 2 == 0),
                regex_mode=True
            )
        
        # 創建多個搜尋結果
        file_results = []
        for i in range(50):
            file_result = FileResult(file_path=f"test_file_{i}.py")
            
            for j in range(10):
                match = SearchMatch(
                    line_number=j+1,
                    column=0,
                    content=f"test content {j} in file {i}"
                )
                file_result.add_match(match)
            
            file_results.append(file_result)
        
        data_model_time = time.time() - start_time
        
        results['data_models'] = {
            'time': data_model_time,
            'objects_created': 100 + 50 + 500,  # params + file_results + matches
            'status': 'PASS' if data_model_time < 1.0 else 'SLOW'
        }
        
        print(f"   資料模型創建時間: {data_model_time:.3f}s")
        print(f"   創建物件數量: {results['data_models']['objects_created']}")
        print(f"   性能評估: {results['data_models']['status']}")
        
    except Exception as e:
        print(f"   錯誤: {e}")
        results['data_models'] = {'status': 'ERROR', 'error': str(e)}
    
    # 4. 匯出功能性能測試
    print("\n4. 匯出功能性能測試")
    
    try:
        if plugin:
            model = plugin.create_model()
            if model and hasattr(model, 'export_results'):
                # 準備測試資料
                from tools.ripgrep.core.data_models import FileResult, SearchMatch
                
                test_result = FileResult(file_path="test_performance.py")
                for i in range(20):
                    match = SearchMatch(
                        line_number=i+1,
                        column=0,
                        content=f"performance test content line {i}"
                    )
                    test_result.add_match(match)
                
                model.search_results.append(test_result)
                
                # 測試匯出
                import tempfile
                export_times = {}
                
                for fmt in ['json', 'csv', 'txt']:
                    with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as tmp:
                        start_time = time.time()
                        success = model.export_results(tmp.name, fmt)
                        export_time = time.time() - start_time
                        
                        export_times[fmt] = {
                            'time': export_time,
                            'success': success,
                            'size': os.path.getsize(tmp.name) if success else 0
                        }
                        
                        try:
                            os.unlink(tmp.name)
                        except:
                            pass
                
                results['export'] = export_times
                
                total_export_time = sum(t['time'] for t in export_times.values())
                print(f"   總匯出時間: {total_export_time:.3f}s")
                
                for fmt, data in export_times.items():
                    status = "✓" if data['success'] else "✗"
                    print(f"     {fmt.upper()}: {data['time']:.3f}s ({data['size']} bytes) {status}")
                
                # 清理
                if hasattr(model, 'cleanup'):
                    model.cleanup()
            else:
                print("   跳過: Model 或匯出功能不可用")
                results['export'] = {'status': 'SKIP'}
        else:
            print("   跳過: Ripgrep 插件不可用")
            results['export'] = {'status': 'SKIP'}
            
    except Exception as e:
        print(f"   錯誤: {e}")
        results['export'] = {'status': 'ERROR', 'error': str(e)}
    
    # 生成性能報告
    print("\n" + "=" * 50)
    print("性能測試報告")
    print("=" * 50)
    
    overall_status = "PASS"
    
    print("測試項目摘要:")
    for test_name, result in results.items():
        if isinstance(result, dict):
            status = result.get('status', 'UNKNOWN')
            time_info = ""
            
            if 'time' in result:
                time_info = f" ({result['time']:.3f}s)"
            elif 'average_time' in result:
                time_info = f" ({result['average_time']:.3f}s avg)"
            
            print(f"  {test_name:15s}: {status}{time_info}")
            
            if status in ['SLOW', 'FAIL', 'ERROR']:
                overall_status = "ISSUES"
    
    print(f"\n整體評估: {overall_status}")
    
    if overall_status == "PASS":
        print("所有性能測試通過，插件性能符合標準。")
        return True
    else:
        print("發現性能問題，建議進行優化。")
        return False

def main():
    """主執行函數"""
    try:
        success = test_plugin_performance()
        return 0 if success else 1
    except Exception as e:
        print(f"性能測試執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())