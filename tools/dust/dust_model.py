"""
dust 工具的模型層
負責執行 dust 命令並處理結果數據
"""

import subprocess
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from ansi2html import Ansi2HTMLConverter
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class DustModel:
    """dust 磁碟空間分析工具的數據模型"""
    
    def __init__(self):
        """初始化 DustModel"""
        # 從配置管理器獲取 dust 執行檔路徑
        self.dust_executable_path = config_manager.get('tools.dust.executable_path')
        logger.info(f"DustModel initialized with executable path: {self.dust_executable_path}")
    
    def estimate_analysis_time(self, target_path: str) -> Tuple[int, str]:
        """
        估算分析時間和目錄信息
        
        Returns:
            (estimated_timeout_seconds, directory_info)
        """
        try:
            path = Path(target_path)
            if not path.exists():
                return 300, "路徑不存在"
            
            # 快速統計目錄信息
            file_count = 0
            dir_count = 0
            total_size = 0
            
            # 限制統計時間，避免在統計階段就卡住
            start_time = time.time()
            max_scan_time = 30  # 最多花30秒統計
            
            try:
                for root, dirs, files in os.walk(target_path):
                    if time.time() - start_time > max_scan_time:
                        break
                    
                    dir_count += len(dirs)
                    file_count += len(files)
                    
                    # 統計檔案大小
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):
                                total_size += os.path.getsize(file_path)
                        except (OSError, PermissionError):
                            continue
                    
                    # 每處理1000個檔案檢查一次時間
                    if file_count % 1000 == 0 and time.time() - start_time > max_scan_time:
                        break
            
            except (OSError, PermissionError) as e:
                logger.warning(f"Permission denied while scanning {target_path}: {e}")
                return 600, f"無法完整掃描目錄（權限不足），建議使用較長超時時間"
            
            # 格式化大小
            def format_size(size_bytes):
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    return f"{size_bytes/1024:.1f} KB"
                elif size_bytes < 1024**3:
                    return f"{size_bytes/(1024**2):.1f} MB"
                else:
                    return f"{size_bytes/(1024**3):.1f} GB"
            
            # 從配置獲取超時設定
            timeout_settings = config_manager.get('tools.dust.timeout_settings', {})
            base_timeout = timeout_settings.get('base_timeout', 300)
            max_timeout = timeout_settings.get('max_timeout', 1800)
            timeout_per_10k_files = timeout_settings.get('timeout_per_10k_files', 60)
            timeout_per_gb = timeout_settings.get('timeout_per_gb', 30)
            
            # 根據統計結果估算超時時間
            estimated_timeout = base_timeout
            
            # 根據檔案數量調整 (每10k檔案增加60秒)
            file_timeout_addition = (file_count // 10000) * timeout_per_10k_files
            estimated_timeout += file_timeout_addition
            
            # 根據總大小調整 (每GB增加30秒)  
            gb_size = total_size / (1024**3)
            size_timeout_addition = int(gb_size) * timeout_per_gb
            estimated_timeout += size_timeout_addition
            
            # 不超過最大超時時間
            estimated_timeout = min(estimated_timeout, max_timeout)
            
            directory_info = f"約 {file_count} 個檔案, {dir_count} 個目錄, 總大小約 {format_size(total_size)}"
            
            return estimated_timeout, directory_info
            
        except Exception as e:
            logger.error(f"Error estimating analysis time: {e}")
            return 600, f"無法估算（{str(e)}），使用預設超時時間"
    
    def execute_dust_command(
        self, 
        target_path: str = ".", 
        max_depth: Optional[int] = None,
        sort_reverse: bool = True,
        number_of_lines: Optional[int] = None,
        file_types: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        show_apparent_size: bool = False,
        min_size: Optional[str] = None,
        full_paths: bool = False,
        files_only: bool = False,
        progress_callback=None
    ) -> Tuple[str, str]:
        """
        執行 dust 命令並返回結果
        
        Args:
            target_path: 要分析的目標路徑
            max_depth: 最大遞歸深度
            sort_reverse: 是否反向排序（大到小）
            number_of_lines: 顯示結果行數限制
            file_types: 要包含的檔案類型
            exclude_patterns: 要排除的模式
            show_apparent_size: 是否顯示表面大小
            min_size: 最小檔案大小過濾
            full_paths: 是否顯示完整路徑
            files_only: 是否僅顯示檔案（不含目錄）
            
        Returns:
            Tuple[html_output, html_error]
        """
        try:
            if progress_callback:
                progress_callback("正在估算目錄大小...")
            
            # 智能估算超時時間
            estimated_timeout, directory_info = self.estimate_analysis_time(target_path)
            
            if progress_callback:
                progress_callback(f"目錄信息: {directory_info}")
                progress_callback(f"預估需要 {estimated_timeout//60} 分鐘，正在建構命令...")
            
            command = self._build_dust_command(
                target_path, max_depth, sort_reverse, number_of_lines,
                file_types, exclude_patterns, show_apparent_size, min_size,
                full_paths, files_only
            )
            
            logger.info(f"Executing dust command: {' '.join(command)}")
            logger.info(f"Directory info: {directory_info}")
            logger.info(f"Estimated timeout: {estimated_timeout} seconds")
            
            if progress_callback:
                progress_callback(f"執行命令: {' '.join(command[:3])}...")
            
            # 執行命令，使用非阻塞方式監控進度，指定編碼
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'  # 忽略編碼錯誤
            )
            
            if progress_callback:
                progress_callback("正在分析磁碟空間...")
            
            # 使用智能超時機制
            timeout = estimated_timeout
            start_time = time.time()
            
            # 定期檢查進程狀態並更新進度
            while process.poll() is None:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    if progress_callback:
                        progress_callback("分析超時，正在終止...")
                    process.terminate()
                    process.wait(timeout=10)
                    timeout_minutes = timeout // 60
                    return "", f"分析超時 ({timeout}秒/{timeout_minutes}分鐘)，目錄過大。建議：1) 減少深度限制 2) 增加行數限制 3) 排除大型子目錄"
                
                # 檢查是否被請求停止
                if progress_callback and elapsed > 0:
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)
                    should_continue = progress_callback(f"分析進行中... ({minutes:02d}:{seconds:02d})")
                    
                    # 如果進度回調返回 False，表示請求停止
                    if should_continue is False:
                        if progress_callback:
                            progress_callback("正在停止分析...")
                        process.terminate()
                        process.wait(timeout=10)
                        return "", "分析已被用戶取消"
                
                time.sleep(2)  # 每2秒更新一次進度
            
            # 進程完成，讀取輸出
            stdout, stderr = process.communicate()
            
            if progress_callback:
                progress_callback("正在處理分析結果...")
            
            # stdout 和 stderr 已經是字符串，不需要再解碼
            
            if progress_callback:
                progress_callback("正在轉換輸出格式...")
            
            # 使用 Ansi2HTMLConverter 轉換 ANSI 顏色為 HTML
            conv = Ansi2HTMLConverter()
            
            html_output = ""
            html_error = ""
            
            if stdout:
                html_output = conv.convert(stdout, full=False)
                if progress_callback:
                    line_count = html_output.count('\n')
                    progress_callback(f"分析完成，共 {line_count} 行結果")
            if stderr:
                html_error = conv.convert(stderr, full=False)
            
            return html_output, html_error
            
        except FileNotFoundError:
            return "", "Error: 'dust' executable not found at the specified path. Please verify the path."
        except Exception as e:
            return "", f"An unexpected error occurred: {e}"
    
    def _build_dust_command(
        self,
        target_path: str,
        max_depth: Optional[int],
        sort_reverse: bool,
        number_of_lines: Optional[int],
        file_types: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
        show_apparent_size: bool,
        min_size: Optional[str],
        full_paths: bool,
        files_only: bool
    ) -> List[str]:
        """
        構建 dust 命令參數列表
        
        Returns:
            完整的命令參數列表
        """
        command = [self.dust_executable_path]
        
        # 基本參數
        if target_path:
            command.append(target_path)
        
        # 深度限制 (-d, --depth)
        if max_depth is not None and max_depth > 0:
            command.extend(["-d", str(max_depth)])
        
        # 排序選項 (-r, --reverse)
        if sort_reverse:
            command.append("-r")
        
        # 行數限制 (-n, --number-of-lines)
        if number_of_lines is not None and number_of_lines > 0:
            command.extend(["-n", str(number_of_lines)])
        
        # 檔案類型過濾 (-t, --file_types)
        if file_types:
            for file_type in file_types:
                command.extend(["-t", file_type])
        
        # 排除模式 (-X, --ignore-directory)
        if exclude_patterns:
            for pattern in exclude_patterns:
                command.extend(["-X", pattern])
        
        # 顯示表面大小 (-s, --apparent-size)
        if show_apparent_size:
            command.append("-s")
        
        # 最小大小過濾 (-z, --min-size)
        if min_size:
            command.extend(["-z", min_size])
        
        # 顯示完整路徑 (-p, --full-paths)
        if full_paths:
            command.append("-p")
        
        # 僅顯示檔案 (-f, --filecount)
        if files_only:
            command.append("-f")
        
        # 總是顯示顏色輸出 (dust 使用 --force-colors 參數)
        command.append("--force-colors")
        
        return command
    
    def parse_dust_output(self, raw_output: str) -> List[Dict[str, str]]:
        """
        解析 dust 命令的原始輸出
        
        Args:
            raw_output: dust 命令的原始輸出
            
        Returns:
            解析後的目錄資訊列表
        """
        try:
            parsed_results = []
            
            if not raw_output:
                return parsed_results
            
            lines = raw_output.strip().split('\n')
            
            for line in lines:
                # 跳過空行
                if not line.strip():
                    continue
                
                # 簡單的解析邏輯，後續可以擴展
                # dust 輸出格式通常為：大小  路徑
                parts = line.strip().split()
                if len(parts) >= 2:
                    size = parts[0]
                    path = ' '.join(parts[1:])
                    
                    parsed_results.append({
                        'size': size,
                        'path': path,
                        'raw_line': line
                    })
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Error parsing dust output: {e}")
            return []
    
    def validate_path(self, path: str) -> bool:
        """
        驗證目標路徑是否有效
        
        Args:
            path: 要驗證的路徑
            
        Returns:
            路徑是否有效
        """
        try:
            import os
            return os.path.exists(path) and os.path.isdir(path)
        except Exception:
            return False
    
    def get_default_settings(self) -> Dict:
        """
        獲取預設設定
        
        Returns:
            預設設定字典
        """
        return {
            'max_depth': config_manager.get('tools.dust.default_max_depth', 3),
            'sort_reverse': config_manager.get('tools.dust.default_sort_reverse', True),
            'number_of_lines': config_manager.get('tools.dust.default_number_of_lines', 50),
            'show_apparent_size': config_manager.get('tools.dust.default_show_apparent_size', False),
            'min_size': config_manager.get('tools.dust.default_min_size', '')
        }
    
    def check_dust_availability(self) -> Tuple[bool, str, str]:
        """
        檢查 dust 工具是否可用
        
        Returns:
            Tuple[is_available, version_info, error_message]
        """
        try:
            # 嘗試執行 dust --version 來檢查工具可用性
            result = subprocess.run(
                [self.dust_executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"Dust tool available: {version_info}")
                return True, version_info, ""
            else:
                error_msg = f"Dust command returned non-zero exit code: {result.returncode}"
                logger.warning(error_msg)
                return False, "", error_msg
                
        except FileNotFoundError:
            error_msg = f"Dust executable not found at: {self.dust_executable_path}"
            logger.error(error_msg)
            return False, "", error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "Dust command timed out"
            logger.error(error_msg)
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Error checking dust availability: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        獲取快取資訊
        
        Returns:
            快取狀態和統計資訊
        """
        # 這裡可以實現快取相關的功能
        # 目前返回基本資訊
        return {
            "cache_enabled": config_manager.get('tools.dust.use_cache', True),
            "cache_ttl": config_manager.get('tools.dust.cache_ttl', 1800),
            "cache_entries": 0,  # 實際實現時可以返回真實數量
            "cache_size": 0      # 實際實現時可以返回真實大小
        }