import os
import tempfile
import shutil
from PyQt5.QtWidgets import QFileDialog
from tools.poppler.poppler_model import PopplerModel
from tools.poppler.poppler_view import PopplerView

class PopplerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self._connect_signals()

    def _connect_signals(self):
        # PDF Info Signals
        self.view.pdfinfo_browse_button.clicked.connect(self.select_info_pdf_path)
        self.view.pdfinfo_get_info_button.clicked.connect(self.execute_info)

        # PDF to Text Signals
        self.view.pdftotext_browse_pdf_button.clicked.connect(self.select_text_pdf_path)
        self.view.pdftotext_browse_output_button.clicked.connect(self.select_text_output_path)
        self.view.pdftotext_convert_button.clicked.connect(self.execute_text_conversion)

        # PDF Images Signals
        self.view.pdfimages_browse_pdf_button.clicked.connect(self.select_images_pdf_path)
        self.view.pdfimages_browse_output_dir_button.clicked.connect(self.select_images_output_dir)
        self.view.pdfimages_extract_button.clicked.connect(self.execute_image_extraction)

        # PDF Separate Signals
        self.view.pdfseparate_browse_pdf_button.clicked.connect(self.select_separate_pdf_path)
        self.view.pdfseparate_browse_output_button.clicked.connect(self.select_separate_output_directory)
        self.view.pdfseparate_separate_button.clicked.connect(self.execute_separation)

        # PDF Unite Signals
        self.view.pdfunite_add_button.clicked.connect(self.add_pdfs_to_unite_list)
        self.view.pdfunite_remove_button.clicked.connect(self.remove_selected_pdf_from_unite_list)
        self.view.pdfunite_move_up_button.clicked.connect(self.move_selected_pdf_up_in_unite_list)
        self.view.pdfunite_move_down_button.clicked.connect(self.move_selected_pdf_down_in_unite_list)
        self.view.pdfunite_browse_output_button.clicked.connect(self.select_unite_output_path)
        self.view.pdfunite_unite_button.clicked.connect(self.execute_unite)
        self.view.pdfunite_file_list.itemSelectionChanged.connect(self.update_unite_button_states)

        # PDF to PPM Signals
        self.view.pdftoppm_browse_pdf_button.clicked.connect(self.select_pdftoppm_pdf_path)
        self.view.pdftoppm_browse_output_button.clicked.connect(self.select_pdftoppm_output_directory)
        self.view.pdftoppm_convert_button.clicked.connect(self.execute_pdftoppm)

        

        

    def add_pdfs_to_unite_list(self):
        paths, _ = QFileDialog.getOpenFileNames(self.view, "Select PDF Files to Add", "", "PDF Files (*.pdf)")
        if paths:
            for path in paths:
                self.view.pdfunite_file_list.addItem(path)
            self.update_unite_button_states()

    def remove_selected_pdf_from_unite_list(self):
        selected_items = self.view.pdfunite_file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.view.pdfunite_file_list.takeItem(self.view.pdfunite_file_list.row(item))
        self.update_unite_button_states()

    def move_selected_pdf_up_in_unite_list(self):
        selected_items = self.view.pdfunite_file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.view.pdfunite_file_list.row(item)
            if row > 0:
                self.view.pdfunite_file_list.takeItem(row)
                self.view.pdfunite_file_list.insertItem(row - 1, item)
                self.view.pdfunite_file_list.setCurrentItem(item)

    def move_selected_pdf_down_in_unite_list(self):
        selected_items = self.view.pdfunite_file_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.view.pdfunite_file_list.row(item)
            if row < self.view.pdfunite_file_list.count() - 1:
                self.view.pdfunite_file_list.takeItem(row)
                self.view.pdfunite_file_list.insertItem(row + 1, item)
                self.view.pdfunite_file_list.setCurrentItem(item)

    def select_unite_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self.view, "Select Output PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdfunite_output_path_input.setText(path)
        self.update_unite_button_states()

    def execute_unite(self):
        input_paths = [self.view.pdfunite_file_list.item(i).text() for i in range(self.view.pdfunite_file_list.count())]
        output_path = self.view.pdfunite_output_path_input.text()

        if not input_paths or not output_path:
            self.view.pdfunite_results_display.setText("錯誤：請至少新增兩個 PDF 檔案並指定輸出路徑。")
            return

        temp_dir = tempfile.mkdtemp()
        decrypted_paths = []
        try:
            self.view.pdfunite_results_display.setText("正在解密檔案中，請稍候...")
            for i, path in enumerate(input_paths):
                decrypted_path = os.path.join(temp_dir, f"decrypted_{i}.pdf")
                _, stderr = self.model.decrypt_pdf(path, decrypted_path)
                if stderr and "failed to decrypt" in stderr.lower():
                    # If decryption fails, it might not be encrypted, so use original
                    shutil.copy(path, decrypted_path)
                decrypted_paths.append(decrypted_path)
            
            self.view.pdfunite_results_display.setText("解密完成，正在合併檔案...")
            stdout, stderr = self.model.unite_pdfs(decrypted_paths, output_path)
            if stderr:
                self.view.pdfunite_results_display.setText(f"錯誤：\n{stderr}")
            else:
                self.view.pdfunite_results_display.setText(f"成功！合併後的檔案已儲存至：\n{output_path}")

        except Exception as e:
            self.view.pdfunite_results_display.setText(f"發生預期外的錯誤：{e}")
        finally:
            shutil.rmtree(temp_dir) # Clean up the temporary directory

    # --- Handlers for PDF Info ---
    def select_info_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdfinfo_path_input.setText(path)

    def execute_info(self):
        pdf_path = self.view.pdfinfo_path_input.text()
        if not pdf_path:
            self.view.pdfinfo_results_display.setText("錯誤：請選擇一個 PDF 檔案。")
            return
        stdout, stderr = self.model.get_pdf_info(pdf_path)
        if stderr:
            self.view.pdfinfo_results_display.setText(f"錯誤：\n{stderr}")
        else:
            self.view.pdfinfo_results_display.setText(stdout)

    # --- Handlers for PDF to Text ---
    def select_text_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdftotext_pdf_path_input.setText(path)

    def select_text_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self.view, "Select Output Text File", "", "Text Files (*.txt)")
        if path:
            self.view.pdftotext_output_path_input.setText(path)

    def execute_text_conversion(self):
        pdf_path = self.view.pdftotext_pdf_path_input.text()
        output_path = self.view.pdftotext_output_path_input.text()
        if not pdf_path or not output_path:
            self.view.pdftotext_results_display.setText("錯誤：請選擇 PDF 檔案和輸出路徑。")
            return
        _, stderr = self.model.convert_pdf_to_text(pdf_path, output_path)
        if stderr:
            self.view.pdftotext_results_display.setText(f"錯誤：\n{stderr}")
        else:
            self.view.pdftotext_results_display.setText(f"成功！文字已儲存至：\n{output_path}")

    # --- Handlers for PDF Images ---
    def select_images_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdfimages_pdf_path_input.setText(path)

    def select_images_output_dir(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdfimages_output_dir_input.setText(path)

    def execute_image_extraction(self):
        pdf_path = self.view.pdfimages_pdf_path_input.text()
        output_dir = self.view.pdfimages_output_dir_input.text()
        prefix = self.view.pdfimages_file_prefix_input.text()
        img_format = self.view.pdfimages_format_combobox.currentText()
        if not pdf_path or not output_dir:
            self.view.pdfimages_results_display.setText("錯誤：請選擇 PDF 檔案和輸出目錄。")
            return
        _, stderr = self.model.extract_pdf_images(pdf_path, output_dir, prefix, img_format)
        if stderr:
            self.view.pdfimages_results_display.setText(f"錯誤：\n{stderr}")
        else:
            self.view.pdfimages_results_display.setText(f"成功！圖片已儲存至：\n{output_dir}")

    # --- Handlers for PDF Separate ---
    def select_separate_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdfseparate_pdf_path_input.setText(path)

    def select_separate_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdfseparate_output_dir_input.setText(path)

    def execute_separation(self):
        pdf_path = self.view.pdfseparate_pdf_path_input.text()
        output_dir = self.view.pdfseparate_output_dir_input.text()

        if not pdf_path or not output_dir:
            self.view.pdfseparate_results_display.setText("Error: Please select a PDF file and an output directory.")
            return

        # Automatically create the output prefix
        base_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_prefix = os.path.join(output_dir, f"{name_without_ext}-%d.pdf")

        try:
            stdout, stderr = self.model.separate_pdf_pages(pdf_path, output_prefix)
            if stderr:
                self.view.pdfseparate_results_display.setText(f"Error:\n{stderr}")
            else:
                self.view.pdfseparate_results_display.setText(f"Success:\n{stdout}")
        except Exception as e:
            self.view.pdfseparate_results_display.setText(f"An unexpected error occurred: {e}")

    # --- Handlers for PDF to PPM ---
    def select_pdftoppm_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdftoppm_pdf_path_input.setText(path)

    def select_pdftoppm_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdftoppm_output_dir_input.setText(path)

    def execute_pdftoppm(self):
        pdf_path = self.view.pdftoppm_pdf_path_input.text()
        output_dir = self.view.pdftoppm_output_dir_input.text()
        file_prefix = self.view.pdftoppm_file_prefix_input.text()
        img_format = self.view.pdftoppm_format_combobox.currentText()
        start_page = self.view.pdftoppm_start_page_input.text()
        end_page = self.view.pdftoppm_end_page_input.text()

        if not pdf_path or not output_dir or not file_prefix:
            self.view.pdftoppm_results_display.setText("錯誤：請選擇 PDF 檔案、輸出目錄和檔案前綴。")
            return

        output_prefix = os.path.join(output_dir, file_prefix)

        try:
            stdout, stderr = self.model.convert_pdf_to_ppm(pdf_path, output_prefix, img_format, start_page, end_page)
            if stderr:
                self.view.pdftoppm_results_display.setText(f"錯誤：\n{stderr}")
            else:
                self.view.pdftoppm_results_display.setText(f"成功！圖片已儲存至：\n{output_dir}")
        except Exception as e:
            self.view.pdftoppm_results_display.setText(f"發生預期外的錯誤：{e}")

    # --- Handlers for PDF to HTML ---
    def select_pdftohtml_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdftohtml_pdf_path_input.setText(path)

    def select_pdftohtml_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdftohtml_output_dir_input.setText(path)

    def execute_pdftohtml(self):
        pdf_path = self.view.pdftohtml_pdf_path_input.text()
        output_dir = self.view.pdftohtml_output_dir_input.text()
        file_prefix = self.view.pdftohtml_file_prefix_input.text()
        start_page = self.view.pdftohtml_start_page_input.text()
        end_page = self.view.pdftohtml_end_page_input.text()
        single_file = self.view.pdftohtml_single_file_checkbox.isChecked()
        include_images = self.view.pdftohtml_include_images_checkbox.isChecked()

        if not pdf_path or not output_dir or not file_prefix:
            self.view.pdftohtml_results_display.setText("錯誤：請選擇 PDF 檔案、輸出目錄和檔案前綴。")
            return

        output_path = os.path.join(output_dir, file_prefix)

        try:
            stdout, stderr = self.model.convert_pdf_to_html(pdf_path, output_path, start_page, end_page, single_file, include_images)
            if stderr:
                self.view.pdftohtml_results_display.setText(f"錯誤：\n{stderr}")
            else:
                self.view.pdftohtml_results_display.setText(f"成功！HTML 已儲存至：\n{output_dir}")
        except Exception as e:
            self.view.pdftohtml_results_display.setText(f"發生預期外的錯誤：{e}")

    # --- Handlers for PDF to HTML ---
    def select_pdftohtml_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdftohtml_pdf_path_input.setText(path)

    def select_pdftohtml_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdftohtml_output_dir_input.setText(path)

    def execute_pdftohtml(self):
        pdf_path = self.view.pdftohtml_pdf_path_input.text()
        output_dir = self.view.pdftohtml_output_dir_input.text()
        file_prefix = self.view.pdftohtml_file_prefix_input.text()
        start_page = self.view.pdftohtml_start_page_input.text()
        end_page = self.view.pdftohtml_end_page_input.text()
        single_file = self.view.pdftohtml_single_file_checkbox.isChecked()
        include_images = self.view.pdftohtml_include_images_checkbox.isChecked()

        if not pdf_path or not output_dir or not file_prefix:
            self.view.pdftohtml_results_display.setText("錯誤：請選擇 PDF 檔案、輸出目錄和檔案前綴。")
            return

        output_path = os.path.join(output_dir, file_prefix)

        try:
            stdout, stderr = self.model.convert_pdf_to_html(pdf_path, output_path, start_page, end_page, single_file, include_images)
            if stderr:
                self.view.pdftohtml_results_display.setText(f"錯誤：\n{stderr}")
            else:
                self.view.pdftohtml_results_display.setText(f"成功！HTML 已儲存至：\n{output_dir}")
        except Exception as e:
            self.view.pdftohtml_results_display.setText(f"發生預期外的錯誤：{e}")

    # --- Handlers for PDF to HTML ---
    def select_pdftohtml_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdftohtml_pdf_path_input.setText(path)

    def select_pdftohtml_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdftohtml_output_dir_input.setText(path)

    def execute_pdftohtml(self):
        pdf_path = self.view.pdftohtml_pdf_path_input.text()
        output_dir = self.view.pdftohtml_output_dir_input.text()
        file_prefix = self.view.pdftohtml_file_prefix_input.text()
        start_page = self.view.pdftohtml_start_page_input.text()
        end_page = self.view.pdftohtml_end_page_input.text()
        single_file = self.view.pdftohtml_single_file_checkbox.isChecked()
        include_images = self.view.pdftohtml_include_images_checkbox.isChecked()

        if not pdf_path or not output_dir or not file_prefix:
            self.view.pdftohtml_results_display.setText("錯誤：請選擇 PDF 檔案、輸出目錄和檔案前綴。")
            return

        output_path = os.path.join(output_dir, file_prefix)

        try:
            stdout, stderr = self.model.convert_pdf_to_html(pdf_path, output_path, start_page, end_page, single_file, include_images)
            if stderr:
                self.view.pdftohtml_results_display.setText(f"錯誤：\n{stderr}")
            else:
                self.view.pdftohtml_results_display.setText(f"成功！HTML 已儲存至：\n{output_dir}")
        except Exception as e:
            self.view.pdftohtml_results_display.setText(f"發生預期外的錯誤：{e}")

    def update_unite_button_states(self):
        list_has_items = self.view.pdfunite_file_list.count() > 0
        item_is_selected = len(self.view.pdfunite_file_list.selectedItems()) > 0
        can_unite = self.view.pdfunite_file_list.count() >= 2 and bool(self.view.pdfunite_output_path_input.text())

        self.view.pdfunite_remove_button.setEnabled(item_is_selected)
        self.view.pdfunite_move_up_button.setEnabled(item_is_selected)
        self.view.pdfunite_move_down_button.setEnabled(item_is_selected)
        self.view.pdfunite_unite_button.setEnabled(can_unite)

    

    def select_pdf_path(self):
        path, _ = QFileDialog.getOpenFileName(self.view, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.view.pdfseparate_pdf_path_input.setText(path)

    def select_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select Output Directory")
        if path:
            self.view.pdfseparate_output_dir_input.setText(path)

    def execute_separation(self):
        pdf_path = self.view.pdfseparate_pdf_path_input.text()
        output_dir = self.view.pdfseparate_output_dir_input.text()

        if not pdf_path or not output_dir:
            self.view.pdfseparate_results_display.setText("Error: Please select a PDF file and an output directory.")
            return

        # Automatically create the output prefix
        base_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_prefix = os.path.join(output_dir, f"{name_without_ext}-%d.pdf")

        try:
            stdout, stderr = self.model.separate_pdf_pages(pdf_path, output_prefix)
            if stderr:
                self.view.pdfseparate_results_display.setText(f"Error:\n{stderr}")
            else:
                self.view.pdfseparate_results_display.setText(f"Success:\n{stdout}")
        except Exception as e:
            self.view.pdfseparate_results_display.setText(f"An unexpected error occurred: {e}")