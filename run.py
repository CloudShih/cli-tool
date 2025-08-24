#!/usr/bin/env python3
"""CLI Tool 應用程式啟動腳本。

這個腳本不再修改 ``sys.path`` 或 ``PYTHONPATH``，
取而代之的是依賴於 package 安裝時設定的入口點。
"""

import sys


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