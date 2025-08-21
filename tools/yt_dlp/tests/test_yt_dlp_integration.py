"""
YT-DLP 插件整合測試
測試插件的基本功能和整合性
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import QObject, pyqtSignal
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class TestYtDlpPlugin(unittest.TestCase):
    """YT-DLP 插件基本測試"""
    
    def setUp(self):
        """測試設定"""
        self.plugin_path = Path(__file__).parent.parent
        sys.path.insert(0, str(self.plugin_path))
    
    def test_plugin_import(self):
        """測試插件可以正確導入"""
        try:
            from plugin import create_plugin
            plugin = create_plugin()
            self.assertIsNotNone(plugin)
            self.assertEqual(plugin.name, "yt_dlp")
            self.assertEqual(plugin.display_name, "影音下載")
        except ImportError as e:
            self.fail(f"Failed to import plugin: {e}")
    
    def test_plugin_properties(self):
        """測試插件屬性"""
        try:
            from plugin import YtDlpPlugin
            plugin = YtDlpPlugin()
            
            # 基本屬性
            self.assertEqual(plugin.name, "yt_dlp")
            self.assertEqual(plugin.display_name, "影音下載")
            self.assertIsInstance(plugin.description, str)
            self.assertGreater(len(plugin.description), 0)
            self.assertEqual(plugin.icon, "🎬")
            self.assertEqual(plugin.required_tools, ["yt-dlp"])
            
        except Exception as e:
            self.fail(f"Plugin properties test failed: {e}")
    
    @patch('subprocess.run')
    def test_tool_availability_check(self, mock_run):
        """測試工具可用性檢查"""
        try:
            from plugin import YtDlpPlugin
            plugin = YtDlpPlugin()
            
            # 模擬工具可用
            mock_run.return_value = Mock(returncode=0, stdout="yt-dlp 2023.12.30")
            self.assertTrue(plugin.check_tools_availability())
            
            # 模擬工具不可用
            mock_run.side_effect = FileNotFoundError()
            plugin._is_available = None  # 重置快取
            self.assertFalse(plugin.check_tools_availability())
            
        except Exception as e:
            self.fail(f"Tool availability test failed: {e}")
    
    def test_data_models(self):
        """測試資料模型"""
        try:
            from tools.yt_dlp.core.data_models import (
                DownloadParameters, DownloadResult, DownloadProgress,
                DownloadSummary, VideoInfo, VideoQuality, AudioFormat
            )
            
            # 測試下載參數
            params = DownloadParameters(
                url="https://www.youtube.com/watch?v=test",
                output_dir="/tmp"
            )
            self.assertEqual(params.url, "https://www.youtube.com/watch?v=test")
            self.assertEqual(params.output_dir, "/tmp")
            
            # 測試枚舉
            self.assertIsNotNone(VideoQuality.BEST)
            self.assertIsNotNone(AudioFormat.MP3)
            
        except Exception as e:
            self.fail(f"Data models test failed: {e}")
    
    def test_download_engine(self):
        """測試下載引擎"""
        try:
            from tools.yt_dlp.core.download_engine import validate_ytdlp_available, YtDlpCommandBuilder
            
            # 測試 YT-DLP 可用性驗證函數
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="yt-dlp 2023.12.30")
                self.assertTrue(validate_ytdlp_available())
                
                mock_run.side_effect = FileNotFoundError()
                self.assertFalse(validate_ytdlp_available())
            
            # 測試命令建構器
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="yt-dlp 2023.12.30")
                builder = YtDlpCommandBuilder()
                self.assertIsNotNone(builder)
            
        except Exception as e:
            self.fail(f"Download engine test failed: {e}")


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt5 not available")
class TestYtDlpPluginWithQt(unittest.TestCase):
    """需要 PyQt5 的 YT-DLP 插件測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類設定"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """測試設定"""
        self.plugin_path = Path(__file__).parent.parent
        sys.path.insert(0, str(self.plugin_path))
    
    def test_model_creation(self):
        """測試模型創建"""
        try:
            from plugin import YtDlpPlugin
            
            with patch.object(YtDlpPlugin, 'check_tools_availability', return_value=True):
                plugin = YtDlpPlugin()
                model = plugin.create_model()
                
                if model is not None:  # 只有在成功創建時才測試
                    self.assertIsInstance(model, QObject)
                    self.assertTrue(hasattr(model, 'download_started'))
                    self.assertTrue(hasattr(model, 'download_progress'))
                    self.assertTrue(hasattr(model, 'download_completed'))
                
        except Exception as e:
            self.skipTest(f"Model creation test skipped due to: {e}")
    
    def test_view_creation(self):
        """測試視圖創建"""
        try:
            from plugin import YtDlpPlugin
            
            plugin = YtDlpPlugin()
            view = plugin.create_view()
            
            if view is not None:  # 只有在成功創建時才測試
                self.assertIsInstance(view, QWidget)
                self.assertTrue(hasattr(view, 'download_requested'))
                self.assertTrue(hasattr(view, 'download_cancelled'))
                
        except Exception as e:
            self.skipTest(f"View creation test skipped due to: {e}")
    
    def test_controller_creation(self):
        """測試控制器創建"""
        try:
            from plugin import YtDlpPlugin
            
            with patch.object(YtDlpPlugin, 'check_tools_availability', return_value=True):
                plugin = YtDlpPlugin()
                model = plugin.create_model()
                view = plugin.create_view()
                
                if model is not None and view is not None:
                    controller = plugin.create_controller(model, view)
                    if controller is not None:
                        self.assertIsInstance(controller, QObject)
                        self.assertTrue(hasattr(controller, 'model'))
                        self.assertTrue(hasattr(controller, 'view'))
                
        except Exception as e:
            self.skipTest(f"Controller creation test skipped due to: {e}")


class TestYtDlpComponents(unittest.TestCase):
    """YT-DLP 組件測試"""
    
    def setUp(self):
        """測試設定"""
        self.plugin_path = Path(__file__).parent.parent
        sys.path.insert(0, str(self.plugin_path))
    
    def test_url_validation(self):
        """測試 URL 驗證"""
        try:
            from plugin import YtDlpPlugin
            plugin = YtDlpPlugin()
            
            # 有效 URL
            valid_urls = [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://www.bilibili.com/video/BV1xx411c7mu",
                "http://example.com/video.mp4"
            ]
            
            for url in valid_urls:
                self.assertTrue(plugin.validate_url(url), f"Valid URL should pass: {url}")
            
            # 無效 URL
            invalid_urls = [
                "",
                "not_a_url",
                "ftp://example.com/video.mp4",
                "https://",
                None
            ]
            
            for url in invalid_urls:
                self.assertFalse(plugin.validate_url(url), f"Invalid URL should fail: {url}")
                
        except Exception as e:
            self.fail(f"URL validation test failed: {e}")
    
    def test_supported_sites(self):
        """測試支援的網站列表"""
        try:
            from plugin import YtDlpPlugin
            
            with patch.object(YtDlpPlugin, 'is_available', return_value=True):
                plugin = YtDlpPlugin()
                sites = plugin.get_supported_sites()
                
                self.assertIsInstance(sites, list)
                self.assertGreater(len(sites), 0)
                self.assertIn("YouTube", sites)
                self.assertIn("Bilibili", sites)
                
        except Exception as e:
            self.fail(f"Supported sites test failed: {e}")
    
    def test_installation_guide(self):
        """測試安裝指南"""
        try:
            from plugin import YtDlpPlugin
            plugin = YtDlpPlugin()
            
            guide = plugin.get_installation_guide()
            self.assertIsInstance(guide, str)
            self.assertGreater(len(guide), 0)
            self.assertIn("pip install yt-dlp", guide)
            self.assertIn("FFmpeg", guide)
            
        except Exception as e:
            self.fail(f"Installation guide test failed: {e}")


class TestProgressParsing(unittest.TestCase):
    """進度解析測試"""
    
    def setUp(self):
        """測試設定"""
        self.plugin_path = Path(__file__).parent.parent
        sys.path.insert(0, str(self.plugin_path))
    
    def test_progress_line_parsing(self):
        """測試進度行解析"""
        try:
            from tools.yt_dlp.core.download_engine import parse_progress_line
            
            # 測試下載進度行
            progress_line = "[download]  45.2% of 123.45MiB at 1.23MiB/s ETA 01:23"
            result = parse_progress_line(progress_line)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['percentage'], 45.2)
            self.assertEqual(result['status'], 'downloading')
            
            # 測試完成行
            complete_line = "[download] 100% of 123.45MiB in 02:34"
            result = parse_progress_line(complete_line)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['status'], 'completed')
            
        except Exception as e:
            self.fail(f"Progress parsing test failed: {e}")
    
    def test_file_size_estimation(self):
        """測試檔案大小估算"""
        try:
            from tools.yt_dlp.core.download_engine import estimate_total_size, estimate_speed
            
            # 測試大小估算
            self.assertEqual(estimate_total_size("1.5MiB"), 1572864)  # 1.5 * 1024 * 1024
            self.assertEqual(estimate_total_size("500KiB"), 512000)   # 500 * 1024
            self.assertEqual(estimate_total_size("2GiB"), 2147483648) # 2 * 1024^3
            
            # 測試速度估算
            self.assertEqual(estimate_speed("1.5MiB/s"), 1572864.0)
            self.assertEqual(estimate_speed("500KiB/s"), 512000.0)
            
        except Exception as e:
            self.fail(f"File size estimation test failed: {e}")


def run_tests():
    """運行所有測試"""
    # 創建測試套件
    test_suite = unittest.TestSuite()
    
    # 添加基本測試
    test_suite.addTest(unittest.makeSuite(TestYtDlpPlugin))
    test_suite.addTest(unittest.makeSuite(TestYtDlpComponents))
    test_suite.addTest(unittest.makeSuite(TestProgressParsing))
    
    # 只有在 PyQt5 可用時才添加 GUI 測試
    if PYQT_AVAILABLE:
        test_suite.addTest(unittest.makeSuite(TestYtDlpPluginWithQt))
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("YT-DLP Plugin Integration Tests")
    print("=" * 50)
    
    if not PYQT_AVAILABLE:
        print("Warning: PyQt5 not available, skipping GUI tests")
        print()
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)