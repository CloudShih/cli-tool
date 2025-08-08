"""
Ripgrep 結果解析器
解析 ripgrep 的各種輸出格式
"""
import json
import re
import logging
from typing import List, Iterator, Optional, Tuple, Dict
from .data_models import (
    SearchMatch, FileResult, HighlightSpan, 
    create_search_match_from_ripgrep_json,
    create_file_result_from_ripgrep_json
)

logger = logging.getLogger(__name__)


class ANSIProcessor:
    """ANSI 逸出序列處理器"""
    
    # ANSI 顏色碼模式
    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    
    # 常見的 ANSI 顏色碼
    ANSI_CODES = {
        '\x1b[1;31m': 'match_start',    # 紅色粗體 - 匹配開始
        '\x1b[0m': 'reset',             # 重設
        '\x1b[35m': 'filename',         # 紫色 - 檔案名稱
        '\x1b[32m': 'line_number',      # 綠色 - 行號
    }
    
    @classmethod
    def strip_ansi_codes(cls, text: str) -> str:
        """移除 ANSI 顏色碼"""
        if not text:
            return text
        return cls.ANSI_PATTERN.sub('', text)
    
    @classmethod
    def extract_highlights(cls, text: str) -> Tuple[str, List[HighlightSpan]]:
        """提取高亮區域資訊並返回純文字和高亮範圍"""
        if not text:
            return text, []
        
        highlights = []
        clean_text = ""
        current_pos = 0
        in_match = False
        match_start = 0
        
        # 處理每個 ANSI 碼
        last_end = 0
        for match in cls.ANSI_PATTERN.finditer(text):
            # 添加 ANSI 碼前的文字
            clean_text += text[last_end:match.start()]
            
            code = match.group()
            if code in cls.ANSI_CODES:
                code_type = cls.ANSI_CODES[code]
                
                if code_type == 'match_start' and not in_match:
                    # 匹配開始
                    match_start = len(clean_text)
                    in_match = True
                elif code_type == 'reset' and in_match:
                    # 匹配結束
                    match_end = len(clean_text)
                    if match_end > match_start:
                        highlights.append(HighlightSpan(match_start, match_end))
                    in_match = False
            
            last_end = match.end()
        
        # 添加剩餘文字
        clean_text += text[last_end:]
        
        # 處理未閉合的匹配
        if in_match:
            highlights.append(HighlightSpan(match_start, len(clean_text)))
        
        return clean_text, highlights


class RipgrepParser:
    """Ripgrep 輸出解析器 - 支援多種輸出格式"""
    
    def __init__(self):
        self.ansi_processor = ANSIProcessor()
        self.parsers = {
            'json': self._parse_json_output,
            'vimgrep': self._parse_vimgrep_output,
            'default': self._parse_default_output,
        }
    
    def parse_output(self, output: str, format_type: str = 'json') -> List[FileResult]:
        """統一解析介面"""
        if not output or not output.strip():
            return []
        
        parser = self.parsers.get(format_type, self.parsers['json'])
        
        try:
            results = parser(output)
            logger.debug(f"Parsed {len(results)} file results using {format_type} parser")
            return results
        except Exception as e:
            logger.error(f"Error parsing output with {format_type} parser: {e}")
            # 嘗試回退到預設解析器
            if format_type != 'default':
                logger.info("Attempting fallback to default parser")
                return self._parse_default_output(output)
            return []
    
    def parse_streaming_output(self, output_lines: Iterator[str], format_type: str = 'json') -> Iterator[FileResult]:
        """串流解析輸出 - 逐行處理"""
        current_file_data = {}
        
        for line in output_lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                if format_type == 'json':
                    # 處理 JSON 串流
                    for result in self._parse_json_line(line, current_file_data):
                        yield result
                else:
                    # 處理其他格式的行
                    result = self._parse_single_line(line, format_type)
                    if result:
                        yield result
                        
            except Exception as e:
                logger.warning(f"Error parsing line: {line[:100]}... - {e}")
                continue
    
    def _parse_json_output(self, output: str) -> List[FileResult]:
        """解析 JSON 格式輸出"""
        results = []
        file_results = {}  # file_path -> FileResult
        
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
                
            try:
                data = json.loads(line)
                file_result = self._process_json_data(data, file_results)
                if file_result and file_result not in results:
                    results.append(file_result)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON line: {line[:100]}... - {e}")
                continue
        
        return results
    
    def _parse_json_line(self, line: str, file_data_cache: dict) -> List[FileResult]:
        """解析單行 JSON 資料 - 用於串流處理"""
        if not line.startswith('{'):
            return []
        
        try:
            data = json.loads(line)
            file_result = self._process_json_data(data, file_data_cache)
            return [file_result] if file_result else []
        except json.JSONDecodeError:
            return []
    
    def _process_json_data(self, data: dict, file_cache: dict) -> Optional[FileResult]:
        """處理 JSON 資料項"""
        data_type = data.get('type')
        
        if data_type == 'match':
            # 匹配資料
            match_data = data.get('data', {})
            file_path = match_data.get('path', {}).get('text', '')
            
            if not file_path:
                return None
            
            # 獲取或創建檔案結果
            if file_path not in file_cache:
                file_cache[file_path] = FileResult(file_path=file_path)
            
            file_result = file_cache[file_path]
            
            # 創建匹配項
            match = self._create_match_from_json(match_data)
            if match:
                file_result.add_match(match)
                return file_result
        
        elif data_type == 'context':
            # 上下文資料 - 可以用來增強匹配項的上下文
            match_data = data.get('data', {})
            file_path = match_data.get('path', {}).get('text', '')
            
            if file_path in file_cache:
                # 將上下文資料添加到最近的匹配項
                file_result = file_cache[file_path]
                if file_result.matches:
                    last_match = file_result.matches[-1]
                    context_line = match_data.get('lines', {}).get('text', '')
                    line_number = match_data.get('line_number', 0)
                    
                    # 判斷是前置還是後置上下文
                    if line_number < last_match.line_number:
                        last_match.context_before.append(context_line)
                    elif line_number > last_match.line_number:
                        last_match.context_after.append(context_line)
        
        return None
    
    def _create_match_from_json(self, match_data: dict) -> Optional[SearchMatch]:
        """從 JSON 資料創建匹配項"""
        try:
            lines_data = match_data.get('lines', {})
            line_number = match_data.get('line_number', 0)
            content = lines_data.get('text', '')
            
            # 處理子匹配 (高亮區域)
            submatches = match_data.get('submatches', [])
            highlights = []
            
            for submatch in submatches:
                start = submatch.get('start', 0)
                end = submatch.get('end', start)
                if end > start:  # 確保高亮區域有效
                    highlights.append(HighlightSpan(start, end))
            
            return SearchMatch(
                line_number=line_number,
                column=submatches[0].get('start', 0) if submatches else 0,
                content=content,
                highlights=highlights
            )
            
        except Exception as e:
            logger.warning(f"Error creating match from JSON data: {e}")
            return None
    
    def _parse_vimgrep_output(self, output: str) -> List[FileResult]:
        """解析 vimgrep 格式輸出"""
        # 格式: filename:line:col:content
        pattern = re.compile(r'^([^:]+):(\d+):(\d+):(.*)$')
        file_results = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            match = pattern.match(line)
            if not match:
                continue
            
            file_path = match.group(1)
            line_number = int(match.group(2))
            column = int(match.group(3))
            content = match.group(4)
            
            # 處理 ANSI 顏色碼
            clean_content, highlights = self.ansi_processor.extract_highlights(content)
            
            # 創建匹配項
            search_match = SearchMatch(
                line_number=line_number,
                column=column,
                content=clean_content,
                highlights=highlights
            )
            
            # 添加到檔案結果
            if file_path not in file_results:
                file_results[file_path] = FileResult(file_path=file_path)
            
            file_results[file_path].add_match(search_match)
        
        return list(file_results.values())
    
    def _parse_default_output(self, output: str) -> List[FileResult]:
        """解析預設格式輸出 (回退方案)"""
        # 嘗試多種常見格式
        
        # 首先嘗試 vimgrep 格式
        try:
            results = self._parse_vimgrep_output(output)
            if results:
                return results
        except Exception as e:
            logger.warning(f"Vimgrep parsing failed: {e}")
        
        # 嘗試簡單的逐行解析
        return self._parse_simple_format(output)
    
    def _parse_simple_format(self, output: str) -> List[FileResult]:
        """解析簡單格式輸出"""
        file_results = {}
        current_file = None
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 檢查是否是檔案路徑 (不包含 :數字: 模式)
            if not re.search(r':\d+:', line) and ('/' in line or '\\' in line):
                current_file = line
                if current_file not in file_results:
                    file_results[current_file] = FileResult(file_path=current_file)
                continue
            
            # 嘗試提取行號和內容
            line_match = re.match(r'^(\d+)[:\-](.*)$', line)
            if line_match and current_file:
                line_number = int(line_match.group(1))
                content = line_match.group(2).strip()
                
                clean_content, highlights = self.ansi_processor.extract_highlights(content)
                
                search_match = SearchMatch(
                    line_number=line_number,
                    column=0,
                    content=clean_content,
                    highlights=highlights
                )
                
                file_results[current_file].add_match(search_match)
        
        return list(file_results.values())
    
    def _parse_single_line(self, line: str, format_type: str) -> Optional[FileResult]:
        """解析單行輸出 - 用於串流處理"""
        if format_type == 'vimgrep':
            pattern = re.compile(r'^([^:]+):(\d+):(\d+):(.*)$')
            match = pattern.match(line)
            
            if match:
                file_path = match.group(1)
                line_number = int(match.group(2))
                column = int(match.group(3))
                content = match.group(4)
                
                clean_content, highlights = self.ansi_processor.extract_highlights(content)
                
                search_match = SearchMatch(
                    line_number=line_number,
                    column=column,
                    content=clean_content,
                    highlights=highlights
                )
                
                file_result = FileResult(file_path=file_path)
                file_result.add_match(search_match)
                return file_result
        
        return None


# 便利函數
def parse_ripgrep_output(output: str, format_type: str = 'json') -> List[FileResult]:
    """便利函數 - 解析 ripgrep 輸出"""
    parser = RipgrepParser()
    return parser.parse_output(output, format_type)


def parse_ripgrep_streaming(output_lines: Iterator[str], format_type: str = 'json') -> Iterator[FileResult]:
    """便利函數 - 串流解析 ripgrep 輸出"""
    parser = RipgrepParser()
    return parser.parse_streaming_output(output_lines, format_type)