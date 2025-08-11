"""
Comprehensive unit tests for dust plugin.py
Tests for plugin interface implementation, plugin discovery and loading,
tool availability checking, MVC component creation, and plugin cleanup.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from PyQt5.QtWidgets import QApplication, QWidget
import sys

from tools.dust.plugin import DustPlugin, create_plugin
from core.plugin_manager import PluginInterface
from tools.dust.dust_model import DustModel
from tools.dust.dust_view import DustView
from tools.dust.dust_controller import DustController


class TestDustPlugin(unittest.TestCase):
    """Test cases for DustPlugin"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.plugin = DustPlugin()

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'plugin'):
            self.plugin.cleanup()
            self.plugin = None

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    def test_plugin_inheritance(self):
        """Test that DustPlugin inherits from PluginInterface"""
        self.assertIsInstance(self.plugin, PluginInterface)

    def test_plugin_basic_properties(self):
        """Test basic plugin properties"""
        # Test name
        self.assertEqual(self.plugin.name, "dust")
        
        # Test description
        self.assertIn("dust 工具", self.plugin.description)
        self.assertIn("磁碟空間分析", self.plugin.description)
        
        # Test version
        self.assertEqual(self.plugin.version, "1.0.0")
        
        # Test required tools
        self.assertEqual(self.plugin.required_tools, ["dust"])

    def test_plugin_display_properties(self):
        """Test plugin display properties"""
        # Test display name
        self.assertEqual(self.plugin.get_display_name(), "磁碟空間分析器")
        
        # Test author
        self.assertEqual(self.plugin.get_author(), "CLI Tool Developer")
        
        # Test icon path (optional)
        self.assertIsNone(self.plugin.get_icon_path())

    def test_supported_operations(self):
        """Test supported operations list"""
        operations = self.plugin.get_supported_operations()
        expected_operations = [
            "disk_usage_analysis", "directory_size", "file_statistics",
            "space_visualization", "tree_view", "detailed_report"
        ]
        
        for operation in expected_operations:
            self.assertIn(operation, operations)

    def test_initial_state(self):
        """Test plugin initial state"""
        # Should not be initialized initially
        self.assertFalse(self.plugin.is_initialized())
        self.assertFalse(self.plugin._initialized)
        
        # Components should be None initially
        self.assertIsNone(self.plugin._model)
        self.assertIsNone(self.plugin._view)
        self.assertIsNone(self.plugin._controller)

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_initialization_success(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test successful plugin initialization"""
        # Arrange
        mock_model = Mock()
        mock_view = Mock()
        mock_controller = Mock()
        
        mock_model_class.return_value = mock_model
        mock_view_class.return_value = mock_view
        mock_controller_class.return_value = mock_controller
        
        # Act
        result = self.plugin.initialize()
        
        # Assert
        self.assertTrue(result)
        self.assertTrue(self.plugin.is_initialized())
        
        # Check components were created
        mock_model_class.assert_called_once()
        mock_view_class.assert_called_once()
        mock_controller_class.assert_called_once_with(mock_view, mock_model)
        
        # Check components were stored
        self.assertEqual(self.plugin._model, mock_model)
        self.assertEqual(self.plugin._view, mock_view)
        self.assertEqual(self.plugin._controller, mock_controller)

    @patch('tools.dust.plugin.DustModel')
    def test_initialization_failure(self, mock_model_class):
        """Test plugin initialization failure"""
        # Arrange
        mock_model_class.side_effect = Exception("Initialization failed")
        
        # Act
        result = self.plugin.initialize()
        
        # Assert
        self.assertFalse(result)
        self.assertFalse(self.plugin.is_initialized())

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_double_initialization(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test double initialization handling"""
        # First initialization
        self.plugin.initialize()
        
        # Reset mocks
        mock_model_class.reset_mock()
        mock_view_class.reset_mock()
        mock_controller_class.reset_mock()
        
        # Second initialization
        result = self.plugin.initialize()
        
        # Should return True but not create new components
        self.assertTrue(result)
        mock_model_class.assert_not_called()
        mock_view_class.assert_not_called()
        mock_controller_class.assert_not_called()

    def test_create_model(self):
        """Test model creation"""
        model = self.plugin.create_model()
        self.assertIsInstance(model, DustModel)

    @patch('tools.dust.plugin.config_manager')
    def test_create_view(self, mock_config):
        """Test view creation"""
        mock_config.get.return_value = "dust"
        view = self.plugin.create_view()
        self.assertIsInstance(view, DustView)
        view.deleteLater()

    def test_create_controller(self):
        """Test controller creation"""
        # Create mock components
        mock_model = Mock()
        mock_view = Mock()
        
        # Create controller
        controller = self.plugin.create_controller(mock_model, mock_view)
        
        # Assert
        self.assertIsInstance(controller, DustController)

    @patch('tools.dust.plugin.DustModel')
    def test_check_tools_availability_success(self, mock_model_class):
        """Test successful tool availability check"""
        # Arrange
        mock_model = Mock()
        mock_model.check_dust_availability.return_value = (True, "dust 0.8.0", "")
        mock_model_class.return_value = mock_model
        
        # Act
        result = self.plugin.check_tools_availability()
        
        # Assert
        self.assertTrue(result)

    @patch('tools.dust.plugin.DustModel')
    def test_check_tools_availability_failure(self, mock_model_class):
        """Test tool availability check failure"""
        # Arrange
        mock_model = Mock()
        mock_model.check_dust_availability.return_value = (False, "", "Tool not found")
        mock_model_class.return_value = mock_model
        
        # Act
        result = self.plugin.check_tools_availability()
        
        # Assert
        self.assertFalse(result)

    @patch('tools.dust.plugin.DustModel')
    def test_check_tools_availability_exception(self, mock_model_class):
        """Test tool availability check with exception"""
        # Arrange
        mock_model_class.side_effect = Exception("Check failed")
        
        # Act
        result = self.plugin.check_tools_availability()
        
        # Assert
        self.assertFalse(result)

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_get_widget_initialized(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test getting widget when plugin is initialized"""
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        widget = self.plugin.get_widget()
        
        # Assert
        self.assertIsNotNone(widget)
        self.assertEqual(widget, self.plugin._view)

    def test_get_widget_not_initialized(self):
        """Test getting widget when plugin is not initialized"""
        # Act
        widget = self.plugin.get_widget()
        
        # Assert - should attempt initialization and may return None if it fails
        # The exact behavior depends on initialization success
        if self.plugin.is_initialized():
            self.assertIsNotNone(widget)
        else:
            self.assertIsNone(widget)

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_cleanup(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test plugin cleanup"""
        # Initialize plugin
        self.plugin.initialize()
        
        # Store references to components
        controller = self.plugin._controller
        
        # Act
        self.plugin.cleanup()
        
        # Assert
        # Controller cleanup should be called
        controller.cleanup.assert_called_once()
        
        # Components should be reset
        self.assertIsNone(self.plugin._controller)
        self.assertIsNone(self.plugin._view)
        self.assertIsNone(self.plugin._model)
        self.assertFalse(self.plugin._initialized)

    def test_cleanup_not_initialized(self):
        """Test cleanup when plugin is not initialized"""
        # Act - should not raise exception
        self.plugin.cleanup()
        
        # Assert
        self.assertFalse(self.plugin._initialized)

    def test_configuration_schema(self):
        """Test configuration schema"""
        schema = self.plugin.get_configuration_schema()
        
        # Check required schema properties
        required_keys = [
            "executable_path", "default_depth", "default_limit",
            "show_full_paths", "files_only", "apparent_size",
            "output_format", "color_scheme", "use_cache", "cache_ttl"
        ]
        
        for key in required_keys:
            self.assertIn(key, schema)
        
        # Check some specific schema details
        self.assertEqual(schema["executable_path"]["default"], "dust")
        self.assertEqual(schema["default_depth"]["default"], 3)
        self.assertTrue(schema["use_cache"]["default"])

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_get_settings(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test getting plugin settings"""
        # Setup mock view with test values
        mock_view = Mock()
        mock_view.dust_max_depth_spinbox.value.return_value = 5
        mock_view.dust_lines_spinbox.value.return_value = 100
        mock_view.dust_reverse_sort_checkbox.isChecked.return_value = True
        mock_view.dust_apparent_size_checkbox.isChecked.return_value = False
        mock_view.dust_min_size_input.text.return_value = "1M"
        mock_view.dust_path_input.text.return_value = "/test/path"
        mock_view.dust_include_types_input.text.return_value = "txt,pdf"
        mock_view.dust_exclude_patterns_input.text.return_value = "*.tmp"
        
        mock_view_class.return_value = mock_view
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        settings = self.plugin.get_settings()
        
        # Assert
        expected_settings = {
            "max_depth": 5,
            "number_of_lines": 100,
            "sort_reverse": True,
            "apparent_size": False,
            "min_size": "1M",
            "target_path": "/test/path",
            "include_types": "txt,pdf",
            "exclude_patterns": "*.tmp"
        }
        
        self.assertEqual(settings, expected_settings)

    def test_get_settings_not_initialized(self):
        """Test getting settings when plugin is not initialized"""
        # Act
        settings = self.plugin.get_settings()
        
        # Assert
        self.assertEqual(settings, {})

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_apply_settings(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test applying plugin settings"""
        # Setup mock view
        mock_view = Mock()
        mock_view.dust_max_depth_spinbox = Mock()
        mock_view.dust_lines_spinbox = Mock()
        mock_view.dust_reverse_sort_checkbox = Mock()
        mock_view.dust_apparent_size_checkbox = Mock()
        mock_view.dust_min_size_input = Mock()
        mock_view.dust_path_input = Mock()
        mock_view.dust_include_types_input = Mock()
        mock_view.dust_exclude_patterns_input = Mock()
        
        mock_view_class.return_value = mock_view
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Test settings
        test_settings = {
            "max_depth": 7,
            "number_of_lines": 200,
            "sort_reverse": False,
            "apparent_size": True,
            "min_size": "2M",
            "target_path": "/custom/path",
            "include_types": "doc,docx",
            "exclude_patterns": "*.bak"
        }
        
        # Act
        self.plugin.apply_settings(test_settings)
        
        # Assert
        mock_view.dust_max_depth_spinbox.setValue.assert_called_with(7)
        mock_view.dust_lines_spinbox.setValue.assert_called_with(200)
        mock_view.dust_reverse_sort_checkbox.setChecked.assert_called_with(False)
        mock_view.dust_apparent_size_checkbox.setChecked.assert_called_with(True)
        mock_view.dust_min_size_input.setText.assert_called_with("2M")
        mock_view.dust_path_input.setText.assert_called_with("/custom/path")
        mock_view.dust_include_types_input.setText.assert_called_with("doc,docx")
        mock_view.dust_exclude_patterns_input.setText.assert_called_with("*.bak")

    def test_apply_settings_not_initialized(self):
        """Test applying settings when plugin is not initialized"""
        # Act - should not raise exception
        self.plugin.apply_settings({"max_depth": 5})
        
        # Assert - no specific assertion needed, just that no exception is raised

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_handle_directory_analysis(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test handling directory analysis request"""
        # Setup mock view
        mock_view = Mock()
        mock_view.dust_path_input = Mock()
        mock_view_class.return_value = mock_view
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        result = self.plugin.handle_directory_analysis("/analysis/path")
        
        # Assert
        self.assertTrue(result)
        mock_view.dust_path_input.setText.assert_called_with("/analysis/path")

    def test_handle_directory_analysis_not_initialized(self):
        """Test handling directory analysis when not initialized"""
        # Act
        result = self.plugin.handle_directory_analysis("/test/path")
        
        # Assert - depends on whether initialization succeeds
        self.assertIsInstance(result, bool)

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_get_status_info(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test getting plugin status information"""
        # Setup mocks
        mock_view = Mock()
        mock_view.dust_path_input.text.return_value = "/current/directory"
        mock_view_class.return_value = mock_view
        
        mock_model = Mock()
        mock_model.get_cache_info.return_value = {"cache_enabled": True}
        mock_model_class.return_value = mock_model
        
        # Setup tool availability
        with patch.object(self.plugin, 'check_tools_availability', return_value=True):
            # Initialize plugin
            self.plugin.initialize()
            
            # Act
            status_info = self.plugin.get_status_info()
        
        # Assert
        self.assertTrue(status_info["initialized"])
        self.assertTrue(status_info["tool_available"])
        self.assertEqual(status_info["current_directory"], "/current/directory")
        self.assertEqual(status_info["cache_info"], {"cache_enabled": True})

    def test_get_status_info_not_initialized(self):
        """Test getting status info when not initialized"""
        # Act
        status_info = self.plugin.get_status_info()
        
        # Assert
        self.assertFalse(status_info["initialized"])
        self.assertIsInstance(status_info["tool_available"], bool)

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_execute_command_analyze(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test executing analyze command"""
        # Setup mocks
        mock_view = Mock()
        mock_view.dust_path_input = Mock()
        mock_view_class.return_value = mock_view
        
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        result = self.plugin.execute_command("analyze", {"directory": "/test/dir"})
        
        # Assert
        self.assertEqual(result["status"], "analysis_started")
        mock_view.dust_path_input.setText.assert_called_with("/test/dir")
        mock_controller._execute_analysis.assert_called_once()

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_execute_command_check_tool(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test executing check_tool command"""
        # Setup mock
        mock_model = Mock()
        mock_model.check_dust_availability.return_value = (True, "dust 0.8.0", "")
        mock_model_class.return_value = mock_model
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        result = self.plugin.execute_command("check_tool")
        
        # Assert
        self.assertEqual(result["status"], "tool_checked")
        self.assertTrue(result["available"])
        self.assertEqual(result["version"], "dust 0.8.0")
        self.assertEqual(result["error"], "")

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_execute_command_unknown(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test executing unknown command"""
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        result = self.plugin.execute_command("unknown_command")
        
        # Assert
        self.assertIn("error", result)
        self.assertIn("Unknown command", result["error"])

    def test_execute_command_not_initialized(self):
        """Test executing command when not initialized"""
        # Act
        result = self.plugin.execute_command("analyze")
        
        # Assert
        self.assertIn("error", result)
        self.assertIn("not initialized", result["error"])

    @patch('tools.dust.plugin.DustModel')
    @patch('tools.dust.plugin.DustView')
    @patch('tools.dust.plugin.DustController')
    def test_execute_command_exception(self, mock_controller_class, mock_view_class, mock_model_class):
        """Test executing command with exception"""
        # Setup mock to raise exception
        mock_controller = Mock()
        mock_controller._execute_analysis.side_effect = Exception("Command failed")
        mock_controller_class.return_value = mock_controller
        
        # Initialize plugin
        self.plugin.initialize()
        
        # Act
        result = self.plugin.execute_command("analyze")
        
        # Assert
        self.assertIn("error", result)
        self.assertIn("Command failed", result["error"])


class TestCreatePlugin(unittest.TestCase):
    """Test cases for create_plugin function"""

    def test_create_plugin(self):
        """Test create_plugin function"""
        plugin = create_plugin()
        
        self.assertIsInstance(plugin, DustPlugin)
        self.assertIsInstance(plugin, PluginInterface)


if __name__ == '__main__':
    unittest.main()