"""
Pandoc 文檔轉換工具的控制器
連接視圖和模型，處理用戶操作邏輯
"""

import os
import logging
from pathlib import Path
from typing import List, Dict
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class ConversionWorker(QThread):
    """後台轉換工作線程"""
    
    conversion_finished = pyqtSignal(bool, str, str)  # 成功標誌, 輸出, 錯誤
    batch_finished = pyqtSignal(list)  # 批量轉換結果
    
    def __init__(self, model, conversion_type="single", **kwargs):
        super().__init__()
        self.model = model
        self.conversion_type = conversion_type
        self.params = kwargs
    
    def run(self):
        """執行轉換任務"""
        try:
            if self.conversion_type == "single":
                self._run_single_conversion()
            elif self.conversion_type == "batch":
                self._run_batch_conversion()
        except Exception as e:
            logger.error(f"Conversion worker error: {e}")
            self.conversion_finished.emit(False, "", str(e))
    
    def _run_single_conversion(self):
        """執行單個轉換"""
        input_file = self.params.get('input_file')
        output_dir = self.params.get('output_dir')
        output_format = self.params.get('output_format', 'html')
        
        # 生成輸出檔案名
        input_path = Path(input_file)
        output_filename = input_path.stem + self.model._get_extension_for_format(output_format)
        output_file = os.path.join(output_dir, output_filename)
        
        # 執行轉換
        success, stdout, stderr = self.model.convert_document(
            input_file=input_file,
            output_file=output_file,
            input_format=self.params.get('input_format'),
            output_format=output_format,
            standalone=self.params.get('standalone', True),
            template=self.params.get('template'),
            css_file=self.params.get('css_file'),
            metadata=self.params.get('metadata', {}),
        )
        
        self.conversion_finished.emit(success, stdout, stderr)
    
    def _run_batch_conversion(self):
        """執行批量轉換"""
        input_files = self.params.get('input_files', [])
        
        results = self.model.batch_convert(
            input_files=input_files,
            output_dir=self.params.get('output_dir'),
            input_format=self.params.get('input_format'),
            output_format=self.params.get('output_format', 'html'),
            standalone=self.params.get('standalone', True),
            template=self.params.get('template'),
            css_file=self.params.get('css_file'),
            metadata=self.params.get('metadata', {}),
        )
        
        self.batch_finished.emit(results)


class PandocController(QObject):
    """Pandoc 工具的控制器"""
    
    def __init__(self, view, model):
        super().__init__()
        self.view = view
        self.model = model
        self.worker = None
        self._connect_signals()
        self._initialize_formats()
        self._check_pandoc_on_startup()
    
    def _connect_signals(self):
        """連接視圖信號到控制器方法"""
        # 視圖信號連接
        self.view.convert_requested.connect(self._handle_single_conversion)
        self.view.batch_convert_requested.connect(self._handle_batch_conversion)
        self.view.check_pandoc_requested.connect(self._check_pandoc_availability)
    
    def _initialize_formats(self):
        """初始化支援的格式"""
        try:
            input_formats, output_formats = self.model.get_supported_formats()
            self.view.populate_formats(input_formats, output_formats)
            logger.info("Initialized pandoc format options")
        except Exception as e:
            logger.error(f"Failed to initialize formats: {e}")
    
    def _check_pandoc_on_startup(self):
        """啟動時檢查 pandoc 可用性"""
        QTimer.singleShot(1000, self._check_pandoc_availability)  # 延遲檢查
    
    def _check_pandoc_availability(self):
        """檢查 pandoc 工具可用性"""
        try:
            available, message = self.model.check_pandoc_availability()
            
            if available:
                self.view.update_status("ready", f"Pandoc 已就緒: {message}")
                self.view.update_output_display(
                    f"<p style='color: green;'>✓ {message}</p>"
                )
                logger.info(f"Pandoc available: {message}")
            else:
                self.view.update_status("error", "Pandoc 不可用")
                self.view.update_output_display(
                    f"<p style='color: red;'>✗ Pandoc 不可用: {message}</p>"
                    f"<p>請確保已安裝 Pandoc 並添加到系統 PATH 環境變數中。</p>"
                    f"<p>下載地址: <a href='https://pandoc.org/installing.html'>https://pandoc.org/installing.html</a></p>"
                )
                logger.warning(f"Pandoc not available: {message}")
                
                # 顯示安裝提示對話框
                self._show_pandoc_installation_dialog(message)
                
        except Exception as e:
            error_msg = f"檢查 Pandoc 時發生錯誤: {str(e)}"
            self.view.update_status("error", error_msg)
            logger.error(error_msg)
    
    def _show_pandoc_installation_dialog(self, error_message: str):
        """顯示 Pandoc 安裝提示對話框"""
        msg_box = QMessageBox(self.view)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Pandoc 未安裝")
        msg_box.setText("未找到 Pandoc 工具")
        msg_box.setInformativeText(
            f"錯誤詳情: {error_message}\n\n"
            "Pandoc 是一個強大的文檔轉換工具，支援 50+ 種格式互相轉換。\n"
            "請安裝 Pandoc 後重新檢查。\n\n"
            "安裝方法:\n"
            "• Windows: 從官網下載安裝包\n"
            "• macOS: brew install pandoc\n"
            "• Linux: apt-get install pandoc 或 yum install pandoc"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def _handle_single_conversion(self, params: dict):
        """處理單個轉換請求"""
        if self._is_conversion_running():
            return
        
        try:
            self.view.show_conversion_progress(True)
            self.view.update_status("processing", "正在轉換文檔...")
            
            # 啟動後台轉換線程
            self.worker = ConversionWorker(
                self.model,
                conversion_type="single",
                **params
            )
            self.worker.conversion_finished.connect(self._on_conversion_finished)
            self.worker.start()
            
            logger.info(f"Started single document conversion: {params.get('input_file')}")
            
        except Exception as e:
            self._handle_conversion_error(f"啟動轉換時發生錯誤: {str(e)}")
    
    def _handle_batch_conversion(self, input_files: List[str], params: dict):
        """處理批量轉換請求"""
        if self._is_conversion_running():
            return
        
        try:
            self.view.show_conversion_progress(True)
            self.view.update_status("processing", f"正在批量轉換 {len(input_files)} 個檔案...")
            
            # 啟動後台批量轉換線程
            params['input_files'] = input_files
            self.worker = ConversionWorker(
                self.model,
                conversion_type="batch",
                **params
            )
            self.worker.batch_finished.connect(self._on_batch_conversion_finished)
            self.worker.start()
            
            logger.info(f"Started batch conversion for {len(input_files)} files")
            
        except Exception as e:
            self._handle_conversion_error(f"啟動批量轉換時發生錯誤: {str(e)}")
    
    def _on_conversion_finished(self, success: bool, stdout: str, stderr: str):
        """處理單個轉換完成"""
        try:
            self.view.show_conversion_progress(False)
            
            if success:
                self.view.update_status("success", "轉換完成")
                output_html = self.model.format_output_for_display(stdout)
                self.view.update_output_display(
                    f"<h3 style='color: green;'>✓ 轉換成功</h3>{output_html}"
                )
                logger.info("Document conversion completed successfully")
            else:
                self.view.update_status("error", "轉換失敗")
                error_html = self.model.format_output_for_display(stderr)
                self.view.update_output_display(
                    f"<h3 style='color: red;'>✗ 轉換失敗</h3>{error_html}"
                )
                logger.error(f"Document conversion failed: {stderr}")
                
        except Exception as e:
            logger.error(f"Error handling conversion result: {e}")
        finally:
            if self.worker:
                self.worker.deleteLater()
                self.worker = None
    
    def _on_batch_conversion_finished(self, results: List[tuple]):
        """處理批量轉換完成"""
        try:
            self.view.show_conversion_progress(False)
            
            # 統計結果
            total_files = len(results)
            successful_files = sum(1 for _, success, _ in results if success)
            failed_files = total_files - successful_files
            
            if failed_files == 0:
                self.view.update_status("success", f"批量轉換完成: {total_files}/{total_files} 成功")
                self.view.update_output_display(
                    f"<h3 style='color: green;'>✓ 批量轉換完成</h3>"
                    f"<p>成功轉換 {successful_files} 個檔案</p>"
                )
            else:
                self.view.update_status("warning", f"批量轉換完成: {successful_files}/{total_files} 成功")
                self.view.update_output_display(
                    f"<h3 style='color: orange;'>⚠ 批量轉換完成 (部分失敗)</h3>"
                    f"<p>成功: {successful_files} 個檔案</p>"
                    f"<p>失敗: {failed_files} 個檔案</p>"
                    f"<p>詳細結果請查看「批量結果」標籤頁</p>"
                )
            
            # 更新批量結果顯示
            self.view.update_batch_results_display(results)
            
            logger.info(f"Batch conversion completed: {successful_files}/{total_files} successful")
            
        except Exception as e:
            logger.error(f"Error handling batch conversion result: {e}")
        finally:
            if self.worker:
                self.worker.deleteLater()
                self.worker = None
    
    def _handle_conversion_error(self, error_message: str):
        """處理轉換錯誤"""
        self.view.show_conversion_progress(False)
        self.view.update_status("error", "轉換失敗")
        self.view.update_output_display(
            f"<h3 style='color: red;'>✗ 轉換錯誤</h3>"
            f"<p>{error_message}</p>"
        )
        logger.error(error_message)
        
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def _is_conversion_running(self) -> bool:
        """檢查是否有轉換正在進行"""
        if self.worker and self.worker.isRunning():
            QMessageBox.information(
                self.view,
                "轉換進行中",
                "已有轉換任務正在進行中，請等待完成後再開始新的轉換。"
            )
            return True
        return False
    
    def cleanup(self):
        """清理資源"""
        try:
            if self.worker and self.worker.isRunning():
                self.worker.quit()
                self.worker.wait()
                
            logger.info("Pandoc controller cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during pandoc controller cleanup: {e}")