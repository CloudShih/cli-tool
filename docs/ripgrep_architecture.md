# Ripgrep 系統架構設計文檔
**版本**: 1.0  
**日期**: 2025-01-06  
**專案**: CLI Tool Integration - ripgrep 模組架構設計  

## 🏗️ 系統架構概覽

### 架構原則
- **MVC 模式遵循**: 嚴格分離模型、視圖、控制器職責
- **插件模式整合**: 與現有插件系統無縫整合
- **非同步處理**: 搜尋操作不阻塞 UI 主執行緒
- **可擴展性**: 支援未來功能擴展和優化
- **效能優先**: 針對大量搜尋結果最佳化

### 核心架構圖
```
┌─ CLI Tool Integration Application ────────────────────────────┐
│                                                              │
│ ┌─ Plugin Manager ────────────────────────────────────────────┐ │
│ │  • 載入和管理所有工具插件                                      │ │
│ │  • 提供統一的插件接口 (PluginInterface)                      │ │
│ │  • 生命週期管理 (initialize, cleanup)                       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                              ↓                               │
│ ┌─ Ripgrep Plugin ───────────────────────────────────────────┐ │
│ │                                                            │ │
│ │  ┌─ ripgrep_model.py ─────────────────────────────────┐    │ │
│ │  │  • RipgrepEngine (命令執行引擎)                        │    │ │
│ │  │  • RipgrepParser (輸出解析器)                         │    │ │
│ │  │  • SearchResultModel (搜尋結果資料模型)               │    │ │
│ │  │  • ConfigModel (配置管理模型)                        │    │ │
│ │  └──────────────────────────────────────────────────┘    │ │
│ │                              ↕                             │ │
│ │  ┌─ ripgrep_controller.py ───────────────────────────┐    │ │
│ │  │  • SearchController (搜尋流程控制)                   │    │ │
│ │  │  • ResultsController (結果管理控制)                  │    │ │
│ │  │  • ConfigController (配置管理控制)                   │    │ │
│ │  └──────────────────────────────────────────────────┘    │ │
│ │                              ↕                             │ │
│ │  ┌─ ripgrep_view.py ──────────────────────────────────┐    │ │
│ │  │  • RipgrepMainView (主要介面視圖)                     │    │ │
│ │  │  • SearchPanelView (搜尋面板視圖)                     │    │ │
│ │  │  • ResultsTreeView (階層結果樹視圖)                   │    │ │
│ │  │  • ContextDetailView (上下文詳細視圖)                │    │ │
│ │  └──────────────────────────────────────────────────┘    │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─ Shared Components ─────────────────────────────────────────┐ │
│ │  • Config Manager (統一配置管理)                           │ │
│ │  • Theme Manager (主題管理)                               │ │
│ │  • UI Components (ModernButton, ModernLineEdit 等)        │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 📂 模組結構設計

### 目錄結構
```
tools/ripgrep/
├── __init__.py
├── plugin.py                 # 插件入口點
├── ripgrep_model.py          # 資料模型層
├── ripgrep_view.py           # 視圖層
├── ripgrep_controller.py     # 控制器層
├── components/               # 專屬 UI 元件
│   ├── __init__.py
│   ├── search_panel.py       # 搜尋面板元件
│   ├── results_tree.py       # 結果樹元件
│   ├── context_viewer.py     # 上下文檢視器
│   └── advanced_options.py   # 進階選項面板
├── core/                     # 核心邏輯
│   ├── __init__.py
│   ├── search_engine.py      # 搜尋引擎
│   ├── result_parser.py      # 結果解析器
│   ├── data_models.py        # 資料結構定義
│   └── async_worker.py       # 非同步工作執行緒
└── tests/                    # 測試檔案
    ├── __init__.py
    ├── test_model.py
    ├── test_view.py
    ├── test_controller.py
    └── test_integration.py
```

## 🔧 核心模組設計

### 1. 插件入口點 (plugin.py)
```python
"""
Ripgrep 插件入口點 - 實現 PluginInterface
"""
from core.plugin_manager import PluginInterface
from .ripgrep_model import RipgrepModel
from .ripgrep_view import RipgrepView
from .ripgrep_controller import RipgrepController
import subprocess
import logging

logger = logging.getLogger(__name__)

class RipgrepPlugin(PluginInterface):
    """Ripgrep 文本搜尋工具插件"""
    
    def __init__(self):
        self._is_available = None
        self._version = None
    
    @property
    def name(self) -> str:
        return "ripgrep"
    
    @property
    def display_name(self) -> str:
        return "文本搜尋"
    
    @property
    def description(self) -> str:
        return "使用 ripgrep 進行高效能文本內容搜尋，支援正則表達式和多種檔案格式"
    
    @property
    def version(self) -> str:
        if self._version is None:
            self._version = self._detect_version()
        return self._version
    
    @property
    def required_tools(self) -> list[str]:
        return ["rg"]  # ripgrep 執行檔
    
    @property
    def icon(self) -> str:
        return "🔍"  # 搜尋圖示
    
    def check_tools_availability(self) -> bool:
        """檢查 ripgrep 工具可用性"""
        if self._is_available is not None:
            return self._is_available
            
        try:
            result = subprocess.run(
                ['rg', '--version'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            self._is_available = result.returncode == 0
            if self._is_available:
                # 提取版本資訊
                version_line = result.stdout.split('\n')[0]
                self._version = version_line.split()[1] if len(version_line.split()) > 1 else "Unknown"
            logger.info(f"Ripgrep availability check: {self._is_available}, version: {self._version}")
            
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Ripgrep not found or timeout: {e}")
            self._is_available = False
            
        return self._is_available
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 檢查工具可用性
            if not self.check_tools_availability():
                logger.error("Ripgrep tool not available")
                return False
            
            logger.info(f"Ripgrep plugin initialized successfully (version: {self.version})")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ripgrep plugin: {e}")
            return False
    
    def is_available(self) -> bool:
        """檢查插件是否可用"""
        return self.check_tools_availability()
    
    def create_model(self):
        """創建模型實例"""
        return RipgrepModel()
    
    def create_view(self):
        """創建視圖實例"""
        return RipgrepView()
    
    def create_controller(self, model, view):
        """創建控制器實例"""
        return RipgrepController(model, view)
    
    def cleanup(self):
        """清理資源"""
        logger.info("Ripgrep plugin cleanup completed")
    
    def _detect_version(self) -> str:
        """偵測 ripgrep 版本"""
        try:
            if self._is_available:
                return self._version or "Unknown"
            else:
                return "Not Available"
        except:
            return "Unknown"

def create_plugin():
    """插件工廠函數"""
    return RipgrepPlugin()
```

### 2. 資料模型層 (ripgrep_model.py)
```python
"""
Ripgrep 資料模型層 - 處理搜尋邏輯和資料管理
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import re
import logging
from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class SearchStatus(Enum):
    """搜尋狀態枚舉"""
    IDLE = "idle"
    SEARCHING = "searching"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass
class HighlightSpan:
    """高亮區域資料結構"""
    start: int
    end: int
    highlight_type: str = 'match'

@dataclass
class SearchMatch:
    """搜尋匹配項資料結構"""
    line_number: int
    column: int
    content: str
    highlights: List[HighlightSpan] = field(default_factory=list)
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)

@dataclass
class FileResult:
    """檔案搜尋結果資料結構"""
    file_path: str
    matches: List[SearchMatch] = field(default_factory=list)
    total_matches: int = 0
    file_type: Optional[str] = None
    file_size: Optional[int] = None

@dataclass
class SearchParameters:
    """搜尋參數資料結構"""
    pattern: str
    search_path: str = "."
    case_sensitive: bool = False
    whole_words: bool = False
    regex_mode: bool = False
    multiline: bool = False
    context_lines: int = 3
    max_results: int = 1000
    file_types: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_depth: Optional[int] = None
    follow_symlinks: bool = False
    search_hidden: bool = False

@dataclass
class SearchSummary:
    """搜尋結果摘要"""
    pattern: str
    total_matches: int = 0
    files_with_matches: int = 0
    files_searched: int = 0
    search_time: float = 0.0
    status: SearchStatus = SearchStatus.IDLE
    error_message: Optional[str] = None

class RipgrepModel(QObject):
    """Ripgrep 模型類 - 管理搜尋邏輯和資料"""
    
    # 信號定義
    search_started = pyqtSignal()
    search_progress = pyqtSignal(int, int)  # files_scanned, matches_found
    search_result_found = pyqtSignal(object)  # FileResult
    search_completed = pyqtSignal(object)  # SearchSummary
    search_error = pyqtSignal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self.current_search = None
        self.search_history: List[SearchParameters] = []
        self.results: List[FileResult] = []
        self.summary = SearchSummary("")
        
    def start_search(self, search_params: SearchParameters):
        """開始搜尋操作"""
        from .core.async_worker import RipgrepSearchWorker
        
        # 儲存搜尋參數到歷史
        self.add_to_history(search_params)
        
        # 清除之前的結果
        self.clear_results()
        
        # 創建並啟動搜尋工作執行緒
        self.current_search = RipgrepSearchWorker(search_params)
        self.current_search.search_started.connect(self.search_started.emit)
        self.current_search.progress_updated.connect(self.search_progress.emit)
        self.current_search.result_found.connect(self._on_result_found)
        self.current_search.search_completed.connect(self._on_search_completed)
        self.current_search.search_error.connect(self.search_error.emit)
        
        self.current_search.start()
    
    def cancel_search(self):
        """取消當前搜尋"""
        if self.current_search and self.current_search.isRunning():
            self.current_search.cancel_search()
    
    def clear_results(self):
        """清除搜尋結果"""
        self.results.clear()
        self.summary = SearchSummary("")
    
    def add_to_history(self, search_params: SearchParameters):
        """添加搜尋參數到歷史記錄"""
        # 避免重複的歷史記錄
        if search_params not in self.search_history:
            self.search_history.insert(0, search_params)
            # 限制歷史記錄數量
            if len(self.search_history) > 50:
                self.search_history = self.search_history[:50]
    
    def get_search_history(self) -> List[SearchParameters]:
        """獲取搜尋歷史"""
        return self.search_history.copy()
    
    def _on_result_found(self, file_result: FileResult):
        """處理找到的搜尋結果"""
        self.results.append(file_result)
        self.search_result_found.emit(file_result)
    
    def _on_search_completed(self, summary: SearchSummary):
        """處理搜尋完成"""
        self.summary = summary
        self.search_completed.emit(summary)
        self.current_search = None
    
    def export_results(self, format_type: str = "json") -> str:
        """匯出搜尋結果"""
        if format_type.lower() == "json":
            return json.dumps([
                {
                    "file_path": result.file_path,
                    "total_matches": result.total_matches,
                    "matches": [
                        {
                            "line_number": match.line_number,
                            "column": match.column,
                            "content": match.content,
                            "highlights": [
                                {"start": h.start, "end": h.end, "type": h.highlight_type}
                                for h in match.highlights
                            ]
                        }
                        for match in result.matches
                    ]
                }
                for result in self.results
            ], indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["File Path", "Line Number", "Column", "Content"])
            
            for result in self.results:
                for match in result.matches:
                    writer.writerow([
                        result.file_path,
                        match.line_number,
                        match.column,
                        match.content.strip()
                    ])
            
            return output.getvalue()
        
        else:  # plain text
            lines = []
            lines.append(f"搜尋結果摘要:")
            lines.append(f"  模式: {self.summary.pattern}")
            lines.append(f"  總匹配數: {self.summary.total_matches}")
            lines.append(f"  包含匹配的檔案數: {self.summary.files_with_matches}")
            lines.append(f"  搜尋時間: {self.summary.search_time:.2f} 秒")
            lines.append("")
            
            for result in self.results:
                lines.append(f"📁 {result.file_path} ({result.total_matches} 個匹配)")
                for match in result.matches:
                    lines.append(f"  {match.line_number:4d}: {match.content.strip()}")
                lines.append("")
            
            return "\n".join(lines)
```

### 3. 視圖層架構設計 (ripgrep_view.py)
```python
"""
Ripgrep 視圖層 - UI 界面組件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QTreeView, QTextEdit, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ui.components.buttons import ModernButton, PrimaryButton
from ui.components.inputs import ModernLineEdit, ModernComboBox
from .components.search_panel import SearchPanel
from .components.results_tree import ResultsTreeView
from .components.context_viewer import ContextViewer
from .components.advanced_options import AdvancedOptionsPanel

import logging

logger = logging.getLogger(__name__)

class RipgrepView(QWidget):
    """Ripgrep 主視圖 - 整合所有 UI 組件"""
    
    # 信號定義
    search_requested = pyqtSignal(object)  # SearchParameters
    search_cancelled = pyqtSignal()
    result_selected = pyqtSignal(str, int)  # file_path, line_number
    export_requested = pyqtSignal(str)  # format_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """設置使用者介面"""
        self.setWindowTitle("Ripgrep 文本搜尋")
        
        # 主佈局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 搜尋面板
        self.search_panel = SearchPanel()
        main_layout.addWidget(self.search_panel)
        
        # 進階選項面板 (可摺疊)
        self.advanced_options = AdvancedOptionsPanel()
        self.advanced_options.setVisible(False)  # 預設隱藏
        main_layout.addWidget(self.advanced_options)
        
        # 分割器 - 分隔結果和詳細資訊
        splitter = QSplitter(Qt.Horizontal)
        
        # 結果樹狀檢視
        self.results_tree = ResultsTreeView()
        splitter.addWidget(self.results_tree)
        
        # 上下文檢視器
        self.context_viewer = ContextViewer()
        splitter.addWidget(self.context_viewer)
        
        # 設置分割比例
        splitter.setStretchFactor(0, 2)  # 結果樹佔 2/3
        splitter.setStretchFactor(1, 1)  # 上下文檢視佔 1/3
        
        main_layout.addWidget(splitter, 1)  # 占據剩餘空間
        
        # 狀態列
        self.setup_status_bar()
        main_layout.addLayout(self.status_layout)
        
        self.setLayout(main_layout)
        
    def setup_status_bar(self):
        """設置狀態列"""
        self.status_layout = QHBoxLayout()
        
        # 狀態標籤
        self.status_label = QLabel("準備就緒")
        self.status_layout.addWidget(self.status_label)
        
        self.status_layout.addStretch()
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.status_layout.addWidget(self.progress_bar)
        
        # 匯出按鈕
        self.export_button = ModernButton("💾 匯出結果")
        self.export_button.setEnabled(False)
        self.status_layout.addWidget(self.export_button)
        
    def setup_connections(self):
        """設置信號連接"""
        # 搜尋面板信號
        self.search_panel.search_requested.connect(self._on_search_requested)
        self.search_panel.search_cancelled.connect(self.search_cancelled.emit)
        self.search_panel.advanced_options_toggled.connect(self._toggle_advanced_options)
        
        # 進階選項面板信號
        self.advanced_options.options_changed.connect(self._on_advanced_options_changed)
        
        # 結果樹信號
        self.results_tree.result_selected.connect(self._on_result_selected)
        self.results_tree.file_double_clicked.connect(self._on_file_double_clicked)
        
        # 匯出按鈕
        self.export_button.clicked.connect(self._on_export_requested)
        
    def _on_search_requested(self):
        """處理搜尋請求"""
        # 收集搜尋參數
        search_params = self._collect_search_parameters()
        if search_params:
            self.search_requested.emit(search_params)
            
    def _collect_search_parameters(self):
        """收集搜尋參數"""
        from .ripgrep_model import SearchParameters
        
        # 基本參數
        pattern = self.search_panel.get_pattern()
        if not pattern:
            self.status_label.setText("❌ 請輸入搜尋模式")
            return None
            
        search_path = self.search_panel.get_search_path()
        
        # 進階參數
        advanced_params = self.advanced_options.get_parameters()
        
        return SearchParameters(
            pattern=pattern,
            search_path=search_path,
            **advanced_params
        )
    
    def _toggle_advanced_options(self, visible: bool):
        """切換進階選項顯示"""
        self.advanced_options.setVisible(visible)
        
    def _on_advanced_options_changed(self):
        """處理進階選項變更"""
        # 可以實現即時搜尋或參數驗證
        pass
    
    def _on_result_selected(self, file_path: str, line_number: int):
        """處理結果選擇"""
        self.result_selected.emit(file_path, line_number)
        # 更新上下文檢視器
        self.context_viewer.show_file_context(file_path, line_number)
        
    def _on_file_double_clicked(self, file_path: str, line_number: int):
        """處理檔案雙擊"""
        # 可以實現開啟外部編輯器等功能
        logger.info(f"Double clicked: {file_path}:{line_number}")
        
    def _on_export_requested(self):
        """處理匯出請求"""
        # 可以彈出格式選擇對話框
        self.export_requested.emit("json")  # 預設為 JSON 格式
        
    # 公共介面方法
    def show_search_progress(self, files_scanned: int, matches_found: int):
        """顯示搜尋進度"""
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"🔍 搜尋中... ({files_scanned} 檔案, {matches_found} 匹配)")
        
    def show_search_completed(self, summary):
        """顯示搜尋完成"""
        self.progress_bar.setVisible(False)
        self.export_button.setEnabled(True)
        self.status_label.setText(
            f"✅ 搜尋完成: {summary.total_matches} 個匹配 "
            f"在 {summary.files_with_matches} 個檔案中 "
            f"({summary.search_time:.2f}s)"
        )
        
    def show_search_error(self, error_message: str):
        """顯示搜尋錯誤"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ 搜尋錯誤: {error_message}")
        
    def add_search_result(self, file_result):
        """添加搜尋結果到樹狀檢視"""
        self.results_tree.add_file_result(file_result)
        
    def clear_results(self):
        """清除搜尋結果"""
        self.results_tree.clear()
        self.context_viewer.clear()
        self.export_button.setEnabled(False)
        self.status_label.setText("準備就緒")
```

### 4. 控制器層設計 (ripgrep_controller.py)
```python
"""
Ripgrep 控制器層 - 協調模型和視圖
"""
from PyQt5.QtCore import QObject
from .ripgrep_model import RipgrepModel
from .ripgrep_view import RipgrepView
import logging

logger = logging.getLogger(__name__)

class RipgrepController(QObject):
    """Ripgrep 控制器 - 管理模型和視圖之間的互動"""
    
    def __init__(self, model: RipgrepModel, view: RipgrepView):
        super().__init__()
        self.model = model
        self.view = view
        self.setup_connections()
        
    def setup_connections(self):
        """設置模型和視圖之間的信號連接"""
        # 視圖 → 模型
        self.view.search_requested.connect(self.model.start_search)
        self.view.search_cancelled.connect(self.model.cancel_search)
        self.view.export_requested.connect(self._handle_export_request)
        
        # 模型 → 視圖
        self.model.search_started.connect(self._on_search_started)
        self.model.search_progress.connect(self.view.show_search_progress)
        self.model.search_result_found.connect(self.view.add_search_result)
        self.model.search_completed.connect(self.view.show_search_completed)
        self.model.search_error.connect(self.view.show_search_error)
        
        # 視圖內部信號處理
        self.view.result_selected.connect(self._handle_result_selection)
        
    def _on_search_started(self):
        """處理搜尋開始"""
        self.view.clear_results()
        logger.info("Search started")
        
    def _handle_result_selection(self, file_path: str, line_number: int):
        """處理結果選擇"""
        logger.info(f"Result selected: {file_path}:{line_number}")
        # 可以實現額外的邏輯，如載入檔案內容等
        
    def _handle_export_request(self, format_type: str):
        """處理匯出請求"""
        try:
            export_data = self.model.export_results(format_type)
            
            # 可以實現檔案儲存對話框
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                f"匯出搜尋結果 ({format_type.upper()})",
                f"search_results.{format_type}",
                f"{format_type.upper()} files (*.{format_type})"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                    
                logger.info(f"Results exported to: {file_path}")
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            self.view.show_search_error(f"匯出失敗: {str(e)}")
    
    def get_current_results(self):
        """獲取當前搜尋結果"""
        return self.model.results
    
    def get_search_history(self):
        """獲取搜尋歷史"""
        return self.model.get_search_history()
```

## 🔌 介面設計

### PluginInterface 實現
```python
"""
插件介面定義 - 確保與主應用程式相容
"""
from abc import ABC, abstractmethod
from typing import List

class PluginInterface(ABC):
    """插件介面 - 所有插件必須實現的介面"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名稱"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """顯示名稱"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def required_tools(self) -> List[str]:
        """所需的外部工具"""
        pass
    
    @property
    @abstractmethod
    def icon(self) -> str:
        """插件圖示"""
        pass
    
    @abstractmethod
    def check_tools_availability(self) -> bool:
        """檢查外部工具可用性"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """檢查插件是否可用"""
        pass
    
    @abstractmethod
    def create_model(self):
        """創建模型實例"""
        pass
    
    @abstractmethod
    def create_view(self):
        """創建視圖實例"""
        pass
    
    @abstractmethod
    def create_controller(self, model, view):
        """創建控制器實例"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理資源"""
        pass
```

## 📊 資料流程架構

### 搜尋流程序列圖
```
用戶輸入搜尋 → SearchPanel → Controller → Model → AsyncWorker
                                                        ↓
用戶看到結果 ← ResultsTree ← View ← Controller ← Model ← RipgrepParser
```

### 記憶體管理架構
```python
"""
記憶體管理策略 - 處理大量搜尋結果
"""
class MemoryManager:
    """記憶體管理器"""
    
    def __init__(self, max_memory_mb: int = 200):
        self.max_memory_mb = max_memory_mb
        self.current_usage = 0
        self.cache = {}
        
    def check_memory_usage(self) -> bool:
        """檢查記憶體使用狀況"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb > self.max_memory_mb
    
    def optimize_memory(self):
        """記憶體優化"""
        import gc
        # 清理快取
        self.cache.clear()
        # 強制垃圾回收
        gc.collect()
        logger.info("Memory optimization completed")
```

## 🧪 測試架構設計

### 測試金字塔
```
┌─ E2E Tests (Integration) ─────────────────────┐
│  • 完整搜尋流程測試                              │
│  • UI 互動測試                                 │
│  • 效能測試                                    │
└──────────────────────────────────────────────┘
         ↑
┌─ Component Tests ─────────────────────────────┐
│  • Controller 測試                           │
│  • View 組件測試                              │
│  • Model 邏輯測試                             │
└──────────────────────────────────────────────┘
         ↑
┌─ Unit Tests ──────────────────────────────────┐
│  • 解析器測試                                  │
│  • 資料結構測試                                │
│  • 工具函數測試                                │
└──────────────────────────────────────────────┘
```

### 測試覆蓋率目標
- **單元測試**: >90% 程式碼覆蓋率
- **整合測試**: >80% 功能路徑覆蓋
- **效能測試**: 關鍵指標驗證

## 🔧 配置架構設計

### 配置檔案結構
```json
{
  "tools": {
    "ripgrep": {
      "executable_path": "rg",
      "default_format": "json",
      "performance": {
        "max_results": 1000,
        "max_memory_mb": 200,
        "batch_size": 20,
        "ui_update_interval": 100
      },
      "search_defaults": {
        "context_lines": 3,
        "case_sensitive": false,
        "regex_mode": false,
        "follow_symlinks": false
      },
      "ui_preferences": {
        "enable_syntax_highlighting": true,
        "show_line_numbers": true,
        "auto_expand_single_file": true
      },
      "history": {
        "search_history_size": 50,
        "remember_search_options": true
      }
    }
  }
}
```

## 📈 擴展架構設計

### 未來擴展接口
```python
"""
擴展接口設計 - 支援未來功能增強
"""
class RipgrepExtensionInterface(ABC):
    """Ripgrep 擴展接口"""
    
    @abstractmethod
    def process_search_result(self, result: FileResult) -> FileResult:
        """後處理搜尋結果"""
        pass
    
    @abstractmethod
    def enhance_search_parameters(self, params: SearchParameters) -> SearchParameters:
        """增強搜尋參數"""
        pass
    
    @abstractmethod
    def provide_search_suggestions(self, pattern: str) -> List[str]:
        """提供搜尋建議"""
        pass

# 示例擴展實現
class SyntaxHighlightExtension(RipgrepExtensionInterface):
    """語法高亮擴展"""
    
    def process_search_result(self, result: FileResult) -> FileResult:
        # 為結果添加語法高亮
        return result
    
    def enhance_search_parameters(self, params: SearchParameters) -> SearchParameters:
        return params
    
    def provide_search_suggestions(self, pattern: str) -> List[str]:
        return []
```

---

**系統架構設計完成**。下一步將進入後端實現階段，開始開發核心的搜尋引擎和資料處理模組。