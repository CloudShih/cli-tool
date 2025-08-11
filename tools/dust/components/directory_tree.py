"""
目錄樹組件
提供視覺化的目錄結構顯示功能
"""

import logging
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)


class DirectoryTreeWidget(QTreeWidget):
    """自定義目錄樹控件"""
    
    # 自定義信號
    item_selected = pyqtSignal(str, str)  # path, size
    item_expanded = pyqtSignal(str)  # path
    
    def __init__(self):
        super().__init__()
        self.setup_tree()
    
    def setup_tree(self):
        """設置樹狀控件"""
        # 設置表頭
        self.setHeaderLabels(["目錄/檔案", "大小", "類型"])
        
        # 設置列寬
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 目錄名稱可伸縮
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 大小固定
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 類型固定
        
        # 設置樣式
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setExpandsOnDoubleClick(True)
        
        # 連接信號
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """處理項目點擊事件"""
        if item:
            path = item.data(0, Qt.UserRole) or item.text(0)
            size = item.text(1)
            self.item_selected.emit(path, size)
    
    def _on_item_expanded(self, item: QTreeWidgetItem):
        """處理項目展開事件"""
        if item:
            path = item.data(0, Qt.UserRole) or item.text(0)
            self.item_expanded.emit(path)


class DirectoryTreeComponent(QWidget):
    """目錄樹組件主類"""
    
    # 組件信號
    directory_selected = pyqtSignal(str)  # 選中的目錄路徑
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_data = {}  # 存儲樹狀結構資料
        self.setup_ui()
        self._connect_signals()
    
    def setup_ui(self):
        """設置用戶界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 標題
        title_label = QLabel("目錄結構")
        title_label.setProperty("section-title", True)
        layout.addWidget(title_label)
        
        # 目錄樹控件
        self.tree_widget = DirectoryTreeWidget()
        self.tree_widget.setMinimumHeight(200)
        layout.addWidget(self.tree_widget)
        
        # 狀態標籤
        self.status_label = QLabel("準備顯示目錄結構...")
        self.status_label.setProperty("status-text", True)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def _connect_signals(self):
        """連接信號槽"""
        self.tree_widget.item_selected.connect(self._on_directory_selected)
        self.tree_widget.item_expanded.connect(self._on_directory_expanded)
    
    def _on_directory_selected(self, path: str, size: str):
        """處理目錄選擇事件"""
        self.status_label.setText(f"選中: {path} ({size})")
        self.directory_selected.emit(path)
        logger.debug(f"Directory selected: {path}")
    
    def _on_directory_expanded(self, path: str):
        """處理目錄展開事件"""
        self.status_label.setText(f"展開: {path}")
        logger.debug(f"Directory expanded: {path}")
    
    def populate_tree(self, dust_results: List[Dict[str, Any]]):
        """
        根據 dust 分析結果填充目錄樹
        
        Args:
            dust_results: dust 命令解析後的結果列表
        """
        try:
            self.tree_widget.clear()
            
            if not dust_results:
                self.status_label.setText("沒有可顯示的目錄結構")
                return
            
            # 構建樹狀結構
            root_items = {}
            
            for result in dust_results:
                path = result.get('path', '')
                size = result.get('size', '')
                
                if not path:
                    continue
                
                # 分解路徑
                path_parts = self._split_path(path)
                
                # 創建或獲取樹節點
                current_parent = None
                current_path = ""
                
                for i, part in enumerate(path_parts):
                    current_path = self._join_path(current_path, part)
                    
                    if current_parent is None:
                        # 根節點
                        if part not in root_items:
                            item = QTreeWidgetItem(self.tree_widget)
                            item.setText(0, part)
                            item.setData(0, Qt.UserRole, current_path)
                            root_items[part] = item
                            
                            # 設置圖標（可以後續添加）
                            item.setText(2, "目錄" if i < len(path_parts) - 1 else self._get_file_type(part))
                        
                        current_parent = root_items[part]
                    else:
                        # 子節點
                        child_item = self._find_or_create_child(current_parent, part, current_path)
                        child_item.setText(2, "目錄" if i < len(path_parts) - 1 else self._get_file_type(part))
                        current_parent = child_item
                
                # 設置最終節點的大小
                if current_parent:
                    current_parent.setText(1, size)
            
            # 展開第一層
            self.tree_widget.expandToDepth(0)
            
            self.status_label.setText(f"已載入 {len(dust_results)} 個項目")
            logger.info(f"Tree populated with {len(dust_results)} items")
            
        except Exception as e:
            logger.error(f"Error populating tree: {e}")
            self.status_label.setText(f"載入目錄結構時發生錯誤: {str(e)}")
    
    def _split_path(self, path: str) -> List[str]:
        """分解路徑為組件列表"""
        import os
        # 處理不同操作系統的路徑分隔符
        parts = path.replace('\\', '/').split('/')
        return [part for part in parts if part]
    
    def _join_path(self, base: str, part: str) -> str:
        """連接路徑組件"""
        if not base:
            return part
        return f"{base}/{part}"
    
    def _find_or_create_child(self, parent: QTreeWidgetItem, name: str, full_path: str) -> QTreeWidgetItem:
        """查找或創建子節點"""
        # 檢查是否已存在
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(0) == name:
                return child
        
        # 創建新子節點
        child = QTreeWidgetItem(parent)
        child.setText(0, name)
        child.setData(0, Qt.UserRole, full_path)
        return child
    
    def _get_file_type(self, filename: str) -> str:
        """獲取檔案類型"""
        import os
        ext = os.path.splitext(filename)[1].lower()
        
        type_map = {
            '.txt': '文本檔案',
            '.py': 'Python檔案',
            '.js': 'JavaScript檔案',
            '.html': 'HTML檔案',
            '.css': 'CSS檔案',
            '.jpg': '圖像檔案',
            '.png': '圖像檔案',
            '.pdf': 'PDF檔案',
            '.zip': '壓縮檔案',
            '.exe': '執行檔案',
        }
        
        return type_map.get(ext, '檔案')
    
    def clear_tree(self):
        """清空目錄樹"""
        self.tree_widget.clear()
        self.tree_data.clear()
        self.status_label.setText("目錄樹已清空")
    
    def expand_all(self):
        """展開所有節點"""
        self.tree_widget.expandAll()
        self.status_label.setText("已展開所有目錄")
    
    def collapse_all(self):
        """收合所有節點"""
        self.tree_widget.collapseAll()
        self.status_label.setText("已收合所有目錄")