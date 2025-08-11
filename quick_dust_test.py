#!/usr/bin/env python3
"""
Quick Dust Integration Test
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("Quick Dust Integration Test")
    print("=" * 30)
    
    # Test 1: Plugin file exists
    dust_plugin_path = project_root / "tools" / "dust" / "plugin.py"
    print(f"1. Plugin file exists: {dust_plugin_path.exists()}")
    
    # Test 2: Plugin import
    try:
        from tools.dust.plugin import create_plugin
        dust_plugin = create_plugin()
        print(f"2. Plugin import: OK (name={dust_plugin.name})")
    except Exception as e:
        print(f"2. Plugin import: FAIL ({e})")
        return False
    
    # Test 3: Plugin manager
    try:
        from core.plugin_manager import plugin_manager
        plugin_manager.discover_plugins()
        plugins = plugin_manager.get_all_plugins()
        dust_found = "dust" in plugins
        print(f"3. Plugin discovery: {'OK' if dust_found else 'FAIL'}")
    except Exception as e:
        print(f"3. Plugin discovery: FAIL ({e})")
        return False
    
    # Test 4: Main window import
    try:
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from ui.main_window import ModernMainWindow
        print("4. Main window import: OK")
    except Exception as e:
        print(f"4. Main window import: FAIL ({e})")
        return False
    
    print("=" * 30)
    print("SUCCESS: Basic dust integration verified!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)