#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試初始化延遲自動啟動監控功能
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import time

project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_init_auto_start():
    """測試初始化延遲自動啟動"""
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    try:
        print("Testing initialization auto-start...")
        
        # 監聽監控啟動信號
        monitor_started = False
        
        def on_start_monitoring():
            nonlocal monitor_started
            monitor_started = True
            print("+ Monitoring signal emitted from init delay!")
            
        # 創建 Glances 視圖（這會觸發 QTimer.singleShot）
        from tools.glances.glances_view import GlancesView
        view = GlancesView()
        
        print("Created GlancesView with init delay timer")
        
        view.start_monitoring.connect(on_start_monitoring)
        
        # 等待初始化延遲自動啟動 - 3秒總等待時間
        QTimer.singleShot(3500, app.quit)  # 3.5秒後退出
        app.exec_()
        
        if monitor_started:
            print("+ Init delay auto-start monitoring SUCCESSFUL!")
            return True
        else:
            print("- Init delay auto-start monitoring FAILED")
            return False
            
    except Exception as e:
        print(f"Error testing init auto-start: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Init Delay Auto-Start Test")
    print("=" * 50)
    
    success = test_init_auto_start()
    
    print("=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")