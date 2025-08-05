"""
Bat 語法高亮顯示插件
整合 bat 命令行工具提供語法高亮的文件查看功能
"""

__version__ = "1.0.0"
__author__ = "CLI Tool Developer"

# 使插件模組可被導入
from .plugin import BatPlugin, create_plugin

__all__ = ['BatPlugin', 'create_plugin']