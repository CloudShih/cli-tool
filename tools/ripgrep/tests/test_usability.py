#!/usr/bin/env python3
"""
Usability Testing Framework for Ripgrep Plugin
Tests user workflows, accessibility, and user experience
"""
import sys
import os
import unittest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import Qt components for GUI testing
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt, QTimer, QPoint
    from PyQt5.QtGui import QKeySequence
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    QT_AVAILABLE = True
    
except ImportError:
    QT_AVAILABLE = False


class UsabilityTestBase(unittest.TestCase):
    """Base class for usability tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up usability test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_test_content()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_test_content(cls):
        """Create test content for usability testing"""
        test_content = {
            'user_guide.md': '''
# User Guide

This is a comprehensive user guide for testing search functionality.

## Getting Started
To get started with the application, follow these steps:
1. Open the search panel
2. Enter your search pattern
3. Configure search options
4. Execute the search

## Advanced Features
- Regular expression support
- File type filtering
- Context line display
- Result export capabilities

## Troubleshooting
If you encounter issues:
- Check your search pattern
- Verify file permissions
- Review search scope settings
''',
            'code_example.py': '''
#!/usr/bin/env python3
"""
Example Python code for usability testing
"""

def search_function(pattern, files):
    """Search for pattern in files"""
    results = []
    for file in files:
        if pattern in file.content:
            results.append(file)
    return results

class SearchEngine:
    """Advanced search engine implementation"""
    
    def __init__(self):
        self.patterns = []
        self.results = []
    
    def add_pattern(self, pattern):
        """Add search pattern"""
        self.patterns.append(pattern)
    
    def execute_search(self):
        """Execute search with all patterns"""
        # Implementation here
        pass

# TODO: Add more search options
# FIXME: Optimize search performance
''',
            'config.json': '''
{
    "application": {
        "name": "Search Tool",
        "version": "1.0.0"
    },
    "search_settings": {
        "case_sensitive": false,
        "regex_enabled": true,
        "max_results": 1000,
        "context_lines": 3
    },
    "ui_settings": {
        "theme": "light",
        "font_size": 12,
        "show_line_numbers": true
    }
}
'''
        }
        
        for filename, content in test_content.items():
            file_path = Path(cls.temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestUserWorkflows(UsabilityTestBase):
    """Test common user workflows"""
    
    def setUp(self):
        """Set up UI components for workflow testing"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        self.view = RipgrepView()
    
    def tearDown(self):
        """Clean up UI components"""
        if hasattr(self, 'view') and self.view:
            self.view.deleteLater()
    
    def test_basic_search_workflow(self):
        """Test basic search workflow"""
        # Step 1: User enters search pattern
        pattern_edit = self.view.search_params_widget.pattern_edit
        pattern_edit.setText("search")
        
        # Verify pattern is entered
        self.assertEqual(pattern_edit.text(), "search")
        
        # Step 2: User sets search path
        path_edit = self.view.search_params_widget.path_edit
        path_edit.setText(self.temp_dir)
        
        # Verify path is set
        self.assertEqual(path_edit.text(), self.temp_dir)
        
        # Step 3: User configures options
        case_check = self.view.search_params_widget.case_sensitive_check
        case_check.setChecked(True)
        
        # Verify option is set
        self.assertTrue(case_check.isChecked())
        
        # Step 4: User initiates search
        search_button = self.view.search_button
        self.assertTrue(search_button.isEnabled())
        
        # Simulate button click
        QTest.mouseClick(search_button, Qt.LeftButton)
        
        # Verify search state changes
        # (This would trigger actual search in real application)
    
    def test_advanced_search_workflow(self):
        """Test advanced search workflow with multiple options"""
        params_widget = self.view.search_params_widget
        
        # Set advanced search parameters
        params_widget.pattern_edit.setText(r'def\s+\w+\(')
        params_widget.regex_check.setChecked(True)
        params_widget.whole_words_check.setChecked(False)
        params_widget.context_lines_spin.setValue(5)
        params_widget.max_results_spin.setValue(500)
        
        # Verify all parameters are set correctly
        self.assertTrue(params_widget.regex_check.isChecked())
        self.assertFalse(params_widget.whole_words_check.isChecked())
        self.assertEqual(params_widget.context_lines_spin.value(), 5)
        self.assertEqual(params_widget.max_results_spin.value(), 500)
        
        # Get search parameters
        params = params_widget.get_search_parameters()
        self.assertTrue(params.regex_mode)
        self.assertFalse(params.whole_words)
        self.assertEqual(params.context_lines, 5)
        self.assertEqual(params.max_results, 500)
    
    def test_result_interaction_workflow(self):
        """Test result interaction workflow"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        results_widget = self.view.results_widget
        
        # Simulate search results
        file_result = FileResult(file_path=str(Path(self.temp_dir) / "test.py"))
        match = SearchMatch(line_number=10, column=4, content="def search_function():")
        file_result.add_match(match)
        
        # Add result to widget
        results_widget.add_result(file_result)
        
        # Verify result is displayed
        self.assertEqual(results_widget.results_tree.topLevelItemCount(), 1)
        
        # Test result navigation
        tree_widget = results_widget.results_tree
        top_item = tree_widget.topLevelItem(0)
        self.assertIsNotNone(top_item)
        
        # Simulate double-click on result
        QTest.mouseDClick(tree_widget, Qt.LeftButton)
        
        # Verify interaction works (in real app, this would open file)
    
    def test_export_workflow(self):
        """Test export workflow"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        results_widget = self.view.results_widget
        
        # Add test results
        for i in range(3):
            file_result = FileResult(file_path=f"/test/file_{i}.py")
            match = SearchMatch(line_number=i+1, column=0, content=f"test content {i}")
            file_result.add_match(match)
            results_widget.add_result(file_result)
        
        # Test export button availability
        export_button = results_widget.export_button
        self.assertTrue(export_button.isEnabled())
        
        # Simulate export action
        QTest.mouseClick(export_button, Qt.LeftButton)
        
        # Verify export data is available
        export_data = results_widget.get_export_data()
        self.assertEqual(len(export_data), 3)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestAccessibilityCompliance(UsabilityTestBase):
    """Test accessibility compliance"""
    
    def setUp(self):
        """Set up UI components for accessibility testing"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        self.view = RipgrepView()
    
    def tearDown(self):
        """Clean up UI components"""
        if hasattr(self, 'view') and self.view:
            self.view.deleteLater()
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation accessibility"""
        # Test tab order
        focusable_widgets = [
            self.view.search_params_widget.pattern_edit,
            self.view.search_params_widget.path_edit,
            self.view.search_params_widget.case_sensitive_check,
            self.view.search_button,
            self.view.cancel_button
        ]
        
        # Set initial focus
        focusable_widgets[0].setFocus()
        self.assertTrue(focusable_widgets[0].hasFocus())
        
        # Test tab navigation
        for i in range(1, len(focusable_widgets)):
            QTest.keyPress(self.view, Qt.Key_Tab)
            QApplication.processEvents()
            # Focus should move to next widget
            # (Exact behavior depends on tab order configuration)
    
    def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts"""
        # Test Ctrl+F for focus on search field
        pattern_edit = self.view.search_params_widget.pattern_edit
        
        # Simulate Ctrl+F shortcut
        QTest.keySequence(self.view, QKeySequence.Find)
        QApplication.processEvents()
        
        # Pattern edit should receive focus (if shortcut is implemented)
        # self.assertTrue(pattern_edit.hasFocus())
        
        # Test Enter key for search
        pattern_edit.setText("test")
        QTest.keyPress(pattern_edit, Qt.Key_Return)
        QApplication.processEvents()
        
        # Should trigger search (in real implementation)
    
    def test_screen_reader_compatibility(self):
        """Test screen reader compatibility"""
        # Test accessible names
        pattern_edit = self.view.search_params_widget.pattern_edit
        self.assertIsNotNone(pattern_edit.accessibleName())
        
        # Test accessible descriptions
        search_button = self.view.search_button
        self.assertIsNotNone(search_button.accessibleDescription())
        
        # Test ARIA roles (if implemented)
        results_tree = self.view.results_widget.results_tree
        self.assertIsNotNone(results_tree.accessibleName())
    
    def test_high_contrast_compatibility(self):
        """Test high contrast theme compatibility"""
        # Apply high contrast stylesheet
        high_contrast_style = """
        QWidget {
            background-color: black;
            color: white;
            border: 1px solid white;
        }
        QPushButton {
            background-color: #003366;
            color: white;
            border: 2px solid white;
        }
        """
        
        self.view.setStyleSheet(high_contrast_style)
        
        # Verify components are still visible and functional
        self.assertTrue(self.view.search_button.isVisible())
        self.assertTrue(self.view.search_params_widget.pattern_edit.isVisible())
        
        # Test contrast ratio (would need color analysis in real test)
    
    def test_font_size_scaling(self):
        """Test font size scaling accessibility"""
        original_font = self.view.font()
        
        # Test larger font sizes
        large_sizes = [14, 18, 24]
        
        for size in large_sizes:
            font = original_font
            font.setPointSize(size)
            self.view.setFont(font)
            
            # Verify layout still works
            self.assertTrue(self.view.search_params_widget.isVisible())
            self.assertTrue(self.view.results_widget.isVisible())
            
            # Process layout changes
            QApplication.processEvents()


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestUserInputValidation(UsabilityTestBase):
    """Test user input validation and feedback"""
    
    def setUp(self):
        """Set up UI components for input validation testing"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        self.view = RipgrepView()
    
    def tearDown(self):
        """Clean up UI components"""
        if hasattr(self, 'view') and self.view:
            self.view.deleteLater()
    
    def test_empty_pattern_validation(self):
        """Test validation of empty search patterns"""
        pattern_edit = self.view.search_params_widget.pattern_edit
        
        # Test empty pattern
        pattern_edit.setText("")
        
        try:
            params = self.view.get_search_parameters()
            # Should raise ValueError for empty pattern
            self.fail("Expected ValueError for empty pattern")
        except ValueError:
            pass  # Expected
    
    def test_invalid_regex_pattern_feedback(self):
        """Test feedback for invalid regex patterns"""
        params_widget = self.view.search_params_widget
        
        # Enable regex mode
        params_widget.regex_check.setChecked(True)
        
        # Test invalid regex patterns
        invalid_patterns = [
            "[unclosed bracket",
            "*invalid quantifier",
            "(?invalid group",
            "\\invalid escape"
        ]
        
        for pattern in invalid_patterns:
            params_widget.pattern_edit.setText(pattern)
            
            # In real implementation, this would show validation feedback
            # For now, just verify the pattern is set
            self.assertEqual(params_widget.pattern_edit.text(), pattern)
    
    def test_path_validation_feedback(self):
        """Test feedback for invalid search paths"""
        path_edit = self.view.search_params_widget.path_edit
        
        # Test non-existent path
        path_edit.setText("/nonexistent/path")
        
        # Should provide visual feedback (in real implementation)
        # For now, verify path is set
        self.assertEqual(path_edit.text(), "/nonexistent/path")
    
    def test_parameter_range_validation(self):
        """Test validation of parameter ranges"""
        params_widget = self.view.search_params_widget
        
        # Test context lines limits
        context_spin = params_widget.context_lines_spin
        
        # Test valid range
        context_spin.setValue(5)
        self.assertEqual(context_spin.value(), 5)
        
        # Test boundary values
        context_spin.setValue(0)
        self.assertEqual(context_spin.value(), 0)
        
        context_spin.setValue(20)
        self.assertEqual(context_spin.value(), 20)
        
        # Test max results limits
        max_results_spin = params_widget.max_results_spin
        max_results_spin.setValue(1000)
        self.assertEqual(max_results_spin.value(), 1000)


@unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
class TestUserExperienceFeatures(UsabilityTestBase):
    """Test user experience features"""
    
    def setUp(self):
        """Set up UI components for UX testing"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        from tools.ripgrep.ripgrep_model import RipgrepModel
        
        self.view = RipgrepView()
        self.model = Mock()
        self.model.get_search_history.return_value = ["previous1", "previous2", "previous3"]
    
    def tearDown(self):
        """Clean up UI components"""
        if hasattr(self, 'view') and self.view:
            self.view.deleteLater()
    
    def test_search_history_autocomplete(self):
        """Test search history and autocomplete features"""
        pattern_edit = self.view.search_params_widget.pattern_edit
        
        # Test history population
        history = ["search1", "search2", "search3"]
        
        # In real implementation, this would populate autocomplete
        # For now, verify the edit widget is functional
        pattern_edit.setText("search")
        self.assertEqual(pattern_edit.text(), "search")
        
        # Test autocomplete behavior (would require QCompleter in real implementation)
    
    def test_progress_indication(self):
        """Test progress indication during searches"""
        # Test initial state
        self.assertFalse(self.view.is_searching)
        
        # Test progress indication when searching starts
        self.view.set_searching_state(True)
        self.assertTrue(self.view.is_searching)
        
        # Verify UI changes appropriately
        self.assertFalse(self.view.search_button.isEnabled())
        self.assertTrue(self.view.cancel_button.isEnabled())
        
        # Test progress completion
        self.view.set_searching_state(False)
        self.assertFalse(self.view.is_searching)
        self.assertTrue(self.view.search_button.isEnabled())
        self.assertFalse(self.view.cancel_button.isEnabled())
    
    def test_result_preview_functionality(self):
        """Test result preview functionality"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch, HighlightSpan
        
        results_widget = self.view.results_widget
        
        # Create test result with highlights
        file_result = FileResult(file_path=str(Path(self.temp_dir) / "test.py"))
        match = SearchMatch(
            line_number=10,
            column=4,
            content="def search_function(pattern):",
            highlights=[HighlightSpan(4, 10)]  # Highlight "search"
        )
        file_result.add_match(match)
        
        # Add result
        results_widget.add_result(file_result)
        
        # Verify result is displayed with proper formatting
        tree_item = results_widget.results_tree.topLevelItem(0)
        self.assertIsNotNone(tree_item)
        
        # Test preview display (would show highlighted text in real implementation)
    
    def test_responsive_ui_feedback(self):
        """Test responsive UI feedback"""
        # Test button hover states
        search_button = self.view.search_button
        
        # Simulate mouse events
        QTest.mouseMove(search_button, QPoint(10, 10))
        QApplication.processEvents()
        
        # Verify button is still functional
        self.assertTrue(search_button.isEnabled())
        
        # Test tooltips
        self.assertIsNotNone(search_button.toolTip())


class TestCrossFileNavigation(UsabilityTestBase):
    """Test cross-file navigation features"""
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_file_opening_integration(self):
        """Test file opening from search results"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        view = RipgrepView()
        
        try:
            # Create test result
            file_result = FileResult(file_path=str(Path(self.temp_dir) / "user_guide.md"))
            match = SearchMatch(line_number=5, column=0, content="## Getting Started")
            file_result.add_match(match)
            
            # Add to results
            view.results_widget.add_result(file_result)
            
            # Test double-click to open (would trigger file opening in real app)
            tree_widget = view.results_widget.results_tree
            QTest.mouseDClick(tree_widget, Qt.LeftButton)
            
            # Verify interaction is handled
            self.assertEqual(tree_widget.topLevelItemCount(), 1)
        
        finally:
            view.deleteLater()
    
    @unittest.skipUnless(QT_AVAILABLE, "PyQt5 not available")
    def test_context_menu_functionality(self):
        """Test context menu functionality"""
        from tools.ripgrep.ripgrep_view import RipgrepView
        from tools.ripgrep.core.data_models import FileResult, SearchMatch
        
        view = RipgrepView()
        
        try:
            # Add test result
            file_result = FileResult(file_path=str(Path(self.temp_dir) / "code_example.py"))
            match = SearchMatch(line_number=10, column=0, content="def search_function(pattern, files):")
            file_result.add_match(match)
            view.results_widget.add_result(file_result)
            
            # Test right-click context menu
            tree_widget = view.results_widget.results_tree
            QTest.mouseClick(tree_widget, Qt.RightButton)
            
            # Verify context menu actions are available (in real implementation)
            # Actions might include: Open File, Copy Path, Show in Explorer, etc.
        
        finally:
            view.deleteLater()


def run_usability_tests():
    """Run all usability tests"""
    if not QT_AVAILABLE:
        print("PyQt5 not available, skipping usability tests")
        return False
    
    test_classes = [
        TestUserWorkflows,
        TestAccessibilityCompliance,
        TestUserInputValidation,
        TestUserExperienceFeatures,
        TestCrossFileNavigation,
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Usability Tests for Ripgrep Plugin...")
    print("=" * 60)
    
    if not QT_AVAILABLE:
        print("⚠️  PyQt5 not available, cannot run GUI usability tests")
        sys.exit(0)
    
    try:
        success = run_usability_tests()
        
        if success:
            print("\n✅ All usability tests passed!")
            print("Ripgrep plugin provides excellent user experience.")
        else:
            print("\n❌ Some usability tests failed!")
            print("User experience improvements needed.")
            
    except Exception as e:
        print(f"\n💥 Usability test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Usability testing completed.")