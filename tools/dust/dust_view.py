"""
dust 插件的現代化視圖層
提供磁碟空間分析的用戶界面
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QSizePolicy, QGroupBox, QSpinBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from ui.components.buttons import ModernButton, PrimaryButton, DirectoryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox, ModernTextEdit
from ui.components.indicators import StatusIndicator, LoadingSpinner
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class DustView(QWidget):
    """dust 工具的現代化視圖界面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_default_settings()
    
    def setup_ui(self):
        """設置現代化用戶界面"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題和狀態區域
        header_layout = QHBoxLayout()
        
        title_label = QLabel("磁碟空間分析工具 (dust)")
        title_label.setProperty("heading", True)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 狀態指示器
        self.status_indicator = StatusIndicator("ready")
        header_layout.addWidget(self.status_indicator)
        
        main_layout.addLayout(header_layout)
        
        # 分析參數群組
        analysis_group = QGroupBox("分析參數")
        analysis_layout = QGridLayout()
        analysis_layout.setSpacing(12)
        
        row = 0
        
        # 目標路徑
        analysis_layout.addWidget(QLabel("分析路徑:"), row, 0)
        
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        
        self.dust_path_input = ModernLineEdit(placeholder="選擇要分析的目錄路徑")
        self.dust_path_input.setToolTip("選擇要進行磁碟空間分析的目錄路徑，預設為當前目錄。")
        path_layout.addWidget(self.dust_path_input, 1)
        
        self.dust_browse_button = DirectoryButton(text="瀏覽...")
        self.dust_browse_button.directory_selected.connect(self.dust_path_input.setText)
        path_layout.addWidget(self.dust_browse_button)
        
        analysis_layout.addLayout(path_layout, row, 1, 1, 2)
        row += 1
        
        # 最大深度
        analysis_layout.addWidget(QLabel("最大深度:"), row, 0)
        self.dust_max_depth_spinbox = QSpinBox()
        self.dust_max_depth_spinbox.setMinimum(1)
        self.dust_max_depth_spinbox.setMaximum(20)
        self.dust_max_depth_spinbox.setValue(3)
        self.dust_max_depth_spinbox.setToolTip("設置目錄遞歸的最大深度。")
        analysis_layout.addWidget(self.dust_max_depth_spinbox, row, 1)
        row += 1
        
        # 顯示行數
        analysis_layout.addWidget(QLabel("顯示行數:"), row, 0)
        self.dust_lines_spinbox = QSpinBox()
        self.dust_lines_spinbox.setMinimum(10)
        self.dust_lines_spinbox.setMaximum(1000)
        self.dust_lines_spinbox.setValue(50)
        self.dust_lines_spinbox.setToolTip("限制顯示的結果行數。")
        analysis_layout.addWidget(self.dust_lines_spinbox, row, 1)
        row += 1
        
        # 最小檔案大小
        analysis_layout.addWidget(QLabel("最小大小:"), row, 0)
        self.dust_min_size_input = ModernLineEdit(placeholder="例如: 1M, 100K")
        self.dust_min_size_input.setToolTip("設置最小檔案大小過濾條件，例如 '1M' 或 '100K'。")
        analysis_layout.addWidget(self.dust_min_size_input, row, 1, 1, 2)
        row += 1
        
        analysis_group.setLayout(analysis_layout)
        main_layout.addWidget(analysis_group)
        
        # 顯示選項群組
        options_group = QGroupBox("顯示選項")
        options_layout = QHBoxLayout()
        
        self.dust_reverse_sort_checkbox = QCheckBox("反向排序 (大到小)")
        self.dust_reverse_sort_checkbox.setToolTip("勾選以按檔案大小從大到小排序。")
        self.dust_reverse_sort_checkbox.setChecked(True)
        options_layout.addWidget(self.dust_reverse_sort_checkbox)
        
        self.dust_apparent_size_checkbox = QCheckBox("顯示表面大小")
        self.dust_apparent_size_checkbox.setToolTip("勾選以顯示檔案的表面大小而非實際佔用空間。")
        options_layout.addWidget(self.dust_apparent_size_checkbox)
        
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # 過濾選項群組
        filter_group = QGroupBox("過濾選項")
        filter_layout = QGridLayout()
        filter_layout.setSpacing(12)
        
        # 檔案類型過濾
        filter_layout.addWidget(QLabel("包含類型:"), 0, 0)
        self.dust_include_types_input = ModernLineEdit(placeholder="例如: txt,pdf,jpg")
        self.dust_include_types_input.setToolTip("指定要包含的檔案類型，用逗號分隔。")
        filter_layout.addWidget(self.dust_include_types_input, 0, 1)
        
        # 排除模式
        filter_layout.addWidget(QLabel("排除模式:"), 1, 0)
        self.dust_exclude_patterns_input = ModernLineEdit(placeholder="例如: *.tmp,node_modules")
        self.dust_exclude_patterns_input.setToolTip("指定要排除的檔案或目錄模式，用逗號分隔。")
        filter_layout.addWidget(self.dust_exclude_patterns_input, 1, 1)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # 額外選項群組
        extra_group = QGroupBox("額外選項")
        extra_layout = QHBoxLayout()
        
        self.dust_full_paths_checkbox = QCheckBox("顯示完整路徑")
        self.dust_full_paths_checkbox.setToolTip("勾選以顯示檔案和目錄的完整路徑。")
        extra_layout.addWidget(self.dust_full_paths_checkbox)
        
        self.dust_files_only_checkbox = QCheckBox("僅顯示檔案")
        self.dust_files_only_checkbox.setToolTip("勾選以僅顯示檔案，不包含目錄。")
        extra_layout.addWidget(self.dust_files_only_checkbox)
        
        extra_layout.addStretch()
        extra_group.setLayout(extra_layout)
        main_layout.addWidget(extra_group)
        
        # 操作按鈕區域
        button_layout = QHBoxLayout()
        
        self.dust_analyze_button = PrimaryButton("開始分析")
        self.dust_analyze_button.setMinimumHeight(40)
        button_layout.addWidget(self.dust_analyze_button)
        
        clear_button = ModernButton("清除結果")
        clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        # 載入指示器
        self.loading_spinner = LoadingSpinner(24)
        button_layout.addWidget(self.loading_spinner)
        
        main_layout.addLayout(button_layout)
        
        # 結果顯示區域
        results_group = QGroupBox("分析結果")
        results_layout = QVBoxLayout()
        
        self.dust_results_display = ModernTextEdit(placeholder="磁碟空間分析結果將顯示在這裡...")
        self.dust_results_display.set_read_only_style(True)
        self.dust_results_display.setMinimumHeight(350)
        results_layout.addWidget(self.dust_results_display)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)  # 結果區域可擴展
        
        self.setLayout(main_layout)
    
    def load_default_settings(self):
        """載入預設設定"""
        try:
            # 載入預設最大深度
            default_max_depth = config_manager.get('tools.dust.default_max_depth', 3)
            self.dust_max_depth_spinbox.setValue(default_max_depth)
            
            # 載入預設顯示行數
            default_lines = config_manager.get('tools.dust.default_number_of_lines', 50)
            self.dust_lines_spinbox.setValue(default_lines)
            
            # 載入預設排序選項
            default_reverse_sort = config_manager.get('tools.dust.default_sort_reverse', True)
            self.dust_reverse_sort_checkbox.setChecked(default_reverse_sort)
            
            # 載入預設表面大小選項
            default_apparent_size = config_manager.get('tools.dust.default_show_apparent_size', False)
            self.dust_apparent_size_checkbox.setChecked(default_apparent_size)
            
            # 載入預設最小大小
            default_min_size = config_manager.get('tools.dust.default_min_size', '')
            self.dust_min_size_input.setText(default_min_size)
            
            # 載入預設路徑
            default_path = config_manager.get('tools.dust.default_path', '')
            self.dust_path_input.setText(default_path)
            
            logger.info(f"Loaded default dust settings: max_depth={default_max_depth}, "
                       f"lines={default_lines}, reverse_sort={default_reverse_sort}, "
                       f"apparent_size={default_apparent_size}")
            
        except Exception as e:
            logger.error(f"Error loading default dust settings: {e}")
            # 使用硬編碼預設值作為回退
            self.dust_max_depth_spinbox.setValue(3)
            self.dust_lines_spinbox.setValue(50)
            self.dust_reverse_sort_checkbox.setChecked(True)
            self.dust_apparent_size_checkbox.setChecked(False)
    
    def set_analyze_button_state(self, text, enabled, background_color=None, text_color=None):
        """設置分析按鈕狀態"""
        self.dust_analyze_button.setText(text)
        self.dust_analyze_button.setEnabled(enabled)
        
        # 更新狀態指示器
        if enabled:
            if "分析" in text:
                self.status_indicator.set_status("ready", "準備分析")
                self.loading_spinner.stop_spinning()
            else:
                self.status_indicator.set_status("processing", "分析中...")
                self.loading_spinner.start_spinning()
        else:
            self.status_indicator.set_status("processing", "處理中...")
            self.loading_spinner.start_spinning()
    
    def clear_results(self):
        """清除分析結果"""
        self.dust_results_display.clear()
        self.status_indicator.set_status("ready", "準備分析")
        self.loading_spinner.stop_spinning()
    
    def set_analysis_completed(self, success=True, message=""):
        """設置分析完成狀態"""
        if success:
            self.status_indicator.set_status("success", message or "分析完成")
        else:
            self.status_indicator.set_status("error", message or "分析失敗")
        
        self.loading_spinner.stop_spinning()
        self.dust_analyze_button.setText("開始分析")
        self.dust_analyze_button.setEnabled(True)
    
    def get_analysis_parameters(self):
        """獲取當前的分析參數"""
        # 處理檔案類型和排除模式
        include_types = []
        if self.dust_include_types_input.text().strip():
            include_types = [t.strip() for t in self.dust_include_types_input.text().split(',') if t.strip()]
        
        exclude_patterns = []
        if self.dust_exclude_patterns_input.text().strip():
            exclude_patterns = [p.strip() for p in self.dust_exclude_patterns_input.text().split(',') if p.strip()]
        
        return {
            'target_path': self.dust_path_input.text().strip() or '.',
            'max_depth': self.dust_max_depth_spinbox.value(),
            'sort_reverse': self.dust_reverse_sort_checkbox.isChecked(),
            'number_of_lines': self.dust_lines_spinbox.value(),
            'file_types': include_types if include_types else None,
            'exclude_patterns': exclude_patterns if exclude_patterns else None,
            'show_apparent_size': self.dust_apparent_size_checkbox.isChecked(),
            'min_size': self.dust_min_size_input.text().strip() or None,
            'full_paths': self.dust_full_paths_checkbox.isChecked(),
            'files_only': self.dust_files_only_checkbox.isChecked()
        }