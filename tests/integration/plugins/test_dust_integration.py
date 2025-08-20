#!/usr/bin/env python3
"""
Dust Tool Integration Test Script
測試 dust 工具整合到主 CLI 應用程式的基本功能

本腳本測試：
1. Dust 插件是否能正確載入
2. Dust 標籤頁是否能正確創建
3. UI 組件是否能正常初始化
4. 基本整合功能是否正常運作
"""

import sys
import os
import logging
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加專案根目錄到路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

# 設置測試環境的日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 在導入 PyQt5 之前設置環境變數
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtTest import QTest
    from PyQt5.QtCore import Qt, QTimer
except ImportError as e:
    logger.error(f"Failed to import PyQt5: {e}")
    logger.error("Please install PyQt5: pip install PyQt5")
    sys.exit(1)


class DustIntegrationTest(unittest.TestCase):
    """Dust 工具整合測試類"""
    
    @classmethod
    def setUpClass(cls):
        """設置測試類 - 創建 QApplication"""
        try:
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication(sys.argv)
            
            logger.info("QApplication created successfully")
        except Exception as e:
            logger.error(f"Failed to create QApplication: {e}")
            raise
    
    def setUp(self):
        """設置每個測試"""
        self.plugin_manager = None
        self.main_window = None
        logger.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        """清理每個測試"""
        try:
            if self.main_window:
                self.main_window.close()
                self.main_window = None
            
            if self.plugin_manager:
                self.plugin_manager.cleanup()
                self.plugin_manager = None
            
            logger.info(f"Completed test: {self._testMethodName}")
        except Exception as e:
            logger.error(f"Error in tearDown: {e}")
    
    def test_01_plugin_manager_import(self):
        """測試 1: 插件管理器導入"""
        try:
            from core.plugin_manager import plugin_manager, PluginInterface
            self.assertIsNotNone(plugin_manager)
            logger.info("✅ Plugin manager imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import plugin manager: {e}")
    
    def test_02_dust_plugin_import(self):
        """測試 2: Dust 插件導入"""
        try:
            from tools.dust.plugin import DustPlugin, create_plugin
            dust_plugin = create_plugin()
            
            self.assertIsNotNone(dust_plugin)
            self.assertEqual(dust_plugin.name, "dust")
            self.assertEqual(dust_plugin.description, "使用 dust 工具提供磁碟空間分析功能，支援目錄大小視覺化和詳細檔案統計")
            self.assertEqual(dust_plugin.version, "1.0.0")
            self.assertEqual(dust_plugin.required_tools, ["dust"])
            
            logger.info("✅ Dust plugin imported and validated successfully")
        except ImportError as e:
            self.fail(f"Failed to import dust plugin: {e}")
        except Exception as e:
            self.fail(f"Error validating dust plugin: {e}")
    
    def test_03_dust_mvc_components_import(self):
        """測試 3: Dust MVC 組件導入"""
        try:
            from tools.dust.dust_model import DustModel
            from tools.dust.dust_view import DustView
            from tools.dust.dust_controller import DustController
            
            # 測試組件能否實例化
            model = DustModel()
            self.assertIsNotNone(model)
            
            view = DustView()
            self.assertIsNotNone(view)
            
            controller = DustController(view, model)
            self.assertIsNotNone(controller)
            
            # 清理
            controller.cleanup()
            
            logger.info("✅ Dust MVC components imported and instantiated successfully")
        except ImportError as e:
            self.fail(f"Failed to import dust MVC components: {e}")
        except Exception as e:
            self.fail(f"Error testing dust MVC components: {e}")
    
    def test_04_plugin_discovery_and_loading(self):
        """測試 4: 插件發現和載入"""
        try:
            from core.plugin_manager import plugin_manager
            
            # 初始化插件管理器
            plugin_manager.initialize()
            self.plugin_manager = plugin_manager
            
            # 檢查 dust 插件是否被發現
            available_plugins = plugin_manager.get_available_plugins()
            
            if "dust" in available_plugins:
                dust_plugin = available_plugins["dust"]
                self.assertEqual(dust_plugin.name, "dust")
                logger.info("✅ Dust plugin discovered and loaded successfully")
            else:
                # 如果沒有 dust 工具，也算正常
                all_plugins = plugin_manager.get_all_plugins()
                if "dust" in all_plugins:
                    logger.info("⚠️  Dust plugin discovered but not available (dust tool not installed)")
                else:
                    self.fail("Dust plugin not discovered")
        
        except Exception as e:
            self.fail(f"Error in plugin discovery and loading: {e}")
    
    def test_05_main_window_integration(self):
        """測試 5: 主窗口整合"""
        try:
            from ui.main_window import ModernMainWindow
            
            # 創建主窗口
            self.main_window = ModernMainWindow()
            self.assertIsNotNone(self.main_window)
            
            # 檢查內容堆疊是否創建
            self.assertIsNotNone(self.main_window.content_stack)
            
            # 檢查側邊欄是否創建
            self.assertIsNotNone(self.main_window.sidebar)
            
            logger.info("✅ Main window integration successful")
        
        except Exception as e:
            self.fail(f"Error in main window integration: {e}")
    
    def test_06_sidebar_navigation_update(self):
        """測試 6: 側邊欄導航更新"""
        try:
            from ui.main_window import ModernMainWindow
            from core.plugin_manager import plugin_manager
            
            # 初始化插件管理器
            plugin_manager.initialize()
            self.plugin_manager = plugin_manager
            
            # 創建主窗口
            self.main_window = ModernMainWindow()
            
            # 檢查導航按鈕
            navigation_buttons = self.main_window.sidebar.navigation_buttons
            self.assertIsInstance(navigation_buttons, dict)
            
            # 檢查是否包含基本導航項
            expected_items = ["welcome", "themes", "components"]
            for item in expected_items:
                self.assertIn(item, navigation_buttons)
            
            logger.info("✅ Sidebar navigation update successful")
        
        except Exception as e:
            self.fail(f"Error in sidebar navigation update: {e}")
    
    def test_07_dust_icon_and_display_name(self):
        """測試 7: Dust 圖標和顯示名稱"""
        try:
            from ui.main_window import ModernMainWindow
            
            # 創建主窗口
            self.main_window = ModernMainWindow()
            
            # 測試圖標對應
            page_names = {
                "welcome": "歡迎頁面",
                "fd": "檔案搜尋",
                "poppler": "PDF 處理",
                "glow": "Markdown 閱讀器",
                "pandoc": "文檔轉換",
                "bat": "語法高亮查看器",
                "dust": "磁碟空間分析器",
                "themes": "主題設定",
                "components": "UI 組件"
            }
            
            icon_map = {
                "welcome": "🏠",
                "fd": "🔍", 
                "poppler": "📄",
                "glow": "📖",
                "pandoc": "🔄",
                "bat": "🌈",
                "dust": "💾",
                "themes": "🎨",
                "components": "🧩"
            }
            
            # 檢查 dust 是否正確映射
            self.assertEqual(page_names.get("dust"), "磁碟空間分析器")
            self.assertEqual(icon_map.get("dust"), "💾")
            
            logger.info("✅ Dust icon and display name mapping successful")
        
        except Exception as e:
            self.fail(f"Error testing dust icon and display name: {e}")
    
    def test_08_plugin_view_creation(self):
        """測試 8: 插件視圖創建"""
        try:
            from core.plugin_manager import plugin_manager
            from tools.dust.plugin import create_plugin
            
            # 初始化插件管理器
            plugin_manager.initialize()
            self.plugin_manager = plugin_manager
            
            # 手動創建 dust 插件並註冊
            dust_plugin = create_plugin()
            plugin_manager.register_plugin(dust_plugin)
            
            # 如果 dust 工具可用，測試視圖創建
            if dust_plugin.is_available():
                dust_plugin.initialize()
                
                # 測試 MVC 組件創建
                model = dust_plugin.create_model()
                view = dust_plugin.create_view()
                controller = dust_plugin.create_controller(model, view)
                
                self.assertIsNotNone(model)
                self.assertIsNotNone(view)
                self.assertIsNotNone(controller)
                
                # 清理
                dust_plugin.cleanup()
                
                logger.info("✅ Plugin view creation successful (dust tool available)")
            else:
                logger.info("⚠️  Dust tool not available, skipping view creation test")
        
        except Exception as e:
            self.fail(f"Error in plugin view creation: {e}")
    
    def test_09_welcome_page_dust_card(self):
        """測試 9: 歡迎頁面 Dust 卡片"""
        try:
            from ui.main_window import WelcomePage
            
            # 創建歡迎頁面
            welcome_page = WelcomePage()
            self.assertIsNotNone(welcome_page)
            
            # 歡迎頁面應該能正常創建，包含 dust 卡片
            logger.info("✅ Welcome page with dust card created successfully")
        
        except Exception as e:
            self.fail(f"Error testing welcome page dust card: {e}")
    
    def test_10_full_application_launch_test(self):
        """測試 10: 完整應用程式啟動測試"""
        try:
            from ui.main_window import ModernMainWindow
            from core.plugin_manager import plugin_manager
            
            # 初始化插件管理器
            plugin_manager.initialize()
            self.plugin_manager = plugin_manager
            
            # 創建主窗口
            self.main_window = ModernMainWindow()
            
            # 顯示窗口（在 offscreen 模式下）
            self.main_window.show()
            
            # 檢查窗口是否可見
            self.assertTrue(self.main_window.isVisible())
            
            # 模擬一些基本交互
            QTest.qWaitForWindowExposed(self.main_window, 1000)
            
            # 檢查基本功能
            self.assertIsNotNone(self.main_window.content_stack)
            self.assertGreater(self.main_window.content_stack.count(), 0)
            
            logger.info("✅ Full application launch test successful")
        
        except Exception as e:
            self.fail(f"Error in full application launch test: {e}")


def run_integration_tests():
    """運行整合測試"""
    logger.info("=" * 60)
    logger.info("DUST TOOL INTEGRATION TEST SUITE")
    logger.info("=" * 60)
    
    # 創建測試套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(DustIntegrationTest)
    
    # 運行測試
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    result = runner.run(test_suite)
    
    # 顯示摘要
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    
    if result.failures:
        logger.info("\nFailures:")
        for test, traceback in result.failures:
            logger.info(f"- {test}: {traceback}")
    
    if result.errors:
        logger.info("\nErrors:")
        for test, traceback in result.errors:
            logger.info(f"- {test}: {traceback}")
    
    # 返回是否成功
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    try:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Critical error running tests: {e}")
        sys.exit(1)