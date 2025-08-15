"""
Glances 配置管理器
處理用戶偏好設定、監控參數和圖表配置
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """監控配置"""
    update_interval: int = 1000  # 更新間隔（毫秒）
    max_processes: int = 20      # 最大進程數
    enable_auto_scale: bool = True  # 自動縮放
    chart_range: int = 60        # 圖表時間範圍（秒）
    enable_charts: bool = True   # 啟用圖表
    

@dataclass 
class DisplayConfig:
    """顯示配置"""
    theme: str = "default"       # 主題
    show_grid: bool = True       # 顯示網格
    show_legend: bool = True     # 顯示圖例
    font_size: int = 10          # 字體大小
    animation_enabled: bool = True  # 動畫效果


@dataclass
class ConnectionConfig:
    """連接配置"""
    web_api_url: str = "http://localhost:61208/api/3"
    web_api_timeout: int = 5
    web_api_retry: int = 3
    fallback_enabled: bool = True
    glances_port: int = 61208


@dataclass
class AlertConfig:
    """警告配置"""
    cpu_threshold: float = 80.0      # CPU 警告閾值
    memory_threshold: float = 85.0   # 記憶體警告閾值
    disk_threshold: float = 90.0     # 磁碟警告閾值
    enable_alerts: bool = True       # 啟用警告
    alert_sound: bool = False        # 警告聲音


class GlancesConfigManager:
    """Glances 配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        # 配置目錄
        if config_dir is None:
            self.config_dir = Path.home() / ".glances_plugin"
        else:
            self.config_dir = Path(config_dir)
            
        self.config_file = self.config_dir / "config.json"
        
        # 確保配置目錄存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 默認配置
        self.monitoring = MonitoringConfig()
        self.display = DisplayConfig()
        self.connection = ConnectionConfig()
        self.alerts = AlertConfig()
        
        # 載入配置
        self.load_config()
        
        logger.info(f"GlancesConfigManager initialized: {self.config_dir}")
        
    def load_config(self) -> bool:
        """載入配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 更新配置
                if 'monitoring' in data:
                    self.monitoring = MonitoringConfig(**data['monitoring'])
                if 'display' in data:
                    self.display = DisplayConfig(**data['display'])
                if 'connection' in data:
                    self.connection = ConnectionConfig(**data['connection'])
                if 'alerts' in data:
                    self.alerts = AlertConfig(**data['alerts'])
                    
                logger.info("Configuration loaded successfully")
                return True
            else:
                logger.info("No config file found, using defaults")
                self.save_config()  # 保存默認配置
                return True
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
            
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            config_data = {
                'monitoring': asdict(self.monitoring),
                'display': asdict(self.display),
                'connection': asdict(self.connection),
                'alerts': asdict(self.alerts),
                'version': '1.0.0',
                'last_updated': str(Path.ctime(Path.now()) if hasattr(Path, 'now') else 'unknown')
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
            
    def get_monitoring_config(self) -> MonitoringConfig:
        """獲取監控配置"""
        return self.monitoring
        
    def get_display_config(self) -> DisplayConfig:
        """獲取顯示配置"""
        return self.display
        
    def get_connection_config(self) -> ConnectionConfig:
        """獲取連接配置"""
        return self.connection
        
    def get_alert_config(self) -> AlertConfig:
        """獲取警告配置"""
        return self.alerts
        
    def update_monitoring_config(self, **kwargs) -> bool:
        """更新監控配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
                else:
                    logger.warning(f"Unknown monitoring config key: {key}")
                    
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating monitoring config: {e}")
            return False
            
    def update_display_config(self, **kwargs) -> bool:
        """更新顯示配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.display, key):
                    setattr(self.display, key, value)
                else:
                    logger.warning(f"Unknown display config key: {key}")
                    
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating display config: {e}")
            return False
            
    def update_connection_config(self, **kwargs) -> bool:
        """更新連接配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.connection, key):
                    setattr(self.connection, key, value)
                else:
                    logger.warning(f"Unknown connection config key: {key}")
                    
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating connection config: {e}")
            return False
            
    def update_alert_config(self, **kwargs) -> bool:
        """更新警告配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.alerts, key):
                    setattr(self.alerts, key, value)
                else:
                    logger.warning(f"Unknown alert config key: {key}")
                    
            return self.save_config()
        except Exception as e:
            logger.error(f"Error updating alert config: {e}")
            return False
            
    def reset_to_defaults(self) -> bool:
        """重置為默認配置"""
        try:
            self.monitoring = MonitoringConfig()
            self.display = DisplayConfig()
            self.connection = ConnectionConfig()
            self.alerts = AlertConfig()
            
            return self.save_config()
        except Exception as e:
            logger.error(f"Error resetting config: {e}")
            return False
            
    def validate_config(self) -> Dict[str, list]:
        """驗證配置有效性"""
        errors = {
            'monitoring': [],
            'display': [],
            'connection': [],
            'alerts': []
        }
        
        # 驗證監控配置
        if not (500 <= self.monitoring.update_interval <= 60000):
            errors['monitoring'].append("更新間隔必須在 500-60000ms 之間")
            
        if not (1 <= self.monitoring.max_processes <= 100):
            errors['monitoring'].append("最大進程數必須在 1-100 之間")
            
        if not (10 <= self.monitoring.chart_range <= 600):
            errors['monitoring'].append("圖表時間範圍必須在 10-600 秒之間")
            
        # 驗證連接配置
        if not (1 <= self.connection.web_api_timeout <= 30):
            errors['connection'].append("API 超時時間必須在 1-30 秒之間")
            
        if not (1 <= self.connection.web_api_retry <= 10):
            errors['connection'].append("重試次數必須在 1-10 之間")
            
        if not (1024 <= self.connection.glances_port <= 65535):
            errors['connection'].append("端口必須在 1024-65535 之間")
            
        # 驗證警告配置
        if not (0 <= self.alerts.cpu_threshold <= 100):
            errors['alerts'].append("CPU 警告閾值必須在 0-100% 之間")
            
        if not (0 <= self.alerts.memory_threshold <= 100):
            errors['alerts'].append("記憶體警告閾值必須在 0-100% 之間")
            
        if not (0 <= self.alerts.disk_threshold <= 100):
            errors['alerts'].append("磁碟警告閾值必須在 0-100% 之間")
            
        # 驗證顯示配置
        if not (8 <= self.display.font_size <= 24):
            errors['display'].append("字體大小必須在 8-24 之間")
            
        return errors
        
    def export_config(self, export_path: Path) -> bool:
        """導出配置到指定路徑"""
        try:
            config_data = {
                'monitoring': asdict(self.monitoring),
                'display': asdict(self.display),
                'connection': asdict(self.connection),
                'alerts': asdict(self.alerts),
                'export_timestamp': str(Path.ctime(Path.now()) if hasattr(Path, 'now') else 'unknown'),
                'version': '1.0.0'
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False
            
    def import_config(self, import_path: Path) -> bool:
        """從指定路徑導入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 暫存當前配置
            old_monitoring = self.monitoring
            old_display = self.display
            old_connection = self.connection
            old_alerts = self.alerts
            
            try:
                # 載入新配置
                if 'monitoring' in data:
                    self.monitoring = MonitoringConfig(**data['monitoring'])
                if 'display' in data:
                    self.display = DisplayConfig(**data['display'])
                if 'connection' in data:
                    self.connection = ConnectionConfig(**data['connection'])
                if 'alerts' in data:
                    self.alerts = AlertConfig(**data['alerts'])
                    
                # 驗證配置
                validation_errors = self.validate_config()
                has_errors = any(errors for errors in validation_errors.values())
                
                if has_errors:
                    # 恢復舊配置
                    self.monitoring = old_monitoring
                    self.display = old_display
                    self.connection = old_connection
                    self.alerts = old_alerts
                    
                    logger.error("Imported config failed validation")
                    return False
                    
                # 保存新配置
                self.save_config()
                logger.info(f"Configuration imported from: {import_path}")
                return True
                
            except Exception as e:
                # 恢復舊配置
                self.monitoring = old_monitoring
                self.display = old_display
                self.connection = old_connection
                self.alerts = old_alerts
                raise e
                
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False
            
    def get_config_summary(self) -> Dict[str, Any]:
        """獲取配置摘要"""
        return {
            'monitoring': {
                'update_interval': f"{self.monitoring.update_interval}ms",
                'max_processes': self.monitoring.max_processes,
                'charts_enabled': self.monitoring.enable_charts
            },
            'connection': {
                'api_url': self.connection.web_api_url,
                'fallback_enabled': self.connection.fallback_enabled
            },
            'alerts': {
                'cpu_threshold': f"{self.alerts.cpu_threshold}%",
                'memory_threshold': f"{self.alerts.memory_threshold}%",
                'alerts_enabled': self.alerts.enable_alerts
            },
            'display': {
                'theme': self.display.theme,
                'font_size': self.display.font_size
            }
        }