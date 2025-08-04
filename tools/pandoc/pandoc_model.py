"""
Pandoc 文檔轉換工具的模型層
負責執行 pandoc 命令和處理業務邏輯
"""

import subprocess
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from ansi2html import Ansi2HTMLConverter
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class PandocModel:
    """Pandoc 工具的業務邏輯模型"""
    
    # 支援的輸入格式
    INPUT_FORMATS = {
        'markdown': 'Markdown',
        'html': 'HTML',
        'docx': 'Microsoft Word (DOCX)',
        'odt': 'OpenDocument Text',
        'rtf': 'Rich Text Format',
        'latex': 'LaTeX',
        'epub': 'EPUB',
        'rst': 'reStructuredText',
        'textile': 'Textile',
        'mediawiki': 'MediaWiki'
    }
    
    # 支援的輸出格式
    OUTPUT_FORMATS = {
        'html': 'HTML',
        'html5': 'HTML5',
        'pdf': 'PDF',
        'docx': 'Microsoft Word (DOCX)',
        'odt': 'OpenDocument Text',
        'rtf': 'Rich Text Format',
        'latex': 'LaTeX',
        'epub': 'EPUB',
        'mobi': 'Mobipocket',
        'rst': 'reStructuredText',
        'markdown': 'Markdown',
        'plain': 'Plain Text'
    }
    
    def __init__(self):
        """初始化 Pandoc 模型"""
        # 從配置管理器獲取 pandoc 執行檔路徑
        self.pandoc_executable = config_manager.get('tools.pandoc.executable_path', 'pandoc')
        self.conv = Ansi2HTMLConverter()
        logger.info(f"PandocModel initialized with executable: {self.pandoc_executable}")
    
    def check_pandoc_availability(self) -> Tuple[bool, str]:
        """檢查 pandoc 工具是否可用"""
        try:
            result = subprocess.run(
                [self.pandoc_executable, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                logger.info(f"Pandoc available: {version_info}")
                return True, version_info
            else:
                error_msg = f"Pandoc command failed: {result.stderr}"
                logger.warning(error_msg)
                return False, error_msg
        except FileNotFoundError:
            error_msg = f"Pandoc executable not found: {self.pandoc_executable}"
            logger.warning(error_msg)
            return False, error_msg
        except subprocess.TimeoutExpired:
            error_msg = "Pandoc command timed out"
            logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error checking pandoc: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def convert_document(self, 
                        input_file: str,
                        output_file: str,
                        input_format: str = None,
                        output_format: str = None,
                        standalone: bool = True,
                        template: str = None,
                        css_file: str = None,
                        metadata: Dict[str, str] = None,
                        extra_options: List[str] = None) -> Tuple[bool, str, str]:
        """
        執行文檔轉換
        
        Args:
            input_file: 輸入檔案路徑
            output_file: 輸出檔案路徑
            input_format: 輸入格式 (可選，pandoc 會自動檢測)
            output_format: 輸出格式 (可選，根據副檔名推斷)
            standalone: 是否生成獨立文檔
            template: 自訂模板路徑
            css_file: CSS 樣式檔案路徑
            metadata: 元數據字典
            extra_options: 額外的命令行選項
            
        Returns:
            (成功標誌, 標準輸出, 標準錯誤)
        """
        try:
            # 驗證輸入檔案
            if not os.path.exists(input_file):
                error_msg = f"輸入檔案不存在: {input_file}"
                logger.error(error_msg)
                return False, "", error_msg
            
            # 建構 pandoc 命令
            command = [self.pandoc_executable]
            
            # 輸入格式
            if input_format:
                command.extend(['-f', input_format])
            
            # 輸出格式
            if output_format:
                command.extend(['-t', output_format])
            
            # 輸入檔案
            command.append(input_file)
            
            # 輸出檔案
            command.extend(['-o', output_file])
            
            # Standalone 模式
            if standalone:
                command.append('-s')
            
            # 自訂模板
            if template and os.path.exists(template):
                command.extend(['--template', template])
            
            # CSS 樣式
            if css_file and os.path.exists(css_file):
                command.extend(['-c', css_file])
            
            # 元數據
            if metadata:
                for key, value in metadata.items():
                    command.extend(['-M', f'{key}:{value}'])
            
            # 額外選項
            if extra_options:
                command.extend(extra_options)
            
            logger.info(f"Executing pandoc command: {' '.join(command)}")
            
            # 執行命令
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                success_msg = f"文檔轉換成功: {input_file} → {output_file}"
                logger.info(success_msg)
                
                # 檢查輸出檔案是否生成
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    success_msg += f"\n輸出檔案大小: {file_size} bytes"
                
                return True, success_msg, stderr
            else:
                error_msg = f"Pandoc 轉換失敗 (退出碼: {process.returncode})\n{stderr}"
                logger.error(error_msg)
                return False, stdout, error_msg
                
        except Exception as e:
            error_msg = f"執行 pandoc 命令時發生錯誤: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def batch_convert(self,
                     input_files: List[str],
                     output_dir: str,
                     input_format: str = None,
                     output_format: str = 'html',
                     **conversion_options) -> List[Tuple[str, bool, str]]:
        """
        批量轉換文檔
        
        Args:
            input_files: 輸入檔案列表
            output_dir: 輸出目錄
            input_format: 輸入格式
            output_format: 輸出格式
            **conversion_options: 轉換選項
            
        Returns:
            轉換結果列表: [(檔案名, 成功標誌, 訊息), ...]
        """
        results = []
        
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        for input_file in input_files:
            try:
                # 生成輸出檔案名
                input_path = Path(input_file)
                output_filename = input_path.stem + self._get_extension_for_format(output_format)
                output_file = os.path.join(output_dir, output_filename)
                
                # 執行轉換
                success, stdout, stderr = self.convert_document(
                    input_file=input_file,
                    output_file=output_file,
                    input_format=input_format,
                    output_format=output_format,
                    **conversion_options
                )
                
                if success:
                    results.append((input_path.name, True, f"轉換成功 → {output_filename}"))
                else:
                    results.append((input_path.name, False, stderr))
                    
            except Exception as e:
                error_msg = f"處理檔案 {input_file} 時發生錯誤: {str(e)}"
                results.append((os.path.basename(input_file), False, error_msg))
                logger.error(error_msg)
        
        return results
    
    def get_supported_formats(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """獲取支援的輸入和輸出格式"""
        return self.INPUT_FORMATS.copy(), self.OUTPUT_FORMATS.copy()
    
    def _get_extension_for_format(self, format_name: str) -> str:
        """根據格式名稱獲取檔案副檔名"""
        format_extensions = {
            'html': '.html',
            'html5': '.html',
            'pdf': '.pdf',
            'docx': '.docx',
            'odt': '.odt',
            'rtf': '.rtf',
            'latex': '.tex',
            'epub': '.epub',
            'mobi': '.mobi',
            'rst': '.rst',
            'markdown': '.md',
            'plain': '.txt'
        }
        return format_extensions.get(format_name, '.txt')
    
    def format_output_for_display(self, text: str) -> str:
        """將命令輸出格式化為 HTML 以便在 GUI 中顯示"""
        if not text.strip():
            return "<p style='color: #888;'>無輸出內容</p>"
        
        try:
            # 轉換 ANSI 色碼為 HTML
            html_output = self.conv.convert(text, full=False)
            return f"<pre style='font-family: monospace; background: #f5f5f5; padding: 10px; border-radius: 4px;'>{html_output}</pre>"
        except Exception as e:
            logger.warning(f"Failed to convert ANSI to HTML: {e}")
            # 後備方案：使用純文字
            escaped_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f"<pre style='font-family: monospace; background: #f5f5f5; padding: 10px; border-radius: 4px;'>{escaped_text}</pre>"