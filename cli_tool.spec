# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for CLI Tool
Based on lesson learn best practices for relative import fixes
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path('.').resolve()

block_cipher = None

a = Analysis(
    ['main_app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include configuration files
        ('config/cli_tool_config.json', 'config'),
        # Include static assets (icons, etc.)
        ('static', 'static'),
    ],
    hiddenimports=[
        # PyQt5 modules
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        
        # Application modules - absolute imports
        'config',
        'config.config_manager',
        'tools',
        'tools.fd',
        'tools.fd.fd_model',
        'tools.fd.fd_view', 
        'tools.fd.fd_controller',
        'tools.poppler',
        'tools.poppler.poppler_model',
        'tools.poppler.poppler_view',
        'tools.poppler.poppler_controller',
        
        # PDF processing dependencies
        'pikepdf',
        'ansi2html',
        
        # Standard library modules that might be missed
        'json',
        'logging',
        'subprocess',
        'pathlib',
        'tempfile',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
        # Documentation and testing modules
        'sphinx',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CLITool',
    debug=False,  # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for console output during development
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/favicon/favicon.ico' if Path('static/favicon/favicon.ico').exists() else None,
    version_file=None,  # Can add version info later
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following lines if you prefer directory distribution
# 
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='CLITool'
# )