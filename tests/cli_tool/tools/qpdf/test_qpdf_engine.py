"""
QPDF 引擎測試
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import subprocess
import json
import os

# 修正導入路徑
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from tools.qpdf.core.qpdf_engine import QPDFEngine
from tools.qpdf.core.data_models import (
    QPDFOperation, QPDFResult, QPDFOperationType, QPDFBatchOperation,
    EncryptionLevel, CompressionLevel, build_qpdf_command
)


class TestQPDFEngine:
    """QPDF 引擎測試類"""
    
    @pytest.fixture
    def qpdf_engine(self):
        """創建 QPDF 引擎實例"""
        return QPDFEngine("qpdf")
    
    @patch('subprocess.run')
    def test_is_available_success(self, mock_run, qpdf_engine):
        """測試工具可用性檢查成功"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "QPDF version 11.1.1"
        
        result = qpdf_engine.is_available()
        
        assert result is True
        assert qpdf_engine._version == "QPDF version 11.1.1"
        mock_run.assert_called_once_with(
            ["qpdf", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_is_available_failure(self, mock_run, qpdf_engine):
        """測試工具不可用"""
        mock_run.side_effect = FileNotFoundError()
        
        result = qpdf_engine.is_available()
        
        assert result is False
        assert qpdf_engine._is_available is False
    
    @patch('subprocess.run')
    def test_get_version(self, mock_run, qpdf_engine):
        """測試版本獲取"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "QPDF version 11.1.1"
        
        version = qpdf_engine.get_version()
        
        assert version == "QPDF version 11.1.1"
    
    @patch('subprocess.run')
    @patch('os.path.getsize')
    def test_execute_operation_success(self, mock_getsize, mock_run, qpdf_engine):
        """測試操作執行成功"""
        # 模擬檔案大小
        mock_getsize.side_effect = [1000, 950]  # 輸入檔案大小, 輸出檔案大小
        
        # 模擬 subprocess 成功執行
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "PDF decrypted successfully"
        mock_run.return_value.stderr = ""
        
        # 創建測試操作
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf",
            password="testpass"
        )
        
        with patch('tools.qpdf.core.data_models.validate_pdf_file', return_value=True):
            with patch('os.path.exists', return_value=True):
                result = qpdf_engine.execute_operation(operation)
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.DECRYPT
        assert result.input_file == "/test/encrypted.pdf"
        assert result.output_file == "/test/decrypted.pdf"
        assert result.stdout == "PDF decrypted successfully"
        assert result.file_size_before == 1000
        assert result.file_size_after == 950
        assert result.execution_time > 0
    
    @patch('subprocess.run')
    def test_execute_operation_failure(self, mock_run, qpdf_engine):
        """測試操作執行失敗"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Invalid password"
        
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf",
            password="wrongpass"
        )
        
        with patch('tools.qpdf.core.data_models.validate_pdf_file', return_value=True):
            with patch('os.path.getsize', return_value=1000):
                result = qpdf_engine.execute_operation(operation)
        
        assert result.success is False
        assert result.error_message == "Invalid password"
        assert result.exit_code == 1
    
    @patch('subprocess.run')
    def test_execute_operation_timeout(self, mock_run, qpdf_engine):
        """測試操作超時"""
        mock_run.side_effect = subprocess.TimeoutExpired(["qpdf"], 300)
        
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf"
        )
        
        with patch('tools.qpdf.core.data_models.validate_pdf_file', return_value=True):
            with patch('os.path.getsize', return_value=1000):
                result = qpdf_engine.execute_operation(operation)
        
        assert result.success is False
        assert "timed out" in result.error_message
    
    def test_execute_batch_operations_sequential(self, qpdf_engine):
        """測試批量操作順序執行"""
        operations = [
            QPDFOperation(
                operation_type=QPDFOperationType.CHECK,
                input_file="/test/file1.pdf"
            ),
            QPDFOperation(
                operation_type=QPDFOperationType.CHECK,
                input_file="/test/file2.pdf"
            )
        ]
        
        batch_op = QPDFBatchOperation(
            operations=operations,
            parallel_execution=False
        )
        
        with patch.object(qpdf_engine, 'execute_operation') as mock_execute:
            mock_execute.side_effect = [
                QPDFResult(success=True, operation_type=QPDFOperationType.CHECK, 
                          input_file="/test/file1.pdf"),
                QPDFResult(success=True, operation_type=QPDFOperationType.CHECK, 
                          input_file="/test/file2.pdf")
            ]
            
            result = qpdf_engine.execute_batch_operations(batch_op)
        
        assert result.total_operations == 2
        assert result.successful_operations == 2
        assert result.failed_operations == 0
        assert len(result.results) == 2
        assert mock_execute.call_count == 2
    
    def test_execute_batch_operations_with_failure(self, qpdf_engine):
        """測試批量操作中包含失敗的情況"""
        operations = [
            QPDFOperation(
                operation_type=QPDFOperationType.CHECK,
                input_file="/test/file1.pdf"
            ),
            QPDFOperation(
                operation_type=QPDFOperationType.CHECK,
                input_file="/test/file2.pdf"
            )
        ]
        
        batch_op = QPDFBatchOperation(
            operations=operations,
            parallel_execution=False,
            continue_on_error=True
        )
        
        with patch.object(qpdf_engine, 'execute_operation') as mock_execute:
            mock_execute.side_effect = [
                QPDFResult(success=True, operation_type=QPDFOperationType.CHECK, 
                          input_file="/test/file1.pdf"),
                QPDFResult(success=False, operation_type=QPDFOperationType.CHECK, 
                          input_file="/test/file2.pdf", error_message="File not found")
            ]
            
            result = qpdf_engine.execute_batch_operations(batch_op)
        
        assert result.total_operations == 2
        assert result.successful_operations == 1
        assert result.failed_operations == 1
    
    @patch('subprocess.run')
    def test_get_pdf_info_success(self, mock_run, qpdf_engine):
        """測試獲取 PDF 資訊成功"""
        # 模擬 --check 命令輸出
        mock_run.side_effect = [
            # 第一次調用 (--check)
            type('MockResult', (), {
                'returncode': 0,
                'stdout': 'PDF file is encrypted and linearized',
                'stderr': ''
            })(),
            # 第二次調用 (--json)
            type('MockResult', (), {
                'returncode': 0,
                'stdout': '{"version": "1.4", "pages": [{"obj": "3 0 R"}, {"obj": "4 0 R"}]}',
                'stderr': ''
            })()
        ]
        
        with patch('tools.qpdf.core.data_models.validate_pdf_file', return_value=True):
            with patch('os.path.getsize', return_value=50000):
                info = qpdf_engine.get_pdf_info("/test/document.pdf")
        
        assert info.file_path == "/test/document.pdf"
        assert info.is_encrypted is True
        assert info.is_linearized is True
        assert info.page_count == 2
        assert info.pdf_version == "1.4"
        assert info.file_size == 50000
    
    @patch('subprocess.run')
    def test_get_pdf_info_json_parse_error(self, mock_run, qpdf_engine):
        """測試 JSON 解析錯誤"""
        mock_run.side_effect = [
            type('MockResult', (), {
                'returncode': 0,
                'stdout': 'PDF file is valid',
                'stderr': ''
            })(),
            type('MockResult', (), {
                'returncode': 0,
                'stdout': 'invalid json',
                'stderr': ''
            })()
        ]
        
        with patch('tools.qpdf.core.data_models.validate_pdf_file', return_value=True):
            with patch('os.path.getsize', return_value=50000):
                info = qpdf_engine.get_pdf_info("/test/document.pdf")
        
        assert "Could not parse JSON output" in info.warnings
    
    @patch('subprocess.run')
    def test_check_pdf_integrity_success(self, mock_run, qpdf_engine):
        """測試 PDF 完整性檢查成功"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        is_valid, message = qpdf_engine.check_pdf_integrity("/test/document.pdf")
        
        assert is_valid is True
        assert message == "PDF file is valid"
    
    @patch('subprocess.run')
    def test_check_pdf_integrity_failure(self, mock_run, qpdf_engine):
        """測試 PDF 完整性檢查失敗"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "PDF file is corrupted"
        
        is_valid, message = qpdf_engine.check_pdf_integrity("/test/corrupted.pdf")
        
        assert is_valid is False
        assert message == "PDF file is corrupted"
    
    def test_repair_pdf(self, qpdf_engine):
        """測試 PDF 修復"""
        with patch.object(qpdf_engine, 'execute_operation') as mock_execute:
            mock_result = QPDFResult(
                success=True,
                operation_type=QPDFOperationType.REPAIR,
                input_file="/test/corrupted.pdf",
                output_file="/test/repaired.pdf"
            )
            mock_execute.return_value = mock_result
            
            result = qpdf_engine.repair_pdf("/test/corrupted.pdf", "/test/repaired.pdf")
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.REPAIR
        
        # 檢查傳遞的操作參數
        call_args = mock_execute.call_args[0][0]
        assert call_args.normalize_content is True
    
    def test_optimize_pdf(self, qpdf_engine):
        """測試 PDF 優化"""
        with patch.object(qpdf_engine, 'execute_operation') as mock_execute:
            mock_result = QPDFResult(
                success=True,
                operation_type=QPDFOperationType.COMPRESS_STREAMS,
                input_file="/test/document.pdf",
                output_file="/test/optimized.pdf"
            )
            mock_execute.return_value = mock_result
            
            result = qpdf_engine.optimize_pdf("/test/document.pdf", "/test/optimized.pdf")
        
        assert result.success is True
        assert result.operation_type == QPDFOperationType.COMPRESS_STREAMS
        
        # 檢查傳遞的操作參數
        call_args = mock_execute.call_args[0][0]
        assert call_args.remove_unreferenced is True
        assert call_args.normalize_content is True


class TestDataModels:
    """數據模型測試類"""
    
    def test_build_qpdf_command_decrypt(self):
        """測試解密命令構建"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file="/test/encrypted.pdf",
            output_file="/test/decrypted.pdf",
            password="testpass"
        )
        
        cmd = build_qpdf_command(operation)
        
        expected = ["qpdf", "--password", "testpass", "--decrypt", 
                   "/test/encrypted.pdf", "/test/decrypted.pdf"]
        assert cmd == expected
    
    def test_build_qpdf_command_encrypt(self):
        """測試加密命令構建"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.ENCRYPT,
            input_file="/test/document.pdf",
            output_file="/test/encrypted.pdf",
            encryption_level=EncryptionLevel.AES_256,
            user_password="user123",
            owner_password="owner456",
            print_allowed=False,
            modify_allowed=False
        )
        
        cmd = build_qpdf_command(operation)
        
        assert "qpdf" in cmd
        assert "--encrypt" in cmd
        assert "user123" in cmd
        assert "owner456" in cmd
        assert "256R6" in cmd
        assert "--print=none" in cmd
        assert "--modify=none" in cmd
        assert "--" in cmd
    
    def test_build_qpdf_command_linearize(self):
        """測試線性化命令構建"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.LINEARIZE,
            input_file="/test/document.pdf",
            output_file="/test/linearized.pdf"
        )
        
        cmd = build_qpdf_command(operation)
        
        expected = ["qpdf", "--linearize", "/test/document.pdf", "/test/linearized.pdf"]
        assert cmd == expected
    
    def test_build_qpdf_command_compress(self):
        """測試壓縮命令構建"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.COMPRESS_STREAMS,
            input_file="/test/document.pdf",
            output_file="/test/compressed.pdf",
            compression_level=CompressionLevel.HIGH,
            remove_unreferenced=True,
            normalize_content=True
        )
        
        cmd = build_qpdf_command(operation)
        
        assert "qpdf" in cmd
        assert "--compress-streams=y" in cmd
        assert "--decode-level=all" in cmd
        assert "--remove-unreferenced-resources" in cmd
        assert "--normalize-content=y" in cmd
    
    def test_build_qpdf_command_rotate(self):
        """測試旋轉命令構建"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.ROTATE,
            input_file="/test/document.pdf",
            output_file="/test/rotated.pdf",
            rotation_angle=90,
            rotation_pages="1-5"
        )
        
        cmd = build_qpdf_command(operation)
        
        assert "qpdf" in cmd
        assert "--rotate" in cmd
        assert "90:1-5" in cmd
    
    def test_validate_pdf_file(self):
        """測試 PDF 檔案驗證"""
        from tools.qpdf.core.data_models import validate_pdf_file
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_file', return_value=True):
                # 測試有效的 PDF 檔案
                assert validate_pdf_file("/test/document.pdf") is True
                assert validate_pdf_file("/test/document.PDF") is True
                
                # 測試無效的檔案擴展名
                assert validate_pdf_file("/test/document.txt") is False
    
    def test_validate_page_range(self):
        """測試頁面範圍驗證"""
        from tools.qpdf.core.data_models import validate_page_range
        
        # 測試有效的頁面範圍
        assert validate_page_range("1-5") is True
        assert validate_page_range("1,3,5") is True
        assert validate_page_range("1-") is True
        assert validate_page_range("1-5,7,9-12") is True
        
        # 測試無效的頁面範圍
        assert validate_page_range("1-5-7") is False
        assert validate_page_range("a-b") is False
        assert validate_page_range("1--5") is False
        
        # 測試空範圍（應該返回 True，表示沒有限制）
        assert validate_page_range("") is True
        assert validate_page_range(None) is True