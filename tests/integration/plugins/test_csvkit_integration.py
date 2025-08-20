#!/usr/bin/env python3
"""
csvkit 插件整合測試
測試 csvkit 插件的基本功能和界面整合
"""

import sys
import os
import tempfile
import csv
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent / "../../.."
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from tools.csvkit.csvkit_controller import CsvkitController
from tools.csvkit.csvkit_model import CsvkitModel


def create_sample_csv():
    """創建一個示例 CSV 文件用於測試"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    
    # 寫入示例數據
    sample_data = [
        ['name', 'age', 'city', 'salary'],
        ['Alice', '25', 'New York', '50000'],
        ['Bob', '30', 'Los Angeles', '60000'],
        ['Charlie', '35', 'Chicago', '70000'],
        ['Diana', '28', 'Houston', '55000'],
        ['Eve', '32', 'Phoenix', '65000']
    ]
    
    writer = csv.writer(temp_file)
    writer.writerows(sample_data)
    temp_file.close()
    
    print(f"Created sample CSV file: {temp_file.name}")
    return temp_file.name


def test_csvkit_model():
    """測試 csvkit 模型"""
    print("\n=== Testing csvkit Model ===")
    
    model = CsvkitModel()
    print(f"csvkit available: {model.csvkit_available}")
    print(f"Available tools: {len(model.available_tools)}")
    
    # 顯示工具分類
    categories = model.get_tool_categories()
    for category, tools in categories.items():
        if tools:
            print(f"\n{category}:")
            for tool, description in tools.items():
                print(f"  - {tool}: {description}")
    
    # 測試 csvstat 命令
    if 'csvstat' in model.available_tools:
        csv_file = create_sample_csv()
        try:
            print(f"\n=== Testing csvstat on {csv_file} ===")
            stdout, stderr, returncode = model.execute_csvstat(csv_file)
            print(f"Return code: {returncode}")
            if returncode == 0:
                print("Output:")
                print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
            else:
                print(f"Error: {stderr}")
        finally:
            os.unlink(csv_file)
    
    return model


def test_csvkit_controller():
    """測試 csvkit 控制器和視圖"""
    print("\n=== Testing csvkit Controller and View ===")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    controller = CsvkitController()
    view = controller.get_view()
    
    print(f"Controller created: {controller is not None}")
    print(f"View created: {view is not None}")
    print(f"Model available: {controller.model.csvkit_available}")
    
    # 顯示視圖
    view.show()
    view.resize(1000, 700)
    view.setWindowTitle("csvkit Integration Test")
    
    # 設置定時器在幾秒後關閉應用程序
    def close_app():
        print("Closing application...")
        view.close()
        app.quit()
    
    timer = QTimer()
    timer.singleShot(3000, close_app)  # 3秒後關閉
    
    print("View displayed for 3 seconds...")
    app.exec_()
    
    return controller


def test_plugin_integration():
    """測試插件整合"""
    print("\n=== Testing Plugin Integration ===")
    
    from core.plugin_manager import plugin_manager
    
    # 初始化插件管理器
    plugin_manager.initialize()
    
    # 檢查 csvkit 插件
    plugins = plugin_manager.get_all_plugins()
    
    if 'csvkit' in plugins:
        csvkit_plugin = plugins['csvkit']
        print(f"Plugin found: {csvkit_plugin.name}")
        print(f"Version: {csvkit_plugin.version}")
        print(f"Available: {csvkit_plugin.is_available()}")
        print(f"Required tools: {csvkit_plugin.required_tools}")
        
        # 測試插件創建
        try:
            model = csvkit_plugin.create_model()
            view = csvkit_plugin.create_view()
            controller = csvkit_plugin.create_controller(model, view)
            
            print(f"Model created: {model is not None}")
            print(f"View created: {view is not None}")
            print(f"Controller created: {controller is not None}")
            
            return True
            
        except Exception as e:
            print(f"Error creating plugin components: {e}")
            return False
    else:
        print("csvkit plugin not found")
        return False


def main():
    """主測試函數"""
    print("csvkit Plugin Integration Test")
    print("=" * 50)
    
    # 測試模型
    model = test_csvkit_model()
    
    # 測試插件整合
    plugin_success = test_plugin_integration()
    
    # 測試控制器和視圖（如果可用）
    if model.csvkit_available and plugin_success:
        test_csvkit_controller()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    if model.csvkit_available and plugin_success:
        print("✅ csvkit plugin integration successful!")
        print("✅ All components working correctly")
    else:
        print("❌ Some issues found:")
        if not model.csvkit_available:
            print("  - csvkit not available")
        if not plugin_success:
            print("  - Plugin integration failed")


if __name__ == "__main__":
    main()