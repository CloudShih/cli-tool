"""
QPDF 數據模型
定義 PDF 處理相關的數據結構和枚舉
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path


class QPDFOperationType(Enum):
    """QPDF 操作類型"""
    CHECK = "check"
    DECRYPT = "decrypt"
    ENCRYPT = "encrypt"
    LINEARIZE = "linearize"
    SPLIT_PAGES = "split_pages"
    MERGE = "merge"
    ROTATE = "rotate"
    REPAIR = "repair"
    JSON_INFO = "json_info"
    OBJECT_STREAMS = "object_streams"
    COMPRESS_STREAMS = "compress_streams"
    REMOVE_RESTRICTIONS = "remove_restrictions"
    ADD_ATTACHMENTS = "add_attachments"
    EXTRACT_ATTACHMENTS = "extract_attachments"


class EncryptionLevel(Enum):
    """加密等級"""
    RC4_40 = "40"      # 40-bit RC4
    RC4_128 = "128"    # 128-bit RC4
    AES_128 = "256"    # 128-bit AES
    AES_256 = "256R6"  # 256-bit AES


class CompressionLevel(Enum):
    """壓縮等級"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class QPDFOperation:
    """QPDF 操作參數"""
    operation_type: QPDFOperationType
    input_file: str
    output_file: Optional[str] = None
    password: Optional[str] = None
    
    # 加密選項
    encryption_level: Optional[EncryptionLevel] = None
    user_password: Optional[str] = None
    owner_password: Optional[str] = None
    print_allowed: bool = True
    modify_allowed: bool = True
    extract_allowed: bool = True
    annotate_allowed: bool = True
    
    # 分頁選項
    page_range: Optional[str] = None  # e.g., "1-5", "1,3,5", "1-"
    
    # 旋轉選項
    rotation_angle: int = 0  # 0, 90, 180, 270
    rotation_pages: Optional[str] = None
    
    # 壓縮選項
    compression_level: Optional[CompressionLevel] = None
    remove_unreferenced: bool = False
    
    # 檢查選項
    check_linearization: bool = False
    show_data: bool = False
    
    # JSON 輸出選項
    json_keys: Optional[List[str]] = None
    json_objects: Optional[str] = None
    
    # 附件選項
    attachment_files: List[str] = field(default_factory=list)
    attachment_names: List[str] = field(default_factory=list)
    
    # 其他選項
    preserve_unreferenced: bool = False
    normalize_content: bool = False
    suppress_recovery: bool = False


@dataclass
class QPDFResult:
    """QPDF 操作結果"""
    success: bool
    operation_type: QPDFOperationType
    input_file: str
    output_file: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    file_size_before: Optional[int] = None
    file_size_after: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class PDFInfo:
    """PDF 檔案資訊"""
    file_path: str
    is_encrypted: bool = False
    is_linearized: bool = False
    pdf_version: Optional[str] = None
    page_count: Optional[int] = None
    has_attachments: bool = False
    has_forms: bool = False
    has_annotations: bool = False
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    file_size: Optional[int] = None
    encryption_details: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class QPDFBatchOperation:
    """批量 QPDF 操作"""
    operations: List[QPDFOperation] = field(default_factory=list)
    parallel_execution: bool = False
    max_workers: int = 4
    continue_on_error: bool = True
    output_directory: Optional[str] = None


@dataclass
class QPDFBatchResult:
    """批量操作結果"""
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[QPDFResult] = field(default_factory=list)
    execution_time: float = 0.0
    summary: str = ""


def validate_pdf_file(file_path: str) -> bool:
    """驗證 PDF 檔案路徑"""
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and path.suffix.lower() == '.pdf'
    except Exception:
        return False


def validate_page_range(page_range: str) -> bool:
    """驗證頁面範圍格式"""
    if not page_range:
        return True
    
    try:
        # 支援格式: "1-5", "1,3,5", "1-", "1-5,7,9-12"
        import re
        pattern = r'^(\d+(-\d*)?|\d+)(,(\d+(-\d*)?|\d+))*$'
        return bool(re.match(pattern, page_range.replace(' ', '')))
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化檔案大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def estimate_compression_ratio(operation: QPDFOperation) -> float:
    """估算壓縮比率"""
    base_ratio = 0.8  # 基礎壓縮比率
    
    if operation.compression_level == CompressionLevel.HIGH:
        return base_ratio * 0.7
    elif operation.compression_level == CompressionLevel.MEDIUM:
        return base_ratio * 0.85
    elif operation.compression_level == CompressionLevel.LOW:
        return base_ratio * 0.95
    else:
        return base_ratio


def get_encryption_description(level: EncryptionLevel) -> str:
    """獲取加密等級描述"""
    descriptions = {
        EncryptionLevel.RC4_40: "40-bit RC4 加密 (較低安全性)",
        EncryptionLevel.RC4_128: "128-bit RC4 加密 (中等安全性)",
        EncryptionLevel.AES_128: "128-bit AES 加密 (高安全性)",
        EncryptionLevel.AES_256: "256-bit AES 加密 (最高安全性)"
    }
    return descriptions.get(level, "未知加密等級")


def build_qpdf_command(operation: QPDFOperation) -> List[str]:
    """構建 QPDF 命令行參數"""
    cmd = ["qpdf"]
    
    # 基本選項
    if operation.password:
        cmd.append(f"--password={operation.password}")
    
    # 根據操作類型添加參數
    if operation.operation_type == QPDFOperationType.CHECK:
        cmd.append("--check")
        if operation.check_linearization:
            cmd.append("--check-linearization")
        if operation.show_data:
            cmd.append("--show-data")
    
    elif operation.operation_type == QPDFOperationType.DECRYPT:
        cmd.append("--decrypt")
    
    elif operation.operation_type == QPDFOperationType.ENCRYPT:
        if operation.encryption_level:
            cmd.extend(["--encrypt", 
                       operation.user_password or "",
                       operation.owner_password or "",
                       operation.encryption_level.value])
            
            # 權限設定
            if not operation.print_allowed:
                cmd.append("--print=none")
            if not operation.modify_allowed:
                cmd.append("--modify=none")
            if not operation.extract_allowed:
                cmd.append("--extract=n")
            if not operation.annotate_allowed:
                cmd.append("--annotate=n")
            
            cmd.append("--")
    
    elif operation.operation_type == QPDFOperationType.LINEARIZE:
        cmd.append("--linearize")
    
    elif operation.operation_type == QPDFOperationType.SPLIT_PAGES:
        cmd.append("--split-pages")
        if operation.page_range:
            cmd.extend(["--pages", operation.input_file, operation.page_range, "--"])
    
    elif operation.operation_type == QPDFOperationType.JSON_INFO:
        cmd.append("--json")
        if operation.json_keys:
            for key in operation.json_keys:
                cmd.append(f"--json-key={key}")
        if operation.json_objects:
            cmd.append(f"--json-object={operation.json_objects}")
    
    elif operation.operation_type == QPDFOperationType.ROTATE:
        if operation.rotation_angle and operation.rotation_pages:
            cmd.append(f"--rotate={operation.rotation_angle}:{operation.rotation_pages}")
    
    # 壓縮選項
    if operation.compression_level:
        if operation.compression_level == CompressionLevel.HIGH:
            cmd.extend(["--compress-streams=y", "--decode-level=all"])
        elif operation.compression_level == CompressionLevel.NONE:
            cmd.append("--compress-streams=n")
    
    if operation.remove_unreferenced:
        cmd.append("--remove-unreferenced-resources")
    
    if operation.normalize_content:
        cmd.append("--normalize-content=y")
    
    if operation.suppress_recovery:
        cmd.append("--suppress-recovery")
    
    # 輸入和輸出檔案
    cmd.append(operation.input_file)
    if operation.output_file:
        cmd.append(operation.output_file)
    
    return cmd