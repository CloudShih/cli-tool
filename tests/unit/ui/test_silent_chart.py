#!/usr/bin/env python3
"""
靜默圖表測試 - 驗證修復效果
"""
import sys
import os
import time
import random

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from collections import deque

class SimpleChart(QWidget):
    """簡化圖表組件 - 無調試輸出"""
    
    def __init__(self, title="Test Chart", parent=None):
        super().__init__(parent)
        self.title = title
        self.data_points = deque(maxlen=60)  # 最多60個點
        self.setMinimumHeight(200)
        
        # 更新定時器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(1000)  # 每秒重繪
        
    def add_data_point(self, value):
        """添加數據點"""
        self.data_points.append(value)
        
    def paintEvent(self, event):
        """繪製圖表"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 繪製背景
        chart_rect = self.rect().adjusted(40, 20, -20, -40)
        painter.fillRect(chart_rect, QColor(250, 250, 250))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(chart_rect)
        
        # 繪製標題
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 15, self.title)
        
        # 繪製數據線
        if len(self.data_points) >= 2:
            painter.setPen(QPen(QColor(0, 120, 255), 2))
            
            # 計算點位置
            points = []
            width = chart_rect.width()
            height = chart_rect.height()
            
            for i, value in enumerate(self.data_points):
                x = chart_rect.left() + (i * width / max(1, len(self.data_points) - 1))
                y = chart_rect.bottom() - (value / 100 * height)  # 假設0-100範圍
                points.append((int(x), int(y)))
            
            # 繪製線段
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                painter.drawLine(x1, y1, x2, y2)
            
            # 繪製數據點
            painter.setBrush(QBrush(QColor(0, 120, 255)))
            for x, y in points:
                painter.drawEllipse(x - 3, y - 3, 6, 6)
        
        # 顯示數據點數量
        if self.data_points:
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setFont(QFont("Arial", 10))
            point_count = len(self.data_points)
            last_value = self.data_points[-1] if self.data_points else 0
            status_text = f"Points: {point_count}, Last: {last_value:.1f}"
            painter.drawText(chart_rect.right() - 120, chart_rect.bottom() + 15, status_text)

class SilentChartTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Silent Chart Test - Verify Fix")
        self.setGeometry(100, 100, 800, 600)
        
        # 創建中央 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加說明
        self.info_label = QLabel("Testing chart fix: Should show continuous line without blanking")
        layout.addWidget(self.info_label)
        
        # 創建圖表
        self.chart = SimpleChart("CPU Usage Test")
        layout.addWidget(self.chart)
        
        # 添加控制按鈕
        self.start_btn = QPushButton("Start Test")
        self.start_btn.clicked.connect(self.start_test)
        layout.addWidget(self.start_btn)
        
        # 數據計數器
        self.data_count = 0
        
        # 數據更新定時器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        
    def start_test(self):
        """開始測試"""
        self.start_btn.setText("Testing...")
        self.start_btn.setEnabled(False)
        
        # 啟動定時器，每秒更新一次數據
        self.timer.start(1000)
        
    def update_data(self):
        """更新模擬數據"""
        self.data_count += 1
        
        # 生成模擬 CPU 數據
        cpu_value = 50 + 30 * (time.time() % 10 / 10)  # 在 20-80 之間波動
        
        # 添加到圖表
        self.chart.add_data_point(cpu_value)
        
        # 更新信息
        self.info_label.setText(f"Update #{self.data_count}: CPU = {cpu_value:.1f}% (Should see continuous line)")
        
        # 運行30次後停止
        if self.data_count >= 30:
            self.timer.stop()
            self.start_btn.setText("Test Complete")
            self.info_label.setText(f"Test complete - Added 30 data points. Chart should show full line.")
            
    def closeEvent(self, event):
        """關閉事件"""
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    window = SilentChartTest()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())