"""
實時圖表組件 - 提供系統監控數據的實時圖表顯示
支援 CPU、記憶體、磁碟 I/O、網路等多種指標的時間序列圖表
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QComboBox, QCheckBox, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
import logging
from collections import deque
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)


class TimeSeriesData:
    """時間序列數據容器"""
    
    def __init__(self, max_points: int = 120):  # 2分鐘的數據（每秒1個點）
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.name = ""
        self.unit = ""
        self.color = QColor(0, 120, 255)  # 默認藍色
        
    def add_point(self, value: float, timestamp: Optional[float] = None):
        """添加數據點"""
        if timestamp is None:
            timestamp = time.time()
        
        self.timestamps.append(timestamp)
        self.values.append(value)
        
    def get_recent_data(self, seconds: int = 60) -> tuple:
        """獲取最近指定秒數的數據"""
        if not self.timestamps:
            return [], []
            
        current_time = time.time()
        cutoff_time = current_time - seconds
        
        recent_timestamps = []
        recent_values = []
        
        for ts, val in zip(self.timestamps, self.values):
            if ts >= cutoff_time:
                recent_timestamps.append(ts)
                recent_values.append(val)
                
        return recent_timestamps, recent_values
        
    def get_all_data(self) -> tuple:
        """獲取所有數據"""
        return list(self.timestamps), list(self.values)
        
    def clear(self):
        """清空數據"""
        self.timestamps.clear()
        self.values.clear()


class RealTimeChart(QWidget):
    """實時圖表組件"""
    
    # 預設顏色方案
    CHART_COLORS = [
        QColor(0, 120, 255),    # 藍色
        QColor(255, 99, 132),   # 紅色
        QColor(54, 162, 235),   # 淺藍色
        QColor(255, 205, 86),   # 黃色
        QColor(75, 192, 192),   # 青色
        QColor(153, 102, 255),  # 紫色
        QColor(255, 159, 64),   # 橙色
        QColor(199, 199, 199)   # 灰色
    ]
    
    def __init__(self, title: str = "系統監控圖表", parent=None):
        super().__init__(parent)
        self.title = title
        self.series_data = {}  # 存儲多個時間序列
        self.chart_range = 60  # 顯示範圍（秒）
        self.auto_scale = True
        self.y_min = 0
        self.y_max = 100
        self.grid_enabled = True
        self.legend_enabled = True
        
        # 簡化的重繪控制
        self.needs_redraw = False
        
        self.setup_ui()
        self.setup_chart_area()
        
        # 優化的更新定時器 - 使用較快的檢查頻率但智能重繪
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.smart_update_chart)
        self.update_timer.start(250)  # 每250ms檢查一次是否需要重繪
        
        logger.info(f"RealTimeChart initialized: {title}")
        
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # 標題和控制區域 - 緊湊設計
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # 圖表區域 - 擴展以填滿剩餘空間
        self.chart_frame = QFrame()
        self.chart_frame.setFrameStyle(QFrame.StyledPanel)
        self.chart_frame.setMinimumHeight(300)  # 增加最小高度
        self.setMinimumHeight(400)  # 設置整個組件最小高度
        layout.addWidget(self.chart_frame, 1)  # stretch factor = 1，填滿剩餘空間
        
    def create_header(self) -> QHBoxLayout:
        """創建標題和控制區域"""
        layout = QHBoxLayout()
        
        # 標題 - 緊湊設計
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 2px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 時間範圍選擇 - 緊湊標籤
        range_label = QLabel("範圍:")
        range_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(range_label)
        
        self.range_combo = QComboBox()
        self.range_combo.addItems(["30秒", "1分鐘", "2分鐘", "5分鐘"])
        self.range_combo.setCurrentText("1分鐘")
        self.range_combo.currentTextChanged.connect(self.on_range_changed)
        layout.addWidget(self.range_combo)
        
        # 網格線切換
        self.grid_checkbox = QCheckBox("網格線")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.toggled.connect(self.on_grid_toggled)
        layout.addWidget(self.grid_checkbox)
        
        # 圖例切換
        self.legend_checkbox = QCheckBox("圖例")
        self.legend_checkbox.setChecked(True)
        self.legend_checkbox.toggled.connect(self.on_legend_toggled)
        layout.addWidget(self.legend_checkbox)
        
        # 清空數據按鈕
        clear_btn = QPushButton("清空")
        clear_btn.setMaximumWidth(60)
        clear_btn.clicked.connect(self.clear_data)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(clear_btn)
        
        return layout
        
    def setup_chart_area(self):
        """設置圖表繪製區域"""
        self.chart_rect = None
        self.margin_left = 60   # 左邊距 (Y軸標籤)
        self.margin_right = 20  # 右邊距 (圖例空間)
        self.margin_top = 20    # 上邊距
        self.margin_bottom = 40 # 下邊距 (X軸標籤)
        
    def add_series(self, name: str, unit: str = "", color: Optional[QColor] = None) -> bool:
        """添加新的數據系列"""
        if name in self.series_data:
            logger.warning(f"Series '{name}' already exists")
            return False
            
        series = TimeSeriesData()
        series.name = name
        series.unit = unit
        
        # 分配顏色
        if color:
            series.color = color
        else:
            color_index = len(self.series_data) % len(self.CHART_COLORS)
            series.color = self.CHART_COLORS[color_index]
            
        self.series_data[name] = series
        logger.debug(f"Added series: {name}")
        return True
        
    def update_series(self, name: str, value: float, timestamp: Optional[float] = None):
        """更新數據系列"""
        if name not in self.series_data:
            print(f"      [DEBUG] 圖表系列 '{name}' 不存在")
            logger.warning(f"Series '{name}' not found")
            return
            
        print(f"      [DEBUG] 更新圖表系列 '{name}': {value}")
        self.series_data[name].add_point(value, timestamp)
        
        # 檢查數據點數量
        points_count = len(self.series_data[name].values)
        print(f"         [DEBUG] 系列 '{name}' 現在有 {points_count} 個數據點")
        
        # 簡化重繪控制：只標記需要重繪
        self.needs_redraw = True
        print(f"         [DEBUG] 數據已更新，標記需要重繪")
        
    def remove_series(self, name: str) -> bool:
        """移除數據系列"""
        if name in self.series_data:
            del self.series_data[name]
            logger.debug(f"Removed series: {name}")
            return True
        return False
        
    def clear_data(self):
        """清空所有數據"""
        for series in self.series_data.values():
            series.clear()
        self.update()
        logger.debug("Cleared all chart data")
        
    def on_range_changed(self, text: str):
        """時間範圍變更處理"""
        range_map = {
            "30秒": 30,
            "1分鐘": 60,
            "2分鐘": 120,
            "5分鐘": 300
        }
        self.chart_range = range_map.get(text, 60)
        self.update()
        
    def on_grid_toggled(self, checked: bool):
        """網格線切換處理"""
        self.grid_enabled = checked
        self.update()
        
    def on_legend_toggled(self, checked: bool):
        """圖例切換處理"""
        self.legend_enabled = checked
        self.update()
        
    def smart_update_chart(self):
        """智能更新圖表 - 只在需要時重繪"""
        # 簡化邏輯：有標記就重繪，消除錯誤的時間條件
        if self.needs_redraw:
            print(f"         [DEBUG] {self.title} 執行重繪")
            self.needs_redraw = False
            self.update()  # 觸發重繪
    
    def update_chart(self):
        """向後兼容的更新方法"""
        self.needs_redraw = True
        self.update()  # 觸發重繪
    
    def set_update_frequency(self, frequency_ms: int):
        """設置更新頻率（毫秒）"""
        self.redraw_interval = max(100, min(5000, frequency_ms))  # 限制在100ms-5s之間
        print(f"         [DEBUG] {self.title} 更新頻率設為 {self.redraw_interval}ms")
    
    def optimize_for_data_rate(self, data_points_per_second: float):
        """根據數據率自動優化更新頻率"""
        if data_points_per_second <= 0.1:  # 每10秒一個數據點
            optimal_interval = 2000  # 2秒更新一次
        elif data_points_per_second <= 0.5:  # 每2秒一個數據點
            optimal_interval = 1000  # 1秒更新一次
        elif data_points_per_second <= 2:  # 每秒2個數據點
            optimal_interval = 500   # 0.5秒更新一次
        else:  # 高頻數據
            optimal_interval = 250   # 0.25秒更新一次
        
        self.set_update_frequency(optimal_interval)
        
    def paintEvent(self, event):
        """繪製圖表"""
        print(f"         [DEBUG] {self.title} 開始繪製事件")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 使用 chart_frame 的實際大小而不是整個 widget
        if hasattr(self, 'chart_frame'):
            frame_rect = self.chart_frame.geometry()
            # 設置繪製區域為 chart_frame 內部
            self.chart_rect = frame_rect.adjusted(
                self.margin_left, self.margin_top, 
                -self.margin_right, -self.margin_bottom
            )
        else:
            # 回退到原始方法
            self.chart_rect = self.rect().adjusted(
                self.margin_left, self.margin_top, 
                -self.margin_right, -self.margin_bottom
            )
        
        print(f"            📐 [DEBUG] 圖表區域: {self.chart_rect.width()}x{self.chart_rect.height()}")
        
        # 繪製背景
        self.draw_background(painter)
        
        # 繪製網格
        if self.grid_enabled:
            self.draw_grid(painter)
            
        # 繪製軸線
        self.draw_axes(painter)
        
        # 繪製數據線
        self.draw_data_lines(painter)
        
        # 繪製圖例
        if self.legend_enabled:
            self.draw_legend(painter)
            
        print(f"         [DEBUG] {self.title} 繪製完成")
            
    def draw_background(self, painter: QPainter):
        """繪製背景"""
        painter.fillRect(self.chart_rect, QColor(250, 250, 250))
        
        # 邊框
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.chart_rect)
        
    def draw_grid(self, painter: QPainter):
        """繪製網格線"""
        painter.setPen(QPen(QColor(230, 230, 230), 1))
        
        # 垂直網格線（時間）
        for i in range(1, 6):
            x = int(self.chart_rect.left() + (self.chart_rect.width() * i / 6))
            painter.drawLine(x, self.chart_rect.top(), x, self.chart_rect.bottom())
            
        # 水平網格線（數值）
        for i in range(1, 5):
            y = int(self.chart_rect.top() + (self.chart_rect.height() * i / 5))
            painter.drawLine(self.chart_rect.left(), y, self.chart_rect.right(), y)
            
    def draw_axes(self, painter: QPainter):
        """繪製座標軸"""
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setFont(QFont("Segoe UI", 8))
        
        # Y軸標籤
        if self.auto_scale:
            self.calculate_y_range()
            
        y_range = self.y_max - self.y_min
        for i in range(6):
            y_value = self.y_min + (y_range * i / 5)
            y_pos = int(self.chart_rect.bottom() - (self.chart_rect.height() * i / 5))
            
            # 標籤
            label = f"{y_value:.1f}"
            painter.drawText(self.chart_rect.left() - 45, y_pos + 3, label)
            
        # X軸標籤（時間）
        current_time = time.time()
        for i in range(6):
            time_offset = self.chart_range * i / 5
            time_value = current_time - self.chart_range + time_offset
            x_pos = int(self.chart_rect.left() + (self.chart_rect.width() * i / 5))
            
            # 格式化時間
            time_str = time.strftime("%H:%M:%S", time.localtime(time_value))
            painter.drawText(x_pos - 20, self.chart_rect.bottom() + 15, time_str[-8:])
            
    def draw_data_lines(self, painter: QPainter):
        """繪製數據線"""
        if not self.series_data:
            print(f"            [DEBUG] 沒有數據系列可繪製")
            return
            
        current_time = time.time()
        start_time = current_time - self.chart_range
        
        print(f"            [DEBUG] 開始繪製 {len(self.series_data)} 個數據系列")
        
        for series_name, series in self.series_data.items():
            timestamps, values = series.get_recent_data(self.chart_range)
            
            print(f"               [DEBUG] 系列 '{series_name}': {len(timestamps)} 個時間戳, {len(values)} 個數值")
            
            if len(timestamps) < 1:
                print(f"               [DEBUG] 系列 '{series_name}' 沒有數據點，跳過")
                continue
                
            # 設置畫筆
            painter.setPen(QPen(series.color, 2))
            
            print(f"               [DEBUG] 系列 '{series_name}' 使用顏色: {series.color.name()}")
            
            # 轉換為圖表座標
            points = []
            valid_points = 0
            for ts, val in zip(timestamps, values):
                if ts < start_time:
                    continue
                    
                # X座標（時間）
                time_ratio = (ts - start_time) / self.chart_range
                x = int(self.chart_rect.left() + (self.chart_rect.width() * time_ratio))
                
                # Y座標（數值）
                if self.y_max > self.y_min:
                    value_ratio = (val - self.y_min) / (self.y_max - self.y_min)
                    y = int(self.chart_rect.bottom() - (self.chart_rect.height() * value_ratio))
                else:
                    y = int(self.chart_rect.bottom())
                    
                points.append((x, y))
                valid_points += 1
                
            print(f"               [DEBUG] 系列 '{series_name}' 轉換了 {valid_points} 個有效點，Y範圍: {self.y_min:.1f} - {self.y_max:.1f}")
                
            # 繪製線段（需要至少2個點）
            if len(points) >= 2:
                lines_drawn = 0
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    painter.drawLine(x1, y1, x2, y2)
                    lines_drawn += 1
                print(f"               [DEBUG] 系列 '{series_name}' 繪製了 {lines_drawn} 條線段")
            else:
                print(f"               [DEBUG] 系列 '{series_name}' 點數不足，無法繪製線段 (只有 {len(points)} 個點)")
                
            # 繪製數據點（即使只有1個點也顯示）
            painter.setBrush(QBrush(series.color))
            dots_drawn = 0
            for x, y in points:
                painter.drawEllipse(x - 3, y - 3, 6, 6)  # 稍大一點的點
                dots_drawn += 1
            print(f"               [DEBUG] 系列 '{series_name}' 繪製了 {dots_drawn} 個數據點")
                
    def draw_legend(self, painter: QPainter):
        """繪製圖例"""
        if not self.series_data:
            return
            
        painter.setFont(QFont("Segoe UI", 9))
        legend_x = int(self.chart_rect.right() - 150)
        legend_y = int(self.chart_rect.top() + 10)
        
        for i, (name, series) in enumerate(self.series_data.items()):
            y_pos = int(legend_y + (i * 20))
            
            # 顏色方塊
            painter.fillRect(legend_x, y_pos, 12, 12, series.color)
            
            # 名稱和當前值
            if series.values:
                current_value = series.values[-1]
                text = f"{name}: {current_value:.1f} {series.unit}"
            else:
                text = f"{name}: -- {series.unit}"
                
            painter.setPen(QPen(QColor(50, 50, 50), 1))
            painter.drawText(legend_x + 18, y_pos + 10, text)
            
    def calculate_y_range(self):
        """自動計算Y軸範圍"""
        if not self.series_data:
            return
            
        all_values = []
        for series in self.series_data.values():
            _, values = series.get_recent_data(self.chart_range)
            all_values.extend(values)
            
        if all_values:
            min_val = min(all_values)
            max_val = max(all_values)
            
            # 確保y_min不小於0（除非數據本身是負的）
            self.y_min = max(0, min_val * 0.95) if min_val >= 0 else min_val * 1.05
            self.y_max = max_val * 1.05
            
            # 確保最小範圍，給百分比數據合適的範圍
            range_diff = self.y_max - self.y_min
            if range_diff < 1:
                center = (self.y_max + self.y_min) / 2
                self.y_min = max(0, center - 0.5)
                self.y_max = center + 0.5
            elif self.y_max <= 100 and self.y_min >= 0:  # 看起來像百分比數據
                self.y_min = 0
                self.y_max = min(100, max(self.y_max, 10))  # 最小顯示範圍為10%
        else:
            self.y_min = 0
            self.y_max = 100


class SystemChartsWidget(QWidget):
    """系統圖表組合組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.charts = {}
        self.last_update_time = 0
        self.data_rate_monitor = {}  # 監控每個圖表的數據率
        self.setup_ui()
        logger.info("SystemChartsWidget initialized")
        
    def setup_ui(self):
        """設置UI佈局"""
        layout = QVBoxLayout(self)
        self.setMinimumHeight(800)  # 設置整個圖表組件的最小高度
        
        # CPU 和記憶體圖表
        performance_layout = QHBoxLayout()
        
        # CPU 圖表
        self.cpu_chart = RealTimeChart("CPU 使用率 (%)")
        self.cpu_chart.add_series("CPU", "%", QColor(255, 99, 132))
        performance_layout.addWidget(self.cpu_chart)
        
        # 記憶體圖表
        self.memory_chart = RealTimeChart("記憶體使用率 (%)")
        self.memory_chart.add_series("記憶體", "%", QColor(54, 162, 235))
        performance_layout.addWidget(self.memory_chart)
        
        layout.addLayout(performance_layout, 1)  # 給第一行圖表更多空間
        
        # 網路和磁碟圖表
        io_layout = QHBoxLayout()
        
        # 網路圖表
        self.network_chart = RealTimeChart("網路 I/O (MB/s)")
        self.network_chart.add_series("接收", "MB/s", QColor(75, 192, 192))
        self.network_chart.add_series("發送", "MB/s", QColor(255, 205, 86))
        io_layout.addWidget(self.network_chart)
        
        # 磁碟圖表
        self.disk_chart = RealTimeChart("磁碟 I/O (MB/s)")
        self.disk_chart.add_series("讀取", "MB/s", QColor(153, 102, 255))
        self.disk_chart.add_series("寫入", "MB/s", QColor(255, 159, 64))
        io_layout.addWidget(self.disk_chart)
        
        layout.addLayout(io_layout, 1)  # 給第二行圖表更多空間
        
        # 保存圖表引用
        self.charts = {
            'cpu': self.cpu_chart,
            'memory': self.memory_chart,
            'network': self.network_chart,
            'disk': self.disk_chart
        }
        
    def update_data(self, stats: Dict[str, Any]):
        """更新所有圖表數據"""
        try:
            print("[DEBUG] SystemChartsWidget 開始更新圖表數據...")
            current_time = time.time()
            
            # 監控數據更新率
            if self.last_update_time > 0:
                update_interval = current_time - self.last_update_time
                data_rate = 1.0 / update_interval if update_interval > 0 else 1.0
                
                # 每10次更新後優化一次更新頻率
                if hasattr(self, '_update_count'):
                    self._update_count += 1
                else:
                    self._update_count = 1
                
                if self._update_count % 10 == 0:
                    print(f"   [DEBUG] 檢測到數據率: {data_rate:.2f} 更新/秒，優化圖表更新頻率...")
                    for chart in self.charts.values():
                        chart.optimize_for_data_rate(data_rate)
            
            self.last_update_time = current_time
            
            # 更新 CPU 數據
            if 'cpu' in stats:
                cpu_percent = stats['cpu'].get('total', 0)
                print(f"   [DEBUG] 更新 CPU 圖表: {cpu_percent}%")
                self.cpu_chart.update_series("CPU", cpu_percent, current_time)
                
            # 更新記憶體數據
            if 'mem' in stats:
                mem_percent = stats['mem'].get('percent', 0)
                print(f"   [DEBUG] 更新記憶體圖表: {mem_percent}%")
                self.memory_chart.update_series("記憶體", mem_percent, current_time)
                
            # 更新網路數據
            if 'network' in stats and stats['network']:
                # 計算總網路流量
                total_rx = sum(iface.get('rx', 0) for iface in stats['network'])
                total_tx = sum(iface.get('tx', 0) for iface in stats['network'])
                
                # 轉換為 MB/s (假設數據是累計值，需要計算差值)
                rx_mb = total_rx / (1024*1024)
                tx_mb = total_tx / (1024*1024)
                print(f"   [DEBUG] 更新網路圖表: 接收 {rx_mb:.2f} MB/s, 發送 {tx_mb:.2f} MB/s")
                self.network_chart.update_series("接收", rx_mb, current_time)
                self.network_chart.update_series("發送", tx_mb, current_time)
                
            # 更新磁碟數據
            if 'diskio' in stats:
                read_bytes = stats['diskio'].get('read_bytes', 0)
                write_bytes = stats['diskio'].get('write_bytes', 0)
                
                # 轉換為 MB/s
                read_mb = read_bytes / (1024*1024)
                write_mb = write_bytes / (1024*1024)
                print(f"   [DEBUG] 更新磁碟圖表: 讀取 {read_mb:.2f} MB/s, 寫入 {write_mb:.2f} MB/s")
                self.disk_chart.update_series("讀取", read_mb, current_time)
                self.disk_chart.update_series("寫入", write_mb, current_time)
                
            # 檢查所有圖表的數據點數量
            total_points = 0
            for chart_name, chart in self.charts.items():
                chart_points = 0
                for series_name, series in chart.series_data.items():
                    chart_points += len(series.values)
                print(f"   [DEBUG] {chart_name} 圖表: {chart_points} 數據點")
                total_points += chart_points
            
            print(f"   [DEBUG] 總計 {total_points} 個數據點，圖表更新完成")
                
        except Exception as e:
            print(f"   [DEBUG] 圖表數據更新錯誤: {e}")
            logger.error(f"Error updating chart data: {e}")
            
    def clear_all_data(self):
        """清空所有圖表數據"""
        for chart in self.charts.values():
            chart.clear_data()
            
    def get_chart(self, name: str) -> Optional[RealTimeChart]:
        """獲取指定圖表"""
        return self.charts.get(name)