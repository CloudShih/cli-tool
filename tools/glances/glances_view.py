"""
Glances 視圖類 - 提供系統監控的 GUI 界面
包含系統概覽、進程監控、磁碟空間、網路詳情等功能模組
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QGroupBox, QTabWidget, QFileDialog,
    QScrollArea, QFrame, QProgressBar, QMessageBox, QSplitter,
    QTextBrowser, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette
import logging

logger = logging.getLogger(__name__)


class GlancesView(QWidget):
    """Glances 視圖類 - 系統監控的 GUI 界面"""
    
    # 信號定義
    start_monitoring = pyqtSignal()
    stop_monitoring = pyqtSignal()
    refresh_data = pyqtSignal()
    update_interval_changed = pyqtSignal(int)
    start_glances_server = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.is_monitoring_started = False
        self.auto_start_attempted = False
        logger.info("GlancesView initialized")
        
        # 延遲自動啟動監控（在視圖完全初始化後）
        QTimer.singleShot(2000, self._try_auto_start_monitoring)
        
    def showEvent(self, event):
        """視圖顯示事件 - 自動啟動監控"""
        super().showEvent(event)
        logger.info("GlancesView showEvent triggered")
        
        # 只在第一次顯示時自動啟動監控
        if not self.auto_start_attempted:
            self.auto_start_attempted = True
            logger.info("Scheduling auto-start monitoring in 1 second")
            # 延遲 1 秒啟動，確保視圖完全載入
            QTimer.singleShot(1000, self._auto_start_monitoring)
            
    def _try_auto_start_monitoring(self):
        """嘗試自動啟動監控（從初始化後延遲調用）"""
        if not self.auto_start_attempted:
            print("[DEBUG] 嘗試自動啟動監控...")
            logger.info("Attempting auto-start monitoring from initialization delay")
            self.auto_start_attempted = True
            self._auto_start_monitoring()
        else:
            print("[DEBUG] 自動啟動已嘗試過，跳過")
    
    def _auto_start_monitoring(self):
        """自動啟動監控"""
        try:
            if not self.is_monitoring_started:
                logger.info("Auto-starting monitoring from showEvent")
                self.start_monitoring.emit()
                self.is_monitoring_started = True
                
                # 更新按鈕狀態
                if hasattr(self, 'start_btn'):
                    self.start_btn.setText("⏹ 停止監控")
                    self.start_btn.clicked.disconnect()
                    self.start_btn.clicked.connect(self.stop_monitoring.emit)
                    
        except Exception as e:
            logger.error(f"Error auto-starting monitoring: {e}")
        
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 標題區域
        title_layout = self.create_title_section()
        layout.addLayout(title_layout)
        
        # 主要內容區域 - 垂直分割器
        main_splitter = QSplitter(Qt.Vertical)
        layout.addWidget(main_splitter)
        
        # 上方：控制面板和快速指標
        top_panel = self.create_top_panel()
        main_splitter.addWidget(top_panel)
        
        # 下方：詳細監控標籤頁
        bottom_panel = self.create_bottom_panel()
        main_splitter.addWidget(bottom_panel)
        
        # 設置分割器比例
        main_splitter.setStretchFactor(0, 1)  # 上方面板
        main_splitter.setStretchFactor(1, 2)  # 下方面板（更大空間）
        
        # 底部狀態欄
        self.create_status_bar(layout)
        
    def create_title_section(self) -> QHBoxLayout:
        """創建標題區域"""
        layout = QHBoxLayout()
        
        # 標題
        title_label = QLabel("Glances - 系統資源監控")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 控制按鈕
        self.start_btn = QPushButton("🚀 開始監控")
        self.start_btn.setMaximumWidth(120)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_monitoring)
        layout.addWidget(self.start_btn)
        
        self.refresh_btn = QPushButton("🔄 重新整理")
        self.refresh_btn.setMaximumWidth(100)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_data.emit)
        layout.addWidget(self.refresh_btn)
        
        # 配置按鈕
        self.config_btn = QPushButton("⚙️ 配置")
        self.config_btn.setMaximumWidth(80)
        self.config_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        self.config_btn.clicked.connect(self.show_config_dialog)
        layout.addWidget(self.config_btn)
        
        return layout
    
    def create_top_panel(self) -> QWidget:
        """創建上方面板（控制和快速指標）"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # 左側：系統概覽
        overview_group = self.create_system_overview()
        layout.addWidget(overview_group, 2)
        
        # 右側：配置控制
        config_group = self.create_config_panel()
        layout.addWidget(config_group, 1)
        
        return panel
    
    def create_system_overview(self) -> QGroupBox:
        """創建系統概覽組件"""
        group = QGroupBox("系統概覽")
        layout = QGridLayout(group)
        
        # CPU 指標
        layout.addWidget(QLabel("CPU 使用率:"), 0, 0)
        self.cpu_label = QLabel("-- %")
        self.cpu_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.cpu_label, 0, 1)
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        layout.addWidget(self.cpu_progress, 0, 2)
        
        # 記憶體指標
        layout.addWidget(QLabel("記憶體使用:"), 1, 0)
        self.memory_label = QLabel("-- / -- MB")
        self.memory_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.memory_label, 1, 1)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        layout.addWidget(self.memory_progress, 1, 2)
        
        # 負載平均值
        layout.addWidget(QLabel("負載平均:"), 2, 0)
        self.load_label = QLabel("-- / -- / --")
        self.load_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.load_label, 2, 1, 1, 2)
        
        # 磁碟 I/O
        layout.addWidget(QLabel("磁碟 I/O:"), 3, 0)
        self.disk_label = QLabel("讀: -- MB/s 寫: -- MB/s")
        self.disk_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.disk_label, 3, 1, 1, 2)
        
        # 網路
        layout.addWidget(QLabel("網路:"), 4, 0)
        self.network_label = QLabel("上行: -- MB/s 下行: -- MB/s")
        self.network_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.network_label, 4, 1, 1, 2)
        
        return group
    
    def create_config_panel(self) -> QGroupBox:
        """創建配置面板"""
        group = QGroupBox("監控設定")
        layout = QVBoxLayout(group)
        
        # 更新間隔設定
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("更新間隔:"))
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(500, 10000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.valueChanged.connect(self.update_interval_changed.emit)
        interval_layout.addWidget(self.interval_spin)
        layout.addLayout(interval_layout)
        
        # Glances 服務器控制
        server_layout = QVBoxLayout()
        server_layout.addWidget(QLabel("Glances 服務器:"))
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(61208)
        port_layout.addWidget(self.port_spin)
        server_layout.addLayout(port_layout)
        
        self.server_btn = QPushButton("啟動 Web 服務器")
        self.server_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.server_btn.clicked.connect(self.start_server)
        server_layout.addWidget(self.server_btn)
        
        layout.addLayout(server_layout)
        
        # 狀態指示
        self.status_indicator = QLabel("● 離線")
        self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")
        layout.addWidget(self.status_indicator)
        
        layout.addStretch()
        
        return group
    
    def create_bottom_panel(self) -> QWidget:
        """創建下方面板（詳細監控標籤頁）"""
        tab_widget = QTabWidget()
        
        # 進程監控標籤
        process_tab = self.create_process_tab()
        tab_widget.addTab(process_tab, "進程監控")
        
        # 磁碟空間標籤
        disk_tab = self.create_disk_tab()
        tab_widget.addTab(disk_tab, "磁碟空間")
        
        # 網路詳情標籤
        network_tab = self.create_network_tab()
        tab_widget.addTab(network_tab, "網路詳情")
        
        # 原始數據標籤
        raw_data_tab = self.create_raw_data_tab()
        tab_widget.addTab(raw_data_tab, "原始數據")
        
        return tab_widget
    
    def create_process_tab(self) -> QWidget:
        """創建進程監控標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 進程表格
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "進程名稱", "CPU %", "記憶體 %", "狀態", "命令行"
        ])
        
        # 設置表格屬性
        header = self.process_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # PID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 名稱
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CPU
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 記憶體
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 狀態
        
        # 設置暗色主題樣式
        self.process_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                gridline-color: #34495e;
                border: 1px solid #34495e;
            }
            QTableWidget::item {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 6px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.process_table)
        
        return widget
    
    def create_disk_tab(self) -> QWidget:
        """創建磁碟空間標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 磁碟空間表格
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(5)
        self.disk_table.setHorizontalHeaderLabels([
            "磁碟", "總容量", "已使用", "可用空間", "使用率 %"
        ])
        
        header = self.disk_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # 設置暗色主題樣式
        self.disk_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                gridline-color: #34495e;
                border: 1px solid #34495e;
            }
            QTableWidget::item {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 6px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.disk_table)
        
        return widget
    
    def create_network_tab(self) -> QWidget:
        """創建網路詳情標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 網路介面表格
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(6)
        self.network_table.setHorizontalHeaderLabels([
            "介面", "接收 (MB)", "發送 (MB)", "接收速率", "發送速率", "狀態"
        ])
        
        header = self.network_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # 設置暗色主題樣式
        self.network_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                gridline-color: #34495e;
                border: 1px solid #34495e;
            }
            QTableWidget::item {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 6px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.network_table)
        
        return widget
    
    def create_raw_data_tab(self) -> QWidget:
        """創建原始數據標籤頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 原始數據顯示
        self.raw_data_display = QTextBrowser()
        self.raw_data_display.setFont(QFont("Consolas", 10))
        self.raw_data_display.setStyleSheet("""
            QTextBrowser {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.raw_data_display)
        
        return widget
    
    def create_status_bar(self, layout):
        """創建狀態欄"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("準備就緒")
        self.connection_status = QLabel("● 未連接")
        self.connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status)
        
        layout.addWidget(status_frame)
    
    # UI 更新方法
    def update_system_overview(self, data: dict):
        """更新系統概覽"""
        try:
            # 更新 CPU
            cpu_data = data.get('cpu', {})
            if cpu_data:
                cpu_percent = cpu_data.get('total', 0)
                self.cpu_label.setText(f"{cpu_percent:.1f} %")
                self.cpu_progress.setValue(int(cpu_percent))
            
            # 更新記憶體
            mem_data = data.get('mem', {})
            if mem_data:
                total = mem_data.get('total', 0) / (1024**3)  # 轉換為 GB
                used = mem_data.get('used', 0) / (1024**3)
                percent = mem_data.get('percent', 0)
                
                self.memory_label.setText(f"{used:.1f} / {total:.1f} GB")
                self.memory_progress.setValue(int(percent))
            
            # 更新網路（示例）
            network_data = data.get('network', [])
            if network_data:
                total_rx = sum(iface.get('rx', 0) for iface in network_data) / (1024**2)
                total_tx = sum(iface.get('tx', 0) for iface in network_data) / (1024**2)
                self.network_label.setText(f"下行: {total_rx:.1f} MB/s 上行: {total_tx:.1f} MB/s")
            
        except Exception as e:
            logger.error(f"Error updating system overview: {e}")
        
        # 更新進程數據
        processes_data = data.get('processlist', data.get('processes', []))
        if processes_data:
            self.update_process_table(processes_data)
        
        # 更新磁碟數據
        self.update_disk_data(data)
        
        # 更新網路詳情數據
        self.update_network_data(data)
        
        # 更新原始數據
        self.update_raw_data(data)
    
    def update_process_table(self, processes: list):
        """更新進程表格"""
        try:
            self.process_table.setRowCount(len(processes))
            
            for row, process in enumerate(processes):
                self.process_table.setItem(row, 0, QTableWidgetItem(str(process.get('pid', ''))))
                self.process_table.setItem(row, 1, QTableWidgetItem(process.get('name', '')))
                self.process_table.setItem(row, 2, QTableWidgetItem(f"{process.get('cpu_percent', 0):.1f}"))
                self.process_table.setItem(row, 3, QTableWidgetItem(f"{process.get('memory_percent', 0):.1f}"))
                self.process_table.setItem(row, 4, QTableWidgetItem(process.get('status', '')))
                self.process_table.setItem(row, 5, QTableWidgetItem(process.get('cmdline', '')))
                
        except Exception as e:
            logger.error(f"Error updating process table: {e}")
    
    def update_disk_data(self, data: dict):
        """更新磁碟空間數據"""
        try:
            if 'fs' not in data or not data['fs']:
                return
                
            fs_data = data['fs']
            if not isinstance(fs_data, list):
                return
                
            self.disk_table.setRowCount(len(fs_data))
            
            for row, disk in enumerate(fs_data):
                # 磁碟名稱
                device_name = disk.get('device_name', disk.get('mnt_point', 'Unknown'))
                self.disk_table.setItem(row, 0, QTableWidgetItem(device_name))
                
                # 總容量 (轉換為 GB)
                total_bytes = disk.get('size', 0)
                total_gb = total_bytes / (1024**3) if total_bytes else 0
                self.disk_table.setItem(row, 1, QTableWidgetItem(f"{total_gb:.1f} GB"))
                
                # 已使用 (轉換為 GB)
                used_bytes = disk.get('used', 0)
                used_gb = used_bytes / (1024**3) if used_bytes else 0
                self.disk_table.setItem(row, 2, QTableWidgetItem(f"{used_gb:.1f} GB"))
                
                # 可用空間 (轉換為 GB)
                free_bytes = disk.get('free', 0)
                free_gb = free_bytes / (1024**3) if free_bytes else 0
                self.disk_table.setItem(row, 3, QTableWidgetItem(f"{free_gb:.1f} GB"))
                
                # 使用率
                percent = disk.get('percent', 0)
                self.disk_table.setItem(row, 4, QTableWidgetItem(f"{percent:.1f}%"))
                
        except Exception as e:
            logger.error(f"Error updating disk data: {e}")
    
    def update_network_data(self, data: dict):
        """更新網路詳情數據"""
        try:
            if 'network' not in data or not data['network']:
                return
                
            network_data = data['network']
            if not isinstance(network_data, list):
                return
                
            self.network_table.setRowCount(len(network_data))
            
            for row, interface in enumerate(network_data):
                # 介面名稱
                interface_name = interface.get('interface_name', f'eth{row}')
                self.network_table.setItem(row, 0, QTableWidgetItem(interface_name))
                
                # 接收 (轉換為 MB)
                rx_bytes = interface.get('cumulative_rx', interface.get('rx', 0))
                rx_mb = rx_bytes / (1024*1024) if rx_bytes else 0
                self.network_table.setItem(row, 1, QTableWidgetItem(f"{rx_mb:.2f}"))
                
                # 發送 (轉換為 MB)
                tx_bytes = interface.get('cumulative_tx', interface.get('tx', 0))
                tx_mb = tx_bytes / (1024*1024) if tx_bytes else 0
                self.network_table.setItem(row, 2, QTableWidgetItem(f"{tx_mb:.2f}"))
                
                # 接收速率
                rx_rate = interface.get('rx_rate', 0)
                rx_rate_kb = rx_rate / 1024 if rx_rate else 0
                self.network_table.setItem(row, 3, QTableWidgetItem(f"{rx_rate_kb:.1f} KB/s"))
                
                # 發送速率
                tx_rate = interface.get('tx_rate', 0)
                tx_rate_kb = tx_rate / 1024 if tx_rate else 0
                self.network_table.setItem(row, 4, QTableWidgetItem(f"{tx_rate_kb:.1f} KB/s"))
                
                # 狀態
                is_up = interface.get('is_up', True)
                status = "活躍" if is_up else "未活躍"
                self.network_table.setItem(row, 5, QTableWidgetItem(status))
                
        except Exception as e:
            logger.error(f"Error updating network data: {e}")

    def update_raw_data(self, data: dict):
        """更新原始數據顯示"""
        import json
        try:
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
            self.raw_data_display.setPlainText(formatted_data)
        except Exception as e:
            logger.error(f"Error updating raw data: {e}")
    
    def set_status(self, message: str):
        """設置狀態訊息"""
        self.status_label.setText(message)
    
    def set_connection_status(self, connected: bool, mode: str = ""):
        """設置連接狀態"""
        if connected:
            self.connection_status.setText(f"● 已連接 ({mode})")
            self.connection_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.status_indicator.setText("● 線上")
            self.status_indicator.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.connection_status.setText("● 未連接")
            self.connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.status_indicator.setText("● 離線")
            self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def toggle_monitoring(self):
        """切換監控狀態"""
        if self.start_btn.text() == "🚀 開始監控":
            self.start_monitoring.emit()
            self.start_btn.setText("⏹ 停止監控")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
        else:
            self.stop_monitoring.emit()
            self.start_btn.setText("🚀 開始監控")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
            """)
    
    def start_server(self):
        """啟動 Glances 服務器"""
        port = self.port_spin.value()
        self.start_glances_server.emit(port)
    
    def show_error(self, title: str, message: str):
        """顯示錯誤訊息"""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title: str, message: str):
        """顯示信息訊息"""
        QMessageBox.information(self, title, message)
    
    def show_config_dialog(self):
        """顯示配置對話框"""
        try:
            from .config.config_manager import GlancesConfigManager
            from .config.config_dialog import ConfigDialog
            
            # 創建配置管理器
            if not hasattr(self, 'config_manager'):
                self.config_manager = GlancesConfigManager()
            
            # 顯示配置對話框
            dialog = ConfigDialog(self.config_manager, self)
            dialog.config_changed.connect(self.on_config_changed)
            dialog.exec_()
            
        except ImportError:
            QMessageBox.warning(self, "功能不可用", "配置功能目前不可用")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"打開配置對話框時發生錯誤:\n{str(e)}")
    
    def on_config_changed(self, config_summary: dict):
        """配置變更處理"""
        try:
            # 發送配置變更信號給控制器
            # 這將在控制器中處理
            pass
            
        except Exception as e:
            logger.error(f"Error handling config change: {e}")
    
    def showEvent(self, event):
        """視圖顯示事件 - 自動啟動監控"""
        super().showEvent(event)
        
        # 只在第一次顯示時啟動監控
        if not self.is_monitoring_started and hasattr(self, 'parent') and hasattr(self.parent(), 'parent'):
            try:
                # 嘗試通過信號啟動監控
                QTimer.singleShot(1000, self._auto_start_monitoring)
            except Exception as e:
                logger.error(f"Error in showEvent: {e}")
    
    def _auto_start_monitoring(self):
        """自動啟動監控"""
        try:
            if not self.is_monitoring_started:
                self.start_monitoring.emit()
                self.is_monitoring_started = True
                logger.info("Auto-started monitoring from view showEvent")
        except Exception as e:
            logger.error(f"Error auto-starting monitoring: {e}")