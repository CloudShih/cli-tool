"""
QPDF 核心引擎
負責執行 QPDF 命令和處理結果
"""

import subprocess
import time
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .data_models import (
    QPDFOperation, QPDFResult, PDFInfo, QPDFBatchOperation, QPDFBatchResult,
    QPDFOperationType, build_qpdf_command, validate_pdf_file, format_file_size
)

logger = logging.getLogger(__name__)


class QPDFEngine:
    """QPDF 核心執行引擎"""
    
    def __init__(self, qpdf_executable: str = "qpdf"):
        self.qpdf_executable = qpdf_executable
        self._is_available = None
        self._version = None
    
    def is_available(self) -> bool:
        """檢查 QPDF 是否可用"""
        if self._is_available is not None:
            return self._is_available
        
        try:
            result = subprocess.run(
                [self.qpdf_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._is_available = True
                self._version = result.stdout.strip()
                logger.info(f"QPDF available: {self._version}")
            else:
                self._is_available = False
                logger.warning("QPDF not available")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            self._is_available = False
            logger.warning(f"QPDF check failed: {e}")
        
        return self._is_available
    
    def get_version(self) -> Optional[str]:
        """獲取 QPDF 版本"""
        if not self.is_available():
            return None
        return self._version
    
    def execute_operation(self, operation: QPDFOperation) -> QPDFResult:
        """執行單個 QPDF 操作"""
        start_time = time.time()
        
        # 驗證輸入檔案
        if not validate_pdf_file(operation.input_file):
            return QPDFResult(
                success=False,
                operation_type=operation.operation_type,
                input_file=operation.input_file,
                output_file=operation.output_file,
                error_message=f"Invalid PDF file: {operation.input_file}",
                execution_time=time.time() - start_time
            )
        
        # 獲取輸入檔案大小
        file_size_before = os.path.getsize(operation.input_file)
        
        # 構建命令
        cmd = build_qpdf_command(operation)
        cmd[0] = self.qpdf_executable  # 使用配置的可執行檔路徑
        
        try:
            # 執行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 分鐘超時
                encoding='utf-8',
                errors='replace'
            )
            
            execution_time = time.time() - start_time
            
            # 獲取輸出檔案大小
            file_size_after = None
            if operation.output_file and os.path.exists(operation.output_file):
                file_size_after = os.path.getsize(operation.output_file)
            
            # 創建結果對象
            qpdf_result = QPDFResult(
                success=result.returncode == 0,
                operation_type=operation.operation_type,
                input_file=operation.input_file,
                output_file=operation.output_file,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                file_size_before=file_size_before,
                file_size_after=file_size_after
            )
            
            if result.returncode != 0:
                qpdf_result.error_message = result.stderr or "Unknown error occurred"
                logger.error(f"QPDF operation failed: {qpdf_result.error_message}")
            
            return qpdf_result
            
        except subprocess.TimeoutExpired:
            return QPDFResult(
                success=False,
                operation_type=operation.operation_type,
                input_file=operation.input_file,
                output_file=operation.output_file,
                error_message="Operation timed out (5 minutes)",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return QPDFResult(
                success=False,
                operation_type=operation.operation_type,
                input_file=operation.input_file,
                output_file=operation.output_file,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def execute_batch_operations(self, batch_op: QPDFBatchOperation) -> QPDFBatchResult:
        """執行批量操作"""
        start_time = time.time()
        results = []
        
        if batch_op.parallel_execution and len(batch_op.operations) > 1:
            # 並行執行
            with ThreadPoolExecutor(max_workers=batch_op.max_workers) as executor:
                future_to_op = {
                    executor.submit(self.execute_operation, op): op 
                    for op in batch_op.operations
                }
                
                for future in as_completed(future_to_op):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if not result.success and not batch_op.continue_on_error:
                            # 取消剩餘任務
                            for f in future_to_op:
                                if not f.done():
                                    f.cancel()
                            break
                    except Exception as e:
                        op = future_to_op[future]
                        error_result = QPDFResult(
                            success=False,
                            operation_type=op.operation_type,
                            input_file=op.input_file,
                            output_file=op.output_file,
                            error_message=str(e)
                        )
                        results.append(error_result)
        else:
            # 順序執行
            for operation in batch_op.operations:
                result = self.execute_operation(operation)
                results.append(result)
                
                if not result.success and not batch_op.continue_on_error:
                    break
        
        execution_time = time.time() - start_time
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        
        summary = f"完成 {len(results)}/{len(batch_op.operations)} 個操作"
        if successful_count > 0:
            summary += f", 成功: {successful_count}"
        if failed_count > 0:
            summary += f", 失敗: {failed_count}"
        
        return QPDFBatchResult(
            total_operations=len(batch_op.operations),
            successful_operations=successful_count,
            failed_operations=failed_count,
            results=results,
            execution_time=execution_time,
            summary=summary
        )
    
    def get_pdf_info(self, file_path: str, password: Optional[str] = None) -> PDFInfo:
        """獲取 PDF 檔案詳細資訊"""
        info = PDFInfo(file_path=file_path)
        
        if not validate_pdf_file(file_path):
            info.errors.append("Invalid PDF file path")
            return info
        
        try:
            # 使用 QPDF 檢查檔案
            cmd = [self.qpdf_executable, "--check"]
            if password:
                cmd.extend(["--password", password])
            cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            # 解析檢查結果
            if "encrypted" in result.stdout.lower() or "password" in result.stderr.lower():
                info.is_encrypted = True
            
            if "linearized" in result.stdout.lower():
                info.is_linearized = True
            
            # 使用 JSON 模式獲取詳細資訊
            json_cmd = [self.qpdf_executable, "--json", "--json-key=pages"]
            if password:
                json_cmd.extend(["--password", password])
            json_cmd.append(file_path)
            
            json_result = subprocess.run(
                json_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            if json_result.returncode == 0:
                try:
                    data = json.loads(json_result.stdout)
                    if "pages" in data:
                        info.page_count = len(data["pages"])
                    
                    # 提取版本資訊
                    if "version" in data:
                        info.pdf_version = data["version"]
                    
                    # 檢查是否有附件
                    if "attachments" in data:
                        info.has_attachments = len(data["attachments"]) > 0
                    
                except json.JSONDecodeError:
                    info.warnings.append("Could not parse JSON output")
            
            # 獲取檔案大小
            info.file_size = os.path.getsize(file_path)
            
            # 如果有錯誤，記錄到 warnings 或 errors
            if result.returncode != 0:
                if result.stderr:
                    if "password" in result.stderr.lower():
                        info.warnings.append("File is password protected")
                    else:
                        info.errors.append(result.stderr.strip())
            
        except subprocess.TimeoutExpired:
            info.errors.append("Operation timed out")
        except Exception as e:
            info.errors.append(str(e))
        
        return info
    
    def check_pdf_integrity(self, file_path: str, password: Optional[str] = None) -> Tuple[bool, str]:
        """檢查 PDF 檔案完整性"""
        try:
            cmd = [self.qpdf_executable, "--check"]
            if password:
                cmd.extend(["--password", password])
            cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                return True, "PDF file is valid"
            else:
                return False, result.stderr or "PDF file validation failed"
                
        except Exception as e:
            return False, str(e)
    
    def repair_pdf(self, input_file: str, output_file: str, password: Optional[str] = None) -> QPDFResult:
        """修復 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.REPAIR,
            input_file=input_file,
            output_file=output_file,
            password=password
        )
        
        # QPDF 的修復通常通過重新寫入來實現
        operation.normalize_content = True
        
        return self.execute_operation(operation)
    
    def optimize_pdf(self, input_file: str, output_file: str, password: Optional[str] = None) -> QPDFResult:
        """優化 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.COMPRESS_STREAMS,
            input_file=input_file,
            output_file=output_file,
            password=password,
            remove_unreferenced=True,
            normalize_content=True
        )
        
        return self.execute_operation(operation)


def validate_qpdf_available() -> bool:
    """驗證 QPDF 是否可用"""
    engine = QPDFEngine()
    return engine.is_available()


def get_qpdf_version() -> Optional[str]:
    """獲取 QPDF 版本"""
    engine = QPDFEngine()
    return engine.get_version()


# 預設引擎實例
default_engine = QPDFEngine()