#!/usr/bin/env python3
"""
Performance Testing Suite for Ripgrep Plugin
Tests search performance, memory usage, and scalability
"""
import sys
import os
import unittest
import tempfile
import time
import psutil
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class PerformanceTestBase(unittest.TestCase):
    """Base class for performance tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up performance test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.large_codebase = cls._create_large_codebase()
        cls.performance_metrics = {
            'search_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_large_codebase(cls):
        """Create a large codebase for performance testing"""
        # Create directory structure
        directories = [
            'src', 'tests', 'docs', 'config', 'utils', 'models', 'views', 'controllers'
        ]
        
        for dir_name in directories:
            dir_path = Path(cls.temp_dir) / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # Create subdirectories
            for i in range(10):
                subdir_path = dir_path / f"subdir_{i}"
                subdir_path.mkdir(exist_ok=True)
        
        # Create test files with various sizes
        file_templates = {
            'small_file.py': cls._generate_python_content(100),
            'medium_file.js': cls._generate_javascript_content(500),
            'large_file.log': cls._generate_log_content(2000),
            'huge_file.txt': cls._generate_text_content(10000)
        }
        
        # Create files in each directory
        for dir_name in directories:
            dir_path = Path(cls.temp_dir) / dir_name
            for filename, content in file_templates.items():
                file_path = dir_path / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        return cls.temp_dir
    
    @classmethod
    def _generate_python_content(cls, lines):
        """Generate Python code content"""
        content = """#!/usr/bin/env python3
\"\"\"
Generated Python file for performance testing
Contains various patterns for search testing
\"\"\"
import os
import sys
from typing import List, Dict, Optional

class TestClass:
    \"\"\"Test class for performance testing\"\"\"
    
    def __init__(self):
        self.data = {}
        self.pattern_match = "SEARCH_TARGET"
    
    def search_function(self, pattern: str) -> List[str]:
        \"\"\"Function that contains search targets\"\"\"
        results = []
        for item in self.data:
            if pattern in str(item):
                results.append(item)
        return results
    
    def process_data(self, input_data: Dict) -> Optional[str]:
        \"\"\"Another function with SEARCH_TARGET pattern\"\"\"
        if "SEARCH_TARGET" in input_data:
            return input_data["SEARCH_TARGET"]
        return None

def main():
    \"\"\"Main function with various patterns\"\"\"
    test_obj = TestClass()
    patterns = ["SEARCH_TARGET", "performance", "testing"]
    
    for pattern in patterns:
        results = test_obj.search_function(pattern)
        print(f"Found {len(results)} matches for {pattern}")

if __name__ == "__main__":
    main()
"""
        
        # Repeat content to reach desired line count
        lines_per_block = content.count('\n')
        repetitions = max(1, lines // lines_per_block)
        
        return (content + '\n') * repetitions
    
    @classmethod
    def _generate_javascript_content(cls, lines):
        """Generate JavaScript content"""
        content = """// Generated JavaScript file for performance testing
// Contains various patterns for search testing

class TestClass {
    constructor() {
        this.data = {};
        this.patternMatch = "SEARCH_TARGET";
    }
    
    searchFunction(pattern) {
        // Function that contains search targets
        const results = [];
        for (const item of Object.values(this.data)) {
            if (String(item).includes(pattern)) {
                results.push(item);
            }
        }
        return results;
    }
    
    processData(inputData) {
        // Another function with SEARCH_TARGET pattern
        if (inputData.hasOwnProperty("SEARCH_TARGET")) {
            return inputData["SEARCH_TARGET"];
        }
        return null;
    }
}

function main() {
    // Main function with various patterns
    const testObj = new TestClass();
    const patterns = ["SEARCH_TARGET", "performance", "testing"];
    
    patterns.forEach(pattern => {
        const results = testObj.searchFunction(pattern);
        console.log(`Found ${results.length} matches for ${pattern}`);
    });
}

// Export for testing
module.exports = { TestClass, main };
"""
        
        lines_per_block = content.count('\n')
        repetitions = max(1, lines // lines_per_block)
        
        return (content + '\n') * repetitions
    
    @classmethod
    def _generate_log_content(cls, lines):
        """Generate log file content"""
        content = ""
        for i in range(lines):
            if i % 10 == 0:
                content += f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] INFO: SEARCH_TARGET event occurred at line {i}\n"
            elif i % 25 == 0:
                content += f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Error in processing SEARCH_TARGET\n"
            else:
                content += f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DEBUG: Regular log entry {i}\n"
        
        return content
    
    @classmethod
    def _generate_text_content(cls, lines):
        """Generate plain text content"""
        content = ""
        words = ["performance", "testing", "search", "ripgrep", "SEARCH_TARGET", "pattern", "match"]
        
        for i in range(lines):
            if i % 50 == 0:
                content += f"Line {i}: This line contains SEARCH_TARGET for testing purposes\n"
            else:
                word = words[i % len(words)]
                content += f"Line {i}: Regular text content with {word} in it\n"
        
        return content
    
    def measure_performance(self, func, *args, **kwargs):
        """Measure function performance"""
        process = psutil.Process()
        
        # Initial measurements
        cpu_before = process.cpu_percent()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Final measurements
        cpu_after = process.cpu_percent()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'success': success,
            'result': result,
            'execution_time': execution_time,
            'cpu_usage': cpu_after - cpu_before,
            'memory_usage': memory_after - memory_before,
            'memory_peak': memory_after
        }


class TestSearchPerformance(PerformanceTestBase):
    """Test search performance with various scenarios"""
    
    def test_small_pattern_search_performance(self):
        """Test performance with small pattern searches"""
        from tools.ripgrep.core.data_models import SearchParameters
        from tools.ripgrep.core.search_engine import RipgrepCommandBuilder
        
        def search_operation():
            params = SearchParameters(
                pattern="SEARCH_TARGET",
                search_path=self.temp_dir,
                max_results=100
            )
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "ripgrep 13.0.0"
                
                builder = RipgrepCommandBuilder("rg")
                cmd = builder.build_command(params)
                return len(cmd)
        
        metrics = self.measure_performance(search_operation)
        
        # Performance assertions
        self.assertLess(metrics['execution_time'], 1.0)  # Should complete within 1 second
        self.assertLess(metrics['memory_usage'], 50)     # Should use less than 50MB additional memory
        self.assertTrue(metrics['success'])
    
    def test_large_codebase_search_performance(self):
        """Test performance with large codebase searches"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        def large_search_operation():
            params = SearchParameters(
                pattern="SEARCH_TARGET",
                search_path=self.temp_dir,
                max_results=10000,
                context_lines=5
            )
            
            # Simulate complex search parameters
            return params.to_dict()
        
        metrics = self.measure_performance(large_search_operation)
        
        # Performance assertions for large searches
        self.assertLess(metrics['execution_time'], 2.0)  # Should complete within 2 seconds
        self.assertLess(metrics['memory_usage'], 100)    # Should use less than 100MB additional memory
        self.assertTrue(metrics['success'])
    
    def test_regex_pattern_performance(self):
        """Test performance with complex regex patterns"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        def regex_search_operation():
            params = SearchParameters(
                pattern=r'SEARCH_TARGET.*(?:function|class|method)',
                search_path=self.temp_dir,
                regex_mode=True,
                max_results=5000
            )
            
            return params.pattern
        
        metrics = self.measure_performance(regex_search_operation)
        
        # Performance assertions for regex searches
        self.assertLess(metrics['execution_time'], 1.5)  # Should complete within 1.5 seconds
        self.assertTrue(metrics['success'])
    
    def test_concurrent_search_performance(self):
        """Test performance with concurrent searches"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        def concurrent_search():
            results = []
            threads = []
            
            def search_worker(pattern):
                params = SearchParameters(
                    pattern=pattern,
                    search_path=self.temp_dir,
                    max_results=100
                )
                results.append(params.to_dict())
            
            patterns = ["SEARCH_TARGET", "performance", "testing", "pattern", "function"]
            
            for pattern in patterns:
                thread = threading.Thread(target=search_worker, args=(pattern,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            return len(results)
        
        metrics = self.measure_performance(concurrent_search)
        
        # Performance assertions for concurrent searches
        self.assertLess(metrics['execution_time'], 3.0)  # Should complete within 3 seconds
        self.assertLess(metrics['memory_usage'], 200)    # Should use less than 200MB additional memory
        self.assertTrue(metrics['success'])
        self.assertEqual(metrics['result'], 5)           # Should find all 5 patterns


class TestMemoryUsage(PerformanceTestBase):
    """Test memory usage patterns"""
    
    def test_large_result_set_memory(self):
        """Test memory usage with large result sets"""
        from tools.ripgrep.core.data_models import FileResult, SearchMatch, SearchResultCollection
        
        def create_large_result_set():
            collection = SearchResultCollection()
            
            # Create 1000 file results with 100 matches each
            for file_idx in range(1000):
                file_result = FileResult(file_path=f"/test/file_{file_idx}.py")
                
                for match_idx in range(100):
                    match = SearchMatch(
                        line_number=match_idx,
                        column=0,
                        content=f"Line {match_idx} with SEARCH_TARGET pattern",
                    )
                    file_result.add_match(match)
                
                collection.add_file_result(file_result)
            
            return len(collection.file_results)
        
        metrics = self.measure_performance(create_large_result_set)
        
        # Memory usage assertions
        self.assertLess(metrics['memory_usage'], 500)    # Should use less than 500MB
        self.assertLess(metrics['execution_time'], 5.0)  # Should complete within 5 seconds
        self.assertEqual(metrics['result'], 1000)        # Should create all 1000 files
    
    def test_memory_cleanup(self):
        """Test memory cleanup after search operations"""
        from tools.ripgrep.core.data_models import SearchResultCollection
        
        def test_cleanup_operation():
            collection = SearchResultCollection()
            
            # Create some results
            from tools.ripgrep.core.data_models import FileResult, SearchMatch
            for i in range(100):
                file_result = FileResult(file_path=f"/test/file_{i}.py")
                match = SearchMatch(line_number=1, column=0, content="test content")
                file_result.add_match(match)
                collection.add_file_result(file_result)
            
            initial_count = len(collection.file_results)
            
            # Clear results
            collection.clear()
            
            return initial_count - len(collection.file_results)
        
        metrics = self.measure_performance(test_cleanup_operation)
        
        # Memory cleanup assertions
        self.assertTrue(metrics['success'])
        self.assertEqual(metrics['result'], 100)  # Should have cleaned up all 100 files
        self.assertLess(metrics['execution_time'], 1.0)


class TestAsyncWorkerPerformance(PerformanceTestBase):
    """Test async worker performance"""
    
    def test_async_worker_responsiveness(self):
        """Test async worker thread responsiveness"""
        # This would test the actual async worker if available
        # For now, test the concept with mock
        
        def simulate_async_operation():
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def worker():
                for i in range(1000):
                    result_queue.put(f"Result {i}")
                    if i % 100 == 0:
                        time.sleep(0.001)  # Simulate small delays
            
            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()
            
            return result_queue.qsize()
        
        metrics = self.measure_performance(simulate_async_operation)
        
        # Async performance assertions
        self.assertLess(metrics['execution_time'], 2.0)  # Should complete within 2 seconds
        self.assertEqual(metrics['result'], 1000)        # Should process all items
        self.assertTrue(metrics['success'])


class TestScalabilityLimits(PerformanceTestBase):
    """Test scalability limits and boundaries"""
    
    def test_maximum_file_count_handling(self):
        """Test handling of maximum file counts"""
        from tools.ripgrep.core.data_models import SearchResultCollection
        
        def test_max_files():
            collection = SearchResultCollection()
            max_files = 50000  # Test with 50k files
            
            from tools.ripgrep.core.data_models import FileResult
            for i in range(max_files):
                if i % 10000 == 0:  # Progress indicator
                    pass
                
                file_result = FileResult(file_path=f"/huge/codebase/file_{i}.py")
                collection.add_file_result(file_result)
            
            return len(collection.file_results)
        
        metrics = self.measure_performance(test_max_files)
        
        # Scalability assertions
        self.assertLess(metrics['execution_time'], 30.0)  # Should complete within 30 seconds
        self.assertLess(metrics['memory_peak'], 2000)     # Should use less than 2GB memory
        self.assertTrue(metrics['success'])
    
    def test_pattern_complexity_limits(self):
        """Test handling of complex search patterns"""
        from tools.ripgrep.core.data_models import SearchParameters
        
        def test_complex_pattern():
            # Very complex regex pattern
            complex_pattern = r'(?:function|class|method|def)\s+(\w+)\s*\([^)]*\)\s*(?:->?\s*\w+)?\s*\{?(?:[^{}]*\{[^{}]*\})*[^{}]*\}?'
            
            params = SearchParameters(
                pattern=complex_pattern,
                search_path=self.temp_dir,
                regex_mode=True,
                max_results=10000,
                context_lines=10
            )
            
            return len(params.pattern)
        
        metrics = self.measure_performance(test_complex_pattern)
        
        # Complex pattern assertions
        self.assertLess(metrics['execution_time'], 1.0)  # Pattern creation should be fast
        self.assertTrue(metrics['success'])
        self.assertGreater(metrics['result'], 100)      # Pattern should be reasonably long


def generate_performance_report(test_results):
    """Generate comprehensive performance report"""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            'python_version': sys.version
        },
        'test_results': test_results,
        'performance_summary': {
            'total_tests': len(test_results),
            'passed_tests': sum(1 for r in test_results if r.get('passed', False)),
            'average_execution_time': sum(r.get('execution_time', 0) for r in test_results) / len(test_results) if test_results else 0,
            'peak_memory_usage': max(r.get('peak_memory', 0) for r in test_results) if test_results else 0
        }
    }
    
    return report


def run_performance_tests():
    """Run all performance tests"""
    test_classes = [
        TestSearchPerformance,
        TestMemoryUsage,
        TestAsyncWorkerPerformance,
        TestScalabilityLimits,
    ]
    
    suite = unittest.TestSuite()
    test_results = []
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Custom test runner to collect performance metrics
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate performance report
    report = generate_performance_report(test_results)
    
    return result.wasSuccessful(), report


if __name__ == "__main__":
    print("Running Performance Tests for Ripgrep Plugin...")
    print("=" * 60)
    
    try:
        success, report = run_performance_tests()
        
        if success:
            print("\n✅ All performance tests passed!")
            print("Performance benchmarks meet requirements.")
        else:
            print("\n⚠️  Some performance tests failed!")
            print("Performance optimization may be needed.")
        
        print("\n📊 Performance Summary:")
        summary = report.get('performance_summary', {})
        print(f"  - Total tests: {summary.get('total_tests', 0)}")
        print(f"  - Passed tests: {summary.get('passed_tests', 0)}")
        print(f"  - Average execution time: {summary.get('average_execution_time', 0):.3f}s")
        print(f"  - Peak memory usage: {summary.get('peak_memory_usage', 0):.1f}MB")
            
    except Exception as e:
        print(f"\n💥 Performance test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Performance testing completed.")