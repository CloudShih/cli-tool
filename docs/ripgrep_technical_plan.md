# Ripgrep 技術實現規劃文檔
**版本**: 1.0  
**日期**: 2025-01-06  
**專案**: CLI Tool Integration - ripgrep 模組技術規劃  

## 🎯 技術目標

### 核心技術目標
- **高效能搜尋**: 支援 10,000+ 個搜尋結果的即時處理
- **非阻塞 UI**: 搜尋過程中保持使用者介面響應性
- **記憶體管理**: 大型結果集的記憶體使用最佳化
- **架構一致性**: 遵循現有 MVC 模式和外掛架構

### 技術約束
- **平台相容性**: Windows/Linux/macOS 跨平台支援
- **Python 版本**: Python 3.8+ 相容性
- **PyQt5 整合**: 利用現有 UI 元件和主題系統
- **效能要求**: 搜尋結果顯示延遲 <100ms

## 🏗️ 整體技術架構

### 技術堆疊選擇
```python
# 核心技術選型
TECHNOLOGY_STACK = {
    'ui_framework': 'PyQt5',                # 與現有系統一致
    'async_processing': 'QThread',          # Qt 原生執行緒支援
    'data_parsing': 'json + regex',         # 混合解析策略
    'data_model': 'QAbstractItemModel',     # Qt Model/View 架構
    'output_format': 'json + ansi',         # ripgrep 雙格式支援
    'memory_management': 'lazy_loading',    # 延遲載入策略
}
```

### 模組依賴關係
```
ripgrep_plugin.py
├── ripgrep_model.py
│   ├── RipgrepEngine (命令執行)
│   ├── RipgrepParser (輸出解析)
│   └── RipgrepResultModel (資料模型)
├── ripgrep_view.py
│   ├── RipgrepSearchPanel (搜尋介面)
│   ├── RipgrepResultsView (結果顯示)
│   └── RipgrepContextView (上下文檢視)
└── ripgrep_controller.py
    ├── SearchController (搜尋控制)
    ├── ResultsController (結果管理)
    └── ConfigController (設定管理)
```

## 🔧 核心技術方案

### 1. Ripgrep 輸出解析策略

#### 多格式解析支援
```python
class RipgrepParser:
    """Ripgrep 輸出解析器 - 支援多種輸出格式"""
    
    def __init__(self):
        self.parsers = {
            'json': self._parse_json_output,
            'vimgrep': self._parse_vimgrep_output,
            'default': self._parse_default_output,
        }
    
    def parse_output(self, output: str, format_type: str) -> List[SearchResult]:
        """統一解析介面"""
        parser = self.parsers.get(format_type, self.parsers['default'])
        return parser(output)
    
    def _parse_json_output(self, output: str) -> List[SearchResult]:
        """解析 JSON 格式輸出 (推薦)"""
        results = []
        for line in output.strip().split('\n'):
            if line.startswith('{'):
                try:
                    data = json.loads(line)
                    if data['type'] == 'match':
                        result = self._create_search_result(data)
                        results.append(result)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON line: {line}")
        return results
    
    def _parse_default_output(self, output: str) -> List[SearchResult]:
        """解析預設格式輸出 (備案)"""
        # 格式: filename:line_number:column:content
        pattern = re.compile(r'^([^:]+):(\d+):(\d+):(.*)$')
        results = []
        for line in output.split('\n'):
            match = pattern.match(line)
            if match:
                result = SearchResult(
                    file_path=match.group(1),
                    line_number=int(match.group(2)),
                    column=int(match.group(3)),
                    content=self._strip_ansi_codes(match.group(4))
                )
                results.append(result)
        return results
```

#### ANSI 顏色碼處理
```python
import re

class ANSIProcessor:
    """ANSI 逸出序列處理器"""
    
    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    
    @classmethod
    def strip_ansi_codes(cls, text: str) -> str:
        """移除 ANSI 顏色碼"""
        return cls.ANSI_PATTERN.sub('', text)
    
    @classmethod
    def extract_highlights(cls, text: str) -> List[HighlightSpan]:
        """提取高亮區域資訊"""
        highlights = []
        current_pos = 0
        
        for match in cls.ANSI_PATTERN.finditer(text):
            if match.group() == '\x1b[1;31m':  # 紅色粗體開始
                start_pos = match.start() - current_pos
                highlights.append(HighlightSpan(start_pos, None))
            elif match.group() == '\x1b[0m':   # 重設
                if highlights and highlights[-1].end is None:
                    highlights[-1].end = match.start() - current_pos
            current_pos += len(match.group())
        
        return highlights
```

### 2. 非同步搜尋執行方案

#### QThread 基礎執行緒實現
```python
class RipgrepSearchWorker(QThread):
    """非同步搜尋工作執行緒"""
    
    # 信號定義
    search_started = pyqtSignal()
    progress_updated = pyqtSignal(int, int)  # (files_scanned, matches_found)
    result_found = pyqtSignal(object)        # SearchResult
    search_completed = pyqtSignal(object)    # SearchSummary
    search_error = pyqtSignal(str)          # error_message
    
    def __init__(self, search_params: SearchParameters):
        super().__init__()
        self.search_params = search_params
        self.process = None
        self.should_cancel = False
        self.parser = RipgrepParser()
    
    def run(self):
        """執行搜尋操作"""
        try:
            self.search_started.emit()
            
            # 建立 ripgrep 命令
            command = self._build_command()
            
            # 啟動進程
            self.process = QProcess()
            self.process.setProgram(command[0])
            self.process.setArguments(command[1:])
            
            # 設定串流處理
            self.process.readyReadStandardOutput.connect(self._process_output)
            self.process.finished.connect(self._on_finished)
            
            self.process.start()
            
            # 等待完成或取消
            while self.process.state() != QProcess.NotRunning:
                if self.should_cancel:
                    self._cancel_search()
                    break
                self.msleep(50)  # 50ms 檢查間隔
                
        except Exception as e:
            self.search_error.emit(str(e))
    
    def _process_output(self):
        """處理即時輸出"""
        if self.process and self.process.bytesAvailable():
            data = self.process.readAllStandardOutput().data()
            output = data.decode('utf-8', errors='replace')
            
            # 解析結果
            try:
                results = self.parser.parse_output(output, 'json')
                for result in results:
                    self.result_found.emit(result)
            except Exception as e:
                logger.error(f"Parse error: {e}")
    
    def cancel_search(self):
        """取消搜尋"""
        self.should_cancel = True
        if self.process:
            self.process.kill()
```

### 3. 階層資料結構設計

#### 搜尋結果資料模型
```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

@dataclass
class HighlightSpan:
    """高亮區域"""
    start: int
    end: Optional[int] = None
    highlight_type: str = 'match'

@dataclass
class SearchMatch:
    """單一搜尋匹配"""
    line_number: int
    column: int
    content: str
    highlights: List[HighlightSpan]
    context_before: List[str] = None
    context_after: List[str] = None

@dataclass
class FileResult:
    """檔案級別結果"""
    file_path: str
    matches: List[SearchMatch]
    total_matches: int
    file_type: str = None
    file_size: int = None

@dataclass
class SearchSummary:
    """搜尋摘要"""
    pattern: str
    total_matches: int
    files_with_matches: int
    files_searched: int
    search_time: float
    status: str  # 'completed', 'cancelled', 'error'
```

#### Qt Model/View 資料模型
```python
class RipgrepResultModel(QAbstractItemModel):
    """搜尋結果資料模型 - 支援階層顯示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = RootItem()
        self.file_items = {}  # file_path -> FileItem
        self.match_count = 0
        
    def add_file_result(self, file_result: FileResult):
        """新增檔案結果"""
        self.beginInsertRows(QModelIndex(), len(self.root_item.children), 
                           len(self.root_item.children))
        
        file_item = FileItem(file_result, self.root_item)
        self.root_item.add_child(file_item)
        self.file_items[file_result.file_path] = file_item
        
        # 新增匹配項
        for match in file_result.matches:
            match_item = MatchItem(match, file_item)
            file_item.add_child(match_item)
            self.match_count += 1
        
        self.endInsertRows()
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """資料提供介面"""
        if not index.isValid():
            return None
            
        item = index.internalPointer()
        
        if role == Qt.DisplayRole:
            if isinstance(item, FileItem):
                return f"{item.file_result.file_path} ({item.file_result.total_matches} matches)"
            elif isinstance(item, MatchItem):
                match = item.match
                return f"Line {match.line_number}: {match.content[:100]}"
                
        elif role == Qt.DecorationRole:
            if isinstance(item, FileItem):
                return self._get_file_icon(item.file_result.file_type)
            elif isinstance(item, MatchItem):
                return QIcon(":/icons/match.png")
        
        return None
```

### 4. 大型結果集處理方案

#### 虛擬滾動實現
```python
class VirtualizedTreeView(QTreeView):
    """虛擬化樹狀檢視 - 支援大量資料"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)  # 啟用統一行高優化
        self.viewport_range = (0, 0)
        self.visible_items = {}
        
    def scrollContentsBy(self, dx: int, dy: int):
        """滾動事件處理"""
        super().scrollContentsBy(dx, dy)
        self._update_visible_range()
    
    def resizeEvent(self, event):
        """視窗大小變更處理"""
        super().resizeEvent(event)
        self._update_visible_range()
    
    def _update_visible_range(self):
        """更新可見範圍"""
        rect = self.viewport().rect()
        top_index = self.indexAt(rect.topLeft())
        bottom_index = self.indexAt(rect.bottomRight())
        
        if top_index.isValid() and bottom_index.isValid():
            self.viewport_range = (top_index.row(), bottom_index.row())
            self._load_visible_items()
    
    def _load_visible_items(self):
        """載入可見項目"""
        start, end = self.viewport_range
        model = self.model()
        
        for row in range(start, min(end + 10, model.rowCount())):  # +10 預載入
            index = model.index(row, 0)
            if index not in self.visible_items:
                self.visible_items[index] = model.data(index, Qt.DisplayRole)
```

#### 批次處理與記憶體管理
```python
class BatchProcessor:
    """批次處理器 - 管理大量搜尋結果"""
    
    def __init__(self, batch_size: int = 100, max_memory_mb: int = 200):
        self.batch_size = batch_size
        self.max_memory_mb = max_memory_mb
        self.current_batch = []
        self.processed_count = 0
        
    def process_results(self, results: List[SearchResult], callback: callable):
        """批次處理搜尋結果"""
        for result in results:
            self.current_batch.append(result)
            
            if len(self.current_batch) >= self.batch_size:
                self._flush_batch(callback)
            
            # 記憶體檢查
            if self._check_memory_usage():
                self._optimize_memory()
    
    def _flush_batch(self, callback: callable):
        """清空當前批次"""
        if self.current_batch:
            callback(self.current_batch.copy())
            self.processed_count += len(self.current_batch)
            self.current_batch.clear()
    
    def _check_memory_usage(self) -> bool:
        """檢查記憶體使用量"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb > self.max_memory_mb
    
    def _optimize_memory(self):
        """記憶體優化"""
        # 實施記憶體優化策略
        import gc
        gc.collect()
        logger.info(f"Memory optimization triggered at {self.processed_count} results")
```

### 5. 效能優化策略

#### 混合串流/批次處理
```python
class HybridResultProcessor:
    """混合結果處理器 - 平衡響應性與效能"""
    
    def __init__(self):
        self.streaming_threshold = 50      # 小於50個結果時串流處理
        self.batch_size = 20              # 批次大小
        self.ui_update_interval = 100     # UI 更新間隔 (ms)
        self.last_ui_update = 0
        
    def process_result(self, result: SearchResult, ui_callback: callable):
        """智能結果處理"""
        current_time = time.time() * 1000
        
        if self._should_stream():
            # 立即更新 UI
            ui_callback([result])
        else:
            # 加入批次佇列
            self.batch_queue.append(result)
            
            # 定時批次更新
            if (current_time - self.last_ui_update) > self.ui_update_interval:
                self._flush_batch(ui_callback)
                self.last_ui_update = current_time
    
    def _should_stream(self) -> bool:
        """判斷是否應該串流處理"""
        return (
            len(self.batch_queue) < self.streaming_threshold and
            self._get_cpu_usage() < 50  # CPU 使用率低於50%
        )
```

#### 平台特定優化
```python
class PlatformOptimizer:
    """平台特定優化"""
    
    @staticmethod
    def get_optimal_settings() -> dict:
        """獲取平台最佳化設定"""
        import platform
        system = platform.system().lower()
        
        settings = {
            'windows': {
                'thread_count': min(8, os.cpu_count()),
                'buffer_size': 8192,
                'encoding': 'utf-8',
            },
            'linux': {
                'thread_count': os.cpu_count(),
                'buffer_size': 16384,
                'encoding': 'utf-8',
            },
            'darwin': {  # macOS
                'thread_count': min(6, os.cpu_count()),
                'buffer_size': 8192,
                'encoding': 'utf-8',
            }
        }
        
        return settings.get(system, settings['linux'])
```

## 📊 資料流程設計

### 搜尋流程圖
```
使用者輸入
    ↓
搜尋參數驗證
    ↓
啟動搜尋執行緒
    ↓
建立 ripgrep 命令
    ↓
執行子進程
    ↓
即時輸出解析 ←→ 進度回報
    ↓
結果批次處理
    ↓
UI 模型更新
    ↓
結果顯示
```

### 記憶體使用最佳化流程
```
結果接收
    ↓
記憶體使用檢查
    ↓
超過閾值？ →→ 是 → 觸發記憶體優化
    ↓ 否              ↓
正常處理 ←←←←←←←← 垃圾回收 + 批次清理
    ↓
UI 更新
```

## 🔌 整合策略

### 與現有系統整合
```python
# config/cli_tool_config.json 擴充
{
  "tools": {
    "ripgrep": {
      "executable_path": "rg",
      "default_format": "json",
      "max_results": 1000,
      "max_memory_mb": 200,
      "batch_size": 20,
      "ui_update_interval": 100,
      "default_context_lines": 3,
      "enable_syntax_highlighting": true,
      "search_history_size": 50
    }
  }
}
```

### 外掛系統整合
```python
class RipgrepPlugin(PluginInterface):
    """Ripgrep 外掛實現"""
    
    @property
    def name(self) -> str:
        return "ripgrep"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["rg"]  # ripgrep 執行檔
    
    def check_tools_availability(self) -> bool:
        """檢查 ripgrep 工具可用性"""
        try:
            result = subprocess.run(['rg', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def create_model(self):
        return RipgrepModel()
    
    def create_view(self):
        return RipgrepView()
    
    def create_controller(self, model, view):
        return RipgrepController(model, view)
```

## 🧪 測試策略

### 單元測試覆蓋
```python
class TestRipgrepParser(unittest.TestCase):
    """Ripgrep 解析器測試"""
    
    def setUp(self):
        self.parser = RipgrepParser()
    
    def test_json_parsing(self):
        """測試 JSON 格式解析"""
        json_output = '''
        {"type":"match","data":{"path":{"text":"file.py"},"lines":{"text":"import os"}}}
        '''
        results = self.parser.parse_output(json_output, 'json')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_path, "file.py")
    
    def test_ansi_color_stripping(self):
        """測試 ANSI 顏色碼移除"""
        colored_text = "\x1b[1;31mmatched\x1b[0m text"
        clean_text = ANSIProcessor.strip_ansi_codes(colored_text)
        self.assertEqual(clean_text, "matched text")

class TestSearchWorker(unittest.TestCase):
    """搜尋工作執行緒測試"""
    
    def test_search_cancellation(self):
        """測試搜尋取消功能"""
        worker = RipgrepSearchWorker(SearchParameters("test", "."))
        worker.cancel_search()
        self.assertTrue(worker.should_cancel)
```

### 效能測試
```python
class PerformanceTest(unittest.TestCase):
    """效能測試"""
    
    def test_large_result_processing(self):
        """測試大量結果處理"""
        start_time = time.time()
        
        # 模擬 10,000 個搜尋結果
        results = [self.create_mock_result() for _ in range(10000)]
        processor = BatchProcessor(batch_size=100)
        
        processed_results = []
        processor.process_results(results, processed_results.extend)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        self.assertLess(processing_time, 2.0)  # 處理時間應少於2秒
        self.assertEqual(len(processed_results), 10000)
```

## 📋 實施階段規劃

### 第一階段 (核心功能)
1. **基礎架構建立** (1週)
   - 建立 MVC 架構骨架
   - 實現基本外掛介面
   - 建立配置管理整合

2. **搜尋引擎開發** (2週)
   - ripgrep 命令建構
   - 輸出解析器實現
   - 非同步執行緒實現

3. **基本 UI 實現** (2週)
   - 搜尋輸入介面
   - 基本結果顯示
   - 進度指示器

### 第二階段 (功能完善)
1. **進階功能** (2週)
   - 階層結果顯示
   - 上下文展開/摺疊
   - 搜尋歷史記錄

2. **效能優化** (1週)
   - 虛擬滾動實現
   - 記憶體管理優化
   - 批次處理調優

### 第三階段 (整合測試)
1. **系統整合** (1週)
   - 與主應用程式整合
   - 主題系統整合
   - 動畫效果整合

2. **測試與除錯** (1週)
   - 單元測試完善
   - 效能測試驗證
   - 使用者體驗測試

## ⚠️ 風險評估與緩解

### 技術風險
| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|----------|
| ripgrep 輸出格式變更 | 高 | 低 | 多格式解析支援 |
| 大量結果造成記憶體溢出 | 高 | 中 | 記憶體監控和優化 |
| UI 響應性問題 | 中 | 中 | 非同步處理和虛擬滾動 |
| 跨平台相容性問題 | 中 | 低 | 平台特定設定和測試 |

### 效能風險
- **記憶體使用**: 實施記憶體監控和自動優化
- **CPU 使用**: 使用適應性處理策略
- **UI 凍結**: 確保所有長時間操作在工作執行緒中執行

## 📈 後續優化計劃

### 短期優化 (1-3個月)
- 搜尋結果快取系統
- 智能搜尋建議
- 正則表達式驗證和提示

### 中期優化 (3-6個月)
- 分散式搜尋支援
- 搜尋結果的 AI 分析
- 個性化搜尋配置

### 長期規劃 (6個月+)
- 實時索引建立
- 語意搜尋支援
- 協作搜尋功能

---

**下一步**: 進入系統架構設計階段，詳細設計各模組的實現細節。