#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Glances 視圖自動啟動監控功能
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import time

project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

def test_auto_monitoring():
    """測試自動監控功能"""
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    try:
        print("Testing auto-start monitoring...")
        
        # 創建 Glances 視圖
        from tools.glances.glances_view import GlancesView
        view = GlancesView()
        
        print("Created GlancesView")
        
        # 檢查是否有 showEvent 方法
        if hasattr(view, 'showEvent'):
            print("+ showEvent method exists")
        else:
            print("- showEvent method missing")
            
        # 檢查是否有自動啟動標記
        if hasattr(view, 'auto_start_attempted'):
            print("+ auto_start_attempted flag exists")
        else:
            print("- auto_start_attempted flag missing")
            
        # 檢查是否有 _auto_start_monitoring 方法
        if hasattr(view, '_auto_start_monitoring'):
            print("+ _auto_start_monitoring method exists")
        else:
            print("- _auto_start_monitoring method missing")
        
        # 模擬顯示視圖並檢查監控是否會啟動
        monitor_started = False
        
        def on_start_monitoring():
            nonlocal monitor_started
            monitor_started = True
            print("+ Monitoring signal emitted!")
            
        view.start_monitoring.connect(on_start_monitoring)
        
        print("Showing view to trigger showEvent...")
        view.show()
        
        # 等待自動啟動 - 延長等待時間
        QTimer.singleShot(2500, app.quit)  # 2.5秒後退出
        app.exec_()
        
        if monitor_started:
            print("+ Auto-start monitoring SUCCESSFUL!")
            return True
        else:
            print("- Auto-start monitoring FAILED")
            return False
            
    except Exception as e:
        print(f"Error testing auto-start monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Auto-Start Monitoring Test")
    print("=" * 50)
    
    success = test_auto_monitoring()
    
    print("=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")