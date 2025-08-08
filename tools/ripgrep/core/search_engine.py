"""
Ripgrep 搜尋引擎
處理 ripgrep 命令的建構和執行
"""
import os
import shlex
import platform
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from .data_models import SearchParameters

logger = logging.getLogger(__name__)


class RipgrepCommandBuilder:
    """Ripgrep 命令建構器"""
    
    def __init__(self, executable_path: str = "rg"):
        self.executable_path = executable_path
        self._validate_executable()
    
    def _validate_executable(self):
        """驗證 ripgrep 執行檔是否可用"""
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            if result.returncode != 0:
                raise FileNotFoundError(f"Ripgrep executable not working: {self.executable_path}")
                
            logger.debug(f"Ripgrep version: {result.stdout.split()[1] if len(result.stdout.split()) > 1 else 'Unknown'}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise FileNotFoundError(f"Ripgrep executable not found: {self.executable_path} - {e}")
    
    def build_command(self, search_params: SearchParameters, output_format: str = 'json') -> List[str]:
        """建構 ripgrep 命令"""
        cmd = [self.executable_path]
        
        # 基本搜尋模式
        cmd.append(search_params.pattern)
        
        # 搜尋路徑
        if search_params.search_path and search_params.search_path != ".":
            # 確保路徑存在
            if os.path.exists(search_params.search_path):
                cmd.append(search_params.search_path)
            else:
                logger.warning(f"Search path does not exist: {search_params.search_path}")
                cmd.append(".")
        else:
            cmd.append(".")
        
        # 輸出格式
        if output_format == 'json':
            cmd.append('--json')
        elif output_format == 'vimgrep':
            cmd.append('--vimgrep')
        
        # 基本選項
        if not search_params.case_sensitive:
            cmd.append('--ignore-case')
        
        if search_params.whole_words:
            cmd.append('--word-regexp')
        
        if not search_params.regex_mode:
            cmd.append('--fixed-strings')
        
        if search_params.multiline:
            cmd.extend(['--multiline', '--multiline-dotall'])
        
        # 上下文行數
        if search_params.context_lines > 0:
            cmd.extend(['-C', str(search_params.context_lines)])
        
        # 結果限制
        if search_params.max_results > 0:
            cmd.extend(['--max-count', str(search_params.max_results)])
        
        # 檔案類型篩選
        if search_params.file_types:
            for file_type in search_params.file_types:
                file_type = file_type.strip()
                if not file_type:
                    continue
                    
                if file_type.startswith('*.'):
                    # Glob 模式 (例如: *.py, *.js)
                    cmd.extend(['--glob', file_type])
                elif file_type.startswith('.'):
                    # 擴展名模式，轉換為 glob (例如: .py -> *.py)
                    cmd.extend(['--glob', f'*{file_type}'])
                else:
                    # 類型名稱 (例如: py, js)
                    cmd.extend(['--type', file_type])
        
        # 排除模式
        if search_params.exclude_patterns:
            for exclude_pattern in search_params.exclude_patterns:
                cmd.extend(['--glob', f'!{exclude_pattern}'])
        
        # 深度限制
        if search_params.max_depth is not None and search_params.max_depth > 0:
            cmd.extend(['--max-depth', str(search_params.max_depth)])
        
        # 特殊選項
        if not search_params.follow_symlinks:
            cmd.append('--no-follow')
        
        if not search_params.search_hidden:
            cmd.append('--no-hidden')
        
        # 效能優化選項
        cmd.extend([
            '--line-number',        # 顯示行號
            '--column',             # 顯示列號
            '--no-heading',         # 每行包含檔案名
            '--color=always',       # 保持顏色輸出用於高亮
            '--threads', '0',       # 自動選擇執行緒數
        ])
        
        logger.debug(f"Built ripgrep command: {' '.join(shlex.quote(arg) for arg in cmd)}")
        return cmd
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """獲取支援的檔案類型"""
        try:
            result = subprocess.run(
                [self.executable_path, '--type-list'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning("Failed to get ripgrep type list")
                return self._get_default_file_types()
            
            types = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    type_name, extensions = line.split(':', 1)
                    type_name = type_name.strip()
                    extensions = [ext.strip().lstrip('*.') for ext in extensions.split(',')]
                    types[type_name] = extensions
            
            return types
            
        except Exception as e:
            logger.warning(f"Error getting file types: {e}")
            return self._get_default_file_types()
    
    def _get_default_file_types(self) -> Dict[str, List[str]]:
        """獲取預設檔案類型"""
        return {
            'py': ['py', 'pyi', 'pyw'],
            'js': ['js', 'jsx', 'mjs'],
            'ts': ['ts', 'tsx'],
            'html': ['html', 'htm'],
            'css': ['css', 'scss', 'sass', 'less'],
            'md': ['md', 'markdown', 'mdown'],
            'json': ['json', 'jsonl'],
            'yaml': ['yaml', 'yml'],
            'xml': ['xml', 'xsl', 'xslt'],
            'txt': ['txt', 'text'],
            'log': ['log', 'logs'],
            'java': ['java'],
            'c': ['c', 'h'],
            'cpp': ['cpp', 'cc', 'cxx', 'hpp', 'hxx'],
            'go': ['go'],
            'rust': ['rs'],
            'php': ['php'],
            'rb': ['rb', 'ruby'],
            'sh': ['sh', 'bash', 'zsh'],
            'ps1': ['ps1', 'psm1'],
            'sql': ['sql'],
        }


class RipgrepEngine:
    """Ripgrep 搜尋引擎"""
    
    def __init__(self, executable_path: str = "rg"):
        self.command_builder = RipgrepCommandBuilder(executable_path)
        self.current_process: Optional[subprocess.Popen] = None
        self._platform = platform.system().lower()
    
    def search(self, search_params: SearchParameters, output_format: str = 'json') -> subprocess.Popen:
        """執行搜尋 - 返回 Popen 物件供非同步處理"""
        command = self.command_builder.build_command(search_params, output_format)
        
        # 平台特定的執行設定
        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'encoding': 'utf-8',    # 強制使用 UTF-8 編碼
            'errors': 'replace',    # 遇到編碼錯誤時替換為佔位符
            'bufsize': 1,  # 行緩衝
            'universal_newlines': True,
        }
        
        if self._platform == 'windows':
            # Windows 特定設定
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            kwargs['shell'] = False
        else:
            # Unix-like 系統設定
            kwargs['preexec_fn'] = os.setsid  # 創建新的進程組
        
        try:
            self.current_process = subprocess.Popen(command, **kwargs)
            logger.info(f"Started ripgrep search with PID: {self.current_process.pid}")
            return self.current_process
            
        except Exception as e:
            logger.error(f"Failed to start ripgrep process: {e}")
            raise RuntimeError(f"Failed to execute ripgrep: {e}")
    
    def search_sync(self, search_params: SearchParameters, output_format: str = 'json', 
                   timeout: Optional[float] = None) -> tuple[str, str, int]:
        """同步搜尋 - 等待完成並返回結果"""
        process = self.search(search_params, output_format)
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
            
            logger.debug(f"Ripgrep process completed with return code: {returncode}")
            return stdout, stderr, returncode
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Ripgrep search timeout after {timeout} seconds")
            self.cancel_search()
            raise TimeoutError(f"Search timeout after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error during search execution: {e}")
            self.cancel_search()
            raise
    
    def cancel_search(self):
        """取消當前搜尋"""
        if self.current_process and self.current_process.poll() is None:
            try:
                if self._platform == 'windows':
                    # Windows: 終止進程
                    self.current_process.terminate()
                else:
                    # Unix-like: 終止整個進程組
                    os.killpg(os.getpgid(self.current_process.pid), subprocess.signal.SIGTERM)
                
                # 等待進程結束
                self.current_process.wait(timeout=5)
                logger.info("Ripgrep search cancelled successfully")
                
            except subprocess.TimeoutExpired:
                # 強制終止
                if self._platform == 'windows':
                    self.current_process.kill()
                else:
                    os.killpg(os.getpgid(self.current_process.pid), subprocess.signal.SIGKILL)
                
                logger.warning("Ripgrep search force killed")
                
            except Exception as e:
                logger.error(f"Error cancelling ripgrep search: {e}")
            
            finally:
                self.current_process = None
    
    def is_searching(self) -> bool:
        """檢查是否正在搜尋"""
        return self.current_process is not None and self.current_process.poll() is None
    
    def get_supported_file_types(self) -> Dict[str, List[str]]:
        """獲取支援的檔案類型"""
        return self.command_builder.get_supported_file_types()
    
    def validate_search_params(self, search_params: SearchParameters) -> List[str]:
        """驗證搜尋參數並返回錯誤列表"""
        errors = []
        
        if not search_params.pattern:
            errors.append("搜尋模式不能為空")
        
        if not os.path.exists(search_params.search_path):
            errors.append(f"搜尋路徑不存在: {search_params.search_path}")
        
        if search_params.regex_mode:
            # 驗證正則表達式語法
            try:
                import re
                re.compile(search_params.pattern)
            except re.error as e:
                errors.append(f"無效的正則表達式: {e}")
        
        if search_params.max_results < 1:
            errors.append("最大結果數必須大於 0")
        
        if search_params.context_lines < 0:
            errors.append("上下文行數不能為負數")
        
        return errors
    
    def get_version(self) -> str:
        """獲取 ripgrep 版本"""
        try:
            result = subprocess.run(
                [self.command_builder.executable_path, '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return version_line.split()[1] if len(version_line.split()) > 1 else "Unknown"
            else:
                return "Unknown"
                
        except Exception as e:
            logger.warning(f"Failed to get ripgrep version: {e}")
            return "Unknown"


# 便利函數
def create_search_engine(executable_path: str = "rg") -> RipgrepEngine:
    """創建搜尋引擎實例"""
    return RipgrepEngine(executable_path)


def validate_ripgrep_available(executable_path: str = "rg") -> bool:
    """驗證 ripgrep 是否可用"""
    try:
        RipgrepCommandBuilder(executable_path)
        return True
    except FileNotFoundError:
        return False