"""
格式選擇器組件
提供影片/音訊格式選擇界面
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QGroupBox, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..core.data_models import VideoQuality, AudioFormat


class FormatSelector(QWidget):
    """格式選擇器組件"""
    
    format_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """設定界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 品質選擇
        quality_group = QGroupBox("影片品質")
        quality_layout = QVBoxLayout(quality_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("最佳品質", VideoQuality.BEST.value)
        self.quality_combo.addItem("1080p HD", VideoQuality.HD_1080P.value)
        self.quality_combo.addItem("720p HD", VideoQuality.HD_720P.value)
        self.quality_combo.addItem("480p SD", VideoQuality.SD_480P.value)
        self.quality_combo.addItem("360p SD", VideoQuality.SD_360P.value)
        self.quality_combo.addItem("僅音訊", VideoQuality.AUDIO_ONLY.value)
        self.quality_combo.addItem("僅影片", VideoQuality.VIDEO_ONLY.value)
        self.quality_combo.addItem("最低品質", VideoQuality.WORST.value)
        self.quality_combo.currentTextChanged.connect(self.format_changed.emit)
        
        quality_layout.addWidget(QLabel("選擇影片品質:"))
        quality_layout.addWidget(self.quality_combo)
        layout.addWidget(quality_group)
        
        # 音訊格式選擇
        audio_group = QGroupBox("音訊設定")
        audio_layout = QVBoxLayout(audio_group)
        
        # 音訊格式
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItem("自動選擇", "")
        self.audio_format_combo.addItem("MP3", AudioFormat.MP3.value)
        self.audio_format_combo.addItem("AAC", AudioFormat.AAC.value)
        self.audio_format_combo.addItem("M4A", AudioFormat.M4A.value)
        self.audio_format_combo.addItem("OGG", AudioFormat.OGG.value)
        self.audio_format_combo.addItem("FLAC", AudioFormat.FLAC.value)
        self.audio_format_combo.addItem("WAV", AudioFormat.WAV.value)
        self.audio_format_combo.currentTextChanged.connect(self.format_changed.emit)
        
        # 音訊選項
        self.extract_audio_check = QCheckBox("僅提取音訊")
        self.extract_audio_check.stateChanged.connect(self.format_changed.emit)
        
        self.keep_video_check = QCheckBox("保留影片檔案")
        self.keep_video_check.setChecked(True)
        self.keep_video_check.stateChanged.connect(self.format_changed.emit)
        
        audio_layout.addWidget(QLabel("音訊格式:"))
        audio_layout.addWidget(self.audio_format_combo)
        audio_layout.addWidget(self.extract_audio_check)
        audio_layout.addWidget(self.keep_video_check)
        layout.addWidget(audio_group)
        
        # 進階選項
        advanced_group = QGroupBox("進階選項")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # 自訂格式字串
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("自訂格式:"))
        
        self.custom_format_combo = QComboBox()
        self.custom_format_combo.setEditable(True)
        self.custom_format_combo.addItem("best", "best")
        self.custom_format_combo.addItem("worst", "worst")
        self.custom_format_combo.addItem("best[height<=720]", "best[height<=720]")
        self.custom_format_combo.addItem("bestvideo+bestaudio", "bestvideo+bestaudio")
        self.custom_format_combo.currentTextChanged.connect(self.format_changed.emit)
        
        custom_layout.addWidget(self.custom_format_combo)
        advanced_layout.addLayout(custom_layout)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
    
    def get_format_selector(self) -> str:
        """獲取格式選擇器字串"""
        # 如果有自訂格式，優先使用
        custom_format = self.custom_format_combo.currentText().strip()
        if custom_format and custom_format != self.custom_format_combo.currentData():
            return custom_format
        
        # 根據選擇建構格式字串
        quality = self.quality_combo.currentData()
        audio_format = self.audio_format_combo.currentData()
        
        if self.extract_audio_check.isChecked():
            if audio_format:
                return f"bestaudio[ext={audio_format}]/bestaudio"
            return "bestaudio"
        
        if quality == VideoQuality.AUDIO_ONLY.value:
            if audio_format:
                return f"bestaudio[ext={audio_format}]/bestaudio"
            return "bestaudio"
        elif quality == VideoQuality.VIDEO_ONLY.value:
            return "bestvideo"
        else:
            base_format = quality
            if audio_format:
                return f"{base_format}+bestaudio[ext={audio_format}]/{base_format}+bestaudio/{base_format}"
            return base_format
    
    def get_audio_format(self) -> str:
        """獲取音訊格式"""
        return self.audio_format_combo.currentData() or ""
    
    def is_extract_audio(self) -> bool:
        """是否僅提取音訊"""
        return self.extract_audio_check.isChecked()
    
    def is_keep_video(self) -> bool:
        """是否保留影片"""
        return self.keep_video_check.isChecked()
    
    def set_format_selector(self, format_str: str):
        """設定格式選擇器"""
        # 嘗試在預設選項中匹配
        for i in range(self.quality_combo.count()):
            if self.quality_combo.itemData(i) == format_str:
                self.quality_combo.setCurrentIndex(i)
                return
        
        # 如果沒有匹配，設定為自訂格式
        self.custom_format_combo.setCurrentText(format_str)