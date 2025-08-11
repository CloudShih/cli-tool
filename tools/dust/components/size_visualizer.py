"""
大小視覺化組件
提供磁碟使用量的圖形化顯示功能
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QSizePolicy, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QPaintEvent, QPixmap

logger = logging.getLogger(__name__)


class SizeBar(QWidget):
    """自定義大小條組件"""
    
    clicked = pyqtSignal(str)  # 點擊時發出路徑信號
    
    def __init__(self, path: str, size_text: str, size_bytes: int, max_size_bytes: int, parent=None):
        super().__init__(parent)
        self.path = path
        self.size_text = size_text
        self.size_bytes = size_bytes
        self.max_size_bytes = max_size_bytes
        self.percentage = (size_bytes / max_size_bytes * 100) if max_size_bytes > 0 else 0
        
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.setCursor(Qt.PointingHandCursor)
        
        # 顏色根據大小百分比決定
        self.bar_color = self._get_color_for_percentage(self.percentage)
    
    def _get_color_for_percentage(self, percentage: float) -> QColor:
        """根據百分比獲取顏色"""
        if percentage >= 80:
            return QColor(231, 76, 60)    # 紅色 - 大檔案
        elif percentage >= 60:
            return QColor(230, 126, 34)   # 橙色 - 中大檔案
        elif percentage >= 40:
            return QColor(241, 196, 15)   # 黃色 - 中檔案
        elif percentage >= 20:
            return QColor(46, 204, 113)   # 綠色 - 小檔案
        else:
            return QColor(52, 152, 219)   # 藍色 - 很小檔案
    
    def paintEvent(self, event: QPaintEvent):
        """自定義繪製事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        bg_color = QColor(245, 245, 245)
        painter.fillRect(self.rect(), bg_color)
        
        # 計算條形寬度
        bar_width = int(self.width() * self.percentage / 100)
        
        # 繪製大小條
        if bar_width > 0:
            bar_rect = self.rect()
            bar_rect.setWidth(bar_width)
            painter.fillRect(bar_rect, self.bar_color)
        
        # 繪製文字
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        
        # 檔案名稱（左側）
        text_rect = self.rect().adjusted(8, 0, -8, 0)
        file_name = self.path.split('/')[-1] if '/' in self.path else self.path
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, file_name)
        
        # 大小文字（右側）
        size_with_percent = f"{self.size_text} ({self.percentage:.1f}%)"
        painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, size_with_percent)
    
    def mousePressEvent(self, event):
        """處理滑鼠點擊事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.path)


class SizeVisualizerComponent(QWidget):
    """大小視覺化組件主類"""
    
    # 組件信號
    item_selected = pyqtSignal(str, str)  # path, size_text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_bars = []  # 存儲大小條列表
        self.data = []  # 存儲原始數據
        self.max_items = 20  # 最大顯示項目數
        self.setup_ui()
    
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 標題和控制區域
        header_layout = QHBoxLayout()
        
        title_label = QLabel("大小視覺化")
        title_label.setProperty("section-title", True)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 顯示項目數標籤
        self.items_label = QLabel(f"顯示前 {self.max_items} 項")
        self.items_label.setProperty("info-text", True)
        header_layout.addWidget(self.items_label)
        
        layout.addLayout(header_layout)
        
        # 滾動區域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setMinimumHeight(250)
        
        # 滾動內容容器
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        # 統計信息
        self.stats_label = QLabel("準備顯示大小視覺化...")
        self.stats_label.setProperty("status-text", True)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def populate_visualizer(self, dust_results: List[Dict[str, Any]]):
        """
        根據 dust 分析結果填充視覺化器
        
        Args:
            dust_results: dust 命令解析後的結果列表
        """
        try:
            # 清除現有內容
            self.clear_visualizer()
            
            if not dust_results:
                self.stats_label.setText("沒有數據可視覺化")
                return
            
            # 處理和排序數據
            processed_data = self._process_dust_data(dust_results)
            
            if not processed_data:
                self.stats_label.setText("無法處理數據進行視覺化")
                return
            
            # 限制顯示項目數
            display_data = processed_data[:self.max_items]
            max_size = processed_data[0]['size_bytes'] if processed_data else 1
            
            # 創建大小條
            for item in display_data:
                size_bar = SizeBar(
                    item['path'],
                    item['size_text'],
                    item['size_bytes'],
                    max_size
                )
                
                # 連接信號
                size_bar.clicked.connect(self._on_item_clicked)
                
                # 添加到布局
                self.scroll_layout.addWidget(size_bar)
                self.size_bars.append(size_bar)
            
            # 添加伸縮空間
            self.scroll_layout.addStretch()
            
            # 更新統計信息
            total_items = len(processed_data)
            displayed_items = len(display_data)
            total_size = self._calculate_total_size(processed_data)
            
            self.stats_label.setText(
                f"顯示 {displayed_items} / {total_items} 項，總大小: {total_size}"
            )
            self.items_label.setText(f"顯示前 {displayed_items} 項")
            
            self.data = processed_data
            logger.info(f"Visualizer populated with {displayed_items} items")
            
        except Exception as e:
            logger.error(f"Error populating visualizer: {e}")
            self.stats_label.setText(f"視覺化載入錯誤: {str(e)}")
    
    def _process_dust_data(self, dust_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理 dust 原始數據
        
        Args:
            dust_results: 原始 dust 結果
            
        Returns:
            處理後的數據列表，包含 size_bytes 欄位
        """
        processed = []
        
        for result in dust_results:
            try:
                path = result.get('path', '')
                size_text = result.get('size', '')
                
                if not path or not size_text:
                    continue
                
                # 解析大小為位元組數
                size_bytes = self._parse_size_to_bytes(size_text)
                
                if size_bytes > 0:
                    processed.append({
                        'path': path,
                        'size_text': size_text,
                        'size_bytes': size_bytes
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing item {result}: {e}")
                continue
        
        # 按大小排序（大到小）
        processed.sort(key=lambda x: x['size_bytes'], reverse=True)
        
        return processed
    
    def _parse_size_to_bytes(self, size_text: str) -> int:
        """
        將大小字符串解析為位元組數
        
        Args:
            size_text: 大小文字，如 "1.5M", "500K", "2.3G"
            
        Returns:
            位元組數
        """
        try:
            import re
            
            # 移除空格並轉為大寫
            size_text = size_text.strip().upper()
            
            # 使用正則表達式解析
            match = re.match(r'^([\d.]+)([KMGT]?)B?$', size_text)
            
            if not match:
                return 0
            
            number_str, unit = match.groups()
            number = float(number_str)
            
            # 單位轉換
            multipliers = {
                '': 1,           # 位元組
                'K': 1024,       # KB
                'M': 1024**2,    # MB
                'G': 1024**3,    # GB
                'T': 1024**4,    # TB
            }
            
            multiplier = multipliers.get(unit, 1)
            return int(number * multiplier)
            
        except Exception as e:
            logger.warning(f"Error parsing size '{size_text}': {e}")
            return 0
    
    def _calculate_total_size(self, data: List[Dict[str, Any]]) -> str:
        """計算總大小並格式化"""
        try:
            total_bytes = sum(item['size_bytes'] for item in data)
            return self._format_bytes(total_bytes)
        except Exception:
            return "未知"
    
    def _format_bytes(self, bytes_count: int) -> str:
        """格式化位元組數為可讀字符串"""
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024**2:
            return f"{bytes_count / 1024:.1f} K"
        elif bytes_count < 1024**3:
            return f"{bytes_count / (1024**2):.1f} M"
        elif bytes_count < 1024**4:
            return f"{bytes_count / (1024**3):.1f} G"
        else:
            return f"{bytes_count / (1024**4):.1f} T"
    
    def _on_item_clicked(self, path: str):
        """處理項目點擊事件"""
        # 查找對應的項目數據
        for item in self.data:
            if item['path'] == path:
                self.item_selected.emit(path, item['size_text'])
                break
        
        logger.debug(f"Size visualizer item clicked: {path}")
    
    def clear_visualizer(self):
        """清空視覺化器"""
        # 移除所有大小條
        for bar in self.size_bars:
            bar.setParent(None)
            bar.deleteLater()
        
        self.size_bars.clear()
        self.data.clear()
        
        self.stats_label.setText("視覺化器已清空")
        self.items_label.setText(f"顯示前 {self.max_items} 項")
    
    def set_max_items(self, max_items: int):
        """設置最大顯示項目數"""
        if max_items > 0:
            self.max_items = max_items
            self.items_label.setText(f"顯示前 {self.max_items} 項")
            
            # 如果有數據，重新填充
            if self.data:
                self.populate_visualizer([
                    {'path': item['path'], 'size': item['size_text']}
                    for item in self.data
                ])
    
    def refresh_colors(self):
        """刷新顏色（用於主題變更時）"""
        for bar in self.size_bars:
            bar.update()  # 觸發重繪