#!/usr/bin/env python3
"""
測試 ripgrep 核心模組
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# 導入要測試的模組
from tools.ripgrep.core.data_models import SearchParameters, FileResult, SearchMatch, HighlightSpan
from tools.ripgrep.core.result_parser import RipgrepParser, ANSIProcessor
from tools.ripgrep.core.search_engine import RipgrepCommandBuilder


class TestDataModels(unittest.TestCase):
    """測試資料模型"""
    
    def test_search_parameters_creation(self):
        """測試搜尋參數創建"""
        params = SearchParameters(
            pattern="test",
            search_path="/tmp",
            case_sensitive=True,
            context_lines=5
        )
        
        self.assertEqual(params.pattern, "test")
        self.assertEqual(params.search_path, "/tmp")
        self.assertTrue(params.case_sensitive)
        self.assertEqual(params.context_lines, 5)
    
    def test_search_parameters_validation(self):
        """測試搜尋參數驗證"""
        with self.assertRaises(ValueError):
            SearchParameters(pattern="")  # 空模式應該拋出異常
    
    def test_file_result_creation(self):
        """測試檔案結果創建"""
        file_result = FileResult(file_path="/test/file.py")
        
        match = SearchMatch(
            line_number=10,
            column=5,
            content="def test_function():",
            highlights=[HighlightSpan(4, 8)]
        )
        
        file_result.add_match(match)
        
        self.assertEqual(file_result.file_path, "/test/file.py")
        self.assertEqual(file_result.total_matches, 1)
        self.assertEqual(len(file_result.matches), 1)
        self.assertEqual(file_result.matches[0].line_number, 10)


class TestANSIProcessor(unittest.TestCase):
    """測試 ANSI 處理器"""
    
    def test_strip_ansi_codes(self):
        """測試移除 ANSI 顏色碼"""
        colored_text = "\x1b[1;31mmatched\x1b[0m text"
        clean_text = ANSIProcessor.strip_ansi_codes(colored_text)
        self.assertEqual(clean_text, "matched text")
    
    def test_extract_highlights(self):
        """測試提取高亮區域"""
        colored_text = "This is \x1b[1;31mmatched\x1b[0m text"
        clean_text, highlights = ANSIProcessor.extract_highlights(colored_text)
        
        self.assertEqual(clean_text, "This is matched text")
        self.assertEqual(len(highlights), 1)
        self.assertEqual(highlights[0].start, 8)
        self.assertEqual(highlights[0].end, 15)


class TestRipgrepParser(unittest.TestCase):
    """測試 Ripgrep 解析器"""
    
    def setUp(self):
        self.parser = RipgrepParser()
    
    def test_parse_json_output(self):
        """測試 JSON 格式解析"""
        json_output = '''
        {"type":"match","data":{"path":{"text":"test.py"},"lines":{"text":"def test():"},"line_number":1,"submatches":[{"match":{"text":"test"},"start":4,"end":8}]}}
        '''
        
        results = self.parser.parse_output(json_output.strip(), 'json')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_path, "test.py")
        self.assertEqual(len(results[0].matches), 1)
        self.assertEqual(results[0].matches[0].line_number, 1)
        self.assertEqual(results[0].matches[0].content, "def test():")
    
    def test_parse_vimgrep_output(self):
        """測試 vimgrep 格式解析"""
        vimgrep_output = "test.py:1:4:def test():"
        
        results = self.parser.parse_output(vimgrep_output, 'vimgrep')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_path, "test.py")
        self.assertEqual(results[0].matches[0].line_number, 1)
        self.assertEqual(results[0].matches[0].column, 4)


class TestRipgrepCommandBuilder(unittest.TestCase):
    """測試 Ripgrep 命令建構器"""
    
    def setUp(self):
        # Mock ripgrep 可用性檢查
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "ripgrep 13.0.0"
            self.builder = RipgrepCommandBuilder("rg")
    
    def test_build_basic_command(self):
        """測試基本命令建構"""
        params = SearchParameters(pattern="test", search_path=".")
        
        cmd = self.builder.build_command(params)
        
        self.assertEqual(cmd[0], "rg")
        self.assertEqual(cmd[1], "test")
        self.assertEqual(cmd[2], ".")
        self.assertIn("--json", cmd)
        self.assertIn("--ignore-case", cmd)  # 預設不區分大小寫
    
    def test_build_command_with_options(self):
        """測試帶選項的命令建構"""
        params = SearchParameters(
            pattern="test",
            search_path=".",
            case_sensitive=True,
            whole_words=True,
            context_lines=3
        )
        
        cmd = self.builder.build_command(params)
        
        self.assertNotIn("--ignore-case", cmd)  # 區分大小寫
        self.assertIn("--word-regexp", cmd)     # 全詞匹配
        self.assertIn("-C", cmd)                # 上下文
        self.assertIn("3", cmd)                 # 上下文行數


def run_tests():
    """運行所有測試"""
    # 創建測試套件
    test_classes = [
        TestDataModels,
        TestANSIProcessor,
        TestRipgrepParser,
        TestRipgrepCommandBuilder,
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回測試結果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 運行 Ripgrep 核心模組測試...")
    print("=" * 50)
    
    try:
        success = run_tests()
        
        if success:
            print("\n✅ 所有測試通過！")
            print("Ripgrep 核心模組實現正確。")
        else:
            print("\n❌ 部分測試失敗！")
            print("請檢查實現並修復問題。")
            
    except Exception as e:
        print(f"\n💥 測試運行失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("測試完成。")