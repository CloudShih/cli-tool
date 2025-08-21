"""
YT-DLP 資料模型定義
定義下載相關的所有資料結構
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json
from pathlib import Path


class DownloadStatus(Enum):
    """下載狀態枚舉"""
    IDLE = "idle"
    PREPARING = "preparing"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"
    EXTRACTING = "extracting"
    POST_PROCESSING = "post_processing"


class VideoQuality(Enum):
    """影片品質枚舉"""
    BEST = "best"
    WORST = "worst"
    HD_1080P = "best[height<=1080]"
    HD_720P = "best[height<=720]"
    SD_480P = "best[height<=480]"
    SD_360P = "best[height<=360]"
    AUDIO_ONLY = "bestaudio"
    VIDEO_ONLY = "bestvideo"


class AudioFormat(Enum):
    """音訊格式枚舉"""
    MP3 = "mp3"
    AAC = "aac"
    M4A = "m4a"
    OGG = "ogg"
    FLAC = "flac"
    WAV = "wav"
    BEST = "best"


@dataclass
class FormatInfo:
    """格式資訊"""
    format_id: str
    ext: str
    quality: Optional[str] = None
    filesize: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    abr: Optional[float] = None  # 音訊位元率
    vbr: Optional[float] = None  # 影片位元率
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'format_id': self.format_id,
            'ext': self.ext,
            'quality': self.quality,
            'filesize': self.filesize,
            'resolution': self.resolution,
            'fps': self.fps,
            'vcodec': self.vcodec,
            'acodec': self.acodec,
            'abr': self.abr,
            'vbr': self.vbr
        }


@dataclass
class VideoInfo:
    """影片資訊"""
    url: str
    title: str
    description: Optional[str] = None
    uploader: Optional[str] = None
    duration: Optional[float] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    thumbnail: Optional[str] = None
    formats: List[FormatInfo] = field(default_factory=list)
    webpage_url: Optional[str] = None
    extractor: Optional[str] = None
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'duration': self.duration,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
            'thumbnail': self.thumbnail,
            'formats': [f.to_dict() for f in self.formats],
            'webpage_url': self.webpage_url,
            'extractor': self.extractor
        }


@dataclass
class DownloadParameters:
    """下載參數資料結構"""
    url: str
    output_dir: str = "."
    output_template: str = "%(title)s.%(ext)s"
    format_selector: str = "best"
    audio_format: Optional[str] = None
    video_quality: Optional[str] = None
    extract_audio: bool = False
    keep_video: bool = True
    subtitles: bool = False
    auto_subtitles: bool = False
    subtitle_langs: List[str] = field(default_factory=lambda: ["zh-TW", "zh", "en"])
    write_info_json: bool = False
    write_description: bool = False
    write_thumbnail: bool = False
    embed_subtitles: bool = False
    embed_thumbnail: bool = False
    ignore_errors: bool = False
    no_warnings: bool = False
    extract_flat: bool = False
    playlist_start: Optional[int] = None
    playlist_end: Optional[int] = None
    max_downloads: Optional[int] = None
    rate_limit: Optional[str] = None
    retries: int = 10
    fragment_retries: int = 10
    skip_unavailable_fragments: bool = True
    geo_bypass: bool = True
    proxy: Optional[str] = None
    cookies_file: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    add_headers: Dict[str, str] = field(default_factory=dict)
    sleep_interval: Optional[int] = None
    max_sleep_interval: Optional[int] = None
    ffmpeg_location: Optional[str] = None
    prefer_ffmpeg: bool = True
    
    def __post_init__(self):
        """後處理 - 驗證參數"""
        if not self.url:
            raise ValueError("URL cannot be empty")
        
        # 驗證輸出目錄
        output_path = Path(self.output_dir)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Cannot create output directory: {e}")
        
        # 驗證播放清單範圍
        if self.playlist_start is not None and self.playlist_start < 1:
            self.playlist_start = 1
        
        if self.playlist_end is not None and self.playlist_end < 1:
            self.playlist_end = None
        
        if (self.playlist_start is not None and self.playlist_end is not None 
            and self.playlist_start > self.playlist_end):
            self.playlist_start, self.playlist_end = self.playlist_end, self.playlist_start
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'url': self.url,
            'output_dir': self.output_dir,
            'output_template': self.output_template,
            'format_selector': self.format_selector,
            'audio_format': self.audio_format,
            'video_quality': self.video_quality,
            'extract_audio': self.extract_audio,
            'keep_video': self.keep_video,
            'subtitles': self.subtitles,
            'auto_subtitles': self.auto_subtitles,
            'subtitle_langs': self.subtitle_langs,
            'write_info_json': self.write_info_json,
            'write_description': self.write_description,
            'write_thumbnail': self.write_thumbnail,
            'embed_subtitles': self.embed_subtitles,
            'embed_thumbnail': self.embed_thumbnail,
            'ignore_errors': self.ignore_errors,
            'no_warnings': self.no_warnings,
            'extract_flat': self.extract_flat,
            'playlist_start': self.playlist_start,
            'playlist_end': self.playlist_end,
            'max_downloads': self.max_downloads,
            'rate_limit': self.rate_limit,
            'retries': self.retries,
            'fragment_retries': self.fragment_retries,
            'skip_unavailable_fragments': self.skip_unavailable_fragments,
            'geo_bypass': self.geo_bypass,
            'proxy': self.proxy,
            'cookies_file': self.cookies_file,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'add_headers': self.add_headers,
            'sleep_interval': self.sleep_interval,
            'max_sleep_interval': self.max_sleep_interval,
            'ffmpeg_location': self.ffmpeg_location,
            'prefer_ffmpeg': self.prefer_ffmpeg
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DownloadParameters':
        """從字典創建實例"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DownloadProgress:
    """下載進度資訊"""
    status: str
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[float] = None
    eta: Optional[int] = None
    elapsed: Optional[float] = None
    filename: Optional[str] = None
    tmpfilename: Optional[str] = None
    fragment_index: Optional[int] = None
    fragment_count: Optional[int] = None
    
    @property
    def percentage(self) -> Optional[float]:
        """計算下載百分比"""
        if self.total_bytes and self.total_bytes > 0:
            return (self.downloaded_bytes / self.total_bytes) * 100
        return None
    
    @property
    def speed_str(self) -> str:
        """格式化速度字符串"""
        if self.speed is None:
            return "未知"
        
        if self.speed < 1024:
            return f"{self.speed:.1f} B/s"
        elif self.speed < 1024 * 1024:
            return f"{self.speed / 1024:.1f} KB/s"
        elif self.speed < 1024 * 1024 * 1024:
            return f"{self.speed / (1024 * 1024):.1f} MB/s"
        else:
            return f"{self.speed / (1024 * 1024 * 1024):.1f} GB/s"
    
    @property
    def eta_str(self) -> str:
        """格式化剩餘時間字符串"""
        if self.eta is None:
            return "未知"
        
        if self.eta < 60:
            return f"{self.eta}秒"
        elif self.eta < 3600:
            return f"{self.eta // 60}分{self.eta % 60}秒"
        else:
            hours = self.eta // 3600
            minutes = (self.eta % 3600) // 60
            return f"{hours}小時{minutes}分"
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'status': self.status,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
            'speed': self.speed,
            'eta': self.eta,
            'elapsed': self.elapsed,
            'filename': self.filename,
            'tmpfilename': self.tmpfilename,
            'fragment_index': self.fragment_index,
            'fragment_count': self.fragment_count,
            'percentage': self.percentage,
            'speed_str': self.speed_str,
            'eta_str': self.eta_str
        }


@dataclass
class DownloadResult:
    """下載結果資料結構"""
    url: str
    title: str
    status: DownloadStatus
    output_files: List[str] = field(default_factory=list)
    file_size: Optional[int] = None
    duration: Optional[float] = None
    format_info: Optional[FormatInfo] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def download_time(self) -> Optional[float]:
        """計算下載時間"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'url': self.url,
            'title': self.title,
            'status': self.status.value,
            'output_files': self.output_files,
            'file_size': self.file_size,
            'duration': self.duration,
            'format_info': self.format_info.to_dict() if self.format_info else None,
            'error_message': self.error_message,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'download_time': self.download_time
        }


@dataclass
class DownloadSummary:
    """下載摘要"""
    total_downloads: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    total_size: int = 0
    total_duration: float = 0.0
    download_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        if self.total_downloads == 0:
            return 0.0
        return (self.successful_downloads / self.total_downloads) * 100
    
    @property
    def average_speed(self) -> Optional[float]:
        """計算平均下載速度"""
        if self.download_time > 0 and self.total_size > 0:
            return self.total_size / self.download_time
        return None
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'total_downloads': self.total_downloads,
            'successful_downloads': self.successful_downloads,
            'failed_downloads': self.failed_downloads,
            'total_size': self.total_size,
            'total_duration': self.total_duration,
            'download_time': self.download_time,
            'success_rate': self.success_rate,
            'average_speed': self.average_speed,
            'errors': self.errors
        }


class DownloadQueue:
    """下載佇列管理"""
    
    def __init__(self, max_concurrent: int = 3):
        self.queue: List[DownloadParameters] = []
        self.active: List[DownloadParameters] = []
        self.completed: List[DownloadResult] = []
        self.max_concurrent = max_concurrent
    
    def add(self, params: DownloadParameters):
        """添加下載任務"""
        self.queue.append(params)
    
    def get_next(self) -> Optional[DownloadParameters]:
        """獲取下一個下載任務"""
        if self.queue and len(self.active) < self.max_concurrent:
            params = self.queue.pop(0)
            self.active.append(params)
            return params
        return None
    
    def complete(self, params: DownloadParameters, result: DownloadResult):
        """標記任務完成"""
        if params in self.active:
            self.active.remove(params)
        self.completed.append(result)
    
    def remove_active(self, params: DownloadParameters):
        """移除活動任務"""
        if params in self.active:
            self.active.remove(params)
    
    def clear(self):
        """清空佇列"""
        self.queue.clear()
        self.active.clear()
        self.completed.clear()
    
    @property
    def total_pending(self) -> int:
        """待處理任務數"""
        return len(self.queue)
    
    @property
    def total_active(self) -> int:
        """活動任務數"""
        return len(self.active)
    
    @property
    def total_completed(self) -> int:
        """已完成任務數"""
        return len(self.completed)
    
    def get_summary(self) -> DownloadSummary:
        """獲取下載摘要"""
        summary = DownloadSummary()
        summary.total_downloads = len(self.completed)
        
        for result in self.completed:
            if result.status == DownloadStatus.COMPLETED:
                summary.successful_downloads += 1
                if result.file_size:
                    summary.total_size += result.file_size
                if result.duration:
                    summary.total_duration += result.duration
                if result.download_time:
                    summary.download_time += result.download_time
            else:
                summary.failed_downloads += 1
                if result.error_message:
                    summary.errors.append(result.error_message)
        
        return summary


# 輔助函數
def create_download_params_from_url(url: str, **kwargs) -> DownloadParameters:
    """從 URL 創建下載參數"""
    return DownloadParameters(url=url, **kwargs)


def parse_format_selector(quality: VideoQuality, audio_format: Optional[AudioFormat] = None) -> str:
    """解析格式選擇器"""
    if quality == VideoQuality.AUDIO_ONLY:
        if audio_format:
            return f"bestaudio[ext={audio_format.value}]/bestaudio"
        return "bestaudio"
    elif quality == VideoQuality.VIDEO_ONLY:
        return "bestvideo"
    else:
        base_format = quality.value
        if audio_format:
            return f"{base_format}+bestaudio[ext={audio_format.value}]/{base_format}+bestaudio/{base_format}"
        return base_format


def format_file_size(size_bytes: int) -> str:
    """格式化檔案大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: float) -> str:
    """格式化播放時長"""
    if seconds < 60:
        return f"{seconds:.0f}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}小時{minutes}分{secs}秒"