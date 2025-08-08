#!/usr/bin/env python3
"""
Test Setup Validation Script
Validates that the QA test suite is properly configured and ready to run
"""
import sys
import os
import subprocess
from pathlib import Path
import importlib.util

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestSetupValidator:
    """Validates QA test suite setup"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.test_dir = Path(__file__).parent
    
    def check_python_version(self):
        """Check Python version"""
        if sys.version_info < (3, 7):
            self.issues.append(f"Python 3.7+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        else:
            print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    def check_required_packages(self):
        """Check required Python packages"""
        packages = {
            'unittest': 'Built-in testing framework',
            'json': 'JSON handling',
            'pathlib': 'Path operations',
            'subprocess': 'Process execution',
            'tempfile': 'Temporary files',
            'time': 'Time operations',
            'platform': 'Platform detection'
        }
        
        for package, description in packages.items():
            try:
                importlib.import_module(package)
                print(f"[OK] {package} - {description}")
            except ImportError:
                self.issues.append(f"Required package missing: {package}")
    
    def check_optional_packages(self):
        """Check optional but recommended packages"""
        optional_packages = {
            'PyQt5': 'GUI testing',
            'psutil': 'Performance monitoring'
        }
        
        for package, description in optional_packages.items():
            try:
                importlib.import_module(package)
                print(f"[OK] {package} - {description}")
            except ImportError:
                self.warnings.append(f"Optional package missing: {package} - {description}")
    
    def check_ripgrep_availability(self):
        """Check if ripgrep is available"""
        try:
            result = subprocess.run(['rg', '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.decode().strip().split('\n')[0]
                print(f"[OK] ripgrep - {version}")
            else:
                self.warnings.append("ripgrep available but version check failed")
        except subprocess.TimeoutExpired:
            self.warnings.append("ripgrep version check timed out")
        except FileNotFoundError:
            self.warnings.append("ripgrep not found - functional tests may fail")
    
    def check_test_files(self):
        """Check that all test files exist"""
        required_test_files = [
            'test_core_modules.py',
            'test_mvc_components.py',
            'test_functional_comprehensive.py',
            'test_performance.py',
            'test_integration_comprehensive.py',
            'test_usability.py',
            'test_cross_platform.py',
            'test_comprehensive_qa.py',
            'run_qa_suite.py'
        ]
        
        for test_file in required_test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                print(f"[OK] {test_file}")
            else:
                self.issues.append(f"Missing test file: {test_file}")
    
    def check_project_structure(self):
        """Check project structure"""
        project_paths = [
            '../plugin.py',
            '../core/data_models.py',
            '../core/search_engine.py',
            '../core/result_parser.py',
            '../ripgrep_model.py',
            '../ripgrep_view.py',
            '../ripgrep_controller.py'
        ]
        
        missing_files = []
        for rel_path in project_paths:
            full_path = self.test_dir / rel_path
            if not full_path.exists():
                missing_files.append(rel_path)
        
        if missing_files:
            self.warnings.append(f"Missing project files: {', '.join(missing_files)}")
        else:
            print("[OK] Project structure complete")
    
    def check_script_permissions(self):
        """Check script permissions"""
        scripts = ['run_ci_test.sh']
        
        for script in scripts:
            script_path = self.test_dir / script
            if script_path.exists():
                if os.access(script_path, os.X_OK):
                    print(f"[OK] {script} (executable)")
                else:
                    self.warnings.append(f"{script} not executable - run: chmod +x {script}")
            else:
                self.issues.append(f"Missing script: {script}")
    
    def check_output_permissions(self):
        """Check output directory permissions"""
        try:
            test_file = self.test_dir / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            print("[OK] Write permissions in test directory")
        except Exception as e:
            self.issues.append(f"Cannot write to test directory: {e}")
    
    def validate_sample_import(self):
        """Validate that we can import core components"""
        try:
            from tools.ripgrep.core.data_models import SearchParameters
            from tools.ripgrep.plugin import RipgrepPlugin
            print("[OK] Core component imports working")
        except ImportError as e:
            self.warnings.append(f"Import issue (may be expected in test env): {e}")
    
    def run_validation(self):
        """Run complete validation"""
        print("VALIDATING QA TEST SUITE SETUP")
        print("=" * 50)
        
        print("\nChecking Python environment...")
        self.check_python_version()
        self.check_required_packages()
        self.check_optional_packages()
        
        print("\nChecking external tools...")
        self.check_ripgrep_availability()
        
        print("\nChecking test files...")
        self.check_test_files()
        
        print("\nChecking project structure...")
        self.check_project_structure()
        
        print("\nChecking permissions...")
        self.check_script_permissions()
        self.check_output_permissions()
        
        print("\nChecking imports...")
        self.validate_sample_import()
        
        self.print_summary()
        
        return len(self.issues) == 0
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        
        if not self.issues and not self.warnings:
            print("PERFECT SETUP!")
            print("All checks passed")
            print("QA test suite is ready to run")
            print("\nRecommended next steps:")
            print("  1. Run quick test: python run_qa_suite.py quick")
            print("  2. Run full suite: python run_qa_suite.py full")
        elif not self.issues:
            print("GOOD SETUP (with minor warnings)")
            print("QA test suite is ready to run")
            if self.warnings:
                print(f"\n{len(self.warnings)} warning(s):")
                for warning in self.warnings:
                    print(f"   - {warning}")
            print("\nRecommended next steps:")
            print("  1. Consider addressing warnings for complete functionality")
            print("  2. Run quick test: python run_qa_suite.py quick")
        else:
            print("SETUP ISSUES DETECTED")
            print("QA test suite may not run correctly")
            
            print(f"\n{len(self.issues)} critical issue(s):")
            for issue in self.issues:
                print(f"   - {issue}")
            
            if self.warnings:
                print(f"\n{len(self.warnings)} warning(s):")
                for warning in self.warnings:
                    print(f"   - {warning}")
            
            print("\nRequired actions:")
            print("  1. Fix all critical issues above")
            print("  2. Re-run this validation script")
            print("  3. Then run QA test suite")


def main():
    """Main validation function"""
    validator = TestSetupValidator()
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\nValidation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()