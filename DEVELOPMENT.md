# CLI Tool 開發指南

## 🚀 快速開始

### 環境設置
```bash
# 1. 克隆專案
git clone <repository-url>
cd cli_tool

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 安裝開發依賴（可選）
pip install -r requirements-dev.txt

# 4. 驗證安裝
python test_simple.py

# 5. 運行應用程式
python run.py
```

## 🏗️ 專案架構

### 目錄結構
```
cli_tool/
├── config/                 # 配置管理
│   ├── config_manager.py   # 配置管理器
│   └── cli_tool_config.json # 配置文件
├── core/                   # 核心框架
│   └── plugin_manager.py   # 插件管理器
├── tools/                  # 工具插件
│   ├── fd/                 # fd 文件搜尋插件
│   │   ├── plugin.py       # 插件介面
│   │   ├── fd_model.py     # 業務邏輯
│   │   ├── fd_view.py      # GUI 界面
│   │   └── fd_controller.py # 控制器
│   └── poppler/            # PDF 處理插件
├── static/                 # 靜態資源
├── tests/                  # 測試文件
├── main_app.py             # 主應用程式
├── run.py                  # 啟動腳本
├── build.py                # 打包腳本
├── cli_tool.spec           # PyInstaller 配置
└── setup.py                # 安裝配置
```

### 架構模式

#### 插件架構
- **PluginInterface**: 所有插件必須實現的接口
- **PluginManager**: 負責插件發現、載入和管理
- **MVC 模式**: 每個插件都採用 Model-View-Controller 架構

#### 配置管理
- **統一配置**: 所有設定通過 `config_manager` 訪問
- **環境適配**: 自動檢測開發/生產環境
- **持久化**: 支援設定保存和載入

## 🔌 插件開發

### 創建新插件

1. **建立插件目錄**
```bash
mkdir tools/my_tool
touch tools/my_tool/__init__.py
```

2. **實現插件接口**
```python
# tools/my_tool/plugin.py
from core.plugin_manager import PluginInterface
from typing import List

class MyToolPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "My awesome tool description"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["my_external_tool"]
    
    def initialize(self) -> bool:
        return True
    
    def create_view(self):
        from .my_tool_view import MyToolView
        return MyToolView()
    
    def create_model(self):
        from .my_tool_model import MyToolModel
        return MyToolModel()
    
    def create_controller(self, model, view):
        from .my_tool_controller import MyToolController
        return MyToolController(model, view)
    
    def cleanup(self):
        pass

def create_plugin():
    return MyToolPlugin()
```

3. **實現 MVC 組件**
```python
# tools/my_tool/my_tool_model.py
from config.config_manager import config_manager

class MyToolModel:
    def __init__(self):
        self.config = config_manager.get_tool_config('my_tool')
    
    def execute_command(self, *args):
        # 實現業務邏輯
        pass

# tools/my_tool/my_tool_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

class MyToolView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.button = QPushButton("Execute")
        layout.addWidget(self.button)
        self.setLayout(layout)

# tools/my_tool/my_tool_controller.py
class MyToolController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self._connect_signals()
    
    def _connect_signals(self):
        self.view.button.clicked.connect(self._execute)
    
    def _execute(self):
        # 處理用戶操作
        pass
```

4. **添加配置**
```json
{
  "tools": {
    "my_tool": {
      "executable_path": "my_tool",
      "default_option": "value"
    }
  }
}
```

### 插件最佳實踐

- **工具檢測**: 實現 `check_tools_availability()` 檢查外部工具
- **錯誤處理**: 優雅處理工具不可用的情況
- **配置管理**: 使用 `config_manager` 管理插件設定
- **日誌記錄**: 使用 `logging` 模組記錄插件狀態
- **資源清理**: 在 `cleanup()` 中釋放資源

## 🧪 測試

### 運行測試
```bash
# 基本功能測試
python test_simple.py

# 完整優化驗證
python test_optimizations.py

# GUI 功能測試（需要顯示環境）
python test_app.py --gui

# 單元測試
pytest tests/
```

### 測試新插件
1. 添加插件到 `test_simple.py`
2. 創建單元測試文件
3. 驗證插件發現和載入
4. 測試 MVC 組件功能

## 📦 打包和部署

### 開發模式運行
```bash
python run.py
```

### 打包為執行檔
```bash
# 完整建置
python build.py

# 除錯模式
python build.py --debug

# 只清理
python build.py --clean-only
```

### 手動 PyInstaller
```bash
pyinstaller --clean cli_tool.spec
```

## 🔧 配置管理

### 讀取配置
```python
from config.config_manager import config_manager

# 讀取工具配置
fd_config = config_manager.get_tool_config('fd')
executable_path = config_manager.get('tools.fd.executable_path')

# 讀取 UI 配置
ui_config = config_manager.get_ui_config()
theme = config_manager.get('ui.theme', 'dark')
```

### 設定配置
```python
# 設定值
config_manager.set('ui.theme', 'light')
config_manager.set('tools.my_tool.option', 'value')

# 保存配置
config_manager.save_config()
```

### 資源路徑處理
```python
# 獲取資源路徑（支援開發和打包環境）
config_path = config_manager.get_resource_path("config/cli_tool_config.json")
icon_path = config_manager.get_resource_path("static/favicon/icon.png")
```

## 🐛 除錯

### 啟用除錯模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 常見問題

**插件無法載入**:
- 檢查 `create_plugin()` 函數
- 驗證 `PluginInterface` 實現
- 確認外部工具可用性

**PyInstaller 打包失敗**:
- 檢查 `cli_tool.spec` 配置
- 確認所有資源文件包含
- 使用 `--debug` 模式查看詳細信息

**配置文件錯誤**:
- 驗證 JSON 格式
- 檢查配置鍵的拼寫
- 使用 `test_simple.py` 驗證配置

## 🚀 發布流程

### 版本更新
1. 更新版本號（`setup.py`, `plugin.py`）
2. 更新 `CHANGELOG.md`
3. 運行完整測試
4. 創建 Git 標籤
5. 生成發布包

### Git 工作流
```bash
# 功能開發
git checkout -b feature/new-feature
# ... 開發 ...
git commit -m "feat: add new feature"

# 合併到主分支
git checkout master
git merge feature/new-feature

# 創建版本標籤
git tag -a v2.1.0 -m "Version 2.1.0 release"
```

## 📚 相關資源

- [PyQt5 文檔](https://doc.qt.io/qtforpython/)
- [PyInstaller 指南](https://pyinstaller.readthedocs.io/)
- [Python 插件架構](https://packaging.python.org/guides/creating-and-discovering-plugins/)
- [Semantic Versioning](https://semver.org/)

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 遵循代碼風格
4. 添加測試覆蓋
5. 更新文檔
6. 提交 Pull Request

歡迎提交 Issue 和 Pull Request！