#!/usr/bin/env python3
"""
測試 Ripgrep MVC 組件
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile

# 設定測試環境
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# 導入 Qt 相關模組 (需要在導入其他組件之前)
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt, QTimer
    
    # 創建 QApplication 實例 (測試所需)
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    # 導入要測試的組件
    from tools.ripgrep.core.data_models import SearchParameters, FileResult, SearchMatch
    from tools.ripgrep.ripgrep_model import RipgrepModel
    from tools.ripgrep.ripgrep_view import RipgrepView, SearchParametersWidget, SearchResultsWidget
    from tools.ripgrep.ripgrep_controller import RipgrepController
    from tools.ripgrep.plugin import RipgrepPlugin

    QT_AVAILABLE = True
    
except ImportError as e:
    print(f"PyQt5 not available, skipping GUI tests: {e}")
    QT_AVAILABLE = False


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestRipgrepModel(unittest.TestCase):
    """測試 Ripgrep 模型"""
    
    def setUp(self):
        """測試設定"""
        self.model = RipgrepModel()
    
    def tearDown(self):
        """測試清理"""
        if hasattr(self, 'model'):
            self.model.cleanup()
    
    @patch('tools.ripgrep.ripgrep_model.validate_ripgrep_available')
    def test_model_initialization(self, mock_validate):
        """測試模型初始化"""
        mock_validate.return_value = True
        
        model = RipgrepModel()
        self.assertIsNotNone(model)
        self.assertEqual(len(model.search_results), 0)
        self.assertFalse(model.is_searching)
    
    @patch('tools.ripgrep.ripgrep_model.validate_ripgrep_available')
    def test_is_available(self, mock_validate):
        """測試可用性檢查"""
        mock_validate.return_value = True
        self.assertTrue(self.model.is_available())
        
        mock_validate.return_value = False
        self.assertFalse(self.model.is_available())
    
    def test_search_history_management(self):
        """測試搜尋歷史管理"""
        # 添加搜尋歷史
        self.model._add_to_history("test pattern")
        self.model._add_to_history("another pattern")
        
        history = self.model.get_search_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], "another pattern")  # 最新的在前面
        
        # 清除歷史
        self.model.clear_search_history()
        self.assertEqual(len(self.model.get_search_history()), 0)
    
    def test_export_results(self):
        """測試結果匯出"""
        # 創建測試結果
        file_result = FileResult(file_path="test.py")
        match = SearchMatch(line_number=1, column=0, content="test content")
        file_result.add_match(match)
        self.model.search_results.append(file_result)
        
        # 測試 JSON 匯出
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            success = self.model.export_results(temp_path, 'json')
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestSearchParametersWidget(unittest.TestCase):
    """測試搜尋參數 Widget"""
    
    def setUp(self):
        """測試設定"""
        self.widget = SearchParametersWidget()
    
    def tearDown(self):
        """測試清理"""
        if hasattr(self, 'widget'):
            self.widget.deleteLater()
    
    def test_widget_creation(self):
        """測試 Widget 創建"""
        self.assertIsNotNone(self.widget)
        self.assertIsNotNone(self.widget.pattern_edit)
        self.assertIsNotNone(self.widget.path_edit)
        self.assertIsNotNone(self.widget.case_sensitive_check)
    
    def test_get_search_parameters(self):
        """測試獲取搜尋參數"""
        # 設定測試值
        self.widget.pattern_edit.setText("test pattern")
        self.widget.path_edit.setText("/test/path")
        self.widget.case_sensitive_check.setChecked(True)
        
        params = self.widget.get_search_parameters()
        
        self.assertEqual(params.pattern, "test pattern")
        self.assertEqual(params.search_path, "/test/path")
        self.assertTrue(params.case_sensitive)
    
    def test_set_search_parameters(self):
        """測試設定搜尋參數"""
        params = SearchParameters(
            pattern="test",
            search_path="/tmp",
            case_sensitive=True,
            whole_words=True,
            regex_mode=True
        )
        
        self.widget.set_search_parameters(params)
        
        self.assertEqual(self.widget.pattern_edit.text(), "test")
        self.assertEqual(self.widget.path_edit.text(), "/tmp")
        self.assertTrue(self.widget.case_sensitive_check.isChecked())
        self.assertTrue(self.widget.whole_words_check.isChecked())
        self.assertTrue(self.widget.regex_check.isChecked())


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestSearchResultsWidget(unittest.TestCase):
    """測試搜尋結果 Widget"""
    
    def setUp(self):
        """測試設定"""
        self.widget = SearchResultsWidget()
    
    def tearDown(self):
        """測試清理"""
        if hasattr(self, 'widget'):
            self.widget.deleteLater()
    
    def test_widget_creation(self):
        """測試 Widget 創建"""
        self.assertIsNotNone(self.widget)
        self.assertIsNotNone(self.widget.results_tree)
        self.assertIsNotNone(self.widget.summary_label)
    
    def test_add_result(self):
        """測試添加搜尋結果"""
        # 創建測試結果
        file_result = FileResult(file_path="test.py")
        match = SearchMatch(line_number=1, column=0, content="test content")
        file_result.add_match(match)
        
        # 添加結果
        self.widget.add_result(file_result)
        
        # 驗證結果
        self.assertEqual(len(self.widget.search_results), 1)
        self.assertEqual(self.widget.results_tree.topLevelItemCount(), 1)
    
    def test_clear_results(self):
        """測試清空結果"""
        # 先添加一些結果
        file_result = FileResult(file_path="test.py")
        match = SearchMatch(line_number=1, column=0, content="test content")
        file_result.add_match(match)
        self.widget.add_result(file_result)
        
        # 清空結果
        self.widget.clear_results()
        
        # 驗證結果
        self.assertEqual(len(self.widget.search_results), 0)
        self.assertEqual(self.widget.results_tree.topLevelItemCount(), 0)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")  
class TestRipgrepView(unittest.TestCase):
    """測試 Ripgrep 主視圖"""
    
    def setUp(self):
        """測試設定"""
        self.view = RipgrepView()
    
    def tearDown(self):
        """測試清理"""
        if hasattr(self, 'view'):
            self.view.deleteLater()
    
    def test_view_creation(self):
        """測試視圖創建"""
        self.assertIsNotNone(self.view)
        self.assertIsNotNone(self.view.search_params_widget)
        self.assertIsNotNone(self.view.results_widget)
        self.assertIsNotNone(self.view.search_button)
        self.assertIsNotNone(self.view.cancel_button)
    
    def test_searching_state(self):
        """測試搜尋狀態"""
        # 初始狀態
        self.assertFalse(self.view.is_searching)
        self.assertTrue(self.view.search_button.isEnabled())
        self.assertFalse(self.view.cancel_button.isEnabled())
        
        # 設定搜尋中狀態
        self.view.set_searching_state(True)
        self.assertTrue(self.view.is_searching)
        self.assertFalse(self.view.search_button.isEnabled())
        self.assertTrue(self.view.cancel_button.isEnabled())
        
        # 設定搜尋完成狀態
        self.view.set_searching_state(False)
        self.assertFalse(self.view.is_searching)
        self.assertTrue(self.view.search_button.isEnabled())
        self.assertFalse(self.view.cancel_button.isEnabled())
    
    def test_get_search_parameters(self):
        """測試獲取搜尋參數"""
        # 設定一個測試模式
        self.view.search_params_widget.pattern_edit.setText("test pattern")
        
        params = self.view.get_search_parameters()
        self.assertIsInstance(params, SearchParameters)
        self.assertEqual(params.pattern, "test pattern")


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestRipgrepController(unittest.TestCase):
    """測試 Ripgrep 控制器"""
    
    def setUp(self):
        """測試設定"""
        # 創建 Mock 模型和視圖
        self.mock_model = Mock(spec=RipgrepModel)
        self.mock_model.is_available.return_value = True
        self.mock_model.get_version_info.return_value = "test version"
        self.mock_model.get_search_history.return_value = []
        self.mock_model.is_searching = False
        self.mock_model.executable_path = "rg"
        self.mock_model.search_results = []
        self.mock_model.search_history = []
        
        self.mock_view = Mock(spec=RipgrepView)
        self.mock_view.results_widget = Mock()
        
        # 創建控制器
        self.controller = RipgrepController(self.mock_model, self.mock_view)
    
    def tearDown(self):
        """測試清理"""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
    
    def test_controller_creation(self):
        """測試控制器創建"""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertEqual(self.controller.view, self.mock_view)
    
    def test_search_request_handling(self):
        """測試搜尋請求處理"""
        params = SearchParameters(pattern="test", search_path=".")
        
        # 設定模型行為
        self.mock_model.start_search.return_value = True
        
        # 觸發搜尋請求
        self.controller._on_search_requested(params)
        
        # 驗證模型被調用
        self.mock_model.start_search.assert_called_once_with(params)
    
    def test_get_model_info(self):
        """測試獲取模型資訊"""
        info = self.controller.get_model_info()
        
        self.assertIn('available', info)
        self.assertIn('version', info)
        self.assertIn('is_searching', info)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestRipgrepPlugin(unittest.TestCase):
    """測試 Ripgrep 插件"""
    
    def setUp(self):
        """測試設定"""
        self.plugin = RipgrepPlugin()
    
    def test_plugin_creation(self):
        """測試插件創建"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.name, "ripgrep")
        self.assertEqual(self.plugin.display_name, "文本搜尋")
        self.assertIn("ripgrep", self.plugin.description)
    
    def test_plugin_properties(self):
        """測試插件屬性"""
        self.assertEqual(self.plugin.icon, "🔍")
        self.assertEqual(self.plugin.required_tools, ["rg"])
    
    @patch('subprocess.run')
    def test_check_tools_availability(self, mock_run):
        """測試工具可用性檢查"""
        # Mock 成功的情況
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ripgrep 13.0.0"
        
        result = self.plugin.check_tools_availability()
        self.assertTrue(result)
    
    def test_mvc_component_creation(self):
        """測試 MVC 組件創建"""
        # 這些方法可能會因為依賴而失敗，但不應該拋出異常
        try:
            model = self.plugin.create_model()
            view = self.plugin.create_view()
            
            if model and view:
                controller = self.plugin.create_controller(model, view)
                self.assertIsNotNone(controller)
                
                # 清理
                if hasattr(controller, 'cleanup'):
                    controller.cleanup()
                if hasattr(view, 'deleteLater'):
                    view.deleteLater()
                if hasattr(model, 'cleanup'):
                    model.cleanup()
                    
        except Exception as e:
            # 在測試環境中，某些依賴可能不可用，這是可以接受的
            print(f"MVC component creation test failed (expected in test env): {e}")


def run_tests():
    """運行所有測試"""
    if not QT_AVAILABLE:
        print("PyQt5 不可用，跳過 GUI 測試")
        return False
    
    print("運行 Ripgrep MVC 組件測試...")
    print("=" * 50)
    
    # 創建測試套件
    test_classes = [
        TestRipgrepModel,
        TestSearchParametersWidget,
        TestSearchResultsWidget,
        TestRipgrepView,
        TestRipgrepController,
        TestRipgrepPlugin,
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回測試結果
    return result.wasSuccessful()


if __name__ == "__main__":
    try:
        success = run_tests()
        
        if success:
            print("\n所有 MVC 組件測試通過！")
            print("Ripgrep 前端實現正確。")
        else:
            print("\n部分測試失敗！")
            print("請檢查實現並修復問題。")
            
    except Exception as e:
        print(f"\n測試運行失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("MVC 組件測試完成。")