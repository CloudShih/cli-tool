from PyQt5.QtWidgets import QApplication
from ui.sidebar import NavigationSidebar


def test_sidebar_navigation_and_status():
    app = QApplication([])
    sidebar = NavigationSidebar()
    results = []
    sidebar.navigation_changed.connect(lambda key: results.append(key))

    sidebar.on_navigation_clicked('themes')
    assert results[-1] == 'themes'

    sidebar.set_status('processing', '處理中')
    assert sidebar.sidebar_status.current_status == 'processing'
