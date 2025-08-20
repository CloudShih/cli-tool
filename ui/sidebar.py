"""側邊欄導航組件"""

import logging
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from ui.components.buttons import ModernButton
from ui.components.indicators import StatusIndicator
from ui.animation_effects import animate_widget, AnimatedButton
from core.plugin_manager import plugin_manager

logger = logging.getLogger(__name__)


class NavigationSidebar(QFrame):
    """側邊欄導航組件"""

    navigation_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_selection = "welcome"
        self.navigation_buttons = {}
        self.setup_ui()

    def setup_ui(self):
        """設置側邊欄 UI"""
        self.setProperty("sidebar", True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedWidth(200)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 20)
        main_layout.setSpacing(5)

        app_title = QLabel("CLI Tools")
        app_title.setProperty("sidebar-title", True)
        app_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(app_title)
        main_layout.addSpacing(20)

        self.add_navigation_item(main_layout, "welcome", "🏠", "歡迎頁面", True)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setProperty("sidebar-separator", True)
        main_layout.addWidget(separator)

        tools_label = QLabel("工具")
        tools_label.setProperty("sidebar-section", True)
        main_layout.addWidget(tools_label)

        self.load_plugin_navigation(main_layout)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setProperty("sidebar-separator", True)
        main_layout.addWidget(separator2)

        settings_label = QLabel("設定")
        settings_label.setProperty("sidebar-section", True)
        main_layout.addWidget(settings_label)

        self.add_navigation_item(main_layout, "themes", "🎨", "主題設定")
        self.add_navigation_item(main_layout, "components", "🧩", "UI 組件")

        main_layout.addStretch()

        self.sidebar_status = StatusIndicator("ready")
        main_layout.addWidget(self.sidebar_status)

        self.setLayout(main_layout)

    def add_navigation_item(self, layout: QVBoxLayout, key: str, icon: str, text: str, selected: bool = False):
        """添加導航項目"""
        button = AnimatedButton(f"{icon} {text}")
        button.setProperty("sidebar-nav", True)
        button.setCheckable(True)
        button.setChecked(selected)
        button.clicked.connect(lambda: self.on_navigation_clicked(key))

        QTimer.singleShot(
            len(self.navigation_buttons) * 50,
            lambda: animate_widget(button, 'slide_in', direction='left', duration=300)
        )

        self.navigation_buttons[key] = button
        layout.addWidget(button)

    def load_plugin_navigation(self, main_layout):
        """載入插件導航項目"""
        try:
            plugins = plugin_manager.get_available_plugins()

            tools_index = -1
            for i in range(main_layout.count()):
                item = main_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QLabel) and widget.text() == "工具":
                        tools_index = i
                        break
            if tools_index == -1:
                return

            plugins_to_remove = [
                name for name in self.navigation_buttons
                if name not in ["welcome", "themes", "components"]
            ]
            for plugin_name in plugins_to_remove:
                button = self.navigation_buttons.pop(plugin_name, None)
                if button:
                    main_layout.removeWidget(button)
                    button.deleteLater()

            insert_index = tools_index + 1
            for plugin_name, plugin in plugins.items():
                icon = "🔧"
                if plugin_name == "fd":
                    icon = "🔍"
                elif plugin_name == "ripgrep":
                    icon = "🔎"
                elif plugin_name == "poppler":
                    icon = "📄"
                elif plugin_name == "glow":
                    icon = "📖"
                elif plugin_name == "pandoc":
                    icon = "🔄"
                elif plugin_name == "bat":
                    icon = "🌈"
                elif plugin_name == "dust":
                    icon = "💾"
                elif plugin_name == "csvkit":
                    icon = "📊"

                button = ModernButton(f"{icon} {plugin.name.title()}")
                button.setProperty("sidebar-nav", True)
                button.setCheckable(True)
                button.clicked.connect(lambda checked, key=plugin_name: self.on_navigation_clicked(key))

                self.navigation_buttons[plugin_name] = button
                main_layout.insertWidget(insert_index, button)
                insert_index += 1

                logger.info(f"Added navigation item for plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Error loading plugin navigation: {e}")

    def refresh_plugin_navigation(self):
        """刷新插件導航"""
        self.load_plugin_navigation(self.layout())

    def on_navigation_clicked(self, key: str):
        """處理導航點擊事件"""
        if key != self.current_selection:
            for nav_key, button in self.navigation_buttons.items():
                button.setChecked(nav_key == key)

            self.current_selection = key
            self.navigation_changed.emit(key)
            logger.info(f"Navigation changed to: {key}")

    def set_status(self, status: str, message: str = ""):
        """設置側邊欄狀態"""
        self.sidebar_status.set_status(status, message)
