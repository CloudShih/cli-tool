"""
Bat 模型類 - 處理 bat 命令執行和數據管理
"""

import os
import sys
import subprocess
import logging
import time
from typing import Tuple, Dict, Any, Optional, List
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class BatModel:
    """Bat 工具的模型類，負責命令執行和數據處理"""
    
    def __init__(self):
        self.executable_path = config_manager.get('tools.bat.executable_path', 'bat')
        self.cache = {}
        self.cache_ttl = config_manager.get('tools.bat.cache_ttl', 1800)  # 30分鐘
        self.max_cache_size = config_manager.get('tools.bat.max_cache_size', 52428800)  # 50MB
        
        logger.info(f"BatModel initialized with executable: {self.executable_path}")
    
    def check_bat_availability(self) -> Tuple[bool, str, str]:
        """
        檢查 bat 工具是否可用
        
        Returns:
            Tuple[bool, str, str]: (是否可用, 版本信息, 錯誤信息)
        """
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"bat tool available: {version_info}")
                return True, version_info, ""
            else:
                error_msg = f"bat command failed with return code {result.returncode}"
                logger.error(error_msg)
                return False, "", error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "bat command timed out"
            logger.error(error_msg)
            return False, "", error_msg
        except FileNotFoundError:
            error_msg = f"bat executable not found at: {self.executable_path}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error checking bat availability: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def get_available_themes(self) -> List[str]:
        """
        獲取可用的主題列表
        
        Returns:
            List[str]: 主題名稱列表
        """
        try:
            result = subprocess.run(
                [self.executable_path, '--list-themes'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                themes = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        themes.append(line.strip())
                return themes
            else:
                logger.error(f"Failed to get themes: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting available themes: {e}")
            return []
    
    def get_supported_languages(self) -> List[str]:
        """
        獲取支援的語言列表
        
        Returns:
            List[str]: 語言名稱列表
        """
        try:
            result = subprocess.run(
                [self.executable_path, '--list-languages'],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                languages = []
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        lang_info = line.split(':')[0].strip()
                        languages.append(lang_info)
                return languages
            else:
                logger.error(f"Failed to get languages: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return []
    
    def highlight_file(self, file_path: str, theme: str = "Monokai Extended", 
                      show_line_numbers: bool = True, show_git_modifications: bool = True,
                      tab_width: int = 4, wrap_text: bool = False, 
                      language: Optional[str] = None, use_cache: bool = True) -> Tuple[bool, str, str]:
        """
        使用 bat 高亮顯示檔案內容
        
        Args:
            file_path: 檔案路徑
            theme: 主題名稱
            show_line_numbers: 是否顯示行號
            show_git_modifications: 是否顯示 Git 修改標記
            tab_width: Tab 寬度
            wrap_text: 是否自動換行
            language: 指定語言（可選）
            use_cache: 是否使用快取
            
        Returns:
            Tuple[bool, str, str]: (成功狀態, HTML內容, 錯誤信息)
        """
        try:
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                return False, "", error_msg
            
            # 生成快取鍵
            cache_key = self._generate_cache_key(file_path, theme, show_line_numbers, 
                                                show_git_modifications, tab_width, 
                                                wrap_text, language)
            
            # 檢查快取
            if use_cache and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    logger.debug(f"Using cached result for: {file_path}")
                    return True, cache_entry['content'], ""
            
            # 構建 bat 命令
            cmd = [self.executable_path]
            
            # 構建樣式組件
            style_components = ['grid', 'header']  # 基本組件
            
            if show_line_numbers:
                style_components.append('numbers')
            
            if show_git_modifications:
                style_components.append('changes')
            
            # 添加參數
            cmd.extend(['--style', ','.join(style_components)])
            cmd.extend(['--theme', theme])
            cmd.extend(['--tabs', str(tab_width)])
            
            if wrap_text:
                cmd.append('--wrap=auto')
            else:
                cmd.append('--wrap=never')
            
            if language:
                cmd.extend(['--language', language])
            
            # 輸出為 HTML
            cmd.extend(['--terminal-width', '120'])
            cmd.extend(['--color', 'always'])
            
            cmd.append(file_path)
            
            logger.debug(f"Executing bat command: {' '.join(cmd)}")
            
            # 執行命令，使用 bytes 模式避免編碼問題
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,  # 使用 bytes 模式
                timeout=30
            )
            
            if result.returncode == 0:
                # 解碼輸出，處理編碼問題
                try:
                    stdout_text = result.stdout.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    stdout_text = result.stdout.decode('cp950', errors='replace')
                
                # 轉換 ANSI 到 HTML
                html_content = self._convert_ansi_to_html(stdout_text)
                
                # 快取結果
                if use_cache:
                    self._cache_result(cache_key, html_content)
                
                logger.debug(f"Successfully highlighted file: {file_path} ({len(html_content)} chars)")
                return True, html_content, ""
            else:
                # 解碼錯誤輸出
                try:
                    stderr_text = result.stderr.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    stderr_text = result.stderr.decode('cp950', errors='replace')
                
                error_msg = f"bat command failed: {stderr_text or 'Unknown error'}"
                logger.error(error_msg)
                return False, "", error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = f"bat command timed out for file: {file_path}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error highlighting file {file_path}: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def highlight_text(self, text: str, language: str, theme: str = "Monokai Extended",
                      show_line_numbers: bool = True, tab_width: int = 4, 
                      wrap_text: bool = False, use_cache: bool = True) -> Tuple[bool, str, str]:
        """
        高亮顯示文本內容
        
        Args:
            text: 要高亮的文本
            language: 語言類型
            theme: 主題名稱
            show_line_numbers: 是否顯示行號
            tab_width: Tab 寬度
            wrap_text: 是否自動換行
            use_cache: 是否使用快取
            
        Returns:
            Tuple[bool, str, str]: (成功狀態, HTML內容, 錯誤信息)
        """
        try:
            # 生成快取鍵
            cache_key = self._generate_text_cache_key(text, language, theme, 
                                                     show_line_numbers, tab_width, wrap_text)
            
            # 檢查快取
            if use_cache and cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    logger.debug("Using cached result for text highlighting")
                    return True, cache_entry['content'], ""
            
            # 構建 bat 命令
            cmd = [self.executable_path]
            
            # 構建樣式組件
            style_components = ['grid', 'header']  # 基本組件
            
            if show_line_numbers:
                style_components.append('numbers')
            
            # 添加參數
            cmd.extend(['--style', ','.join(style_components)])
            cmd.extend(['--theme', theme])
            cmd.extend(['--tabs', str(tab_width)])
            cmd.extend(['--language', language])
            
            if wrap_text:
                cmd.append('--wrap=auto')
            else:
                cmd.append('--wrap=never')
            
            # 輸出為 HTML
            cmd.extend(['--terminal-width', '120'])
            cmd.extend(['--color', 'always'])
            
            logger.debug(f"Executing bat command for text: {' '.join(cmd)}")
            
            # 執行命令，通過 stdin 傳入文本，使用 bytes 模式
            result = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                text=False,  # 使用 bytes 模式
                timeout=30
            )
            
            if result.returncode == 0:
                # 解碼輸出，處理編碼問題
                try:
                    stdout_text = result.stdout.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    stdout_text = result.stdout.decode('cp950', errors='replace')
                
                # 轉換 ANSI 到 HTML
                html_content = self._convert_ansi_to_html(stdout_text)
                
                # 快取結果
                if use_cache:
                    self._cache_result(cache_key, html_content)
                
                logger.debug(f"Successfully highlighted text ({len(html_content)} chars)")
                return True, html_content, ""
            else:
                # 解碼錯誤輸出
                try:
                    stderr_text = result.stderr.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    stderr_text = result.stderr.decode('cp950', errors='replace')
                
                error_msg = f"bat command failed: {stderr_text or 'Unknown error'}"
                logger.error(error_msg)
                return False, "", error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "bat command timed out for text highlighting"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error highlighting text: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def _convert_ansi_to_html(self, ansi_text: str) -> str:
        """
        將 ANSI 顏色代碼轉換為 HTML
        
        Args:
            ansi_text: 包含 ANSI 代碼的文本
            
        Returns:
            str: 轉換後的 HTML
        """
        try:
            # 使用 ansi2html 轉換
            from ansi2html import Ansi2HTMLConverter
            converter = Ansi2HTMLConverter(inline=True, dark_bg=True)
            html = converter.convert(ansi_text)
            
            # 添加自定義樣式
            styled_html = f"""
            <div style="font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
                        font-size: 13px; 
                        line-height: 1.4; 
                        background-color: #1e1e1e; 
                        color: #d4d4d4; 
                        padding: 10px; 
                        border-radius: 4px;
                        overflow-x: auto;">
                {html}
            </div>
            """
            
            return styled_html
            
        except ImportError:
            # 如果沒有 ansi2html，使用簡單的 HTML 包裝
            logger.warning("ansi2html not available, using simple HTML wrapper")
            escaped_text = (ansi_text.replace('&', '&amp;')
                                    .replace('<', '&lt;')
                                    .replace('>', '&gt;'))
            
            return f"""
            <div style="font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
                        font-size: 13px; 
                        line-height: 1.4; 
                        background-color: #1e1e1e; 
                        color: #d4d4d4; 
                        padding: 10px; 
                        border-radius: 4px;
                        white-space: pre-wrap;
                        overflow-x: auto;">
                {escaped_text}
            </div>
            """
        except Exception as e:
            logger.error(f"Error converting ANSI to HTML: {e}")
            return f"<pre>{ansi_text}</pre>"
    
    def _generate_cache_key(self, file_path: str, theme: str, show_line_numbers: bool,
                           show_git_modifications: bool, tab_width: int, wrap_text: bool,
                           language: Optional[str]) -> str:
        """生成檔案快取鍵"""
        import hashlib
        
        # 獲取檔案修改時間
        try:
            mtime = os.path.getmtime(file_path)
        except OSError:
            mtime = 0
        
        # 生成參數字符串
        params = f"{file_path}|{theme}|{show_line_numbers}|{show_git_modifications}|{tab_width}|{wrap_text}|{language}|{mtime}"
        
        return hashlib.md5(params.encode('utf-8')).hexdigest()
    
    def _generate_text_cache_key(self, text: str, language: str, theme: str,
                                show_line_numbers: bool, tab_width: int, wrap_text: bool) -> str:
        """生成文本快取鍵"""
        import hashlib
        
        # 生成參數字符串
        params = f"{text}|{language}|{theme}|{show_line_numbers}|{tab_width}|{wrap_text}"
        
        return hashlib.md5(params.encode('utf-8')).hexdigest()
    
    def _cache_result(self, cache_key: str, content: str):
        """快取結果"""
        try:
            # 檢查快取大小限制
            total_size = sum(len(entry['content']) for entry in self.cache.values())
            
            # 如果超過限制，清理舊的快取項
            if total_size > self.max_cache_size:
                self._cleanup_cache()
            
            self.cache[cache_key] = {
                'content': content,
                'timestamp': time.time()
            }
            
            logger.debug(f"Cached result with key: {cache_key[:16]}...")
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def _cleanup_cache(self):
        """清理過期的快取項"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if current_time - entry['timestamp'] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def clear_cache(self):
        """清除所有快取"""
        try:
            cache_size = len(self.cache)
            self.cache.clear()
            logger.info(f"Cleared {cache_size} cache entries")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """獲取快取信息"""
        try:
            total_size = sum(len(entry['content']) for entry in self.cache.values())
            current_time = time.time()
            
            # 統計有效和過期的快取項
            valid_entries = 0
            expired_entries = 0
            
            for entry in self.cache.values():
                if current_time - entry['timestamp'] < self.cache_ttl:
                    valid_entries += 1
                else:
                    expired_entries += 1
            
            return {
                "total_entries": len(self.cache),
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "max_size_mb": round(self.max_cache_size / 1024 / 1024, 2),
                "cache_ttl_seconds": self.cache_ttl
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {"error": str(e)}