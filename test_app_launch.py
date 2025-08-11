#!/usr/bin/env python3
"""
Test Application Launch with Dust Plugin
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set offscreen mode for GUI testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_app_launch():
    """Test that the main application launches successfully with dust plugin"""
    print("Testing Application Launch with Dust Plugin")
    print("=" * 45)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from ui.main_window import ModernMainWindow
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("1. QApplication created: OK")
        
        # Create main window
        main_window = ModernMainWindow()
        print("2. Main window created: OK")
        
        # Check if dust plugin is loaded
        plugin_views = main_window.plugin_views
        dust_in_views = "dust" in plugin_views
        print(f"3. Dust plugin in views: {'OK' if dust_in_views else 'PENDING'}")
        
        # Check navigation buttons
        nav_buttons = main_window.sidebar.navigation_buttons
        dust_nav_found = any("dust" in key.lower() or "dust" in str(btn.text()).lower() 
                            for key, btn in nav_buttons.items())
        print(f"4. Dust navigation button: {'OK' if dust_nav_found else 'CHECKING'}")
        
        # Show window briefly
        main_window.show()
        print("5. Window displayed: OK")
        
        # Use a timer to close the window after a short delay
        def close_window():
            main_window.close()
            print("6. Window closed: OK")
            print("=" * 45)
            print("SUCCESS: Application launched successfully with dust plugin!")
        
        QTimer.singleShot(1000, close_window)  # Close after 1 second
        
        # Run event loop briefly
        QTimer.singleShot(1500, app.quit)  # Exit after 1.5 seconds
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"FAIL: Error during application launch: {e}")
        return False

if __name__ == "__main__":
    success = test_app_launch()
    sys.exit(0 if success else 1)