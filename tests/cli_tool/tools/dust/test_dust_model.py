"""
Comprehensive unit tests for dust_model.py
Tests for DustModel initialization, configuration loading, command execution, error handling,
ANSI to HTML conversion, and result parsing.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
import pytest
from tools.dust.dust_model import DustModel


class TestDustModel(unittest.TestCase):
    """Test cases for DustModel"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock config_manager to avoid real config dependencies
        with patch('tools.dust.dust_model.config_manager') as mock_config:
            mock_config.get.return_value = 'dust'
            self.model = DustModel()
        
    def tearDown(self):
        """Clean up after each test method"""
        self.model = None

    @patch('tools.dust.dust_model.config_manager')
    def test_initialization_with_config(self, mock_config):
        """Test DustModel initialization with configuration loading"""
        # Arrange
        mock_config.get.return_value = '/usr/bin/dust'
        
        # Act
        model = DustModel()
        
        # Assert
        mock_config.get.assert_called_once_with('tools.dust.executable_path')
        self.assertEqual(model.dust_executable_path, '/usr/bin/dust')
        
    @patch('tools.dust.dust_model.config_manager')
    def test_initialization_default_config(self, mock_config):
        """Test DustModel initialization with default configuration"""
        # Arrange
        mock_config.get.return_value = None
        
        # Act
        model = DustModel()
        
        # Assert
        self.assertIsNone(model.dust_executable_path)

    @patch('tools.dust.dust_model.subprocess.Popen')
    @patch('tools.dust.dust_model.Ansi2HTMLConverter')
    def test_execute_dust_command_success(self, mock_converter, mock_popen):
        """Test successful dust command execution"""
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = (b'100M /home/user\n50M /home/user/docs', b'')
        mock_popen.return_value = mock_process
        
        mock_conv = Mock()
        mock_conv.convert.return_value = '<span>100M /home/user</span>'
        mock_converter.return_value = mock_conv
        
        # Act
        html_output, html_error = self.model.execute_dust_command()
        
        # Assert
        mock_popen.assert_called_once()
        mock_process.communicate.assert_called_once()
        mock_conv.convert.assert_called_once()
        self.assertIsInstance(html_output, str)
        self.assertEqual(html_error, "")

    @patch('tools.dust.dust_model.subprocess.Popen')
    def test_execute_dust_command_file_not_found(self, mock_popen):
        """Test dust command execution when executable not found"""
        # Arrange
        mock_popen.side_effect = FileNotFoundError()
        
        # Act
        html_output, html_error = self.model.execute_dust_command()
        
        # Assert
        self.assertEqual(html_output, "")
        self.assertIn("'dust' executable not found", html_error)

    @patch('tools.dust.dust_model.subprocess.Popen')
    def test_execute_dust_command_exception(self, mock_popen):
        """Test dust command execution with unexpected exception"""
        # Arrange
        mock_popen.side_effect = Exception("Unexpected error")
        
        # Act
        html_output, html_error = self.model.execute_dust_command()
        
        # Assert
        self.assertEqual(html_output, "")
        self.assertIn("An unexpected error occurred", html_error)

    @patch('tools.dust.dust_model.subprocess.Popen')
    @patch('tools.dust.dust_model.Ansi2HTMLConverter')
    def test_execute_dust_command_with_parameters(self, mock_converter, mock_popen):
        """Test dust command execution with various parameters"""
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = (b'output', b'')
        mock_popen.return_value = mock_process
        
        mock_conv = Mock()
        mock_conv.convert.return_value = 'converted output'
        mock_converter.return_value = mock_conv
        
        # Act
        self.model.execute_dust_command(
            target_path="/test/path",
            max_depth=5,
            sort_reverse=False,
            number_of_lines=100,
            file_types=['txt', 'pdf'],
            exclude_patterns=['*.tmp', 'node_modules'],
            show_apparent_size=True,
            min_size="1M",
            full_paths=True,
            files_only=True
        )
        
        # Assert
        mock_popen.assert_called_once()
        # Check that the command was built with correct parameters
        call_args = mock_popen.call_args[0][0]  # Get the command list
        self.assertIn('/test/path', call_args)
        self.assertIn('-d', call_args)
        self.assertIn('5', call_args)
        self.assertIn('-n', call_args)
        self.assertIn('100', call_args)

    def test_build_dust_command_basic(self):
        """Test basic dust command building"""
        # Act
        command = self.model._build_dust_command(
            target_path=".",
            max_depth=None,
            sort_reverse=True,
            number_of_lines=None,
            file_types=None,
            exclude_patterns=None,
            show_apparent_size=False,
            min_size=None,
            full_paths=False,
            files_only=False
        )
        
        # Assert
        self.assertIn('dust', command[0])
        self.assertIn('.', command)
        self.assertIn('-r', command)
        self.assertIn('--color', command)

    def test_build_dust_command_all_parameters(self):
        """Test dust command building with all parameters"""
        # Act
        command = self.model._build_dust_command(
            target_path="/home/user",
            max_depth=3,
            sort_reverse=False,
            number_of_lines=50,
            file_types=['txt', 'pdf'],
            exclude_patterns=['*.tmp'],
            show_apparent_size=True,
            min_size="1M",
            full_paths=True,
            files_only=True
        )
        
        # Assert
        expected_elements = [
            '/home/user', '-d', '3', '-n', '50', '-t', 'txt', '-t', 'pdf',
            '-X', '*.tmp', '-s', '-z', '1M', '-p', '-f', '--color'
        ]
        
        for element in expected_elements:
            self.assertIn(element, command)

    def test_parse_dust_output_empty(self):
        """Test parsing empty dust output"""
        # Act
        result = self.model.parse_dust_output("")
        
        # Assert
        self.assertEqual(result, [])

    def test_parse_dust_output_valid(self):
        """Test parsing valid dust output"""
        # Arrange
        raw_output = "100M /home/user\n50M /home/user/docs\n25M /home/user/pics"
        
        # Act
        result = self.model.parse_dust_output(raw_output)
        
        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['size'], '100M')
        self.assertEqual(result[0]['path'], '/home/user')
        self.assertEqual(result[1]['size'], '50M')
        self.assertEqual(result[1]['path'], '/home/user/docs')

    def test_parse_dust_output_malformed(self):
        """Test parsing malformed dust output"""
        # Arrange
        raw_output = "malformed line\n\n   \nanother bad line"
        
        # Act
        result = self.model.parse_dust_output(raw_output)
        
        # Assert
        # Should handle malformed lines gracefully
        self.assertIsInstance(result, list)

    @patch('tools.dust.dust_model.os.path.exists')
    @patch('tools.dust.dust_model.os.path.isdir')
    def test_validate_path_valid(self, mock_isdir, mock_exists):
        """Test path validation with valid directory"""
        # Arrange
        mock_exists.return_value = True
        mock_isdir.return_value = True
        
        # Act
        result = self.model.validate_path("/valid/path")
        
        # Assert
        self.assertTrue(result)

    @patch('tools.dust.dust_model.os.path.exists')
    def test_validate_path_invalid(self, mock_exists):
        """Test path validation with invalid path"""
        # Arrange
        mock_exists.return_value = False
        
        # Act
        result = self.model.validate_path("/invalid/path")
        
        # Assert
        self.assertFalse(result)

    @patch('tools.dust.dust_model.os.path.exists')
    def test_validate_path_exception(self, mock_exists):
        """Test path validation with exception"""
        # Arrange
        mock_exists.side_effect = Exception("Permission denied")
        
        # Act
        result = self.model.validate_path("/some/path")
        
        # Assert
        self.assertFalse(result)

    @patch('tools.dust.dust_model.config_manager')
    def test_get_default_settings(self, mock_config):
        """Test getting default settings"""
        # Arrange
        mock_config.get.side_effect = lambda key, default=None: {
            'tools.dust.default_max_depth': 5,
            'tools.dust.default_sort_reverse': False,
            'tools.dust.default_number_of_lines': 25,
            'tools.dust.default_show_apparent_size': True,
            'tools.dust.default_min_size': '1M'
        }.get(key, default)
        
        # Act
        settings = self.model.get_default_settings()
        
        # Assert
        self.assertEqual(settings['max_depth'], 5)
        self.assertFalse(settings['sort_reverse'])
        self.assertEqual(settings['number_of_lines'], 25)
        self.assertTrue(settings['show_apparent_size'])
        self.assertEqual(settings['min_size'], '1M')

    @patch('tools.dust.dust_model.subprocess.run')
    def test_check_dust_availability_success(self, mock_run):
        """Test successful dust availability check"""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "dust 0.8.0"
        mock_run.return_value = mock_result
        
        # Act
        available, version, error = self.model.check_dust_availability()
        
        # Assert
        self.assertTrue(available)
        self.assertEqual(version, "dust 0.8.0")
        self.assertEqual(error, "")

    @patch('tools.dust.dust_model.subprocess.run')
    def test_check_dust_availability_not_found(self, mock_run):
        """Test dust availability check when not found"""
        # Arrange
        mock_run.side_effect = FileNotFoundError()
        
        # Act
        available, version, error = self.model.check_dust_availability()
        
        # Assert
        self.assertFalse(available)
        self.assertEqual(version, "")
        self.assertIn("Dust executable not found", error)

    @patch('tools.dust.dust_model.subprocess.run')
    def test_check_dust_availability_timeout(self, mock_run):
        """Test dust availability check with timeout"""
        # Arrange
        mock_run.side_effect = subprocess.TimeoutExpired('dust', 10)
        
        # Act
        available, version, error = self.model.check_dust_availability()
        
        # Assert
        self.assertFalse(available)
        self.assertEqual(version, "")
        self.assertIn("Dust command timed out", error)

    @patch('tools.dust.dust_model.subprocess.run')
    def test_check_dust_availability_nonzero_exit(self, mock_run):
        """Test dust availability check with non-zero exit code"""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        # Act
        available, version, error = self.model.check_dust_availability()
        
        # Assert
        self.assertFalse(available)
        self.assertEqual(version, "")
        self.assertIn("returned non-zero exit code", error)

    @patch('tools.dust.dust_model.config_manager')
    def test_get_cache_info(self, mock_config):
        """Test getting cache information"""
        # Arrange
        mock_config.get.side_effect = lambda key, default=None: {
            'tools.dust.use_cache': True,
            'tools.dust.cache_ttl': 3600
        }.get(key, default)
        
        # Act
        cache_info = self.model.get_cache_info()
        
        # Assert
        self.assertTrue(cache_info['cache_enabled'])
        self.assertEqual(cache_info['cache_ttl'], 3600)
        self.assertEqual(cache_info['cache_entries'], 0)
        self.assertEqual(cache_info['cache_size'], 0)

    @patch('tools.dust.dust_model.subprocess.Popen')
    @patch('tools.dust.dust_model.Ansi2HTMLConverter')
    def test_execute_dust_command_with_stderr(self, mock_converter, mock_popen):
        """Test dust command execution with stderr output"""
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = (b'output', b'warning message')
        mock_popen.return_value = mock_process
        
        mock_conv = Mock()
        mock_conv.convert.side_effect = ['converted output', 'converted error']
        mock_converter.return_value = mock_conv
        
        # Act
        html_output, html_error = self.model.execute_dust_command()
        
        # Assert
        self.assertEqual(html_output, 'converted output')
        self.assertEqual(html_error, 'converted error')

    @patch('tools.dust.dust_model.subprocess.Popen')
    @patch('tools.dust.dust_model.Ansi2HTMLConverter')
    def test_ansi_to_html_conversion(self, mock_converter, mock_popen):
        """Test ANSI to HTML conversion functionality"""
        # Arrange
        mock_process = Mock()
        mock_process.communicate.return_value = (b'\x1b[32mGreen text\x1b[0m', b'')
        mock_popen.return_value = mock_process
        
        mock_conv = Mock()
        mock_conv.convert.return_value = '<span style="color: green;">Green text</span>'
        mock_converter.return_value = mock_conv
        
        # Act
        html_output, html_error = self.model.execute_dust_command()
        
        # Assert
        mock_conv.convert.assert_called_once_with('Green text', full=False)
        self.assertIn('Green text', html_output)

    def test_build_dust_command_edge_cases(self):
        """Test dust command building with edge cases"""
        # Test with zero depth
        command = self.model._build_dust_command(
            target_path=".", max_depth=0, sort_reverse=True,
            number_of_lines=0, file_types=[], exclude_patterns=[],
            show_apparent_size=False, min_size="", full_paths=False, files_only=False
        )
        
        # Should not include depth or lines if they are 0 or negative
        self.assertNotIn('-d', command)
        self.assertNotIn('-n', command)
        
        # Test with None values
        command = self.model._build_dust_command(
            target_path=None, max_depth=None, sort_reverse=False,
            number_of_lines=None, file_types=None, exclude_patterns=None,
            show_apparent_size=False, min_size=None, full_paths=False, files_only=False
        )
        
        # Should still have basic command structure
        self.assertIn('dust', command[0])
        self.assertIn('--color', command)


if __name__ == '__main__':
    unittest.main()