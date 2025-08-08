"""
Ripgrep 資料模型定義
定義搜尋相關的所有資料結構
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class SearchStatus(Enum):
    """搜尋狀態枚舉"""
    IDLE = "idle"
    SEARCHING = "searching"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class HighlightSpan:
    """高亮區域資料結構"""
    start: int
    end: int
    highlight_type: str = 'match'
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'start': self.start,
            'end': self.end,
            'type': self.highlight_type
        }


@dataclass
class SearchMatch:
    """搜尋匹配項資料結構"""
    line_number: int
    column: int
    content: str
    highlights: List[HighlightSpan] = field(default_factory=list)
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'line_number': self.line_number,
            'column': self.column,
            'content': self.content,
            'highlights': [h.to_dict() for h in self.highlights],
            'context_before': self.context_before,
            'context_after': self.context_after
        }


@dataclass
class FileResult:
    """檔案搜尋結果資料結構"""
    file_path: str
    matches: List[SearchMatch] = field(default_factory=list)
    total_matches: int = 0
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    
    def __post_init__(self):
        """後處理 - 自動計算總匹配數"""
        if self.total_matches == 0:
            self.total_matches = len(self.matches)
    
    def add_match(self, match: SearchMatch):
        """添加匹配項"""
        self.matches.append(match)
        self.total_matches = len(self.matches)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'file_path': self.file_path,
            'total_matches': self.total_matches,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'matches': [m.to_dict() for m in self.matches]
        }


@dataclass
class SearchParameters:
    """搜尋參數資料結構"""
    pattern: str
    search_path: str = "."
    case_sensitive: bool = False
    whole_words: bool = False
    regex_mode: bool = False
    multiline: bool = False
    context_lines: int = 3
    max_results: int = 1000
    file_types: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_depth: Optional[int] = None
    follow_symlinks: bool = False
    search_hidden: bool = False
    
    def __post_init__(self):
        """後處理 - 驗證參數"""
        if not self.pattern:
            raise ValueError("Search pattern cannot be empty")
        
        if self.context_lines < 0:
            self.context_lines = 0
        elif self.context_lines > 20:
            self.context_lines = 20
            
        if self.max_results < 1:
            self.max_results = 1000
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'pattern': self.pattern,
            'search_path': self.search_path,
            'case_sensitive': self.case_sensitive,
            'whole_words': self.whole_words,
            'regex_mode': self.regex_mode,
            'multiline': self.multiline,
            'context_lines': self.context_lines,
            'max_results': self.max_results,
            'file_types': self.file_types,
            'exclude_patterns': self.exclude_patterns,
            'max_depth': self.max_depth,
            'follow_symlinks': self.follow_symlinks,
            'search_hidden': self.search_hidden
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchParameters':
        """從字典創建實例"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SearchSummary:
    """搜尋結果摘要"""
    pattern: str
    total_matches: int = 0
    files_with_matches: int = 0
    files_searched: int = 0
    search_time: float = 0.0
    status: SearchStatus = SearchStatus.IDLE
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'pattern': self.pattern,
            'total_matches': self.total_matches,
            'files_with_matches': self.files_with_matches,
            'files_searched': self.files_searched,
            'search_time': self.search_time,
            'status': self.status.value,
            'error_message': self.error_message
        }


class SearchResultCollection:
    """搜尋結果集合 - 管理多個檔案結果"""
    
    def __init__(self):
        self.file_results: List[FileResult] = []
        self.summary = SearchSummary("")
        self._file_index: Dict[str, FileResult] = {}
    
    def add_file_result(self, file_result: FileResult):
        """添加檔案結果"""
        if file_result.file_path in self._file_index:
            # 合併已存在的檔案結果
            existing = self._file_index[file_result.file_path]
            existing.matches.extend(file_result.matches)
            existing.total_matches = len(existing.matches)
        else:
            self.file_results.append(file_result)
            self._file_index[file_result.file_path] = file_result
    
    def get_file_result(self, file_path: str) -> Optional[FileResult]:
        """獲取特定檔案的結果"""
        return self._file_index.get(file_path)
    
    def update_summary(self, summary: SearchSummary):
        """更新搜尋摘要"""
        self.summary = summary
        # 同步統計資訊
        self.summary.files_with_matches = len(self.file_results)
        self.summary.total_matches = sum(fr.total_matches for fr in self.file_results)
    
    def clear(self):
        """清除所有結果"""
        self.file_results.clear()
        self._file_index.clear()
        self.summary = SearchSummary("")
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'summary': self.summary.to_dict(),
            'files': [fr.to_dict() for fr in self.file_results]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def get_statistics(self) -> dict:
        """獲取統計資訊"""
        if not self.file_results:
            return {
                'files_count': 0,
                'total_matches': 0,
                'avg_matches_per_file': 0,
                'file_types': {}
            }
        
        file_types = {}
        for fr in self.file_results:
            if fr.file_type:
                file_types[fr.file_type] = file_types.get(fr.file_type, 0) + 1
        
        return {
            'files_count': len(self.file_results),
            'total_matches': self.summary.total_matches,
            'avg_matches_per_file': self.summary.total_matches / len(self.file_results),
            'file_types': file_types
        }


# 輔助函數
def create_search_match_from_ripgrep_json(data: dict) -> SearchMatch:
    """從 ripgrep JSON 資料創建 SearchMatch"""
    submatches = data.get('submatches', [])
    highlights = []
    
    for submatch in submatches:
        start = submatch.get('start', 0)
        end = submatch.get('end', start)
        highlights.append(HighlightSpan(start, end))
    
    return SearchMatch(
        line_number=data.get('line_number', 0),
        column=submatches[0].get('start', 0) if submatches else 0,
        content=data.get('lines', {}).get('text', ''),
        highlights=highlights
    )


def create_file_result_from_ripgrep_json(file_path: str, matches_data: List[dict]) -> FileResult:
    """從 ripgrep JSON 資料創建 FileResult"""
    file_result = FileResult(file_path=file_path)
    
    for match_data in matches_data:
        if match_data.get('type') == 'match':
            match = create_search_match_from_ripgrep_json(match_data['data'])
            file_result.add_match(match)
    
    return file_result