"""
QPDF 模型層
處理業務邏輯和數據管理
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal

from .core.qpdf_engine import QPDFEngine, default_engine
from .core.data_models import (
    QPDFOperation, QPDFResult, PDFInfo, QPDFBatchOperation, QPDFBatchResult,
    QPDFOperationType, EncryptionLevel, CompressionLevel,
    validate_pdf_file, validate_page_range
)
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class QPDFModel(QObject):
    """QPDF 模型類"""
    
    # 信號定義
    operation_started = pyqtSignal(str)  # 操作開始
    operation_completed = pyqtSignal(QPDFResult)  # 操作完成
    operation_failed = pyqtSignal(str)  # 操作失敗
    progress_updated = pyqtSignal(int, str)  # 進度更新
    info_updated = pyqtSignal(PDFInfo)  # PDF 資訊更新
    batch_progress = pyqtSignal(int, int, str)  # 批量操作進度 (完成數量, 總數量, 當前操作)
    
    def __init__(self):
        super().__init__()
        
        # 初始化 QPDF 引擎
        qpdf_config = config_manager.get_tool_config('qpdf')
        qpdf_executable = qpdf_config.get('executable_path', 'qpdf')
        self.engine = QPDFEngine(qpdf_executable)
        
        # 操作歷史
        self.operation_history: List[QPDFResult] = []
        
        # 當前設定
        self.settings = self._load_settings()
        
        # 驗證工具可用性
        self._check_availability()
        
        logger.info("QPDFModel initialized")
    
    def _check_availability(self):
        """檢查 QPDF 工具可用性"""
        if not self.engine.is_available():
            logger.warning("QPDF tool not available")
        else:
            version = self.engine.get_version()
            logger.info(f"QPDF available: {version}")
    
    def _load_settings(self) -> Dict[str, Any]:
        """載入設定"""
        # 在專案根目錄創建設定目錄
        project_root = config_manager.get_resource_path(".")
        settings_dir = project_root / ".cache" / "qpdf"
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_path = settings_dir / "qpdf_settings.json"
        
        default_settings = {
            "default_encryption_level": "256",
            "default_compression_level": "medium",
            "preserve_metadata": True,
            "auto_backup": True,
            "parallel_operations": True,
            "max_workers": 4,
            "output_directory": "",
            "recent_files": [],
            "operation_presets": {}
        }
        
        try:
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                default_settings.update(saved_settings)
        except Exception as e:
            logger.warning(f"Could not load QPDF settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """保存設定"""
        try:
            # 使用與 _load_settings 相同的路徑邏輯
            project_root = config_manager.get_resource_path(".")
            settings_dir = project_root / ".cache" / "qpdf"
            settings_dir.mkdir(parents=True, exist_ok=True)
            settings_path = settings_dir / "qpdf_settings.json"
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save QPDF settings: {e}")
    
    def is_available(self) -> bool:
        """檢查 QPDF 是否可用"""
        return self.engine.is_available()
    
    def get_version(self) -> Optional[str]:
        """獲取 QPDF 版本"""
        return self.engine.get_version()
    
    def check_pdf_file(self, file_path: str, password: Optional[str] = None) -> PDFInfo:
        """檢查 PDF 檔案"""
        self.operation_started.emit(f"檢查 PDF 檔案: {os.path.basename(file_path)}")
        
        try:
            info = self.engine.get_pdf_info(file_path, password)
            self.info_updated.emit(info)
            return info
        except Exception as e:
            logger.error(f"Error checking PDF file: {e}")
            self.operation_failed.emit(str(e))
            return PDFInfo(file_path=file_path, errors=[str(e)])
    
    def decrypt_pdf(self, input_file: str, output_file: str, password: str) -> QPDFResult:
        """解密 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.DECRYPT,
            input_file=input_file,
            output_file=output_file,
            password=password
        )
        
        return self._execute_single_operation(operation, "解密 PDF")
    
    def encrypt_pdf(self, input_file: str, output_file: str, 
                   user_password: str, owner_password: str = "",
                   encryption_level: EncryptionLevel = EncryptionLevel.AES_256,
                   print_allowed: bool = True, modify_allowed: bool = True,
                   extract_allowed: bool = True, annotate_allowed: bool = True) -> QPDFResult:
        """加密 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.ENCRYPT,
            input_file=input_file,
            output_file=output_file,
            encryption_level=encryption_level,
            user_password=user_password,
            owner_password=owner_password or user_password,
            print_allowed=print_allowed,
            modify_allowed=modify_allowed,
            extract_allowed=extract_allowed,
            annotate_allowed=annotate_allowed
        )
        
        return self._execute_single_operation(operation, "加密 PDF")
    
    def linearize_pdf(self, input_file: str, output_file: str, password: Optional[str] = None) -> QPDFResult:
        """線性化 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.LINEARIZE,
            input_file=input_file,
            output_file=output_file,
            password=password
        )
        
        return self._execute_single_operation(operation, "線性化 PDF")
    
    def split_pdf_pages(self, input_file: str, output_pattern: str, 
                       page_range: Optional[str] = None, password: Optional[str] = None) -> QPDFResult:
        """分割 PDF 頁面"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.SPLIT_PAGES,
            input_file=input_file,
            output_file=output_pattern,
            page_range=page_range,
            password=password
        )
        
        return self._execute_single_operation(operation, "分割 PDF 頁面")
    
    def rotate_pdf_pages(self, input_file: str, output_file: str,
                        rotation_angle: int, rotation_pages: str = "1-",
                        password: Optional[str] = None) -> QPDFResult:
        """旋轉 PDF 頁面"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.ROTATE,
            input_file=input_file,
            output_file=output_file,
            rotation_angle=rotation_angle,
            rotation_pages=rotation_pages,
            password=password
        )
        
        return self._execute_single_operation(operation, "旋轉 PDF 頁面")
    
    def compress_pdf(self, input_file: str, output_file: str,
                    compression_level: CompressionLevel = CompressionLevel.MEDIUM,
                    remove_unreferenced: bool = True,
                    password: Optional[str] = None) -> QPDFResult:
        """壓縮 PDF 檔案"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.COMPRESS_STREAMS,
            input_file=input_file,
            output_file=output_file,
            compression_level=compression_level,
            remove_unreferenced=remove_unreferenced,
            normalize_content=True,
            password=password
        )
        
        return self._execute_single_operation(operation, "壓縮 PDF")
    
    def repair_pdf(self, input_file: str, output_file: str, password: Optional[str] = None) -> QPDFResult:
        """修復 PDF 檔案"""
        return self.engine.repair_pdf(input_file, output_file, password)
    
    def get_pdf_json_info(self, input_file: str, password: Optional[str] = None) -> QPDFResult:
        """獲取 PDF 的 JSON 格式資訊"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.JSON_INFO,
            input_file=input_file,
            password=password
        )
        
        return self._execute_single_operation(operation, "獲取 PDF JSON 資訊")
    
    def remove_pdf_restrictions(self, input_file: str, output_file: str, 
                               password: Optional[str] = None) -> QPDFResult:
        """移除 PDF 限制"""
        operation = QPDFOperation(
            operation_type=QPDFOperationType.REMOVE_RESTRICTIONS,
            input_file=input_file,
            output_file=output_file,
            password=password
        )
        
        return self._execute_single_operation(operation, "移除 PDF 限制")
    
    def execute_batch_operations(self, operations: List[QPDFOperation], 
                                parallel: bool = True) -> QPDFBatchResult:
        """執行批量操作"""
        batch_op = QPDFBatchOperation(
            operations=operations,
            parallel_execution=parallel,
            max_workers=self.settings.get("max_workers", 4),
            continue_on_error=True
        )
        
        self.operation_started.emit(f"批量執行 {len(operations)} 個操作")
        
        try:
            result = self.engine.execute_batch_operations(batch_op)
            
            # 更新歷史記錄
            self.operation_history.extend(result.results)
            
            # 發送完成信號
            if result.failed_operations == 0:
                self.operation_completed.emit(None)  # 批量操作沒有單一結果
            else:
                self.operation_failed.emit(f"批量操作完成，但有 {result.failed_operations} 個失敗")
            
            return result
            
        except Exception as e:
            logger.error(f"Batch operation failed: {e}")
            self.operation_failed.emit(str(e))
            return QPDFBatchResult(
                total_operations=len(operations),
                successful_operations=0,
                failed_operations=len(operations),
                summary=f"批量操作失敗: {str(e)}"
            )
    
    def _execute_single_operation(self, operation: QPDFOperation, operation_name: str) -> QPDFResult:
        """執行單個操作的通用方法"""
        self.operation_started.emit(f"{operation_name}: {os.path.basename(operation.input_file)}")
        
        try:
            result = self.engine.execute_operation(operation)
            
            # 添加到歷史記錄
            self.operation_history.append(result)
            
            # 更新最近使用的檔案
            self._add_recent_file(operation.input_file)
            
            # 發送信號
            if result.success:
                self.operation_completed.emit(result)
            else:
                self.operation_failed.emit(result.error_message or "操作失敗")
            
            return result
            
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            self.operation_failed.emit(str(e))
            
            # 創建失敗結果
            result = QPDFResult(
                success=False,
                operation_type=operation.operation_type,
                input_file=operation.input_file,
                output_file=operation.output_file,
                error_message=str(e)
            )
            self.operation_history.append(result)
            return result
    
    def _add_recent_file(self, file_path: str):
        """添加到最近使用的檔案"""
        recent_files = self.settings.get("recent_files", [])
        
        # 移除已存在的相同路徑
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到開頭
        recent_files.insert(0, file_path)
        
        # 限制數量
        recent_files = recent_files[:10]
        
        self.settings["recent_files"] = recent_files
        self.save_settings()
    
    def get_recent_files(self) -> List[str]:
        """獲取最近使用的檔案"""
        recent_files = self.settings.get("recent_files", [])
        # 過濾掉不存在的檔案
        return [f for f in recent_files if os.path.exists(f)]
    
    def clear_history(self):
        """清除操作歷史"""
        self.operation_history.clear()
    
    def export_history(self, file_path: str) -> bool:
        """匯出操作歷史"""
        try:
            history_data = []
            for result in self.operation_history:
                history_data.append({
                    "operation_type": result.operation_type.value,
                    "input_file": result.input_file,
                    "output_file": result.output_file,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "file_size_before": result.file_size_before,
                    "file_size_after": result.file_size_after,
                    "error_message": result.error_message
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            return False
    
    def validate_operation_inputs(self, operation_type: QPDFOperationType, 
                                 input_file: str, output_file: Optional[str] = None,
                                 page_range: Optional[str] = None) -> List[str]:
        """驗證操作輸入"""
        errors = []
        
        # 檢查輸入檔案
        if not input_file:
            errors.append("請選擇輸入檔案")
        elif not validate_pdf_file(input_file):
            errors.append("輸入檔案不是有效的 PDF 檔案")
        
        # 檢查輸出檔案
        if operation_type != QPDFOperationType.CHECK and operation_type != QPDFOperationType.JSON_INFO:
            if not output_file:
                errors.append("請指定輸出檔案")
            elif input_file == output_file:
                errors.append("輸出檔案不能與輸入檔案相同")
        
        # 檢查頁面範圍
        if page_range and not validate_page_range(page_range):
            errors.append("頁面範圍格式無效 (例如: 1-5, 1,3,5, 1-)")
        
        return errors