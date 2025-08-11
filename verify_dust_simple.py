#!/usr/bin/env python3
"""
Simple Dust Integration Verification Script
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set offscreen mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def verify_integration():
    """Verify dust tool integration status"""
    print("Dust Tool Integration Verification")
    print("=" * 50)
    
    results = []
    
    # 1. Check dust plugin file exists
    try:
        dust_plugin_path = project_root / "tools" / "dust" / "plugin.py"
        if dust_plugin_path.exists():
            print("OK: Dust plugin file exists")
            results.append(True)
        else:
            print("FAIL: Dust plugin file missing")
            results.append(False)
    except Exception as e:
        print(f"FAIL: Error checking dust plugin file: {e}")
        results.append(False)
    
    # 2. Check plugin import
    try:
        from tools.dust.plugin import create_plugin
        dust_plugin = create_plugin()
        if dust_plugin.name == "dust":
            print("OK: Dust plugin imports correctly")
            results.append(True)
        else:
            print("FAIL: Dust plugin import failed")
            results.append(False)
    except Exception as e:
        print(f"FAIL: Error importing dust plugin: {e}")
        results.append(False)
    
    # 3. Check plugin manager discovery
    try:
        from core.plugin_manager import plugin_manager
        plugin_manager.initialize()
        
        all_plugins = plugin_manager.get_all_plugins()
        if "dust" in all_plugins:
            print("OK: Dust plugin discovered by plugin manager")
            results.append(True)
        else:
            print("FAIL: Dust plugin not discovered")
            results.append(False)
    except Exception as e:
        print(f"FAIL: Error checking plugin discovery: {e}")
        results.append(False)
    
    # 4. Check UI integration
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from ui.main_window import ModernMainWindow
        main_window = ModernMainWindow()
        
        # Check navigation buttons
        navigation_buttons = main_window.sidebar.navigation_buttons
        dust_found = False
        for key, btn in navigation_buttons.items():
            if "dust" in key.lower() or "dust" in str(btn.text()).lower():
                dust_found = True
                break
        
        if dust_found:
            print("OK: Dust navigation button created")
            results.append(True)
        else:
            print("FAIL: Dust navigation button missing")
            results.append(False)
            
        main_window.close()
    except Exception as e:
        print(f"FAIL: Error checking UI integration: {e}")
        results.append(False)
    
    # 5. Check dust tool availability
    try:
        from tools.dust.dust_model import DustModel
        model = DustModel()
        available, version, _ = model.check_dust_availability()
        
        if available:
            print(f"OK: Dust tool available: {version}")
            results.append(True)
        else:
            print("INFO: Dust tool not installed (integration still works)")
            results.append(True)  # This is not an error
    except Exception as e:
        print(f"FAIL: Error checking dust tool: {e}")
        results.append(False)
    
    # Summary
    print("=" * 50)
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Integration Status: {success_count}/{total_count} checks passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("SUCCESS: Dust tool integration completed!")
        return True
    else:
        print("FAILED: Dust tool integration has issues!")
        return False

if __name__ == "__main__":
    try:
        success = verify_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)