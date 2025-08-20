"""歡迎頁面組件"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QGridLayout
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)


class WelcomePage(QWidget):
    """歡迎頁面組件"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """設置歡迎頁面 UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setProperty("welcome-scroll", True)

        # 滾動內容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # 標題區域
        title_label = QLabel("CLI Tool Integration")
        title_label.setProperty("welcome-title", True)
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)

        # 副標題
        subtitle_label = QLabel("整合多種命令列工具的現代化圖形界面")
        subtitle_label.setProperty("welcome-subtitle", True)
        subtitle_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(subtitle_label)

        content_layout.addSpacing(20)

        # 功能介紹卡片 - 使用網格佈局進行分行排列
        features_container = QWidget()
        features_grid = QGridLayout()
        features_grid.setSpacing(20)
        features_grid.setContentsMargins(20, 0, 20, 0)

        # 創建所有工具卡片
        cards = [
            ("🔍", "檔案搜尋", "使用 fd 工具快速搜尋檔案和目錄，支援正則表達式和各種篩選選項。"),
            ("🔎", "文本搜尋", "使用 Ripgrep 進行高效能文本內容搜尋，支援正則表達式和多種檔案格式。"),
            ("📖", "Markdown 閱讀器", "使用 Glow 工具美觀地預覽 Markdown 文檔，支援本地檔案和遠程 URL，提供多種主題樣式。"),
            ("🔄", "文檔轉換", "使用 Pandoc 萬能轉換器，支援 Markdown、HTML、DOCX 等多種格式互轉，可輸出為 PDF。"),
            ("📄", "PDF 處理", "使用 Poppler 工具集處理 PDF 文件，包括轉換、分割、合併等功能。"),
            ("🌈", "語法高亮查看器", "使用 bat 工具提供語法高亮的文件查看功能，支援多種程式語言和主題樣式。"),
            ("💾", "磁碟空間分析器", "使用 dust 工具提供磁碟空間分析功能，支援目錄大小視覺化和詳細檔案統計。"),
            ("📊", "CSV 數據處理", "使用 csvkit 工具套件處理 CSV 數據，提供格式轉換、數據清理、統計分析等 15 個專業工具。"),
            ("🎨", "主題設定", "豐富的主題選擇，支援深色、淺色和系統主題自動切換。"),
        ]

        for i, (icon, title, description) in enumerate(cards):
            row = i // 3
            col = i % 3
            card = self.create_feature_card(icon, title, description)
            features_grid.addWidget(card, row, col)

        for col in range(3):
            features_grid.setColumnStretch(col, 1)

        total_rows = (len(cards) + 2) // 3
        for row in range(total_rows):
            features_grid.setRowMinimumHeight(row, 180)

        features_grid.setVerticalSpacing(25)
        features_grid.setHorizontalSpacing(20)

        features_container.setLayout(features_grid)
        content_layout.addWidget(features_container)

        content_layout.addSpacing(20)

        info_label = QLabel("請從左側導航選擇要使用的工具")
        info_label.setProperty("welcome-info", True)
        info_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(info_label)

        content_layout.addSpacing(20)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def create_feature_card(self, icon: str, title: str, description: str) -> QFrame:
        """創建功能介紹卡片"""
        card = QFrame()
        card.setProperty("feature-card", True)
        card.setFrameStyle(QFrame.StyledPanel)
        card.setFixedSize(300, 180)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setProperty("feature-icon", True)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("feature-title", True)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setProperty("feature-description", True)
        layout.addWidget(desc_label)

        card.setLayout(layout)
        return card
