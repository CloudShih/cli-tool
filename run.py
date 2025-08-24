#!/usr/bin/env python3
"""
CLI Tool 應用程式啟動腳本
提供統一的啟動入口點
"""

import sys
import os
from pathlib import Path

from logging_setup import setup_logging
setup_logging()

# 確保專案根目錄在 Python 路徑中
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 設置環境變數
os.environ['PYTHONPATH'] = str(project_root)

def main():
    """主函數"""
    try:
        from main_app import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())