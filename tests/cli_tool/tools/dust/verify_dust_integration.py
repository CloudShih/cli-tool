"""
Final integration verification script for dust tool
Tests the complete dust tool workflow, verifies all components work together,
checks performance and resource usage, and validates user experience.
"""

import unittest
import sys
import os
import time
import psutil
import threading
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtTest import QTest
import tempfile
import json
import subprocess

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, project_root)

# Import components
from tools.dust.plugin import DustPlugin
from tools.dust.dust_model import DustModel
from tools.dust.dust_view import DustView
from tools.dust.dust_controller import DustController


class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.monitoring = False
        self.stats = {
            'max_memory_mb': 0,
            'max_cpu_percent': 0,
            'start_memory_mb': 0,
            'end_memory_mb': 0,
            'duration_seconds': 0
        }
        self.process = psutil.Process()
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.stats['start_memory_mb'] = self.process.memory_info().rss / 1024 / 1024
        self.start_time = time.time()
        
        def monitor_loop():
            while self.monitoring:
                try:
                    # Memory usage
                    memory_mb = self.process.memory_info().rss / 1024 / 1024
                    self.stats['max_memory_mb'] = max(self.stats['max_memory_mb'], memory_mb)
                    
                    # CPU usage
                    cpu_percent = self.process.cpu_percent()
                    self.stats['max_cpu_percent'] = max(self.stats['max_cpu_percent'], cpu_percent)
                    
                    time.sleep(0.1)
                except:
                    break
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        self.stats['end_memory_mb'] = self.process.memory_info().rss / 1024 / 1024
        self.stats['duration_seconds'] = time.time() - self.start_time
        return self.stats


class DustIntegrationVerifier:
    """Main integration verification class"""
    
    def __init__(self):
        self.app = None
        self.results = {
            'test_results': [],
            'performance_stats': {},
            'component_status': {},
            'user_experience': {},
            'overall_status': 'UNKNOWN'
        }
        
        # Initialize QApplication
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
    
    def verify_component_initialization(self):
        """Verify all components can be initialized properly"""
        print("🔧 Verifying Component Initialization...")
        
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        try:
            # Test 1: Plugin creation
            start_time = time.time()
            plugin = DustPlugin()
            creation_time = time.time() - start_time
            
            self.results['test_results'].append({
                'test': 'plugin_creation',
                'status': 'PASS',
                'duration': creation_time,
                'details': f'Plugin created in {creation_time:.3f}s'
            })
            
            # Test 2: Plugin initialization
            with patch('tools.dust.dust_model.config_manager') as mock_config:
                mock_config.get.return_value = 'dust'
                
                start_time = time.time()
                success = plugin.initialize()
                init_time = time.time() - start_time
                
                if success:
                    self.results['test_results'].append({
                        'test': 'plugin_initialization',
                        'status': 'PASS',
                        'duration': init_time,
                        'details': f'Plugin initialized in {init_time:.3f}s'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'plugin_initialization',
                        'status': 'FAIL',
                        'duration': init_time,
                        'details': 'Plugin initialization failed'
                    })
                    return False
            
            # Test 3: Component creation
            components_ok = True
            
            # Check model
            if plugin._model and isinstance(plugin._model, DustModel):
                self.results['component_status']['model'] = 'OK'
            else:
                self.results['component_status']['model'] = 'FAIL'
                components_ok = False
            
            # Check view
            if plugin._view and isinstance(plugin._view, DustView):
                self.results['component_status']['view'] = 'OK'
            else:
                self.results['component_status']['view'] = 'FAIL'
                components_ok = False
            
            # Check controller
            if plugin._controller and isinstance(plugin._controller, DustController):
                self.results['component_status']['controller'] = 'OK'
            else:
                self.results['component_status']['controller'] = 'FAIL'
                components_ok = False
            
            if components_ok:
                self.results['test_results'].append({
                    'test': 'component_creation',
                    'status': 'PASS',
                    'duration': 0,
                    'details': 'All MVC components created successfully'
                })
            else:
                self.results['test_results'].append({
                    'test': 'component_creation',
                    'status': 'FAIL',
                    'duration': 0,
                    'details': f'Component status: {self.results["component_status"]}'
                })
                return False
            
            # Test 4: Widget retrieval
            start_time = time.time()
            widget = plugin.get_widget()
            widget_time = time.time() - start_time
            
            if widget is not None:
                self.results['test_results'].append({
                    'test': 'widget_retrieval',
                    'status': 'PASS',
                    'duration': widget_time,
                    'details': f'Widget retrieved in {widget_time:.3f}s'
                })
            else:
                self.results['test_results'].append({
                    'test': 'widget_retrieval',
                    'status': 'FAIL',
                    'duration': widget_time,
                    'details': 'Failed to retrieve widget'
                })
                return False
            
            # Cleanup
            plugin.cleanup()
            if widget:
                widget.deleteLater()
            
            return True
            
        except Exception as e:
            self.results['test_results'].append({
                'test': 'component_initialization',
                'status': 'ERROR',
                'duration': 0,
                'details': f'Exception during initialization: {str(e)}'
            })
            return False
        
        finally:
            stats = performance_monitor.stop_monitoring()
            self.results['performance_stats']['initialization'] = stats
    
    def verify_ui_rendering_and_interaction(self):
        """Verify UI components render and interact correctly"""
        print("🎨 Verifying UI Rendering and Interaction...")
        
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        try:
            # Create plugin and widget
            with patch('tools.dust.dust_model.config_manager') as mock_config:
                mock_config.get.return_value = 'dust'
                
                plugin = DustPlugin()
                plugin.initialize()
                widget = plugin.get_widget()
                
                # Test UI rendering
                start_time = time.time()
                widget.show()
                QApplication.processEvents()
                render_time = time.time() - start_time
                
                if widget.isVisible():
                    self.results['test_results'].append({
                        'test': 'ui_rendering',
                        'status': 'PASS',
                        'duration': render_time,
                        'details': f'UI rendered and visible in {render_time:.3f}s'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'ui_rendering',
                        'status': 'FAIL',
                        'duration': render_time,
                        'details': 'UI not visible after rendering'
                    })
                    return False
                
                # Test component accessibility
                components_accessible = True
                ui_components = [
                    ('path_input', widget.dust_path_input),
                    ('browse_button', widget.dust_browse_button),
                    ('analyze_button', widget.dust_analyze_button),
                    ('results_display', widget.dust_results_display),
                    ('max_depth_spinbox', widget.dust_max_depth_spinbox),
                    ('lines_spinbox', widget.dust_lines_spinbox)
                ]
                
                for comp_name, component in ui_components:
                    if component is None or not hasattr(component, 'isEnabled'):
                        components_accessible = False
                        self.results['component_status'][f'ui_{comp_name}'] = 'FAIL'
                    else:
                        self.results['component_status'][f'ui_{comp_name}'] = 'OK'
                
                if components_accessible:
                    self.results['test_results'].append({
                        'test': 'component_accessibility',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'All UI components are accessible'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'component_accessibility',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': 'Some UI components not accessible'
                    })
                
                # Test basic interaction
                try:
                    # Set values
                    widget.dust_path_input.setText("/test/path")
                    widget.dust_max_depth_spinbox.setValue(5)
                    widget.dust_lines_spinbox.setValue(100)
                    
                    QApplication.processEvents()
                    
                    # Verify values were set
                    if (widget.dust_path_input.text() == "/test/path" and
                        widget.dust_max_depth_spinbox.value() == 5 and
                        widget.dust_lines_spinbox.value() == 100):
                        
                        self.results['test_results'].append({
                            'test': 'basic_interaction',
                            'status': 'PASS',
                            'duration': 0,
                            'details': 'UI components respond to input correctly'
                        })
                    else:
                        self.results['test_results'].append({
                            'test': 'basic_interaction',
                            'status': 'FAIL',
                            'duration': 0,
                            'details': 'UI components do not respond to input properly'
                        })
                        
                except Exception as e:
                    self.results['test_results'].append({
                        'test': 'basic_interaction',
                        'status': 'ERROR',
                        'duration': 0,
                        'details': f'Error during interaction test: {str(e)}'
                    })
                
                # Cleanup
                widget.hide()
                plugin.cleanup()
                widget.deleteLater()
                
                return True
                
        except Exception as e:
            self.results['test_results'].append({
                'test': 'ui_verification',
                'status': 'ERROR',
                'duration': 0,
                'details': f'Exception during UI verification: {str(e)}'
            })
            return False
        
        finally:
            stats = performance_monitor.stop_monitoring()
            self.results['performance_stats']['ui_rendering'] = stats
    
    def verify_workflow_execution(self):
        """Verify complete workflow execution with mocked dust command"""
        print("⚙️ Verifying Workflow Execution...")
        
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        try:
            with patch('tools.dust.dust_model.config_manager') as mock_config, \
                 patch('tools.dust.dust_model.subprocess.Popen') as mock_popen:
                
                # Setup mocks
                mock_config.get.return_value = 'dust'
                
                mock_process = Mock()
                mock_process.communicate.return_value = (
                    b'100M /test/directory\n50M /test/directory/subfolder',
                    b''
                )
                mock_popen.return_value = mock_process
                
                # Create plugin
                plugin = DustPlugin()
                plugin.initialize()
                
                model = plugin._model
                controller = plugin._controller
                
                # Test model execution
                start_time = time.time()
                html_output, html_error = model.execute_dust_command('/test/path')
                execution_time = time.time() - start_time
                
                if html_output and not html_error:
                    self.results['test_results'].append({
                        'test': 'model_execution',
                        'status': 'PASS',
                        'duration': execution_time,
                        'details': f'Model executed successfully in {execution_time:.3f}s'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'model_execution',
                        'status': 'FAIL',
                        'duration': execution_time,
                        'details': f'Model execution failed: {html_error}'
                    })
                    return False
                
                # Test parameter extraction
                view = plugin._view
                view.dust_path_input.setText('/workflow/test')
                view.dust_max_depth_spinbox.setValue(3)
                
                params = view.get_analysis_parameters()
                
                if (params['target_path'] == '/workflow/test' and
                    params['max_depth'] == 3):
                    self.results['test_results'].append({
                        'test': 'parameter_extraction',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'Parameters extracted correctly'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'parameter_extraction',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': f'Parameter extraction failed: {params}'
                    })
                
                # Test command building
                command = model._build_dust_command(
                    '/test/path', 3, True, 50, None, None, False, None, False, False
                )
                
                if '/test/path' in command and 'dust' in command[0]:
                    self.results['test_results'].append({
                        'test': 'command_building',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'Command built correctly'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'command_building',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': f'Command building failed: {command}'
                    })
                
                # Cleanup
                plugin.cleanup()
                view.deleteLater()
                
                return True
                
        except Exception as e:
            self.results['test_results'].append({
                'test': 'workflow_execution',
                'status': 'ERROR',
                'duration': 0,
                'details': f'Exception during workflow test: {str(e)}'
            })
            return False
        
        finally:
            stats = performance_monitor.stop_monitoring()
            self.results['performance_stats']['workflow_execution'] = stats
    
    def verify_error_handling(self):
        """Verify error handling and recovery mechanisms"""
        print("🛡️ Verifying Error Handling...")
        
        try:
            # Test 1: Missing executable
            with patch('tools.dust.dust_model.config_manager') as mock_config:
                mock_config.get.return_value = '/nonexistent/dust'
                
                plugin = DustPlugin()
                plugin.initialize()
                
                available = plugin.check_tools_availability()
                
                if not available:
                    self.results['test_results'].append({
                        'test': 'missing_executable_handling',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'Correctly detected missing executable'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'missing_executable_handling',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': 'Failed to detect missing executable'
                    })
                
                plugin.cleanup()
            
            # Test 2: Command execution error
            with patch('tools.dust.dust_model.config_manager') as mock_config, \
                 patch('tools.dust.dust_model.subprocess.Popen') as mock_popen:
                
                mock_config.get.return_value = 'dust'
                mock_popen.side_effect = FileNotFoundError("Command not found")
                
                plugin = DustPlugin()
                plugin.initialize()
                
                model = plugin._model
                html_output, html_error = model.execute_dust_command('/test/path')
                
                if not html_output and "not found" in html_error:
                    self.results['test_results'].append({
                        'test': 'command_error_handling',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'Correctly handled command execution error'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'command_error_handling',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': 'Did not handle command error properly'
                    })
                
                plugin.cleanup()
            
            # Test 3: Invalid path validation
            with patch('tools.dust.dust_model.config_manager') as mock_config:
                mock_config.get.return_value = 'dust'
                
                plugin = DustPlugin()
                plugin.initialize()
                
                model = plugin._model
                is_valid = model.validate_path('/nonexistent/path/12345')
                
                if not is_valid:
                    self.results['test_results'].append({
                        'test': 'invalid_path_validation',
                        'status': 'PASS',
                        'duration': 0,
                        'details': 'Correctly validated invalid path'
                    })
                else:
                    self.results['test_results'].append({
                        'test': 'invalid_path_validation',
                        'status': 'FAIL',
                        'duration': 0,
                        'details': 'Failed to detect invalid path'
                    })
                
                plugin.cleanup()
            
            return True
            
        except Exception as e:
            self.results['test_results'].append({
                'test': 'error_handling',
                'status': 'ERROR',
                'duration': 0,
                'details': f'Exception during error handling test: {str(e)}'
            })
            return False
    
    def verify_resource_usage(self):
        """Verify resource usage is within acceptable limits"""
        print("📊 Verifying Resource Usage...")
        
        # Analyze performance stats
        all_stats = self.results['performance_stats']
        
        resource_issues = []
        
        for test_name, stats in all_stats.items():
            # Check memory usage (should be < 100MB increase)
            memory_increase = stats.get('max_memory_mb', 0) - stats.get('start_memory_mb', 0)
            if memory_increase > 100:
                resource_issues.append(f"{test_name}: High memory usage (+{memory_increase:.1f}MB)")
            
            # Check CPU usage (should be < 80% max)
            max_cpu = stats.get('max_cpu_percent', 0)
            if max_cpu > 80:
                resource_issues.append(f"{test_name}: High CPU usage ({max_cpu:.1f}%)")
        
        if not resource_issues:
            self.results['test_results'].append({
                'test': 'resource_usage',
                'status': 'PASS',
                'duration': 0,
                'details': 'Resource usage within acceptable limits'
            })
            return True
        else:
            self.results['test_results'].append({
                'test': 'resource_usage',
                'status': 'WARN',
                'duration': 0,
                'details': f'Resource usage issues: {"; ".join(resource_issues)}'
            })
            return True  # Not a critical failure
    
    def generate_final_report(self):
        """Generate final integration verification report"""
        print("\n" + "=" * 60)
        print("🎯 DUST TOOL INTEGRATION VERIFICATION REPORT")
        print("=" * 60)
        
        # Test results summary
        total_tests = len(self.results['test_results'])
        passed_tests = len([t for t in self.results['test_results'] if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.results['test_results'] if t['status'] == 'FAIL'])
        error_tests = len([t for t in self.results['test_results'] if t['status'] == 'ERROR'])
        warn_tests = len([t for t in self.results['test_results'] if t['status'] == 'WARN'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   💥 Errors: {error_tests}")
        print(f"   ⚠️  Warnings: {warn_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Component status
        print(f"\n🔧 Component Status:")
        for component, status in self.results['component_status'].items():
            status_icon = "✅" if status == "OK" else "❌"
            print(f"   {status_icon} {component}: {status}")
        
        # Performance summary
        print(f"\n⚡ Performance Summary:")
        for test_name, stats in self.results['performance_stats'].items():
            memory_change = stats.get('max_memory_mb', 0) - stats.get('start_memory_mb', 0)
            max_cpu = stats.get('max_cpu_percent', 0)
            duration = stats.get('duration_seconds', 0)
            
            print(f"   {test_name}:")
            print(f"     - Duration: {duration:.2f}s")
            print(f"     - Memory Change: {memory_change:+.1f}MB")
            print(f"     - Peak CPU: {max_cpu:.1f}%")
        
        # Detailed test results
        if failed_tests > 0 or error_tests > 0:
            print(f"\n❌ Failed/Error Test Details:")
            for test in self.results['test_results']:
                if test['status'] in ['FAIL', 'ERROR']:
                    print(f"   - {test['test']}: {test['status']}")
                    print(f"     💡 {test['details']}")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment:")
        
        if failed_tests == 0 and error_tests == 0:
            self.results['overall_status'] = 'SUCCESS'
            print("   ✅ INTEGRATION VERIFICATION SUCCESSFUL")
            print("   🎉 Dust tool is ready for production use")
        elif error_tests > 0:
            self.results['overall_status'] = 'CRITICAL_ERRORS'
            print("   💥 CRITICAL ERRORS DETECTED")
            print("   🚨 Dust tool requires fixes before use")
        elif failed_tests > 0:
            self.results['overall_status'] = 'HAS_FAILURES'
            print("   ⚠️  INTEGRATION HAS FAILURES")
            print("   🔧 Dust tool needs improvements")
        
        # User experience assessment
        ui_issues = len([c for c, s in self.results['component_status'].items() 
                        if c.startswith('ui_') and s != 'OK'])
        
        if ui_issues == 0:
            print("   👍 User experience: EXCELLENT")
            self.results['user_experience']['rating'] = 'EXCELLENT'
        elif ui_issues <= 2:
            print("   👌 User experience: GOOD")
            self.results['user_experience']['rating'] = 'GOOD'
        else:
            print("   👎 User experience: NEEDS IMPROVEMENT")
            self.results['user_experience']['rating'] = 'NEEDS_IMPROVEMENT'
        
        return self.results
    
    def save_report(self, filename='dust_integration_report.json'):
        """Save integration report to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Integration report saved to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False


def main():
    """Main verification function"""
    print("🚀 Dust Tool Integration Verification")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    verifier = DustIntegrationVerifier()
    
    try:
        # Run verification steps
        steps = [
            ("Component Initialization", verifier.verify_component_initialization),
            ("UI Rendering", verifier.verify_ui_rendering_and_interaction),
            ("Workflow Execution", verifier.verify_workflow_execution),
            ("Error Handling", verifier.verify_error_handling),
            ("Resource Usage", verifier.verify_resource_usage)
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            print(f"\n📋 Step: {step_name}")
            try:
                success = step_func()
                if not success:
                    all_passed = False
                    print(f"   ❌ {step_name} failed")
                else:
                    print(f"   ✅ {step_name} passed")
            except Exception as e:
                all_passed = False
                print(f"   💥 {step_name} error: {e}")
        
        # Generate final report
        report = verifier.generate_final_report()
        
        # Save report
        verifier.save_report()
        
        # Return appropriate exit code
        if report['overall_status'] == 'SUCCESS':
            print(f"\n🎉 Integration verification completed successfully!")
            return 0
        elif report['overall_status'] == 'CRITICAL_ERRORS':
            print(f"\n💥 Integration verification found critical errors!")
            return 2
        else:
            print(f"\n⚠️ Integration verification completed with issues!")
            return 1
    
    except Exception as e:
        print(f"\n💥 Fatal error during verification: {e}")
        import traceback
        traceback.print_exc()
        return 3
    
    finally:
        # Cleanup QApplication
        if verifier.app:
            verifier.app.quit()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)