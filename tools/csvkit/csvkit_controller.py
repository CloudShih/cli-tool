"""
csvkit 控制器類 - 連接視圖和模型，處理用戶交互
協調 CSV 工具套件的各種操作和數據流
"""

import logging
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import ansi2html

from .csvkit_model import CsvkitModel
from .csvkit_view import CsvkitView

logger = logging.getLogger(__name__)


class CsvkitWorker(QThread):
    """csvkit 工作線程 - 處理耗時的命令執行"""
    
    finished = pyqtSignal(str, str, int)  # stdout, stderr, returncode
    status_update = pyqtSignal(str)
    
    def __init__(self, model, command_type, *args):
        super().__init__()
        self.model = model
        self.command_type = command_type
        self.args = args
        
    def run(self):
        """執行命令"""
        try:
            self.status_update.emit("執行命令中...")
            
            # 根據命令類型調用相應的模型方法
            if self.command_type == 'in2csv':
                result = self.model.execute_in2csv(*self.args)
            elif self.command_type == 'csvcut':
                result = self.model.execute_csvcut(*self.args)
            elif self.command_type == 'csvgrep':
                result = self.model.execute_csvgrep(*self.args)
            elif self.command_type == 'csvstat':
                result = self.model.execute_csvstat(*self.args)
            elif self.command_type == 'csvlook':
                result = self.model.execute_csvlook(*self.args)
            elif self.command_type == 'csvjson':
                result = self.model.execute_csvjson(*self.args)
            elif self.command_type == 'csvsql':
                result = self.model.execute_csvsql(*self.args)
            elif self.command_type == 'csvjoin':
                result = self.model.execute_csvjoin(*self.args)
            elif self.command_type == 'custom':
                result = self.model.execute_custom_command(*self.args)
            elif self.command_type == 'help':
                result = self.model.get_tool_help(*self.args)
            else:
                result = ("", f"Unknown command type: {self.command_type}", 1)
            
            self.finished.emit(*result)
            
        except Exception as e:
            logger.error(f"Error in worker thread: {e}")
            self.finished.emit("", str(e), 1)


class CsvkitController(QObject):
    """csvkit 控制器類 - 協調視圖和模型的交互"""
    
    def __init__(self, model=None, view=None):
        super().__init__()
        self.model = model if model is not None else CsvkitModel()
        self.view = view if view is not None else CsvkitView()
        self.worker = None
        
        self._connect_signals()
        self._initialize_view()
        
    def _connect_signals(self):
        """連接視圖信號到控制器方法"""
        # 連接視圖信號
        self.view.execute_in2csv.connect(self.handle_in2csv)
        self.view.execute_csvcut.connect(self.handle_csvcut)
        self.view.execute_csvgrep.connect(self.handle_csvgrep)
        self.view.execute_csvstat.connect(self.handle_csvstat)
        self.view.execute_csvlook.connect(self.handle_csvlook)
        self.view.execute_csvjson.connect(self.handle_csvjson)
        self.view.execute_csvsql.connect(self.handle_csvsql)
        self.view.execute_csvjoin.connect(self.handle_csvjoin)
        self.view.execute_custom.connect(self.handle_custom_command)
        self.view.get_tool_help.connect(self.handle_tool_help)
        self.view.save_result.connect(self.handle_save_result)
        
    def _initialize_view(self):
        """初始化視圖"""
        # 更新可用工具列表
        self.view.update_available_tools(self.model.available_tools)
        
        # 檢查 csvkit 可用性
        if not self.model.csvkit_available:
            self.view.set_status("csvkit 無法使用 - 請安裝 csvkit: pip install csvkit")
            self.view.display_system_response("csvkit 未安裝或不在 PATH 中。請使用以下命令安裝: pip install csvkit", is_error=True)
            self.view.display_result("歡迎使用 csvkit！\n\n請安裝 csvkit 以使用 CSV 處理工具。\n\n安裝方法: pip install csvkit")
        else:
            self.view.set_status(f"準備就緒 - {len(self.model.available_tools)} 個工具可用")
            self.view.display_system_response(f"準備就緒 - {len(self.model.available_tools)} 個工具可用", is_error=False)
            
            # 顯示可用工具信息到右側輸出面板
            categories = self.model.get_tool_categories()
            info_text = "可用的 csvkit 工具：\n\n"
            
            for category, tools in categories.items():
                if tools:
                    info_text += f"{category}：\n"
                    for tool, description in tools.items():
                        info_text += f"  • {tool}: {description}\n"
                    info_text += "\n"
            
            info_text += "選擇工具標籤頁並配置參數以開始使用。"
            self.view.display_result(info_text)
    
    def handle_in2csv(self, file_path, format_type, sheet, encoding, extra_args):
        """處理 in2csv 命令"""
        if not self._validate_file(file_path):
            return
            
        logger.info(f"Executing in2csv: {file_path}")
        self._execute_command('in2csv', file_path, format_type, sheet, encoding, extra_args)
    
    def handle_csvcut(self, file_path, columns, exclude_columns, names_only, extra_args):
        """處理 csvcut 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvcut: {file_path}")
        self._execute_command('csvcut', file_path, columns, exclude_columns, names_only, extra_args)
    
    def handle_csvgrep(self, file_path, pattern, column, regex, invert_match, extra_args):
        """處理 csvgrep 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvgrep: {file_path}")
        self._execute_command('csvgrep', file_path, pattern, column, regex, invert_match, extra_args)
    
    def handle_csvstat(self, file_path, columns, statistics, no_inference, extra_args):
        """處理 csvstat 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvstat: {file_path}")
        self._execute_command('csvstat', file_path, columns, statistics, no_inference, extra_args)
    
    def handle_csvlook(self, file_path, max_rows, max_columns, max_column_width, extra_args):
        """處理 csvlook 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvlook: {file_path}")
        self._execute_command('csvlook', file_path, max_rows, max_columns, max_column_width, extra_args)
    
    def handle_csvjson(self, file_path, indent, key_column, pretty, extra_args):
        """處理 csvjson 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvjson: {file_path}")
        self._execute_command('csvjson', file_path, indent, key_column, pretty, extra_args)
    
    def handle_csvsql(self, file_path, query, create_table, database_url, extra_args):
        """處理 csvsql 命令"""
        if not self._validate_csv_file(file_path):
            return
            
        logger.info(f"Executing csvsql: {file_path}")
        self._execute_command('csvsql', file_path, query, create_table, database_url, extra_args)
    
    def handle_csvjoin(self, left_file, right_file, left_column, right_column, join_type, extra_args):
        """處理 csvjoin 命令"""
        if not self._validate_csv_file(left_file) or not self._validate_csv_file(right_file):
            return
            
        logger.info(f"Executing csvjoin: {left_file} + {right_file}")
        self._execute_command('csvjoin', left_file, right_file, left_column, right_column, join_type, extra_args)
    
    def handle_custom_command(self, tool, args):
        """處理自定義命令"""
        logger.info(f"Executing custom command: {tool} {' '.join(args)}")
        self._execute_command('custom', tool, args)
    
    def handle_tool_help(self, tool):
        """處理工具幫助請求"""
        logger.info(f"Getting help for tool: {tool}")
        self._execute_command('help', tool)
    
    def handle_save_result(self, content, file_type):
        """處理保存結果請求"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            logger.info(f"Saving result to {file_type} file")
            success, message = self.model.save_result_to_file(content, file_type=file_type)
            
            if success:
                QMessageBox.information(
                    self.view, 
                    "保存成功", 
                    f"檔案已成功保存到:\n{message}"
                )
                logger.info(f"File saved successfully: {message}")
            else:
                QMessageBox.warning(
                    self.view,
                    "保存失敗", 
                    f"檔案保存失敗:\n{message}"
                )
                logger.error(f"File save failed: {message}")
                
        except Exception as e:
            logger.error(f"Error in handle_save_result: {e}")
            QMessageBox.critical(
                self.view,
                "錯誤",
                f"保存檔案時發生錯誤:\n{str(e)}"
            )
    
    def _execute_command(self, command_type, *args):
        """執行命令（在工作線程中）"""
        if self.worker and self.worker.isRunning():
            self.view.set_status("另一個命令正在執行中...")
            self.view.display_system_response("另一個命令正在執行中，請稍候...", is_error=True)
            return
        
        # 禁用按鈕並顯示進度
        self.view.set_buttons_enabled(False)
        self.view.show_progress(True)
        self.view.set_status("執行命令中...")
        self.view.display_system_response("執行命令中...", is_error=False)
        
        # 創建並啟動工作線程
        self.worker = CsvkitWorker(self.model, command_type, *args)
        self.worker.finished.connect(self._on_command_finished)
        self.worker.status_update.connect(self.view.set_status)
        self.worker.start()
    
    def _on_command_finished(self, stdout, stderr, returncode):
        """命令執行完成的回調"""
        # 重新啟用按鈕
        self.view.set_buttons_enabled(True)
        self.view.show_progress(False)
        
        if returncode == 0:
            self.view.set_status("命令執行成功")
            
            # 處理輸出格式
            if stdout:
                # 檢查是否需要 HTML 轉換
                # 只有包含 ANSI 顏色代碼或特殊格式的輸出才轉換為 HTML
                needs_html_conversion = (
                    '\x1b[' in stdout or  # ANSI escape sequences
                    '│' in stdout or      # Table borders from csvlook
                    '─' in stdout or      # Table borders
                    '┌' in stdout or      # Table borders
                    '└' in stdout         # Table borders
                )
                
                if needs_html_conversion:
                    try:
                        html_output = ansi2html.Ansi2HTMLConverter().convert(stdout)
                        self.view.display_result(html_output)
                    except:
                        # 如果轉換失敗，使用純文本
                        self.view.display_result(stdout)
                else:
                    # 對於純 CSV 輸出等，直接使用純文本
                    self.view.display_result(stdout)
            else:
                self.view.display_result("命令執行完成，但無輸出內容。")
                
        else:
            self.view.set_status("命令執行失敗")
            error_msg = stderr if stderr else "命令執行失敗，沒有錯誤訊息"
            self.view.display_result("", error_msg)
        
        # 更新應用程序界面
        QApplication.processEvents()
    
    def _validate_file(self, file_path):
        """驗證文件是否存在"""
        if not file_path or not file_path.strip():
            self.view.display_system_response("請指定檔案路徑", is_error=True)
            return False
            
        from pathlib import Path
        if not Path(file_path).exists():
            self.view.display_system_response(f"找不到檔案: {file_path}", is_error=True)
            return False
            
        return True
    
    def _validate_csv_file(self, file_path):
        """驗證 CSV 文件"""
        if not self._validate_file(file_path):
            return False
            
        if not self.model.validate_csv_file(file_path):
            self.view.display_system_response(f"無效的 CSV 檔案: {file_path}", is_error=True)
            return False
            
        return True
    
    def get_view(self):
        """獲取視圖對象"""
        return self.view
    
    def cleanup(self):
        """清理資源"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        logger.info("csvkit controller cleanup completed")