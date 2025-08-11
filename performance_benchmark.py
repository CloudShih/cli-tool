#!/usr/bin/env python3
"""
Ripgrep 插件性能基準測試
測量關鍵操作的性能指標
"""
import sys
import os
import time
import tempfile
import shutil
import threading
from pathlib import Path
from typing import Dict, List

# 設定路徑
sys.path.append(os.path.dirname(__file__))

# 導入測試目標
from core.plugin_manager import plugin_manager

class PerformanceBenchmark:
    """性能基準測試類"""
    
    def __init__(self):
        self.results = {}
        self.test_data_dir = None
        self.plugin = None
    
    def setup_large_test_dataset(self, num_files: int = 100, lines_per_file: int = 1000):
        """創建大型測試資料集"""
        print(f"創建測試資料集: {num_files} 個檔案，每個 {lines_per_file} 行...")
        
        self.test_data_dir = Path(tempfile.mkdtemp(prefix="ripgrep_perf_"))
        
        # 創建各種類型的檔案
        file_templates = {
            'python': '''#!/usr/bin/env python3
"""Generated Python file for performance testing"""
import os
import sys
from typing import List, Dict, Any

class TestClass_{file_idx}:
    def __init__(self):
        self.data = []
        self.search_pattern = "performance_test_{line_idx}"
    
    def process_data(self):
        """Process data method {line_idx}"""
        for item in self.data:
            if "search_term" in str(item):
                yield item
    
    def search_function_{line_idx}(self, pattern: str) -> List[str]:
        """Search function for line {line_idx}"""
        results = []
        # This is line {line_idx} with search content
        if pattern in "test_data_line_{line_idx}":
            results.append(f"match_found_at_line_{line_idx}")
        return results

def main_function_{line_idx}():
    """Main function for line {line_idx}"""
    test_obj = TestClass_{file_idx}()
    return test_obj.search_function_{line_idx}("search_term")

# Global variable for line {line_idx}
GLOBAL_SEARCH_DATA_{line_idx} = "test_content_{line_idx}_with_patterns"
''',
            
            'javascript': '''// JavaScript file {file_idx} for performance testing
const fs = require('fs');
const path = require('path');

/**
 * Search function for line {line_idx}
 * @param {{string}} searchTerm - Search term
 * @returns {{Array}} Results
 */
function searchFunction_{line_idx}(searchTerm) {{
    const data_{line_idx} = "test_data_line_{line_idx}_with_search_pattern";
    const results = [];
    
    // Line {line_idx} processing
    if (data_{line_idx}.includes(searchTerm)) {{
        results.push({{
            lineNumber: {line_idx},
            content: data_{line_idx},
            match: true,
            performance_marker: "line_{line_idx}"
        }});
    }}
    
    return results;
}}

// Export for line {line_idx}
module.exports = {{
    searchFunction_{line_idx},
    testData_{line_idx}: "search_content_line_{line_idx}"
}};

// Performance test data for line {line_idx}
const PERF_DATA_{line_idx} = {{
    timestamp: new Date().toISOString(),
    line: {line_idx},
    searchable: "performance_test_content_{line_idx}"
}};
''',
            
            'text': '''Line {line_idx}: This is performance test content for searching
Search pattern {line_idx}: performance_test_marker_{line_idx}
Content line {line_idx}: Various text content for testing search functionality
Data line {line_idx}: test_data_{line_idx}_searchable_content_{line_idx}
Pattern line {line_idx}: regex_pattern_\\d+_line_{line_idx}
Unicode line {line_idx}: 測試內容_{line_idx} 🔍 search_emoji_{line_idx}
Log line {line_idx}: 2024-01-01 10:00:{line_idx:02d} INFO Processing request {line_idx}
Error line {line_idx}: 2024-01-01 10:00:{line_idx:02d} ERROR Connection failed at line {line_idx}
Debug line {line_idx}: 2024-01-01 10:00:{line_idx:02d} DEBUG Search completed for line {line_idx}
End line {line_idx}: Final content for performance testing line {line_idx}
'''
        }
        
        # 創建檔案
        for file_idx in range(num_files):
            for ext, template in file_templates.items():
                file_path = self.test_data_dir / f"test_file_{file_idx:03d}.{ext}"
                
                content_lines = []
                for line_idx in range(lines_per_file):
                    line_content = template.format(file_idx=file_idx, line_idx=line_idx)
                    content_lines.append(line_content)
                
                file_path.write_text('\n'.join(content_lines), encoding='utf-8')
        
        total_files = len(list(self.test_data_dir.glob("*")))
        total_lines = total_files * lines_per_file
        print(f"測試資料集創建完成: {total_files} 個檔案，約 {total_lines:,} 行")
        
        return total_files, total_lines
    
    def measure_execution_time(self, func, *args, **kwargs):
        """測量函數執行時間"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = str(e)
            success = False
        
        end_time = time.time()
        
        return {
            'result': result,
            'success': success,
            'execution_time': end_time - start_time
        }
    
    def benchmark_plugin_loading(self):
        """基準測試: 插件載入性能"""
        print("\n測試插件載入性能...")
        
        def load_plugins():
            plugin_manager.discover_plugins()
            return plugin_manager.get_all_plugins()
        
        # 執行多次測量
        times = []
        for i in range(5):
            result = self.measure_execution_time(load_plugins)
            times.append(result['execution_time'])
            if i == 0:  # 記錄第一次的詳細資訊
                self.results['plugin_loading'] = result
        
        avg_time = sum(times) / len(times)
        self.results['plugin_loading']['average_time'] = avg_time
        
        print(f"  平均載入時間: {avg_time:.3f}s")
        
        # 獲取插件實例
        plugins = self.results['plugin_loading']['result']
        self.plugin = plugins.get('ripgrep') if plugins else None
    
    def benchmark_mvc_creation(self):
        """基準測試: MVC 組件創建性能"""
        print("\n測試 MVC 組件創建性能...")
        
        if not self.plugin:
            print("  跳過: 插件不可用")
            return
        
        def create_mvc_components():
            try:
                from PyQt5.QtWidgets import QApplication
                if not QApplication.instance():
                    app = QApplication(sys.argv)
                
                model = self.plugin.create_model()
                view = self.plugin.create_view()
                
                if model and view:
                    controller = self.plugin.create_controller(model, view)
                    
                    # 清理
                    if hasattr(controller, 'cleanup'):
                        controller.cleanup()
                    if hasattr(view, 'deleteLater'):
                        view.deleteLater()
                    if hasattr(model, 'cleanup'):
                        model.cleanup()
                    
                    return True
                return False
                
            except ImportError:
                return "PyQt5 not available"
        
        result = self.measure_memory_usage(create_mvc_components)
        self.results['mvc_creation'] = result
        
        print(f"  MVC 創建時間: {result['execution_time']:.3f}s")
        print(f"  記憶體使用: {result['memory_delta_mb']:.1f}MB")
        print(f"  創建成功: {result['success']}")
    
    def benchmark_search_parameters(self):
        """基準測試: 搜尋參數創建和驗證性能"""
        print("\n測試搜尋參數性能...")
        
        def create_search_params():
            try:
                from tools.ripgrep.core.data_models import SearchParameters
                
                # 創建各種複雜度的搜尋參數
                params_list = []
                
                # 簡單參數
                params_list.append(SearchParameters(
                    pattern="simple_search",
                    search_path=str(self.test_data_dir)
                ))
                
                # 複雜參數
                params_list.append(SearchParameters(
                    pattern=r"\w+@\w+\.\w+",  # 正則表達式
                    search_path=str(self.test_data_dir),
                    case_sensitive=True,
                    whole_words=True,
                    regex_mode=True,
                    context_lines=5,
                    file_types=['*.py', '*.js', '*.txt']
                ))
                
                return len(params_list)
                
            except Exception as e:
                return str(e)
        
        result = self.measure_memory_usage(create_search_params)
        self.results['search_parameters'] = result
        
        print(f"  參數創建時間: {result['execution_time']:.3f}s")
        print(f"  記憶體使用: {result['memory_delta_mb']:.1f}MB")
    
    def benchmark_export_performance(self):
        """基準測試: 匯出功能性能"""
        print("\n測試匯出性能...")
        
        if not self.plugin:
            print("  跳過: 插件不可用")
            return
        
        def test_export():
            try:
                from tools.ripgrep.core.data_models import FileResult, SearchMatch
                
                model = self.plugin.create_model()
                if not model:
                    return False
                
                # 創建大量測試資料
                for i in range(100):  # 100 個檔案結果
                    file_result = FileResult(file_path=f"test_{i}.py")
                    
                    for j in range(10):  # 每個檔案 10 個匹配
                        match = SearchMatch(
                            line_number=j+1,
                            column=0,
                            content=f"test content line {j} in file {i}"
                        )
                        file_result.add_match(match)
                    
                    model.search_results.append(file_result)
                
                # 測試各種格式匯出
                formats = ['json', 'csv', 'txt']
                export_times = {}
                
                for fmt in formats:
                    with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as tmp:
                        start = time.time()
                        success = model.export_results(tmp.name, fmt)
                        export_times[fmt] = time.time() - start
                        
                        if success:
                            file_size = os.path.getsize(tmp.name)
                            export_times[f'{fmt}_size'] = file_size
                        
                        try:
                            os.unlink(tmp.name)
                        except:
                            pass
                
                # 清理
                if hasattr(model, 'cleanup'):
                    model.cleanup()
                
                return export_times
                
            except Exception as e:
                return str(e)
        
        result = self.measure_memory_usage(test_export)
        self.results['export_performance'] = result
        
        if result['success'] and isinstance(result['result'], dict):
            print(f"  匯出測試時間: {result['execution_time']:.3f}s")
            print(f"  記憶體使用: {result['memory_delta_mb']:.1f}MB")
            
            export_times = result['result']
            for fmt in ['json', 'csv', 'txt']:
                if fmt in export_times:
                    size_key = f'{fmt}_size'
                    size_info = f" ({export_times[size_key]} bytes)" if size_key in export_times else ""
                    print(f"    {fmt.upper()}: {export_times[fmt]:.3f}s{size_info}")
        else:
            print(f"  匯出測試失敗: {result['result']}")
    
    def run_all_benchmarks(self):
        """執行所有基準測試"""
        print("=" * 60)
        print("Ripgrep 插件性能基準測試")
        print("=" * 60)
        
        start_time = time.time()
        
        # 創建測試資料集
        total_files, total_lines = self.setup_large_test_dataset(50, 500)  # 較小的資料集以避免超時
        
        # 執行各項基準測試
        self.benchmark_plugin_loading()
        self.benchmark_mvc_creation()
        self.benchmark_search_parameters()
        self.benchmark_export_performance()
        
        total_time = time.time() - start_time
        
        # 生成性能報告
        self.generate_performance_report(total_time, total_files, total_lines)
        
        return self.analyze_performance_results()
    
    def generate_performance_report(self, total_time: float, total_files: int, total_lines: int):
        """生成性能報告"""
        print("\n" + "=" * 60)
        print("性能基準測試報告")
        print("=" * 60)
        
        print(f"測試資料規模: {total_files} 檔案，{total_lines:,} 行")
        print(f"總測試時間: {total_time:.2f}s")
        
        print("\n性能指標摘要:")
        
        for test_name, result in self.results.items():
            if isinstance(result, dict) and 'execution_time' in result:
                time_str = f"{result['execution_time']:.3f}s"
                memory_str = f"{result.get('memory_delta_mb', 0):.1f}MB"
                success_str = "✓" if result.get('success', False) else "✗"
                
                print(f"  {test_name:20s}: {time_str:>8s} | {memory_str:>8s} | {success_str}")
        
        # 性能評估
        print("\n性能評估:")
        
        # 載入時間評估
        if 'plugin_loading' in self.results:
            load_time = self.results['plugin_loading'].get('average_time', 0)
            if load_time < 1.0:
                print("  ✓ 插件載入速度: 優秀 (<1s)")
            elif load_time < 3.0:
                print("  ○ 插件載入速度: 良好 (<3s)")
            else:
                print("  ✗ 插件載入速度: 需要優化 (>3s)")
        
        # MVC 創建評估
        if 'mvc_creation' in self.results:
            mvc_time = self.results['mvc_creation'].get('execution_time', 0)
            if mvc_time < 2.0:
                print("  ✓ MVC 創建速度: 優秀 (<2s)")
            elif mvc_time < 5.0:
                print("  ○ MVC 創建速度: 良好 (<5s)")
            else:
                print("  ✗ MVC 創建速度: 需要優化 (>5s)")
        
        # 記憶體使用評估
        total_memory = sum(r.get('memory_delta_mb', 0) for r in self.results.values() if isinstance(r, dict))
        if total_memory < 50:
            print(f"  ✓ 記憶體使用: 優秀 ({total_memory:.1f}MB)")
        elif total_memory < 100:
            print(f"  ○ 記憶體使用: 良好 ({total_memory:.1f}MB)")
        else:
            print(f"  ✗ 記憶體使用: 需要優化 ({total_memory:.1f}MB)")
    
    def analyze_performance_results(self) -> bool:
        """分析性能結果"""
        # 檢查關鍵性能指標
        issues = []
        
        if 'plugin_loading' in self.results:
            load_time = self.results['plugin_loading'].get('average_time', 0)
            if load_time > 5.0:
                issues.append(f"插件載入時間過長: {load_time:.2f}s")
        
        if 'mvc_creation' in self.results:
            mvc_time = self.results['mvc_creation'].get('execution_time', 0)
            if mvc_time > 10.0:
                issues.append(f"MVC 創建時間過長: {mvc_time:.2f}s")
        
        # 檢查記憶體洩漏
        total_memory = sum(r.get('memory_delta_mb', 0) for r in self.results.values() if isinstance(r, dict))
        if total_memory > 200:
            issues.append(f"記憶體使用過多: {total_memory:.1f}MB")
        
        if issues:
            print(f"\n性能問題:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        return True
    
    def cleanup(self):
        """清理測試環境"""
        if self.test_data_dir and self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            print("\n測試資料清理完成")

def main():
    """主執行函數"""
    benchmark = PerformanceBenchmark()
    
    try:
        success = benchmark.run_all_benchmarks()
        
        print("\n" + "=" * 60)
        if success:
            print("性能基準測試通過！Ripgrep 插件性能符合標準。")
        else:
            print("性能基準測試發現問題，建議進行優化。")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n性能測試執行異常: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        benchmark.cleanup()

if __name__ == "__main__":
    sys.exit(main())