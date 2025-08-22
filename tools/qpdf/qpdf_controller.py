"""
QPDF 控制器層
連接視圖和模型，處理使用者互動
"""

import os
import glob
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

from .qpdf_model import QPDFModel
from .qpdf_view import QPDFView
from .core.data_models import QPDFOperation, QPDFOperationType, EncryptionLevel, CompressionLevel


class QPDFController:
    """QPDF 控制器類"""
    
    def __init__(self, model: QPDFModel, view: QPDFView):
        self.model = model
        self.view = view
        self._connect_signals()
        self._connect_model_signals()
        self._update_button_states()
    
    def _ensure_pdf_extension(self, file_path: str) -> str:
        """確保檔案路徑有 .pdf 副檔名"""
        if not file_path:
            return file_path
        
        file_path = file_path.strip()
        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
        
        return file_path
    
    def _ensure_pdf_extension_pattern(self, pattern: str) -> str:
        """確保輸出模式有 .pdf 副檔名（用於分割功能）"""
        if not pattern:
            return pattern
        
        pattern = pattern.strip()
        
        # 如果模式不包含 .pdf，則在 %d 前添加 .pdf
        if not pattern.lower().endswith('.pdf') and '%d' in pattern:
            # 將 %d 替換為 .pdf 然後再加回 %d
            pattern = pattern.replace('%d', '') + '-%d.pdf'
        elif not pattern.lower().endswith('.pdf'):
            pattern += '.pdf'
        
        return pattern
    
    def _connect_signals(self):
        """連接視圖信號到控制器方法"""
        
        # Check tab signals
        self.view.check_browse_button.clicked.connect(self.select_check_pdf_path)
        self.view.check_button.clicked.connect(self.execute_check)
        
        # Decrypt tab signals
        self.view.decrypt_browse_input_button.clicked.connect(self.select_decrypt_input_path)
        self.view.decrypt_browse_output_button.clicked.connect(self.select_decrypt_output_path)
        self.view.decrypt_button.clicked.connect(self.execute_decrypt)
        
        # Encrypt tab signals
        self.view.encrypt_browse_input_button.clicked.connect(self.select_encrypt_input_path)
        self.view.encrypt_browse_output_button.clicked.connect(self.select_encrypt_output_path)
        self.view.encrypt_button.clicked.connect(self.execute_encrypt)
        
        # Linearize tab signals
        self.view.linearize_browse_input_button.clicked.connect(self.select_linearize_input_path)
        self.view.linearize_browse_output_button.clicked.connect(self.select_linearize_output_path)
        self.view.linearize_button.clicked.connect(self.execute_linearize)
        
        # Split tab signals
        self.view.split_browse_input_button.clicked.connect(self.select_split_input_path)
        self.view.split_browse_output_button.clicked.connect(self.select_split_output_directory)
        self.view.split_button.clicked.connect(self.execute_split)
        
        # Rotate tab signals
        self.view.rotate_browse_input_button.clicked.connect(self.select_rotate_input_path)
        self.view.rotate_browse_output_button.clicked.connect(self.select_rotate_output_path)
        self.view.rotate_button.clicked.connect(self.execute_rotate)
        
        # Compress tab signals
        self.view.compress_browse_input_button.clicked.connect(self.select_compress_input_path)
        self.view.compress_browse_output_button.clicked.connect(self.select_compress_output_path)
        self.view.compress_button.clicked.connect(self.execute_compress)
        
        # Repair tab signals
        self.view.repair_browse_input_button.clicked.connect(self.select_repair_input_path)
        self.view.repair_browse_output_button.clicked.connect(self.select_repair_output_path)
        self.view.repair_button.clicked.connect(self.execute_repair)
        
        # JSON Info tab signals
        self.view.json_info_browse_input_button.clicked.connect(self.select_json_info_input_path)
        self.view.json_info_button.clicked.connect(self.execute_json_info)
        
        # Batch tab signals
        self.view.batch_add_files_button.clicked.connect(self.add_batch_files)
        self.view.batch_add_folder_button.clicked.connect(self.add_batch_folder)
        self.view.batch_remove_button.clicked.connect(self.remove_batch_files)
        self.view.batch_clear_button.clicked.connect(self.clear_batch_files)
        self.view.batch_browse_output_button.clicked.connect(self.select_batch_output_directory)
        self.view.batch_execute_button.clicked.connect(self.execute_batch)
        self.view.batch_file_list.itemSelectionChanged.connect(self._update_batch_button_states)
    
    def _connect_model_signals(self):
        """連接模型信號到控制器方法"""
        self.model.operation_started.connect(self._on_operation_started)
        self.model.operation_completed.connect(self._on_operation_completed)
        self.model.operation_failed.connect(self._on_operation_failed)
        self.model.progress_updated.connect(self._on_progress_updated)
        self.model.info_updated.connect(self._on_info_updated)
        self.model.batch_progress.connect(self._on_batch_progress)
    
    def _update_button_states(self):
        """更新按鈕狀態"""
        self._update_batch_button_states()
    
    def _update_batch_button_states(self):
        """更新批量操作按鈕狀態"""
        has_files = self.view.batch_file_list.count() > 0
        has_selection = len(self.view.batch_file_list.selectedItems()) > 0
        has_output_dir = bool(self.view.batch_output_dir.text().strip())
        
        self.view.batch_remove_button.setEnabled(has_selection)
        self.view.batch_clear_button.setEnabled(has_files)
        self.view.batch_execute_button.setEnabled(has_files and has_output_dir)
    
    # File selection methods
    def select_check_pdf_path(self):
        """選擇要檢查的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.check_path_input.setText(path)
    
    def select_decrypt_input_path(self):
        """選擇要解密的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要解密的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.decrypt_input_path.setText(path)
    
    def select_decrypt_output_path(self):
        """選擇解密後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.decrypt_output_path.setText(path)
    
    def select_encrypt_input_path(self):
        """選擇要加密的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要加密的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.encrypt_input_path.setText(path)
    
    def select_encrypt_output_path(self):
        """選擇加密後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.encrypt_output_path.setText(path)
    
    def select_linearize_input_path(self):
        """選擇要線性化的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要線性化的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.linearize_input_path.setText(path)
    
    def select_linearize_output_path(self):
        """選擇線性化後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.linearize_output_path.setText(path)
    
    def select_split_input_path(self):
        """選擇要分割的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要分割的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.split_input_path.setText(path)
    
    def select_split_output_directory(self):
        """選擇分割後的輸出目錄"""
        path = QFileDialog.getExistingDirectory(self.view, "選擇輸出目錄")
        if path:
            # 自動生成輸出模式
            input_path = self.view.split_input_path.text()
            if input_path:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_pattern = os.path.join(path, f"{base_name}-%d.pdf")
                self.view.split_output_pattern.setText(output_pattern)
            else:
                self.view.split_output_pattern.setText(os.path.join(path, "page-%d.pdf"))
    
    def select_rotate_input_path(self):
        """選擇要旋轉的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要旋轉的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.rotate_input_path.setText(path)
    
    def select_rotate_output_path(self):
        """選擇旋轉後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.rotate_output_path.setText(path)
    
    def select_compress_input_path(self):
        """選擇要壓縮的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要壓縮的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.compress_input_path.setText(path)
    
    def select_compress_output_path(self):
        """選擇壓縮後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.compress_output_path.setText(path)
    
    def select_repair_input_path(self):
        """選擇要修復的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇要修復的 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.repair_input_path.setText(path)
    
    def select_repair_output_path(self):
        """選擇修復後的輸出路徑"""
        path, _ = QFileDialog.getSaveFileName(
            self.view, "選擇輸出檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.repair_output_path.setText(path)
    
    def select_json_info_input_path(self):
        """選擇要獲取資訊的 PDF 檔案"""
        path, _ = QFileDialog.getOpenFileName(
            self.view, "選擇 PDF 檔案", "", "PDF Files (*.pdf)")
        if path:
            self.view.json_info_input_path.setText(path)
    
    def select_batch_output_directory(self):
        """選擇批量操作的輸出目錄"""
        path = QFileDialog.getExistingDirectory(self.view, "選擇輸出目錄")
        if path:
            self.view.batch_output_dir.setText(path)
            self._update_batch_button_states()
    
    # Batch operations
    def add_batch_files(self):
        """新增批量處理檔案"""
        paths, _ = QFileDialog.getOpenFileNames(
            self.view, "選擇 PDF 檔案", "", "PDF Files (*.pdf)")
        if paths:
            for path in paths:
                # 避免重複添加
                items = [self.view.batch_file_list.item(i).text() 
                        for i in range(self.view.batch_file_list.count())]
                if path not in items:
                    self.view.batch_file_list.addItem(path)
            self._update_batch_button_states()
    
    def add_batch_folder(self):
        """新增資料夾中的所有 PDF 檔案"""
        folder_path = QFileDialog.getExistingDirectory(self.view, "選擇包含 PDF 檔案的資料夾")
        if folder_path:
            pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
            if pdf_files:
                items = [self.view.batch_file_list.item(i).text() 
                        for i in range(self.view.batch_file_list.count())]
                for pdf_file in pdf_files:
                    if pdf_file not in items:
                        self.view.batch_file_list.addItem(pdf_file)
                self._update_batch_button_states()
            else:
                QMessageBox.information(self.view, "資訊", "選擇的資料夾中沒有找到 PDF 檔案。")
    
    def remove_batch_files(self):
        """移除選取的批量處理檔案"""
        selected_items = self.view.batch_file_list.selectedItems()
        for item in selected_items:
            row = self.view.batch_file_list.row(item)
            self.view.batch_file_list.takeItem(row)
        self._update_batch_button_states()
    
    def clear_batch_files(self):
        """清空批量處理檔案列表"""
        self.view.batch_file_list.clear()
        self._update_batch_button_states()
    
    # Operation execution methods
    def execute_check(self):
        """執行 PDF 檢查"""
        pdf_path = self.view.check_path_input.text().strip()
        password = self.view.check_password_input.text().strip() or None
        
        if not pdf_path:
            self.view.display_results('check', '<font color="red">錯誤：請選擇 PDF 檔案</font>')
            return
        
        if not os.path.exists(pdf_path):
            self.view.display_results('check', '<font color="red">錯誤：檔案不存在</font>')
            return
        
        self.view.clear_results('check')
        self.view.check_button.setText("檢查中...")
        self.view.check_button.setEnabled(False)
        
        try:
            info = self.model.check_pdf_file(pdf_path, password)
            # 格式化顯示結果
            result_html = self._format_pdf_info(info)
            self.view.display_results('check', result_html)
        except Exception as e:
            self.view.display_results('check', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.check_button.setText("檢查 PDF")
            self.view.check_button.setEnabled(True)
    
    def execute_decrypt(self):
        """執行 PDF 解密"""
        input_path = self.view.decrypt_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.decrypt_output_path.text().strip())
        password = self.view.decrypt_password_input.text().strip()
        
        if not input_path or not output_path or not password:
            self.view.display_results('decrypt', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('decrypt', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('decrypt')
        self.view.decrypt_button.setText("解密中...")
        self.view.decrypt_button.setEnabled(False)
        
        try:
            result = self.model.decrypt_pdf(input_path, output_path, password)
            if result.success:
                size_info = ""
                if result.file_size_before and result.file_size_after:
                    size_info = f"<br>檔案大小：{result.file_size_before:,} → {result.file_size_after:,} bytes"
                self.view.display_results('decrypt', 
                    f'<font color="green">成功解密 PDF！<br>輸出檔案：{output_path}{size_info}</font>')
            else:
                self.view.display_results('decrypt', 
                    f'<font color="red">解密失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('decrypt', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.decrypt_button.setText("解密 PDF")
            self.view.decrypt_button.setEnabled(True)
    
    def execute_encrypt(self):
        """執行 PDF 加密"""
        input_path = self.view.encrypt_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.encrypt_output_path.text().strip())
        user_password = self.view.encrypt_user_password.text().strip()
        owner_password = self.view.encrypt_owner_password.text().strip()
        
        if not input_path or not output_path or not user_password:
            self.view.display_results('encrypt', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('encrypt', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        encryption_level = self.view.encrypt_level_combo.currentData()
        print_allowed = self.view.encrypt_allow_print.isChecked()
        modify_allowed = self.view.encrypt_allow_modify.isChecked()
        extract_allowed = self.view.encrypt_allow_extract.isChecked()
        annotate_allowed = self.view.encrypt_allow_annotate.isChecked()
        
        self.view.clear_results('encrypt')
        self.view.encrypt_button.setText("加密中...")
        self.view.encrypt_button.setEnabled(False)
        
        try:
            result = self.model.encrypt_pdf(
                input_path, output_path, user_password, owner_password,
                encryption_level, print_allowed, modify_allowed,
                extract_allowed, annotate_allowed
            )
            if result.success:
                self.view.display_results('encrypt', 
                    f'<font color="green">成功加密 PDF！<br>輸出檔案：{output_path}</font>')
            else:
                self.view.display_results('encrypt', 
                    f'<font color="red">加密失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('encrypt', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.encrypt_button.setText("加密 PDF")
            self.view.encrypt_button.setEnabled(True)
    
    def execute_linearize(self):
        """執行 PDF 線性化"""
        input_path = self.view.linearize_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.linearize_output_path.text().strip())
        password = self.view.linearize_password_input.text().strip() or None
        
        if not input_path or not output_path:
            self.view.display_results('linearize', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('linearize', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('linearize')
        self.view.linearize_button.setText("線性化中...")
        self.view.linearize_button.setEnabled(False)
        
        try:
            result = self.model.linearize_pdf(input_path, output_path, password)
            if result.success:
                self.view.display_results('linearize', 
                    f'<font color="green">成功線性化 PDF！<br>輸出檔案：{output_path}</font>')
            else:
                self.view.display_results('linearize', 
                    f'<font color="red">線性化失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('linearize', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.linearize_button.setText("線性化 PDF")
            self.view.linearize_button.setEnabled(True)
    
    def execute_split(self):
        """執行 PDF 分割"""
        input_path = self.view.split_input_path.text().strip()
        output_pattern = self._ensure_pdf_extension_pattern(self.view.split_output_pattern.text().strip())
        page_range = self.view.split_page_range.text().strip() or None
        password = self.view.split_password_input.text().strip() or None
        
        if not input_path or not output_pattern:
            self.view.display_results('split', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('split', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('split')
        self.view.split_button.setText("分割中...")
        self.view.split_button.setEnabled(False)
        
        try:
            result = self.model.split_pdf_pages(input_path, output_pattern, page_range, password)
            if result.success:
                self.view.display_results('split', 
                    f'<font color="green">成功分割 PDF！<br>輸出模式：{output_pattern}</font>')
            else:
                self.view.display_results('split', 
                    f'<font color="red">分割失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('split', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.split_button.setText("分割 PDF 頁面")
            self.view.split_button.setEnabled(True)
    
    def execute_rotate(self):
        """執行 PDF 旋轉"""
        input_path = self.view.rotate_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.rotate_output_path.text().strip())
        rotation_angle = self.view.rotate_angle_combo.currentData()
        rotation_pages = self.view.rotate_page_range.text().strip()
        password = self.view.rotate_password_input.text().strip() or None
        
        if not input_path or not output_path:
            self.view.display_results('rotate', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('rotate', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('rotate')
        self.view.rotate_button.setText("旋轉中...")
        self.view.rotate_button.setEnabled(False)
        
        try:
            result = self.model.rotate_pdf_pages(input_path, output_path, rotation_angle, rotation_pages, password)
            if result.success:
                self.view.display_results('rotate', 
                    f'<font color="green">成功旋轉 PDF！<br>輸出檔案：{output_path}</font>')
            else:
                self.view.display_results('rotate', 
                    f'<font color="red">旋轉失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('rotate', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.rotate_button.setText("旋轉 PDF 頁面")
            self.view.rotate_button.setEnabled(True)
    
    def execute_compress(self):
        """執行 PDF 壓縮"""
        input_path = self.view.compress_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.compress_output_path.text().strip())
        compression_level = self.view.compress_level_combo.currentData()
        remove_unreferenced = self.view.compress_remove_unreferenced.isChecked()
        password = self.view.compress_password_input.text().strip() or None
        
        if not input_path or not output_path:
            self.view.display_results('compress', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('compress', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('compress')
        self.view.compress_button.setText("壓縮中...")
        self.view.compress_button.setEnabled(False)
        
        try:
            result = self.model.compress_pdf(input_path, output_path, compression_level, remove_unreferenced, password)
            if result.success:
                size_info = ""
                if result.file_size_before and result.file_size_after:
                    compression_ratio = (1 - result.file_size_after / result.file_size_before) * 100
                    size_info = f"<br>檔案大小：{result.file_size_before:,} → {result.file_size_after:,} bytes ({compression_ratio:.1f}% 壓縮)"
                self.view.display_results('compress', 
                    f'<font color="green">成功壓縮 PDF！<br>輸出檔案：{output_path}{size_info}</font>')
            else:
                self.view.display_results('compress', 
                    f'<font color="red">壓縮失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('compress', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.compress_button.setText("壓縮 PDF")
            self.view.compress_button.setEnabled(True)
    
    def execute_repair(self):
        """執行 PDF 修復"""
        input_path = self.view.repair_input_path.text().strip()
        output_path = self._ensure_pdf_extension(self.view.repair_output_path.text().strip())
        password = self.view.repair_password_input.text().strip() or None
        
        if not input_path or not output_path:
            self.view.display_results('repair', '<font color="red">錯誤：請填寫所有必要欄位</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('repair', '<font color="red">錯誤：輸入檔案不存在</font>')
            return
        
        self.view.clear_results('repair')
        self.view.repair_button.setText("修復中...")
        self.view.repair_button.setEnabled(False)
        
        try:
            result = self.model.repair_pdf(input_path, output_path, password)
            if result.success:
                self.view.display_results('repair', 
                    f'<font color="green">成功修復 PDF！<br>輸出檔案：{output_path}</font>')
            else:
                self.view.display_results('repair', 
                    f'<font color="red">修復失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('repair', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.repair_button.setText("修復 PDF")
            self.view.repair_button.setEnabled(True)
    
    def execute_json_info(self):
        """執行獲取 JSON 資訊"""
        input_path = self.view.json_info_input_path.text().strip()
        password = self.view.json_info_password_input.text().strip() or None
        
        if not input_path:
            self.view.display_results('json_info', '<font color="red">錯誤：請選擇 PDF 檔案</font>')
            return
        
        if not os.path.exists(input_path):
            self.view.display_results('json_info', '<font color="red">錯誤：檔案不存在</font>')
            return
        
        self.view.clear_results('json_info')
        self.view.json_info_button.setText("獲取資訊中...")
        self.view.json_info_button.setEnabled(False)
        
        try:
            result = self.model.get_pdf_json_info(input_path, password)
            if result.success:
                # 格式化 JSON 輸出
                import json
                try:
                    if result.stdout:
                        json_data = json.loads(result.stdout)
                        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                        self.view.display_results('json_info', f'<pre>{formatted_json}</pre>')
                    else:
                        self.view.display_results('json_info', '<font color="yellow">沒有 JSON 資訊輸出</font>')
                except json.JSONDecodeError:
                    self.view.display_results('json_info', f'<pre>{result.stdout}</pre>')
            else:
                self.view.display_results('json_info', 
                    f'<font color="red">獲取資訊失敗：{result.error_message}</font>')
        except Exception as e:
            self.view.display_results('json_info', f'<font color="red">錯誤：{str(e)}</font>')
        finally:
            self.view.json_info_button.setText("取得 JSON 資訊")
            self.view.json_info_button.setEnabled(True)
    
    def execute_batch(self):
        """執行批量操作"""
        file_count = self.view.batch_file_list.count()
        if file_count == 0:
            self.view.display_results('batch', '<font color="red">錯誤：請添加要處理的檔案</font>')
            return
        
        output_dir = self.view.batch_output_dir.text().strip()
        if not output_dir:
            self.view.display_results('batch', '<font color="red">錯誤：請選擇輸出目錄</font>')
            return
        
        operation_type = self.view.batch_operation_combo.currentData()
        parallel = self.view.batch_parallel.isChecked()
        max_workers = self.view.batch_max_workers.value()
        
        # 收集檔案列表
        file_paths = []
        for i in range(file_count):
            file_paths.append(self.view.batch_file_list.item(i).text())
        
        # 創建操作列表
        operations = []
        for file_path in file_paths:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            if operation_type == "check":
                # 檢查操作不需要輸出檔案
                operation = QPDFOperation(
                    operation_type=QPDFOperationType.CHECK,
                    input_file=file_path
                )
            elif operation_type == "linearize":
                output_file = os.path.join(output_dir, f"{base_name}_linearized.pdf")
                operation = QPDFOperation(
                    operation_type=QPDFOperationType.LINEARIZE,
                    input_file=file_path,
                    output_file=output_file
                )
            elif operation_type == "compress":
                output_file = os.path.join(output_dir, f"{base_name}_compressed.pdf")
                operation = QPDFOperation(
                    operation_type=QPDFOperationType.COMPRESS_STREAMS,
                    input_file=file_path,
                    output_file=output_file,
                    compression_level=CompressionLevel.MEDIUM,
                    remove_unreferenced=True
                )
            elif operation_type == "repair":
                output_file = os.path.join(output_dir, f"{base_name}_repaired.pdf")
                operation = QPDFOperation(
                    operation_type=QPDFOperationType.REPAIR,
                    input_file=file_path,
                    output_file=output_file
                )
            else:
                continue
            
            operations.append(operation)
        
        if not operations:
            self.view.display_results('batch', '<font color="red">錯誤：沒有有效的操作</font>')
            return
        
        self.view.clear_results('batch')
        self.view.batch_execute_button.setText("執行中...")
        self.view.batch_execute_button.setEnabled(False)
        self.view.show_progress(True)
        self.view.set_progress(0, "準備中")
        
        try:
            batch_result = self.model.execute_batch_operations(operations, parallel)
            
            # 顯示結果
            result_html = f"""
            <h3>批量操作完成</h3>
            <p><strong>總操作數：</strong>{batch_result.total_operations}</p>
            <p><strong>成功：</strong><font color="green">{batch_result.successful_operations}</font></p>
            <p><strong>失敗：</strong><font color="red">{batch_result.failed_operations}</font></p>
            <p><strong>執行時間：</strong>{batch_result.execution_time:.2f} 秒</p>
            <p><strong>摘要：</strong>{batch_result.summary}</p>
            """
            
            # 顯示詳細結果
            if batch_result.results:
                result_html += "<h4>詳細結果：</h4><ul>"
                for result in batch_result.results:
                    status = "✅" if result.success else "❌"
                    file_name = os.path.basename(result.input_file)
                    result_html += f"<li>{status} {file_name}"
                    if not result.success and result.error_message:
                        result_html += f" - {result.error_message}"
                    result_html += "</li>"
                result_html += "</ul>"
            
            self.view.display_results('batch', result_html)
            
        except Exception as e:
            self.view.display_results('batch', f'<font color="red">批量操作錯誤：{str(e)}</font>')
        finally:
            self.view.batch_execute_button.setText("執行批量操作")
            self.view.batch_execute_button.setEnabled(True)
            self.view.show_progress(False)
    
    # Model signal handlers
    def _on_operation_started(self, operation_name):
        """操作開始時的處理"""
        # 可以在這裡添加狀態更新邏輯
        pass
    
    def _on_operation_completed(self, result):
        """操作完成時的處理"""
        # 可以在這裡添加完成後的處理邏輯
        pass
    
    def _on_operation_failed(self, error_message):
        """操作失敗時的處理"""
        # 可以在這裡添加錯誤處理邏輯
        pass
    
    def _on_progress_updated(self, progress, message):
        """進度更新時的處理"""
        # 可以在這裡更新進度條
        pass
    
    def _on_info_updated(self, pdf_info):
        """PDF 資訊更新時的處理"""
        # 可以在這裡處理 PDF 資訊更新
        pass
    
    def _on_batch_progress(self, completed, total, current_operation):
        """批量操作進度更新"""
        if total > 0:
            progress = int((completed / total) * 100)
            self.view.set_progress(progress, f"{current_operation} ({completed}/{total})")
    
    def _format_pdf_info(self, pdf_info):
        """格式化 PDF 資訊顯示"""
        html = "<h3>PDF 檔案資訊</h3>"
        html += f"<p><strong>檔案路徑：</strong>{pdf_info.file_path}</p>"
        
        if pdf_info.file_size:
            html += f"<p><strong>檔案大小：</strong>{pdf_info.file_size:,} bytes</p>"
        
        if pdf_info.pdf_version:
            html += f"<p><strong>PDF 版本：</strong>{pdf_info.pdf_version}</p>"
        
        if pdf_info.page_count is not None:
            html += f"<p><strong>頁數：</strong>{pdf_info.page_count}</p>"
        
        html += f"<p><strong>是否加密：</strong>{'是' if pdf_info.is_encrypted else '否'}</p>"
        html += f"<p><strong>是否線性化：</strong>{'是' if pdf_info.is_linearized else '否'}</p>"
        html += f"<p><strong>是否有附件：</strong>{'是' if pdf_info.has_attachments else '否'}</p>"
        
        if pdf_info.warnings:
            html += "<h4>警告：</h4><ul>"
            for warning in pdf_info.warnings:
                html += f"<li><font color='orange'>{warning}</font></li>"
            html += "</ul>"
        
        if pdf_info.errors:
            html += "<h4>錯誤：</h4><ul>"
            for error in pdf_info.errors:
                html += f"<li><font color='red'>{error}</font></li>"
            html += "</ul>"
        
        return html