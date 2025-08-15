"""
Glances 控制器類 - 連接視圖和模型，處理用戶交互
協調系統監控數據的獲取、處理和顯示
"""

import logging
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication

from .glances_model import GlancesModel
from .glances_view import GlancesView

logger = logging.getLogger(__name__)


class GlancesDataWorker(QThread):
    """Glances 數據獲取工作線程"""
    
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool, str)
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.stop_flag = False
        self.update_interval = 1000  # 1秒
        
    def run(self):
        """執行數據獲取循環"""
        print("[DEBUG] Glances 數據工作線程啟動...")
        logger.info("Glances data worker started")
        
        cycle_count = 0
        while not self.stop_flag:
            try:
                cycle_count += 1
                print(f"[DEBUG] 數據獲取循環 #{cycle_count}...")
                
                # 獲取系統數據
                data = self.model.get_system_stats()
                
                if data:
                    print(f"   [DEBUG] 數據獲取成功，包含 {len(data)} 個字段")
                    # 顯示主要數據指標
                    cpu = data.get('cpu', {}).get('total', 'N/A')
                    mem = data.get('mem', {}).get('percent', 'N/A')
                    print(f"   [DEBUG] 當前指標: CPU {cpu}%, 記憶體 {mem}%")
                    
                    self.data_received.emit(data)
                    print("   [DEBUG] 數據已發送到視圖...")
                    
                    # 檢查連接模式
                    if data.get("status") == "fallback_mode":
                        print("   [DEBUG] 使用回退模式")
                        self.connection_status_changed.emit(False, "fallback")
                    elif self.model.api_mode:
                        print("   [DEBUG] API 模式已連接")
                        self.connection_status_changed.emit(True, "API")
                    elif self.model.subprocess_mode:
                        print("   [DEBUG] 子進程模式已連接")
                        self.connection_status_changed.emit(True, "subprocess")
                else:
                    print("   [DEBUG] 數據獲取失敗，返回空數據")
                    self.error_occurred.emit("無法獲取系統數據")
                    
            except Exception as e:
                print(f"   [DEBUG] 數據獲取異常: {e}")
                logger.error(f"Error in data worker: {e}")
                self.error_occurred.emit(f"數據獲取錯誤: {str(e)}")
            
            # 等待指定間隔
            self.msleep(self.update_interval)
        
        print("[DEBUG] Glances 數據工作線程停止")
        logger.info("Glances data worker stopped")
    
    def stop(self):
        """停止工作線程"""
        self.stop_flag = True
    
    def set_update_interval(self, interval_ms: int):
        """設置更新間隔"""
        self.update_interval = max(500, min(10000, interval_ms))


class GlancesController(QObject):
    """Glances 控制器類 - 協調視圖和模型的交互"""
    
    def __init__(self, model=None, view=None):
        super().__init__()
        print("[DEBUG] 初始化 Glances 控制器...")
        self.model = model if model is not None else GlancesModel()
        self.view = view if view is not None else GlancesView()
        self.data_worker = None
        self.is_monitoring = False
        
        print("[DEBUG] 連接視圖信號...")
        self._connect_signals()
        print("[DEBUG] 初始化視圖設置...")
        self._initialize_view()
        
        print("[DEBUG] Glances 控制器初始化完成")
        logger.info("GlancesController initialized")
        
    def _connect_signals(self):
        """連接視圖信號到控制器方法"""
        # 連接視圖信號
        self.view.start_monitoring.connect(self.start_monitoring)
        self.view.stop_monitoring.connect(self.stop_monitoring)
        self.view.refresh_data.connect(self.refresh_data)
        self.view.update_interval_changed.connect(self.update_interval_changed)
        self.view.start_glances_server.connect(self.start_glances_server)
        
        logger.info("Signals connected")
    
    def _initialize_view(self):
        """初始化視圖"""
        # 檢查 Glances 可用性
        availability = self.model.check_glances_availability()
        
        if not availability["available"]:
            self.view.set_status("Glances 不可用 - 請安裝 Glances 工具")
            self.view.set_connection_status(False)
            
            # 顯示安裝信息
            install_info = self.model.get_installation_info()
            error_msg = f"""Glances 系統監控工具未安裝或不可用。

安裝方法：
{install_info['install_command']}

描述：{install_info['description']}

請安裝後重新啟動應用程式。"""
            
            self.view.show_error("Glances 不可用", error_msg)
            return
        
        # 設置初始狀態
        recommended_mode = availability["recommended_mode"]
        status_msg = f"Glances 可用 - 推薦模式: {recommended_mode}"
        
        if availability["web_api"]:
            status_msg += " (Web API 可用)"
        elif availability["subprocess"]:
            status_msg += " (僅命令行模式)"
            
        self.view.set_status(status_msg)
        self.view.set_connection_status(availability["available"], recommended_mode)
        
        # 初始數據載入
        self.refresh_data()
        
        logger.info(f"View initialized - {status_msg}")
    
    def start_monitoring(self):
        """開始監控"""
        if self.is_monitoring:
            print("[DEBUG] 監控已在運行，跳過啟動")
            return
            
        print("[DEBUG] 開始啟動 Glances 監控...")
        logger.info("Starting monitoring")
        
        # 創建並啟動數據工作線程
        print("[DEBUG] 創建數據工作線程...")
        self.data_worker = GlancesDataWorker(self.model)
        self.data_worker.data_received.connect(self.handle_data_received)
        self.data_worker.error_occurred.connect(self.handle_error)
        self.data_worker.connection_status_changed.connect(self.handle_connection_status)
        
        # 設置更新間隔
        interval = self.view.interval_spin.value()
        print(f"[DEBUG] 設置更新間隔: {interval}ms")
        self.data_worker.set_update_interval(interval)
        
        print("[DEBUG] 啟動數據工作線程...")
        self.data_worker.start()
        self.is_monitoring = True
        
        self.view.set_status("監控中...")
        print("[DEBUG] Glances 監控啟動完成")
        logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """停止監控"""
        if not self.is_monitoring:
            return
            
        logger.info("Stopping monitoring")
        
        if self.data_worker:
            self.data_worker.stop()
            if not self.data_worker.wait(5000):  # 等待 5 秒
                self.data_worker.terminate()
                self.data_worker.wait(1000)
            
            self.data_worker = None
        
        self.is_monitoring = False
        self.view.set_status("監控已停止")
        logger.info("Monitoring stopped")
    
    def refresh_data(self):
        """手動重新整理數據"""
        logger.info("Manual data refresh")
        
        try:
            # 重新檢測可用模式
            self.model._detect_available_modes()
            
            # 獲取當前數據
            data = self.model.get_system_stats()
            
            if data:
                self.handle_data_received(data)
                self.view.set_status("數據已更新")
            else:
                self.view.set_status("無法獲取數據")
                
        except Exception as e:
            logger.error(f"Error during manual refresh: {e}")
            self.view.set_status(f"更新失敗: {str(e)}")
    
    def update_interval_changed(self, interval_ms: int):
        """更新間隔變更"""
        logger.info(f"Update interval changed to {interval_ms}ms")
        
        if self.data_worker:
            self.data_worker.set_update_interval(interval_ms)
        
        # 更新模型配置
        self.model.update_config({"update_interval": interval_ms})
    
    def start_glances_server(self, port: int):
        """啟動 Glances 服務器"""
        logger.info(f"Starting Glances server on port {port}")
        
        success, message = self.model.start_glances_server(port)
        
        if success:
            self.view.show_info("服務器啟動", message)
            self.view.set_status("正在啟動 Glances 服務器...")
            
            # 5 秒後重新檢測連接
            QTimer.singleShot(5000, self._recheck_connection)
        else:
            self.view.show_error("服務器啟動失敗", message)
            self.view.set_status("服務器啟動失敗")
    
    def _recheck_connection(self):
        """重新檢查連接狀態"""
        self.model._detect_available_modes()
        availability = self.model.check_glances_availability()
        
        if availability["web_api"]:
            self.view.set_connection_status(True, "API")
            self.view.set_status("Glances Web API 可用")
        else:
            self.view.set_status("Web API 仍不可用，請檢查服務器狀態")
    
    def handle_data_received(self, data: dict):
        """處理接收到的數據"""
        try:
            print("[DEBUG] 控制器接收到數據，開始更新視圖...")
            
            # 檢查數據內容
            cpu = data.get('cpu', {}).get('total', 'N/A')
            mem = data.get('mem', {}).get('percent', 'N/A')
            processes_count = len(data.get('processes', []))
            print(f"   [DEBUG] 數據內容: CPU {cpu}%, 記憶體 {mem}%, {processes_count} 個進程")
            
            # 更新系統概覽
            print("   [DEBUG] 更新系統概覽...")
            self.view.update_system_overview(data)
            
            # 更新進程表格
            processes = data.get('processes', [])
            if processes:
                # 限制顯示的進程數量（前 50 個）
                print(f"   [DEBUG] 更新進程表格 (前50個，共{len(processes)}個)...")
                self.view.update_process_table(processes[:50])
            
            # 更新原始數據顯示
            print("   [DEBUG] 更新原始數據顯示...")
            self.view.update_raw_data(data)
            
            # 更新應用程序事件循環
            QApplication.processEvents()
            print("   [DEBUG] 視圖更新完成")
            
        except Exception as e:
            print(f"   [DEBUG] 處理數據時發生錯誤: {e}")
            logger.error(f"Error handling received data: {e}")
    
    def handle_error(self, error_message: str):
        """處理錯誤"""
        logger.error(f"Data worker error: {error_message}")
        self.view.set_status(f"錯誤: {error_message}")
    
    def handle_connection_status(self, connected: bool, mode: str):
        """處理連接狀態變更"""
        self.view.set_connection_status(connected, mode)
        
        if connected:
            status_msg = f"已連接 - {mode} 模式"
        else:
            status_msg = "連接失敗 - 使用回退數據"
            
        self.view.set_status(status_msg)
    
    def get_view(self):
        """獲取視圖對象"""
        return self.view
    
    def cleanup(self):
        """清理資源"""
        logger.info("Starting cleanup")
        
        # 停止監控
        self.stop_monitoring()
        
        # 清理模型資源
        if hasattr(self.model, 'cleanup'):
            self.model.cleanup()
        
        logger.info("GlancesController cleanup completed")