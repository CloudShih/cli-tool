#!/usr/bin/env python3
"""
CLI Tool Build Script
自動化打包腳本，包含清理、建置和驗證步驟
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse


class CLIToolBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / 'build'
        self.dist_dir = self.project_root / 'dist'
        self.spec_file = self.project_root / 'cli_tool.spec'
    
    def clean(self):
        """清理之前的建置文件"""
        print("🧹 Cleaning previous build files...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed {dir_path}")
        
        # 清理 __pycache__ 目錄
        for pycache in self.project_root.rglob('__pycache__'):
            shutil.rmtree(pycache)
            print(f"  ✅ Removed {pycache}")
        
        print("  ✨ Clean completed!")
    
    def check_dependencies(self):
        """檢查依賴是否安裝"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'PyQt5',
            'ansi2html', 
            'pikepdf',
            'pyinstaller'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.lower().replace('-', '_'))
                print(f"  ✅ {package} is installed")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package} is missing")
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Please install them using: pip install -r requirements.txt")
            return False
        
        print("  ✨ All dependencies are satisfied!")
        return True
    
    def validate_project_structure(self):
        """驗證專案結構"""
        print("📁 Validating project structure...")
        
        required_files = [
            'main_app.py',
            'requirements.txt',
            'cli_tool.spec',
            'config/config_manager.py',
            'config/cli_tool_config.json',
            'tools/fd/fd_model.py',
            'tools/poppler/poppler_model.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path}")
        
        if missing_files:
            print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
            return False
        
        print("  ✨ Project structure is valid!")
        return True
    
    def build(self, debug=False):
        """執行 PyInstaller 建置"""
        print("🔨 Building executable with PyInstaller...")
        
        cmd = ['pyinstaller', '--clean']
        
        if debug:
            cmd.extend(['--debug=all', '--console'])
            print("  🐛 Debug mode enabled")
        
        cmd.append(str(self.spec_file))
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("  ✅ PyInstaller completed successfully!")
            
            if result.stdout:
                print("  📄 PyInstaller output:")
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            print(f"  ❌ PyInstaller failed with exit code {e.returncode}")
            if e.stdout:
                print("  📄 stdout:")
                print(e.stdout)
            if e.stderr:
                print("  📄 stderr:")
                print(e.stderr)
            return False
        
        return True
    
    def validate_build(self):
        """驗證建置結果"""
        print("✅ Validating build result...")
        
        exe_path = self.dist_dir / 'CLITool.exe'
        if not exe_path.exists():
            print(f"  ❌ Executable not found at {exe_path}")
            return False
        
        # 檢查執行檔大小
        exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"  📏 Executable size: {exe_size:.1f} MB")
        
        if exe_size > 200:  # 警告如果超過 200MB
            print("  ⚠️  Executable is quite large, consider optimizing")
        
        print(f"  ✅ Executable created successfully at {exe_path}")
        return True
    
    def run_full_build(self, debug=False, skip_clean=False):
        """執行完整建置流程"""
        print("🚀 Starting CLI Tool build process...")
        print("=" * 50)
        
        # 步驟 1: 清理 (可選)
        if not skip_clean:
            self.clean()
        
        # 步驟 2: 檢查依賴
        if not self.check_dependencies():
            return False
        
        # 步驟 3: 驗證專案結構
        if not self.validate_project_structure():
            return False
        
        # 步驟 4: 建置
        if not self.build(debug=debug):
            return False
        
        # 步驟 5: 驗證建置結果
        if not self.validate_build():
            return False
        
        print("=" * 50)
        print("🎉 Build completed successfully!")
        print(f"📦 Executable location: {self.dist_dir / 'CLITool.exe'}")
        return True


def main():
    parser = argparse.ArgumentParser(description='CLI Tool Build Script')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode (console output)')
    parser.add_argument('--skip-clean', action='store_true',
                       help='Skip cleaning previous build files')
    parser.add_argument('--clean-only', action='store_true',
                       help='Only clean build files, do not build')
    
    args = parser.parse_args()
    
    builder = CLIToolBuilder()
    
    if args.clean_only:
        builder.clean()
        return
    
    success = builder.run_full_build(debug=args.debug, skip_clean=args.skip_clean)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()