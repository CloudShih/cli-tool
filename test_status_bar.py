from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.sidebar import NavigationSidebar
from ui.status_bar import StatusBarController


def test_status_bar_updates_sidebar():
    app = QApplication([])
    window = QMainWindow()
    sidebar = NavigationSidebar()
    status = StatusBarController(window, sidebar)
    status.set_status('測試狀態', 'processing')

    assert status.status_label.text() == '測試狀態'
    assert status.status_indicator.current_status == 'processing'
    assert sidebar.sidebar_status.current_status == 'processing'
