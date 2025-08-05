#!/usr/bin/env python3
"""
快取機制和線程數據傳輸問題診斷
"""

import sys
import os
import logging
import threading
import time
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.glow.glow_model import GlowModel
from tools.glow.glow_controller import RenderWorker, CacheWorker
from PyQt5.QtCore import QCoreApplication

# 設置詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_cache_functionality():
    """測試快取功能"""
    print("=" * 60)
    print("測試快取功能")
    print("=" * 60)
    
    try:
        model = GlowModel()
        test_file = "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md"
        
        # 清除快取以確保測試的準確性
        print("清除快取...")
        clear_success, clear_message = model.clear_cache()
        print(f"清除快取結果: {clear_success}, 消息: {clear_message}")
        
        # 獲取初始快取信息
        cache_info_before = model.get_cache_info()
        print(f"初始快取信息: {cache_info_before}")
        
        # 第一次渲染（應該會創建快取）
        print("\n第一次渲染（創建快取）...")
        start_time = time.time()
        success1, html1, error1 = model.render_markdown(
            test_file, "file", "auto", 80, True  # 使用快取
        )
        time1 = time.time() - start_time
        
        print(f"第一次渲染結果:")
        print(f"- 成功: {success1}")
        print(f"- HTML 長度: {len(html1)}")
        print(f"- 時間: {time1:.3f}s")
        print(f"- 錯誤: {error1}")
        
        # 檢查快取信息
        cache_info_after1 = model.get_cache_info()
        print(f"渲染後快取信息: {cache_info_after1}")
        
        # 第二次渲染（應該使用快取）
        print("\n第二次渲染（使用快取）...")
        start_time = time.time()
        success2, html2, error2 = model.render_markdown(
            test_file, "file", "auto", 80, True  # 使用快取
        )
        time2 = time.time() - start_time
        
        print(f"第二次渲染結果:")
        print(f"- 成功: {success2}")
        print(f"- HTML 長度: {len(html2)}")
        print(f"- 時間: {time2:.3f}s")
        print(f"- 錯誤: {error2}")
        print(f"- 內容相同: {html1 == html2}")
        
        # 檢查效能提升
        if time1 > 0 and time2 > 0:
            speedup = time1 / time2
            print(f"快取效能提升: {speedup:.2f}x 倍")
        
        # 第三次渲染（禁用快取）
        print("\n第三次渲染（禁用快取）...")
        start_time = time.time()
        success3, html3, error3 = model.render_markdown(
            test_file, "file", "auto", 80, False  # 不使用快取
        )
        time3 = time.time() - start_time
        
        print(f"第三次渲染結果:")
        print(f"- 成功: {success3}")
        print(f"- HTML 長度: {len(html3)}")
        print(f"- 時間: {time3:.3f}s")
        print(f"- 錯誤: {error3}")
        print(f"- 與快取內容相同: {html1 == html3}")
        
        return True
        
    except Exception as e:
        print(f"快取功能測試失敗: {e}")
        return False

def test_render_worker_thread():
    """測試 RenderWorker 線程數據傳輸"""
    print("\n" + "=" * 60)
    print("測試 RenderWorker 線程數據傳輸")
    print("=" * 60)
    
    try:
        # 創建 Qt 應用程式（線程需要）
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication(sys.argv)
        
        model = GlowModel()
        test_file = "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md"
        
        # 準備渲染參數
        render_params = {
            'source': test_file,
            'source_type': 'file',
            'theme': 'auto',
            'width': 80,
            'use_cache': True
        }
        
        # 用於接收線程結果的變數
        thread_results = {
            'completed': False,
            'success': False,
            'html_content': '',
            'raw_output': '',
            'error_message': ''
        }
        
        def on_render_finished(success, html_content, raw_output, error_message):
            """處理渲染完成信號"""
            print(f"\n[THREAD SIGNAL] 收到渲染完成信號:")
            print(f"- Success: {success}")
            print(f"- HTML length: {len(html_content)}")
            print(f"- HTML type: {type(html_content)}")
            print(f"- Raw output length: {len(raw_output)}")
            print(f"- Error: {error_message}")
            print(f"- HTML contains <html>: {'<html>' in html_content}")
            print(f"- HTML contains <h1>: {'<h1' in html_content}")
            
            # 儲存結果
            thread_results['completed'] = True
            thread_results['success'] = success
            thread_results['html_content'] = html_content
            thread_results['raw_output'] = raw_output
            thread_results['error_message'] = error_message
            
            # 退出事件循環
            app.quit()
        
        # 創建工作線程
        print("創建 RenderWorker 線程...")
        worker = RenderWorker(model, render_params)
        worker.render_finished.connect(on_render_finished)
        
        # 啟動線程
        print("啟動線程...")
        worker.start()
        
        # 運行事件循環等待完成
        print("等待線程完成...")
        app.exec_()
        
        # 檢查結果
        print(f"\n線程執行結果:")
        print(f"- 完成: {thread_results['completed']}")
        print(f"- 成功: {thread_results['success']}")
        print(f"- HTML 長度: {len(thread_results['html_content'])}")
        print(f"- 原始輸出長度: {len(thread_results['raw_output'])}")
        print(f"- 錯誤: {thread_results['error_message']}")
        
        # 等待線程結束
        worker.wait(5000)
        
        if thread_results['completed'] and thread_results['success']:
            print("✅ RenderWorker 線程數據傳輸正常")
            return True
        else:
            print("❌ RenderWorker 線程數據傳輸有問題")
            return False
            
    except Exception as e:
        print(f"RenderWorker 線程測試失敗: {e}")
        return False

def test_cache_worker_thread():
    """測試 CacheWorker 線程數據傳輸"""
    print("\n" + "=" * 60)
    print("測試 CacheWorker 線程數據傳輸")
    print("=" * 60)
    
    try:
        # 創建 Qt 應用程式（線程需要）
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication(sys.argv)
        
        model = GlowModel()
        
        # 用於接收線程結果的變數
        cache_results = {
            'completed': False,
            'success': False,
            'message': '',
            'cache_info': {}
        }
        
        def on_cache_operation_finished(success, message, cache_info):
            """處理快取操作完成信號"""
            print(f"\n[CACHE THREAD SIGNAL] 收到快取操作完成信號:")
            print(f"- Success: {success}")
            print(f"- Message: {message}")
            print(f"- Cache info: {cache_info}")
            
            # 儲存結果
            cache_results['completed'] = True
            cache_results['success'] = success
            cache_results['message'] = message
            cache_results['cache_info'] = cache_info
            
            # 退出事件循環
            app.quit()
        
        # 測試快取信息獲取
        print("創建 CacheWorker 線程（獲取信息）...")
        cache_worker = CacheWorker(model, "info")
        cache_worker.cache_operation_finished.connect(on_cache_operation_finished)
        
        # 啟動線程
        print("啟動快取線程...")
        cache_worker.start()
        
        # 運行事件循環等待完成
        print("等待快取線程完成...")
        app.exec_()
        
        # 檢查結果
        print(f"\n快取線程執行結果:")
        print(f"- 完成: {cache_results['completed']}")
        print(f"- 成功: {cache_results['success']}")
        print(f"- 消息: {cache_results['message']}")
        print(f"- 快取信息: {cache_results['cache_info']}")
        
        # 等待線程結束
        cache_worker.wait(5000)
        
        if cache_results['completed'] and cache_results['success']:
            print("✅ CacheWorker 線程數據傳輸正常")
            return True
        else:
            print("❌ CacheWorker 線程數據傳輸有問題")
            return False
            
    except Exception as e:
        print(f"CacheWorker 線程測試失敗: {e}")
        return False

def test_thread_safety():
    """測試線程安全性"""
    print("\n" + "=" * 60)
    print("測試線程安全性")
    print("=" * 60)
    
    try:
        model = GlowModel()
        test_file = "D:\\ClaudeCode\\projects\\cli_tool\\CHANGELOG.md"
        
        # 多線程同時訪問快取
        results = []
        errors = []
        
        def worker_function(thread_id):
            """工作線程函數"""
            try:
                print(f"線程 {thread_id} 開始...")
                success, html, error = model.render_markdown(
                    test_file, "file", "auto", 80, True
                )
                results.append({
                    'thread_id': thread_id,
                    'success': success,
                    'html_length': len(html),
                    'error': error
                })
                print(f"線程 {thread_id} 完成")
            except Exception as e:
                errors.append(f"線程 {thread_id} 錯誤: {e}")
                print(f"線程 {thread_id} 發生錯誤: {e}")
        
        # 創建多個線程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
        
        # 啟動所有線程
        print("啟動多個線程同時訪問快取...")
        for thread in threads:
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join(timeout=30)
        
        # 檢查結果
        print(f"\n線程安全性測試結果:")
        print(f"- 成功完成的線程: {len(results)}")
        print(f"- 發生錯誤的線程: {len(errors)}")
        
        for result in results:
            print(f"  線程 {result['thread_id']}: 成功={result['success']}, HTML長度={result['html_length']}")
        
        for error in errors:
            print(f"  錯誤: {error}")
        
        if len(errors) == 0 and len(results) == 3:
            print("✅ 線程安全性測試通過")
            return True
        else:
            print("❌ 線程安全性測試有問題")
            return False
            
    except Exception as e:
        print(f"線程安全性測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("快取機制和線程數據傳輸診斷")
    print("時間:", time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # 測試結果
    test_results = []
    
    # 1. 測試快取功能
    cache_result = test_cache_functionality()
    test_results.append(("快取功能", cache_result))
    
    # 2. 測試 RenderWorker 線程
    render_thread_result = test_render_worker_thread()
    test_results.append(("RenderWorker 線程", render_thread_result))
    
    # 3. 測試 CacheWorker 線程
    cache_thread_result = test_cache_worker_thread()
    test_results.append(("CacheWorker 線程", cache_thread_result))
    
    # 4. 測試線程安全性
    thread_safety_result = test_thread_safety()
    test_results.append(("線程安全性", thread_safety_result))
    
    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總體結果: {passed}/{len(test_results)} 測試通過")
    
    if passed == len(test_results):
        print("🎉 所有測試通過！快取機制和線程數據傳輸正常")
    else:
        print("⚠️  有些測試失敗，需要修復相關問題")

if __name__ == "__main__":
    main()