#!/usr/bin/env python3
"""
Debug QPDF plugin loading and display
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_qpdf_loading():
    """Debug QPDF plugin loading process"""
    try:
        print("=== Debug QPDF Plugin Loading ===")
        
        # Test plugin manager
        from core.plugin_manager import plugin_manager
        print("\n1. Testing standard plugin manager...")
        
        # Initialize plugin manager
        plugin_manager.initialize()
        
        # Check if QPDF is discovered
        all_plugins = plugin_manager.get_all_plugins()
        available_plugins = plugin_manager.get_available_plugins()
        
        print(f"All plugins: {list(all_plugins.keys())}")
        print(f"Available plugins: {list(available_plugins.keys())}")
        
        if 'qpdf' in all_plugins:
            print("✓ QPDF plugin discovered")
            if 'qpdf' in available_plugins:
                print("✓ QPDF plugin available")
            else:
                print("✗ QPDF plugin not available")
        else:
            print("✗ QPDF plugin not discovered")
            
        # Test plugin instance creation
        if 'qpdf' in available_plugins:
            print("\n2. Testing QPDF plugin instance creation...")
            qpdf_plugin = available_plugins['qpdf']
            
            try:
                model = qpdf_plugin.create_model()
                print("✓ QPDF model created")
                
                view = qpdf_plugin.create_view()
                print("✓ QPDF view created")
                
                controller = qpdf_plugin.create_controller(model, view)
                print("✓ QPDF controller created")
                
                # Check if view has required methods
                if hasattr(view, 'windowTitle'):
                    print(f"✓ View title: {view.windowTitle()}")
                else:
                    print("✗ View missing windowTitle method")
                    
            except Exception as e:
                print(f"✗ Plugin instance creation failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== Debug Complete ===")
        return True
        
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_qpdf_loading()