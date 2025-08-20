# csvkit 格式和編碼問題修復

## 🐛 發現的問題

### 1. 編碼錯誤問題
**錯誤現象**：
```
Error: Your file is not "utf-8-sig" encoded. Please specify the correct encoding with the --encoding flag. Use the -v flag to see the complete error.
```

**問題原因**：
- 當格式不選擇 `auto` 時，csvkit 工具要求明確指定編碼
- 原始代碼只在編碼不是 `utf-8` 時才添加 `-e` 參數
- 導致許多情況下編碼參數缺失

### 2. CSV 輸出顯示為 HTML
**錯誤現象**：
- 轉換後的 CSV 內容在界面中顯示為 HTML 格式
- 純文本的 CSV 數據被不必要地轉換成 HTML

**問題原因**：
- `ansi2html.Ansi2HTMLConverter()` 對所有輸出進行 HTML 轉換
- 純 CSV 文本不需要 HTML 轉換，應保持原始格式

## ✅ 修復方案

### 1. 編碼參數修復

**修復位置**：`tools/csvkit/csvkit_model.py:95-96`

**修復前**：
```python
if encoding != 'utf-8':
    command.extend(['-e', encoding])
```

**修復後**：
```python
# 總是明確指定編碼，避免編碼檢測問題
command.extend(['-e', encoding])
```

**修復效果**：
- ✅ 所有情況都明確指定編碼參數
- ✅ 避免 csvkit 工具的編碼檢測失敗
- ✅ 支援任何用戶選擇的編碼格式

### 2. HTML 轉換邏輯優化

**修復位置**：`tools/csvkit/csvkit_controller.py:250-269`

**修復前**：
```python
# 所有輸出都嘗試 HTML 轉換
html_output = ansi2html.Ansi2HTMLConverter().convert(stdout)
self.view.display_result(html_output)
```

**修復後**：
```python
# 檢查是否需要 HTML 轉換
needs_html_conversion = (
    '\x1b[' in stdout or  # ANSI escape sequences
    '│' in stdout or      # Table borders from csvlook
    '─' in stdout or      # Table borders
    '┌' in stdout or      # Table borders
    '└' in stdout         # Table borders
)

if needs_html_conversion:
    html_output = ansi2html.Ansi2HTMLConverter().convert(stdout)
    self.view.display_result(html_output)
else:
    # 對於純 CSV 輸出等，直接使用純文本
    self.view.display_result(stdout)
```

**修復效果**：
- ✅ 純 CSV 數據保持文本格式
- ✅ 表格格式輸出（csvlook）正確轉換為 HTML
- ✅ ANSI 顏色代碼正確處理
- ✅ 改善數據可讀性和可保存性

### 3. 編碼選項擴展

**修復位置**：`tools/csvkit/csvkit_view.py:172-175`

**修復前**：
```python
self.encoding_combo.addItems(['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1'])
```

**修復後**：
```python
self.encoding_combo.addItems([
    'utf-8', 'utf-8-sig', 'cp950', 'big5', 'gbk', 
    'utf-16', 'latin-1', 'cp1252', 'iso-8859-1'
])
```

**修復效果**：
- ✅ 新增 `utf-8-sig`（UTF-8 with BOM）
- ✅ 新增 `cp950`（Windows 繁體中文）
- ✅ 新增 `big5`（繁體中文）
- ✅ 新增 `gbk`（簡體中文）
- ✅ 更好的中文文件支援

## 🧪 測試驗證

### 測試結果
執行 `test_fixes_simple.py`：
```
csvkit Format and Encoding Fix Test
=============================================
Tests passed: 4/4

ALL TESTS PASSED!
```

### 測試覆蓋項目
1. ✅ **命令生成邏輯** - 驗證編碼參數總是被添加
2. ✅ **HTML轉換檢測** - 驗證只在需要時進行HTML轉換
3. ✅ **編碼選項更新** - 確認新增的編碼格式
4. ✅ **檔案類型檢測** - 驗證正確識別不同輸出格式

### 命令生成測試結果
```
1. auto format: in2csv -e utf-8 test.json ✓
2. json format: in2csv -e utf-8 -f json test.json ✓  
3. xlsx format: in2csv -e cp950 -f xlsx test.xlsx ✓
4. with sheet: in2csv -e utf-8-sig -f xlsx --sheet Sheet1 test.xlsx ✓
```

## 🎯 修復效果

### 解決的問題
1. **✅ 編碼錯誤消除**
   - 非 auto 格式不再出現編碼錯誤
   - 所有格式都能正確處理編碼

2. **✅ CSV 輸出格式正確**
   - CSV 數據以純文本格式顯示
   - 不會被錯誤轉換為 HTML 格式

3. **✅ 中文字符支援改善**
   - 支援 CP950、BIG5、GBK 等中文編碼
   - UTF-8-SIG 支援帶 BOM 的文件

4. **✅ 智能格式處理**
   - 表格輸出（csvlook）保持格式化顯示
   - 純數據輸出保持文本格式

### 用戶體驗改善
- 🎨 **更直觀的數據顯示** - CSV 數據以表格形式清晰顯示
- 💾 **更準確的檔案保存** - 保存的檔案格式與顯示格式一致
- 🌏 **更好的國際化支援** - 多種中文編碼選擇
- ⚡ **更穩定的轉換過程** - 減少編碼相關錯誤

## 📊 技術實現詳情

### 編碼處理策略
```python
# 策略：總是明確指定編碼
command = ['in2csv']
command.extend(['-e', encoding])  # 明確編碼參數
if format_type != 'auto':
    command.extend(['-f', format_type])
```

### HTML 轉換決策邏輯
```python
# 智能檢測需要 HTML 轉換的內容
needs_html_conversion = (
    '\x1b[' in stdout or  # ANSI 顏色代碼
    '│' in stdout or      # 表格邊框字符
    '─' in stdout or      # 表格橫線
    '┌' in stdout or      # 表格角落
    '└' in stdout         # 表格角落
)
```

### 支援的編碼格式
| 編碼 | 用途 | 適用場景 |
|------|------|----------|
| `utf-8` | 標準UTF-8 | 現代系統默認 |
| `utf-8-sig` | UTF-8 with BOM | Excel兼容 |
| `cp950` | Windows繁體中文 | 台灣Windows系統 |
| `big5` | 繁體中文 | 傳統繁體中文文件 |
| `gbk` | 簡體中文 | 中國大陸系統 |
| `utf-16` | Unicode雙字節 | 國際化應用 |
| `latin-1` | 西歐字符 | 歐美系統 |

## 🚀 使用建議

### 1. 處理中文檔案
- **Windows 系統**：選擇 `cp950` 編碼
- **跨平台檔案**：選擇 `utf-8` 或 `utf-8-sig`
- **Excel 相容**：選擇 `utf-8-sig`

### 2. 格式轉換最佳實踐
1. 明確選擇輸入格式（不使用 auto）
2. 根據源檔案選擇正確編碼
3. 對於 Excel 檔案，指定工作表名稱
4. 檢查輸出結果的格式正確性

### 3. 故障排除
- 如果仍出現編碼錯誤，嘗試不同的編碼格式
- 對於複雜的檔案結構，查看 csvkit 的詳細錯誤信息
- 確保輸入檔案格式與指定格式匹配

## 📋 修改的檔案

### 核心修復
- `tools/csvkit/csvkit_model.py` - 編碼參數修復
- `tools/csvkit/csvkit_controller.py` - HTML轉換邏輯優化
- `tools/csvkit/csvkit_view.py` - 編碼選項擴展

### 測試檔案
- `test_fixes_simple.py` - 修復驗證測試
- `test_format_encoding_fix.py` - 詳細修復測試
- `format_encoding_fixes.md` - 本修復文檔

## 📈 總結

通過這次修復，csvkit 插件現在能夠：

1. **✅ 穩定處理各種格式**
   - 無論選擇何種格式，都不會出現編碼錯誤
   - 支援 Excel、JSON、DBF 等多種輸入格式

2. **✅ 正確顯示輸出內容**
   - CSV 數據保持純文本格式，便於閱讀和處理
   - 格式化表格正確顯示，保持可讀性

3. **✅ 全面支援中文處理**
   - 多種中文編碼選擇
   - 跨平台中文檔案相容性

4. **✅ 提供更好的用戶體驗**
   - 直觀的數據呈現
   - 準確的檔案保存
   - 穩定的操作流程

所有修復已通過測試驗證，用戶現在可以順利使用 csvkit 的完整功能，無需擔心編碼錯誤或格式顯示問題。

---

**修復完成日期**：2025-08-13  
**版本**：2.1.0  
**狀態**：✅ 完成並通過測試驗證