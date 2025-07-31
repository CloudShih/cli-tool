"""
主題選擇器 - 提供用戶友善的主題切換介面
支援主題預覽、即時切換和配置保存
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QButtonGroup, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPalette, QFont
from ui.theme_manager import theme_manager
import logging

logger = logging.getLogger(__name__)


class ThemePreviewCard(QFrame):
    """主題預覽卡片"""
    
    theme_selected = pyqtSignal(str)  # 發出選中的主題名稱
    
    def __init__(self, theme_id: str, theme_info: dict, parent=None):
        super().__init__(parent)
        self.theme_id = theme_id
        self.theme_info = theme_info
        self.is_selected = False
        self.setup_ui()
        
    def setup_ui(self):
        """設置卡片 UI"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setFixedSize(180, 120)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # 主題名稱
        name_label = QLabel(self.theme_info.get("name", self.theme_id))
        name_label.setAlignment(Qt.AlignCenter)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # 顏色預覽
        color_preview = QFrame()
        color_preview.setFixedHeight(40)
        preview_color = self.theme_info.get("preview_color", "#2e2e2e")
        color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {preview_color};
                border: 1px solid #666666;
                border-radius: 4px;
            }}
        """)
        layout.addWidget(color_preview)
        
        # 主題描述
        desc_label = QLabel(self.theme_info.get("description", ""))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(9)
        desc_label.setFont(desc_font)
        layout.addWidget(desc_label)
        
        self.setLayout(layout)
        self.update_selection_style()
        
    def mousePressEvent(self, event):
        """處理滑鼠點擊事件"""
        if event.button() == Qt.LeftButton:
            self.theme_selected.emit(self.theme_id)
            logger.info(f"Theme preview card clicked: {self.theme_id}")
    
    def set_selected(self, selected: bool):
        """設置選中狀態"""
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_selection_style()
    
    def update_selection_style(self):
        """更新選中狀態的視覺樣式"""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    border: 3px solid #007acc;
                    border-radius: 6px;
                    background-color: rgba(0, 122, 204, 0.1);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #666666;
                    border-radius: 6px;
                    background-color: transparent;
                }
                QFrame:hover {
                    border: 2px solid #888888;
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """)


class ThemeSelector(QWidget):
    """主題選擇器主要組件"""
    
    theme_changed = pyqtSignal(str)  # 主題變更信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_cards = {}
        self.current_theme = theme_manager.get_current_theme()
        self.setup_ui()
        self.load_themes()
        
        # 連接主題管理器信號
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def setup_ui(self):
        """設置主要 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 標題
        title_label = QLabel("選擇主題")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 主題卡片區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(300)
        
        # 主題卡片容器
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(10)
        self.cards_widget.setLayout(self.cards_layout)
        
        scroll_area.setWidget(self.cards_widget)
        layout.addWidget(scroll_area)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("套用主題")
        self.apply_button.setMinimumSize(100, 32)
        self.apply_button.clicked.connect(self.apply_selected_theme)
        button_layout.addWidget(self.apply_button)
        
        self.reset_button = QPushButton("重設為預設")
        self.reset_button.setMinimumSize(100, 32)
        self.reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_themes(self):
        """載入所有可用主題"""
        try:
            available_themes = theme_manager.get_available_themes()
            
            # 清除現有卡片
            for card in self.theme_cards.values():
                card.deleteLater()
            self.theme_cards.clear()
            
            # 創建主題卡片
            row, col = 0, 0
            max_cols = 3  # 每行最多 3 個卡片
            
            for theme_id, theme_info in available_themes.items():
                card = ThemePreviewCard(theme_id, theme_info)
                card.theme_selected.connect(self.on_theme_card_selected)
                
                # 設置當前主題為選中狀態
                if theme_id == self.current_theme:
                    card.set_selected(True)
                
                self.theme_cards[theme_id] = card
                self.cards_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            logger.info(f"Loaded {len(available_themes)} theme cards")
            
        except Exception as e:
            logger.error(f"Error loading themes: {e}")
    
    def on_theme_card_selected(self, theme_id: str):
        """處理主題卡片選擇事件"""
        # 更新所有卡片的選中狀態
        for card_id, card in self.theme_cards.items():
            card.set_selected(card_id == theme_id)
        
        self.current_theme = theme_id
        logger.info(f"Theme card selected: {theme_id}")
    
    def apply_selected_theme(self):
        """套用選中的主題"""
        if self.current_theme:
            success = theme_manager.set_theme(self.current_theme)
            if success:
                self.theme_changed.emit(self.current_theme)
                logger.info(f"Applied theme: {self.current_theme}")
            else:
                logger.error(f"Failed to apply theme: {self.current_theme}")
    
    def reset_to_default(self):
        """重設為預設主題"""
        default_theme = "dark_professional"
        if default_theme in self.theme_cards:
            self.on_theme_card_selected(default_theme)
            self.apply_selected_theme()
    
    def on_theme_changed(self, theme_name: str):
        """處理主題變更事件"""
        self.current_theme = theme_name
        # 更新卡片選中狀態
        for card_id, card in self.theme_cards.items():
            card.set_selected(card_id == theme_name)
    
    def refresh_themes(self):
        """重新載入主題"""
        theme_manager.refresh_themes()
        self.load_themes()