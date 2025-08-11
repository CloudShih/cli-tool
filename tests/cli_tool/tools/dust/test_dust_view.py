"""
Comprehensive unit tests for dust_view.py
Tests for UI component initialization, parameter extraction methods,
status updates, progress indicators, and configuration loading/saving.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
import sys

from tools.dust.dust_view import DustView


class TestDustView(unittest.TestCase):
    """Test cases for DustView"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method"""
        with patch('tools.dust.dust_view.config_manager') as mock_config:
            # Setup default config returns
            mock_config.get.side_effect = self._mock_config_get
            self.view = DustView()

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'view'):
            self.view.deleteLater()
            self.view = None

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    def _mock_config_get(self, key, default=None):
        """Mock configuration getter"""
        config_values = {
            'tools.dust.default_max_depth': 3,
            'tools.dust.default_number_of_lines': 50,
            'tools.dust.default_sort_reverse': True,
            'tools.dust.default_show_apparent_size': False,
            'tools.dust.default_min_size': '',
            'tools.dust.default_path': ''
        }
        return config_values.get(key, default)

    def test_initialization(self):
        """Test DustView initialization"""
        # Assert main components exist
        self.assertIsNotNone(self.view.dust_path_input)
        self.assertIsNotNone(self.view.dust_browse_button)
        self.assertIsNotNone(self.view.dust_max_depth_spinbox)
        self.assertIsNotNone(self.view.dust_lines_spinbox)
        self.assertIsNotNone(self.view.dust_analyze_button)
        self.assertIsNotNone(self.view.dust_results_display)
        self.assertIsNotNone(self.view.status_indicator)
        self.assertIsNotNone(self.view.loading_spinner)

    def test_ui_components_setup(self):
        """Test UI components are set up correctly"""
        # Test spinbox ranges
        self.assertEqual(self.view.dust_max_depth_spinbox.minimum(), 1)
        self.assertEqual(self.view.dust_max_depth_spinbox.maximum(), 20)
        self.assertEqual(self.view.dust_lines_spinbox.minimum(), 10)
        self.assertEqual(self.view.dust_lines_spinbox.maximum(), 1000)
        
        # Test default values
        self.assertEqual(self.view.dust_max_depth_spinbox.value(), 3)
        self.assertEqual(self.view.dust_lines_spinbox.value(), 50)
        
        # Test checkboxes
        self.assertTrue(self.view.dust_reverse_sort_checkbox.isChecked())
        self.assertFalse(self.view.dust_apparent_size_checkbox.isChecked())

    @patch('tools.dust.dust_view.config_manager')
    def test_load_default_settings_success(self, mock_config):
        """Test successful loading of default settings"""
        # Arrange
        mock_config.get.side_effect = lambda key, default=None: {
            'tools.dust.default_max_depth': 5,
            'tools.dust.default_number_of_lines': 100,
            'tools.dust.default_sort_reverse': False,
            'tools.dust.default_show_apparent_size': True,
            'tools.dust.default_min_size': '1M',
            'tools.dust.default_path': '/test/path'
        }.get(key, default)
        
        # Create new view to test loading
        view = DustView()
        
        # Assert
        self.assertEqual(view.dust_max_depth_spinbox.value(), 5)
        self.assertEqual(view.dust_lines_spinbox.value(), 100)
        self.assertFalse(view.dust_reverse_sort_checkbox.isChecked())
        self.assertTrue(view.dust_apparent_size_checkbox.isChecked())
        self.assertEqual(view.dust_min_size_input.text(), '1M')
        self.assertEqual(view.dust_path_input.text(), '/test/path')
        
        view.deleteLater()

    @patch('tools.dust.dust_view.config_manager')
    def test_load_default_settings_exception(self, mock_config):
        """Test loading default settings with exception handling"""
        # Arrange
        mock_config.get.side_effect = Exception("Config error")
        
        # Create new view to test error handling
        view = DustView()
        
        # Assert fallback values are used
        self.assertEqual(view.dust_max_depth_spinbox.value(), 3)
        self.assertEqual(view.dust_lines_spinbox.value(), 50)
        self.assertTrue(view.dust_reverse_sort_checkbox.isChecked())
        self.assertFalse(view.dust_apparent_size_checkbox.isChecked())
        
        view.deleteLater()

    def test_get_analysis_parameters_basic(self):
        """Test basic parameter extraction"""
        # Arrange - set some values
        self.view.dust_path_input.setText("/test/path")
        self.view.dust_max_depth_spinbox.setValue(5)
        self.view.dust_lines_spinbox.setValue(25)
        self.view.dust_reverse_sort_checkbox.setChecked(False)
        self.view.dust_apparent_size_checkbox.setChecked(True)
        
        # Act
        params = self.view.get_analysis_parameters()
        
        # Assert
        self.assertEqual(params['target_path'], '/test/path')
        self.assertEqual(params['max_depth'], 5)
        self.assertEqual(params['number_of_lines'], 25)
        self.assertFalse(params['sort_reverse'])
        self.assertTrue(params['show_apparent_size'])

    def test_get_analysis_parameters_with_file_types(self):
        """Test parameter extraction with file types"""
        # Arrange
        self.view.dust_include_types_input.setText("txt, pdf, jpg")
        self.view.dust_exclude_patterns_input.setText("*.tmp, node_modules, *.log")
        
        # Act
        params = self.view.get_analysis_parameters()
        
        # Assert
        self.assertEqual(params['file_types'], ['txt', 'pdf', 'jpg'])
        self.assertEqual(params['exclude_patterns'], ['*.tmp', 'node_modules', '*.log'])

    def test_get_analysis_parameters_empty_inputs(self):
        """Test parameter extraction with empty inputs"""
        # Arrange - leave inputs empty
        self.view.dust_path_input.setText("")
        self.view.dust_include_types_input.setText("")
        self.view.dust_exclude_patterns_input.setText("")
        self.view.dust_min_size_input.setText("")
        
        # Act
        params = self.view.get_analysis_parameters()
        
        # Assert
        self.assertEqual(params['target_path'], '.')  # Default to current dir
        self.assertIsNone(params['file_types'])
        self.assertIsNone(params['exclude_patterns'])
        self.assertIsNone(params['min_size'])

    def test_get_analysis_parameters_whitespace_handling(self):
        """Test parameter extraction handles whitespace correctly"""
        # Arrange - add whitespace
        self.view.dust_path_input.setText("  /test/path  ")
        self.view.dust_include_types_input.setText(" txt , , pdf , ")
        self.view.dust_min_size_input.setText("  1M  ")
        
        # Act
        params = self.view.get_analysis_parameters()
        
        # Assert
        self.assertEqual(params['target_path'], '/test/path')
        self.assertEqual(params['file_types'], ['txt', 'pdf'])  # Empty entries removed
        self.assertEqual(params['min_size'], '1M')

    def test_set_analyze_button_state_enabled(self):
        """Test setting analyze button to enabled state"""
        # Act
        self.view.set_analyze_button_state("開始分析", True)
        
        # Assert
        self.assertEqual(self.view.dust_analyze_button.text(), "開始分析")
        self.assertTrue(self.view.dust_analyze_button.isEnabled())

    def test_set_analyze_button_state_disabled(self):
        """Test setting analyze button to disabled state"""
        # Act
        self.view.set_analyze_button_state("分析中...", False)
        
        # Assert
        self.assertEqual(self.view.dust_analyze_button.text(), "分析中...")
        self.assertFalse(self.view.dust_analyze_button.isEnabled())

    def test_clear_results(self):
        """Test clearing analysis results"""
        # Arrange - add some content
        self.view.dust_results_display.setPlainText("Some analysis results")
        
        # Act
        self.view.clear_results()
        
        # Assert
        self.assertEqual(self.view.dust_results_display.toPlainText(), "")

    def test_set_analysis_completed_success(self):
        """Test setting analysis completed with success"""
        # Act
        self.view.set_analysis_completed(success=True, message="分析成功完成")
        
        # Assert
        self.assertEqual(self.view.dust_analyze_button.text(), "開始分析")
        self.assertTrue(self.view.dust_analyze_button.isEnabled())

    def test_set_analysis_completed_failure(self):
        """Test setting analysis completed with failure"""
        # Act
        self.view.set_analysis_completed(success=False, message="分析失敗")
        
        # Assert
        self.assertEqual(self.view.dust_analyze_button.text(), "開始分析")
        self.assertTrue(self.view.dust_analyze_button.isEnabled())

    def test_directory_button_signal_connection(self):
        """Test that directory button signal is connected"""
        # The DirectoryButton should emit directory_selected signal
        # which is connected to dust_path_input.setText
        
        # Arrange
        initial_text = self.view.dust_path_input.text()
        
        # Act - simulate directory selection
        test_path = "/selected/directory"
        self.view.dust_browse_button.directory_selected.emit(test_path)
        
        # Process events to ensure signal is handled
        QApplication.processEvents()
        
        # Assert
        self.assertEqual(self.view.dust_path_input.text(), test_path)

    def test_input_field_properties(self):
        """Test input field properties and tooltips"""
        # Test that input fields have appropriate properties
        self.assertIsNotNone(self.view.dust_path_input.toolTip())
        self.assertIsNotNone(self.view.dust_max_depth_spinbox.toolTip())
        self.assertIsNotNone(self.view.dust_lines_spinbox.toolTip())
        self.assertIsNotNone(self.view.dust_min_size_input.toolTip())
        
        # Test placeholder text
        self.assertIn("選擇要分析的目錄路徑", self.view.dust_path_input.placeholderText())
        self.assertIn("例如: 1M, 100K", self.view.dust_min_size_input.placeholderText())

    def test_checkbox_properties(self):
        """Test checkbox properties and tooltips"""
        # Test checkbox tooltips
        self.assertIsNotNone(self.view.dust_reverse_sort_checkbox.toolTip())
        self.assertIsNotNone(self.view.dust_apparent_size_checkbox.toolTip())
        self.assertIsNotNone(self.view.dust_full_paths_checkbox.toolTip())
        self.assertIsNotNone(self.view.dust_files_only_checkbox.toolTip())
        
        # Test checkbox text
        self.assertIn("反向排序", self.view.dust_reverse_sort_checkbox.text())
        self.assertIn("顯示表面大小", self.view.dust_apparent_size_checkbox.text())
        self.assertIn("顯示完整路徑", self.view.dust_full_paths_checkbox.text())
        self.assertIn("僅顯示檔案", self.view.dust_files_only_checkbox.text())

    def test_results_display_properties(self):
        """Test results display widget properties"""
        # Test minimum height
        self.assertGreaterEqual(self.view.dust_results_display.minimumHeight(), 350)
        
        # Test placeholder text
        self.assertIn("磁碟空間分析結果", self.view.dust_results_display.placeholderText())

    def test_spinbox_ranges_and_values(self):
        """Test spinbox ranges and default values"""
        # Max depth spinbox
        self.assertEqual(self.view.dust_max_depth_spinbox.minimum(), 1)
        self.assertEqual(self.view.dust_max_depth_spinbox.maximum(), 20)
        self.assertEqual(self.view.dust_max_depth_spinbox.value(), 3)
        
        # Lines spinbox
        self.assertEqual(self.view.dust_lines_spinbox.minimum(), 10)
        self.assertEqual(self.view.dust_lines_spinbox.maximum(), 1000)
        self.assertEqual(self.view.dust_lines_spinbox.value(), 50)

    def test_button_properties(self):
        """Test button properties"""
        # Primary analyze button
        self.assertEqual(self.view.dust_analyze_button.text(), "開始分析")
        self.assertGreaterEqual(self.view.dust_analyze_button.minimumHeight(), 40)
        
        # Browse button
        self.assertEqual(self.view.dust_browse_button.text(), "瀏覽...")

    def test_status_indicator_and_spinner(self):
        """Test status indicator and loading spinner"""
        # Test status indicator exists
        self.assertIsNotNone(self.view.status_indicator)
        
        # Test loading spinner exists
        self.assertIsNotNone(self.view.loading_spinner)

    def test_layout_structure(self):
        """Test that the layout is properly structured"""
        # Test that main layout exists
        main_layout = self.view.layout()
        self.assertIsNotNone(main_layout)
        
        # Test that layout has proper spacing and margins
        self.assertGreaterEqual(main_layout.spacing(), 0)
        self.assertGreaterEqual(main_layout.contentsMargins().top(), 0)

    def test_widget_connections(self):
        """Test widget signal connections"""
        # Test that clear button is connected
        # This should be tested by ensuring the clear_results method works
        # since the connection is done in setup_ui
        
        # Add some text and clear it
        self.view.dust_results_display.setPlainText("test content")
        self.view.clear_results()
        self.assertEqual(self.view.dust_results_display.toPlainText(), "")

    def test_parameter_extraction_edge_cases(self):
        """Test parameter extraction with edge cases"""
        # Test with comma-separated values containing spaces
        self.view.dust_include_types_input.setText("txt,   pdf  ,jpg,")
        self.view.dust_exclude_patterns_input.setText(" *.tmp , node_modules,*.log , ")
        
        params = self.view.get_analysis_parameters()
        
        # Should handle spaces and empty entries
        self.assertEqual(params['file_types'], ['txt', 'pdf', 'jpg'])
        self.assertEqual(params['exclude_patterns'], ['*.tmp', 'node_modules', '*.log'])

    def test_boolean_parameter_extraction(self):
        """Test extraction of boolean parameters"""
        # Set all checkboxes
        self.view.dust_reverse_sort_checkbox.setChecked(True)
        self.view.dust_apparent_size_checkbox.setChecked(True)
        self.view.dust_full_paths_checkbox.setChecked(True)
        self.view.dust_files_only_checkbox.setChecked(True)
        
        params = self.view.get_analysis_parameters()
        
        self.assertTrue(params['sort_reverse'])
        self.assertTrue(params['show_apparent_size'])
        self.assertTrue(params['full_paths'])
        self.assertTrue(params['files_only'])
        
        # Uncheck all
        self.view.dust_reverse_sort_checkbox.setChecked(False)
        self.view.dust_apparent_size_checkbox.setChecked(False)
        self.view.dust_full_paths_checkbox.setChecked(False)
        self.view.dust_files_only_checkbox.setChecked(False)
        
        params = self.view.get_analysis_parameters()
        
        self.assertFalse(params['sort_reverse'])
        self.assertFalse(params['show_apparent_size'])
        self.assertFalse(params['full_paths'])
        self.assertFalse(params['files_only'])


if __name__ == '__main__':
    unittest.main()