"""
QPDF 模型測試
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import tempfile
from pathlib import Path

# 修正導入路徑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from tools.qpdf.qpdf_model import QPDFModel
from tools.qpdf.core.data_models import (
    QPDFOperation, QPDFResult, PDFInfo, QPDFOperationType, 
    EncryptionLevel, CompressionLevel
)


class TestQPDFModel:
    """QPDF 模型測試類"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """模擬配置管理器"""
        with patch('tools.qpdf.qpdf_model.config_manager') as mock_config:
            mock_config.get_tool_config.return_value = {'executable_path': 'qpdf'}
            mock_config.get_user_data_path.return_value = Path('/tmp/test')
            yield mock_config
    
    @pytest.fixture
    def mock_engine(self):
        """模擬 QPDF 引擎"""
        with patch('tools.qpdf.qpdf_model.QPDFEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine.is_available.return_value = True
            mock_engine.get_version.return_value = "QPDF version 11.1.1"
            mock_engine_class.return_value = mock_engine
            yield mock_engine
    
    @pytest.fixture
    def qpdf_model(self, mock_config_manager, mock_engine):
        """創建 QPDF 模型實例"""
        with patch('builtins.open', mock_open(read_data='{}'))):
            model = QPDFModel()
            return model
    
    def test_model_initialization(self, qpdf_model, mock_engine):
        """測試模型初始化"""
        assert qpdf_model.engine is not None
        assert isinstance(qpdf_model.operation_history, list)
        assert isinstance(qpdf_model.settings, dict)
        mock_engine.is_available.assert_called_once()
        mock_engine.get_version.assert_called_once()
    
    def test_is_available(self, qpdf_model, mock_engine):
        """測試工具可用性檢查"""
        mock_engine.is_available.return_value = True
        assert qpdf_model.is_available() is True
        
        mock_engine.is_available.return_value = False
        assert qpdf_model.is_available() is False
    
    def test_get_version(self, qpdf_model, mock_engine):
        """測試版本獲取"""
        expected_version = "QPDF version 11.1.1"
        mock_engine.get_version.return_value = expected_version
        assert qpdf_model.get_version() == expected_version
    
    def test_check_pdf_file_success(self, qpdf_model, mock_engine):
        """測試 PDF 檔案檢查成功"""
        # 模擬 PDF 資訊
        mock_info = PDFInfo(
            file_path="/test/file.pdf",
            is_encrypted=False,
            page_count=10,
            pdf_version="1.4"
        )
        mock_engine.get_pdf_info.return_value = mock_info
        
        result = qpdf_model.check_pdf_file("/test/file.pdf")
        
        assert result == mock_info
        mock_engine.get_pdf_info.assert_called_once_with("/test/file.pdf", None)
    
    def test_check_pdf_file_with_password(self, qpdf_model, mock_engine):
        """測試帶密碼的 PDF 檔案檢查"""
        mock_info = PDFInfo(
            file_path="/test/encrypted.pdf",
            is_encrypted=True,
            page_count=5
        )
        mock_engine.get_pdf_info.return_value = mock_info
        
        result = qpdf_model.check_pdf_file("/test/encrypted.pdf", "password123")
        
        assert result == mock_info
        mock_engine.get_pdf_info.assert_called_once_with("/test/encrypted.pdf", "password123")
    
    def test_decrypt_pdf_success(self, qpdf_model, mock_engine):
        """測試 PDF 解密成功"""
        # 模擬成功的解密結果
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf",
            execution_time=2.5,
            file_size_before=1024,
            file_size_after=1020
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.decrypt_pdf("/test/encrypted.pdf", "/test/decrypted.pdf", "password123")
        
        assert result.success is True
        assert result.input_file == "/test/encrypted.pdf"
        assert result.output_file == "/test/decrypted.pdf"
        assert result.operation_type == QPDFOperationType.DECRYPT
        
        # 檢查操作歷史是否被添加
        assert len(qpdf_model.operation_history) == 1
        assert qpdf_model.operation_history[0] == mock_result
    
    def test_encrypt_pdf_success(self, qpdf_model, mock_engine):
        """測試 PDF 加密成功"""
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.ENCRYPT,
            input_file="/test/document.pdf",
            output_file="/test/encrypted.pdf",
            execution_time=3.0
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.encrypt_pdf(
            "/test/document.pdf", "/test/encrypted.pdf", 
            "user_pass", "owner_pass", EncryptionLevel.AES_256
        )
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.ENCRYPT
        
        # 檢查傳遞給引擎的操作參數
        call_args = mock_engine.execute_operation.call_args[0][0]
        assert isinstance(call_args, QPDFOperation)
        assert call_args.operation_type == QPDFOperationType.ENCRYPT
        assert call_args.user_password == "user_pass"
        assert call_args.owner_password == "owner_pass"
        assert call_args.encryption_level == EncryptionLevel.AES_256
    
    def test_linearize_pdf_success(self, qpdf_model, mock_engine):
        """測試 PDF 線性化成功"""
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.LINEARIZE,
            input_file="/test/document.pdf",
            output_file="/test/linearized.pdf"
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.linearize_pdf("/test/document.pdf", "/test/linearized.pdf")
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.LINEARIZE
    
    def test_compress_pdf_with_options(self, qpdf_model, mock_engine):
        """測試帶選項的 PDF 壓縮"""
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.COMPRESS_STREAMS,
            input_file="/test/document.pdf",
            output_file="/test/compressed.pdf",
            file_size_before=5000,
            file_size_after=3000
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.compress_pdf(
            "/test/document.pdf", "/test/compressed.pdf",
            CompressionLevel.HIGH, remove_unreferenced=True
        )
        
        assert result.success is True
        assert result.file_size_before == 5000
        assert result.file_size_after == 3000
        
        # 檢查操作參數
        call_args = mock_engine.execute_operation.call_args[0][0]
        assert call_args.compression_level == CompressionLevel.HIGH
        assert call_args.remove_unreferenced is True
        assert call_args.normalize_content is True
    
    def test_split_pdf_pages(self, qpdf_model, mock_engine):
        """測試 PDF 頁面分割"""
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.SPLIT_PAGES,
            input_file="/test/document.pdf",
            output_file="/test/page-%d.pdf"
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.split_pdf_pages(
            "/test/document.pdf", "/test/page-%d.pdf", "1-5"
        )
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.SPLIT_PAGES
        
        # 檢查操作參數
        call_args = mock_engine.execute_operation.call_args[0][0]
        assert call_args.page_range == "1-5"
    
    def test_rotate_pdf_pages(self, qpdf_model, mock_engine):
        """測試 PDF 頁面旋轉"""
        mock_result = QPDFResult(
            success=True,
            operation_type=QPDFOperationType.ROTATE,
            input_file="/test/document.pdf",
            output_file="/test/rotated.pdf"
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.rotate_pdf_pages(
            "/test/document.pdf", "/test/rotated.pdf", 90, "1-10"
        )
        
        assert result.success is True
        
        # 檢查操作參數
        call_args = mock_engine.execute_operation.call_args[0][0]
        assert call_args.rotation_angle == 90
        assert call_args.rotation_pages == "1-10"
    
    def test_operation_failure_handling(self, qpdf_model, mock_engine):
        """測試操作失敗處理"""
        mock_result = QPDFResult(
            success=False,
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf",
            error_message="Invalid password"
        )
        mock_engine.execute_operation.return_value = mock_result
        
        result = qpdf_model.decrypt_pdf("/test/encrypted.pdf", "/test/decrypted.pdf", "wrong_password")
        
        assert result.success is False
        assert result.error_message == "Invalid password"
        
        # 失敗的操作也應該被記錄在歷史中
        assert len(qpdf_model.operation_history) == 1
    
    def test_batch_operations(self, qpdf_model, mock_engine):
        """測試批量操作"""
        from tools.qpdf.core.data_models import QPDFBatchResult
        
        operations = [
            QPDFOperation(
                operation_type=QPDFOperationType.LINEARIZE,
                input_file="/test/doc1.pdf",
                output_file="/test/doc1_linear.pdf"
            ),
            QPDFOperation(
                operation_type=QPDFOperationType.COMPRESS_STREAMS,
                input_file="/test/doc2.pdf",
                output_file="/test/doc2_compressed.pdf"
            )
        ]
        
        mock_batch_result = QPDFBatchResult(
            total_operations=2,
            successful_operations=2,
            failed_operations=0,
            results=[],
            summary="完成 2/2 個操作, 成功: 2"
        )
        mock_engine.execute_batch_operations.return_value = mock_batch_result
        
        result = qpdf_model.execute_batch_operations(operations, parallel=True)
        
        assert result.total_operations == 2
        assert result.successful_operations == 2
        assert result.failed_operations == 0
        
        # 檢查批量操作參數
        call_args = mock_engine.execute_batch_operations.call_args[0][0]
        assert call_args.parallel_execution is True
        assert call_args.max_workers == 4  # 預設值
        assert len(call_args.operations) == 2
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_settings(self, mock_file, qpdf_model, mock_config_manager):
        """測試設定保存"""
        qpdf_model.settings["test_setting"] = "test_value"
        
        qpdf_model.save_settings()
        
        mock_file.assert_called_once()
        # 檢查是否寫入了 JSON 數據
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        assert "test_setting" in written_data
        assert "test_value" in written_data
    
    def test_get_recent_files(self, qpdf_model):
        """測試獲取最近使用的檔案"""
        # 設定模擬的最近檔案
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            qpdf_model.settings["recent_files"] = ["/test/file1.pdf", "/test/file2.pdf"]
            
            recent_files = qpdf_model.get_recent_files()
            
            assert len(recent_files) == 2
            assert "/test/file1.pdf" in recent_files
            assert "/test/file2.pdf" in recent_files
    
    def test_clear_history(self, qpdf_model):
        """測試清除操作歷史"""
        # 添加一些模擬歷史記錄
        qpdf_model.operation_history.append(QPDFResult(
            success=True,
            operation_type=QPDFOperationType.CHECK,
            input_file="/test/file.pdf"
        ))
        
        assert len(qpdf_model.operation_history) == 1
        
        qpdf_model.clear_history()
        
        assert len(qpdf_model.operation_history) == 0
    
    def test_validate_operation_inputs(self, qpdf_model):
        """測試操作輸入驗證"""
        # 測試空輸入檔案
        errors = qpdf_model.validate_operation_inputs(
            QPDFOperationType.DECRYPT, "", "/test/output.pdf"
        )
        assert "請選擇輸入檔案" in errors
        
        # 測試缺少輸出檔案的操作
        errors = qpdf_model.validate_operation_inputs(
            QPDFOperationType.DECRYPT, "/test/input.pdf", ""
        )
        assert "請指定輸出檔案" in errors
        
        # 測試輸入和輸出檔案相同
        errors = qpdf_model.validate_operation_inputs(
            QPDFOperationType.DECRYPT, "/test/file.pdf", "/test/file.pdf"
        )
        assert "輸出檔案不能與輸入檔案相同" in errors