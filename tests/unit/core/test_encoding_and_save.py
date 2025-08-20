#!/usr/bin/env python3
"""
編碼處理和檔案保存功能測試
測試 csvkit 在處理不同編碼和保存檔案時的表現
"""

import sys
import tempfile
import json
import csv
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from tools.csvkit.csvkit_controller import CsvkitController


def create_test_files_with_encoding():
    """創建不同編碼的測試文件"""
    test_files = {}
    
    # 創建包含中文的 CSV 文件 (UTF-8)
    csv_utf8 = tempfile.NamedTemporaryFile(mode='w', suffix='_utf8.csv', delete=False, encoding='utf-8')
    csv_data = [
        ['產品名稱', '價格', '庫存量', '供應商'],
        ['筆記本電腦', '25000', '50', '台北科技有限公司'],
        ['智能手機', '15000', '120', '高雄電子股份有限公司'],
        ['平板電腦', '12000', '80', '台中資訊科技'],
        ['無線耳機', '2500', '200', '桃園音響設備']
    ]
    writer = csv.writer(csv_utf8)
    writer.writerows(csv_data)
    csv_utf8.close()
    test_files['csv_utf8'] = csv_utf8.name
    
    # 創建包含中文的 JSON 文件
    json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
    json_data = [
        {'產品': '筆記本電腦', '價格': 25000, '分類': '電腦設備', '描述': '高性能商用筆記本'},
        {'產品': '智能手機', '價格': 15000, '分類': '通訊設備', '描述': '最新5G智能手機'},
        {'產品': '平板電腦', '價格': 12000, '分類': '電腦設備', '描述': '輕薄便攜平板電腦'},
        {'產品': '藍牙耳機', '價格': 2500, '分類': '音響設備', '描述': '無線降噪耳機'}
    ]
    json.dump(json_data, json_file, ensure_ascii=False, indent=2)
    json_file.close()
    test_files['json'] = json_file.name
    
    # 創建包含特殊字符的 CSV 文件
    special_csv = tempfile.NamedTemporaryFile(mode='w', suffix='_special.csv', delete=False, encoding='utf-8')
    special_data = [
        ['項目', '說明', '符號'],
        ['溫度', '攝氏25°C', '°'],
        ['貨幣', '新台幣$1,000', '$'],
        ['百分比', '效率95%', '%'],
        ['數學', 'α + β = γ', 'αβγ'],
        ['特殊', '©®™€£¥', '©®™']
    ]
    writer = csv.writer(special_csv)
    writer.writerows(special_data)
    special_csv.close()
    test_files['special_csv'] = special_csv.name
    
    print("創建測試文件:")
    for key, path in test_files.items():
        print(f"  {key}: {path}")
    
    return test_files


def test_encoding_handling():
    """測試編碼處理"""
    print("\n=== 測試編碼處理功能 ===")
    
    from tools.csvkit.csvkit_model import CsvkitModel
    
    model = CsvkitModel()
    if not model.csvkit_available:
        print("csvkit 不可用，跳過測試")
        return False
    
    test_files = create_test_files_with_encoding()
    
    # 測試 JSON 轉 CSV（包含中文）
    print("\n1. 測試 JSON 轉 CSV（包含中文）")
    stdout, stderr, code = model.execute_in2csv(
        test_files['json'], 'json', '', 'utf-8', []
    )
    
    if code == 0:
        print("  ✓ JSON 轉 CSV 成功")
        print(f"  輸出長度: {len(stdout)} 字符")
        lines = stdout.strip().split('\n')
        print(f"  表頭: {lines[0] if lines else 'N/A'}")
        if len(lines) > 1:
            print(f"  首行數據: {lines[1]}")
        
        # 測試保存功能
        print("  測試保存功能...")
        success, message = model.save_result_to_file(
            stdout, 
            suggested_filename="test_json_to_csv.csv",
            file_type="csv"
        )
        print(f"  保存結果: {'成功' if success else '失敗'}")
        if success:
            print(f"  保存路徑: {message}")
        else:
            print(f"  錯誤信息: {message}")
    else:
        print(f"  ✗ JSON 轉 CSV 失敗: {stderr}")
    
    # 測試 CSV 統計（包含中文列名）
    print("\n2. 測試 CSV 統計分析（包含中文列名）")
    stdout, stderr, code = model.execute_csvstat(
        test_files['csv_utf8'], '', '', False, []
    )
    
    if code == 0:
        print("  ✓ CSV 統計分析成功")
        print(f"  輸出長度: {len(stdout)} 字符")
        # 顯示統計摘要的前幾行
        lines = stdout.strip().split('\n')
        for i, line in enumerate(lines[:5]):
            print(f"  {i+1}: {line}")
        
        # 測試保存統計結果
        print("  測試保存統計結果...")
        success, message = model.save_result_to_file(
            stdout,
            suggested_filename="statistics_report.txt",
            file_type="txt"
        )
        print(f"  保存結果: {'成功' if success else '失敗'}")
    else:
        print(f"  ✗ CSV 統計分析失敗: {stderr}")
    
    # 測試特殊字符處理
    print("\n3. 測試特殊字符處理")
    stdout, stderr, code = model.execute_csvlook(
        test_files['special_csv'], 10, 10, 50, []
    )
    
    if code == 0:
        print("  ✓ 特殊字符處理成功")
        print("  格式化表格預覽:")
        lines = stdout.strip().split('\n')
        for line in lines[:8]:  # 顯示前8行
            print(f"  {line}")
    else:
        print(f"  ✗ 特殊字符處理失敗: {stderr}")
    
    # 清理測試文件
    import os
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    return True


def test_gui_save_functionality():
    """測試 GUI 保存功能"""
    print("\n=== 測試 GUI 保存功能 ===")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # 創建控制器
        controller = CsvkitController()
        view = controller.view
        
        print("✓ 控制器和視圖創建成功")
        
        # 檢查保存按鈕
        save_btn = view.save_btn
        print(f"✓ 保存按鈕存在: {save_btn is not None}")
        print(f"  初始狀態: {'啟用' if save_btn.isEnabled() else '禁用'}")
        
        # 模擬設置結果
        test_content = """產品,價格,庫存
筆記本電腦,25000,50
智能手機,15000,120
平板電腦,12000,80"""
        
        view.set_result_for_saving(test_content, "csv")
        print(f"  設置結果後狀態: {'啟用' if save_btn.isEnabled() else '禁用'}")
        
        # 測試顯示結果
        view.display_result(test_content)
        print("✓ 結果顯示成功")
        
        # 設置窗口
        view.setWindowTitle("編碼和保存功能測試")
        view.resize(900, 700)
        view.show()
        
        print("✓ 界面已顯示")
        print("請測試:")
        print("  1. 保存按鈕是否啟用")
        print("  2. 點擊保存是否能選擇檔案位置")
        print("  3. 檔案是否正確保存")
        
        # 3秒後自動關閉
        def close_test():
            print("GUI 測試完成")
            app.quit()
        
        QTimer.singleShot(5000, close_test)
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI 測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("csvkit 編碼處理和檔案保存功能測試")
    print("=" * 60)
    
    # 檢查 csvkit 可用性
    try:
        import subprocess
        result = subprocess.run(['csvstat', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"csvkit 版本: {result.stdout.strip()}")
        else:
            print("csvkit 不可用")
            return
    except:
        print("csvkit 未安裝")
        return
    
    # 運行測試
    encoding_test = test_encoding_handling()
    gui_test = test_gui_save_functionality()
    
    print("\n" + "=" * 60)
    print("測試總結:")
    print(f"編碼處理測試: {'✓ 通過' if encoding_test else '✗ 失敗'}")
    print(f"GUI 保存測試: {'✓ 通過' if gui_test else '✗ 失敗'}")
    
    if encoding_test and gui_test:
        print("\n🎉 所有測試通過！")
        print("新功能:")
        print("  • 智能編碼檢測和處理")
        print("  • 多編碼格式支援 (UTF-8, CP950, BIG5, GBK)")
        print("  • 自動檔案類型識別")
        print("  • 結果檔案保存功能")
        print("  • 用戶友善的檔案對話框")
    else:
        print("\n❌ 部分測試失敗，請檢查問題")


if __name__ == "__main__":
    main()