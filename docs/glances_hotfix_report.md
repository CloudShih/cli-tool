# Glances 插件緊急修復報告

## 修復日期
2025-08-14

## 問題描述
在實際運行 Glances 插件時，實時圖表功能出現 `TypeError` 錯誤：

```
TypeError: arguments did not match any overloaded call:
  drawLine(self, l: QLineF): argument 1 has unexpected type 'float'
  drawLine(self, line: QLine): argument 1 has unexpected type 'float'
  drawLine(self, x1: int, y1: int, x2: int, y2: int): argument 1 has unexpected type 'float'
```

## 根本原因
PyQt5 的 `QPainter.drawLine()` 方法要求整數座標參數，但程式碼中傳入了浮點數座標。這是因為圖表座標計算時使用了浮點數除法運算。

## 受影響的功能
- 實時圖表繪製
- 網格線顯示
- 座標軸標籤
- 數據線繪製
- 圖例顯示

## 修復內容

### 文件：`tools/glances/charts/real_time_chart.py`

#### 1. 網格線繪製修復
```python
# 修復前
x = self.chart_rect.left() + (self.chart_rect.width() * i / 6)
painter.drawLine(x, self.chart_rect.top(), x, self.chart_rect.bottom())

# 修復後
x = int(self.chart_rect.left() + (self.chart_rect.width() * i / 6))
painter.drawLine(x, self.chart_rect.top(), x, self.chart_rect.bottom())
```

#### 2. 座標軸繪製修復
```python
# 修復前
y_pos = self.chart_rect.bottom() - (self.chart_rect.height() * i / 5)
x_pos = self.chart_rect.left() + (self.chart_rect.width() * i / 5)

# 修復後
y_pos = int(self.chart_rect.bottom() - (self.chart_rect.height() * i / 5))
x_pos = int(self.chart_rect.left() + (self.chart_rect.width() * i / 5))
```

#### 3. 數據線繪製修復
```python
# 修復前
x = self.chart_rect.left() + (self.chart_rect.width() * time_ratio)
y = self.chart_rect.bottom() - (self.chart_rect.height() * value_ratio)

# 修復後
x = int(self.chart_rect.left() + (self.chart_rect.width() * time_ratio))
y = int(self.chart_rect.bottom() - (self.chart_rect.height() * value_ratio))
```

#### 4. 圖例繪製修復
```python
# 修復前
legend_x = self.chart_rect.right() - 150
legend_y = self.chart_rect.top() + 10
y_pos = legend_y + (i * 20)

# 修復後
legend_x = int(self.chart_rect.right() - 150)
legend_y = int(self.chart_rect.top() + 10)
y_pos = int(legend_y + (i * 20))
```

## 修復驗證
- ✅ 圖表組件創建成功
- ✅ 數據系列添加正常
- ✅ 圖表更新無錯誤
- ✅ 繪製方法調用成功

## 影響評估
- **正面影響**：修復了阻礙圖表功能正常運行的關鍵錯誤
- **負面影響**：無，修復只是類型轉換，不影響功能邏輯
- **性能影響**：微不足道，int() 轉換開銷極小

## 測試結果
```
測試圖表繪製修復...
PASS: 圖表繪製修復成功
```

## 建議後續動作
1. **全面測試**：在主應用程式中測試所有圖表功能
2. **回歸測試**：確認修復沒有引入新問題
3. **文檔更新**：更新開發指南，說明 PyQt5 座標要求

## 經驗教訓
- PyQt5 繪圖 API 對參數類型要求嚴格
- 在開發圖形界面時需要注意整數/浮點數類型一致性
- 測試應包含實際 UI 渲染場景

## 修復負責人
Claude Code SuperClaude

## 修復狀態
✅ 已完成並驗證