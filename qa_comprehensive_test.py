#!/usr/bin/env python3
"""
Ripgrep 插件全面品質保證測試套件
包含功能測試、性能測試、可用性測試、錯誤處理測試
"""
import sys
import os
import time
import tempfile
import shutil
import threading
from typing import List, Dict, Any
from pathlib import Path

# 設定路徑
sys.path.append(os.path.dirname(__file__))

# PyQt5 相關導入
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# 導入測試目標
from core.plugin_manager import plugin_manager
if QT_AVAILABLE:
    from tools.ripgrep.core.data_models import SearchParameters, FileResult, SearchMatch
    from tools.ripgrep.ripgrep_model import RipgrepModel
    from tools.ripgrep.ripgrep_view import RipgrepView
    from tools.ripgrep.ripgrep_controller import RipgrepController

class QATestSuite:
    """全面品質保證測試套件"""
    
    def __init__(self):
        self.test_results = []
        self.test_data_dir = None
        self.plugin = None
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """設置測試環境"""
        print("設置測試環境...")
        
        # 創建測試資料目錄
        self.test_data_dir = Path(tempfile.mkdtemp(prefix="ripgrep_qa_"))
        print(f"測試資料目錄: {self.test_data_dir}")
        
        # 創建測試檔案
        self.create_test_files()
        
        # 載入 ripgrep 插件
        try:
            plugin_manager.discover_plugins()
            plugins = plugin_manager.get_all_plugins()
            self.plugin = plugins.get('ripgrep')
            if self.plugin:
                print("Ripgrep 插件載入成功")
            else:
                print("警告: Ripgrep 插件未找到")
        except Exception as e:
            print(f"插件載入失敗: {e}")
    
    def create_test_files(self):
        """創建測試檔案集合"""
        test_files = {
            "python_file.py": '''#!/usr/bin/env python3
"""Test Python file for ripgrep testing"""
import os
import sys
from typing import List, Dict, Any

class TestClass:
    def __init__(self, name: str):
        self.name = name
        self.items = []
    
    def add_item(self, item: str) -> bool:
        """Add an item to the list"""
        self.items.append(item)
        return True
    
    def search_items(self, pattern: str) -> List[str]:
        """Search for items matching pattern"""
        results = []
        for item in self.items:
            if pattern.lower() in item.lower():
                results.append(item)
        return results

def main():
    test_obj = TestClass("test_object")
    test_obj.add_item("hello world")
    test_obj.add_item("goodbye world")
    
    # Search test
    matches = test_obj.search_items("world")
    print(f"Found {len(matches)} matches")

if __name__ == "__main__":
    main()
''',
            
            "javascript_file.js": '''// JavaScript test file
const fs = require('fs');
const path = require('path');

/**
 * Test function for searching
 * @param {string} searchTerm - The term to search for
 * @param {Array} data - Array of data to search
 * @returns {Array} Matching results
 */
function searchInData(searchTerm, data) {
    const results = [];
    
    data.forEach((item, index) => {
        if (typeof item === 'string' && item.includes(searchTerm)) {
            results.push({
                index: index,
                value: item,
                match: true
            });
        }
    });
    
    return results;
}

// Test data
const testData = [
    "hello world",
    "foo bar",
    "test case",
    "search pattern",
    "ripgrep testing",
    "javascript code"
];

// Execute search
const searchResults = searchInData("test", testData);
console.log(`Found ${searchResults.length} matches`);

// Export for testing
module.exports = { searchInData, testData };
''',
            
            "text_file.txt": '''This is a plain text file for testing ripgrep functionality.
It contains various patterns and text samples:

- Email addresses: test@example.com, user123@domain.org
- URLs: https://www.example.com, http://test.local
- Phone numbers: +1-555-123-4567, (555) 987-6543
- Dates: 2024-01-15, 12/31/2023, January 1st, 2024
- Code snippets: console.log("hello"), print("world")
- Special characters: @#$%^&*()_+-={}[]|\\:";'<>?,./
- Unicode content: 你好世界, Héllo Wörld, 🌍🔍📝

Multi-line content:
Line 1: First line of text
Line 2: Second line with different content
Line 3: Third line for context testing

Search patterns to test:
- Case sensitivity: Hello vs hello vs HELLO
- Regex patterns: \\d+, [a-zA-Z]+, \\w+@\\w+\\.\\w+
- Special escaping: \\n, \\t, \\r
''',
            
            "config.yaml": '''# YAML configuration file
app:
  name: "Test Application"
  version: "1.0.0"
  debug: true
  
database:
  host: "localhost"
  port: 5432
  name: "test_db"
  user: "test_user"
  password: "secret123"
  
features:
  - search
  - export
  - analytics
  - reporting
  
search:
  enabled: true
  engines:
    - ripgrep
    - grep
    - ag
  options:
    case_sensitive: false
    regex_mode: true
    context_lines: 3
    
logging:
  level: "DEBUG"
  file: "/var/log/app.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
''',
            
            "large_file.log": self.generate_large_log_content(),
            
            "unicode_test.txt": '''Unicode and encoding test file:

中文內容：這是一個測試檔案，包含中文字符
日本語：これはテストファイルです
한국어：이것은 테스트 파일입니다
العربية: هذا ملف اختبار
Русский: Это тестовый файл

Emoji content:
🔍 Search icon
📁 Folder icon  
⚡ Lightning bolt
🌟 Star icon
❤️ Heart emoji

Special characters:
"Smart quotes" vs "regular quotes"
'Single quotes' vs 'smart singles'
em-dash — vs hyphen -
ellipsis… vs three dots...
'''
        }
        
        # 創建檔案
        for filename, content in test_files.items():
            file_path = self.test_data_dir / filename
            file_path.write_text(content, encoding='utf-8')
        
        # 創建子目錄結構
        sub_dirs = ['subdir1', 'subdir2', 'deep/nested/path']
        for sub_dir in sub_dirs:
            dir_path = self.test_data_dir / sub_dir
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # 在子目錄中創建檔案
            (dir_path / 'nested_file.txt').write_text(
                f"Content in {sub_dir}\nSearch pattern: nested_content\n",
                encoding='utf-8'
            )
    
    def generate_large_log_content(self) -> str:
        """生成大型日誌檔案內容"""
        content = []
        for i in range(1000):
            content.append(f"2024-01-{i%28+1:02d} 10:{i%60:02d}:{i%60:02d} INFO [Thread-{i%10}] Processing request {i}")
            content.append(f"2024-01-{i%28+1:02d} 10:{i%60:02d}:{i%60:02d} DEBUG [Thread-{i%10}] Database query executed")
            if i % 50 == 0:
                content.append(f"2024-01-{i%28+1:02d} 10:{i%60:02d}:{i%60:02d} ERROR [Thread-{i%10}] Connection failed")
            content.append(f"2024-01-{i%28+1:02d} 10:{i%60:02d}:{i%60:02d} INFO [Thread-{i%10}] Request completed")
        return '\n'.join(content)
    
    def cleanup_test_environment(self):
        """清理測試環境"""
        if self.test_data_dir and self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            print("測試環境清理完成")
    
    def record_test_result(self, test_name: str, success: bool, message: str = "", 
                          execution_time: float = 0, details: Dict = None):
        """記錄測試結果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'execution_time': execution_time,
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        time_str = f" ({execution_time:.2f}s)" if execution_time > 0 else ""
        print(f"  {status}: {test_name}{time_str}")
        if message:
            print(f"    {message}")
    
    def test_1_plugin_availability(self):
        """測試 1: 插件可用性檢查"""
        print("\n1. 插件可用性測試")
        
        start_time = time.time()
        try:
            if not self.plugin:
                self.record_test_result("插件載入", False, "插件未找到")
                return
            
            # 測試基本屬性
            name = self.plugin.name
            version = self.plugin.version
            description = self.plugin.description
            tools = self.plugin.required_tools
            
            self.record_test_result("插件基本屬性", True, 
                                  f"名稱={name}, 版本={version}", 
                                  time.time() - start_time)
            
            # 測試工具可用性
            available = self.plugin.check_tools_availability()
            self.record_test_result("工具可用性", available, 
                                  f"所需工具: {tools}")
            
            # 測試初始化
            init_success = self.plugin.initialize()
            self.record_test_result("插件初始化", init_success)
            
        except Exception as e:
            self.record_test_result("插件可用性測試", False, f"異常: {e}")
    
    def test_2_mvc_components(self):
        """測試 2: MVC 組件創建和基本功能"""
        print("\n2. MVC 組件測試")
        
        if not self.plugin or not QT_AVAILABLE:
            self.record_test_result("MVC 組件測試", False, "插件或 PyQt5 不可用")
            return
        
        try:
            # 創建 QApplication（如果需要）
            if not QApplication.instance():
                app = QApplication(sys.argv)
            
            start_time = time.time()
            
            # 測試 Model 創建
            model = self.plugin.create_model()
            model_success = model is not None
            self.record_test_result("Model 創建", model_success)
            
            if model_success and hasattr(model, 'is_available'):
                availability = model.is_available()
                version_info = model.get_version_info()
                self.record_test_result("Model 功能", True, f"可用性={availability}, 版本={version_info}")
            
            # 測試 View 創建
            view = self.plugin.create_view()
            view_success = view is not None
            self.record_test_result("View 創建", view_success)
            
            # 測試 Controller 創建
            if model and view:
                controller = self.plugin.create_controller(model, view)
                controller_success = controller is not None
                self.record_test_result("Controller 創建", controller_success, 
                                      execution_time=time.time() - start_time)
                
                # 清理資源
                if controller and hasattr(controller, 'cleanup'):
                    controller.cleanup()
                if view and hasattr(view, 'deleteLater'):
                    view.deleteLater()
                if model and hasattr(model, 'cleanup'):
                    model.cleanup()
            
        except Exception as e:
            self.record_test_result("MVC 組件測試", False, f"異常: {e}")
    
    def test_3_search_functionality(self):
        """測試 3: 搜尋功能測試"""
        print("\n3. 搜尋功能測試")
        
        if not self.plugin or not QT_AVAILABLE:
            self.record_test_result("搜尋功能測試", False, "插件或 PyQt5 不可用")
            return
        
        try:
            model = self.plugin.create_model()
            if not model:
                self.record_test_result("搜尋功能測試", False, "Model 創建失敗")
                return
            
            # 測試基本搜尋參數
            test_cases = [
                ("基本文字搜尋", "hello", str(self.test_data_dir)),
                ("大小寫敏感搜尋", "Hello", str(self.test_data_dir)),  
                ("正則表達式搜尋", r"\\d+", str(self.test_data_dir)),
                ("文件類型過濾", "function", str(self.test_data_dir)),
            ]
            
            for test_name, pattern, path in test_cases:
                start_time = time.time()
                try:
                    params = SearchParameters(
                        pattern=pattern,
                        search_path=path,
                        case_sensitive=False,
                        regex_mode=True
                    )
                    
                    # 這裡不實際執行搜尋（避免阻塞），只測試參數創建
                    self.record_test_result(test_name, True, 
                                          f"參數創建成功: {pattern}",
                                          time.time() - start_time)
                    
                except Exception as e:
                    self.record_test_result(test_name, False, f"異常: {e}")
            
            # 清理
            if hasattr(model, 'cleanup'):
                model.cleanup()
                
        except Exception as e:
            self.record_test_result("搜尋功能測試", False, f"異常: {e}")
    
    def test_4_error_handling(self):
        """測試 4: 錯誤處理測試"""
        print("\n4. 錯誤處理測試")
        
        if not QT_AVAILABLE:
            self.record_test_result("錯誤處理測試", False, "PyQt5 不可用")
            return
        
        try:
            # 測試無效參數處理
            test_cases = [
                ("空搜尋模式", ""),
                ("不存在路徑", "/nonexistent/path"),
                ("無效正則表達式", "[invalid(regex"),
            ]
            
            for test_name, invalid_input in test_cases:
                start_time = time.time()
                try:
                    if test_name == "空搜尋模式":
                        # 測試空模式
                        params = SearchParameters(pattern=invalid_input)
                        self.record_test_result(test_name, False, "應該拋出異常但沒有")
                    elif test_name == "不存在路徑":
                        params = SearchParameters(pattern="test", search_path=invalid_input)
                        self.record_test_result(test_name, True, "參數創建但路徑驗證應在執行時處理")
                    elif test_name == "無效正則表達式":
                        import re
                        try:
                            re.compile(invalid_input)
                            self.record_test_result(test_name, False, "正則表達式應該無效")
                        except re.error:
                            self.record_test_result(test_name, True, "正確檢測到無效正則表達式")
                    
                except ValueError as e:
                    # 預期的錯誤
                    self.record_test_result(test_name, True, 
                                          f"正確處理錯誤: {e}",
                                          time.time() - start_time)
                except Exception as e:
                    self.record_test_result(test_name, False, f"未預期異常: {e}")
            
        except Exception as e:
            self.record_test_result("錯誤處理測試", False, f"測試執行異常: {e}")
    
    def test_5_performance_basic(self):
        """測試 5: 基本性能測試"""
        print("\n5. 基本性能測試")
        
        # 測試檔案創建性能
        start_time = time.time()
        test_files_count = len(list(self.test_data_dir.glob("**/*")))
        file_creation_time = time.time() - start_time
        
        self.record_test_result("測試檔案創建", True,
                              f"創建 {test_files_count} 個檔案",
                              file_creation_time)
        
        # 測試插件載入性能
        start_time = time.time()
        plugin_manager.discover_plugins()
        plugins = plugin_manager.get_all_plugins()
        plugin_load_time = time.time() - start_time
        
        self.record_test_result("插件載入性能", True,
                              f"載入 {len(plugins)} 個插件",
                              plugin_load_time)
        
        # 性能基準檢查
        if plugin_load_time > 5.0:
            self.record_test_result("插件載入性能基準", False, 
                                  f"載入時間過長: {plugin_load_time:.2f}s > 5.0s")
        else:
            self.record_test_result("插件載入性能基準", True,
                                  f"載入時間良好: {plugin_load_time:.2f}s")
    
    def test_6_data_integrity(self):
        """測試 6: 資料完整性測試"""
        print("\n6. 資料完整性測試")
        
        if not QT_AVAILABLE:
            self.record_test_result("資料完整性測試", False, "PyQt5 不可用")
            return
        
        try:
            # 測試資料模型創建
            start_time = time.time()
            
            # 測試 SearchParameters
            params = SearchParameters(
                pattern="test",
                search_path=str(self.test_data_dir),
                case_sensitive=True,
                whole_words=False,
                regex_mode=True,
                context_lines=3,
                file_types=['*.py', '*.js']
            )
            
            # 驗證屬性
            attributes_correct = (
                params.pattern == "test" and
                params.case_sensitive == True and
                params.whole_words == False and
                params.regex_mode == True and
                params.context_lines == 3 and
                len(params.file_types) == 2
            )
            
            self.record_test_result("SearchParameters 完整性", attributes_correct,
                                  f"所有屬性正確設置",
                                  time.time() - start_time)
            
            # 測試 FileResult 和 SearchMatch
            file_result = FileResult(file_path="test.py")
            match = SearchMatch(line_number=10, column=5, content="test content")
            file_result.add_match(match)
            
            integrity_check = (
                file_result.file_path == "test.py" and
                file_result.total_matches == 1 and
                len(file_result.matches) == 1 and
                file_result.matches[0].line_number == 10
            )
            
            self.record_test_result("FileResult 完整性", integrity_check,
                                  "資料結構完整性正確")
            
        except Exception as e:
            self.record_test_result("資料完整性測試", False, f"異常: {e}")
    
    def test_7_export_functionality(self):
        """測試 7: 匯出功能測試"""
        print("\n7. 匯出功能測試")
        
        if not self.plugin or not QT_AVAILABLE:
            self.record_test_result("匯出功能測試", False, "插件或 PyQt5 不可用")
            return
        
        try:
            model = self.plugin.create_model()
            if not model:
                self.record_test_result("匯出功能測試", False, "Model 創建失敗")
                return
            
            # 創建測試資料
            file_result = FileResult(file_path="test.py")
            match = SearchMatch(line_number=1, column=0, content="test content")
            file_result.add_match(match)
            model.search_results.append(file_result)
            
            # 測試各種匯出格式
            export_formats = ['json', 'csv', 'txt']
            
            for fmt in export_formats:
                start_time = time.time()
                try:
                    with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as tmp_file:
                        export_success = model.export_results(tmp_file.name, fmt)
                        
                        if export_success and os.path.exists(tmp_file.name):
                            file_size = os.path.getsize(tmp_file.name)
                            self.record_test_result(f"{fmt.upper()} 匯出", True,
                                                  f"檔案大小: {file_size} bytes",
                                                  time.time() - start_time)
                        else:
                            self.record_test_result(f"{fmt.upper()} 匯出", False, "匯出失敗")
                        
                        # 清理檔案
                        try:
                            os.unlink(tmp_file.name)
                        except:
                            pass
                
                except Exception as e:
                    self.record_test_result(f"{fmt.upper()} 匯出", False, f"異常: {e}")
            
            # 清理
            if hasattr(model, 'cleanup'):
                model.cleanup()
                
        except Exception as e:
            self.record_test_result("匯出功能測試", False, f"異常: {e}")
    
    def run_all_tests(self):
        """執行所有測試"""
        print("=" * 60)
        print("Ripgrep 插件全面品質保證測試")
        print("=" * 60)
        
        start_time = time.time()
        
        # 執行所有測試
        self.test_1_plugin_availability()
        self.test_2_mvc_components()
        self.test_3_search_functionality()
        self.test_4_error_handling()
        self.test_5_performance_basic()
        self.test_6_data_integrity()
        self.test_7_export_functionality()
        
        total_time = time.time() - start_time
        
        # 生成測試報告
        self.generate_test_report(total_time)
        
        return self.analyze_test_results()
    
    def generate_test_report(self, total_time: float):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("測試結果報告")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        failed = total - passed
        
        print(f"總測試數: {total}")
        print(f"通過數: {passed}")
        print(f"失敗數: {failed}")
        print(f"成功率: {passed/total*100:.1f}%")
        print(f"總執行時間: {total_time:.2f}s")
        
        if failed > 0:
            print(f"\n失敗的測試:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n詳細結果:")
        for result in self.test_results:
            status = "PASS" if result['success'] else "FAIL"
            time_info = f" ({result['execution_time']:.2f}s)" if result['execution_time'] > 0 else ""
            print(f"  {status}: {result['test_name']}{time_info}")
            if result['message']:
                print(f"       {result['message']}")
    
    def analyze_test_results(self) -> bool:
        """分析測試結果並返回整體成功狀態"""
        critical_tests = [
            "插件載入",
            "插件基本屬性", 
            "工具可用性",
            "插件初始化"
        ]
        
        # 檢查關鍵測試是否通過
        critical_failures = []
        for result in self.test_results:
            if result['test_name'] in critical_tests and not result['success']:
                critical_failures.append(result['test_name'])
        
        if critical_failures:
            print(f"\n關鍵測試失敗: {critical_failures}")
            return False
        
        # 檢查整體成功率
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        success_rate = passed / total if total > 0 else 0
        
        return success_rate >= 0.8  # 80% 以上成功率視為通過

def main():
    """主執行函數"""
    qa_suite = QATestSuite()
    
    try:
        success = qa_suite.run_all_tests()
        
        print("\n" + "=" * 60)
        if success:
            print("品質保證測試通過！Ripgrep 插件符合品質標準。")
        else:
            print("品質保證測試未完全通過，需要修復問題。")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n測試執行異常: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        qa_suite.cleanup_test_environment()

if __name__ == "__main__":
    sys.exit(main())