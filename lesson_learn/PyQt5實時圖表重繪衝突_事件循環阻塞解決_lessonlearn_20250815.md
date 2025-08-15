# PyQt5實時圖表重繪衝突問題解決 - Lesson Learn

**日期**: 2025-08-15  
**問題類型**: PyQt5 實時數據可視化  
**關鍵字**: 重繪衝突, 事件循環阻塞, 圖表空白, 渲染飢餓  

## 問題描述

### 現象
- **測試版本**: Glances 實時圖表正常顯示數據，圖表線條流暢更新
- **正式版本**: 整合到主應用程式後，圖表顯示空白，雖然數據流正常但無視覺輸出

### 環境差異
- **測試環境**: 獨立運行的簡單應用程式，低負載
- **生產環境**: 插件化架構的複雜應用程式，多組件並行運行

## 根本原因分析

### 技術根因: 「渲染飢餓」現象

通過與 Gemini AI 協作分析發現，問題的本質是 **Qt 事件循環被過度的重繪請求淹沒**：

```python
# 問題代碼 - real_time_chart.py:205-221
def update_series(self, name: str, value: float, timestamp: Optional[float] = None):
    self.series_data[name].add_point(value, timestamp)
    self.update()  # ← 立即重繪觸發器（問題源頭）
```

### 雙重重繪觸發機制
1. **定時器重繪** (正常): 每1000ms觸發 `update()`
2. **數據更新重繪** (問題): 每次數據到達立即觸發 `update()`

### 事件循環衝突機制

#### Gemini 洞察: 異步特性誤解
- `widget.update()` 不是立即繪圖，而是向事件隊列**調度繪圖事件**
- Qt 會嘗試合併同一 widget 的多個繪圖事件
- 高頻調度會導致事件隊列擁塞，形成「渲染飢餓」

#### 精彩比喻 (來自 Gemini)
- **測試環境**: 畫家每15分鐘接到一個肖像請求，輕鬆完成
- **生產環境**: 50個人同時湧入要求立即畫肖像，畫家不斷被打斷，永遠完成不了任何一幅

## 解決方案

### 核心修復: 消除重繪衝突

```python
# 修復後代碼
def update_series(self, name: str, value: float, timestamp: Optional[float] = None):
    """更新數據系列"""
    if name not in self.series_data:
        return
        
    # 只更新數據模型，不觸發立即重繪
    self.series_data[name].add_point(value, timestamp)
    
    # 移除: self.update()  
    # 讓定時器統一處理重繪，避免衝突
```

### 架構原則: 數據與渲染分離

```python
# 推薦架構模式
class RealTimeChart(QWidget):
    def __init__(self):
        # 唯一重繪來源: 定時器
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update)
        self.render_timer.start(33)  # 30 FPS
    
    def update_series(self, name: str, value: float):
        # 只更新數據模型
        self.series_data[name].add_point(value)
        # 讓定時器處理重繪
```

## 驗證過程

### 調試策略: 全流程追蹤
通過在關鍵節點添加調試輸出，確認了：
1. ✅ 數據獲取正常 (GlancesModel)
2. ✅ 數據傳遞正常 (GlancesController) 
3. ✅ 數據處理正常 (Chart組件)
4. ✅ 繪製調用正常 (QPainter)
5. ❌ 視覺效果異常 (過度重繪導致)

### 測試驗證
創建簡化測試程式 `test_silent_chart.py` 驗證修復效果：
- 模擬實時數據更新
- 驗證圖表能正常顯示連續線條
- 確認修復消除了空白問題

## 技術深度分析 (與 Gemini 協作)

### Qt 事件循環機制
1. **事件調度**: `update()` 只調度重繪事件，不立即執行
2. **事件合併**: Qt 嘗試合併相同 widget 的重繪事件
3. **隊列壓力**: 高頻調度可能導致事件隊列擁塞
4. **渲染時機**: 只有在事件循環空閒時才執行實際繪製

### 為什麼測試版本正常？
- **低事件壓力**: 測試環境只有單一組件產生事件
- **簡單事件循環**: 沒有其他插件競爭事件循環資源
- **較少異步操作**: 整體系統負載低

### 為什麼正式版本異常？
- **高事件壓力**: 多插件並行運行，事件循環繁忙
- **資源競爭**: 多個組件同時請求重繪資源
- **系統負載**: 複雜架構增加了事件處理延遲

## 架構改進建議

### 1. 統一渲染管理
```python
class RenderManager:
    """統一管理所有組件的重繪請求"""
    def __init__(self):
        self.render_timer = QTimer()
        self.pending_widgets = set()
        
    def request_render(self, widget):
        self.pending_widgets.add(widget)
        
    def render_all(self):
        for widget in self.pending_widgets:
            widget.update()
        self.pending_widgets.clear()
```

### 2. 性能監控機制
```python
class PerformanceMonitor:
    """監控事件循環性能"""
    def detect_event_congestion(self):
        # 檢測事件隊列擁塞
        # 自動調整重繪頻率
        pass
```

### 3. 自適應幀率控制
```python
class AdaptiveFrameRate:
    """根據系統負載自適應調整幀率"""
    def adjust_fps(self, system_load):
        if system_load > 0.8:
            return 15  # 降低到 15 FPS
        return 30  # 正常 30 FPS
```

## 預防措施

### 代碼審查檢查點
- ❌ 禁止在數據處理方法中直接調用 `update()`
- ✅ 確保每個 widget 只有一個重繪觸發源
- ✅ 使用統一的定時器管理重繪
- ✅ 實施幀率限制防止過度重繪

### 測試策略
- 🧪 **壓力測試**: 模擬高頻數據更新場景
- 🧪 **整合測試**: 在完整應用環境中測試組件
- 🧪 **性能測試**: 監控事件循環響應時間
- 🧪 **並發測試**: 多插件同時運行的測試

### 架構設計原則
1. **數據與渲染分離**: 數據更新不應觸發立即重繪
2. **統一重繪管理**: 使用定時器或統一管理器控制重繪
3. **資源隔離**: 不同插件的重繪操作應該隔離
4. **性能監控**: 實時監控渲染性能並自適應調整

## 經驗總結

### 關鍵學習點
1. **異步特性理解**: Qt 的 `update()` 是異步調度，不是同步執行
2. **事件循環限制**: 高頻事件調度會導致性能問題
3. **測試環境差異**: 簡單測試環境可能隱藏整合問題
4. **架構複雜度**: 複雜應用需要更謹慎的資源管理

### 技術債務識別
- 需要重構其他可能存在類似問題的組件
- 建立統一的性能監控和渲染管理機制
- 改進測試策略以更好地模擬生產環境

### 最佳實踐確立
- 實時數據可視化組件應採用定時器驅動渲染
- 避免在數據處理邏輯中混入渲染調用
- 建立事件循環性能監控機制
- 實施分層的錯誤恢復和降級策略

## 相關資源

- **修復提交**: real_time_chart.py line 220-221
- **測試程式**: test_silent_chart.py
- **技術協作**: Claude Code × Gemini AI 深度分析
- **架構文檔**: pyqt5_redraw_issue_comprehensive_analysis.md

## 後續行動項

1. [ ] 清理其他組件中的類似重繪衝突
2. [ ] 實施統一的渲染管理器
3. [ ] 建立事件循環性能監控
4. [ ] 改進整合測試覆蓋率
5. [ ] 編寫 PyQt5 實時組件開發指南

---

**教訓**: 在複雜的 PyQt5 應用中，看似簡單的重繪調用可能導致嚴重的性能問題。理解 Qt 事件循環的異步特性和資源競爭機制，是開發高質量實時數據可視化應用的關鍵。