#!/usr/bin/env python3
"""
QA Test Suite Runner - Automated execution of comprehensive QA tests
Supports multiple execution modes: quick, full, continuous integration
"""
import sys
import os
import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class QATestRunner:
    """Automated QA test suite runner"""
    
    def __init__(self, mode: str = 'full', verbose: bool = False, output_dir: Optional[str] = None):
        self.mode = mode
        self.verbose = verbose
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Test configurations for different modes
        self.test_configs = {
            'quick': {
                'description': 'Quick validation tests (5-10 minutes)',
                'tests': ['core_modules', 'functional_basic', 'integration_basic'],
                'performance_limited': True,
                'skip_heavy_tests': True
            },
            'full': {
                'description': 'Comprehensive QA test suite (30-60 minutes)',
                'tests': ['core_modules', 'mvc_components', 'functional', 'performance', 
                         'integration', 'usability', 'cross_platform'],
                'performance_limited': False,
                'skip_heavy_tests': False
            },
            'ci': {
                'description': 'Continuous integration tests (10-15 minutes)',
                'tests': ['core_modules', 'functional', 'integration', 'performance_basic'],
                'performance_limited': True,
                'skip_heavy_tests': True,
                'fail_fast': True
            },
            'performance': {
                'description': 'Performance-focused testing (15-30 minutes)',
                'tests': ['performance', 'scalability', 'memory_profiling'],
                'performance_limited': False,
                'skip_heavy_tests': False
            },
            'regression': {
                'description': 'Regression testing (20-40 minutes)',
                'tests': ['core_modules', 'functional', 'integration'],
                'performance_limited': True,
                'skip_heavy_tests': True,
                'baseline_comparison': True
            }
        }
    
    def print_banner(self):
        """Print test runner banner"""
        config = self.test_configs[self.mode]
        print("RIPGREP PLUGIN QA TEST SUITE")
        print("=" * 50)
        print(f"Mode: {self.mode.upper()}")
        print(f"Description: {config['description']}")
        print(f"Tests: {', '.join(config['tests'])}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Verbose: {self.verbose}")
        print("=" * 50)
    
    def check_prerequisites(self) -> bool:
        """Check test prerequisites"""
        print("Checking Prerequisites...")
        
        prerequisites_ok = True
        
        # Check Python version
        if sys.version_info < (3, 7):
            print("[ERROR] Python 3.7+ required")
            prerequisites_ok = False
        else:
            print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check ripgrep availability
        try:
            result = subprocess.run(['rg', '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.decode().split('\n')[0]
                print(f"[OK] Ripgrep: {version}")
            else:
                print("[WARNING] Ripgrep available but version check failed")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("[ERROR] Ripgrep not found - some tests will fail")
            if self.mode in ['full', 'ci']:
                prerequisites_ok = False
        
        # Check PyQt5 availability
        try:
            from PyQt5.QtWidgets import QApplication
            print("[OK] PyQt5 available")
        except ImportError:
            print("[WARNING] PyQt5 not available - GUI tests will be skipped")
            if self.mode == 'full':
                print("   Note: Full mode recommended with PyQt5 for complete coverage")
        
        # Check required Python packages
        required_packages = ['psutil']
        for package in required_packages:
            try:
                __import__(package)
                print(f"[OK] {package}")
            except ImportError:
                print(f"[WARNING] {package} not available - some performance tests may be limited")
        
        # Check output directory
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            test_file = self.output_dir / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            print(f"[OK] Output directory writable: {self.output_dir}")
        except Exception as e:
            print(f"[ERROR] Output directory not writable: {e}")
            prerequisites_ok = False
        
        return prerequisites_ok
    
    def run_test_module(self, test_name: str) -> Dict[str, Any]:
        """Run individual test module"""
        if self.verbose:
            print(f"\n🔄 Running {test_name}...")
        
        start_time = time.time()
        
        try:
            # Map test names to actual modules/functions
            test_mapping = {
                'core_modules': self._run_core_modules,
                'mvc_components': self._run_mvc_components,
                'functional': self._run_functional,
                'functional_basic': self._run_functional_basic,
                'performance': self._run_performance,
                'performance_basic': self._run_performance_basic,
                'integration': self._run_integration,
                'integration_basic': self._run_integration_basic,
                'usability': self._run_usability,
                'cross_platform': self._run_cross_platform,
                'scalability': self._run_scalability,
                'memory_profiling': self._run_memory_profiling
            }
            
            test_function = test_mapping.get(test_name)
            if not test_function:
                raise ValueError(f"Unknown test: {test_name}")
            
            result = test_function()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                'test': test_name,
                'success': result.get('success', False),
                'execution_time': execution_time,
                'details': result,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            if self.verbose:
                print(f"[ERROR] {test_name} failed: {e}")
                import traceback
                traceback.print_exc()
            
            return {
                'test': test_name,
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'exception_type': type(e).__name__,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _run_core_modules(self) -> Dict[str, Any]:
        """Run core module tests"""
        try:
            from test_core_modules import run_tests
            success = run_tests()
            return {'success': success, 'type': 'core_modules'}
        except ImportError:
            # Run via subprocess if direct import fails
            return self._run_subprocess_test('test_core_modules.py')
    
    def _run_mvc_components(self) -> Dict[str, Any]:
        """Run MVC component tests"""
        try:
            from test_mvc_components import run_tests
            success = run_tests()
            return {'success': success, 'type': 'mvc_components'}
        except ImportError:
            return self._run_subprocess_test('test_mvc_components.py')
    
    def _run_functional(self) -> Dict[str, Any]:
        """Run full functional tests"""
        try:
            from test_functional_comprehensive import run_functional_tests
            success = run_functional_tests()
            return {'success': success, 'type': 'functional'}
        except ImportError:
            return self._run_subprocess_test('test_functional_comprehensive.py')
    
    def _run_functional_basic(self) -> Dict[str, Any]:
        """Run basic functional tests"""
        # For basic mode, run a subset of functional tests
        return self._run_functional()  # Can be customized for lighter testing
    
    def _run_performance(self) -> Dict[str, Any]:
        """Run performance tests"""
        try:
            from test_performance import run_performance_tests
            success, report = run_performance_tests()
            return {
                'success': success, 
                'type': 'performance',
                'performance_report': report
            }
        except ImportError:
            return self._run_subprocess_test('test_performance.py')
    
    def _run_performance_basic(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        # Run performance tests with limited scope
        return self._run_performance()
    
    def _run_integration(self) -> Dict[str, Any]:
        """Run integration tests"""
        try:
            from test_integration_comprehensive import run_integration_tests
            success = run_integration_tests()
            return {'success': success, 'type': 'integration'}
        except ImportError:
            return self._run_subprocess_test('test_integration_comprehensive.py')
    
    def _run_integration_basic(self) -> Dict[str, Any]:
        """Run basic integration tests"""
        return self._run_integration()
    
    def _run_usability(self) -> Dict[str, Any]:
        """Run usability tests"""
        try:
            from test_usability import run_usability_tests
            success = run_usability_tests()
            return {'success': success, 'type': 'usability'}
        except ImportError:
            return self._run_subprocess_test('test_usability.py')
    
    def _run_cross_platform(self) -> Dict[str, Any]:
        """Run cross-platform tests"""
        try:
            from test_cross_platform import run_cross_platform_tests
            success, report = run_cross_platform_tests()
            return {
                'success': success, 
                'type': 'cross_platform',
                'platform_report': report
            }
        except ImportError:
            return self._run_subprocess_test('test_cross_platform.py')
    
    def _run_scalability(self) -> Dict[str, Any]:
        """Run scalability tests"""
        # Placeholder for scalability-specific tests
        return self._run_performance()
    
    def _run_memory_profiling(self) -> Dict[str, Any]:
        """Run memory profiling tests"""
        # Placeholder for memory profiling tests
        return self._run_performance()
    
    def _run_subprocess_test(self, test_file: str) -> Dict[str, Any]:
        """Run test via subprocess"""
        test_path = Path(__file__).parent / test_file
        
        if not test_path.exists():
            return {
                'success': False,
                'error': f'Test file not found: {test_file}',
                'type': 'subprocess'
            }
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'type': 'subprocess',
                'returncode': result.returncode,
                'stdout': result.stdout if self.verbose else result.stdout[:1000],
                'stderr': result.stderr if self.verbose else result.stderr[:1000]
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test timeout (5 minutes)',
                'type': 'subprocess'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'type': 'subprocess'
            }
    
    def run_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("[ERROR] Prerequisites not met. Aborting test run.")
            return {
                'success': False,
                'error': 'Prerequisites not met',
                'results': {}
            }
        
        self.start_time = time.time()
        config = self.test_configs[self.mode]
        
        print(f"\nStarting {self.mode} test suite...")
        
        # Run tests
        for test_name in config['tests']:
            result = self.run_test_module(test_name)
            self.results[test_name] = result
            
            # Print progress
            status = "[PASS]" if result['success'] else "[FAIL]"
            time_str = f"({result['execution_time']:.1f}s)"
            print(f"{status} {test_name} {time_str}")
            
            # Fail fast for CI mode
            if config.get('fail_fast') and not result['success']:
                print(f"[ERROR] Failing fast due to {test_name} failure in CI mode")
                break
        
        self.end_time = time.time()
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test run summary"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        total_time = self.end_time - self.start_time
        
        # Determine overall status
        if success_rate >= 95:
            overall_status = "EXCELLENT"
        elif success_rate >= 85:
            overall_status = "GOOD"
        elif success_rate >= 70:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "POOR"
        
        summary = {
            'mode': self.mode,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_execution_time': total_time,
            'test_summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'overall_status': overall_status
            },
            'test_results': self.results,
            'failed_tests': [name for name, result in self.results.items() if not result['success']],
            'recommendations': self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        failed_tests = [name for name, result in self.results.items() if not result['success']]
        
        if 'core_modules' in failed_tests:
            recommendations.append("[CRITICAL] Fix core module issues before any deployment")
        
        if 'functional' in failed_tests or 'functional_basic' in failed_tests:
            recommendations.append("[CRITICAL] Resolve functional test failures - core features not working")
        
        if 'integration' in failed_tests:
            recommendations.append("[HIGH] Address integration issues - may affect plugin loading")
        
        if 'performance' in failed_tests:
            recommendations.append("[HIGH] Investigate performance issues - may affect user experience")
        
        if 'usability' in failed_tests:
            recommendations.append("[MEDIUM] Improve usability - affects user satisfaction")
        
        if 'cross_platform' in failed_tests:
            recommendations.append("[MEDIUM] Fix cross-platform compatibility issues")
        
        if not recommendations:
            recommendations.append("[SUCCESS] All tests passed! Plugin is ready for deployment.")
        
        return recommendations
    
    def save_results(self, summary: Dict[str, Any]) -> str:
        """Save test results to file"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f'qa_results_{self.mode}_{timestamp}.json'
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        return str(output_path)
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test run summary"""
        print(f"\n{'='*60}")
        print(f"QA TEST SUITE RESULTS - {self.mode.upper()} MODE")
        print(f"{'='*60}")
        
        test_summary = summary['test_summary']
        print(f"Summary:")
        print(f"   Total Tests: {test_summary['total_tests']}")
        print(f"   Successful: {test_summary['successful_tests']}")
        print(f"   Failed: {test_summary['failed_tests']}")
        print(f"   Success Rate: {test_summary['success_rate']:.1f}%")
        print(f"   Overall Status: {test_summary['overall_status']}")
        print(f"   Execution Time: {summary['total_execution_time']:.1f}s")
        
        if summary['failed_tests']:
            print(f"\nFailed Tests:")
            for test_name in summary['failed_tests']:
                print(f"   - {test_name}")
        
        print(f"\nRecommendations:")
        for recommendation in summary['recommendations']:
            print(f"   {recommendation}")
        
        print(f"\n{'='*60}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Ripgrep Plugin QA Test Suite Runner')
    parser.add_argument('mode', choices=['quick', 'full', 'ci', 'performance', 'regression'],
                       help='Test execution mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--output-dir', '-o', type=str,
                       help='Output directory for test results')
    parser.add_argument('--save-results', '-s', action='store_true',
                       help='Save detailed results to JSON file')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = QATestRunner(
        mode=args.mode,
        verbose=args.verbose,
        output_dir=args.output_dir
    )
    
    # Run test suite
    try:
        summary = runner.run_test_suite()
        
        # Print summary
        runner.print_summary(summary)
        
        # Save results if requested
        if args.save_results:
            output_path = runner.save_results(summary)
            print(f"\nResults saved: {output_path}")
        
        # Exit with appropriate code
        success_rate = summary['test_summary']['success_rate']
        if success_rate >= 90:
            sys.exit(0)  # Excellent/Good
        elif success_rate >= 70:
            sys.exit(1)  # Acceptable but with warnings
        else:
            sys.exit(2)  # Poor - significant issues
            
    except KeyboardInterrupt:
        print(f"\nTest run interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\nTest runner failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(4)


if __name__ == "__main__":
    main()