#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試手動調用自動啟動監控功能
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import time

project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_manual_auto_start():
    """測試手動調用自動啟動"""
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    try:
        print("Testing manual auto-start...")
        
        # 創建 Glances 視圖
        from tools.glances.glances_view import GlancesView
        view = GlancesView()
        
        print("Created GlancesView")
        
        # 監聽監控啟動信號
        monitor_started = False
        
        def on_start_monitoring():
            nonlocal monitor_started
            monitor_started = True
            print("+ Monitoring signal emitted!")
            
        view.start_monitoring.connect(on_start_monitoring)
        
        # 手動調用 _auto_start_monitoring 方法
        print("Manually calling _auto_start_monitoring...")
        view._auto_start_monitoring()
        
        # 給一點時間讓信號處理
        app.processEvents()
        
        if monitor_started:
            print("+ Manual auto-start monitoring SUCCESSFUL!")
            return True
        else:
            print("- Manual auto-start monitoring FAILED")
            return False
            
    except Exception as e:
        print(f"Error testing manual auto-start: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Manual Auto-Start Test")
    print("=" * 50)
    
    success = test_manual_auto_start()
    
    print("=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")