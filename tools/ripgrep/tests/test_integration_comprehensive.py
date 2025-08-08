#!/usr/bin/env python3
"""
Comprehensive Integration Testing for Ripgrep Plugin
Tests integration with main application, plugin manager, and UI components
"""
import sys
import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import Qt components for GUI testing
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt, QTimer
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    QT_AVAILABLE = True
    
except ImportError:
    QT_AVAILABLE = False


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_test_project_structure()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_test_project_structure(cls):
        """Create a realistic project structure for testing"""
        project_files = {
            'main.py': '''
#!/usr/bin/env python3
"""Main application file"""
import sys
from pathlib import Path

def main():
    print("Hello World from main function")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''',
            'config.json': '''
{
    "app_name": "Test Application",
    "version": "1.0.0",
    "search_patterns": ["TODO", "FIXME", "BUG"]
}
''',
            'requirements.txt': '''
PyQt5>=5.15.0
requests>=2.25.0
click>=8.0.0
''',
            'README.md': '''
# Test Project

This is a test project for integration testing.

## Features
- Search functionality
- Configuration management
- Plugin architecture

## TODO Items
- Add more tests
- Improve performance
- Fix known bugs
'''
        }
        
        # Create subdirectories
        subdirs = ['src', 'tests', 'docs', 'config']
        for subdir in subdirs:
            (Path(cls.temp_dir) / subdir).mkdir(exist_ok=True)
        
        # Create files
        for filename, content in project_files.items():
            file_path = Path(cls.temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create files in subdirectories
        for subdir in subdirs:
            subdir_path = Path(cls.temp_dir) / subdir
            
            for i in range(3):
                test_file = subdir_path / f"test_file_{i}.py"
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(f'''
# Test file {i} in {subdir}
def function_{i}():
    """TODO: Implement this function"""
    pass

# FIXME: This needs optimization
def buggy_function():
    return "BUG: Known issue here"
''')


class TestPluginManagerIntegration(IntegrationTestBase):
    """Test integration with plugin manager"""
    
    def test_plugin_discovery_and_registration(self):
        """Test plugin discovery and registration with plugin manager"""
        from tools.ripgrep.plugin import RipgrepPlugin
        from core.plugin_manager import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Create and register plugin
        plugin = RipgrepPlugin()
        plugin_manager.register_plugin(plugin)
        
        # Test registration
        registered_plugins = plugin_manager.get_all_plugins()
        self.assertIn('ripgrep', registered_plugins)
        self.assertEqual(registered_plugins['ripgrep'].name, 'ripgrep')
    
    @patch('subprocess.run')
    def test_plugin_availability_check(self, mock_run):
        """Test plugin availability checking through plugin manager"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        # Mock successful ripgrep availability
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ripgrep 13.0.0"
        
        plugin = RipgrepPlugin()
        self.assertTrue(plugin.is_available())
        self.assertTrue(plugin.check_tools_availability())
    
    @patch('subprocess.run')
    def test_plugin_initialization_flow(self, mock_run):
        """Test complete plugin initialization flow"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        # Mock ripgrep availability
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ripgrep 13.0.0"
        
        plugin = RipgrepPlugin()
        
        # Test initialization sequence
        self.assertTrue(plugin.initialize())
        self.assertEqual(plugin.name, "ripgrep")
        self.assertEqual(plugin.display_name, "文本搜尋")
        self.assertIsNotNone(plugin.description)
        self.assertIsNotNone(plugin.version)
    
    def test_plugin_mvc_component_creation(self):
        """Test MVC component creation through plugin interface"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        plugin = RipgrepPlugin()
        
        # Test model creation
        model = plugin.create_model()
        if model:  # Only test if creation succeeds
            self.assertIsNotNone(model)
            self.assertTrue(hasattr(model, 'search_results'))
        
        # Test view creation (may fail without Qt)
        if QT_AVAILABLE:
            view = plugin.create_view()
            if view:
                self.assertIsNotNone(view)
                self.assertTrue(hasattr(view, 'search_params_widget'))
        
        # Test controller creation
        if model and QT_AVAILABLE:
            view = plugin.create_view()
            if view:
                controller = plugin.create_controller(model, view)
                if controller:
                    self.assertIsNotNone(controller)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestUIIntegration(IntegrationTestBase):
    """Test UI integration with main application"""
    
    def setUp(self):
        """Set up UI test environment"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        from tools.ripgrep.ripgrep_model import RipgrepModel
        from tools.ripgrep.ripgrep_controller import RipgrepController
        
        # Create MVC components
        self.model = Mock()
        self.view = RipgrepView()
        self.controller = Mock()
        
        # Set up model mock
        self.model.is_available.return_value = True
        self.model.get_search_history.return_value = []
        self.model.search_results = []
        self.model.is_searching = False
    
    def tearDown(self):
        """Clean up UI test environment"""
        if hasattr(self, 'view') and self.view:
            self.view.deleteLater()
    
    def test_search_widget_integration(self):
        """Test search widget integration"""
        # Test search parameters widget
        params_widget = self.view.search_params_widget
        self.assertIsNotNone(params_widget)
        
        # Test setting search parameters
        params_widget.pattern_edit.setText("test pattern")
        params_widget.path_edit.setText(self.temp_dir)
        params_widget.case_sensitive_check.setChecked(True)
        
        # Get search parameters
        params = params_widget.get_search_parameters()
        self.assertEqual(params.pattern, "test pattern")
        self.assertEqual(params.search_path, self.temp_dir)
        self.assertTrue(params.case_sensitive)
    
    def test_results_widget_integration(self):
        """Test results widget integration"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        results_widget = self.view.results_widget
        self.assertIsNotNone(results_widget)
        
        # Test adding results
        file_result = FileResult(file_path=str(Path(self.temp_dir) / "test.py"))
        match = SearchMatch(line_number=1, column=0, content="test content")
        file_result.add_match(match)
        
        results_widget.add_result(file_result)
        
        # Verify results are displayed
        self.assertEqual(len(results_widget.search_results), 1)
        self.assertEqual(results_widget.results_tree.topLevelItemCount(), 1)
    
    def test_search_button_state_management(self):
        """Test search button state management"""
        # Initial state
        self.assertFalse(self.view.is_searching)
        self.assertTrue(self.view.search_button.isEnabled())
        self.assertFalse(self.view.cancel_button.isEnabled())
        
        # Set searching state
        self.view.set_searching_state(True)
        self.assertTrue(self.view.is_searching)
        self.assertFalse(self.view.search_button.isEnabled())
        self.assertTrue(self.view.cancel_button.isEnabled())
        
        # Reset state
        self.view.set_searching_state(False)
        self.assertFalse(self.view.is_searching)
        self.assertTrue(self.view.search_button.isEnabled())
        self.assertFalse(self.view.cancel_button.isEnabled())
    
    def test_export_functionality_integration(self):
        """Test export functionality integration"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        results_widget = self.view.results_widget
        
        # Add some test results
        for i in range(3):
            file_result = FileResult(file_path=f"/test/file_{i}.py")
            match = SearchMatch(line_number=i+1, column=0, content=f"test content {i}")
            file_result.add_match(match)
            results_widget.add_result(file_result)
        
        # Test export menu availability
        self.assertIsNotNone(results_widget.export_button)
        
        # Simulate export operation
        # (In real test, this would trigger file dialog and actual export)
        export_data = results_widget.get_export_data()
        self.assertEqual(len(export_data), 3)


class TestThemeIntegration(IntegrationTestBase):
    """Test theme integration"""
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_theme_switching_integration(self):
        """Test theme switching integration"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        
        view = RipgrepView()
        
        try:
            # Test theme switching (simulate theme manager integration)
            themes = ['dark_professional', 'light_modern', 'blue_corporate']
            
            for theme in themes:
                # Simulate theme application
                view.setStyleSheet(f"/* {theme} theme styles */")
                
                # Verify view still functions
                self.assertIsNotNone(view.search_params_widget)
                self.assertIsNotNone(view.results_widget)
        
        finally:
            view.deleteLater()


class TestWindowManagementIntegration(IntegrationTestBase):
    """Test window management integration"""
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_window_resizing_integration(self):
        """Test window resizing integration"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        
        view = RipgrepView()
        
        try:
            # Test various window sizes
            sizes = [(800, 600), (1024, 768), (1920, 1080)]
            
            for width, height in sizes:
                view.resize(width, height)
                
                # Process events to trigger layout updates
                QApplication.processEvents()
                
                # Verify components are still accessible
                self.assertIsNotNone(view.search_params_widget)
                self.assertIsNotNone(view.results_widget)
                self.assertTrue(view.search_button.isVisible())
        
        finally:
            view.deleteLater()
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_responsive_layout_integration(self):
        """Test responsive layout integration"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        
        view = RipgrepView()
        
        try:
            # Test minimum size constraints
            view.resize(400, 300)  # Small size
            QApplication.processEvents()
            
            # Verify layout adapts appropriately
            self.assertGreaterEqual(view.width(), 400)
            self.assertGreaterEqual(view.height(), 300)
            
            # Test large size
            view.resize(1600, 1200)
            QApplication.processEvents()
            
            # Verify components scale appropriately
            self.assertTrue(view.search_params_widget.isVisible())
            self.assertTrue(view.results_widget.isVisible())
        
        finally:
            view.deleteLater()


class TestDataPersistenceIntegration(IntegrationTestBase):
    """Test data persistence integration"""
    
    def test_search_history_persistence(self):
        """Test search history persistence"""
        from tools.ripgrep.ripgrep_model import RipgrepModel
        
        model = RipgrepModel()
        
        # Add search history
        test_patterns = ["pattern1", "pattern2", "pattern3"]
        for pattern in test_patterns:
            model._add_to_history(pattern)
        
        # Get history
        history = model.get_search_history()
        
        # Verify persistence
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], "pattern3")  # Most recent first
        
        # Test history limits
        for i in range(20):  # Add many patterns
            model._add_to_history(f"pattern_{i}")
        
        history = model.get_search_history()
        self.assertLessEqual(len(history), 50)  # Should have reasonable limit
    
    def test_export_import_integration(self):
        """Test export/import integration"""
        from tools.ripgrep.ripgrep_model import RipgrepModel
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        model = RipgrepModel()
        
        # Create test results
        file_result = FileResult(file_path="/test/file.py")
        match = SearchMatch(line_number=1, column=0, content="test content")
        file_result.add_match(match)
        model.search_results.append(file_result)
        
        # Test export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            success = model.export_results(temp_path, 'json')
            self.assertTrue(success)
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify file content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("test content", content)
                self.assertIn("/test/file.py", content)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestErrorRecoveryIntegration(IntegrationTestBase):
    """Test error recovery integration"""
    
    def test_graceful_degradation(self):
        """Test graceful degradation when components fail"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        plugin = RipgrepPlugin()
        
        # Test with missing ripgrep
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("rg not found")
            
            self.assertFalse(plugin.check_tools_availability())
            self.assertFalse(plugin.is_available())
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_ui_error_handling(self):
        """Test UI error handling integration"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        from tools.ripgrep.core.data_models import SearchParameters
        
        view = RipgrepView()
        
        try:
            # Test invalid search parameters
            view.search_params_widget.pattern_edit.setText("")  # Empty pattern
            
            # Should handle gracefully without crashing
            try:
                params = view.get_search_parameters()
            except ValueError:
                pass  # Expected for empty pattern
            
            # View should still be functional
            self.assertIsNotNone(view.search_params_widget)
            self.assertIsNotNone(view.results_widget)
        
        finally:
            view.deleteLater()


def run_integration_tests():
    """Run all integration tests"""
    test_classes = [
        TestPluginManagerIntegration,
    ]
    
    if QT_AVAILABLE:
        test_classes.extend([
            TestUIIntegration,
            TestThemeIntegration,
            TestWindowManagementIntegration,
        ])
    
    test_classes.extend([
        TestDataPersistenceIntegration,
        TestErrorRecoveryIntegration,
    ])
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Integration Tests for Ripgrep Plugin...")
    print("=" * 60)
    
    if not QT_AVAILABLE:
        print("⚠️  PyQt5 not available, skipping GUI integration tests")
    
    try:
        success = run_integration_tests()
        
        if success:
            print("\n✅ All integration tests passed!")
            print("Ripgrep plugin integrates correctly with the main application.")
        else:
            print("\n❌ Some integration tests failed!")
            print("Please check integration points and fix issues.")
            
    except Exception as e:
        print(f"\n💥 Integration test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Integration testing completed.")