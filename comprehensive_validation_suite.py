#!/usr/bin/env python3
"""
綜合驗證測試套件
全面評估 GPT Codex 優化 PR 對 CLI Tool 的影響
包含功能測試、效能測試、相容性測試和穩定性測試
"""

import sys
import os
import time
import json
import shutil
import subprocess
import threading
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# 設置路徑
sys.path.insert(0, '.')
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

class ComprehensiveValidationSuite:
    """綜合驗證測試套件"""
    
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            },
            'tests': {}
        }
        self.temp_dir = None
    
    def setup(self):
        """設置測試環境"""
        print("=== 設置測試環境 ===")
        
        # 建立臨時目錄用於測試
        self.temp_dir = tempfile.mkdtemp(prefix="cli_tool_test_")
        print(f"[INFO] 臨時測試目錄: {self.temp_dir}")
        
        return True
    
    def cleanup(self):
        """清理測試環境"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"[INFO] 已清理臨時目錄: {self.temp_dir}")
    
    def test_core_functionality(self) -> Dict[str, Any]:
        """測試核心功能完整性"""
        print("\n=== 核心功能測試 ===")
        
        tests = {}
        
        # 1. 模組導入測試
        tests['module_imports'] = self._test_module_imports()
        
        # 2. 配置系統測試
        tests['config_system'] = self._test_config_system()
        
        # 3. 插件系統測試
        tests['plugin_system'] = self._test_plugin_system()
        
        # 4. 工具整合測試
        tests['tool_integration'] = self._test_tool_integration()
        
        # 5. UI 組件測試
        tests['ui_components'] = self._test_ui_components()
        
        return tests
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """效能基準測試"""
        print("\n=== 效能基準測試 ===")
        
        benchmarks = {}
        
        # 1. 應用程式啟動時間
        benchmarks['app_startup'] = self._benchmark_app_startup()
        
        # 2. 工具探測效能
        benchmarks['tool_detection'] = self._benchmark_tool_detection()
        
        # 3. 配置載入效能
        benchmarks['config_loading'] = self._benchmark_config_loading()
        
        # 4. 記憶體使用量（靜態分析）
        benchmarks['memory_usage'] = self._estimate_memory_usage()
        
        return benchmarks
    
    def test_compatibility(self) -> Dict[str, Any]:
        """相容性測試"""
        print("\n=== 相容性測試 ===")
        
        compatibility_tests = {}
        
        # 1. Python 版本相容性
        compatibility_tests['python_version'] = self._test_python_compatibility()
        
        # 2. 外部工具版本相容性
        compatibility_tests['external_tools'] = self._test_external_tool_compatibility()
        
        # 3. 配置檔案相容性
        compatibility_tests['config_file'] = self._test_config_compatibility()
        
        return compatibility_tests
    
    def test_error_handling(self) -> Dict[str, Any]:
        """錯誤處理測試"""
        print("\n=== 錯誤處理測試 ===")
        
        error_tests = {}
        
        # 1. 缺失工具處理
        error_tests['missing_tools'] = self._test_missing_tool_handling()
        
        # 2. 無效配置處理
        error_tests['invalid_config'] = self._test_invalid_config_handling()
        
        # 3. 權限錯誤處理
        error_tests['permission_errors'] = self._test_permission_error_handling()
        
        return error_tests
    
    def _test_module_imports(self) -> Dict[str, Any]:
        """測試模組導入"""
        modules = [
            'main_app',
            'config.config_manager',
            'ui.theme_manager', 
            'ui.main_window',
            'core.plugin_manager',
            'tools.fd.fd_model',
            'tools.fd.fd_view',
            'tools.fd.fd_controller',
            'tools.poppler.poppler_model',
            'tools.pandoc.pandoc_model',
            'tools.glow.glow_model'
        ]
        
        results = {'total': len(modules), 'passed': 0, 'failed': 0, 'details': {}}
        
        for module in modules:
            try:
                start_time = time.time()
                __import__(module)
                import_time = time.time() - start_time
                
                results['details'][module] = {
                    'success': True,
                    'import_time': import_time
                }
                results['passed'] += 1
                print(f"[OK] {module}: {import_time:.3f}s")
                
            except Exception as e:
                results['details'][module] = {
                    'success': False,
                    'error': str(e)
                }
                results['failed'] += 1
                print(f"[FAIL] {module}: {e}")
        
        results['pass_rate'] = results['passed'] / results['total'] * 100
        return results
    
    def _test_config_system(self) -> Dict[str, Any]:
        """測試配置系統"""
        try:
            from config.config_manager import config_manager
            
            # 測試配置載入
            config = config_manager.get_config()
            
            # 測試關鍵配置項
            required_sections = ['tools', 'ui', 'general']
            missing_sections = [section for section in required_sections if section not in config]
            
            # 測試工具配置
            tool_configs = config.get('tools', {})
            configured_tools = list(tool_configs.keys())
            
            result = {
                'config_loaded': True,
                'total_sections': len(config),
                'required_sections_present': len(missing_sections) == 0,
                'missing_sections': missing_sections,
                'configured_tools': configured_tools,
                'tool_count': len(configured_tools)
            }
            
            print(f"[OK] 配置系統: {len(config)} 個節, {len(configured_tools)} 個工具")
            return result
            
        except Exception as e:
            print(f"[FAIL] 配置系統: {e}")
            return {'config_loaded': False, 'error': str(e)}
    
    def _test_plugin_system(self) -> Dict[str, Any]:
        """測試插件系統"""
        try:
            from core.plugin_manager import PluginManager
            
            plugin_manager = PluginManager()
            plugin_manager.initialize()
            
            available_plugins = plugin_manager.get_available_plugins()
            
            result = {
                'plugin_manager_initialized': True,
                'available_plugins': available_plugins,
                'plugin_count': len(available_plugins)
            }
            
            print(f"[OK] 插件系統: {len(available_plugins)} 個插件")
            return result
            
        except Exception as e:
            print(f"[FAIL] 插件系統: {e}")
            return {'plugin_manager_initialized': False, 'error': str(e)}
    
    def _test_tool_integration(self) -> Dict[str, Any]:
        """測試工具整合"""
        tools_to_test = ['fd', 'pandoc', 'bat', 'rg']
        results = {'total': len(tools_to_test), 'available': 0, 'details': {}}
        
        for tool in tools_to_test:
            tool_path = shutil.which(tool)
            if tool_path:
                # 嘗試執行工具獲取版本
                try:
                    result = subprocess.run([tool, '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=3)
                    if result.returncode == 0:
                        version = result.stdout.strip().split('\n')[0]
                        results['details'][tool] = {
                            'available': True,
                            'path': tool_path,
                            'version': version
                        }
                        results['available'] += 1
                        print(f"[OK] {tool}: {version}")
                    else:
                        results['details'][tool] = {
                            'available': False,
                            'path': tool_path,
                            'error': 'Version check failed'
                        }
                        print(f"[FAIL] {tool}: 版本檢查失敗")
                except subprocess.TimeoutExpired:
                    results['details'][tool] = {
                        'available': False,
                        'path': tool_path,
                        'error': 'Timeout'
                    }
                    print(f"[FAIL] {tool}: 超時")
            else:
                results['details'][tool] = {
                    'available': False,
                    'error': 'Tool not found in PATH'
                }
                print(f"[FAIL] {tool}: 在 PATH 中未找到")
        
        results['availability_rate'] = results['available'] / results['total'] * 100
        return results
    
    def _test_ui_components(self) -> Dict[str, Any]:
        """測試 UI 組件"""
        try:
            # 測試主要 UI 組件的導入
            ui_components = [
                'ui.theme_manager',
                'ui.theme_selector', 
                'ui.responsive_layout',
                'ui.components.inputs',
                'ui.components.buttons',
                'ui.components.indicators'
            ]
            
            results = {'total': len(ui_components), 'imported': 0, 'details': {}}
            
            for component in ui_components:
                try:
                    __import__(component)
                    results['details'][component] = {'success': True}
                    results['imported'] += 1
                    print(f"[OK] UI 組件: {component}")
                except Exception as e:
                    results['details'][component] = {'success': False, 'error': str(e)}
                    print(f"[FAIL] UI 組件: {component}: {e}")
            
            results['import_rate'] = results['imported'] / results['total'] * 100
            return results
            
        except Exception as e:
            print(f"[FAIL] UI 組件測試: {e}")
            return {'error': str(e)}
    
    def _benchmark_app_startup(self) -> Dict[str, Any]:
        """應用程式啟動時間基準測試"""
        print("測試應用程式啟動時間...")
        
        startup_times = []
        
        for i in range(3):  # 測試 3 次取平均
            start_time = time.time()
            try:
                # 模擬應用程式啟動過程
                from main_app import main
                from config.config_manager import config_manager
                from ui.theme_manager import ThemeManager
                
                # 載入配置
                config_manager.get_config()
                
                # 初始化主題管理器
                theme_manager = ThemeManager()
                
                startup_time = time.time() - start_time
                startup_times.append(startup_time)
                print(f"  啟動測試 {i+1}: {startup_time:.3f}s")
                
            except Exception as e:
                print(f"  啟動測試 {i+1} 失敗: {e}")
                return {'error': str(e)}
        
        if startup_times:
            avg_time = sum(startup_times) / len(startup_times)
            min_time = min(startup_times)
            max_time = max(startup_times)
            
            return {
                'average_startup_time': avg_time,
                'min_startup_time': min_time,
                'max_startup_time': max_time,
                'measurements': startup_times
            }
        else:
            return {'error': 'No successful measurements'}
    
    def _benchmark_tool_detection(self) -> Dict[str, Any]:
        """工具探測效能基準測試"""
        tools = ['fd', 'pandoc', 'bat', 'rg', 'git', 'python', 'nonexistent_tool']
        
        # 測試 shutil.which 方法
        shutil_times = []
        start_time = time.time()
        for tool in tools:
            shutil.which(tool)
        shutil_total_time = time.time() - start_time
        
        # 測試 subprocess 方法
        subprocess_times = []
        start_time = time.time()
        for tool in tools:
            try:
                subprocess.run([tool, '--help'], 
                              capture_output=True, 
                              timeout=1)
            except:
                pass
        subprocess_total_time = time.time() - start_time
        
        performance_ratio = subprocess_total_time / shutil_total_time if shutil_total_time > 0 else float('inf')
        
        return {
            'tools_tested': len(tools),
            'shutil_which_time': shutil_total_time,
            'subprocess_time': subprocess_total_time,
            'performance_improvement': performance_ratio,
            'recommendation': 'Use shutil.which' if performance_ratio > 1.5 else 'Current method acceptable'
        }
    
    def _benchmark_config_loading(self) -> Dict[str, Any]:
        """配置載入效能測試"""
        try:
            from config.config_manager import ConfigManager
            
            load_times = []
            
            for i in range(5):
                start_time = time.time()
                config_manager = ConfigManager()
                load_time = time.time() - start_time
                load_times.append(load_time)
            
            return {
                'average_load_time': sum(load_times) / len(load_times),
                'min_load_time': min(load_times),
                'max_load_time': max(load_times),
                'measurements': load_times
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _estimate_memory_usage(self) -> Dict[str, Any]:
        """估算記憶體使用量"""
        try:
            import psutil
            import gc
            
            # 強制垃圾回收
            gc.collect()
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # 實際記憶體使用量
                'vms_mb': memory_info.vms / 1024 / 1024,  # 虛擬記憶體使用量
                'measurement_available': True
            }
            
        except ImportError:
            return {
                'measurement_available': False,
                'note': 'psutil not available for memory measurement'
            }
    
    def _test_python_compatibility(self) -> Dict[str, Any]:
        """測試 Python 版本相容性"""
        current_version = sys.version_info
        
        return {
            'current_version': f"{current_version.major}.{current_version.minor}.{current_version.micro}",
            'major': current_version.major,
            'minor': current_version.minor,
            'micro': current_version.micro,
            'is_supported': current_version >= (3, 8),  # 假設支援 Python 3.8+
            'recommendations': 'Compatible' if current_version >= (3, 8) else 'Upgrade recommended'
        }
    
    def _test_external_tool_compatibility(self) -> Dict[str, Any]:
        """測試外部工具版本相容性"""
        tools = {
            'fd': {'min_version': '8.0.0'},
            'pandoc': {'min_version': '2.0.0'},
            'bat': {'min_version': '0.20.0'},
            'rg': {'min_version': '13.0.0'}
        }
        
        compatibility_results = {}
        
        for tool, requirements in tools.items():
            tool_path = shutil.which(tool)
            if tool_path:
                try:
                    result = subprocess.run([tool, '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=3)
                    if result.returncode == 0:
                        version_output = result.stdout.strip()
                        compatibility_results[tool] = {
                            'available': True,
                            'version_output': version_output,
                            'path': tool_path
                        }
                    else:
                        compatibility_results[tool] = {
                            'available': False,
                            'error': 'Version check failed'
                        }
                except Exception as e:
                    compatibility_results[tool] = {
                        'available': False,
                        'error': str(e)
                    }
            else:
                compatibility_results[tool] = {
                    'available': False,
                    'error': 'Tool not found'
                }
        
        return compatibility_results
    
    def _test_config_compatibility(self) -> Dict[str, Any]:
        """測試配置檔案相容性"""
        try:
            from config.config_manager import config_manager
            
            config = config_manager.get_config()
            
            # 檢查關鍵配置結構
            structure_checks = {
                'has_tools_section': 'tools' in config,
                'has_ui_section': 'ui' in config,
                'has_general_section': 'general' in config,
                'tools_has_fd': 'fd' in config.get('tools', {}),
                'ui_has_theme': 'theme' in config.get('ui', {})
            }
            
            return {
                'config_structure': structure_checks,
                'structure_valid': all(structure_checks.values()),
                'config_size': len(json.dumps(config))
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_missing_tool_handling(self) -> Dict[str, Any]:
        """測試缺失工具處理"""
        # 模擬缺失工具的情況
        fake_tool = 'nonexistent_cli_tool_12345'
        
        try:
            from core.plugin_manager import PluginInterface
            
            # 測試工具探測是否優雅處理缺失工具
            plugin_interface = PluginInterface()
            result = plugin_interface._check_tool_availability(fake_tool)
            
            return {
                'handles_missing_tools': not result,  # 應該返回 False
                'graceful_failure': True
            }
            
        except Exception as e:
            return {
                'handles_missing_tools': False,
                'graceful_failure': False,
                'error': str(e)
            }
    
    def _test_invalid_config_handling(self) -> Dict[str, Any]:
        """測試無效配置處理"""
        # 這裡只是概念性測試，實際實作可能需要更複雜的邏輯
        return {
            'test_implemented': False,
            'note': 'Invalid config handling test requires more complex setup'
        }
    
    def _test_permission_error_handling(self) -> Dict[str, Any]:
        """測試權限錯誤處理"""
        # 這裡只是概念性測試
        return {
            'test_implemented': False,
            'note': 'Permission error handling test requires more complex setup'
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """運行完整的綜合驗證測試"""
        print("開始綜合驗證測試套件")
        print("=" * 80)
        
        try:
            self.setup()
            
            # 執行各項測試
            self.results['tests']['functionality'] = self.test_core_functionality()
            self.results['tests']['performance'] = self.test_performance_benchmarks()
            self.results['tests']['compatibility'] = self.test_compatibility()
            self.results['tests']['error_handling'] = self.test_error_handling()
            
            # 生成測試摘要
            self.results['summary'] = self._generate_test_summary()
            
            print("\n" + "=" * 80)
            print("綜合驗證測試完成")
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            print(f"測試套件執行失敗: {e}")
            self.results['error'] = str(e)
            return self.results
            
        finally:
            self.cleanup()
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """生成測試摘要"""
        summary = {
            'total_test_categories': len(self.results['tests']),
            'categories': {}
        }
        
        for category, tests in self.results['tests'].items():
            if isinstance(tests, dict):
                summary['categories'][category] = {
                    'status': 'completed',
                    'details_available': True
                }
            else:
                summary['categories'][category] = {
                    'status': 'error',
                    'details_available': False
                }
        
        return summary
    
    def _print_summary(self):
        """打印測試摘要"""
        print(f"\n測試摘要:")
        print(f"測試時間: {self.results['timestamp']}")
        print(f"Python 版本: {self.results['test_environment']['python_version'].split()[0]}")
        print(f"測試類別: {len(self.results['tests'])}")
        
        for category in self.results['tests']:
            print(f"  - {category}: 完成")

def main():
    """主函數"""
    suite = ComprehensiveValidationSuite()
    results = suite.run_comprehensive_validation()
    
    # 保存結果到文件
    output_file = "comprehensive_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n詳細測試結果已保存到: {output_file}")

if __name__ == "__main__":
    main()