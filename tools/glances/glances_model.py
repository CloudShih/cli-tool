"""
Glances 模型類 - 處理系統監控數據的獲取和處理
支援 Web API 和 Subprocess 雙重模式
"""

import subprocess
import requests
import json
import logging
import platform
from typing import Dict, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class GlancesModel:
    """Glances 模型類 - 封裝系統監控數據獲取功能"""
    
    # 默認配置
    DEFAULT_CONFIG = {
        "base_url": "http://localhost:61208/api/3",
        "timeout": 5,
        "retry_attempts": 3,
        "fallback_enabled": True,
        "update_interval": 1000,
        "glances_port": 61208
    }
    
    # 主要 API 端點
    PRIMARY_ENDPOINTS = [
        "/stats",           # 綜合系統狀態
        "/cpu",            # CPU 詳細信息
        "/mem",            # 記憶體信息
        "/network",        # 網路統計
        "/diskio",         # 磁碟 I/O
        "/fs",             # 檔案系統空間
        "/processes"       # 進程列表
    ]
    
    # 回退命令選項
    FALLBACK_COMMANDS = {
        "basic_stats": ["glances", "--export", "json", "--once"],
        "short_format": ["glances", "--export", "json", "--once"],
        "with_fs": ["glances", "--stdout-json", "now,cpu,mem,network,diskio,fs,processes", "-t", "1"]
    }
    
    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.glances_available = self._check_glances_installation()
        self.api_mode = False
        self.subprocess_mode = False
        self._last_data = {}
        
        # 檢查可用模式
        self._detect_available_modes()
        
    def _check_glances_installation(self) -> bool:
        """檢查 Glances 是否安裝"""
        try:
            result = subprocess.run(['glances', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                logger.info(f"Glances found: {result.stdout.strip()}")
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("Glances tool not found in system PATH")
            return False
    
    def _detect_available_modes(self):
        """檢測可用的數據獲取模式"""
        # 檢查 Web API 模式
        self.api_mode = self._check_web_api_connection()
        
        # 檢查 Subprocess 模式
        self.subprocess_mode = self.glances_available
        
        logger.info(f"Available modes - API: {self.api_mode}, Subprocess: {self.subprocess_mode}")
    
    def _check_web_api_connection(self) -> bool:
        """檢查 Web API 連接"""
        try:
            response = requests.get(
                f"{self.config['base_url']}/status",
                timeout=self.config['timeout']
            )
            if response.status_code == 200:
                logger.info("Glances Web API is available")
                return True
        except requests.exceptions.RequestException:
            logger.debug("Glances Web API not available")
        return False
    
    def check_glances_availability(self) -> Dict[str, Any]:
        """檢查 Glances 工具可用性"""
        return {
            "available": self.api_mode or self.subprocess_mode,
            "web_api": self.api_mode,
            "subprocess": self.subprocess_mode,
            "recommended_mode": "web_api" if self.api_mode else "subprocess" if self.subprocess_mode else "none",
            "installation_status": self.glances_available
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """獲取系統統計數據"""
        print("[DEBUG] GlancesModel 開始獲取系統統計數據...")
        if self.api_mode:
            print("   [DEBUG] 使用 API 模式獲取數據")
            return self._get_stats_via_api()
        elif self.subprocess_mode:
            print("   [DEBUG] 使用子進程模式獲取數據")
            return self._get_stats_via_subprocess()
        else:
            print("   [DEBUG] 使用回退模式獲取數據")
            return self._get_fallback_data()
    
    def _get_stats_via_api(self) -> Dict[str, Any]:
        """通過 Web API 獲取數據"""
        try:
            print("      [DEBUG] 開始通過 API 獲取數據...")
            stats = {}
            
            # 獲取各個端點的數據
            for endpoint in self.PRIMARY_ENDPOINTS:
                try:
                    url = f"{self.config['base_url']}{endpoint}"
                    print(f"         [DEBUG] 請求端點: {endpoint}")
                    response = requests.get(url, timeout=self.config['timeout'])
                    if response.status_code == 200:
                        endpoint_key = endpoint.strip('/')
                        data = response.json()
                        stats[endpoint_key] = data
                        if endpoint == '/cpu':
                            print(f"            [DEBUG] CPU 數據: {data.get('total', 'N/A')}%")
                        elif endpoint == '/mem':
                            print(f"            [DEBUG] 記憶體數據: {data.get('percent', 'N/A')}%")
                    else:
                        print(f"         [DEBUG] 端點 {endpoint} 響應錯誤: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"         [DEBUG] 端點 {endpoint} 請求失敗: {e}")
                    logger.warning(f"Failed to fetch {endpoint}: {e}")
                    continue
            
            if stats:
                self._last_data = stats
                logger.debug("Successfully fetched data via Web API")
                return stats
            else:
                raise Exception("No data received from API")
                
        except Exception as e:
            logger.error(f"API data fetch failed: {e}")
            if self.subprocess_mode and self.config['fallback_enabled']:
                logger.info("Falling back to subprocess mode")
                return self._get_stats_via_subprocess()
            return self._get_fallback_data()
    
    def _get_stats_via_subprocess(self) -> Dict[str, Any]:
        """通過 Subprocess 獲取數據 - 實用簡化版本"""
        try:
            # 使用 psutil 模組 (Glances 的底層依賴) 來直接獲取系統數據
            # 這避免了複雜的 Glances 命令行問題
            data = self._get_system_stats_direct()
            
            if data:
                self._last_data = data
                logger.debug("Successfully fetched data via direct system calls")
                return data
            else:
                raise Exception("Failed to get system stats")
                
        except Exception as e:
            logger.error(f"Direct system stats failed: {e}")
            return self._get_fallback_data()
    
    def _get_system_stats_direct(self) -> Dict[str, Any]:
        """直接使用系統調用獲取監控數據"""
        try:
            import psutil
            import time
            
            # 獲取 CPU 數據
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # 獲取記憶體數據
            memory = psutil.virtual_memory()
            
            # 獲取磁碟 I/O
            disk_io = psutil.disk_io_counters()
            
            # 獲取檔案系統數據 (添加缺失的 fs 數據)
            fs_data = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    fs_data.append({
                        'device_name': partition.device,
                        'mnt_point': partition.mountpoint,
                        'fs_type': partition.fstype,
                        'size': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percent': (partition_usage.used / partition_usage.total) * 100 if partition_usage.total > 0 else 0,
                        'key': 'mnt_point'
                    })
                except (PermissionError, OSError):
                    # 跳過無法訪問的分區
                    continue
            
            # 獲取網路數據
            network_io = psutil.net_io_counters()
            
            # 獲取進程數據（前 10 個按 CPU 使用率排序）
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'memory_percent': pinfo['memory_percent'] or 0,
                        'status': pinfo['status'],
                        'cmdline': ' '.join(proc.cmdline()[:3]) if proc.cmdline() else ''
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 按 CPU 使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            processes = processes[:20]  # 只取前 20 個
            
            # 組裝數據結構
            return {
                'cpu': {
                    'total': cpu_percent,
                    'user': cpu_percent * 0.7,  # 估算值
                    'system': cpu_percent * 0.3,  # 估算值
                    'count': cpu_count
                },
                'mem': {
                    'total': memory.total,
                    'used': memory.used,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'diskio': {
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                },
                'fs': fs_data,
                'network': [
                    {
                        'interface_name': 'total',
                        'rx': network_io.bytes_recv if network_io else 0,
                        'tx': network_io.bytes_sent if network_io else 0,
                        'packets_recv': network_io.packets_recv if network_io else 0,
                        'packets_sent': network_io.packets_sent if network_io else 0
                    }
                ],
                'processes': processes,
                'status': 'direct_system'
            }
            
        except ImportError:
            logger.warning("psutil not available, using fallback data")
            return None
        except Exception as e:
            logger.error(f"Error getting direct system stats: {e}")
            return None
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """獲取回退數據（模擬數據或最後已知數據）"""
        if self._last_data:
            logger.debug("Using last known data")
            return self._last_data
        
        # 提供基本的模擬數據
        logger.warning("Providing simulated fallback data")
        return {
            "cpu": {"total": 0, "user": 0, "system": 0},
            "mem": {"total": 0, "used": 0, "available": 0, "percent": 0},
            "network": [],
            "diskio": [],
            "processes": [],
            "status": "fallback_mode"
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """獲取 CPU 信息"""
        stats = self.get_system_stats()
        return stats.get("cpu", {})
    
    def get_memory_info(self) -> Dict[str, Any]:
        """獲取記憶體信息"""
        stats = self.get_system_stats()
        return stats.get("mem", {})
    
    def get_network_info(self) -> Dict[str, Any]:
        """獲取網路信息"""
        stats = self.get_system_stats()
        return stats.get("network", [])
    
    def get_disk_info(self) -> Dict[str, Any]:
        """獲取磁碟 I/O 信息"""
        stats = self.get_system_stats()
        return stats.get("diskio", [])
    
    def get_process_info(self) -> Dict[str, Any]:
        """獲取進程信息"""
        stats = self.get_system_stats()
        return stats.get("processes", [])
    
    def start_glances_server(self, port: int = None) -> Tuple[bool, str]:
        """啟動 Glances Web 服務器"""
        if not self.glances_available:
            return False, "Glances is not installed"
        
        port = port or self.config['glances_port']
        
        try:
            # 檢查端口是否已被使用
            if self._check_web_api_connection():
                return True, f"Glances server already running on port {port}"
            
            # 啟動 Glances Web 服務器
            command = ['glances', '-w', '--port', str(port)]
            
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            logger.info(f"Attempted to start Glances server on port {port}")
            return True, f"Glances server starting on port {port}"
            
        except Exception as e:
            logger.error(f"Failed to start Glances server: {e}")
            return False, f"Failed to start server: {str(e)}"
    
    def update_config(self, config_updates: Dict[str, Any]):
        """更新配置"""
        self.config.update(config_updates)
        
        # 重新檢測模式
        if 'base_url' in config_updates or 'glances_port' in config_updates:
            self._detect_available_modes()
    
    def get_installation_info(self) -> Dict[str, str]:
        """獲取安裝信息和建議"""
        system = platform.system().lower()
        
        installation_info = {
            "windows": {
                "install_command": "pip install glances",
                "description": "使用 pip 安裝 Glances"
            },
            "linux": {
                "install_command": "sudo apt install glances  # 或 pip install glances",
                "description": "使用包管理器或 pip 安裝 Glances"
            },
            "darwin": {
                "install_command": "brew install glances  # 或 pip install glances", 
                "description": "使用 Homebrew 或 pip 安裝 Glances"
            }
        }
        
        return installation_info.get(system, installation_info["linux"])