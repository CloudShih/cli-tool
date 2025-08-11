"""
Test runner script for dust tool comprehensive testing
Executes all dust-related tests and generates a comprehensive test report
"""

import unittest
import sys
import os
import time
import json
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import traceback

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

# Test modules
TEST_MODULES = [
    'test_dust_model',
    'test_dust_view', 
    'test_dust_controller',
    'test_dust_plugin',
    'test_dust_e2e'
]


class DustTestResult(unittest.TestResult):
    """Custom test result class to collect detailed test information"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
        
    def stopTest(self, test):
        super().stopTest(test)
        self.end_time = time.time()
        
        # Calculate test duration
        duration = self.end_time - self.start_time if self.start_time else 0
        
        # Determine test status
        status = 'PASS'
        error_info = None
        
        if hasattr(test, '_outcome'):
            if test._outcome.errors:
                status = 'ERROR'
                error_info = test._outcome.errors[-1][1] if test._outcome.errors else None
            elif test._outcome.failures:
                status = 'FAIL'
                error_info = test._outcome.failures[-1][1] if test._outcome.failures else None
            elif test._outcome.skipped:
                status = 'SKIP'
                error_info = test._outcome.skipped[-1][1] if test._outcome.skipped else None
        
        # Record test result
        self.test_results.append({
            'test_name': f"{test.__class__.__name__}.{test._testMethodName}",
            'module': test.__class__.__module__,
            'status': status,
            'duration': duration,
            'error_info': error_info
        })


class DustTestRunner:
    """Main test runner for dust tool tests"""
    
    def __init__(self):
        self.results = {
            'summary': {},
            'modules': {},
            'failed_tests': [],
            'error_tests': [],
            'skipped_tests': [],
            'execution_time': 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def run_all_tests(self):
        """Run all dust tool tests and collect results"""
        print("🧪 Starting comprehensive dust tool test suite")
        print("=" * 60)
        
        start_time = time.time()
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0
        
        # Run tests for each module
        for module_name in TEST_MODULES:
            print(f"\n📋 Running tests for {module_name}")
            print("-" * 40)
            
            try:
                # Import test module
                test_module = __import__(module_name)
                
                # Create test suite
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_module)
                
                # Run tests with custom result collector
                test_result = DustTestResult()
                runner = unittest.TextTestRunner(
                    stream=StringIO(),
                    resultclass=lambda: test_result
                )
                
                # Capture output
                output_stream = StringIO()
                error_stream = StringIO()
                
                with redirect_stdout(output_stream), redirect_stderr(error_stream):
                    runner.run(suite)
                
                # Collect module statistics
                module_tests = len(test_result.test_results)
                module_passed = len([r for r in test_result.test_results if r['status'] == 'PASS'])
                module_failed = len([r for r in test_result.test_results if r['status'] == 'FAIL'])
                module_errors = len([r for r in test_result.test_results if r['status'] == 'ERROR'])
                module_skipped = len([r for r in test_result.test_results if r['status'] == 'SKIP'])
                
                # Update totals
                total_tests += module_tests
                total_passed += module_passed
                total_failed += module_failed
                total_errors += module_errors
                total_skipped += module_skipped
                
                # Store module results
                self.results['modules'][module_name] = {
                    'total': module_tests,
                    'passed': module_passed,
                    'failed': module_failed,
                    'errors': module_errors,
                    'skipped': module_skipped,
                    'test_results': test_result.test_results
                }
                
                # Print module summary
                print(f"✅ Tests: {module_tests}, Passed: {module_passed}, Failed: {module_failed}, Errors: {module_errors}")
                
                # Collect failed and error tests
                for result in test_result.test_results:
                    if result['status'] == 'FAIL':
                        self.results['failed_tests'].append(result)
                    elif result['status'] == 'ERROR':
                        self.results['error_tests'].append(result)
                    elif result['status'] == 'SKIP':
                        self.results['skipped_tests'].append(result)
                
            except Exception as e:
                print(f"❌ Error running tests for {module_name}: {e}")
                self.results['modules'][module_name] = {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
        
        # Calculate execution time
        end_time = time.time()
        self.results['execution_time'] = end_time - start_time
        
        # Store summary
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'errors': total_errors,
            'skipped': total_skipped,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
        }
        
        return self.results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🎯 DUST TOOL TEST REPORT")
        print("=" * 60)
        
        summary = self.results['summary']
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   💥 Errors: {summary['errors']}")
        print(f"   ⏭️  Skipped: {summary['skipped']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   ⏱️  Execution Time: {self.results['execution_time']:.2f}s")
        
        # Module breakdown
        print(f"\n📋 Module Breakdown:")
        for module_name, module_result in self.results['modules'].items():
            if 'error' in module_result:
                print(f"   {module_name}: ❌ ERROR - {module_result['error']}")
            else:
                total = module_result['total']
                passed = module_result['passed']
                rate = (passed / total * 100) if total > 0 else 0
                print(f"   {module_name}: {passed}/{total} tests passed ({rate:.1f}%)")
        
        # Failed tests details
        if self.results['failed_tests']:
            print(f"\n❌ Failed Tests ({len(self.results['failed_tests'])}):")
            for test in self.results['failed_tests']:
                print(f"   - {test['test_name']}")
                if test['error_info']:
                    # Show first line of error
                    error_line = test['error_info'].split('\n')[0] if test['error_info'] else 'No details'
                    print(f"     💡 {error_line}")
        
        # Error tests details
        if self.results['error_tests']:
            print(f"\n💥 Error Tests ({len(self.results['error_tests'])}):")
            for test in self.results['error_tests']:
                print(f"   - {test['test_name']}")
                if test['error_info']:
                    error_line = test['error_info'].split('\n')[0] if test['error_info'] else 'No details'
                    print(f"     💡 {error_line}")
        
        # Skipped tests
        if self.results['skipped_tests']:
            print(f"\n⏭️ Skipped Tests ({len(self.results['skipped_tests'])}):")
            for test in self.results['skipped_tests']:
                print(f"   - {test['test_name']}")
        
        # Performance insights
        print(f"\n⚡ Performance Insights:")
        all_tests = []
        for module_result in self.results['modules'].values():
            if 'test_results' in module_result:
                all_tests.extend(module_result['test_results'])
        
        if all_tests:
            total_duration = sum(t.get('duration', 0) for t in all_tests)
            avg_duration = total_duration / len(all_tests)
            slowest_tests = sorted(all_tests, key=lambda x: x.get('duration', 0), reverse=True)[:5]
            
            print(f"   Average test duration: {avg_duration:.3f}s")
            print(f"   Total test time: {total_duration:.2f}s")
            print(f"   Slowest tests:")
            for test in slowest_tests:
                duration = test.get('duration', 0)
                print(f"     - {test['test_name']}: {duration:.3f}s")
        
        print(f"\n📅 Report generated: {self.results['timestamp']}")
        
        return self.results
    
    def save_json_report(self, filename='dust_test_report.json'):
        """Save detailed test results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed report saved to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving JSON report: {e}")
            return False
    
    def check_coverage_requirements(self):
        """Check if tests meet coverage requirements"""
        print(f"\n🔍 Coverage Analysis:")
        
        # Define expected test coverage
        expected_coverage = {
            'test_dust_model': {
                'methods': ['__init__', 'execute_dust_command', '_build_dust_command', 
                           'parse_dust_output', 'validate_path', 'get_default_settings', 
                           'check_dust_availability', 'get_cache_info'],
                'min_tests': 15
            },
            'test_dust_view': {
                'methods': ['__init__', 'setup_ui', 'load_default_settings',
                           'get_analysis_parameters', 'set_analyze_button_state',
                           'clear_results', 'set_analysis_completed'],
                'min_tests': 10
            },
            'test_dust_controller': {
                'methods': ['__init__', '_connect_signals', '_execute_analysis',
                           '_on_analysis_started', '_on_analysis_progress',
                           '_on_analysis_completed', 'cleanup'],
                'min_tests': 12
            },
            'test_dust_plugin': {
                'methods': ['__init__', 'initialize', 'create_model', 'create_view',
                           'create_controller', 'cleanup', 'check_tools_availability',
                           'get_widget', 'get_settings', 'apply_settings'],
                'min_tests': 15
            },
            'test_dust_e2e': {
                'scenarios': ['full_plugin_lifecycle', 'mvc_component_integration',
                             'basic_workflow_simulation', 'ui_component_rendering',
                             'configuration_persistence', 'error_scenarios_and_recovery'],
                'min_tests': 8
            }
        }
        
        coverage_issues = []
        
        for module_name, expected in expected_coverage.items():
            if module_name in self.results['modules']:
                module_result = self.results['modules'][module_name]
                if 'total' in module_result:
                    actual_tests = module_result['total']
                    min_tests = expected.get('min_tests', 5)
                    
                    if actual_tests < min_tests:
                        coverage_issues.append(
                            f"{module_name}: {actual_tests} tests (expected ≥{min_tests})"
                        )
                    else:
                        print(f"   ✅ {module_name}: {actual_tests} tests (≥{min_tests} required)")
                else:
                    coverage_issues.append(f"{module_name}: Module failed to load")
            else:
                coverage_issues.append(f"{module_name}: Module not tested")
        
        if coverage_issues:
            print(f"\n⚠️ Coverage Issues:")
            for issue in coverage_issues:
                print(f"   - {issue}")
            return False
        else:
            print(f"   ✅ All modules meet minimum test coverage requirements")
            return True


def main():
    """Main test execution function"""
    print("🚀 Dust Tool Comprehensive Test Suite")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create test runner
    runner = DustTestRunner()
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        # Generate and display report
        runner.generate_report()
        
        # Check coverage requirements
        coverage_ok = runner.check_coverage_requirements()
        
        # Save JSON report
        runner.save_json_report()
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        summary = results['summary']
        
        if summary['failed'] == 0 and summary['errors'] == 0:
            print("   ✅ ALL TESTS PASSED!")
            status = "SUCCESS"
        elif summary['errors'] > 0:
            print("   💥 TESTS COMPLETED WITH ERRORS")
            status = "ERRORS"
        else:
            print("   ❌ SOME TESTS FAILED")
            status = "FAILURES"
        
        if not coverage_ok:
            print("   ⚠️  Coverage requirements not fully met")
        
        success_rate = summary['success_rate']
        if success_rate >= 95:
            print(f"   🏆 Excellent test coverage: {success_rate:.1f}%")
        elif success_rate >= 80:
            print(f"   👍 Good test coverage: {success_rate:.1f}%")
        else:
            print(f"   📈 Test coverage needs improvement: {success_rate:.1f}%")
        
        print(f"\n🏁 Test suite completed in {results['execution_time']:.2f}s")
        
        # Return appropriate exit code
        if status == "SUCCESS" and coverage_ok:
            return 0
        elif status == "ERRORS":
            return 2
        else:
            return 1
            
    except Exception as e:
        print(f"\n💥 Fatal error running test suite: {e}")
        print(traceback.format_exc())
        return 3


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)