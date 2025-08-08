"""
Ripgrep 插件包
高效能文本搜尋工具整合
"""

from .plugin import create_plugin

__version__ = "1.0.0"
__author__ = "CLI Tool Integration Team"
__description__ = "Ripgrep 文本搜尋工具插件"

__all__ = ['create_plugin']