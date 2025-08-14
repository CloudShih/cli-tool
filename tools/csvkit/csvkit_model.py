"""
csvkit 模型類 - 處理 CSV 工具套件的業務邏輯
支援 csvkit 的 15 個核心工具，提供完整的 CSV 處理功能
"""

import subprocess
import logging
import json
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CsvkitModel:
    """csvkit 模型類 - 封裝 csvkit 工具套件的功能"""
    
    # csvkit 工具分類
    INPUT_TOOLS = {
        'in2csv': '將各種表格資料格式轉換為 CSV',
        'sql2csv': '在資料庫上執行 SQL 查詢並輸出 CSV'
    }
    
    PROCESSING_TOOLS = {
        'csvclean': '修復常見的 CSV 格式問題',
        'csvcut': '從 CSV 檔案中擷取和重新排序欄位',
        'csvgrep': '在 CSV 檔案中搜尋模式',
        'csvjoin': '在指定欄位上連接多個 CSV 檔案',
        'csvsort': '按指定欄位排序 CSV 檔案',
        'csvstack': '將多個 CSV 檔案堆疊成一個'
    }
    
    OUTPUT_ANALYSIS_TOOLS = {
        'csvformat': '將 CSV 轉換為不同方言和格式',
        'csvjson': '將 CSV 轉換為 JSON 格式',
        'csvlook': '以格式化表格顯示 CSV 資料',
        'csvpy': '將 CSV 資料載入 Python 直譯器會話',
        'csvsql': '生成 SQL DDL 或使用 SQL 查詢 CSV 檔案',
        'csvstat': '計算 CSV 資料的描述性統計'
    }
    
    def __init__(self):
        self.csvkit_available = self._check_csvkit_availability()
        self.available_tools = self._get_available_tools()
        
    def _check_csvkit_availability(self) -> bool:
        """檢查 csvkit 是否安裝"""
        try:
            result = subprocess.run(['csvstat', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def _get_available_tools(self) -> Dict[str, str]:
        """獲取可用的 csvkit 工具列表"""
        if not self.csvkit_available:
            return {}
            
        available = {}
        all_tools = {**self.INPUT_TOOLS, **self.PROCESSING_TOOLS, **self.OUTPUT_ANALYSIS_TOOLS}
        
        for tool, description in all_tools.items():
            try:
                result = subprocess.run([tool, '--help'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    available[tool] = description
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue
                
        return available
    
    def get_tool_categories(self) -> Dict[str, Dict[str, str]]:
        """獲取工具分類資訊"""
        return {
            '輸入工具': {k: v for k, v in self.INPUT_TOOLS.items() if k in self.available_tools},
            '處理工具': {k: v for k, v in self.PROCESSING_TOOLS.items() if k in self.available_tools},
            '輸出與分析工具': {k: v for k, v in self.OUTPUT_ANALYSIS_TOOLS.items() if k in self.available_tools}
        }
    
    def execute_in2csv(self, input_file: str, format_type: str = 'auto', 
                       sheet: Optional[str] = None, encoding: str = 'utf-8',
                       additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 in2csv 命令 - 將各種格式轉換為 CSV"""
        if 'in2csv' not in self.available_tools:
            return "", "in2csv tool not available", 1
            
        command = ['in2csv']
        
        # 總是明確指定編碼，避免編碼檢測問題
        command.extend(['-e', encoding])
        
        if format_type != 'auto':
            command.extend(['-f', format_type])
        if sheet:
            command.extend(['--sheet', sheet])
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvcut(self, input_file: str, columns: str = None, 
                       exclude_columns: str = None, names_only: bool = False,
                       additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvcut 命令 - 提取和重新排序列"""
        if 'csvcut' not in self.available_tools:
            return "", "csvcut tool not available", 1
            
        command = ['csvcut']
        
        if names_only:
            command.append('-n')
        if columns:
            command.extend(['-c', columns])
        if exclude_columns:
            command.extend(['-C', exclude_columns])
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvgrep(self, input_file: str, pattern: str, column: str = None,
                        regex: bool = False, invert_match: bool = False,
                        additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvgrep 命令 - 在 CSV 文件中搜索模式"""
        if 'csvgrep' not in self.available_tools:
            return "", "csvgrep tool not available", 1
            
        command = ['csvgrep']
        
        if column:
            command.extend(['-c', column])
        if regex:
            command.extend(['-r', pattern])
        else:
            command.extend(['-m', pattern])
        if invert_match:
            command.append('-i')
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvstat(self, input_file: str, columns: str = None,
                        statistics: str = None, no_inference: bool = False,
                        additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvstat 命令 - 計算描述性統計"""
        if 'csvstat' not in self.available_tools:
            return "", "csvstat tool not available", 1
            
        command = ['csvstat']
        
        if columns:
            command.extend(['-c', columns])
        if statistics:
            command.extend(['--type', statistics])
        if no_inference:
            command.append('-I')
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvlook(self, input_file: str, max_rows: int = None,
                        max_columns: int = None, max_column_width: int = None,
                        additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvlook 命令 - 格式化顯示 CSV 數據"""
        if 'csvlook' not in self.available_tools:
            return "", "csvlook tool not available", 1
            
        command = ['csvlook']
        
        if max_rows:
            command.extend(['--max-rows', str(max_rows)])
        if max_columns:
            command.extend(['--max-columns', str(max_columns)])
        if max_column_width:
            command.extend(['--max-column-width', str(max_column_width)])
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvjson(self, input_file: str, indent: int = None,
                        key_column: str = None, pretty: bool = False,
                        additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvjson 命令 - 將 CSV 轉換為 JSON"""
        if 'csvjson' not in self.available_tools:
            return "", "csvjson tool not available", 1
            
        command = ['csvjson']
        
        if indent is not None:
            command.extend(['--indent', str(indent)])
        if key_column:
            command.extend(['-k', key_column])
        if pretty:
            command.append('--pretty')
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvsql(self, input_file: str, query: str = None,
                       create_table: bool = False, database_url: str = None,
                       additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvsql 命令 - 使用 SQL 查詢 CSV 或生成 DDL"""
        if 'csvsql' not in self.available_tools:
            return "", "csvsql tool not available", 1
            
        command = ['csvsql']
        
        if create_table:
            command.append('--tables')
        if query:
            command.extend(['--query', query])
        if database_url:
            command.extend(['--db', database_url])
        if additional_args:
            command.extend(additional_args)
            
        command.append(input_file)
        
        return self._execute_command(command)
    
    def execute_csvjoin(self, left_file: str, right_file: str,
                        left_column: str, right_column: str = None,
                        join_type: str = 'inner', additional_args: List[str] = None) -> Tuple[str, str, int]:
        """執行 csvjoin 命令 - 連接多個 CSV 文件"""
        if 'csvjoin' not in self.available_tools:
            return "", "csvjoin tool not available", 1
            
        command = ['csvjoin']
        
        command.extend(['-c', left_column])
        if right_column and right_column != left_column:
            command.extend(['--right-column', right_column])
        if join_type != 'inner':
            command.extend(['--' + join_type])
        if additional_args:
            command.extend(additional_args)
            
        command.extend([left_file, right_file])
        
        return self._execute_command(command)
    
    def execute_custom_command(self, tool: str, args: List[str]) -> Tuple[str, str, int]:
        """執行自定義 csvkit 命令"""
        if tool not in self.available_tools:
            return "", f"{tool} not available", 1
            
        command = [tool] + args
        return self._execute_command(command)
    
    def _execute_command(self, command: List[str]) -> Tuple[str, str, int]:
        """執行命令並返回結果"""
        try:
            logger.info(f"Executing command: {' '.join(command)}")
            
            # 嘗試多種編碼處理方式
            encodings_to_try = ['utf-8', 'cp950', 'big5', 'gbk', 'latin-1']
            
            for encoding in encodings_to_try:
                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        encoding=encoding,
                        errors='replace'
                    )
                    
                    stdout, stderr = process.communicate(timeout=30)
                    
                    # 如果成功且有輸出，返回結果
                    if process.returncode == 0 or stdout or stderr:
                        logger.info(f"Command completed with encoding {encoding}, return code: {process.returncode}")
                        return stdout, stderr, process.returncode
                        
                except UnicodeDecodeError:
                    logger.debug(f"Encoding {encoding} failed, trying next...")
                    continue
                except Exception:
                    break
            
            # 如果所有編碼都失敗，使用 bytes 模式
            logger.warning("All encodings failed, using bytes mode")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout_bytes, stderr_bytes = process.communicate(timeout=30)
            
            # 嘗試解碼 bytes
            def safe_decode(data_bytes):
                for encoding in encodings_to_try:
                    try:
                        return data_bytes.decode(encoding, errors='replace')
                    except:
                        continue
                return data_bytes.decode('utf-8', errors='replace')
            
            stdout = safe_decode(stdout_bytes)
            stderr = safe_decode(stderr_bytes)
            
            logger.info(f"Command completed with bytes mode, return code: {process.returncode}")
            return stdout, stderr, process.returncode
            
        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            return "", "Command timed out after 30 seconds", 1
        except FileNotFoundError:
            logger.error(f"Command not found: {command[0]}")
            return "", f"Command not found: {command[0]}", 1
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return "", f"Error executing command: {str(e)}", 1
    
    def get_tool_help(self, tool: str) -> Tuple[str, str, int]:
        """獲取工具的幫助信息"""
        if tool not in self.available_tools:
            return "", f"{tool} not available", 1
            
        return self._execute_command([tool, '--help'])
    
    def validate_csv_file(self, file_path: str) -> bool:
        """驗證 CSV 文件是否存在且可讀"""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.suffix.lower() in ['.csv', '.tsv', '.txt']
        except Exception:
            return False
    
    def save_result_to_file(self, content: str, suggested_filename: str = None, 
                           file_type: str = "csv") -> Tuple[bool, str]:
        """保存結果到檔案"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QApplication
            import os
            from datetime import datetime
            
            # 生成建議檔名
            if not suggested_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                suggested_filename = f"csvkit_output_{timestamp}.{file_type}"
            
            # 確保有正確的副檔名
            if not suggested_filename.endswith(f".{file_type}"):
                suggested_filename += f".{file_type}"
            
            # 使用文件對話框讓用戶選擇保存位置
            app = QApplication.instance()
            if app:
                file_path, _ = QFileDialog.getSaveFileName(
                    None,
                    f"保存 {file_type.upper()} 檔案",
                    suggested_filename,
                    f"{file_type.upper()} 檔案 (*.{file_type});;所有檔案 (*)"
                )
                
                if not file_path:
                    return False, "用戶取消儲存"
            else:
                # 如果沒有 GUI，保存到當前目錄
                file_path = suggested_filename
            
            # 嘗試不同編碼保存檔案
            encodings_to_try = ['utf-8-sig', 'utf-8', 'cp950', 'big5']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'w', encoding=encoding, newline='') as f:
                        f.write(content)
                    
                    logger.info(f"File saved successfully with encoding {encoding}: {file_path}")
                    return True, file_path
                    
                except UnicodeEncodeError:
                    logger.debug(f"Encoding {encoding} failed for saving, trying next...")
                    continue
                except Exception as e:
                    logger.error(f"Error saving with encoding {encoding}: {e}")
                    continue
            
            # 如果所有編碼都失敗，使用錯誤替換模式
            try:
                with open(file_path, 'w', encoding='utf-8', errors='replace', newline='') as f:
                    f.write(content)
                logger.warning(f"File saved with error replacement: {file_path}")
                return True, file_path
            except Exception as e:
                logger.error(f"Failed to save file: {e}")
                return False, f"儲存失敗: {str(e)}"
                
        except Exception as e:
            logger.error(f"Error in save_result_to_file: {e}")
            return False, f"儲存檔案時發生錯誤: {str(e)}"