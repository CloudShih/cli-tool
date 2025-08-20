"""插件管理與載入"""

import logging
from PyQt5.QtCore import QTimer
from ui.plugin_loader import PluginLoadingDialog
from core.plugin_manager import plugin_manager

logger = logging.getLogger(__name__)


class PluginHost:
    """負責插件載入與視圖管理"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.plugin_views = {}

    def load_plugins(self):
        """載入插件"""
        try:
            self.main_window.status_bar.set_status("準備載入插件...", "processing")
            loading_dialog = PluginLoadingDialog(plugin_manager, self.main_window)
            loading_dialog.loading_completed.connect(self.on_plugins_loaded)
            QTimer.singleShot(100, loading_dialog.start_loading)
        except Exception as e:
            logger.error(f"Error starting plugin loading: {e}")
            self.main_window.status_bar.set_status(f"插件載入失敗: {e}", "error")
            self.main_window.show_plugin_error(str(e))

    def on_plugins_loaded(self, success: bool, message: str):
        """處理插件載入完成"""
        try:
            if success:
                self.create_plugin_views_in_main_thread()
                self.main_window.sidebar.refresh_plugin_navigation()
                plugin_count = len(self.plugin_views)
                self.main_window.status_bar.set_status(f"已載入 {plugin_count} 個插件", "success")
                logger.info(f"Successfully loaded {plugin_count} plugins")
            else:
                self.main_window.status_bar.set_status(f"插件載入失敗: {message}", "error")
                self.main_window.show_plugin_error(message)
        except Exception as e:
            logger.error(f"Error processing loaded plugins: {e}")
            self.main_window.status_bar.set_status(f"插件處理失敗: {e}", "error")
            self.main_window.show_plugin_error(str(e))

    def create_plugin_views_in_main_thread(self):
        """在主線程中創建插件視圖"""
        try:
            available_plugins = plugin_manager.get_available_plugins()
            for plugin_name, plugin in available_plugins.items():
                try:
                    model = plugin.create_model()
                    view = plugin.create_view()
                    controller = plugin.create_controller(model, view)
                    plugin_manager.plugin_instances[plugin_name] = {
                        'plugin': plugin,
                        'model': model,
                        'view': view,
                        'controller': controller
                    }
                    self.plugin_views[plugin_name] = view
                    self.main_window.content_stack.addWidget(view)
                    logger.info(f"Created plugin view in main thread: {plugin_name}")
                except Exception as e:
                    logger.error(f"Error creating view for plugin {plugin_name}: {e}")

            from ui.theme_selector import ThemeSelector
            theme_selector = ThemeSelector()
            theme_selector.theme_changed.connect(self.main_window.on_theme_changed)
            self.plugin_views["themes"] = theme_selector
            self.main_window.content_stack.addWidget(theme_selector)

            from ui.component_showcase import ComponentShowcase
            showcase = ComponentShowcase()
            self.plugin_views["components"] = showcase
            self.main_window.content_stack.addWidget(showcase)

            logger.info("Added special views (themes, components)")
        except Exception as e:
            logger.error(f"Error creating plugin views in main thread: {e}")

    def refresh_plugins(self):
        """重新整理插件"""
        try:
            self.main_window.status_bar.set_status("重新整理插件中...", "processing")
            if self.main_window.toast_manager:
                self.main_window.toast_manager.show_progress_toast(
                    "🔄 重新整理插件",
                    "正在重新載入插件...",
                    duration=0
                )
            plugin_manager.cleanup()
            self.load_plugins()
        except Exception as e:
            logger.error(f"Error refreshing plugins: {e}")
            self.main_window.status_bar.set_status(f"重新整理失敗: {e}", "error")
            if self.main_window.toast_manager:
                self.main_window.toast_manager.show_progress_toast(
                    "❌ 重新整理失敗",
                    str(e),
                    duration=3000
                )

    def cleanup(self):
        """清理插件"""
        plugin_manager.cleanup()
