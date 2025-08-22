#!/usr/bin/env python3
"""
Test QPDF plugin components
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_qpdf_plugin():
    """Test QPDF plugin component creation"""
    try:
        print("Testing QPDF plugin component creation...")
        
        from tools.qpdf.plugin import create_plugin
        
        # Create plugin
        plugin = create_plugin()
        print(f"✓ Plugin created: {plugin.name}")
        
        # Create model
        model = plugin.create_model()
        print(f"✓ Model created: {type(model).__name__}")
        
        # Create view
        view = plugin.create_view()
        print(f"✓ View created: {type(view).__name__}")
        
        # Create controller
        controller = plugin.create_controller(model, view)
        print(f"✓ Controller created: {type(controller).__name__}")
        
        print("✓ All QPDF components created successfully!")
        return True
        
    except Exception as e:
        print(f"✗ QPDF plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qpdf_plugin()
    if success:
        print("\n🎉 QPDF plugin is working correctly!")
    else:
        print("\n❌ QPDF plugin has issues!")
        sys.exit(1)