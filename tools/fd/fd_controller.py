from PyQt5.QtWidgets import QFileDialog, QApplication
from tools.fd.fd_model import FdModel
from tools.fd.fd_view import FdView

class FdController:
    def __init__(self, view: FdView, model: FdModel):
        self.view = view
        self.model = model
        self._connect_signals()

    def _connect_signals(self):
        self.view.fd_search_button.clicked.connect(self._execute_search)
        self.view.fd_browse_button.clicked.connect(self._browse_folder)

    def _execute_search(self):
        pattern = self.view.fd_pattern_input.text().strip()
        path = self.view.fd_path_input.text().strip()
        extension = self.view.fd_extension_input.text().strip()
        search_type_index = self.view.fd_type_combobox.currentIndex()
        hidden = self.view.fd_hidden_checkbox.isChecked()
        case_sensitive = self.view.fd_case_sensitive_checkbox.isChecked()

        if not pattern and not extension:
            self.view.fd_results_display.setText("Please enter a search pattern or a file extension.")
            return

        # Set button to waiting state
        self.view.set_search_button_state("wait...", False, "#F5F5DC", "black")
        QApplication.processEvents() # Force UI update

        self.view.fd_results_display.setText(f"Running command...\n")
        
        html_output, html_error = self.model.execute_fd_command(
            pattern, path, extension, search_type_index, hidden, case_sensitive
        )

        if html_output:
            self.view.fd_results_display.append("--- Results ---")
            self.view.fd_results_display.append(html_output)
        if html_error:
            self.view.fd_results_display.append("--- Error ---")
            self.view.fd_results_display.append(html_error)
        if not html_output and not html_error:
            self.view.fd_results_display.append("No results found or command failed silently.")

        # Restore button to original state
        self.view.set_search_button_state("Search", True, "#555555", "#f0f0f0")

    def _browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self.view, "選擇資料夾", self.view.fd_path_input.text())
        if folder_path:
            self.view.fd_path_input.setText(folder_path)
