"""
Glow Markdown 閱讀器的業務邏輯模型
提供 Glow CLI 工具整合和 Markdown 渲染功能
"""

import subprocess
import os
import re
import hashlib
import tempfile
import time
import logging
from typing import Dict, List, Tuple, Optional, Union
from urllib.parse import urlparse, quote
from ansi2html import Ansi2HTMLConverter
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class GlowModel:
    """Glow CLI 工具的業務邏輯模型"""
    
    def __init__(self):
        # 從配置管理器獲取 Glow 工具路徑
        glow_config = config_manager.get_tool_config('glow')
        self.glow_executable = glow_config.get('executable_path', 'glow')
        
        # 支援的輸入來源類型
        self.supported_sources = ["file", "url", "text"]
        
        # Glow 支援的主題樣式
        self.available_themes = [
            "auto",      # 自動檢測
            "dark",      # 深色主題
            "light",     # 淺色主題
            "pink",      # 粉色主題
            "notty",     # 無樣式
            "dracula",   # Dracula 主題
        ]
        
        # 支援的 Markdown 檔案擴展名
        self.supported_extensions = ['.md', '.markdown', '.mdown', '.mkd', '.txt']
        
        # 快取設定
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'cli_tool_glow_cache')
        self.cache_ttl = glow_config.get('cache_ttl', 3600)  # 1小時
        self.max_cache_size = glow_config.get('max_cache_size', 104857600)  # 100MB
        
        # 確保快取目錄存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # ANSI 到 HTML 轉換器
        self.ansi_converter = Ansi2HTMLConverter(dark_bg=True)
        
        logger.info("GlowModel initialized with configuration")
    
    def check_glow_availability(self) -> Tuple[bool, str, str]:
        """
        檢查 Glow 工具的可用性和版本信息
        
        Returns:
            tuple: (是否可用, 版本信息, 錯誤訊息)
        """
        try:
            # 嘗試執行 glow --version
            process = subprocess.Popen(
                [self.glow_executable, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            stdout, stderr = process.communicate(timeout=10)
            
            if process.returncode == 0:
                # 解析版本信息
                version_line = stdout.strip().split('\n')[0] if stdout.strip() else "Unknown version"
                logger.info(f"Glow is available: {version_line}")
                return True, version_line, ""
            else:
                error_msg = stderr.strip() or "Unknown error"
                logger.warning(f"Glow command failed: {error_msg}")
                return False, "", error_msg
                
        except FileNotFoundError:
            error_msg = f"Glow executable not found at: {self.glow_executable}"
            logger.error(error_msg)
            return False, "", error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "Glow command timed out"
            logger.error(error_msg)
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error checking Glow: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def validate_url(self, url: str) -> Tuple[bool, str, str]:
        """
        驗證和處理 URL，支援 GitHub 快捷方式
        
        Args:
            url: 輸入的 URL 或 GitHub 快捷方式
        
        Returns:
            tuple: (是否有效, 處理後的URL, 錯誤訊息)
        """
        if not url or not url.strip():
            return False, "", "URL 不能為空"
        
        url = url.strip()
        
        # 檢查是否為 GitHub 快捷方式 (user/repo 格式)
        github_pattern = r'^([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)(?:@([a-zA-Z0-9._/-]+))?(?::(.+))?$'
        github_match = re.match(github_pattern, url)
        
        if github_match:
            user, repo, branch_or_tag, file_path = github_match.groups()
            branch_or_tag = branch_or_tag or 'main'
            file_path = file_path or 'README.md'
            
            # 構建 GitHub raw URL
            processed_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch_or_tag}/{file_path}"
            logger.info(f"GitHub shortcut converted: {url} → {processed_url}")
            return True, processed_url, ""
        
        # 檢查是否為有效的 HTTP/HTTPS URL
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False, "", "僅支援 HTTP 和 HTTPS URL"
            
            if not parsed.netloc:
                return False, "", "無效的 URL 格式"
            
            logger.info(f"Valid URL: {url}")
            return True, url, ""
            
        except Exception as e:
            error_msg = f"URL 解析錯誤: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def get_cache_key(self, content_source: str) -> str:
        """
        生成快取鍵值
        
        Args:
            content_source: 內容來源 (檔案路徑或URL)
        
        Returns:
            str: 快取鍵值
        """
        return hashlib.md5(content_source.encode('utf-8')).hexdigest()
    
    def get_cached_content(self, cache_key: str) -> Optional[str]:
        """
        獲取快取內容
        
        Args:
            cache_key: 快取鍵值
        
        Returns:
            str or None: 快取內容，如果沒有或已過期則返回 None
        """
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")
        
        try:
            if os.path.exists(cache_file):
                # 檢查快取是否過期
                if time.time() - os.path.getmtime(cache_file) < self.cache_ttl:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        logger.info(f"Cache hit for key: {cache_key}")
                        return f.read()
                else:
                    # 刪除過期快取
                    os.remove(cache_file)
                    logger.info(f"Cache expired and removed: {cache_key}")
        except Exception as e:
            logger.warning(f"Error reading cache {cache_key}: {e}")
        
        return None
    
    def save_to_cache(self, cache_key: str, content: str):
        """
        保存內容到快取
        
        Args:
            cache_key: 快取鍵值
            content: 要快取的內容
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Content cached with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Error saving cache {cache_key}: {e}")
    
    def render_markdown(
        self, 
        source: str, 
        source_type: str = "file",
        theme: str = "auto",
        width: int = 120,
        use_cache: bool = True
    ) -> Tuple[bool, str, str]:
        """
        使用 Glow 渲染 Markdown 內容
        
        Args:
            source: 內容來源 (檔案路徑、URL 或直接文字)
            source_type: 來源類型 ("file", "url", "text")
            theme: Glow 主題樣式
            width: 顯示寬度
            use_cache: 是否使用快取
        
        Returns:
            tuple: (是否成功, HTML內容, 錯誤訊息)
        """
        if source_type not in self.supported_sources:
            return False, "", f"不支援的來源類型: {source_type}"
        
        if theme not in self.available_themes:
            logger.warning(f"Unknown theme '{theme}', using 'auto'")
            theme = "auto"
        
        # 檢查快取
        if use_cache and source_type in ["file", "url"]:
            cache_key = self.get_cache_key(f"{source_type}:{source}:{theme}:{width}")
            cached_content = self.get_cached_content(cache_key)
            if cached_content:
                return True, cached_content, ""
        
        try:
            # 構建 Glow 命令
            command = [self.glow_executable]
            
            # 添加樣式參數
            if theme != "auto":
                command.extend(['--style', theme])
            
            # 添加寬度參數
            command.extend(['--width', str(width)])
            
            # 根據來源類型處理輸入
            if source_type == "file":
                if not os.path.exists(source):
                    return False, "", f"檔案不存在: {source}"
                if not os.path.isfile(source):
                    return False, "", f"路徑不是檔案: {source}"
                command.append(source)
                
            elif source_type == "url":
                # 先驗證 URL
                is_valid, processed_url, error_msg = self.validate_url(source)
                if not is_valid:
                    return False, "", error_msg
                command.append(processed_url)
                
            elif source_type == "text":
                # 使用 stdin 輸入
                command.append('-')
            
            # 執行 Glow 命令
            process_input = source.encode('utf-8') if source_type == "text" else None
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if source_type == "text" else None,
                text=False  # 使用 bytes 模式
            )
            
            stdout_bytes, stderr_bytes = process.communicate(
                input=process_input,
                timeout=30  # 30秒超時
            )
            
            # 安全解碼輸出
            def safe_decode(byte_data):
                for encoding in ['utf-8', 'cp1252', 'latin1']:
                    try:
                        return byte_data.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                return byte_data.decode('utf-8', errors='replace')
            
            stdout = safe_decode(stdout_bytes)
            stderr = safe_decode(stderr_bytes)
            
            if process.returncode == 0:
                # 成功執行，轉換 ANSI 到 HTML
                html_content = self.ansi_converter.convert(stdout, full=False)
                
                # 添加自訂 CSS 樣式
                styled_html = self._apply_custom_styling(html_content, theme)
                
                # 保存到快取
                if use_cache and source_type in ["file", "url"]:
                    self.save_to_cache(cache_key, styled_html)
                
                logger.info(f"Successfully rendered markdown from {source_type}: {source[:100]}...")
                return True, styled_html, ""
            else:
                error_message = stderr.strip() or "Glow 命令執行失敗"
                logger.error(f"Glow command failed: {error_message}")
                return False, "", error_message
                
        except subprocess.TimeoutExpired:
            error_msg = "Glow 命令執行超時"
            logger.error(error_msg)
            return False, "", error_msg
            
        except Exception as e:
            error_msg = f"執行 Glow 時發生錯誤: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def _apply_custom_styling(self, html_content: str, theme: str) -> str:
        """
        應用自訂 CSS 樣式到 HTML 內容
        
        Args:
            html_content: 原始 HTML 內容
            theme: 主題名稱
        
        Returns:
            str: 應用樣式後的 HTML 內容
        """
        # 基礎樣式
        base_styles = """
        <style>
        body {
            font-family: 'Microsoft YaHei', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            margin: 20px;
            word-wrap: break-word;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #e1e1e8;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
        }
        code {
            background-color: #f1f1f1;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        blockquote {
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        </style>
        """
        
        # 根據主題調整樣式
        if theme == "dark":
            dark_styles = """
            <style>
            body { background-color: #1e1e1e; color: #d4d4d4; }
            pre { background-color: #2d2d2d; border-color: #444; color: #d4d4d4; }
            code { background-color: #2d2d2d; color: #d4d4d4; }
            blockquote { border-left-color: #666; color: #aaa; }
            th { background-color: #444; color: #fff; }
            th, td { border-color: #666; }
            </style>
            """
            base_styles += dark_styles
        
        # 包裝 HTML 內容
        wrapped_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            {base_styles}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return wrapped_html
    
    def get_file_info(self, file_path: str) -> Dict[str, Union[str, int, bool]]:
        """
        獲取檔案信息
        
        Args:
            file_path: 檔案路徑
        
        Returns:
            dict: 檔案信息字典
        """
        try:
            if not os.path.exists(file_path):
                return {"exists": False, "error": "檔案不存在"}
            
            if not os.path.isfile(file_path):
                return {"exists": False, "error": "路徑不是檔案"}
            
            stat_info = os.stat(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            return {
                "exists": True,
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
                "extension": file_ext,
                "is_markdown": file_ext in self.supported_extensions,
                "readable": os.access(file_path, os.R_OK)
            }
            
        except Exception as e:
            return {"exists": False, "error": f"獲取檔案信息時發生錯誤: {str(e)}"}
    
    def clear_cache(self) -> Tuple[bool, str]:
        """
        清除所有快取檔案
        
        Returns:
            tuple: (是否成功, 訊息)
        """
        try:
            if not os.path.exists(self.cache_dir):
                return True, "快取目錄不存在，無需清理"
            
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.cache')]
            removed_count = 0
            
            for cache_file in cache_files:
                try:
                    os.remove(os.path.join(self.cache_dir, cache_file))
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove cache file {cache_file}: {e}")
            
            message = f"已清除 {removed_count} 個快取檔案"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"清除快取時發生錯誤: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_cache_info(self) -> Dict[str, Union[int, str]]:
        """
        獲取快取信息
        
        Returns:
            dict: 快取信息字典
        """
        try:
            if not os.path.exists(self.cache_dir):
                return {"count": 0, "size": 0, "status": "快取目錄不存在"}
            
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.cache')]
            total_size = 0
            
            for cache_file in cache_files:
                try:
                    file_path = os.path.join(self.cache_dir, cache_file)
                    total_size += os.path.getsize(file_path)
                except Exception:
                    continue
            
            return {
                "count": len(cache_files),
                "size": total_size,
                "size_mb": round(total_size / 1024 / 1024, 2),
                "status": "正常"
            }
            
        except Exception as e:
            return {"count": 0, "size": 0, "status": f"錯誤: {str(e)}"}