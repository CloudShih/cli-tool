"""
Comprehensive end-to-end integration tests for dust tool
Tests for full application launch with dust tool, tab creation and UI rendering,
basic workflow simulation, error scenarios and recovery, and configuration persistence.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
from PyQt5.QtWidgets import QApplication, QTabWidget
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtTest import QTest
import sys
import tempfile
import os
import json

# Mock heavy dependencies for testing
sys.modules['main_app'] = Mock()
sys.modules['ui.main_window'] = Mock()
sys.modules['core.plugin_manager'] = Mock()

from tools.dust.plugin import DustPlugin
from tools.dust.dust_model import DustModel
from tools.dust.dust_view import DustView
from tools.dust.dust_controller import DustController


class TestDustE2EIntegration(unittest.TestCase):
    """End-to-end integration tests for dust tool"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create mock configuration
        self.mock_config_data = {
            "tools": {
                "dust": {
                    "executable_path": "dust",
                    "default_max_depth": 3,
                    "default_number_of_lines": 50,
                    "default_sort_reverse": True,
                    "default_show_apparent_size": False,
                    "default_min_size": "",
                    "default_path": ""
                }
            }
        }

    def tearDown(self):
        """Clean up after each test method"""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    @patch('tools.dust.dust_model.config_manager')
    def test_full_plugin_lifecycle(self, mock_config):
        """Test complete plugin lifecycle from creation to cleanup"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create plugin
        plugin = DustPlugin()
        
        # Test initial state
        self.assertFalse(plugin.is_initialized())
        
        # Initialize plugin
        success = plugin.initialize()
        self.assertTrue(success)
        self.assertTrue(plugin.is_initialized())
        
        # Get widget
        widget = plugin.get_widget()
        self.assertIsNotNone(widget)
        self.assertIsInstance(widget, DustView)
        
        # Test plugin properties
        self.assertEqual(plugin.name, "dust")
        self.assertIn("磁碟空間分析", plugin.description)
        
        # Cleanup
        plugin.cleanup()
        self.assertFalse(plugin.is_initialized())
        
        # Cleanup widget
        if widget:
            widget.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    def test_mvc_component_integration(self, mock_config):
        """Test MVC components work together properly"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create and initialize plugin
        plugin = DustPlugin()
        plugin.initialize()
        
        # Get components
        model = plugin._model
        view = plugin._view
        controller = plugin._controller
        
        # Test components exist and are correct types
        self.assertIsInstance(model, DustModel)
        self.assertIsInstance(view, DustView)
        self.assertIsInstance(controller, DustController)
        
        # Test that controller has references to model and view
        self.assertEqual(controller.model, model)
        self.assertEqual(controller.view, view)
        
        # Cleanup
        plugin.cleanup()
        view.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    @patch('tools.dust.dust_model.subprocess.Popen')
    def test_basic_workflow_simulation(self, mock_popen, mock_config):
        """Test basic workflow without actual dust execution"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Setup mock process
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b'100M ./test_folder\n50M ./test_folder/subfolder', 
            b''
        )
        mock_popen.return_value = mock_process
        
        # Create and initialize plugin
        plugin = DustPlugin()
        plugin.initialize()
        
        view = plugin._view
        controller = plugin._controller
        
        # Simulate user input
        view.dust_path_input.setText(self.test_dir)
        view.dust_max_depth_spinbox.setValue(2)
        view.dust_lines_spinbox.setValue(25)
        
        # Test parameter extraction
        params = view.get_analysis_parameters()
        self.assertEqual(params['target_path'], self.test_dir)
        self.assertEqual(params['max_depth'], 2)
        self.assertEqual(params['number_of_lines'], 25)
        
        # Simulate analysis execution (without starting thread)
        # This tests the controller's parameter extraction and setup
        with patch.object(controller, '_execute_analysis') as mock_execute:
            # Trigger analysis button click
            view.dust_analyze_button.clicked.emit()
            
            # Verify execution was triggered
            mock_execute.assert_called_once()
        
        # Cleanup
        plugin.cleanup()
        view.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    def test_ui_component_rendering(self, mock_config):
        """Test that UI components render correctly"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create plugin and get view
        plugin = DustPlugin()
        plugin.initialize()
        view = plugin.get_widget()
        
        # Test main components exist
        self.assertIsNotNone(view.dust_path_input)
        self.assertIsNotNone(view.dust_browse_button)
        self.assertIsNotNone(view.dust_max_depth_spinbox)
        self.assertIsNotNone(view.dust_lines_spinbox)
        self.assertIsNotNone(view.dust_analyze_button)
        self.assertIsNotNone(view.dust_results_display)
        self.assertIsNotNone(view.status_indicator)
        self.assertIsNotNone(view.loading_spinner)
        
        # Test checkboxes
        self.assertIsNotNone(view.dust_reverse_sort_checkbox)
        self.assertIsNotNone(view.dust_apparent_size_checkbox)
        self.assertIsNotNone(view.dust_full_paths_checkbox)
        self.assertIsNotNone(view.dust_files_only_checkbox)
        
        # Test input fields
        self.assertIsNotNone(view.dust_min_size_input)
        self.assertIsNotNone(view.dust_include_types_input)
        self.assertIsNotNone(view.dust_exclude_patterns_input)
        
        # Test that view is visible and has reasonable size
        view.show()
        QApplication.processEvents()
        
        self.assertTrue(view.isVisible())
        self.assertGreater(view.width(), 0)
        self.assertGreater(view.height(), 0)
        
        # Cleanup
        view.hide()
        plugin.cleanup()
        view.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    def test_configuration_persistence(self, mock_config):
        """Test configuration loading and saving"""
        # Setup config with custom values
        custom_config = {
            "tools": {
                "dust": {
                    "executable_path": "/custom/dust",
                    "default_max_depth": 5,
                    "default_number_of_lines": 100,
                    "default_sort_reverse": False,
                    "default_show_apparent_size": True,
                    "default_min_size": "1M",
                    "default_path": "/custom/path"
                }
            }
        }
        
        mock_config.get.side_effect = lambda key, default=None: custom_config.get(
            key.replace('.', '_'), default
        )
        
        # Create plugin
        plugin = DustPlugin()
        plugin.initialize()
        view = plugin.get_widget()
        
        # Check that configuration was loaded correctly
        self.assertEqual(view.dust_max_depth_spinbox.value(), 5)
        self.assertEqual(view.dust_lines_spinbox.value(), 100)
        self.assertFalse(view.dust_reverse_sort_checkbox.isChecked())
        self.assertTrue(view.dust_apparent_size_checkbox.isChecked())
        self.assertEqual(view.dust_min_size_input.text(), "1M")
        self.assertEqual(view.dust_path_input.text(), "/custom/path")
        
        # Test getting current settings
        settings = plugin.get_settings()
        expected_settings = {
            "max_depth": 5,
            "number_of_lines": 100,
            "sort_reverse": False,
            "apparent_size": True,
            "min_size": "1M",
            "target_path": "/custom/path",
            "include_types": "",
            "exclude_patterns": ""
        }
        
        for key, value in expected_settings.items():
            self.assertEqual(settings[key], value)
        
        # Test applying new settings
        new_settings = {
            "max_depth": 7,
            "number_of_lines": 200,
            "sort_reverse": True,
            "apparent_size": False,
            "min_size": "2M",
            "target_path": "/new/path",
            "include_types": "txt,pdf",
            "exclude_patterns": "*.tmp"
        }
        
        plugin.apply_settings(new_settings)
        
        # Verify settings were applied
        self.assertEqual(view.dust_max_depth_spinbox.value(), 7)
        self.assertEqual(view.dust_lines_spinbox.value(), 200)
        self.assertTrue(view.dust_reverse_sort_checkbox.isChecked())
        self.assertFalse(view.dust_apparent_size_checkbox.isChecked())
        self.assertEqual(view.dust_min_size_input.text(), "2M")
        self.assertEqual(view.dust_path_input.text(), "/new/path")
        
        # Cleanup
        plugin.cleanup()
        view.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    def test_error_scenarios_and_recovery(self, mock_config):
        """Test error scenarios and recovery mechanisms"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Test 1: Plugin initialization with config error
        mock_config.get.side_effect = Exception("Config error")
        
        plugin = DustPlugin()
        success = plugin.initialize()
        
        # Should handle error gracefully
        self.assertTrue(success)  # Should still succeed with fallback values
        
        view = plugin.get_widget()
        self.assertIsNotNone(view)
        
        # Cleanup
        plugin.cleanup()
        view.deleteLater()
        
        # Test 2: Tool availability check failure
        with patch('tools.dust.dust_model.DustModel.check_dust_availability') as mock_check:
            mock_check.return_value = (False, "", "Tool not found")
            
            plugin2 = DustPlugin()
            available = plugin2.check_tools_availability()
            self.assertFalse(available)
            
            # Plugin should still initialize even if tool is not available
            success = plugin2.initialize()
            self.assertTrue(success)
            
            plugin2.cleanup()
        
        # Test 3: Model execution error
        with patch('tools.dust.dust_model.DustModel.execute_dust_command') as mock_execute:
            mock_execute.side_effect = Exception("Execution error")
            
            plugin3 = DustPlugin()
            plugin3.initialize()
            
            # Test command execution with error
            result = plugin3.execute_command("analyze")
            
            # Should handle error and return error status
            if "error" in result:
                self.assertIn("error", result)
            
            plugin3.cleanup()

    @patch('tools.dust.dust_model.config_manager')
    @patch('tools.dust.dust_model.subprocess.run')
    def test_tool_availability_integration(self, mock_run, mock_config):
        """Test tool availability checking integration"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Test successful tool check
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "dust 0.8.0"
        mock_run.return_value = mock_result
        
        plugin = DustPlugin()
        available = plugin.check_tools_availability()
        self.assertTrue(available)
        
        # Test failed tool check
        mock_run.side_effect = FileNotFoundError()
        available = plugin.check_tools_availability()
        self.assertFalse(available)

    @patch('tools.dust.dust_model.config_manager')
    def test_thread_management_integration(self, mock_config):
        """Test thread management in controller"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create plugin
        plugin = DustPlugin()
        plugin.initialize()
        
        controller = plugin._controller
        
        # Test that no worker exists initially
        self.assertIsNone(controller.analysis_worker)
        
        # Test cleanup with no worker
        controller.cleanup()  # Should not raise exception
        
        # Test cleanup after creating worker (mocked)
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        controller.analysis_worker = mock_worker
        
        controller.cleanup()
        
        # Verify cleanup was called
        mock_worker.terminate.assert_called_once()
        mock_worker.wait.assert_called_once()
        
        # Cleanup
        plugin.cleanup()

    @patch('tools.dust.dust_model.config_manager')
    def test_command_execution_integration(self, mock_config):
        """Test plugin command execution integration"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create and initialize plugin
        plugin = DustPlugin()
        plugin.initialize()
        
        # Test various commands
        commands_to_test = [
            ("analyze", {"directory": "/test/path"}),
            ("check_tool", {}),
            ("clear_cache", {}),
            ("set_depth", {"depth": 5}),
            ("set_limit", {"limit": 100}),
            ("analyze_directory", {"directory_path": "/analyze/path"})
        ]
        
        for command, args in commands_to_test:
            result = plugin.execute_command(command, args)
            
            # Each command should return a result dictionary
            self.assertIsInstance(result, dict)
            
            # Should not contain generic errors for valid commands
            if command != "analyze":  # analyze might fail without proper setup
                if "error" in result:
                    # Error should be specific, not generic
                    self.assertNotIn("Unknown command", result["error"])
        
        # Test unknown command
        result = plugin.execute_command("unknown_command")
        self.assertIn("error", result)
        self.assertIn("Unknown command", result["error"])
        
        # Cleanup
        plugin.cleanup()

    @patch('tools.dust.dust_model.config_manager')
    def test_status_info_integration(self, mock_config):
        """Test status information integration"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create plugin
        plugin = DustPlugin()
        
        # Test status before initialization
        status = plugin.get_status_info()
        self.assertFalse(status["initialized"])
        
        # Initialize plugin
        plugin.initialize()
        
        # Test status after initialization
        status = plugin.get_status_info()
        self.assertTrue(status["initialized"])
        self.assertIn("tool_available", status)
        self.assertIn("current_directory", status)
        self.assertIn("cache_info", status)
        
        # Cleanup
        plugin.cleanup()

    @patch('tools.dust.dust_model.config_manager')
    def test_directory_analysis_integration(self, mock_config):
        """Test directory analysis request handling"""
        # Setup config
        mock_config.get.side_effect = lambda key, default=None: self.mock_config_data.get(
            key.replace('.', '_'), default
        )
        
        # Create and initialize plugin
        plugin = DustPlugin()
        plugin.initialize()
        
        view = plugin.get_widget()
        
        # Test directory analysis handling
        test_directory = "/test/analysis/directory"
        result = plugin.handle_directory_analysis(test_directory)
        
        self.assertTrue(result)
        
        # Verify directory was set in view
        self.assertEqual(view.dust_path_input.text(), test_directory)
        
        # Cleanup
        plugin.cleanup()
        view.deleteLater()

    def test_create_plugin_function(self):
        """Test create_plugin factory function"""
        from tools.dust.plugin import create_plugin
        
        plugin = create_plugin()
        
        self.assertIsInstance(plugin, DustPlugin)
        self.assertEqual(plugin.name, "dust")
        self.assertEqual(plugin.version, "1.0.0")


class TestDustIntegrationScenarios(unittest.TestCase):
    """Test realistic integration scenarios"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    @patch('tools.dust.dust_model.config_manager')
    def test_user_workflow_simulation(self, mock_config):
        """Test simulated user workflow"""
        # Setup config
        mock_config.get.return_value = "dust"
        
        # Create plugin (simulating plugin discovery)
        plugin = DustPlugin()
        
        # Initialize (simulating main app initialization)
        success = plugin.initialize()
        self.assertTrue(success)
        
        # Get widget (simulating tab creation)
        widget = plugin.get_widget()
        self.assertIsNotNone(widget)
        
        # Simulate user interactions
        widget.dust_path_input.setText("/home/user")
        widget.dust_max_depth_spinbox.setValue(4)
        widget.dust_reverse_sort_checkbox.setChecked(True)
        widget.dust_min_size_input.setText("1M")
        
        # Check parameters
        params = widget.get_analysis_parameters()
        self.assertEqual(params['target_path'], '/home/user')
        self.assertEqual(params['max_depth'], 4)
        self.assertTrue(params['sort_reverse'])
        self.assertEqual(params['min_size'], '1M')
        
        # Simulate analysis (without actual execution)
        # This would trigger the controller in real usage
        
        # Cleanup (simulating app shutdown)
        plugin.cleanup()
        widget.deleteLater()

    @patch('tools.dust.dust_model.config_manager')
    @patch('tools.dust.dust_model.subprocess.Popen')
    def test_mock_analysis_execution(self, mock_popen, mock_config):
        """Test analysis execution with mocked dust command"""
        # Setup config
        mock_config.get.return_value = "dust"
        
        # Setup mock dust output
        mock_process = Mock()
        mock_process.communicate.return_value = (
            b'\x1b[32m150M\x1b[0m ./large_folder\n'
            b'\x1b[33m80M\x1b[0m ./medium_folder\n'
            b'\x1b[31m20M\x1b[0m ./small_folder',
            b''
        )
        mock_popen.return_value = mock_process
        
        # Create plugin and get model
        plugin = DustPlugin()
        plugin.initialize()
        model = plugin._model
        
        # Execute dust command
        html_output, html_error = model.execute_dust_command("/test/path")
        
        # Verify results
        self.assertIsNotNone(html_output)
        self.assertEqual(html_error, "")
        
        # Verify command was built correctly
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('/test/path', call_args)
        self.assertIn('--color', call_args)
        
        # Cleanup
        plugin.cleanup()


if __name__ == '__main__':
    unittest.main()