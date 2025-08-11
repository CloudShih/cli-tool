"""
dust 工具的控制器層
負責協調視圖和模型之間的交互
"""

import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from tools.dust.dust_model import DustModel
from tools.dust.dust_view_redesigned import DustViewRedesigned

logger = logging.getLogger(__name__)


class DustAnalysisWorker(QThread):
    """dust 分析工作線程"""
    
    analysis_started = pyqtSignal()
    analysis_progress = pyqtSignal(str)  # 進度訊息
    analysis_completed = pyqtSignal(str, str, bool)  # output, error, success
    
    def __init__(self, model, target_path, max_depth, sort_reverse, number_of_lines,
                 file_types, exclude_patterns, show_apparent_size, min_size,
                 full_paths, files_only):
        super().__init__()
        self.model = model
        self.target_path = target_path
        self.max_depth = max_depth
        self.sort_reverse = sort_reverse
        self.number_of_lines = number_of_lines
        self.file_types = file_types
        self.exclude_patterns = exclude_patterns
        self.show_apparent_size = show_apparent_size
        self.min_size = min_size
        self.full_paths = full_paths
        self.files_only = files_only
        self._stop_requested = False
    
    def request_stop(self):
        """請求停止分析"""
        self._stop_requested = True
    
    def run(self):
        """執行分析"""
        try:
            if self._stop_requested:
                self.analysis_completed.emit("", "分析已取消", False)
                return
                
            self.analysis_started.emit()
            
            # 定義進度回調函數，支援停止檢查
            def progress_callback(message):
                if self._stop_requested:
                    return False  # 返回 False 表示請求停止
                self.analysis_progress.emit(message)
                return True  # 返回 True 表示繼續
            
            # 執行實際分析，使用真實的進度回調
            html_output, html_error = self.model.execute_dust_command(
                self.target_path, self.max_depth, self.sort_reverse, 
                self.number_of_lines, self.file_types, self.exclude_patterns, 
                self.show_apparent_size, self.min_size, self.full_paths, 
                self.files_only, progress_callback=progress_callback
            )
            
            if self._stop_requested:
                self.analysis_completed.emit("", "分析已取消", False)
                return
            
            success = bool(html_output) or not bool(html_error)
            self.analysis_completed.emit(html_output or "", html_error or "", success)
            
        except Exception as e:
            logger.error(f"Analysis worker error: {e}")
            self.analysis_completed.emit("", f"分析錯誤: {str(e)}", False)


class DustController:
    """dust 工具的控制器"""
    
    def __init__(self, view: DustViewRedesigned, model: DustModel):
        self.view = view
        self.model = model
        self.analysis_worker = None
        self._connect_signals()
    
    def _connect_signals(self):
        """連接信號和槽"""
        # 連接分析按鈕
        self.view.dust_analyze_button.clicked.connect(self._execute_analysis)
        
        # DirectoryButton 的信號已經在 view 中連接
        # 其他控件的信號也可以在這裡連接，例如參數變化時的即時驗證
    
    def _execute_analysis(self):
        """執行磁碟空間分析 - 使用工作線程提供進度反饋"""
        params = self.view.get_analysis_parameters()
        
        target_path = params['target_path']
        max_depth = params['max_depth']
        sort_reverse = params['sort_reverse']
        number_of_lines = params['number_of_lines']
        file_types = params['file_types']
        exclude_patterns = params['exclude_patterns']
        show_apparent_size = params['show_apparent_size']
        min_size = params['min_size']
        full_paths = params['full_paths']
        files_only = params['files_only']

        if not target_path:
            self.view.dust_results_display.set_results("", "請指定要分析的目錄路徑。")
            self.view.set_analysis_completed(False, "需要指定路徑")
            return

        # 停止之前的分析（如果有的話）
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.terminate()
            self.analysis_worker.wait()

        # 設置分析狀態，顯示取消按鈕
        self.view.set_analyze_button_state("取消分析", True)
        self.view.dust_results_display.set_results("準備分析...\n", "")
        
        # 臨時修改按鈕連接，點擊時取消分析
        self.view.dust_analyze_button.clicked.disconnect()
        self.view.dust_analyze_button.clicked.connect(self._cancel_analysis)
        
        # 創建並啟動分析工作線程
        self.analysis_worker = DustAnalysisWorker(
            self.model, target_path, max_depth, sort_reverse, 
            number_of_lines, file_types, exclude_patterns,
            show_apparent_size, min_size, full_paths, files_only
        )
        
        # 連接信號
        self.analysis_worker.analysis_started.connect(self._on_analysis_started)
        self.analysis_worker.analysis_progress.connect(self._on_analysis_progress)
        self.analysis_worker.analysis_completed.connect(self._on_analysis_completed)
        
        # 啟動分析
        self.analysis_worker.start()
        logger.info("Started dust analysis with enhanced progress feedback")
    

    
    def _on_analysis_started(self):
        """分析開始"""
        self.view.dust_results_display.set_results("🔍 開始分析...\n", "")
        logger.debug("Analysis started")
    
    def _on_analysis_progress(self, message: str):
        """分析進度更新"""
        # 直接設置進度訊息，使用 text_widget 顯示
        self.view.dust_results_display.set_results(f"🔍 {message}", "")
        QApplication.processEvents()
        logger.debug(f"Analysis progress: {message}")
    
    def _cancel_analysis(self):
        """取消正在進行的分析"""
        if self.analysis_worker and self.analysis_worker.isRunning():
            logger.info("User cancelled dust analysis")
            
            # 請求工作線程停止
            self.analysis_worker.request_stop()
            
            # 等待工作線程完成或強制終止
            if not self.analysis_worker.wait(5000):  # 等待5秒
                logger.warning("Force terminating dust analysis worker")
                self.analysis_worker.terminate()
                self.analysis_worker.wait()
            
            # 恢復按鈕狀態
            self._restore_button_connection()
            self.view.set_analyze_button_state("開始分析", True)
            self.view.dust_results_display.set_results("❌ 分析已取消\n", "")
            self.view.set_analysis_completed(False, "分析已取消")
    
    def _restore_button_connection(self):
        """恢復分析按鈕的原始連接"""
        self.view.dust_analyze_button.clicked.disconnect()
        self.view.dust_analyze_button.clicked.connect(self._execute_analysis)
    
    def _on_analysis_completed(self, html_output: str, html_error: str, success: bool):
        """分析完成"""
        # 恢復按鈕連接
        self._restore_button_connection()
        self.view.set_analyze_button_state("開始分析", True)
        
        # 設置分析結果
        result_count = 0
        if html_output or html_error:
            self.view.dust_results_display.set_results(html_output, html_error)
            # 統計結果數量
            result_count = html_output.count('\n') if html_output else 0
            status_message = f"✅ 找到 {result_count} 個結果" if success else "❌ 分析出現錯誤"
            self.view.set_analysis_completed(success, status_message)
        else:
            self.view.dust_results_display.set_results("", "❌ 未找到結果或命令執行失敗。")
            self.view.set_analysis_completed(False, "未找到結果")
            
        logger.info(f"Analysis completed: success={success}, results={result_count}")
    
    def cleanup(self):
        """清理資源"""
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.terminate()
            self.analysis_worker.wait()
            
    # DirectoryButton 的 _browse_folder 方法已由 DirectoryButton 組件替代