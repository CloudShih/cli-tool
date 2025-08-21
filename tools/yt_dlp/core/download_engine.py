"""
YT-DLP 下載引擎
處理 yt-dlp 命令的建構和執行
"""
import os
import shlex
import platform
import subprocess
import json
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
import logging
import re

from .data_models import DownloadParameters, VideoInfo, FormatInfo

logger = logging.getLogger(__name__)


class YtDlpCommandBuilder:
    """YT-DLP 命令建構器"""
    
    def __init__(self, executable_path: str = "yt-dlp"):
        self.executable_path = executable_path
        self._validate_executable()
    
    def _validate_executable(self):
        """驗證 yt-dlp 執行檔是否可用"""
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            if result.returncode != 0:
                raise FileNotFoundError(f"YT-DLP executable not working: {self.executable_path}")
                
            logger.debug(f"YT-DLP version: {result.stdout.strip()}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise FileNotFoundError(f"YT-DLP executable not found: {self.executable_path} - {e}")
    
    def build_info_command(self, url: str) -> List[str]:
        """建構資訊獲取命令"""
        cmd = [
            self.executable_path,
            '--dump-json',
            '--no-download',
            '--flat-playlist',
            url
        ]
        
        logger.debug(f"Built info command: {' '.join(shlex.quote(arg) for arg in cmd)}")
        return cmd
    
    def build_download_command(self, params: DownloadParameters) -> List[str]:
        """建構下載命令"""
        cmd = [self.executable_path]
        
        # 基本 URL
        cmd.append(params.url)
        
        # 輸出設定
        output_path = Path(params.output_dir) / params.output_template
        cmd.extend(['-o', str(output_path)])
        
        # 格式選擇
        if params.format_selector:
            cmd.extend(['-f', params.format_selector])
        
        # 音訊提取
        if params.extract_audio:
            cmd.append('--extract-audio')
            if params.audio_format:
                cmd.extend(['--audio-format', params.audio_format])
            if not params.keep_video:
                cmd.append('--no-keep-video')
        
        # 字幕設定
        if params.subtitles:
            cmd.append('--write-subs')
            if params.subtitle_langs:
                cmd.extend(['--sub-langs', ','.join(params.subtitle_langs)])
        
        if params.auto_subtitles:
            cmd.append('--write-auto-subs')
        
        if params.embed_subtitles:
            cmd.append('--embed-subs')
        
        # 元資料設定
        if params.write_info_json:
            cmd.append('--write-info-json')
        
        if params.write_description:
            cmd.append('--write-description')
        
        if params.write_thumbnail:
            cmd.append('--write-thumbnail')
        
        if params.embed_thumbnail:
            cmd.append('--embed-thumbnail')
        
        # 錯誤處理
        if params.ignore_errors:
            cmd.append('--ignore-errors')
        
        if params.no_warnings:
            cmd.append('--no-warnings')
        
        # 播放清單設定
        if params.extract_flat:
            cmd.append('--flat-playlist')
        
        if params.playlist_start:
            cmd.extend(['--playlist-start', str(params.playlist_start)])
        
        if params.playlist_end:
            cmd.extend(['--playlist-end', str(params.playlist_end)])
        
        if params.max_downloads:
            cmd.extend(['--max-downloads', str(params.max_downloads)])
        
        # 網路設定
        if params.rate_limit:
            cmd.extend(['--limit-rate', params.rate_limit])
        
        if params.retries:
            cmd.extend(['--retries', str(params.retries)])
        
        if params.fragment_retries:
            cmd.extend(['--fragment-retries', str(params.fragment_retries)])
        
        if params.skip_unavailable_fragments:
            cmd.append('--skip-unavailable-fragments')
        
        if params.geo_bypass:
            cmd.append('--geo-bypass')
        
        # 代理和認證
        if params.proxy:
            cmd.extend(['--proxy', params.proxy])
        
        if params.cookies_file:
            cmd.extend(['--cookies', params.cookies_file])
        
        if params.user_agent:
            cmd.extend(['--user-agent', params.user_agent])
        
        if params.referer:
            cmd.extend(['--referer', params.referer])
        
        # 額外標頭
        for key, value in params.add_headers.items():
            cmd.extend(['--add-header', f'{key}:{value}'])
        
        # 速率限制
        if params.sleep_interval:
            cmd.extend(['--sleep-interval', str(params.sleep_interval)])
        
        if params.max_sleep_interval:
            cmd.extend(['--max-sleep-interval', str(params.max_sleep_interval)])
        
        # FFmpeg 設定
        if params.ffmpeg_location:
            cmd.extend(['--ffmpeg-location', params.ffmpeg_location])
        
        if params.prefer_ffmpeg:
            cmd.append('--prefer-ffmpeg')
        
        # 進度和輸出控制
        cmd.extend([
            '--newline',  # 每個進度更新輸出新行
            '--progress',  # 顯示進度
            '--console-title',  # 更新控制台標題
        ])
        
        logger.debug(f"Built download command: {' '.join(shlex.quote(arg) for arg in cmd)}")
        return cmd
    
    def build_formats_command(self, url: str) -> List[str]:
        """建構格式列表命令"""
        cmd = [
            self.executable_path,
            '--list-formats',
            url
        ]
        
        logger.debug(f"Built formats command: {' '.join(shlex.quote(arg) for arg in cmd)}")
        return cmd


class YtDlpEngine:
    """YT-DLP 下載引擎"""
    
    def __init__(self, executable_path: str = "yt-dlp"):
        self.command_builder = YtDlpCommandBuilder(executable_path)
        self.current_process: Optional[subprocess.Popen] = None
        self._platform = platform.system().lower()
        self.progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """設定進度回調函數"""
        self.progress_callback = callback
    
    def get_video_info(self, url: str, timeout: Optional[float] = 30) -> Optional[VideoInfo]:
        """獲取影片資訊"""
        command = self.command_builder.build_info_command(url)
        
        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'encoding': 'utf-8',
            'errors': 'replace',
        }
        
        if self._platform == 'windows':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        try:
            result = subprocess.run(command, timeout=timeout, **kwargs)
            
            if result.returncode != 0:
                logger.error(f"Failed to get video info: {result.stderr}")
                return None
            
            # 解析 JSON 輸出
            info_data = json.loads(result.stdout)
            
            # 轉換為 VideoInfo 物件
            video_info = VideoInfo(
                url=url,
                title=info_data.get('title', 'Unknown'),
                description=info_data.get('description'),
                uploader=info_data.get('uploader'),
                duration=info_data.get('duration'),
                view_count=info_data.get('view_count'),
                upload_date=info_data.get('upload_date'),
                thumbnail=info_data.get('thumbnail'),
                webpage_url=info_data.get('webpage_url'),
                extractor=info_data.get('extractor')
            )
            
            # 解析格式資訊
            formats = info_data.get('formats', [])
            for fmt in formats:
                format_info = FormatInfo(
                    format_id=fmt.get('format_id', ''),
                    ext=fmt.get('ext', ''),
                    quality=fmt.get('quality'),
                    filesize=fmt.get('filesize'),
                    resolution=fmt.get('resolution'),
                    fps=fmt.get('fps'),
                    vcodec=fmt.get('vcodec'),
                    acodec=fmt.get('acodec'),
                    abr=fmt.get('abr'),
                    vbr=fmt.get('vbr')
                )
                video_info.formats.append(format_info)
            
            return video_info
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting video info for: {url}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse video info JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def download(self, params: DownloadParameters) -> subprocess.Popen:
        """執行下載 - 返回 Popen 物件供非同步處理"""
        command = self.command_builder.build_download_command(params)
        
        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,  # 合併輸出流
            'text': True,
            'encoding': 'utf-8',
            'errors': 'replace',
            'bufsize': 1,  # 行緩衝
            'universal_newlines': True,
        }
        
        if self._platform == 'windows':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            kwargs['shell'] = False
        else:
            kwargs['preexec_fn'] = os.setsid  # 創建新的進程組
        
        try:
            self.current_process = subprocess.Popen(command, **kwargs)
            logger.info(f"Started yt-dlp download with PID: {self.current_process.pid}")
            return self.current_process
            
        except Exception as e:
            logger.error(f"Failed to start yt-dlp process: {e}")
            raise RuntimeError(f"Failed to execute yt-dlp: {e}")
    
    def download_sync(self, params: DownloadParameters, 
                     timeout: Optional[float] = None) -> tuple[str, int]:
        """同步下載 - 等待完成並返回結果"""
        process = self.download(params)
        
        try:
            stdout, _ = process.communicate(timeout=timeout)
            returncode = process.returncode
            
            logger.debug(f"YT-DLP process completed with return code: {returncode}")
            return stdout, returncode
            
        except subprocess.TimeoutExpired:
            logger.warning(f"YT-DLP download timeout after {timeout} seconds")
            self.cancel_download()
            raise TimeoutError(f"Download timeout after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error during download execution: {e}")
            self.cancel_download()
            raise
    
    def cancel_download(self):
        """取消當前下載"""
        if self.current_process and self.current_process.poll() is None:
            try:
                if self._platform == 'windows':
                    self.current_process.terminate()
                else:
                    os.killpg(os.getpgid(self.current_process.pid), subprocess.signal.SIGTERM)
                
                self.current_process.wait(timeout=5)
                logger.info("YT-DLP download cancelled successfully")
                
            except subprocess.TimeoutExpired:
                if self._platform == 'windows':
                    self.current_process.kill()
                else:
                    os.killpg(os.getpgid(self.current_process.pid), subprocess.signal.SIGKILL)
                
                logger.warning("YT-DLP download force killed")
                
            except Exception as e:
                logger.error(f"Error cancelling yt-dlp download: {e}")
            
            finally:
                self.current_process = None
    
    def is_downloading(self) -> bool:
        """檢查是否正在下載"""
        return self.current_process is not None and self.current_process.poll() is None
    
    def get_available_formats(self, url: str, timeout: Optional[float] = 30) -> List[Dict[str, Any]]:
        """獲取可用格式列表"""
        command = self.command_builder.build_formats_command(url)
        
        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'encoding': 'utf-8',
            'errors': 'replace',
        }
        
        if self._platform == 'windows':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        try:
            result = subprocess.run(command, timeout=timeout, **kwargs)
            
            if result.returncode != 0:
                logger.error(f"Failed to get formats: {result.stderr}")
                return []
            
            # 解析格式輸出
            formats = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                # 解析格式行 (例如: "137     mp4   1920x1080  DASH video  1188k ...")
                if re.match(r'^\d+\s+', line):
                    parts = line.split()
                    if len(parts) >= 3:
                        format_info = {
                            'format_id': parts[0],
                            'ext': parts[1],
                            'resolution': parts[2] if len(parts) > 2 else None,
                            'note': ' '.join(parts[3:]) if len(parts) > 3 else None
                        }
                        formats.append(format_info)
            
            return formats
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting formats for: {url}")
            return []
        except Exception as e:
            logger.error(f"Error getting formats: {e}")
            return []
    
    def validate_url(self, url: str, timeout: Optional[float] = 10) -> bool:
        """驗證 URL 是否受支援"""
        try:
            command = [
                self.command_builder.executable_path,
                '--simulate',
                '--quiet',
                url
            ]
            
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'replace',
            }
            
            if self._platform == 'windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(command, timeout=timeout, **kwargs)
            return result.returncode == 0
            
        except Exception as e:
            logger.warning(f"Error validating URL: {e}")
            return False
    
    def get_version(self) -> str:
        """獲取 yt-dlp 版本"""
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
                return result.stdout.strip()
            else:
                return "Unknown"
                
        except Exception as e:
            logger.warning(f"Failed to get yt-dlp version: {e}")
            return "Unknown"
    
    def get_supported_sites(self, timeout: Optional[float] = 30) -> List[str]:
        """獲取支援的網站列表"""
        try:
            command = [
                self.command_builder.executable_path,
                '--list-extractors'
            ]
            
            kwargs = {
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'replace',
            }
            
            if self._platform == 'windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(command, timeout=timeout, **kwargs)
            
            if result.returncode == 0:
                sites = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('['):
                        sites.append(line)
                return sites
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Failed to get supported sites: {e}")
            return []


# 便利函數
def create_download_engine(executable_path: str = "yt-dlp") -> YtDlpEngine:
    """創建下載引擎實例"""
    return YtDlpEngine(executable_path)


def validate_ytdlp_available(executable_path: str = "yt-dlp") -> bool:
    """驗證 yt-dlp 是否可用"""
    try:
        YtDlpCommandBuilder(executable_path)
        return True
    except FileNotFoundError:
        return False


def parse_progress_line(line: str) -> Optional[Dict[str, Any]]:
    """解析進度輸出行"""
    # YT-DLP 進度格式: [download]  XX.X% of YYY.YYMiB at ZZZ.ZZKiB/s ETA MM:SS
    progress_pattern = r'\[download\]\s+(\d+\.?\d*)%\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)'
    match = re.search(progress_pattern, line)
    
    if match:
        percentage = float(match.group(1))
        total_size_str = match.group(2)
        speed_str = match.group(3)
        eta_str = match.group(4)
        
        return {
            'percentage': percentage,
            'total_size_str': total_size_str,
            'speed_str': speed_str,
            'eta_str': eta_str,
            'status': 'downloading'
        }
    
    # 其他狀態檢查
    if '[download] Destination:' in line:
        return {'status': 'starting', 'filename': line.split('Destination:')[1].strip()}
    elif '[download] 100%' in line:
        return {'status': 'completed'}
    elif '[ExtractAudio]' in line:
        return {'status': 'extracting_audio'}
    elif '[Merger]' in line:
        return {'status': 'merging'}
    elif 'ERROR:' in line:
        return {'status': 'error', 'message': line}
    
    return None


def estimate_total_size(size_str: str) -> Optional[int]:
    """估算總檔案大小 (位元組)"""
    try:
        # 解析格式如 "123.45MiB" 或 "1.23GiB"
        size_match = re.match(r'(\d+\.?\d*)\s*([KMGT]?)i?B', size_str, re.IGNORECASE)
        if size_match:
            value = float(size_match.group(1))
            unit = size_match.group(2).upper()
            
            multipliers = {
                '': 1,
                'K': 1024,
                'M': 1024 * 1024,
                'G': 1024 * 1024 * 1024,
                'T': 1024 * 1024 * 1024 * 1024
            }
            
            return int(value * multipliers.get(unit, 1))
    except:
        pass
    
    return None


def estimate_speed(speed_str: str) -> Optional[float]:
    """估算下載速度 (位元組/秒)"""
    try:
        # 解析格式如 "123.45KiB/s" 或 "1.23MiB/s"
        speed_match = re.match(r'(\d+\.?\d*)\s*([KMGT]?)i?B/s', speed_str, re.IGNORECASE)
        if speed_match:
            value = float(speed_match.group(1))
            unit = speed_match.group(2).upper()
            
            multipliers = {
                '': 1,
                'K': 1024,
                'M': 1024 * 1024,
                'G': 1024 * 1024 * 1024,
                'T': 1024 * 1024 * 1024 * 1024
            }
            
            return value * multipliers.get(unit, 1)
    except:
        pass
    
    return None