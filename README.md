# CLI Tool Integration

一個基於 PyQt5 的 GUI 應用程式，整合多個命令列工具為統一的圖形界面。

## ✨ 特色功能

- 🔌 **插件式架構** - 模組化設計，易於擴展新工具
- 🎨 **深色主題** - 現代化的深色 UI 界面，支援多種主題選擇
- ⚙️ **配置管理** - 統一的配置系統，支援個人化設定
- 📦 **一鍵打包** - 支援 PyInstaller 打包為獨立執行檔
- 🔧 **智能檢測** - 自動檢測外部工具的可用性
- 💾 **狀態記憶** - 記住窗口位置和用戶設定
- 🎯 **響應式佈局** - 優化的 3x2 網格卡片排列，提升視覺體驗
- 🎭 **動畫效果** - 流暢的頁面切換和載入動畫
- 📱 **插件載入器** - 動態進度顯示，5 個內建工具支援

## 🛠️ 內建工具

### fd - 快速檔案搜尋
- 高效率的檔案和目錄搜尋
- 支援正則表達式和檔案類型篩選
- 隱藏檔案和大小寫敏感搜尋選項

### dust - 磁碟空間分析器
- **視覺化分析** - 直觀的目錄樹狀結構顯示
- **智能解析** - 精確解析 dust 輸出格式，清理樹狀符號
- **多層級檢視** - 支援目錄深度限制和層級縮排顯示
- **檔案類型識別** - 自動識別檔案和目錄類型
- **大小統計** - 顯示檔案和目錄的詳細大小資訊
- **過濾功能** - 支援最小大小過濾和檔案類型篩選

### Glow - Markdown 閱讀器
- **美觀預覽** - 精美的 Markdown 文檔渲染和顯示
- **本地支援** - 支援本地 Markdown 檔案快速載入和預覽
- **遠程 URL** - 直接從 GitHub 等遠程 URL 載入 Markdown 內容
- **多種主題** - 內建多種主題樣式，支援自訂主題配置
- **快取機制** - 智能快取系統，提升重複載入速度
- **響應式設計** - 適應不同螢幕尺寸的最佳閱讀體驗

### Pandoc - 萬能文檔轉換器
- **50+ 格式支援** - 支援 Markdown、HTML、PDF、DOCX、EPUB 等格式互轉
- **批量轉換** - 一次處理多個檔案，提升工作效率
- **自訂模板** - 支援自訂 HTML/LaTeX 模板和 CSS 樣式
- **元數據管理** - 設定文檔標題、作者、日期等資訊
- **Standalone 模式** - 生成包含完整樣式的獨立文檔
- **進階選項** - 支援引用處理、數學公式、語法高亮等功能

### bat - 語法高亮查看器
- **語法高亮** - 支援 200+ 種程式語言的精確語法著色
- **Git 整合** - 顯示 Git 修改標記和差異比較
- **行號顯示** - 可選的行號顯示和 Git 修改指示器
- **主題支援** - 40+ 種內建主題，支援自訂主題配置
- **分頁顯示** - 整合 less 分頁器，適合查看大型檔案
- **快取機制** - 快速檔案載入和語法解析快取系統

### Ripgrep - 高速文本搜尋
- **極速搜尋** - 比 grep 快數倍的正則表達式搜尋
- **智能篩選** - 自動忽略 .gitignore 和二進位檔案
- **多格式輸出** - 支援普通、JSON、統計等多種輸出格式
- **檔案類型** - 支援指定檔案類型和自訂模式
- **上下文顯示** - 顯示搜尋結果的前後文內容
- **Unicode 支援** - 完整的 Unicode 和多語言支援

### csvkit - CSV 資料處理工具套件
- **格式轉換** - 將 Excel、JSON、DBF 等格式轉換為 CSV
- **欄位處理** - 擷取、重新排序和操作 CSV 欄位
- **模式搜尋** - 在 CSV 檔案中進行正則表達式搜尋
- **統計分析** - 計算描述性統計和資料摘要
- **表格顯示** - 格式化表格檢視大型 CSV 檔案
- **資料合併** - 連接和堆疊多個 CSV 檔案
- **繁體中文界面** - 完整的繁體中文本地化支援

### Glances - 系統監控工具
- **系統概覽** - 即時顯示 CPU、記憶體、磁碟使用率和進度條
- **進程監控** - 詳細的進程列表和資源使用情況
- **磁碟空間** - 文件系統使用情況和可用空間分析
- **網路詳情** - 網路介面流量統計和連接狀態
- **原始數據** - 完整的 JSON 格式系統資訊檢視
- **自動監控** - 支援自動啟動和可配置的定期刷新
- **Web 服務器** - 內建 Web 服務器功能，可啟動網頁版 Glances

### Poppler Tools - PDF 處理工具集
- **PDF 資訊** - 查看 PDF 文件詳細資訊
- **文字提取** - 將 PDF 轉換為純文字
- **圖片提取** - 從 PDF 中提取圖片
- **頁面分離** - 將多頁 PDF 分離為單頁文件
- **PDF 合併** - 將多個 PDF 合併為一個文件
- **格式轉換** - PDF 轉 HTML、圖片等格式

### QPDF - 進階 PDF 處理工具
- **PDF 解密** - 解除 PDF 密碼保護，支援用戶密碼和擁有者密碼
- **PDF 加密** - 為 PDF 文件添加密碼保護，支援 40-bit、128-bit、256-bit AES 加密
- **檔案線性化** - 優化 PDF 結構，提升網路載入速度
- **頁面分割** - 將多頁 PDF 分割為單獨檔案，支援自訂檔名模式
- **頁面旋轉** - 旋轉指定頁面或範圍，支援 90°、180°、270° 旋轉
- **檔案壓縮** - 壓縮 PDF 內容，減少檔案大小
- **檔案修復** - 修復損壞的 PDF 文件結構
- **自動副檔名** - 智能添加 .pdf 副檔名，簡化檔案名稱設定

### YT-DLP - 影音下載工具
- **多平台支援** - 支援 YouTube、Bilibili 等 1000+ 影音平台
- **格式選擇** - 自由選擇影片品質和音訊格式
- **批量下載** - 支援多個 URL 的批量下載管理
- **即時進度** - 詳細的下載進度監控和速度顯示
- **下載歷史** - 完整的下載記錄追蹤和管理
- **自動重試** - 智能的下載失敗重試機制
- **檔案管理** - 自動組織下載檔案和目錄結構

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

**dust 工具（推薦）**:
- Windows: `winget install dust3d.dust3d` 或從 [dust releases](https://github.com/bootandy/dust/releases) 下載
- macOS: `brew install dust`
- Linux: `cargo install du-dust` 或下載二進位檔
- 驗證安裝: `dust --version`

**Glow 工具（推薦）**:
- Windows: 從 [Glow Releases](https://github.com/charmbracelet/glow/releases) 下載
- macOS: `brew install glow`
- Linux: `apt-get install glow` 或下載二進位檔
- 驗證安裝: `glow --version`

**bat 工具（推薦）**:
- Windows: `winget install sharkdp.bat` 或從 [bat releases](https://github.com/sharkdp/bat/releases) 下載
- macOS: `brew install bat`
- Linux: `apt-get install bat`
- 驗證安裝: `bat --version`

**Ripgrep 工具（推薦）**:
- Windows: `winget install BurntSushi.ripgrep.MSVC` 或從 [ripgrep releases](https://github.com/BurntSushi/ripgrep/releases) 下載
- macOS: `brew install ripgrep`
- Linux: `apt-get install ripgrep`
- 驗證安裝: `rg --version`

**csvkit 工具（推薦）**:
- 所有平台: `pip install csvkit`
- 包含工具: in2csv, csvcut, csvgrep, csvstat, csvlook, csvjoin, csvstack, csvjson, csvsql 等
- 驗證安裝: `csvstat --version`
- 用途: CSV 資料處理、格式轉換、統計分析

**Glances 工具（推薦）**:
- 所有平台: `pip install glances`
- Windows: 也可從 [Glances releases](https://github.com/nicolargo/glances/releases) 下載
- macOS: `brew install glances`
- Linux: `apt-get install glances` 或 `yum install glances`
- 驗證安裝: `glances --version`
- 用途: 系統監控、進程管理、資源使用分析

**Poppler 工具（可選）**:
- Windows: 從 [Poppler Windows](https://blog.alivate.com.au/poppler-windows/) 下載
- 包含工具: pdfinfo, pdftotext, pdfimages, pdfseparate, pdfunite, pdftoppm, pdftohtml
- QPDF: 從 [QPDF](https://qpdf.sourceforge.io/) 下載用於 PDF 加密處理

**YT-DLP 工具（推薦）**:
- 所有平台: `pip install yt-dlp`
- Windows: `winget install yt-dlp.yt-dlp` 或從 [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases) 下載
- macOS: `brew install yt-dlp`
- Linux: `apt-get install yt-dlp` 或使用 pip 安裝
- 驗證安裝: `yt-dlp --version`
- 用途: YouTube、Bilibili 等 1000+ 平台的影音下載
- 建議同時安裝 FFmpeg 以獲得最佳體驗: `https://ffmpeg.org/download.html`

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
│   ├── csvkit/              # csvkit 工具插件
│   │   ├── plugin.py
│   │   ├── csvkit_model.py
│   │   ├── csvkit_view.py
│   │   ├── csvkit_controller.py
│   │   └── csvkit_help.py
│   ├── poppler/             # Poppler 工具插件
│   │   ├── plugin.py
│   │   ├── poppler_model.py
│   │   ├── poppler_view.py
│   │   └── poppler_controller.py
│   ├── qpdf/                # QPDF PDF 處理插件
│   │   ├── plugin.py
│   │   ├── qpdf_model.py
│   │   ├── qpdf_view.py
│   │   ├── qpdf_controller.py
│   │   └── core/            # 核心模組
│   │       └── data_models.py
│   └── yt_dlp/              # YT-DLP 影音下載插件
│       ├── plugin.py
│       ├── yt_dlp_model.py
│       ├── yt_dlp_view.py
│       ├── yt_dlp_controller.py
│       ├── core/            # 核心模組
│       │   ├── data_models.py
│       │   ├── download_engine.py
│       │   └── async_worker.py
│       ├── components/      # UI 組件
│       │   ├── format_selector.py
│       │   └── progress_display.py
│       └── tests/           # 測試文件
│           └── test_yt_dlp_integration.py
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

## 🎨 最新更新 (v2.7.0)

### 🔧 核心改進
- **QPDF 插件完整實現** - 全新整合的進階 PDF 處理工具 📋
  - 解密功能：支援用戶密碼和擁有者密碼的 PDF 解密
  - 加密功能：40-bit、128-bit、256-bit AES 加密選項
  - 線性化優化：改善 PDF 網路載入效能
  - 智能分割：支援自訂檔名模式的頁面分割功能
  - 頁面旋轉：靈活的角度選擇和頁面範圍設定
  - 檔案壓縮：有效減少 PDF 檔案大小
  - 修復功能：自動修復損壞的 PDF 結構
  - **自動副檔名添加** - 智能檔案名稱處理，使用者只需輸入名稱，系統自動添加 .pdf
- **插件載入進度介面** - 恢復原始載入進度顯示 ⏳
  - 詳細載入卡片：每個插件的載入狀態和描述
  - 實時進度反饋：載入階段和完成狀態追蹤
  - 動畫效果：流暢的載入動畫和狀態轉換
  - 工作線程管理：背景載入不阻塞主界面
  - 錯誤處理：載入失敗時的詳細錯誤資訊
- **QPDF 命令格式修復** - 解決參數格式相容性問題
  - 修復 `--password=value` 格式要求
  - 統一所有 QPDF 參數的格式標準
  - 改善命令建構的穩定性

### 新增功能
- **YT-DLP 影音下載工具** - 全新整合的多平台影音下載工具 🎬
  - 多平台支援：YouTube、Bilibili、Twitter、Facebook、TikTok 等 1000+ 影音平台
  - 智能格式選擇：自動識別最佳品質，支援自訂影片解析度和音訊格式
  - 批量下載管理：多 URL 同時下載，支援佇列管理和優先順序設定
  - 即時進度監控：詳細的下載進度、速度、剩餘時間顯示
  - 完整下載歷史：自動記錄下載記錄，支援搜尋和匯出功能
  - 智能重試機制：網路中斷自動重試，確保下載成功
  - 檔案組織管理：自動建立目錄結構，支援自訂檔名模板
- **Glances 系統監控工具** - 全新整合的系統資源監控工具
  - 系統概覽：即時 CPU、記憶體、負載、磁碟 I/O、網路流量
  - 進程監控：詳細的進程列表和資源使用情況
  - 磁碟空間：文件系統使用情況和可用空間分析
  - 網路詳情：網路介面流量統計和連接狀態
  - 原始數據：完整的 JSON 格式系統資訊檢視
  - Web 服務器：內建 Web 服務器功能，可啟動網頁版 Glances
- **csvkit CSV 處理工具套件** - 全新整合的 CSV 資料處理工具
  - 支援 14 個核心工具：in2csv、csvcut、csvgrep、csvstat 等
  - 多格式輸入：Excel、JSON、DBF 轉 CSV
  - 進階資料處理：欄位擷取、模式搜尋、統計分析
  - 繁體中文界面：完整的本地化支援
- **dust 磁碟空間分析器** - 視覺化磁碟空間分析工具
  - 智能解析 dust 輸出格式，清理樹狀符號
  - 支援多層級檢視和檔案類型識別
- **Ripgrep 文本搜尋** - 高速正則表達式搜尋引擎
  - 極速搜尋性能，比傳統 grep 快數倍
  - 完整的 Unicode 和多語言支援

### UI 優化
- **YT-DLP 下載界面** - 專業的影音下載界面設計 🎬
  - 四大功能標籤：URL 輸入、下載佇列、進度監控、歷史記錄
  - 智能 URL 驗證：即時檢測支援的影音平台和 URL 格式
  - 格式選擇器：視覺化影片品質和音訊格式選擇介面
  - 即時進度顯示：下載速度、檔案大小、剩餘時間詳細資訊
  - 佇列管理系統：拖拽排序、暫停/繼續、批量操作功能
  - 歷史記錄管理：搜尋、篩選、匯出下載記錄功能
- **Glances 監控界面** - 專業的系統監控界面設計
  - 上下分割式佈局：控制面板與詳細監控標籤頁
  - 系統概覽區域：即時進度條顯示 CPU 和記憶體使用率
  - 四大監控標籤：進程監控、磁碟空間、網路詳情、原始數據
  - 自動啟動監控：視圖顯示時自動開始系統監控
  - 暗色主題表格：一致的深色主題設計
- **csvkit 工具界面** - 專業的 CSV 處理界面設計
  - 四大功能標籤：輸入工具、處理工具、輸出/分析、自定義命令
  - 智能檔案類型檢測和編碼處理
  - 增強的輸出顯示區域（75% 垂直空間）
  - 完整繁體中文本地化（界面、工具描述、狀態訊息）
- **響應式佈局** - 優化的分割面板設計
  - 控制面板和輸出面板的最佳比例配置
  - 即時結果保存功能，支援多種格式輸出

### 技術改進
- **QPDF 整合架構** - 穩定的 PDF 處理引擎和命令管理 📋
  - MVC 架構設計：清晰分離的模型、視圖、控制器結構
  - 命令建構器：動態生成最佳化的 QPDF 命令參數
  - 參數格式標準化：統一的 `--parameter=value` 格式
  - 錯誤處理機制：詳細的錯誤訊息和恢復策略
  - 檔案路徑處理：自動副檔名添加和路徑驗證
  - 非同步執行：背景處理避免界面阻塞
- **插件載入優化** - 改善的插件管理和載入體驗 ⏳
  - 雙載入策略：支援快速載入和詳細進度顯示兩種模式
  - 工作線程架構：背景載入不影響主界面響應
  - 進度追蹤系統：每個插件的詳細載入階段監控
  - 動畫系統整合：流暢的視覺反饋和狀態轉換
  - 錯誤恢復機制：載入失敗時的詳細診斷和回退
- **影音下載架構** - 穩定的 YT-DLP 整合和多媒體處理 🎬
  - 非同步下載機制：多線程下載管理，確保 UI 回應性
  - 智能命令建構：動態產生最佳化的 yt-dlp 命令參數
  - 進度解析引擎：即時解析下載進度和統計資訊
  - 錯誤恢復系統：網路中斷自動重試和錯誤處理機制
  - 跨平台相容性：Windows、macOS、Linux 完整支援
- **系統監控架構** - 穩定的 Glances 整合和資料處理
  - 自動監控啟動機制和定期資料刷新
  - 多種資料格式支援：系統概覽、進程、磁碟、網路
  - Web 服務器整合：支援啟動獨立的 Glances Web 界面
- **繁體中文本地化** - 全面的多語言支援
  - 工具類別和描述的完整翻譯
  - 狀態訊息和錯誤提示的本地化
  - 動態內容的繁體中文顯示
- **插件架構優化** - 改善插件載入和管理機制
- **編碼支援** - 強化的 UTF-8 編碼處理和多語言支援

## 📝 開發日誌

查看 `CLAUDE.md` 文件了解詳細的開發指南和架構說明。  
查看 `lesson_learn/` 目錄了解開發過程中的重要經驗總結。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

本專案採用 MIT 授權條款。