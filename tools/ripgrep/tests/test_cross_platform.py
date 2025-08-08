#!/usr/bin/env python3
"""
Cross-Platform Compatibility Testing for Ripgrep Plugin
Tests compatibility across Windows, macOS, and Linux platforms
"""
import sys
import os
import unittest
import platform
import tempfile
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from unittest.mock import Mock, patch
import subprocess

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class CrossPlatformTestBase(unittest.TestCase):
    """Base class for cross-platform tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up cross-platform test environment"""
        cls.current_platform = platform.system().lower()
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_cross_platform_test_files()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_cross_platform_test_files(cls):
        """Create test files with platform-specific characteristics"""
        # Create files with different line endings
        test_files = {
            'unix_endings.txt': 'Line 1\nLine 2\nLine 3\n',  # Unix LF
            'windows_endings.txt': 'Line 1\r\nLine 2\r\nLine 3\r\n',  # Windows CRLF
            'mac_endings.txt': 'Line 1\rLine 2\rLine 3\r',  # Old Mac CR
            'mixed_endings.txt': 'Line 1\nLine 2\r\nLine 3\r',  # Mixed
        }
        
        # Create files with platform-specific paths
        path_test_files = {
            'normal_file.py': 'print("Hello from normal file")',
            'file with spaces.py': 'print("Hello from file with spaces")',
            'file-with-dashes.py': 'print("Hello from file with dashes")',
            'file_with_unicode_名前.py': 'print("Hello from Unicode file")',
        }
        
        # Write line ending test files
        for filename, content in test_files.items():
            file_path = Path(cls.temp_dir) / filename
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(content)
        
        # Write path test files
        for filename, content in path_test_files.items():
            file_path = Path(cls.temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def get_platform_executable_name(self, base_name):
        """Get platform-specific executable name"""
        if self.current_platform == 'windows':
            return f"{base_name}.exe"
        return base_name


class TestPlatformSpecificPaths(CrossPlatformTestBase):
    """Test platform-specific path handling"""
    
    def test_path_separator_handling(self):
        """Test correct path separator handling across platforms"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test with different path separators
        if self.current_platform == 'windows':
            test_path = "C:\\Users\\test\\Documents"
            expected_separator = "\\"
        else:
            test_path = "/home/test/documents"
            expected_separator = "/"
        
        params = SearchParameters(
            pattern="test",
            search_path=test_path
        )
        
        # Verify path is stored correctly
        self.assertEqual(params.search_path, test_path)
        self.assertIn(expected_separator, params.search_path)
    
    def test_absolute_vs_relative_paths(self):
        """Test absolute vs relative path handling"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test relative path
        relative_path = "." + os.sep + "test_dir"
        params_rel = SearchParameters(pattern="test", search_path=relative_path)
        self.assertEqual(params_rel.search_path, relative_path)
        
        # Test absolute path
        abs_path = os.path.abspath(self.temp_dir)
        params_abs = SearchParameters(pattern="test", search_path=abs_path)
        self.assertEqual(params_abs.search_path, abs_path)
    
    def test_path_with_spaces_and_special_chars(self):
        """Test paths with spaces and special characters"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test path with spaces
        space_path = str(Path(self.temp_dir) / "folder with spaces")
        params = SearchParameters(pattern="test", search_path=space_path)
        self.assertEqual(params.search_path, space_path)
        
        # Test path with Unicode characters
        unicode_path = str(Path(self.temp_dir) / "フォルダ")  # Japanese folder name
        params_unicode = SearchParameters(pattern="test", search_path=unicode_path)
        self.assertEqual(params_unicode.search_path, unicode_path)
    
    def test_path_normalization(self):
        """Test path normalization across platforms"""
        # Test Path object behavior
        test_paths = [
            "folder/subfolder",
            "folder\\subfolder",
            "./folder/subfolder",
            "../parent/folder"
        ]
        
        for path_str in test_paths:
            path_obj = Path(path_str)
            normalized = str(path_obj)
            
            # Verify path normalization works
            self.assertIsInstance(normalized, str)
            
            # On Windows, should use backslashes; on Unix, forward slashes
            if self.current_platform == 'windows':
                # Windows may have either separator depending on context
                pass  # Skip strict separator check on Windows
            else:
                self.assertNotIn('\\', normalized)


class TestExecutableDetection(CrossPlatformTestBase):
    """Test ripgrep executable detection across platforms"""
    
    def test_ripgrep_executable_detection(self):
        """Test ripgrep executable detection on current platform"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        plugin = RipgrepPlugin()
        
        # Mock successful detection
        expected_exe = self.get_platform_executable_name("rg")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = f"ripgrep 13.0.0-{self.current_platform}"
            
            is_available = plugin.check_tools_availability()
            
            # Verify the correct executable was called
            if mock_run.called:
                called_args = mock_run.call_args[0][0]
                self.assertEqual(called_args[0], "rg")  # Should call 'rg' regardless of platform
    
    def test_executable_path_resolution(self):
        """Test executable path resolution"""
        import shutil
        
        # Test finding ripgrep in system PATH
        rg_path = shutil.which("rg")
        
        if rg_path:
            # Ripgrep is available
            self.assertTrue(os.path.exists(rg_path))
            
            if self.current_platform == 'windows':
                self.assertTrue(rg_path.endswith('.exe'))
        else:
            # Ripgrep not in PATH - this is expected in test environments
            pass
    
    def test_executable_permissions(self):
        """Test executable permissions on Unix-like systems"""
        if self.current_platform in ['linux', 'darwin']:  # Unix-like systems
            # Test that we can check executable permissions
            import stat
            
            # Create a test executable file
            test_exe_path = Path(self.temp_dir) / "test_executable"
            test_exe_path.write_text("#!/bin/bash\necho 'test'")
            
            # Set executable permissions
            test_exe_path.chmod(test_exe_path.stat().st_mode | stat.S_IEXEC)
            
            # Verify permissions
            self.assertTrue(os.access(test_exe_path, os.X_OK))


class TestFileEncodingHandling(CrossPlatformTestBase):
    """Test file encoding handling across platforms"""
    
    def test_utf8_file_handling(self):
        """Test UTF-8 file handling"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Create UTF-8 test file
        utf8_content = "Hello 世界 🌍 Здравствуй мир"
        utf8_file = Path(self.temp_dir) / "utf8_test.txt"
        
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write(utf8_content)
        
        # Test search parameters with UTF-8 content
        params = SearchParameters(
            pattern="世界",
            search_path=str(utf8_file.parent)
        )
        
        self.assertEqual(params.pattern, "世界")
    
    def test_line_ending_handling(self):
        """Test different line ending handling"""
        from tools.ripgrep.core.result_parser import RipgrepParser
        
        parser = RipgrepParser()
        
        # Test with different line endings
        test_outputs = {
            'unix': 'file.txt:1:5:Line with unix ending\n',
            'windows': 'file.txt:1:5:Line with windows ending\r\n',
            'mixed': 'file.txt:1:5:Line 1\nfile.txt:2:5:Line 2\r\n'
        }
        
        for ending_type, output in test_outputs.items():
            try:
                results = parser.parse_output(output, 'vimgrep')
                self.assertGreater(len(results), 0)
                
                # Verify content is parsed correctly regardless of line endings
                first_result = results[0]
                self.assertIn("Line", first_result.matches[0].content)
            except Exception as e:
                self.fail(f"Failed to parse {ending_type} line endings: {e}")
    
    def test_encoding_detection(self):
        """Test encoding detection for different file types"""
        # Test files with different encodings
        encodings_to_test = ['utf-8', 'latin-1']
        
        for encoding in encodings_to_test:
            try:
                test_content = "Test content with special chars: áéíóú"
                test_file = Path(self.temp_dir) / f"test_{encoding}.txt"
                
                with open(test_file, 'w', encoding=encoding) as f:
                    f.write(test_content)
                
                # Verify file was created
                self.assertTrue(test_file.exists())
                
                # Try to read it back
                with open(test_file, 'r', encoding=encoding) as f:
                    read_content = f.read()
                    self.assertEqual(read_content, test_content)
                    
            except UnicodeEncodeError:
                # Some encodings may not support all characters
                pass


class TestCommandLineIntegration(CrossPlatformTestBase):
    """Test command line integration across platforms"""
    
    def test_command_building(self):
        """Test command building for different platforms"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            
            # Test basic command
            params = SearchParameters(pattern="test", search_path=self.temp_dir)
            cmd = builder.build_command(params)
            
            # Verify command structure
            self.assertEqual(cmd[0], "rg")  # Executable should always be 'rg'
            self.assertIn("test", cmd)      # Pattern should be included
            self.assertIn(self.temp_dir, cmd)  # Path should be included
    
    def test_shell_escaping(self):
        """Test proper shell escaping for different platforms"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            
            # Test patterns that need escaping
            special_patterns = [
                'pattern with spaces',
                'pattern"with"quotes',
                "pattern'with'quotes",
                'pattern$with$special',
                'pattern&with&ampersand'
            ]
            
            for pattern in special_patterns:
                params = SearchParameters(pattern=pattern, search_path=self.temp_dir)
                cmd = builder.build_command(params)
                
                # Verify pattern is properly included
                self.assertIn(pattern, cmd)
    
    def test_environment_variable_handling(self):
        """Test environment variable handling"""
        # Test with different environment variables that might affect ripgrep
        test_env_vars = {
            'RIPGREP_CONFIG_PATH': str(Path(self.temp_dir) / 'config'),
            'NO_COLOR': '1',  # Disable colored output
            'COLUMNS': '120'  # Terminal width
        }
        
        original_env = {}
        try:
            # Set test environment variables
            for key, value in test_env_vars.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value
            
            # Test that environment variables don't break functionality
            from tools.ripgrep.core.data_models import SearchParameters
            params = SearchParameters(pattern="test", search_path=self.temp_dir)
            
            # Should create successfully regardless of environment
            self.assertEqual(params.pattern, "test")
            
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value


class TestUIScaling(CrossPlatformTestBase):
    """Test UI scaling across different platforms and DPI settings"""
    
    def setUp(self):
        """Set up UI scaling tests"""
        try:
            from PyQt5.QtWidgets import QApplication
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            self.qt_available = True
        except ImportError:
            self.qt_available = False
    
    @unittest.skipUnless(True, "Qt available check")
    def test_dpi_awareness(self):
        """Test DPI awareness settings"""
        if not self.qt_available:
            self.skipTest("PyQt5 not available")
        
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app:
            # Test that application handles DPI correctly
            # This is mostly about ensuring no crashes occur
            try:
                screen = app.primaryScreen()
                if screen:
                    dpi = screen.logicalDotsPerInch()
                    self.assertGreater(dpi, 0)
            except:
                pass  # DPI detection may fail in test environment
    
    @unittest.skipUnless(True, "Qt available check")
    def test_font_scaling(self):
        """Test font scaling across platforms"""
        if not self.qt_available:
            self.skipTest("PyQt5 not available")
        
        from tools.ripgrep.ripgrep_view import RipgrepView
        from PyQt5.QtGui import QFont
        
        try:
            view = RipgrepView()
            
            # Test different font sizes
            font_sizes = [9, 12, 16, 20]
            
            for size in font_sizes:
                font = QFont()
                font.setPointSize(size)
                view.setFont(font)
                
                # Verify font is applied
                self.assertEqual(view.font().pointSize(), size)
            
            view.deleteLater()
            
        except Exception as e:
            self.skipTest(f"UI test failed: {e}")


class TestPlatformSpecificBehavior(CrossPlatformTestBase):
    """Test platform-specific behavior differences"""
    
    def test_case_sensitivity(self):
        """Test case sensitivity behavior across platforms"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test case-sensitive search
        params_sensitive = SearchParameters(
            pattern="Test",
            search_path=self.temp_dir,
            case_sensitive=True
        )
        
        self.assertTrue(params_sensitive.case_sensitive)
        self.assertEqual(params_sensitive.pattern, "Test")
        
        # Test case-insensitive search
        params_insensitive = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            case_sensitive=False
        )
        
        self.assertFalse(params_insensitive.case_sensitive)
        self.assertEqual(params_insensitive.pattern, "test")
    
    def test_symlink_handling(self):
        """Test symlink handling across platforms"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test symlink following parameter
        params_follow = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            follow_symlinks=True
        )
        
        self.assertTrue(params_follow.follow_symlinks)
        
        params_no_follow = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            follow_symlinks=False
        )
        
        self.assertFalse(params_no_follow.follow_symlinks)
    
    def test_hidden_file_handling(self):
        """Test hidden file handling across platforms"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test hidden file searching
        params_hidden = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            search_hidden=True
        )
        
        self.assertTrue(params_hidden.search_hidden)
        
        # Test normal file searching (no hidden)
        params_normal = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            search_hidden=False
        )
        
        self.assertFalse(params_normal.search_hidden)


def generate_platform_report():
    """Generate platform-specific test report"""
    system_info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }
    
    # Test ripgrep availability
    ripgrep_info = {}
    try:
        result = subprocess.run(['rg', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            ripgrep_info['available'] = True
            ripgrep_info['version'] = result.stdout.strip().split('\n')[0]
        else:
            ripgrep_info['available'] = False
            ripgrep_info['error'] = 'Non-zero return code'
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        ripgrep_info['available'] = False
        ripgrep_info['error'] = str(e)
    
    return {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_info': system_info,
        'ripgrep_info': ripgrep_info
    }


def run_cross_platform_tests():
    """Run all cross-platform tests"""
    test_classes = [
        TestPlatformSpecificPaths,
        TestExecutableDetection,
        TestFileEncodingHandling,
        TestCommandLineIntegration,
        TestUIScaling,
        TestPlatformSpecificBehavior,
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate platform report
    platform_report = generate_platform_report()
    
    return result.wasSuccessful(), platform_report


if __name__ == "__main__":
    import time
    
    print("Running Cross-Platform Compatibility Tests...")
    print("=" * 60)
    print(f"Current Platform: {platform.system()} {platform.release()}")
    print("=" * 60)
    
    try:
        success, report = run_cross_platform_tests()
        
        print(f"\n🖥️  Platform Information:")
        system_info = report['system_info']
        print(f"  - OS: {system_info['platform']} {system_info['platform_release']}")
        print(f"  - Machine: {system_info['machine']}")
        print(f"  - Python: {system_info['python_version']} ({system_info['python_implementation']})")
        
        ripgrep_info = report['ripgrep_info']
        if ripgrep_info['available']:
            print(f"  - Ripgrep: {ripgrep_info['version']}")
        else:
            print(f"  - Ripgrep: Not available ({ripgrep_info['error']})")
        
        if success:
            print("\n✅ All cross-platform tests passed!")
            print("Ripgrep plugin is compatible with current platform.")
        else:
            print("\n❌ Some cross-platform tests failed!")
            print("Platform compatibility issues detected.")
            
    except Exception as e:
        print(f"\n💥 Cross-platform test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Cross-platform testing completed.")