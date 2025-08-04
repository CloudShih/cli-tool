# CLI Tool Integration

一個基於 PyQt5 的 GUI 應用程式，整合多個命令列工具為統一的圖形界面。

## ✨ 特色功能

- 🔌 **插件式架構** - 模組化設計，易於擴展新工具
- 🎨 **深色主題** - 現代化的深色 UI 界面
- ⚙️ **配置管理** - 統一的配置系統，支援個人化設定
- 📦 **一鍵打包** - 支援 PyInstaller 打包為獨立執行檔
- 🔧 **智能檢測** - 自動檢測外部工具的可用性
- 💾 **狀態記憶** - 記住窗口位置和用戶設定

## 🛠️ 內建工具

### fd - 快速檔案搜尋
- 高效率的檔案和目錄搜尋
- 支援正則表達式和檔案類型篩選
- 隱藏檔案和大小寫敏感搜尋選項

### Pandoc - 萬能文檔轉換器
- **50+ 格式支援** - 支援 Markdown、HTML、PDF、DOCX、EPUB 等格式互轉
- **批量轉換** - 一次處理多個檔案，提升工作效率
- **自訂模板** - 支援自訂 HTML/LaTeX 模板和 CSS 樣式
- **元數據管理** - 設定文檔標題、作者、日期等資訊
- **Standalone 模式** - 生成包含完整樣式的獨立文檔
- **進階選項** - 支援引用處理、數學公式、語法高亮等功能

### Poppler Tools - PDF 處理工具集
- **PDF 資訊** - 查看 PDF 文件詳細資訊
- **文字提取** - 將 PDF 轉換為純文字
- **圖片提取** - 從 PDF 中提取圖片
- **頁面分離** - 將多頁 PDF 分離為單頁文件
- **PDF 合併** - 將多個 PDF 合併為一個文件
- **格式轉換** - PDF 轉 HTML、圖片等格式

## 📋 系統要求

### Python 環境
- Python 3.8 或更高版本
- PyQt5 5.15.0+

### 外部工具

**Pandoc 工具（推薦）**:
- Windows: 從 [Pandoc 官網](https://pandoc.org/installing.html) 下載安裝包
- macOS: `brew install pandoc`
- Linux: `apt-get install pandoc` 或 `yum install pandoc`
- 驗證安裝: `pandoc --version`

**fd 工具（必需）**:
- Windows: 可通過 WinGet 安裝 `winget install sharkdp.fd`
- 或從 [fd releases](https://github.com/sharkdp/fd/releases) 下載

**Poppler 工具（可選）**:
- Windows: 從 [Poppler Windows](https://blog.alivate.com.au/poppler-windows/) 下載
- 包含工具: pdfinfo, pdftotext, pdfimages, pdfseparate, pdfunite, pdftoppm, pdftohtml
- QPDF: 從 [QPDF](https://qpdf.sourceforge.io/) 下載用於 PDF 加密處理

## 🚀 快速開始

### 1. 安裝依賴
```bash
# 基本依賴
pip install -r requirements.txt

# 開發依賴（可選）
pip install -r requirements-dev.txt
```

### 2. 運行應用程式
```bash
# 方法 1: 使用啟動腳本
python run.py

# 方法 2: 直接運行主程式
python main_app.py
```

### 3. 配置外部工具
首次運行時，應用程式會自動檢測外部工具。如果需要手動配置：

編輯 `config/cli_tool_config.json`:
```json
{
  "tools": {
    "fd": {
      "executable_path": "C:\\path\\to\\fd.exe"
    },
    "poppler": {
      "pdfinfo_path": "pdfinfo",
      "pdftotext_path": "pdftotext"
    }
  }
}
```

## 📦 打包為執行檔

### 使用自動化打包腳本
```bash
# 完整建置（推薦）
python build.py

# 調試模式建置
python build.py --debug

# 只清理，不建置
python build.py --clean-only
```

### 手動使用 PyInstaller
```bash
# 使用 spec 文件建置
pyinstaller --clean cli_tool.spec

# 建置單一執行檔
pyinstaller --onefile --windowed main_app.py
```

## 🏗️ 專案結構

```
cli_tool/
├── main_app.py              # 主應用程式
├── run.py                   # 啟動腳本
├── build.py                 # 自動化打包腳本
├── cli_tool.spec            # PyInstaller 配置文件
├── setup.py                 # 套件安裝配置
├── requirements.txt         # 依賴清單
├── requirements-dev.txt     # 開發依賴
├── config/                  # 配置管理
│   ├── config_manager.py
│   └── cli_tool_config.json
├── core/                    # 核心系統
│   └── plugin_manager.py    # 插件管理器
├── tools/                   # 工具插件
│   ├── fd/                  # fd 工具插件
│   │   ├── plugin.py
│   │   ├── fd_model.py
│   │   ├── fd_view.py
│   │   └── fd_controller.py
│   └── poppler/             # Poppler 工具插件
│       ├── plugin.py
│       ├── poppler_model.py
│       ├── poppler_view.py
│       └── poppler_controller.py
├── static/                  # 靜態資源
│   └── favicon/
└── tests/                   # 測試文件
```

## 🔌 插件開發

### 創建新插件

1. 在 `tools/` 目錄下創建新的插件目錄
2. 實現 `PluginInterface` 接口
3. 創建 `plugin.py` 文件提供 `create_plugin()` 函數

```python
from core.plugin_manager import PluginInterface

class MyPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "My awesome tool"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def required_tools(self) -> List[str]:
        return ["my_external_tool"]
    
    def initialize(self) -> bool:
        return True
    
    def create_view(self):
        return MyView()
    
    def create_model(self):
        return MyModel()
    
    def create_controller(self, model, view):
        return MyController(model, view)
    
    def cleanup(self):
        pass

def create_plugin():
    return MyPlugin()
```

## 🧪 測試

```bash
# 運行所有測試
pytest tests/

# 運行特定測試
pytest tests/cli_tool/test_pdf_decryptor.py

# 運行測試並生成覆蓋率報告
pytest --cov=. tests/
```

## 🐛 故障排除

### 常見問題

**插件無法載入**:
- 檢查外部工具是否已安裝並在系統 PATH 中
- 查看日誌輸出獲取詳細錯誤信息

**打包失敗**:
- 確保所有依賴都已安裝
- 檢查 `cli_tool.spec` 文件中的路徑配置
- 嘗試使用 `--debug` 模式獲取更多信息

**GUI 無法顯示**:
- 確認 PyQt5 正確安裝
- 檢查是否缺少系統級的 GUI 依賴

## 📝 開發日誌

查看 `CLAUDE.md` 文件了解詳細的開發指南和架構說明。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

本專案採用 MIT 授權條款。