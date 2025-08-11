"""
Comprehensive unit tests for dust_controller.py
Tests for controller initialization, signal connections, thread management,
worker creation, progress reporting, status updates, error handling, and cleanup.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
import time

from tools.dust.dust_controller import DustController, DustAnalysisWorker
from tools.dust.dust_model import DustModel
from tools.dust.dust_view import DustView


class TestDustAnalysisWorker(unittest.TestCase):
    """Test cases for DustAnalysisWorker"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.mock_model = Mock(spec=DustModel)
        self.worker = DustAnalysisWorker(
            model=self.mock_model,
            target_path="/test/path",
            max_depth=3,
            sort_reverse=True,
            number_of_lines=50,
            file_types=None,
            exclude_patterns=None,
            show_apparent_size=False,
            min_size=None,
            full_paths=False,
            files_only=False
        )

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'worker'):
            if self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()
            self.worker.deleteLater()
            self.worker = None

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    def test_worker_initialization(self):
        """Test DustAnalysisWorker initialization"""
        # Assert all parameters are stored correctly
        self.assertEqual(self.worker.target_path, "/test/path")
        self.assertEqual(self.worker.max_depth, 3)
        self.assertTrue(self.worker.sort_reverse)
        self.assertEqual(self.worker.number_of_lines, 50)
        self.assertIsNone(self.worker.file_types)

    def test_worker_signals_exist(self):
        """Test that worker has all required signals"""
        # Assert signals exist
        self.assertTrue(hasattr(self.worker, 'analysis_started'))
        self.assertTrue(hasattr(self.worker, 'analysis_progress'))
        self.assertTrue(hasattr(self.worker, 'analysis_completed'))
        
        # Assert signals are pyqtSignal instances
        self.assertIsInstance(self.worker.analysis_started, pyqtSignal)
        self.assertIsInstance(self.worker.analysis_progress, pyqtSignal)
        self.assertIsInstance(self.worker.analysis_completed, pyqtSignal)

    def test_worker_run_success(self):
        """Test successful worker execution"""
        # Arrange
        self.mock_model.execute_dust_command.return_value = ("test output", "")
        
        # Set up signal monitoring
        started_signals = []
        progress_signals = []
        completed_signals = []
        
        self.worker.analysis_started.connect(lambda: started_signals.append(True))
        self.worker.analysis_progress.connect(lambda msg: progress_signals.append(msg))
        self.worker.analysis_completed.connect(
            lambda output, error, success: completed_signals.append((output, error, success))
        )
        
        # Act
        self.worker.run()
        
        # Assert
        self.assertEqual(len(started_signals), 1)
        self.assertGreater(len(progress_signals), 0)
        self.assertEqual(len(completed_signals), 1)
        
        # Check completed signal
        output, error, success = completed_signals[0]
        self.assertEqual(output, "test output")
        self.assertEqual(error, "")
        self.assertTrue(success)
        
        # Verify model was called correctly
        self.mock_model.execute_dust_command.assert_called_once()

    def test_worker_run_with_error(self):
        """Test worker execution with error"""
        # Arrange
        self.mock_model.execute_dust_command.return_value = ("", "error message")
        
        completed_signals = []
        self.worker.analysis_completed.connect(
            lambda output, error, success: completed_signals.append((output, error, success))
        )
        
        # Act
        self.worker.run()
        
        # Assert
        self.assertEqual(len(completed_signals), 1)
        output, error, success = completed_signals[0]
        self.assertEqual(output, "")
        self.assertEqual(error, "error message")
        self.assertFalse(success)

    def test_worker_run_with_exception(self):
        """Test worker execution with exception"""
        # Arrange
        self.mock_model.execute_dust_command.side_effect = Exception("Test exception")
        
        completed_signals = []
        self.worker.analysis_completed.connect(
            lambda output, error, success: completed_signals.append((output, error, success))
        )
        
        # Act
        self.worker.run()
        
        # Assert
        self.assertEqual(len(completed_signals), 1)
        output, error, success = completed_signals[0]
        self.assertEqual(output, "")
        self.assertIn("分析錯誤", error)
        self.assertIn("Test exception", error)
        self.assertFalse(success)


class TestDustController(unittest.TestCase):
    """Test cases for DustController"""

    @classmethod
    def setUpClass(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create mock view and model
        self.mock_view = Mock(spec=DustView)
        self.mock_model = Mock(spec=DustModel)
        
        # Setup mock view attributes
        self.mock_view.dust_analyze_button = Mock()
        self.mock_view.dust_results_display = Mock()
        self.mock_view.dust_results_display.toPlainText.return_value = ""
        self.mock_view.get_analysis_parameters.return_value = {
            'target_path': '/test/path',
            'max_depth': 3,
            'sort_reverse': True,
            'number_of_lines': 50,
            'file_types': None,
            'exclude_patterns': None,
            'show_apparent_size': False,
            'min_size': None,
            'full_paths': False,
            'files_only': False
        }
        
        # Create controller
        self.controller = DustController(self.mock_view, self.mock_model)

    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'controller'):
            self.controller.cleanup()
            self.controller = None

    @classmethod
    def tearDownClass(cls):
        """Clean up QApplication after all tests"""
        if hasattr(cls, 'app'):
            cls.app.quit()

    def test_controller_initialization(self):
        """Test DustController initialization"""
        # Assert components are stored
        self.assertEqual(self.controller.view, self.mock_view)
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertIsNone(self.controller.analysis_worker)

    def test_signal_connections(self):
        """Test that signals are connected during initialization"""
        # Assert analyze button click is connected
        self.mock_view.dust_analyze_button.clicked.connect.assert_called_once()

    def test_execute_analysis_with_valid_path(self):
        """Test executing analysis with valid path"""
        # Arrange
        self.mock_view.get_analysis_parameters.return_value['target_path'] = '/valid/path'
        
        # Act
        self.controller._execute_analysis()
        
        # Assert
        # Check that view methods were called to set up analysis
        self.mock_view.set_analyze_button_state.assert_called_once_with("分析中...", False)
        self.mock_view.dust_results_display.setPlainText.assert_called_once()
        
        # Check that worker was created
        self.assertIsNotNone(self.controller.analysis_worker)

    def test_execute_analysis_with_empty_path(self):
        """Test executing analysis with empty path"""
        # Arrange
        self.mock_view.get_analysis_parameters.return_value['target_path'] = ''
        
        # Act
        self.controller._execute_analysis()
        
        # Assert
        # Should show error message and set failure state
        self.mock_view.dust_results_display.setPlainText.assert_called_once_with(
            "請指定要分析的目錄路徑。"
        )
        self.mock_view.set_analysis_completed.assert_called_once_with(False, "需要指定路徑")

    def test_execute_analysis_with_running_worker(self):
        """Test executing analysis when another worker is running"""
        # Arrange - create a mock running worker
        old_worker = Mock()
        old_worker.isRunning.return_value = True
        self.controller.analysis_worker = old_worker
        
        self.mock_view.get_analysis_parameters.return_value['target_path'] = '/test/path'
        
        # Act
        self.controller._execute_analysis()
        
        # Assert
        # Should terminate old worker
        old_worker.terminate.assert_called_once()
        old_worker.wait.assert_called_once()
        
        # Should create new worker
        self.assertIsNotNone(self.controller.analysis_worker)
        self.assertNotEqual(self.controller.analysis_worker, old_worker)

    def test_on_analysis_started(self):
        """Test analysis started event handling"""
        # Act
        self.controller._on_analysis_started()
        
        # Assert
        self.mock_view.dust_results_display.setPlainText.assert_called_once_with("🔍 開始分析...\n")

    def test_on_analysis_progress(self):
        """Test analysis progress event handling"""
        # Arrange
        self.mock_view.dust_results_display.toPlainText.return_value = "🔍 開始分析...\n"
        
        # Act
        self.controller._on_analysis_progress("正在掃描目錄...")
        
        # Assert
        # Should update the progress message
        self.mock_view.dust_results_display.setPlainText.assert_called_once()

    def test_on_analysis_completed_with_output(self):
        """Test analysis completed with successful output"""
        # Act
        self.controller._on_analysis_completed("test output", "", True)
        
        # Assert
        # Should clear results and add new content
        self.mock_view.dust_results_display.clear.assert_called_once()
        
        # Should call append multiple times for results
        expected_calls = [
            call("=== 🎯 分析結果 ===\n"),
            call("test output")
        ]
        self.mock_view.dust_results_display.append.assert_has_calls(expected_calls)
        
        # Should set completion state
        self.mock_view.set_analysis_completed.assert_called_once()

    def test_on_analysis_completed_with_error(self):
        """Test analysis completed with error"""
        # Act
        self.controller._on_analysis_completed("", "error message", False)
        
        # Assert
        # Should clear results
        self.mock_view.dust_results_display.clear.assert_called_once()
        
        # Should append error message
        expected_calls = [
            call("\n=== ⚠️ 錯誤訊息 ==="),
            call("error message")
        ]
        self.mock_view.dust_results_display.append.assert_has_calls(expected_calls)

    def test_on_analysis_completed_no_results(self):
        """Test analysis completed with no results"""
        # Act
        self.controller._on_analysis_completed("", "", False)
        
        # Assert
        # Should show no results message
        self.mock_view.dust_results_display.append.assert_called_with(
            "❌ 未找到結果或命令執行失敗。"
        )
        self.mock_view.set_analysis_completed.assert_called_once_with(False, "未找到結果")

    def test_cleanup_with_no_worker(self):
        """Test cleanup when no worker exists"""
        # Arrange
        self.controller.analysis_worker = None
        
        # Act
        self.controller.cleanup()
        
        # Assert - should not raise exception
        self.assertIsNone(self.controller.analysis_worker)

    def test_cleanup_with_running_worker(self):
        """Test cleanup with running worker"""
        # Arrange
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        self.controller.analysis_worker = mock_worker
        
        # Act
        self.controller.cleanup()
        
        # Assert
        mock_worker.terminate.assert_called_once()
        mock_worker.wait.assert_called_once()

    def test_cleanup_with_stopped_worker(self):
        """Test cleanup with stopped worker"""
        # Arrange
        mock_worker = Mock()
        mock_worker.isRunning.return_value = False
        self.controller.analysis_worker = mock_worker
        
        # Act
        self.controller.cleanup()
        
        # Assert - should not terminate if not running
        mock_worker.terminate.assert_not_called()
        mock_worker.wait.assert_not_called()

    def test_worker_signal_connections(self):
        """Test that worker signals are connected properly"""
        # Arrange
        self.mock_view.get_analysis_parameters.return_value['target_path'] = '/test/path'
        
        # Act
        self.controller._execute_analysis()
        
        # Assert that worker was created
        self.assertIsNotNone(self.controller.analysis_worker)
        
        # Worker signals should be connected (tested indirectly through execution)
        worker = self.controller.analysis_worker
        self.assertIsInstance(worker, DustAnalysisWorker)

    def test_parameter_extraction_and_worker_creation(self):
        """Test that parameters are correctly passed to worker"""
        # Arrange
        test_params = {
            'target_path': '/custom/path',
            'max_depth': 5,
            'sort_reverse': False,
            'number_of_lines': 100,
            'file_types': ['txt', 'pdf'],
            'exclude_patterns': ['*.tmp'],
            'show_apparent_size': True,
            'min_size': '1M',
            'full_paths': True,
            'files_only': False
        }
        self.mock_view.get_analysis_parameters.return_value = test_params
        
        # Act
        self.controller._execute_analysis()
        
        # Assert
        worker = self.controller.analysis_worker
        self.assertIsNotNone(worker)
        
        # Check that worker has correct parameters
        self.assertEqual(worker.target_path, '/custom/path')
        self.assertEqual(worker.max_depth, 5)
        self.assertFalse(worker.sort_reverse)
        self.assertEqual(worker.number_of_lines, 100)
        self.assertEqual(worker.file_types, ['txt', 'pdf'])
        self.assertEqual(worker.exclude_patterns, ['*.tmp'])
        self.assertTrue(worker.show_apparent_size)
        self.assertEqual(worker.min_size, '1M')
        self.assertTrue(worker.full_paths)
        self.assertFalse(worker.files_only)

    def test_progress_message_formatting(self):
        """Test progress message formatting with different existing content"""
        # Test with existing progress message
        self.mock_view.dust_results_display.toPlainText.return_value = "🔍 開始分析...\n"
        self.controller._on_analysis_progress("掃描文件...")
        
        # Should replace the last progress line
        self.mock_view.dust_results_display.setPlainText.assert_called_once()
        
        # Test with no existing progress message
        self.mock_view.dust_results_display.reset_mock()
        self.mock_view.dust_results_display.toPlainText.return_value = "Other content\n"
        self.controller._on_analysis_progress("新的進度...")
        
        # Should add new progress line
        self.mock_view.dust_results_display.setPlainText.assert_called_once()

    def test_result_count_calculation(self):
        """Test result count calculation in completion handler"""
        # Test with multi-line output
        test_output = "line1\nline2\nline3\nline4"
        self.controller._on_analysis_completed(test_output, "", True)
        
        # Should calculate result count correctly
        self.mock_view.set_analysis_completed.assert_called_once()
        args = self.mock_view.set_analysis_completed.call_args[0]
        self.assertTrue(args[0])  # success
        self.assertIn("4", args[1])  # should contain count

    def test_multiple_analysis_executions(self):
        """Test multiple analysis executions in sequence"""
        # First execution
        self.mock_view.get_analysis_parameters.return_value['target_path'] = '/path1'
        self.controller._execute_analysis()
        first_worker = self.controller.analysis_worker
        
        # Second execution
        self.mock_view.get_analysis_parameters.return_value['target_path'] = '/path2'
        self.controller._execute_analysis()
        second_worker = self.controller.analysis_worker
        
        # Should create new worker for second execution
        self.assertIsNotNone(first_worker)
        self.assertIsNotNone(second_worker)
        # Workers might be different objects if properly managed


if __name__ == '__main__':
    unittest.main()