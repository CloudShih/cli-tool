#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glances 即時調試監控工具
在用戶手動操作時在終端顯示詳細狀態
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class GlancesDebugMonitor(QObject):
    """Glances 調試監控器"""
    
    status_update = pyqtSignal(str, str)  # timestamp, message
    
    def __init__(self):
        super().__init__()
        self.monitoring_active = False
        self.data_received_count = 0
        self.last_data_time = None
        self.plugin_view = None
        self.plugin_controller = None
        
    def log_status(self, message):
        """記錄狀態信息"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
        self.status_update.emit(timestamp, message)
        
    def monitor_glances_plugin(self):
        """監控 Glances 插件狀態"""
        try:
            from core.plugin_manager import plugin_manager
            
            # 檢查插件管理器狀態
            self.log_status("🔍 檢查插件管理器...")
            
            if not plugin_manager._initialized:
                self.log_status("⚠️  插件管理器未初始化，正在初始化...")
                plugin_manager.initialize()
            
            # 檢查 Glances 插件
            plugins = plugin_manager.get_available_plugins()
            if 'glances' not in plugins:
                self.log_status("❌ Glances 插件不存在於可用插件列表中")
                self.log_status(f"   可用插件: {list(plugins.keys())}")
                return False
            else:
                self.log_status("✅ Glances 插件已註冊")
                
            # 獲取插件實例
            plugin_instance = plugin_manager.get_plugin_instance('glances')
            if not plugin_instance:
                self.log_status("❌ 無法獲取 Glances 插件實例")
                return False
            else:
                self.log_status("✅ Glances 插件實例已創建")
                self.plugin_view = plugin_instance.get('view')
                self.plugin_controller = plugin_instance.get('controller')
                
                if self.plugin_view:
                    self.log_status("✅ Glances 視圖已創建")
                    self.monitor_view_state()
                else:
                    self.log_status("❌ Glances 視圖未創建")
                    
                if self.plugin_controller:
                    self.log_status("✅ Glances 控制器已創建")
                    self.monitor_controller_state()
                else:
                    self.log_status("❌ Glances 控制器未創建")
                    
            return True
            
        except Exception as e:
            self.log_status(f"❌ 監控插件時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def monitor_view_state(self):
        """監控視圖狀態"""
        if not self.plugin_view:
            return
            
        try:
            # 檢查視圖屬性
            self.log_status("📊 檢查視圖狀態...")
            
            if hasattr(self.plugin_view, 'is_monitoring_started'):
                monitoring = self.plugin_view.is_monitoring_started
                self.log_status(f"   監控狀態: {monitoring}")
            
            if hasattr(self.plugin_view, 'auto_start_attempted'):
                auto_started = self.plugin_view.auto_start_attempted
                self.log_status(f"   自動啟動狀態: {auto_started}")
            
            if hasattr(self.plugin_view, 'charts_widget'):
                charts = self.plugin_view.charts_widget
                self.log_status(f"   圖表組件: {'存在' if charts else '缺失'}")
                
                # 檢查圖表數據
                if charts and hasattr(charts, 'charts'):
                    chart_names = list(charts.charts.keys())
                    self.log_status(f"   圖表類型: {chart_names}")
                    
                    # 檢查每個圖表的數據點數量
                    for name, chart in charts.charts.items():
                        if hasattr(chart, 'series_data'):
                            data_count = 0
                            for series_name, series in chart.series_data.items():
                                if hasattr(series, 'values'):
                                    data_count += len(series.values)
                            self.log_status(f"   {name} 圖表數據點: {data_count}")
                            
        except Exception as e:
            self.log_status(f"❌ 監控視圖狀態時發生錯誤: {e}")
            
    def monitor_controller_state(self):
        """監控控制器狀態"""
        if not self.plugin_controller:
            return
            
        try:
            # 檢查控制器屬性
            self.log_status("🎮 檢查控制器狀態...")
            
            if hasattr(self.plugin_controller, 'is_monitoring'):
                monitoring = self.plugin_controller.is_monitoring
                self.log_status(f"   控制器監控狀態: {monitoring}")
            
            if hasattr(self.plugin_controller, 'data_worker'):
                worker = self.plugin_controller.data_worker
                if worker:
                    worker_running = worker.isRunning() if hasattr(worker, 'isRunning') else False
                    self.log_status(f"   數據工作線程: {'運行中' if worker_running else '已停止'}")
                else:
                    self.log_status("   數據工作線程: 未創建")
                    
            # 嘗試手動獲取一次數據來測試
            if hasattr(self.plugin_controller, 'model'):
                model = self.plugin_controller.model
                if model:
                    self.log_status("🔬 測試數據獲取...")
                    try:
                        test_data = model.get_system_stats()
                        if test_data:
                            data_keys = list(test_data.keys())
                            self.log_status(f"   測試數據成功: {data_keys}")
                            
                            # 檢查關鍵數據
                            if 'cpu' in test_data:
                                cpu_total = test_data['cpu'].get('total', 'N/A')
                                self.log_status(f"   CPU 使用率: {cpu_total}%")
                            
                            if 'mem' in test_data:
                                mem_percent = test_data['mem'].get('percent', 'N/A')
                                self.log_status(f"   記憶體使用率: {mem_percent}%")
                        else:
                            self.log_status("❌ 測試數據獲取失敗")
                    except Exception as e:
                        self.log_status(f"❌ 數據獲取測試失敗: {e}")
                        
        except Exception as e:
            self.log_status(f"❌ 監控控制器狀態時發生錯誤: {e}")
            
    def start_continuous_monitoring(self):
        """開始持續監控"""
        self.log_status("🚀 開始持續監控...")
        
        def monitor_loop():
            while True:
                try:
                    if self.plugin_view and self.plugin_controller:
                        # 檢查監控狀態變化
                        current_monitoring = getattr(self.plugin_controller, 'is_monitoring', False)
                        if current_monitoring != self.monitoring_active:
                            self.monitoring_active = current_monitoring
                            self.log_status(f"🔄 監控狀態變化: {current_monitoring}")
                        
                        # 檢查數據更新
                        if self.plugin_view.charts_widget:
                            current_data_count = 0
                            for chart in self.plugin_view.charts_widget.charts.values():
                                if hasattr(chart, 'series_data'):
                                    for series in chart.series_data.values():
                                        if hasattr(series, 'values'):
                                            current_data_count += len(series.values)
                            
                            if current_data_count != self.data_received_count:
                                self.data_received_count = current_data_count
                                self.last_data_time = datetime.now()
                                self.log_status(f"📈 新數據接收: 總數據點 {current_data_count}")
                    
                    time.sleep(2)  # 每2秒檢查一次
                    
                except Exception as e:
                    self.log_status(f"❌ 監控循環錯誤: {e}")
                    time.sleep(5)
        
        # 在後台線程中運行監控
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

def main():
    """主函數"""
    app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()
    
    monitor = GlancesDebugMonitor()
    
    print("=" * 70)
    print("🔍 Glances 即時調試監控工具")
    print("=" * 70)
    print("請在另一個終端運行: python main_app.py")
    print("然後導航到 Glances 頁面，此工具會顯示詳細狀態信息")
    print("按 Ctrl+C 結束監控")
    print("=" * 70)
    
    # 等待一段時間讓用戶啟動主應用程序
    print("等待 5 秒讓您啟動主應用程序...")
    time.sleep(5)
    
    try:
        # 開始監控
        if monitor.monitor_glances_plugin():
            monitor.start_continuous_monitoring()
            
            print("\n✅ 監控已啟動，現在請操作主應用程序...")
            print("   1. 點擊左側導航的 '📈 Glances'")
            print("   2. 觀察實時圖表是否顯示數據")
            print("   3. 此工具會顯示詳細的狀態變化")
            
            # 保持程序運行
            while True:
                time.sleep(1)
        else:
            print("❌ 無法開始監控，請確保主應用程序正在運行")
            
    except KeyboardInterrupt:
        print("\n\n👋 監控已停止")
    except Exception as e:
        print(f"❌ 監控過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()