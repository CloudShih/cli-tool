"""狀態欄控制器"""

from PyQt5.QtWidgets import QLabel
from ui.components.indicators import StatusIndicator, LoadingSpinner


class StatusBarController:
    """管理主窗口狀態欄"""

    def __init__(self, window, sidebar):
        self._status_bar = window.statusBar()
        self.status_label = QLabel("準備就緒")
        self._status_bar.addWidget(self.status_label, 1)

        self.status_spinner = LoadingSpinner(16)
        self._status_bar.addPermanentWidget(self.status_spinner)

        self.status_indicator = StatusIndicator("ready")
        self._status_bar.addPermanentWidget(self.status_indicator)

        self.sidebar = sidebar
        self.set_status("準備就緒", "ready")

    def set_status(self, message: str, status: str = "ready"):
        """更新狀態欄訊息"""
        self.status_label.setText(message)
        self.status_indicator.set_status(status)

        if status == "processing":
            self.status_spinner.start_spinning()
        else:
            self.status_spinner.stop_spinning()

        self.sidebar.set_status(status, message)
