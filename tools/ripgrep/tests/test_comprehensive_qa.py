#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for Ripgrep Plugin
Orchestrates all test categories and generates detailed reports
"""
import sys
import os
import unittest
import time
import json
import platform
from pathlib import Path
from typing import Dict, List, Any
import subprocess

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import all test modules
try:
    from test_functional_comprehensive import run_functional_tests
    functional_available = True
except ImportError as e:
    print(f"⚠️  Functional tests not available: {e}")
    functional_available = False

try:
    from test_performance import run_performance_tests
    performance_available = True
except ImportError as e:
    print(f"⚠️  Performance tests not available: {e}")
    performance_available = False

try:
    from test_integration_comprehensive import run_integration_tests
    integration_available = True
except ImportError as e:
    print(f"⚠️  Integration tests not available: {e}")
    integration_available = False

try:
    from test_usability import run_usability_tests
    usability_available = True
except ImportError as e:
    print(f"⚠️  Usability tests not available: {e}")
    usability_available = False

try:
    from test_cross_platform import run_cross_platform_tests
    cross_platform_available = True
except ImportError as e:
    print(f"⚠️  Cross-platform tests not available: {e}")
    cross_platform_available = False

try:
    from test_core_modules import run_tests as run_core_tests
    core_available = True
except ImportError as e:
    print(f"⚠️  Core module tests not available: {e}")
    core_available = False

try:
    from test_mvc_components import run_tests as run_mvc_tests
    mvc_available = True
except ImportError as e:
    print(f"⚠️  MVC component tests not available: {e}")
    mvc_available = False


class QATestOrchestrator:
    """Orchestrates comprehensive QA testing"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.system_info = self._collect_system_info()
        
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for reporting"""
        try:
            import psutil
            memory_info = psutil.virtual_memory()
            cpu_info = {
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
        except ImportError:
            memory_info = None
            cpu_info = None
        
        # Check ripgrep availability
        ripgrep_info = self._check_ripgrep_availability()
        
        # Check PyQt5 availability
        try:
            from PyQt5.QtWidgets import QApplication
            qt_available = True
            qt_version = None
            try:
                from PyQt5.QtCore import QT_VERSION_STR
                qt_version = QT_VERSION_STR
            except ImportError:
                pass
        except ImportError:
            qt_available = False
            qt_version = None
        
        return {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'executable': sys.executable,
            },
            'memory': {
                'total': memory_info.total if memory_info else None,
                'available': memory_info.available if memory_info else None,
                'percent': memory_info.percent if memory_info else None,
            } if memory_info else None,
            'cpu': cpu_info,
            'ripgrep': ripgrep_info,
            'qt': {
                'available': qt_available,
                'version': qt_version,
            },
            'test_environment': {
                'working_directory': os.getcwd(),
                'python_path': sys.path[:5],  # First 5 entries
            }
        }
    
    def _check_ripgrep_availability(self) -> Dict[str, Any]:
        """Check ripgrep availability and version"""
        try:
            result = subprocess.run(
                ['rg', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.strip().split('\n')[0]
                return {
                    'available': True,
                    'version': version_line,
                    'path': subprocess.run(['which', 'rg'], capture_output=True, text=True).stdout.strip() if platform.system() != 'Windows' else 'rg'
                }
            else:
                return {
                    'available': False,
                    'error': f'Non-zero exit code: {result.returncode}',
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'available': False,
                'error': 'Command timeout'
            }
        except FileNotFoundError:
            return {
                'available': False,
                'error': 'ripgrep executable not found'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def run_test_category(self, category_name: str, test_function, *args, **kwargs) -> Dict[str, Any]:
        """Run a test category and collect results"""
        print(f"\n{'='*20} {category_name.upper()} TESTS {'='*20}")
        
        start_time = time.time()
        
        try:
            if args or kwargs:
                result = test_function(*args, **kwargs)
            else:
                result = test_function()
            
            # Handle different return types
            if isinstance(result, tuple):
                success = result[0]
                additional_info = result[1] if len(result) > 1 else None
            else:
                success = result
                additional_info = None
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            test_result = {
                'category': category_name,
                'success': success,
                'execution_time': execution_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'additional_info': additional_info
            }
            
            if success:
                print(f"✅ {category_name} tests PASSED ({execution_time:.2f}s)")
            else:
                print(f"❌ {category_name} tests FAILED ({execution_time:.2f}s)")
                
            return test_result
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"💥 {category_name} tests CRASHED ({execution_time:.2f}s)")
            print(f"   Error: {str(e)}")
            
            return {
                'category': category_name,
                'success': False,
                'execution_time': execution_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e),
                'exception_type': type(e).__name__
            }
    
    def run_comprehensive_qa(self) -> Dict[str, Any]:
        """Run comprehensive QA test suite"""
        print("🧪 COMPREHENSIVE QA TESTING FOR RIPGREP PLUGIN")
        print("=" * 70)
        
        self.start_time = time.time()
        
        # Test execution plan
        test_plan = []
        
        # Core module tests (if available)
        if core_available:
            test_plan.append(('Core Modules', run_core_tests))
        
        # MVC component tests (if available)
        if mvc_available:
            test_plan.append(('MVC Components', run_mvc_tests))
        
        # Functional tests
        if functional_available:
            test_plan.append(('Functional', run_functional_tests))
        
        # Performance tests
        if performance_available:
            test_plan.append(('Performance', run_performance_tests))
        
        # Integration tests
        if integration_available:
            test_plan.append(('Integration', run_integration_tests))
        
        # Usability tests
        if usability_available:
            test_plan.append(('Usability', run_usability_tests))
        
        # Cross-platform tests
        if cross_platform_available:
            test_plan.append(('Cross-Platform', run_cross_platform_tests))
        
        # Execute test plan
        for test_name, test_function in test_plan:
            result = self.run_test_category(test_name, test_function)
            self.test_results[test_name.lower().replace(' ', '_').replace('-', '_')] = result
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive QA report"""
        total_time = self.end_time - self.start_time
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate risk assessment
        risk_level = self._assess_risk_level()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        report = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_execution_time': total_time,
                'test_environment': 'automated_qa_suite',
                'version': '1.0.0'
            },
            'system_info': self.system_info,
            'test_summary': {
                'total_test_categories': total_tests,
                'successful_categories': successful_tests,
                'failed_categories': total_tests - successful_tests,
                'success_rate': success_rate,
                'overall_status': 'PASS' if success_rate >= 90 else 'FAIL' if success_rate >= 70 else 'CRITICAL'
            },
            'detailed_results': self.test_results,
            'risk_assessment': risk_level,
            'recommendations': recommendations,
            'qa_metrics': self._calculate_qa_metrics(),
            'deployment_readiness': self._assess_deployment_readiness()
        }
        
        return report
    
    def _assess_risk_level(self) -> Dict[str, Any]:
        """Assess overall risk level based on test results"""
        failed_categories = [name for name, result in self.test_results.items() if not result['success']]
        
        # Risk scoring
        critical_categories = ['functional', 'core_modules', 'integration']
        high_risk_categories = ['performance', 'usability']
        medium_risk_categories = ['cross_platform', 'mvc_components']
        
        critical_failures = [cat for cat in failed_categories if cat in critical_categories]
        high_risk_failures = [cat for cat in failed_categories if cat in high_risk_categories]
        medium_risk_failures = [cat for cat in failed_categories if cat in medium_risk_categories]
        
        if critical_failures:
            risk_level = 'CRITICAL'
            risk_score = 90 + len(critical_failures) * 10
        elif len(high_risk_failures) >= 2:
            risk_level = 'HIGH'
            risk_score = 70 + len(high_risk_failures) * 5
        elif high_risk_failures or len(medium_risk_failures) >= 2:
            risk_level = 'MEDIUM'
            risk_score = 40 + len(high_risk_failures) * 10 + len(medium_risk_failures) * 5
        else:
            risk_level = 'LOW'
            risk_score = max(0, 20 + len(medium_risk_failures) * 10)
        
        return {
            'level': risk_level,
            'score': min(risk_score, 100),
            'critical_failures': critical_failures,
            'high_risk_failures': high_risk_failures,
            'medium_risk_failures': medium_risk_failures,
            'description': self._get_risk_description(risk_level)
        }
    
    def _get_risk_description(self, risk_level: str) -> str:
        """Get risk level description"""
        descriptions = {
            'CRITICAL': 'Critical functionality failures detected. Deployment not recommended.',
            'HIGH': 'Significant issues found. Requires immediate attention before deployment.',
            'MEDIUM': 'Some issues detected. Review and fix recommended.',
            'LOW': 'Minor issues or acceptable risk level for deployment.'
        }
        return descriptions.get(risk_level, 'Unknown risk level')
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for category, result in self.test_results.items():
            if not result['success']:
                category_display = category.replace('_', ' ').title()
                
                if category in ['functional', 'core_modules']:
                    recommendations.append({
                        'priority': 'CRITICAL',
                        'category': category_display,
                        'issue': f'{category_display} tests failed',
                        'recommendation': 'Fix core functionality issues before any deployment',
                        'estimated_effort': 'High'
                    })
                elif category in ['performance', 'usability']:
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': category_display,
                        'issue': f'{category_display} tests failed',
                        'recommendation': 'Address performance and usability issues for better user experience',
                        'estimated_effort': 'Medium'
                    })
                else:
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': category_display,
                        'issue': f'{category_display} tests failed',
                        'recommendation': 'Review and fix issues when possible',
                        'estimated_effort': 'Low to Medium'
                    })
        
        # Add general recommendations
        if not self.system_info['ripgrep']['available']:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Environment',
                'issue': 'Ripgrep executable not available',
                'recommendation': 'Install ripgrep for the plugin to function',
                'estimated_effort': 'Low'
            })
        
        if not self.system_info['qt']['available']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Environment',
                'issue': 'PyQt5 not available',
                'recommendation': 'Install PyQt5 for GUI functionality',
                'estimated_effort': 'Low'
            })
        
        return recommendations
    
    def _calculate_qa_metrics(self) -> Dict[str, Any]:
        """Calculate QA metrics"""
        execution_times = [result['execution_time'] for result in self.test_results.values()]
        
        return {
            'total_execution_time': sum(execution_times),
            'average_test_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'fastest_test': min(execution_times) if execution_times else 0,
            'slowest_test': max(execution_times) if execution_times else 0,
            'test_efficiency_score': self._calculate_efficiency_score(),
            'coverage_score': self._calculate_coverage_score()
        }
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate test efficiency score"""
        if not self.test_results:
            return 0.0
        
        # Base score from success rate
        success_rate = sum(1 for r in self.test_results.values() if r['success']) / len(self.test_results)
        base_score = success_rate * 70  # Max 70 points for success rate
        
        # Bonus for having all test categories
        all_categories = ['core_modules', 'mvc_components', 'functional', 'performance', 'integration', 'usability', 'cross_platform']
        available_categories = len([cat for cat in all_categories if cat in self.test_results])
        coverage_bonus = (available_categories / len(all_categories)) * 30  # Max 30 points for coverage
        
        return min(base_score + coverage_bonus, 100.0)
    
    def _calculate_coverage_score(self) -> float:
        """Calculate test coverage score"""
        # Define comprehensive test areas
        test_areas = {
            'core_functionality': ['core_modules', 'functional'],
            'user_interface': ['mvc_components', 'usability'],
            'system_integration': ['integration', 'cross_platform'],
            'performance': ['performance']
        }
        
        covered_areas = 0
        for area, required_tests in test_areas.items():
            if any(test in self.test_results and self.test_results[test]['success'] for test in required_tests):
                covered_areas += 1
        
        return (covered_areas / len(test_areas)) * 100
    
    def _assess_deployment_readiness(self) -> Dict[str, Any]:
        """Assess deployment readiness"""
        success_rate = sum(1 for r in self.test_results.values() if r['success']) / len(self.test_results) if self.test_results else 0
        risk_assessment = self._assess_risk_level()
        
        # Deployment decision matrix
        if success_rate >= 0.95 and risk_assessment['level'] in ['LOW']:
            readiness = 'READY'
            confidence = 'HIGH'
        elif success_rate >= 0.85 and risk_assessment['level'] in ['LOW', 'MEDIUM']:
            readiness = 'CONDITIONAL'
            confidence = 'MEDIUM'
        elif success_rate >= 0.70:
            readiness = 'NOT_READY'
            confidence = 'LOW'
        else:
            readiness = 'BLOCKED'
            confidence = 'VERY_LOW'
        
        return {
            'status': readiness,
            'confidence': confidence,
            'success_rate': success_rate * 100,
            'blocking_issues': [cat for cat, result in self.test_results.items() 
                              if not result['success'] and cat in ['core_modules', 'functional']],
            'recommendation': self._get_deployment_recommendation(readiness)
        }
    
    def _get_deployment_recommendation(self, readiness: str) -> str:
        """Get deployment recommendation"""
        recommendations = {
            'READY': 'Plugin is ready for deployment to production.',
            'CONDITIONAL': 'Plugin can be deployed with monitoring. Address remaining issues in next iteration.',
            'NOT_READY': 'Plugin needs significant fixes before deployment. Consider staging deployment for further testing.',
            'BLOCKED': 'Plugin has critical issues. Deployment is not recommended until core issues are resolved.'
        }
        return recommendations.get(readiness, 'Unknown deployment status')
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive report to file"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'ripgrep_qa_report_{timestamp}.json'
        
        report_path = Path(os.path.dirname(__file__)) / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return str(report_path)
    
    def print_summary(self, report: Dict[str, Any]):
        """Print executive summary"""
        print("\n" + "=" * 70)
        print("🏆 COMPREHENSIVE QA RESULTS SUMMARY")
        print("=" * 70)
        
        # Test Summary
        summary = report['test_summary']
        print(f"📊 Test Summary:")
        print(f"   - Total Categories: {summary['total_test_categories']}")
        print(f"   - Successful: {summary['successful_categories']}")
        print(f"   - Failed: {summary['failed_categories']}")
        print(f"   - Success Rate: {summary['success_rate']:.1f}%")
        print(f"   - Overall Status: {summary['overall_status']}")
        
        # System Info
        system = report['system_info']
        print(f"\n🖥️  Environment:")
        print(f"   - Platform: {system['platform']['system']} {system['platform']['release']}")
        print(f"   - Python: {system['python']['version']}")
        print(f"   - Ripgrep: {'✅' if system['ripgrep']['available'] else '❌'}")
        print(f"   - PyQt5: {'✅' if system['qt']['available'] else '❌'}")
        
        # Risk Assessment
        risk = report['risk_assessment']
        print(f"\n⚠️  Risk Assessment:")
        print(f"   - Level: {risk['level']}")
        print(f"   - Score: {risk['score']}/100")
        print(f"   - Description: {risk['description']}")
        
        # Deployment Readiness
        deployment = report['deployment_readiness']
        print(f"\n🚀 Deployment Readiness:")
        print(f"   - Status: {deployment['status']}")
        print(f"   - Confidence: {deployment['confidence']}")
        print(f"   - Recommendation: {deployment['recommendation']}")
        
        # Top Recommendations
        recommendations = report['recommendations'][:3]  # Top 3
        if recommendations:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['recommendation']}")
        
        print("\n" + "=" * 70)
        print(f"⏱️  Total Execution Time: {report['metadata']['total_execution_time']:.2f} seconds")
        print("=" * 70)


def main():
    """Main QA execution function"""
    orchestrator = QATestOrchestrator()
    
    print("🔧 Initializing Comprehensive QA Suite...")
    print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    
    # Run comprehensive QA
    report = orchestrator.run_comprehensive_qa()
    
    # Print summary
    orchestrator.print_summary(report)
    
    # Save detailed report
    try:
        report_path = orchestrator.save_report(report)
        print(f"\n💾 Detailed report saved: {report_path}")
    except Exception as e:
        print(f"\n⚠️  Failed to save report: {e}")
    
    # Exit with appropriate code
    overall_success = report['test_summary']['success_rate'] >= 70
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()