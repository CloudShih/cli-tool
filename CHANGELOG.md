# Changelog

All notable changes to CLI Tool project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-31

### 🎉 Major Release - 架構全面優化

這是一個重大版本更新，將 CLI Tool 從簡單的工具集合轉變為專業級桌面應用框架。

### Added

#### 🔧 配置管理系統
- 新增統一的配置管理器 (`config/config_manager.py`)
- 支援 JSON 配置文件 (`config/cli_tool_config.json`)
- 智能路徑處理，支援開發和 PyInstaller 打包環境
- 配置持久化和用戶設定記憶

#### 🔌 插件式架構
- 實現插件接口基類 (`core/plugin_manager.py`)
- 自動插件發現和載入機制
- 工具可用性智能檢測
- 插件生命週期管理

#### 📦 打包和部署系統
- 完整的 PyInstaller 配置 (`cli_tool.spec`)
- 自動化打包腳本 (`build.py`)
- 依賴管理 (`requirements.txt`, `requirements-dev.txt`)
- 安裝配置 (`setup.py`)

#### 🎨 用戶體驗增強
- 智能錯誤提示和處理
- 窗口狀態記憶功能
- 插件狀態檢測和反饋
- 完整的日誌記錄系統

#### 🧪 測試和驗證
- 優化驗證腳本 (`test_optimizations.py`, `test_simple.py`)
- 應用程式功能測試 (`test_app.py`)
- 單元測試擴展

#### 📖 完整文檔體系
- 詳細的 README.md 和使用指南
- 插件開發文檔
- CLAUDE.md 開發指南
- 版本記錄 (CHANGELOG.md)

### Changed

#### 🏗️ 架構重構
- 將 fd 和 poppler 工具重構為插件
- 統一使用絕對匯入，修復 PyInstaller 兼容性
- 主應用程式採用插件驅動架構

#### 🔄 代碼改進
- 外部工具路徑配置化
- 錯誤處理機制標準化
- 資源管理最佳化

### Fixed

#### 🐛 Bug 修復
- 修復相對匯入導致的 PyInstaller 打包問題
- 修復硬編碼路徑問題
- 修復缺少依賴管理的問題

### Technical Details

#### 📁 新增文件結構
```
├── config/                  # 配置管理系統
│   ├── config_manager.py
│   └── cli_tool_config.json
├── core/                    # 核心框架
│   └── plugin_manager.py
├── tools/                   # 工具插件
│   ├── fd/plugin.py
│   └── poppler/plugin.py
├── build.py                 # 自動化打包
├── cli_tool.spec           # PyInstaller 配置
├── run.py                  # 統一啟動入口
└── test_*.py               # 測試腳本
```

#### 🔧 技術改進
- **插件接口**: 標準化的 `PluginInterface` 基類
- **配置系統**: 支援開發/生產環境的智能配置管理
- **資源處理**: `get_resource_path()` 統一資源路徑處理
- **錯誤處理**: 全域錯誤捕獲和用戶友好提示

#### 📊 品質指標
- **測試覆蓋**: 6/6 測試項目全部通過
- **代碼質量**: 從腳本級提升到框架級
- **文檔完整性**: 包含開發、使用和部署文檔
- **可維護性**: 模組化設計，易於擴展和修改

### Migration Guide

#### 從 v1.x 升級到 v2.0
1. **配置遷移**: 舊的硬編碼設定需遷移到 `config/cli_tool_config.json`
2. **啟動方式**: 建議使用 `python run.py` 作為統一入口
3. **依賴安裝**: 執行 `pip install -r requirements.txt`
4. **功能驗證**: 運行 `python test_simple.py` 驗證升級結果

#### 開發者注意事項
- 所有匯入改為絕對匯入
- 插件開發需實現 `PluginInterface`
- 配置訪問統一使用 `config_manager`

---

## [1.0.0] - Initial Release

### Added
- 基本的 fd 文件搜尋功能
- Poppler PDF 處理工具整合
- PyQt5 圖形界面
- 基本的 MVC 架構