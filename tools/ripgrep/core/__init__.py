"""
Ripgrep 核心模組
包含搜尋引擎、資料模型、解析器和非同步工作器
"""

from .data_models import (
    SearchStatus,
    HighlightSpan,
    SearchMatch,
    FileResult,
    SearchParameters,
    SearchSummary,
    SearchResultCollection,
    create_search_match_from_ripgrep_json,
    create_file_result_from_ripgrep_json
)

from .result_parser import (
    ANSIProcessor,
    RipgrepParser,
    parse_ripgrep_output,
    parse_ripgrep_streaming
)

from .search_engine import (
    RipgrepCommandBuilder,
    RipgrepEngine,
    create_search_engine,
    validate_ripgrep_available
)

from .async_worker import (
    SearchProgressTracker,
    RipgrepSearchWorker,
    SearchResultBuffer,
    create_search_worker
)

__all__ = [
    # 資料模型
    'SearchStatus',
    'HighlightSpan',
    'SearchMatch',
    'FileResult',
    'SearchParameters',
    'SearchSummary',
    'SearchResultCollection',
    'create_search_match_from_ripgrep_json',
    'create_file_result_from_ripgrep_json',
    
    # 結果解析器
    'ANSIProcessor',
    'RipgrepParser',
    'parse_ripgrep_output',
    'parse_ripgrep_streaming',
    
    # 搜尋引擎
    'RipgrepCommandBuilder',
    'RipgrepEngine',
    'create_search_engine',
    'validate_ripgrep_available',
    
    # 非同步工作器
    'SearchProgressTracker',
    'RipgrepSearchWorker',
    'SearchResultBuffer',
    'create_search_worker',
]