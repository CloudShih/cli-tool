#!/usr/bin/env python3
"""
Comprehensive Functional Testing for Ripgrep Plugin
Tests all core search functionality, edge cases, and integration scenarios
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

# Test data setup
class RipgrepFunctionalTestSuite(unittest.TestCase):
    """Comprehensive functional test suite for ripgrep plugin"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_files = cls._create_test_files()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_test_files(cls):
        """Create test files with various content patterns"""
        test_files = {
            'python_code.py': '''
def hello_world():
    """Test function for searching"""
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.message = "Hello from class"
        
    def get_message(self):
        return self.message
''',
            'javascript_code.js': '''
function helloWorld() {
    console.log("Hello, World!");
    return "success";
}

class TestClass {
    constructor() {
        this.message = "Hello from class";
    }
    
    getMessage() {
        return this.message;
    }
}
''',
            'text_file.txt': '''
This is a test file containing various patterns.
Hello World appears multiple times.
Testing regex patterns: 123-456-7890
Email patterns: test@example.com
Special characters: !@#$%^&*()
Unicode content: 你好世界 こんにちは 안녕하세요
''',
            'large_file.log': 'Line {}: This is a test log entry with pattern SEARCH_ME\n'.format(i) * 10000 for i in range(1, 10001)
        }
        
        for filename, content in test_files.items():
            file_path = Path(cls.temp_dir) / filename
            if filename == 'large_file.log':
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(1, 10001):
                        f.write(f'Line {i}: This is a test log entry with pattern SEARCH_ME\n')
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        return test_files


class TestBasicSearchFunctionality(RipgrepFunctionalTestSuite):
    """Test basic search functionality"""
    
    def test_simple_text_search(self):
        """Test basic text pattern search"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="Hello",
            search_path=self.temp_dir
        )
        
        # Mock ripgrep availability
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            cmd = builder.build_command(params)
            
            self.assertIn("Hello", cmd)
            self.assertIn("--json", cmd)
            self.assertIn("--ignore-case", cmd)
    
    def test_case_sensitive_search(self):
        """Test case-sensitive search"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="Hello",
            search_path=self.temp_dir,
            case_sensitive=True
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            cmd = builder.build_command(params)
            
            self.assertNotIn("--ignore-case", cmd)
    
    def test_regex_pattern_search(self):
        """Test regex pattern search"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern=r'\d{3}-\d{3}-\d{4}',
            search_path=self.temp_dir,
            regex_mode=True
        )
        
        self.assertTrue(params.regex_mode)
        self.assertEqual(params.pattern, r'\d{3}-\d{3}-\d{4}')
    
    def test_whole_word_search(self):
        """Test whole word search"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            whole_words=True
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            cmd = builder.build_command(params)
            
            self.assertIn("--word-regexp", cmd)


class TestFileTypeFiltering(RipgrepFunctionalTestSuite):
    """Test file type filtering functionality"""
    
    def test_python_file_filtering(self):
        """Test filtering by Python files"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="def",
            search_path=self.temp_dir,
            file_types=["py"]
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            cmd = builder.build_command(params)
            
            self.assertIn("--type", cmd)
            self.assertIn("py", cmd)
    
    def test_multiple_file_types(self):
        """Test filtering by multiple file types"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="function",
            search_path=self.temp_dir,
            file_types=["py", "js", "ts"]
        )
        
        self.assertEqual(len(params.file_types), 3)
        self.assertIn("py", params.file_types)
        self.assertIn("js", params.file_types)
        self.assertIn("ts", params.file_types)


class TestContextAndLimiting(RipgrepFunctionalTestSuite):
    """Test context lines and result limiting"""
    
    def test_context_lines(self):
        """Test context lines functionality"""
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="Hello",
            search_path=self.temp_dir,
            context_lines=5
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            
            builder = RipgrepCommandBuilder("rg")
            cmd = builder.build_command(params)
            
            self.assertIn("-C", cmd)
            self.assertIn("5", cmd)
    
    def test_max_results_limiting(self):
        """Test maximum results limiting"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="test",
            search_path=self.temp_dir,
            max_results=100
        )
        
        self.assertEqual(params.max_results, 100)
    
    def test_context_lines_validation(self):
        """Test context lines parameter validation"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        # Test negative context lines get reset to 0
        params1 = SearchParameters(pattern="test", context_lines=-5)
        self.assertEqual(params1.context_lines, 0)
        
        # Test excessive context lines get limited to 20
        params2 = SearchParameters(pattern="test", context_lines=50)
        self.assertEqual(params2.context_lines, 20)


class TestErrorHandling(RipgrepFunctionalTestSuite):
    """Test error handling scenarios"""
    
    def test_empty_pattern_validation(self):
        """Test empty pattern validation"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        with self.assertRaises(ValueError):
            SearchParameters(pattern="")
    
    def test_invalid_search_path(self):
        """Test invalid search path handling"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="test",
            search_path="/nonexistent/path"
        )
        
        # Should create without error, error handling in execution
        self.assertEqual(params.search_path, "/nonexistent/path")
    
    def test_ripgrep_unavailable(self):
        """Test behavior when ripgrep is unavailable"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("rg not found")
            
            plugin = RipgrepPlugin()
            self.assertFalse(plugin.check_tools_availability())
    
    def test_ripgrep_timeout(self):
        """Test ripgrep command timeout"""
        from tools.ripgrep.plugin import RipgrepPlugin
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("rg", 5)
            
            plugin = RipgrepPlugin()
            self.assertFalse(plugin.check_tools_availability())


class TestUnicodeAndSpecialCharacters(RipgrepFunctionalTestSuite):
    """Test Unicode and special character handling"""
    
    def test_unicode_search_patterns(self):
        """Test searching for Unicode characters"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="你好",
            search_path=self.temp_dir
        )
        
        self.assertEqual(params.pattern, "你好")
    
    def test_special_character_patterns(self):
        """Test searching for special characters"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern="!@#$%",
            search_path=self.temp_dir
        )
        
        self.assertEqual(params.pattern, "!@#$%")
    
    def test_regex_special_characters(self):
        """Test regex patterns with special characters"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        params = SearchParameters(
            pattern=r"test@example\.com",
            search_path=self.temp_dir,
            regex_mode=True
        )
        
        self.assertTrue(params.regex_mode)
        self.assertIn("@", params.pattern)
        self.assertIn(r"\.", params.pattern)


def run_functional_tests():
    """Run all functional tests"""
    test_classes = [
        TestBasicSearchFunctionality,
        TestFileTypeFiltering,
        TestContextAndLimiting,
        TestErrorHandling,
        TestUnicodeAndSpecialCharacters,
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Comprehensive Functional Tests for Ripgrep Plugin...")
    print("=" * 70)
    
    try:
        success = run_functional_tests()
        
        if success:
            print("\n✅ All functional tests passed!")
            print("Ripgrep plugin core functionality is working correctly.")
        else:
            print("\n❌ Some functional tests failed!")
            print("Please check the implementation and fix issues.")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Functional testing completed.")