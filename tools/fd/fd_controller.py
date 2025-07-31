from PyQt5.QtWidgets import QApplication
from tools.fd.fd_model import FdModel
from tools.fd.fd_view import FdView

class FdController:
    def __init__(self, view: FdView, model: FdModel):
        self.view = view
        self.model = model
        self._connect_signals()

    def _connect_signals(self):
        self.view.fd_search_button.clicked.connect(self._execute_search)
        # DirectoryButton 的信號已經在 view 中連接

    def _execute_search(self):
        pattern = self.view.fd_pattern_input.text().strip()
        path = self.view.fd_path_input.text().strip()
        extension = self.view.fd_extension_input.text().strip()
        search_type_index = self.view.fd_type_combobox.currentIndex()
        hidden = self.view.fd_hidden_checkbox.isChecked()
        case_sensitive = self.view.fd_case_sensitive_checkbox.isChecked()

        if not pattern and not extension:
            self.view.fd_results_display.setPlainText("請輸入搜尋模式或檔案副檔名。")
            self.view.set_search_completed(False, "需要輸入搜尋條件")
            return

        # Set button to waiting state
        self.view.set_search_button_state("搜尋中...", False)
        QApplication.processEvents() # Force UI update

        self.view.fd_results_display.setPlainText("正在執行搜尋命令...\n")
        
        try:
            html_output, html_error = self.model.execute_fd_command(
                pattern, path, extension, search_type_index, hidden, case_sensitive
            )

            # 清除載入文字
            self.view.fd_results_display.clear()
            
            if html_output:
                self.view.fd_results_display.append("=== 搜尋結果 ===")
                self.view.fd_results_display.append(html_output)
                
            if html_error:
                self.view.fd_results_display.append("\n=== 錯誤訊息 ===")
                self.view.fd_results_display.append(html_error)
                
            if not html_output and not html_error:
                self.view.fd_results_display.append("未找到結果或命令執行失敗。")
                self.view.set_search_completed(False, "未找到結果")
            else:
                # 統計結果數量
                result_count = html_output.count('\n') if html_output else 0
                self.view.set_search_completed(True, f"找到 {result_count} 個結果")
                
        except Exception as e:
            self.view.fd_results_display.setPlainText(f"搜尋過程中發生錯誤: {str(e)}")
            self.view.set_search_completed(False, f"執行錯誤: {str(e)}")

    # _browse_folder 方法已由 DirectoryButton 組件替代
