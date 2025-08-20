#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test():
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    try:
        print("Testing Glances plugin with QApplication...")
        
        from tools.glances.plugin import create_plugin
        plugin = create_plugin()
        
        print(f"Plugin name: {plugin.name}")
        
        init_result = plugin.initialize()
        print(f"Initialization: {init_result}")
        
        if init_result:
            print("Creating model...")
            model = plugin.create_model()
            print("+ Model created")
            
            print("Creating view...")
            view = plugin.create_view()  
            print("+ View created")
            
            print("Creating controller...")
            controller = plugin.create_controller(model, view)
            print("+ Controller created")
            
            print("SUCCESS: All components created successfully!")
            return True
        else:
            print("FAILED: Plugin initialization failed")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")