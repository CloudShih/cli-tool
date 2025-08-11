"""
過濾面板組件
提供 dust 分析結果的過濾和搜尋功能
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QCheckBox, QGroupBox, QButtonGroup, QRadioButton, QSlider,
    QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from ui.components.inputs import ModernLineEdit, ModernComboBox
from ui.components.buttons import ModernButton

logger = logging.getLogger(__name__)


class FilterPanel(QWidget):
    """過濾面板主組件"""
    
    # 過濾條件變更信號
    filter_changed = pyqtSignal(dict)  # 發送過濾條件字典
    filter_applied = pyqtSignal()      # 過濾應用信號
    filter_cleared = pyqtSignal()      # 過濾清除信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_conditions = {}  # 存儲當前過濾條件
        self.original_data = []       # 原始數據
        self.filtered_data = []       # 過濾後數據
        self.update_timer = QTimer()  # 延遲更新計時器
        
        self.setup_ui()
        self._connect_signals()
        self._setup_update_timer()
    
    def setup_ui(self):
        """設置用戶界面"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(12)
        
        # 標題
        title_label = QLabel("過濾選項")
        title_label.setProperty("section-title", True)
        main_layout.addWidget(title_label)
        
        # 搜尋過濾器
        search_group = self._create_search_group()
        main_layout.addWidget(search_group)
        
        # 大小過濾器
        size_group = self._create_size_group()
        main_layout.addWidget(size_group)
        
        # 類型過濾器
        type_group = self._create_type_group()
        main_layout.addWidget(type_group)
        
        # 排序選項
        sort_group = self._create_sort_group()
        main_layout.addWidget(sort_group)
        
        # 操作按鈕
        buttons_layout = self._create_buttons_layout()
        main_layout.addLayout(buttons_layout)
        
        # 狀態信息
        self.status_label = QLabel("準備進行過濾...")
        self.status_label.setProperty("status-text", True)
        main_layout.addWidget(self.status_label)
        
        # 添加伸縮空間
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _create_search_group(self) -> QGroupBox:
        """創建搜尋過濾組"""
        group = QGroupBox("文字搜尋")
        layout = QVBoxLayout()
        
        # 路徑搜尋
        self.path_search_input = ModernLineEdit(placeholder="搜尋路徑...")
        self.path_search_input.setToolTip("輸入關鍵字以搜尋檔案或目錄路徑")
        layout.addWidget(QLabel("路徑關鍵字:"))
        layout.addWidget(self.path_search_input)
        
        # 搜尋選項
        search_options_layout = QHBoxLayout()
        
        self.case_sensitive_checkbox = QCheckBox("區分大小寫")
        search_options_layout.addWidget(self.case_sensitive_checkbox)
        
        self.regex_checkbox = QCheckBox("使用正則表達式")
        search_options_layout.addWidget(self.regex_checkbox)
        
        search_options_layout.addStretch()
        layout.addLayout(search_options_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_size_group(self) -> QGroupBox:
        """創建大小過濾組"""
        group = QGroupBox("大小過濾")
        layout = QGridLayout()
        
        # 最小大小
        layout.addWidget(QLabel("最小大小:"), 0, 0)
        self.min_size_input = ModernLineEdit(placeholder="例如: 1M")
        self.min_size_input.setToolTip("設置最小檔案大小，例如 '1M', '500K'")
        layout.addWidget(self.min_size_input, 0, 1)
        
        # 最大大小
        layout.addWidget(QLabel("最大大小:"), 1, 0)
        self.max_size_input = ModernLineEdit(placeholder="例如: 100M")
        self.max_size_input.setToolTip("設置最大檔案大小，例如 '100M', '1G'")
        layout.addWidget(self.max_size_input, 1, 1)
        
        # 大小單位選擇
        layout.addWidget(QLabel("預設單位:"), 2, 0)
        self.size_unit_combo = ModernComboBox(items=["自動", "B", "K", "M", "G", "T"])
        layout.addWidget(self.size_unit_combo, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def _create_type_group(self) -> QGroupBox:
        """創建類型過濾組"""
        group = QGroupBox("檔案類型")
        layout = QVBoxLayout()
        
        # 類型過濾方式
        filter_mode_layout = QHBoxLayout()
        
        self.type_button_group = QButtonGroup()
        
        self.show_all_radio = QRadioButton("顯示全部")
        self.show_all_radio.setChecked(True)
        self.type_button_group.addButton(self.show_all_radio, 0)
        filter_mode_layout.addWidget(self.show_all_radio)
        
        self.files_only_radio = QRadioButton("僅檔案")
        self.type_button_group.addButton(self.files_only_radio, 1)
        filter_mode_layout.addWidget(self.files_only_radio)
        
        self.dirs_only_radio = QRadioButton("僅目錄")
        self.type_button_group.addButton(self.dirs_only_radio, 2)
        filter_mode_layout.addWidget(self.dirs_only_radio)
        
        filter_mode_layout.addStretch()
        layout.addLayout(filter_mode_layout)
        
        # 檔案副檔名過濾
        layout.addWidget(QLabel("包含副檔名:"))
        self.include_extensions_input = ModernLineEdit(placeholder="例如: txt,py,js")
        self.include_extensions_input.setToolTip("指定要包含的副檔名，用逗號分隔")
        layout.addWidget(self.include_extensions_input)
        
        layout.addWidget(QLabel("排除副檔名:"))
        self.exclude_extensions_input = ModernLineEdit(placeholder="例如: tmp,log")
        self.exclude_extensions_input.setToolTip("指定要排除的副檔名，用逗號分隔")
        layout.addWidget(self.exclude_extensions_input)
        
        group.setLayout(layout)
        return group
    
    def _create_sort_group(self) -> QGroupBox:
        """創建排序選項組"""
        group = QGroupBox("排序選項")
        layout = QGridLayout()
        
        # 排序欄位
        layout.addWidget(QLabel("排序依據:"), 0, 0)
        self.sort_by_combo = ModernComboBox(items=[
            "大小 (預設)",
            "名稱",
            "路徑",
            "檔案類型"
        ])
        layout.addWidget(self.sort_by_combo, 0, 1)
        
        # 排序方向
        layout.addWidget(QLabel("排序方向:"), 1, 0)
        self.sort_order_combo = ModernComboBox(items=[
            "降序 (大到小)",
            "升序 (小到大)"
        ])
        layout.addWidget(self.sort_order_combo, 1, 1)
        
        # 結果限制
        layout.addWidget(QLabel("顯示數量:"), 2, 0)
        self.result_limit_spinbox = QSpinBox()
        self.result_limit_spinbox.setMinimum(1)
        self.result_limit_spinbox.setMaximum(1000)
        self.result_limit_spinbox.setValue(50)
        self.result_limit_spinbox.setSuffix(" 項")
        layout.addWidget(self.result_limit_spinbox, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def _create_buttons_layout(self) -> QHBoxLayout:
        """創建操作按鈕布局"""
        layout = QHBoxLayout()
        
        self.apply_filter_button = ModernButton("套用過濾")
        self.apply_filter_button.setProperty("primary", True)
        layout.addWidget(self.apply_filter_button)
        
        self.clear_filter_button = ModernButton("清除過濾")
        layout.addWidget(self.clear_filter_button)
        
        layout.addStretch()
        
        self.auto_update_checkbox = QCheckBox("自動更新")
        self.auto_update_checkbox.setChecked(True)
        self.auto_update_checkbox.setToolTip("勾選後，過濾條件變更時自動套用")
        layout.addWidget(self.auto_update_checkbox)
        
        return layout
    
    def _connect_signals(self):
        """連接信號槽"""
        # 文字輸入框變更
        self.path_search_input.textChanged.connect(self._on_filter_changed)
        self.min_size_input.textChanged.connect(self._on_filter_changed)
        self.max_size_input.textChanged.connect(self._on_filter_changed)
        self.include_extensions_input.textChanged.connect(self._on_filter_changed)
        self.exclude_extensions_input.textChanged.connect(self._on_filter_changed)
        
        # 核取框變更
        self.case_sensitive_checkbox.toggled.connect(self._on_filter_changed)
        self.regex_checkbox.toggled.connect(self._on_filter_changed)
        
        # 單選按鈕變更
        self.type_button_group.buttonToggled.connect(self._on_filter_changed)
        
        # 下拉選單變更
        self.size_unit_combo.currentTextChanged.connect(self._on_filter_changed)
        self.sort_by_combo.currentTextChanged.connect(self._on_filter_changed)
        self.sort_order_combo.currentTextChanged.connect(self._on_filter_changed)
        
        # 數值變更
        self.result_limit_spinbox.valueChanged.connect(self._on_filter_changed)
        
        # 按鈕點擊
        self.apply_filter_button.clicked.connect(self._apply_filter)
        self.clear_filter_button.clicked.connect(self._clear_filter)
    
    def _setup_update_timer(self):
        """設置延遲更新計時器"""
        self.update_timer.timeout.connect(self._emit_filter_changed)
        self.update_timer.setSingleShot(True)
    
    def _on_filter_changed(self):
        """處理過濾條件變更"""
        if self.auto_update_checkbox.isChecked():
            # 延遲更新，避免頻繁觸發
            self.update_timer.start(300)  # 300ms 延遲
        
        # 更新狀態
        self.status_label.setText("過濾條件已變更...")
    
    def _emit_filter_changed(self):
        """發送過濾條件變更信號"""
        self.filter_conditions = self._get_current_filter_conditions()
        self.filter_changed.emit(self.filter_conditions)
        
        # 更新狀態
        active_filters = self._count_active_filters()
        if active_filters > 0:
            self.status_label.setText(f"已套用 {active_filters} 個過濾條件")
        else:
            self.status_label.setText("未套用過濾條件")
    
    def _get_current_filter_conditions(self) -> Dict[str, Any]:
        """獲取當前過濾條件"""
        conditions = {}
        
        # 文字搜尋
        path_search = self.path_search_input.text().strip()
        if path_search:
            conditions['path_search'] = {
                'text': path_search,
                'case_sensitive': self.case_sensitive_checkbox.isChecked(),
                'regex': self.regex_checkbox.isChecked()
            }
        
        # 大小過濾
        min_size = self.min_size_input.text().strip()
        max_size = self.max_size_input.text().strip()
        if min_size or max_size:
            conditions['size_filter'] = {
                'min_size': min_size,
                'max_size': max_size,
                'unit': self.size_unit_combo.currentText()
            }
        
        # 類型過濾
        type_filter_id = self.type_button_group.checkedId()
        if type_filter_id != 0:  # 非 "顯示全部"
            conditions['type_filter'] = {
                'mode': type_filter_id,  # 1=僅檔案, 2=僅目錄
                'include_extensions': self._parse_extensions(self.include_extensions_input.text()),
                'exclude_extensions': self._parse_extensions(self.exclude_extensions_input.text())
            }
        
        # 排序選項
        conditions['sort_options'] = {
            'sort_by': self.sort_by_combo.currentIndex(),
            'sort_order': self.sort_order_combo.currentIndex(),
            'limit': self.result_limit_spinbox.value()
        }
        
        return conditions
    
    def _parse_extensions(self, text: str) -> List[str]:
        """解析副檔名字符串"""
        if not text.strip():
            return []
        
        extensions = []
        for ext in text.split(','):
            ext = ext.strip().lower()
            if ext:
                if not ext.startswith('.'):
                    ext = '.' + ext
                extensions.append(ext)
        
        return extensions
    
    def _count_active_filters(self) -> int:
        """計算活躍的過濾條件數量"""
        count = 0
        
        if 'path_search' in self.filter_conditions:
            count += 1
        
        if 'size_filter' in self.filter_conditions:
            count += 1
        
        if 'type_filter' in self.filter_conditions:
            count += 1
        
        return count
    
    def _apply_filter(self):
        """手動套用過濾"""
        self._emit_filter_changed()
        self.filter_applied.emit()
        logger.debug("Filter applied manually")
    
    def _clear_filter(self):
        """清除所有過濾條件"""
        # 重置所有控件
        self.path_search_input.clear()
        self.min_size_input.clear()
        self.max_size_input.clear()
        self.include_extensions_input.clear()
        self.exclude_extensions_input.clear()
        
        self.case_sensitive_checkbox.setChecked(False)
        self.regex_checkbox.setChecked(False)
        
        self.show_all_radio.setChecked(True)
        
        self.size_unit_combo.setCurrentIndex(0)
        self.sort_by_combo.setCurrentIndex(0)
        self.sort_order_combo.setCurrentIndex(0)
        self.result_limit_spinbox.setValue(50)
        
        # 清除條件並發送信號
        self.filter_conditions.clear()
        self.filter_cleared.emit()
        
        self.status_label.setText("已清除所有過濾條件")
        logger.debug("All filters cleared")
    
    def apply_filter_to_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        將當前過濾條件套用到數據
        
        Args:
            data: 原始數據列表
            
        Returns:
            過濾後的數據列表
        """
        if not self.filter_conditions:
            return data[:self.result_limit_spinbox.value()]
        
        try:
            filtered = data.copy()
            
            # 套用路徑搜尋過濾
            if 'path_search' in self.filter_conditions:
                filtered = self._apply_path_search(filtered, self.filter_conditions['path_search'])
            
            # 套用大小過濾
            if 'size_filter' in self.filter_conditions:
                filtered = self._apply_size_filter(filtered, self.filter_conditions['size_filter'])
            
            # 套用類型過濾
            if 'type_filter' in self.filter_conditions:
                filtered = self._apply_type_filter(filtered, self.filter_conditions['type_filter'])
            
            # 套用排序
            sort_options = self.filter_conditions.get('sort_options', {})
            filtered = self._apply_sorting(filtered, sort_options)
            
            # 套用數量限制
            limit = sort_options.get('limit', 50)
            filtered = filtered[:limit]
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return data[:50]  # 返回原始數據的前50項作為回退
    
    def _apply_path_search(self, data: List[Dict[str, Any]], search_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """套用路徑搜尋過濾"""
        search_text = search_config['text']
        case_sensitive = search_config['case_sensitive']
        use_regex = search_config['regex']
        
        if not search_text:
            return data
        
        filtered = []
        
        if use_regex:
            import re
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_text, flags)
                
                for item in data:
                    path = item.get('path', '')
                    if pattern.search(path):
                        filtered.append(item)
            except re.error as e:
                logger.warning(f"Invalid regex pattern: {e}")
                return data  # 返回原始數據
        else:
            search_text = search_text if case_sensitive else search_text.lower()
            
            for item in data:
                path = item.get('path', '')
                path = path if case_sensitive else path.lower()
                
                if search_text in path:
                    filtered.append(item)
        
        return filtered
    
    def _apply_size_filter(self, data: List[Dict[str, Any]], size_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """套用大小過濾"""
        # 這裡需要實現大小比較邏輯
        # 由於需要解析大小字符串，這是一個簡化版本
        return data  # TODO: 實現具體的大小過濾邏輯
    
    def _apply_type_filter(self, data: List[Dict[str, Any]], type_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """套用類型過濾"""
        # 這裡需要實現類型過濾邏輯
        return data  # TODO: 實現具體的類型過濾邏輯
    
    def _apply_sorting(self, data: List[Dict[str, Any]], sort_options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """套用排序"""
        sort_by = sort_options.get('sort_by', 0)
        sort_order = sort_options.get('sort_order', 0)
        
        # 簡化的排序實現
        if sort_by == 0:  # 按大小排序
            reverse = (sort_order == 0)  # 0=降序, 1=升序
            return sorted(data, key=lambda x: x.get('size_bytes', 0), reverse=reverse)
        elif sort_by == 1:  # 按名稱排序
            reverse = (sort_order == 1)
            return sorted(data, key=lambda x: x.get('path', ''), reverse=reverse)
        
        return data
    
    def get_filter_summary(self) -> str:
        """獲取過濾條件摘要"""
        if not self.filter_conditions:
            return "無過濾條件"
        
        summary_parts = []
        
        if 'path_search' in self.filter_conditions:
            search_text = self.filter_conditions['path_search']['text']
            summary_parts.append(f"路徑: '{search_text}'")
        
        if 'size_filter' in self.filter_conditions:
            size_filter = self.filter_conditions['size_filter']
            if size_filter['min_size']:
                summary_parts.append(f"最小: {size_filter['min_size']}")
            if size_filter['max_size']:
                summary_parts.append(f"最大: {size_filter['max_size']}")
        
        if 'type_filter' in self.filter_conditions:
            type_filter = self.filter_conditions['type_filter']
            mode_names = {1: "僅檔案", 2: "僅目錄"}
            mode_name = mode_names.get(type_filter['mode'], "未知")
            summary_parts.append(f"類型: {mode_name}")
        
        return " | ".join(summary_parts) if summary_parts else "無過濾條件"