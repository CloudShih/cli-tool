"""
dust 插件的重新設計視圖層 - 優化佈局和結果顯示
提供更直觀的磁碟空間分析用戶界面
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QCheckBox, QSizePolicy, QGroupBox, QSpinBox,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QScrollArea, QFrame
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from ui.components.buttons import ModernButton, PrimaryButton, DirectoryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox, ModernTextEdit
from ui.components.indicators import StatusIndicator, LoadingSpinner
from config.config_manager import config_manager
import json
import re

logger = logging.getLogger(__name__)


class DustTreeWidget(QTreeWidget):
    """自定義的 dust 結果樹狀視圖"""
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["檔案/目錄", "大小", "類型"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        
        # 設定欄位寬度
        self.setColumnWidth(0, 300)  # 檔案名稱
        self.setColumnWidth(1, 100)  # 大小
        self.setColumnWidth(2, 80)   # 類型
        
        # 設定暗色主題樣式
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                alternate-background-color: #333333;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
                background-color: transparent;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: url(vline.png) 0;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: url(branch-more.png) 0;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: url(branch-end.png) 0;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(branch-closed.png);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(branch-open.png);
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #555555;
                font-weight: bold;
            }
        """)


class DustResultsWidget(QWidget):
    """分析結果顯示組件 - 支援樹狀和原始文本兩種檢視"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """設置結果顯示界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 建立標籤頁
        self.tab_widget = QTabWidget()
        
        # 設定標籤頁暗色樣式
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #555555;
                border-bottom-color: #555555;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                border-bottom-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # 樹狀檢視標籤頁
        self.tree_widget = DustTreeWidget()
        self.tab_widget.addTab(self.tree_widget, "📊 樹狀檢視")
        
        # 原始文本標籤頁
        self.text_widget = ModernTextEdit(placeholder="磁碟空間分析結果將顯示在這裡...")
        self.text_widget.set_read_only_style(True)
        self.tab_widget.addTab(self.text_widget, "📄 原始輸出")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def clear_results(self):
        """清除所有結果"""
        self.tree_widget.clear()
        self.text_widget.clear()
    
    def set_results(self, html_output: str, html_error: str):
        """設置分析結果"""
        # 設置原始文本
        if html_output:
            self.text_widget.setHtml(html_output)
        if html_error:
            self.text_widget.append(f"\n<div style='color: #ff6b6b;'><strong>錯誤信息:</strong><br>{html_error}</div>")
        
        # 解析並設置樹狀結果
        self._parse_and_set_tree_results(html_output)
    
    def _parse_and_set_tree_results(self, html_output: str):
        """解析 HTML 輸出並設置樹狀結果"""
        if not html_output:
            return
        
        self.tree_widget.clear()
        
        try:
            # 移除 HTML 標籤，獲取純文本
            import html
            text_output = html.unescape(html_output)
            text_output = re.sub(r'<[^>]*>', '', text_output)
            
            lines = text_output.strip().split('\n')
            parent_stack = []  # 存儲各層級的父項目
            
            for line in lines:
                if not line.strip():
                    continue
                
                parsed_item = self._parse_dust_line(line)
                if parsed_item:
                    tree_item = self._create_tree_item(parsed_item)
                    self._add_item_to_hierarchy(tree_item, parsed_item['indent_level'], parent_stack)
            
            # 展開第一層項目
            self.tree_widget.expandToDepth(1)
            
        except Exception as e:
            logger.error(f"Error parsing dust results for tree view: {e}")
            # 如果解析失敗，添加一個錯誤項目
            error_item = QTreeWidgetItem(self.tree_widget)
            error_item.setText(0, "解析錯誤")
            error_item.setText(1, "")
            error_item.setText(2, "錯誤")
    
    def _parse_dust_line(self, line: str):
        """解析 dust 輸出的單行"""
        try:
            print(f"PARSE: Input line: '{line}'")
            
            # 首先移除 ANSI 色碼
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_line = ansi_escape.sub('', line)
            print(f"PARSE: After ANSI removal: '{clean_line}'")
            
            # dust 輸出格式分析：
            # 原始 Unicode 格式（保持原有，但不在代碼中使用）：
            # 180K   ├── tests
            # 429K   │ ├── favicon
            # 429K   ├─┴ static
            # 445K   ├── ui
            # 1.1M   │ ├── objects
            # 1.2M   └── .git
            
            # 提取大小 - 大小通常在開頭，後跟一些空格
            size_match = re.match(r'^\s*(\d+(?:\.\d+)?[KMGTPE]?[Bb]?)\s+', clean_line)
            if not size_match:
                return None
            
            size = size_match.group(1)
            remaining = clean_line[size_match.end():]
            print(f"PARSE: Size: '{size}', Remaining: '{remaining}'")
            
            # 分析樹狀結構和檔案名
            # dust 輸出格式：[tree_chars] [filename] [spaces] │ [progress_bar] │ [percentage]
            # 需要精確解析以避免包含進度條字符
            tree_pattern = r'^([├└│┌─┴\s]*)\s*([^\s│]+(?:\s+[^\s│]+)*?)\s*│'
            content_match = re.match(tree_pattern, remaining)
            
            if content_match:
                tree_chars = content_match.group(1) or ""
                filename = content_match.group(2) or ""
                # 清理檔案名中可能殘留的樹狀符號
                filename = re.sub(r'^[├└│┌─┴\s]+', '', filename).strip()
                
                print(f"PARSE: Tree chars: '{tree_chars}', Filename: '{filename}'")
                
                # 計算縮排層級 - 基於樹狀結構的深度
                indent_level = self._calculate_indent_level(tree_chars)
                
                # 判斷是否為目錄
                is_directory = self._is_directory(filename)
                
                return {
                    'size': size,
                    'filename': filename,
                    'indent_level': indent_level,
                    'is_directory': is_directory,
                    'original_line': line
                }
            else:
                print(f"PARSE: Failed to match tree pattern for: '{remaining}'")
                # 如果解析失敗，嘗試直接使用剩餘部分作為檔案名
                filename = remaining.strip()
                if filename:
                    return {
                        'size': size,
                        'filename': filename,
                        'indent_level': 0,
                        'is_directory': True,
                        'original_line': line
                    }
            
        except Exception as e:
            print(f"PARSE: Exception parsing line: {line}, error: {e}")
            logger.debug(f"Failed to parse line: {line}, error: {e}")
        
        return None
    
    def _calculate_indent_level(self, tree_chars: str) -> int:
        """計算縮排層級基於樹狀字符"""
        # 分析樹狀字符來確定層級
        # │ 字符表示上層有父目錄
        # ├─, ├─┴, └── 表示當前層級的分支
        
        level = 0
        for char in tree_chars:
            if char == '│':  # 縱向連接線表示層級
                level += 1
            elif char in '├└┌':  # 分支符號，停止計數
                break
        
        return level
    
    def _is_directory(self, filename: str) -> bool:
        """判斷是否為目錄"""
        if '.' in filename:
            # 檢查是否有文件擴展名
            parts = filename.split('.')
            if len(parts) > 1:
                ext = parts[-1].lower()
                # 常見的文件擴展名
                file_extensions = {
                    'txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml',
                    'jpg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
                    'mp3', 'mp4', 'avi', 'zip', 'rar', 'exe', 'dll', 'so',
                    'c', 'cpp', 'h', 'java', 'cs', 'php', 'rb', 'go', 'rs'
                }
                if ext in file_extensions:
                    return False
        return True
    
    def _create_tree_item(self, parsed_item):
        """創建樹狀項目"""
        try:
            item = QTreeWidgetItem()
            item.setText(0, parsed_item['filename'])
            item.setText(1, parsed_item['size'])
            item.setText(2, "目錄" if parsed_item['is_directory'] else "檔案")
            
            # 根據類型設置圖示
            if parsed_item['is_directory']:
                item.setIcon(0, self.tree_widget.style().standardIcon(self.tree_widget.style().SP_DirIcon))
            else:
                item.setIcon(0, self.tree_widget.style().standardIcon(self.tree_widget.style().SP_FileIcon))
            
            return item
            
        except Exception as e:
            logger.error(f"Error creating tree item: {e}")
            return None
    
    def _add_item_to_hierarchy(self, tree_item, indent_level, parent_stack):
        """將項目添加到正確的層級結構中"""
        try:
            if tree_item is None:
                return
                
            # 調整父項目棧的大小以匹配當前層級
            # 如果當前層級比棧深度小，需要移除多餘的父項目
            while len(parent_stack) > indent_level:
                parent_stack.pop()
            
            # 添加項目到正確的父項目下
            if indent_level == 0:
                # 頂層項目
                self.tree_widget.addTopLevelItem(tree_item)
                parent_stack.clear()
                parent_stack.append(tree_item)
            elif len(parent_stack) > 0:
                # 子項目，添加到最後一個父項目下
                parent = parent_stack[-1]
                parent.addChild(tree_item)
                
                # 如果這是新的更深層級，添加到棧中
                if indent_level > len(parent_stack) - 1:
                    parent_stack.append(tree_item)
                else:
                    # 同一層級或回到上層，替換當前層級的項目
                    parent_stack[indent_level] = tree_item
                    # 移除更深層的項目
                    parent_stack = parent_stack[:indent_level + 1]
            else:
                # 如果棧為空但不是頂層，作為頂層處理
                self.tree_widget.addTopLevelItem(tree_item)
                parent_stack.clear()
                parent_stack.append(tree_item)
                
        except Exception as e:
            logger.error(f"Error adding item to hierarchy: {e}")
            # 出錯時直接添加為頂層項目
            if tree_item:
                self.tree_widget.addTopLevelItem(tree_item)


class DustViewRedesigned(QWidget):
    """dust 工具的重新設計界面 - 優化佈局和結果顯示"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_default_settings()
    
    def setup_ui(self):
        """設置優化後的用戶界面"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
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
        
        # 主要配置區域 - 使用水平佈局 (flex)
        config_layout = QHBoxLayout()
        config_layout.setSpacing(16)
        
        # 左側：分析參數 (40% 寬度)
        analysis_group = QGroupBox("分析參數")
        analysis_group.setMaximumWidth(400)
        analysis_layout = QGridLayout()
        analysis_layout.setSpacing(12)
        
        row = 0
        
        # 目標路徑
        analysis_layout.addWidget(QLabel("分析路徑:"), row, 0)
        path_layout = QHBoxLayout()
        path_layout.setSpacing(8)
        
        self.dust_target_path_input = ModernLineEdit(placeholder="選擇要分析的目錄路徑")
        self.dust_target_path_input.setToolTip("選擇要進行磁碟空間分析的目錄路徑")
        path_layout.addWidget(self.dust_target_path_input, 1)
        
        self.dust_browse_button = DirectoryButton(text="瀏覽...")
        self.dust_browse_button.directory_selected.connect(self.dust_target_path_input.setText)
        path_layout.addWidget(self.dust_browse_button)
        
        analysis_layout.addLayout(path_layout, row, 1)
        row += 1
        
        # 最大深度
        analysis_layout.addWidget(QLabel("最大深度:"), row, 0)
        self.dust_max_depth_input = QSpinBox()
        self.dust_max_depth_input.setMinimum(1)
        self.dust_max_depth_input.setMaximum(20)
        self.dust_max_depth_input.setValue(3)
        self.dust_max_depth_input.setToolTip("設置目錄遞歸的最大深度")
        analysis_layout.addWidget(self.dust_max_depth_input, row, 1)
        row += 1
        
        # 顯示行數
        analysis_layout.addWidget(QLabel("顯示行數:"), row, 0)
        self.dust_lines_input = QSpinBox()
        self.dust_lines_input.setMinimum(10)
        self.dust_lines_input.setMaximum(1000)
        self.dust_lines_input.setValue(50)
        self.dust_lines_input.setToolTip("限制顯示的結果行數")
        analysis_layout.addWidget(self.dust_lines_input, row, 1)
        row += 1
        
        # 最小檔案大小
        analysis_layout.addWidget(QLabel("最小大小:"), row, 0)
        self.dust_min_size_input = ModernLineEdit(placeholder="例如: 1M, 100K")
        self.dust_min_size_input.setToolTip("設置最小檔案大小過濾條件")
        analysis_layout.addWidget(self.dust_min_size_input, row, 1)
        row += 1
        
        analysis_group.setLayout(analysis_layout)
        config_layout.addWidget(analysis_group)
        
        # 右側：合併的選項區塊 (60% 寬度)
        options_group = QGroupBox("分析選項")
        options_layout = QGridLayout()
        options_layout.setSpacing(12)
        
        # 顯示選項 (第一行)
        options_layout.addWidget(QLabel("顯示設定:"), 0, 0, Qt.AlignTop)
        display_options_layout = QVBoxLayout()
        
        self.dust_reverse_sort_checkbox = QCheckBox("反向排序 (大到小)")
        self.dust_reverse_sort_checkbox.setToolTip("按檔案大小從大到小排序")
        self.dust_reverse_sort_checkbox.setChecked(True)
        display_options_layout.addWidget(self.dust_reverse_sort_checkbox)
        
        self.dust_apparent_size_checkbox = QCheckBox("顯示表面大小")
        self.dust_apparent_size_checkbox.setToolTip("顯示檔案的表面大小而非實際佔用空間")
        display_options_layout.addWidget(self.dust_apparent_size_checkbox)
        
        self.dust_full_paths_checkbox = QCheckBox("顯示完整路徑")
        self.dust_full_paths_checkbox.setToolTip("顯示檔案和目錄的完整路徑")
        display_options_layout.addWidget(self.dust_full_paths_checkbox)
        
        self.dust_files_only_checkbox = QCheckBox("僅顯示檔案")
        self.dust_files_only_checkbox.setToolTip("僅顯示檔案，不包含目錄")
        display_options_layout.addWidget(self.dust_files_only_checkbox)
        
        options_layout.addLayout(display_options_layout, 0, 1)
        
        # 過濾選項 (第二行)
        options_layout.addWidget(QLabel("過濾設定:"), 1, 0, Qt.AlignTop)
        filter_layout = QGridLayout()
        filter_layout.setSpacing(8)
        
        filter_layout.addWidget(QLabel("包含類型:"), 0, 0)
        self.dust_include_types_input = ModernLineEdit(placeholder="例如: txt,pdf,jpg")
        self.dust_include_types_input.setToolTip("指定要包含的檔案類型，用逗號分隔")
        filter_layout.addWidget(self.dust_include_types_input, 0, 1)
        
        filter_layout.addWidget(QLabel("排除模式:"), 1, 0)
        self.dust_exclude_patterns_input = ModernLineEdit(placeholder="例如: *.tmp,node_modules")
        self.dust_exclude_patterns_input.setToolTip("指定要排除的檔案或目錄模式，用逗號分隔")
        filter_layout.addWidget(self.dust_exclude_patterns_input, 1, 1)
        
        options_layout.addLayout(filter_layout, 1, 1)
        
        options_group.setLayout(options_layout)
        config_layout.addWidget(options_group)
        
        main_layout.addLayout(config_layout)
        
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
        
        # 結果顯示區域 - 使用新的結果組件，佔用剩餘所有空間
        results_group = QGroupBox("分析結果")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(8, 8, 8, 8)
        
        self.dust_results_display = DustResultsWidget()
        results_layout.addWidget(self.dust_results_display)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)  # stretch factor = 1，佔用所有剩餘空間
        
        self.setLayout(main_layout)
    
    def load_default_settings(self):
        """載入預設設定"""
        try:
            # 載入預設值
            default_max_depth = config_manager.get('tools.dust.default_depth', 3)
            self.dust_max_depth_input.setValue(default_max_depth)
            
            default_lines = config_manager.get('tools.dust.default_limit', 50)
            self.dust_lines_input.setValue(default_lines)
            
            default_reverse_sort = True
            self.dust_reverse_sort_checkbox.setChecked(default_reverse_sort)
            
            default_apparent_size = config_manager.get('tools.dust.apparent_size', False)
            self.dust_apparent_size_checkbox.setChecked(default_apparent_size)
            
            logger.info(f"Loaded default dust settings: max_depth={default_max_depth}, lines={default_lines}")
            
        except Exception as e:
            logger.error(f"Error loading default dust settings: {e}")
            # 使用硬編碼預設值作為回退
            self.dust_max_depth_input.setValue(3)
            self.dust_lines_input.setValue(50)
            self.dust_reverse_sort_checkbox.setChecked(True)
    
    def set_analyze_button_state(self, text, enabled):
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
        self.dust_results_display.clear_results()
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
            'target_path': self.dust_target_path_input.text().strip() or '.',
            'max_depth': self.dust_max_depth_input.value(),
            'sort_reverse': self.dust_reverse_sort_checkbox.isChecked(),
            'number_of_lines': self.dust_lines_input.value(),
            'file_types': include_types if include_types else None,
            'exclude_patterns': exclude_patterns if exclude_patterns else None,
            'show_apparent_size': self.dust_apparent_size_checkbox.isChecked(),
            'min_size': self.dust_min_size_input.text().strip() or None,
            'full_paths': self.dust_full_paths_checkbox.isChecked(),
            'files_only': self.dust_files_only_checkbox.isChecked()
        }

    def set_results(self, html_output: str, html_error: str):
        """設置分析結果"""
        self.dust_results_display.set_results(html_output, html_error)