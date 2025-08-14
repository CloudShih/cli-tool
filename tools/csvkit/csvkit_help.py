"""
csvkit 幫助和使用說明窗口
提供詳細的工具使用指南和範例
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextBrowser, QPushButton, QLabel, QScrollArea,
    QWidget, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CsvkitHelpDialog(QDialog):
    """csvkit 幫助對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("csvkit 使用說明")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """設置界面"""
        layout = QVBoxLayout(self)
        
        # 標題
        title = QLabel("csvkit 工具套件使用說明")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; color: #2c3e50;")
        layout.addWidget(title)
        
        # 標籤頁
        tab_widget = QTabWidget()
        
        # 概述標籤
        overview_tab = self.create_overview_tab()
        tab_widget.addTab(overview_tab, "概述")
        
        # 工具說明標籤
        tools_tab = self.create_tools_tab()
        tab_widget.addTab(tools_tab, "工具說明")
        
        # 使用範例標籤
        examples_tab = self.create_examples_tab()
        tab_widget.addTab(examples_tab, "使用範例")
        
        # 常見問題標籤
        faq_tab = self.create_faq_tab()
        tab_widget.addTab(faq_tab, "常見問題")
        
        layout.addWidget(tab_widget)
        
        # 關閉按鈕
        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.close)
        close_btn.setMinimumHeight(35)
        layout.addWidget(close_btn)
    
    def create_overview_tab(self):
        """創建概述標籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextBrowser()
        content.setHtml("""
        <h2>csvkit 工具套件概述</h2>
        
        <p><b>csvkit</b> 是一套功能強大的 CSV 處理命令行工具，包含 15 個專業工具，能夠滿足各種 CSV 數據處理需求。</p>
        
        <h3>🔧 主要功能分類</h3>
        
        <h4>📥 輸入工具 (Input Tools)</h4>
        <ul>
            <li><b>in2csv</b> - 將各種格式轉換為 CSV</li>
            <li><b>sql2csv</b> - 執行 SQL 查詢並輸出 CSV</li>
        </ul>
        
        <h4>⚙️ 處理工具 (Processing Tools)</h4>
        <ul>
            <li><b>csvclean</b> - 修復 CSV 格式問題</li>
            <li><b>csvcut</b> - 提取和重新排序列</li>
            <li><b>csvgrep</b> - 搜索模式匹配的行</li>
            <li><b>csvjoin</b> - 連接多個 CSV 文件</li>
            <li><b>csvsort</b> - 排序 CSV 數據</li>
            <li><b>csvstack</b> - 堆疊多個 CSV 文件</li>
        </ul>
        
        <h4>📊 輸出分析工具 (Output & Analysis Tools)</h4>
        <ul>
            <li><b>csvformat</b> - 轉換 CSV 格式和方言</li>
            <li><b>csvjson</b> - 轉換為 JSON 格式</li>
            <li><b>csvlook</b> - 格式化表格顯示</li>
            <li><b>csvpy</b> - 載入到 Python 環境</li>
            <li><b>csvsql</b> - SQL 查詢和 DDL 生成</li>
            <li><b>csvstat</b> - 計算描述性統計</li>
        </ul>
        
        <h3>🎯 適用場景</h3>
        <ul>
            <li>數據格式轉換 (Excel, JSON → CSV)</li>
            <li>數據清理和預處理</li>
            <li>數據分析和統計</li>
            <li>報告生成和格式化</li>
            <li>數據整合和合併</li>
        </ul>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_tools_tab(self):
        """創建工具說明標籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextBrowser()
        content.setHtml("""
        <h2>工具詳細說明</h2>
        
        <h3>📥 in2csv - 格式轉換器</h3>
        <p><b>功能</b>：將各種檔案格式轉換為 CSV</p>
        <p><b>支援格式</b>：Excel (xls/xlsx), JSON, DBF, Fixed-width, GeoJSON</p>
        <p><b>使用方法</b>：</p>
        <ol>
            <li>選擇要轉換的檔案</li>
            <li>選擇檔案格式（自動偵測或手動指定）</li>
            <li>對於 Excel 檔案，可指定工作表名稱</li>
            <li>選擇適當的字元編碼</li>
            <li>點擊「Convert to CSV」執行轉換</li>
        </ol>
        
        <h3>✂️ csvcut - 列提取器</h3>
        <p><b>功能</b>：提取和重新排序 CSV 檔案的列</p>
        <p><b>使用方法</b>：</p>
        <ol>
            <li>選擇 CSV 檔案</li>
            <li>在「Columns」欄位輸入要提取的列：
                <ul>
                    <li>使用列號：1,3,5</li>
                    <li>使用列名：name,age,email</li>
                    <li>使用範圍：1-5</li>
                </ul>
            </li>
            <li>勾選「Show column names only」只顯示列名</li>
            <li>點擊「Extract Columns」執行</li>
        </ol>
        
        <h3>🔍 csvgrep - 模式搜索</h3>
        <p><b>功能</b>：在 CSV 檔案中搜索符合條件的行</p>
        <p><b>使用方法</b>：</p>
        <ol>
            <li>選擇 CSV 檔案</li>
            <li>輸入搜索模式（支援正則表達式）</li>
            <li>可指定要搜索的列名或列號</li>
            <li>勾選「Use Regex」啟用正則表達式</li>
            <li>勾選「Invert Match」反向匹配</li>
            <li>點擊「Search」執行搜索</li>
        </ol>
        
        <h3>📊 csvstat - 統計分析</h3>
        <p><b>功能</b>：計算 CSV 檔案的描述性統計</p>
        <p><b>提供信息</b>：</p>
        <ul>
            <li>數據類型和空值檢測</li>
            <li>最大值、最小值、平均值</li>
            <li>標準差和方差</li>
            <li>唯一值數量</li>
            <li>最常見值</li>
        </ul>
        <p><b>使用方法</b>：選擇檔案後直接點擊「Calculate Statistics」</p>
        
        <h3>👁️ csvlook - 表格顯示</h3>
        <p><b>功能</b>：以美觀的表格格式顯示 CSV 內容</p>
        <p><b>選項</b>：</p>
        <ul>
            <li>Max Rows：限制顯示的行數</li>
            <li>Max Columns：限制顯示的列數</li>
        </ul>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_examples_tab(self):
        """創建使用範例標籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextBrowser()
        content.setHtml("""
        <h2>實用範例</h2>
        
        <h3>📝 範例 1：Excel 轉 CSV</h3>
        <p><b>場景</b>：將 Excel 檔案轉換為 CSV 格式</p>
        <p><b>步驟</b>：</p>
        <ol>
            <li>切換到「Input Tools」標籤</li>
            <li>點擊「Browse」選擇 Excel 檔案</li>
            <li>格式選擇「xlsx」或「xls」</li>
            <li>如果是多工作表，輸入工作表名稱</li>
            <li>點擊「Convert to CSV」</li>
        </ol>
        <p><b>結果</b>：在輸出區域顯示轉換後的 CSV 內容</p>
        
        <h3>📊 範例 2：數據統計分析</h3>
        <p><b>場景</b>：分析銷售數據的統計信息</p>
        <p><b>步驟</b>：</p>
        <ol>
            <li>切換到「Output/Analysis」標籤</li>
            <li>在 csvstat 區域選擇 CSV 檔案</li>
            <li>可在「Columns」欄位指定特定列（如：sales,profit）</li>
            <li>點擊「Calculate Statistics」</li>
        </ol>
        <p><b>結果</b>：顯示每列的統計摘要，包括平均值、最大最小值等</p>
        
        <h3>🔍 範例 3：數據搜索過濾</h3>
        <p><b>場景</b>：找出所有包含「北京」的客戶記錄</p>
        <p><b>步驟</b>：</p>
        <ol>
            <li>切換到「Processing」標籤</li>
            <li>在 csvgrep 區域選擇 CSV 檔案</li>
            <li>Pattern 欄位輸入「北京」</li>
            <li>Column 欄位輸入「city」或列號</li>
            <li>點擊「Search」</li>
        </ol>
        <p><b>結果</b>：只顯示城市欄位包含「北京」的行</p>
        
        <h3>✂️ 範例 4：提取特定列</h3>
        <p><b>場景</b>：從客戶資料中只提取姓名、電話、郵箱</p>
        <p><b>步驟</b>：</p>
        <ol>
            <li>切換到「Processing」標籤</li>
            <li>在 csvcut 區域選擇 CSV 檔案</li>
            <li>Columns 欄位輸入「name,phone,email」</li>
            <li>點擊「Extract Columns」</li>
        </ol>
        <p><b>結果</b>：只顯示指定的三個列</p>
        
        <h3>👁️ 範例 5：格式化顯示</h3>
        <p><b>場景</b>：以表格形式預覽大型 CSV 檔案的前 50 行</p>
        <p><b>步驟</b>：</p>
        <ol>
            <li>切換到「Output/Analysis」標籤</li>
            <li>在 csvlook 區域選擇 CSV 檔案</li>
            <li>設定 Max Rows 為 50</li>
            <li>設定 Max Columns 為 10（如果列數很多）</li>
            <li>點擊「Display Table」</li>
        </ol>
        <p><b>結果</b>：顯示美觀的表格格式，方便閱讀</p>
        
        <h3>🔗 工作流程組合範例</h3>
        <p><b>場景</b>：處理銷售數據的完整流程</p>
        <ol>
            <li><b>轉換</b>：使用 in2csv 將 Excel 銷售報表轉為 CSV</li>
            <li><b>過濾</b>：使用 csvgrep 找出銷售額 > 10000 的記錄</li>
            <li><b>提取</b>：使用 csvcut 只保留產品、銷售額、日期列</li>
            <li><b>統計</b>：使用 csvstat 計算銷售額的統計信息</li>
            <li><b>顯示</b>：使用 csvlook 格式化顯示最終結果</li>
        </ol>
        """)
        
        layout.addWidget(content)
        return widget
    
    def create_faq_tab(self):
        """創建常見問題標籤"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = QTextBrowser()
        content.setHtml("""
        <h2>常見問題解答</h2>
        
        <h3>❓ 問題 1：點擊按鈕沒有反應？</h3>
        <p><b>可能原因</b>：</p>
        <ul>
            <li>未選擇輸入檔案</li>
            <li>檔案路徑不存在或無法讀取</li>
            <li>csvkit 工具未正確安裝</li>
        </ul>
        <p><b>解決方法</b>：</p>
        <ol>
            <li>確保已選擇有效的檔案</li>
            <li>檢查檔案權限</li>
            <li>確認 csvkit 已安裝：<code>pip install csvkit</code></li>
        </ol>
        
        <h3>❓ 問題 2：轉換 Excel 檔案失敗？</h3>
        <p><b>可能原因</b>：</p>
        <ul>
            <li>Excel 檔案已加密或損壞</li>
            <li>指定的工作表不存在</li>
            <li>檔案格式不受支援</li>
        </ul>
        <p><b>解決方法</b>：</p>
        <ol>
            <li>確認 Excel 檔案可以正常開啟</li>
            <li>檢查工作表名稱是否正確</li>
            <li>嘗試另存為標準 Excel 格式</li>
        </ol>
        
        <h3>❓ 問題 3：中文字符顯示亂碼？</h3>
        <p><b>解決方法</b>：</p>
        <ul>
            <li>在編碼設定中選擇適當的編碼（如 utf-8, gbk, big5）</li>
            <li>對於舊檔案，嘗試 cp1252 或 iso-8859-1</li>
            <li>可以先用文字編輯器檢查檔案編碼</li>
        </ul>
        
        <h3>❓ 問題 4：記憶體不足或處理緩慢？</h3>
        <p><b>解決方法</b>：</p>
        <ul>
            <li>使用 csvlook 限制顯示行數</li>
            <li>先用 csvcut 提取需要的列</li>
            <li>使用 csvgrep 過濾不必要的行</li>
            <li>分批處理大型檔案</li>
        </ul>
        
        <h3>❓ 問題 5：如何處理包含逗號的數據？</h3>
        <p><b>說明</b>：CSV 格式會自動處理包含逗號的數據</p>
        <ul>
            <li>包含逗號的欄位會被自動加上雙引號</li>
            <li>csvkit 工具會正確解析這些格式</li>
            <li>不需要手動處理逗號問題</li>
        </ul>
        
        <h3>🔧 安裝相關</h3>
        <h4>如何安裝 csvkit？</h4>
        <pre>pip install csvkit</pre>
        
        <h4>如何檢查安裝？</h4>
        <pre>csvstat --version</pre>
        
        <h4>安裝依賴問題？</h4>
        <p>如果遇到依賴問題，嘗試：</p>
        <pre>pip install --upgrade setuptools wheel
pip install csvkit</pre>
        
        <h3>💡 使用技巧</h3>
        <ul>
            <li>使用 csvlook 預覽數據結構</li>
            <li>用 csvstat 了解數據特徵</li>
            <li>組合多個工具達到複雜需求</li>
            <li>保存中間結果以備後續處理</li>
            <li>使用自定義命令執行高級操作</li>
        </ul>
        """)
        
        layout.addWidget(content)
        return widget


def show_csvkit_help(parent=None):
    """顯示 csvkit 幫助對話框"""
    dialog = CsvkitHelpDialog(parent)
    dialog.exec_()