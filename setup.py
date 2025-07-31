"""
CLI Tool Setup Configuration
用於安裝和分發的設定文件
"""

from setuptools import setup, find_packages
from pathlib import Path

# 讀取 README 文件
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# 讀取 requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() 
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="cli-tool",
    version="1.0.0",
    description="A PyQt5-based GUI application integrating multiple CLI tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CLI Tool Developer",
    author_email="developer@example.com",
    url="https://github.com/example/cli-tool",
    
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
        "config": ["*.json"],
        "static": ["**/*"],
    },
    
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0", 
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-qt>=4.2.0",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "cli-tool=main_app:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
    
    python_requires=">=3.8",
    
    keywords="gui cli-tools pdf file-search pyqt5",
    
    project_urls={
        "Bug Reports": "https://github.com/example/cli-tool/issues",
        "Source": "https://github.com/example/cli-tool",
        "Documentation": "https://github.com/example/cli-tool/wiki",
    },
)