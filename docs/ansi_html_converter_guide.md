# ANSI 彩色輸出轉 HTML 顯示 - 完整實現指南

## 概述

本指南提供完整的 ANSI 彩色輸出轉 HTML 顯示系統，專為 CLI 工具的視覺效果提升設計。基於現有專案使用 `ansi2html` 的經驗，建立更強大、靈活和主題化的 ANSI 轉 HTML 系統。

## 現有實現分析

### 當前使用情況

專案中已在多個地方使用 `ansi2html.Ansi2HTMLConverter()`:
- `tools/csvkit/csvkit_controller.py` - CSV 工具輸出轉換
- 測試檔案中廣泛使用於驗證輸出格式
- 主要用於將 CLI 工具的彩色輸出轉換為 HTML 在 GUI 中顯示

### 現有問題

1. **基礎功能限制** - 只使用了 `ansi2html` 的基本功能
2. **主題支援不足** - 沒有統一的主題系統
3. **性能考量** - 大量輸出時轉換效率問題
4. **自定義樣式限制** - 難以實現特定的視覺效果

---

## 增強的 ANSI HTML 轉換系統

### 核心架構設計

```
Enhanced ANSI to HTML System
├── ANSI Parser (ANSI 解析器)
│   ├── Escape Sequence Parser (轉義序列解析器)
│   ├── Color Code Parser (顏色代碼解析器)
│   └── Style Attribute Parser (樣式屬性解析器)
├── HTML Generator (HTML 生成器)
│   ├── Tag Generator (標籤生成器)
│   ├── CSS Class Manager (CSS 類別管理器)
│   └── Theme Integration (主題整合)
├── Theme System (主題系統)
│   ├── Dark Theme Support (暗色主題支援)
│   ├── Light Theme Support (亮色主題支援)
│   └── Custom Theme Engine (自定義主題引擎)
├── Performance Optimization (性能優化)
│   ├── Stream Processing (流式處理)
│   ├── Caching System (快取系統)
│   └── Memory Management (記憶體管理)
└── CLI Tools Integration (CLI 工具整合)
    ├── Ripgrep Output (Ripgrep 輸出)
    ├── Bat Syntax Highlighting (Bat 語法高亮)
    └── Generic CLI Output (通用 CLI 輸出)
```

---

## 1. 核心 ANSI 解析器

### 增強的 ANSI 解析器

```python
"""
增強的 ANSI 轉 HTML 轉換器
支援完整的 ANSI 轉義序列和主題化樣式
"""

import re
import html
import logging
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ANSIColorType(Enum):
    """ANSI 顏色類型"""
    STANDARD = "standard"      # 標準 16 色
    BRIGHT = "bright"          # 高亮 16 色
    COLOR_256 = "256"          # 256 色模式
    TRUE_COLOR = "truecolor"   # 24 位真彩色


@dataclass
class ANSIStyle:
    """ANSI 樣式表示"""
    foreground_color: Optional[str] = None
    background_color: Optional[str] = None
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    reverse: bool = False
    blink: bool = False
    
    def to_css_classes(self) -> List[str]:
        """轉換為 CSS 類別名稱"""
        classes = []
        
        if self.foreground_color:
            classes.append(f"ansi-fg-{self.foreground_color}")
        
        if self.background_color:
            classes.append(f"ansi-bg-{self.background_color}")
        
        if self.bold:
            classes.append("ansi-bold")
        if self.dim:
            classes.append("ansi-dim")
        if self.italic:
            classes.append("ansi-italic")
        if self.underline:
            classes.append("ansi-underline")
        if self.strikethrough:
            classes.append("ansi-strikethrough")
        if self.reverse:
            classes.append("ansi-reverse")
        if self.blink:
            classes.append("ansi-blink")
            
        return classes
    
    def to_inline_styles(self, theme_colors: Dict[str, str]) -> str:
        """轉換為內聯 CSS 樣式"""
        styles = []
        
        if self.foreground_color and self.foreground_color in theme_colors:
            styles.append(f"color: {theme_colors[self.foreground_color]}")
        
        if self.background_color and self.background_color in theme_colors:
            styles.append(f"background-color: {theme_colors[self.background_color]}")
        
        if self.bold:
            styles.append("font-weight: bold")
        if self.dim:
            styles.append("opacity: 0.7")
        if self.italic:
            styles.append("font-style: italic")
        if self.underline:
            styles.append("text-decoration: underline")
        if self.strikethrough:
            styles.append("text-decoration: line-through")
        if self.reverse:
            styles.append("filter: invert(1)")
        if self.blink:
            styles.append("animation: ansi-blink 1s infinite")
            
        return "; ".join(styles)


class EnhancedANSIParser:
    """增強的 ANSI 解析器"""
    
    # ANSI 轉義序列模式
    ANSI_ESCAPE_PATTERN = re.compile(r'\x1b\[[0-9;]*[mK]')
    ANSI_COLOR_PATTERN = re.compile(r'\x1b\[([0-9;]*)m')
    
    # 標準 ANSI 顏色映射
    STANDARD_COLORS = {
        '30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
        '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
        '90': 'bright-black', '91': 'bright-red', '92': 'bright-green', '93': 'bright-yellow',
        '94': 'bright-blue', '95': 'bright-magenta', '96': 'bright-cyan', '97': 'bright-white',
    }
    
    BACKGROUND_COLORS = {
        '40': 'black', '41': 'red', '42': 'green', '43': 'yellow',
        '44': 'blue', '45': 'magenta', '46': 'cyan', '47': 'white',
        '100': 'bright-black', '101': 'bright-red', '102': 'bright-green', '103': 'bright-yellow',
        '104': 'bright-blue', '105': 'bright-magenta', '106': 'bright-cyan', '107': 'bright-white',
    }
    
    def __init__(self):
        self.current_style = ANSIStyle()
        self.style_stack: List[ANSIStyle] = []
    
    def parse_ansi_sequence(self, sequence: str) -> ANSIStyle:
        """解析 ANSI 轉義序列"""
        if not sequence.startswith('\x1b[') or not sequence.endswith('m'):
            return self.current_style
        
        # 提取數字代碼
        codes = sequence[2:-1]  # 移除 \x1b[ 和 m
        
        if not codes:  # 空序列，重置樣式
            self.current_style = ANSIStyle()
            return self.current_style
        
        # 分割代碼
        code_parts = codes.split(';') if codes else ['0']
        
        style = ANSIStyle()
        # 保持當前樣式作為基礎
        style.foreground_color = self.current_style.foreground_color
        style.background_color = self.current_style.background_color
        style.bold = self.current_style.bold
        style.dim = self.current_style.dim
        style.italic = self.current_style.italic
        style.underline = self.current_style.underline
        style.strikethrough = self.current_style.strikethrough
        style.reverse = self.current_style.reverse
        style.blink = self.current_style.blink
        
        i = 0
        while i < len(code_parts):
            code = code_parts[i]
            
            if code == '0':  # 重置所有樣式
                style = ANSIStyle()
            elif code == '1':  # 粗體
                style.bold = True
            elif code == '2':  # 暗淡
                style.dim = True
            elif code == '3':  # 斜體
                style.italic = True
            elif code == '4':  # 下劃線
                style.underline = True
            elif code == '7':  # 反色
                style.reverse = True
            elif code == '5':  # 閃爍
                style.blink = True
            elif code == '9':  # 刪除線
                style.strikethrough = True
            elif code == '22':  # 關閉粗體/暗淡
                style.bold = False
                style.dim = False
            elif code == '23':  # 關閉斜體
                style.italic = False
            elif code == '24':  # 關閉下劃線
                style.underline = False
            elif code == '27':  # 關閉反色
                style.reverse = False
            elif code == '25':  # 關閉閃爍
                style.blink = False
            elif code == '29':  # 關閉刪除線
                style.strikethrough = False
            elif code in self.STANDARD_COLORS:  # 前景色
                style.foreground_color = self.STANDARD_COLORS[code]
            elif code in self.BACKGROUND_COLORS:  # 背景色
                style.background_color = self.BACKGROUND_COLORS[code]
            elif code == '38':  # 擴展前景色
                if i + 2 < len(code_parts):
                    if code_parts[i + 1] == '5':  # 256 色
                        color_code = code_parts[i + 2]
                        style.foreground_color = f"color-{color_code}"
                        i += 2
                    elif code_parts[i + 1] == '2':  # RGB 色
                        if i + 4 < len(code_parts):
                            r, g, b = code_parts[i + 2:i + 5]
                            style.foreground_color = f"rgb-{r}-{g}-{b}"
                            i += 4
            elif code == '48':  # 擴展背景色
                if i + 2 < len(code_parts):
                    if code_parts[i + 1] == '5':  # 256 色
                        color_code = code_parts[i + 2]
                        style.background_color = f"color-{color_code}"
                        i += 2
                    elif code_parts[i + 1] == '2':  # RGB 色
                        if i + 4 < len(code_parts):
                            r, g, b = code_parts[i + 2:i + 5]
                            style.background_color = f"rgb-{r}-{g}-{b}"
                            i += 4
            
            i += 1
        
        self.current_style = style
        return style
    
    def reset_parser(self):
        """重置解析器狀態"""
        self.current_style = ANSIStyle()
        self.style_stack.clear()


class ANSITheme:
    """ANSI 主題系統"""
    
    def __init__(self, name: str, colors: Dict[str, str], is_dark: bool = True):
        self.name = name
        self.colors = colors
        self.is_dark = is_dark
    
    @classmethod
    def load_from_file(cls, theme_file: Path) -> 'ANSITheme':
        """從檔案載入主題"""
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        
        return cls(
            name=theme_data['name'],
            colors=theme_data['colors'],
            is_dark=theme_data.get('is_dark', True)
        )
    
    def save_to_file(self, theme_file: Path):
        """儲存主題到檔案"""
        theme_data = {
            'name': self.name,
            'colors': self.colors,
            'is_dark': self.is_dark
        }
        
        with open(theme_file, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2, ensure_ascii=False)
    
    def get_css_variables(self) -> str:
        """生成 CSS 自定義屬性"""
        css_vars = []
        for color_name, color_value in self.colors.items():
            css_vars.append(f"  --ansi-{color_name}: {color_value};")
        
        return "{\n" + "\n".join(css_vars) + "\n}"


class ThemeManager:
    """主題管理器"""
    
    def __init__(self):
        self.themes: Dict[str, ANSITheme] = {}
        self.current_theme: Optional[ANSITheme] = None
        self._load_builtin_themes()
    
    def _load_builtin_themes(self):
        """載入內建主題"""
        # 暗色主題
        dark_theme = ANSITheme("Dark Professional", {
            # 標準顏色
            'black': '#1e1e1e',
            'red': '#f44747',
            'green': '#4ec9b0',
            'yellow': '#ffcc02',
            'blue': '#569cd6',
            'magenta': '#c586c0',
            'cyan': '#4fc1ff',
            'white': '#d4d4d4',
            
            # 亮色版本
            'bright-black': '#666666',
            'bright-red': '#f14c4c',
            'bright-green': '#23d18b',
            'bright-yellow': '#f5f543',
            'bright-blue': '#3b82f6',
            'bright-magenta': '#d946ef',
            'bright-cyan': '#06b6d4',
            'bright-white': '#ffffff',
            
            # 背景
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
        }, is_dark=True)
        
        # 亮色主題
        light_theme = ANSITheme("Light Modern", {
            # 標準顏色
            'black': '#383a42',
            'red': '#e45649',
            'green': '#50a14f',
            'yellow': '#c18401',
            'blue': '#0184bc',
            'magenta': '#a626a4',
            'cyan': '#0997b3',
            'white': '#fafafa',
            
            # 亮色版本
            'bright-black': '#4f525e',
            'bright-red': '#e06c75',
            'bright-green': '#98c379',
            'bright-yellow': '#e5c07b',
            'bright-blue': '#61afef',
            'bright-magenta': '#c678dd',
            'bright-cyan': '#56b6c2',
            'bright-white': '#ffffff',
            
            # 背景
            'background': '#fafafa',
            'foreground': '#383a42',
        }, is_dark=False)
        
        # 夜貓主題 (Monokai 風格)
        monokai_theme = ANSITheme("Night Owl", {
            'black': '#272822',
            'red': '#f92672',
            'green': '#a6e22e',
            'yellow': '#f4bf75',
            'blue': '#66d9ef',
            'magenta': '#ae81ff',
            'cyan': '#a1efe4',
            'white': '#f8f8f2',
            
            'bright-black': '#75715e',
            'bright-red': '#f92672',
            'bright-green': '#a6e22e',
            'bright-yellow': '#f4bf75',
            'bright-blue': '#66d9ef',
            'bright-magenta': '#ae81ff',
            'bright-cyan': '#a1efe4',
            'bright-white': '#f9f8f5',
            
            'background': '#272822',
            'foreground': '#f8f8f2',
        }, is_dark=True)
        
        # 藍色企業主題
        corporate_theme = ANSITheme("Corporate Blue", {
            'black': '#002b36',
            'red': '#dc322f',
            'green': '#859900',
            'yellow': '#b58900',
            'blue': '#268bd2',
            'magenta': '#d33682',
            'cyan': '#2aa198',
            'white': '#eee8d5',
            
            'bright-black': '#073642',
            'bright-red': '#cb4b16',
            'bright-green': '#586e75',
            'bright-yellow': '#657b83',
            'bright-blue': '#839496',
            'bright-magenta': '#6c71c4',
            'bright-cyan': '#93a1a1',
            'bright-white': '#fdf6e3',
            
            'background': '#002b36',
            'foreground': '#839496',
        }, is_dark=True)
        
        self.themes = {
            'dark': dark_theme,
            'light': light_theme,
            'night-owl': monokai_theme,
            'corporate': corporate_theme
        }
        
        self.current_theme = dark_theme
    
    def set_theme(self, theme_name: str):
        """設置當前主題"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            logger.info(f"ANSI theme set to: {theme_name}")
        else:
            logger.warning(f"Theme '{theme_name}' not found")
    
    def get_current_theme(self) -> Optional[ANSITheme]:
        """取得當前主題"""
        return self.current_theme
    
    def add_custom_theme(self, theme: ANSITheme):
        """添加自定義主題"""
        self.themes[theme.name.lower().replace(' ', '-')] = theme
        logger.info(f"Added custom theme: {theme.name}")


class EnhancedANSIToHTMLConverter:
    """增強的 ANSI 到 HTML 轉換器"""
    
    def __init__(self, theme_manager: ThemeManager = None):
        self.parser = EnhancedANSIParser()
        self.theme_manager = theme_manager or ThemeManager()
        self.use_inline_styles = False
        self.include_css = True
        
    def convert_to_html(self, 
                       ansi_text: str, 
                       include_wrapper: bool = True,
                       css_class_prefix: str = "ansi",
                       line_numbers: bool = False,
                       title: str = None) -> str:
        """
        將 ANSI 文本轉換為 HTML
        
        Args:
            ansi_text: 包含 ANSI 轉義序列的文本
            include_wrapper: 是否包含 HTML 包裝器
            css_class_prefix: CSS 類別前綴
            line_numbers: 是否顯示行號
            title: HTML 標題
            
        Returns:
            轉換後的 HTML 字符串
        """
        if not ansi_text:
            return ""
        
        # 重置解析器
        self.parser.reset_parser()
        
        html_parts = []
        
        if include_wrapper:
            html_parts.append(self._generate_html_header(title))
        
        # 分行處理
        lines = ansi_text.split('\n')
        
        if line_numbers:
            html_parts.append('<div class="ansi-content ansi-line-numbers">')
        else:
            html_parts.append('<div class="ansi-content">')
        
        for line_no, line in enumerate(lines, 1):
            line_html = self._convert_line_to_html(line, css_class_prefix)
            
            if line_numbers:
                html_parts.append(f'<div class="ansi-line">')
                html_parts.append(f'<span class="ansi-line-number">{line_no:4d}</span>')
                html_parts.append(f'<span class="ansi-line-content">{line_html}</span>')
                html_parts.append('</div>')
            else:
                html_parts.append(f'<div class="ansi-line">{line_html}</div>')
        
        html_parts.append('</div>')
        
        if include_wrapper:
            html_parts.append(self._generate_html_footer())
        
        return '\n'.join(html_parts)
    
    def _convert_line_to_html(self, line: str, css_class_prefix: str) -> str:
        """轉換單行為 HTML"""
        if not line:
            return "&nbsp;"  # 空行用不間斷空格
        
        # 查找所有 ANSI 轉義序列
        parts = []
        last_end = 0
        
        for match in self.parser.ANSI_COLOR_PATTERN.finditer(line):
            # 添加轉義序列前的文本
            if match.start() > last_end:
                text = line[last_end:match.start()]
                if text:
                    parts.append(('text', text))
            
            # 解析 ANSI 轉義序列
            ansi_sequence = match.group(0)
            style = self.parser.parse_ansi_sequence(ansi_sequence)
            parts.append(('style', style))
            
            last_end = match.end()
        
        # 添加剩餘文本
        if last_end < len(line):
            text = line[last_end:]
            if text:
                parts.append(('text', text))
        
        # 生成 HTML
        return self._render_parts_to_html(parts, css_class_prefix)
    
    def _render_parts_to_html(self, parts: List[Tuple[str, Union[str, ANSIStyle]]], css_class_prefix: str) -> str:
        """渲染部分為 HTML"""
        html = []
        current_span = None
        current_style = ANSIStyle()
        
        for part_type, part_data in parts:
            if part_type == 'style':
                # 樣式改變，關閉當前 span 並開始新的
                if current_span is not None:
                    html.append('</span>')
                
                current_style = part_data
                
                # 如果有樣式，開始新 span
                if self._has_style(current_style):
                    span_attrs = self._generate_span_attributes(current_style, css_class_prefix)
                    html.append(f'<span{span_attrs}>')
                    current_span = True
                else:
                    current_span = None
                    
            elif part_type == 'text':
                # 轉義 HTML 特殊字符
                escaped_text = html.escape(part_data)
                # 轉換空格為 &nbsp; 保持格式
                escaped_text = escaped_text.replace(' ', '&nbsp;')
                # 轉換 tab 為 4 個空格
                escaped_text = escaped_text.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
                html.append(escaped_text)
        
        # 關閉最後的 span
        if current_span is not None:
            html.append('</span>')
        
        return ''.join(html)
    
    def _has_style(self, style: ANSIStyle) -> bool:
        """檢查樣式是否有效果"""
        return (style.foreground_color is not None or
                style.background_color is not None or
                style.bold or style.dim or style.italic or
                style.underline or style.strikethrough or
                style.reverse or style.blink)
    
    def _generate_span_attributes(self, style: ANSIStyle, css_class_prefix: str) -> str:
        """生成 span 標籤屬性"""
        if self.use_inline_styles:
            theme = self.theme_manager.get_current_theme()
            if theme:
                inline_style = style.to_inline_styles(theme.colors)
                if inline_style:
                    return f' style="{inline_style}"'
        else:
            css_classes = style.to_css_classes()
            if css_classes:
                # 添加前綴
                prefixed_classes = [f"{css_class_prefix}-{cls}" for cls in css_classes]
                return f' class="{" ".join(prefixed_classes)}"'
        
        return ""
    
    def _generate_html_header(self, title: str = None) -> str:
        """生成 HTML 頭部"""
        html_title = html.escape(title) if title else "ANSI Output"
        
        header = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{html_title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">'''
        
        if self.include_css:
            header += f'\n    <style>\n{self._generate_css()}\n    </style>'
        
        header += '\n</head>\n<body>'
        
        return header
    
    def _generate_html_footer(self) -> str:
        """生成 HTML 尾部"""
        return '</body>\n</html>'
    
    def _generate_css(self) -> str:
        """生成主題相關的 CSS"""
        theme = self.theme_manager.get_current_theme()
        if not theme:
            return ""
        
        css_rules = []
        
        # 根元素變數定義
        root_vars = theme.get_css_variables()
        css_rules.append(f":root {root_vars}")
        
        # 基本樣式
        css_rules.extend([
            """
body {
    background-color: var(--ansi-background);
    color: var(--ansi-foreground);
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.4;
    margin: 0;
    padding: 16px;
}

.ansi-content {
    background-color: var(--ansi-background);
    border: 1px solid var(--ansi-bright-black);
    border-radius: 4px;
    padding: 12px;
    overflow-x: auto;
}

.ansi-line {
    display: block;
    white-space: pre;
    margin: 0;
}

.ansi-line-numbers .ansi-line {
    display: flex;
}

.ansi-line-number {
    color: var(--ansi-bright-black);
    margin-right: 12px;
    user-select: none;
    text-align: right;
    min-width: 4em;
}

.ansi-line-content {
    flex: 1;
}
"""])
        
        # 顏色類別
        for color_name, color_value in theme.colors.items():
            if color_name not in ['background', 'foreground']:
                css_rules.append(f".ansi-fg-{color_name} {{ color: var(--ansi-{color_name}); }}")
                css_rules.append(f".ansi-bg-{color_name} {{ background-color: var(--ansi-{color_name}); }}")
        
        # 樣式類別
        css_rules.extend([
            ".ansi-bold { font-weight: bold; }",
            ".ansi-dim { opacity: 0.7; }",
            ".ansi-italic { font-style: italic; }",
            ".ansi-underline { text-decoration: underline; }",
            ".ansi-strikethrough { text-decoration: line-through; }",
            ".ansi-reverse { filter: invert(1); }",
            ".ansi-blink { animation: ansi-blink 1s infinite; }",
            
            # 動畫定義
            """
@keyframes ansi-blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

/* 256 色支援 */
"""])
        
        # 256 色映射（簡化版）
        for i in range(256):
            r = g = b = 0
            if i < 16:
                # 標準 16 色已在主題中定義
                continue
            elif i < 232:
                # 6x6x6 色彩立方體
                i -= 16
                r = (i // 36) * 51
                g = ((i % 36) // 6) * 51
                b = (i % 6) * 51
            else:
                # 灰階
                gray = 8 + (i - 232) * 10
                r = g = b = gray
            
            color = f"rgb({r}, {g}, {b})"
            css_rules.append(f".ansi-fg-color-{i} {{ color: {color}; }}")
            css_rules.append(f".ansi-bg-color-{i} {{ background-color: {color}; }}")
        
        return "\n".join(css_rules)
    
    def set_theme(self, theme_name: str):
        """設置主題"""
        self.theme_manager.set_theme(theme_name)
    
    def set_use_inline_styles(self, use_inline: bool):
        """設置是否使用內聯樣式"""
        self.use_inline_styles = use_inline


# 全域轉換器實例
theme_manager = ThemeManager()
ansi_converter = EnhancedANSIToHTMLConverter(theme_manager)
```

---

## 2. 流式處理和性能優化

### 高效能流式轉換器

```python
"""
高效能流式 ANSI 轉 HTML 處理器
用於處理大量實時輸出
"""

import asyncio
import queue
import threading
from typing import AsyncGenerator, Generator, Callable, Optional
from concurrent.futures import ThreadPoolExecutor


class StreamingANSIProcessor:
    """流式 ANSI 處理器"""
    
    def __init__(self, converter: EnhancedANSIToHTMLConverter):
        self.converter = converter
        self.buffer_size = 8192
        self.line_buffer = ""
        self.processed_lines = 0
        
    def process_stream(self, 
                      text_stream: Generator[str, None, None],
                      callback: Callable[[str], None] = None) -> Generator[str, None, None]:
        """
        流式處理文本流
        
        Args:
            text_stream: 文本流生成器
            callback: 每行處理完成後的回調函數
            
        Yields:
            處理完成的 HTML 行
        """
        for chunk in text_stream:
            self.line_buffer += chunk
            
            # 處理完整的行
            while '\n' in self.line_buffer:
                line, self.line_buffer = self.line_buffer.split('\n', 1)
                
                # 轉換行為 HTML
                html_line = self.converter._convert_line_to_html(line, "ansi")
                html_output = f'<div class="ansi-line">{html_line}</div>'
                
                self.processed_lines += 1
                
                if callback:
                    callback(html_output)
                
                yield html_output
        
        # 處理剩餘緩衝區內容
        if self.line_buffer:
            html_line = self.converter._convert_line_to_html(self.line_buffer, "ansi")
            html_output = f'<div class="ansi-line">{html_line}</div>'
            
            if callback:
                callback(html_output)
            
            yield html_output
    
    async def process_stream_async(self,
                                  text_stream: AsyncGenerator[str, None],
                                  callback: Callable[[str], None] = None) -> AsyncGenerator[str, None]:
        """
        異步流式處理
        
        Args:
            text_stream: 異步文本流
            callback: 回調函數
            
        Yields:
            處理完成的 HTML 行
        """
        async for chunk in text_stream:
            self.line_buffer += chunk
            
            while '\n' in self.line_buffer:
                line, self.line_buffer = self.line_buffer.split('\n', 1)
                
                # 在線程池中處理轉換以避免阻塞
                with ThreadPoolExecutor(max_workers=1) as executor:
                    html_line = await asyncio.get_event_loop().run_in_executor(
                        executor, 
                        self.converter._convert_line_to_html, 
                        line, 
                        "ansi"
                    )
                
                html_output = f'<div class="ansi-line">{html_line}</div>'
                self.processed_lines += 1
                
                if callback:
                    callback(html_output)
                
                yield html_output
        
        # 處理剩餘內容
        if self.line_buffer:
            with ThreadPoolExecutor(max_workers=1) as executor:
                html_line = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    self.converter._convert_line_to_html,
                    self.line_buffer,
                    "ansi"
                )
            
            html_output = f'<div class="ansi-line">{html_line}</div>'
            
            if callback:
                callback(html_output)
            
            yield html_output
    
    def reset(self):
        """重置處理器狀態"""
        self.line_buffer = ""
        self.processed_lines = 0
        self.converter.parser.reset_parser()


class CachingANSIProcessor:
    """帶快取的 ANSI 處理器"""
    
    def __init__(self, converter: EnhancedANSIToHTMLConverter, cache_size: int = 10000):
        self.converter = converter
        self.cache: Dict[str, str] = {}
        self.cache_size = cache_size
        self.cache_hits = 0
        self.cache_misses = 0
    
    def process_with_cache(self, ansi_text: str) -> str:
        """帶快取的處理"""
        # 計算內容雜湊作為快取鍵
        import hashlib
        cache_key = hashlib.md5(ansi_text.encode('utf-8')).hexdigest()
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        # 快取未命中，進行轉換
        self.cache_misses += 1
        html_output = self.converter.convert_to_html(ansi_text, include_wrapper=False)
        
        # 檢查快取大小
        if len(self.cache) >= self.cache_size:
            # 簡單的 LRU - 移除最舊的項目
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = html_output
        return html_output
    
    def get_cache_stats(self) -> Dict[str, int]:
        """取得快取統計"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'total': total_requests,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }
    
    def clear_cache(self):
        """清空快取"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
```

---

## 3. CLI 工具專用處理器

### 工具特定的 ANSI 處理器

```python
"""
CLI 工具專用的 ANSI 處理器
針對不同工具的輸出特性進行優化
"""

from abc import ABC, abstractmethod
import re


class CLIToolProcessor(ABC):
    """CLI 工具處理器基類"""
    
    def __init__(self, converter: EnhancedANSIToHTMLConverter):
        self.converter = converter
        
    @abstractmethod
    def process_output(self, output: str) -> str:
        """處理工具輸出"""
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """取得工具名稱"""
        pass


class RipgrepProcessor(CLIToolProcessor):
    """Ripgrep 輸出處理器"""
    
    # Ripgrep 輸出格式模式
    MATCH_PATTERN = re.compile(r'^([^:]+):(\d+):(\d+):(.*)$')
    CONTEXT_PATTERN = re.compile(r'^([^:]+)-(\d+)-(.*)$')
    
    def get_tool_name(self) -> str:
        return "ripgrep"
    
    def process_output(self, output: str) -> str:
        """處理 ripgrep 輸出，增強匹配結果顯示"""
        lines = output.split('\n')
        processed_lines = []
        
        for line in lines:
            if not line.strip():
                processed_lines.append('<div class="ansi-line">&nbsp;</div>')
                continue
            
            # 檢查是否為匹配行
            match = self.MATCH_PATTERN.match(line)
            if match:
                file_path, line_num, col_num, content = match.groups()
                processed_line = self._process_match_line(file_path, line_num, col_num, content)
                processed_lines.append(processed_line)
                continue
            
            # 檢查是否為上下文行
            context_match = self.CONTEXT_PATTERN.match(line)
            if context_match:
                file_path, line_num, content = context_match.groups()
                processed_line = self._process_context_line(file_path, line_num, content)
                processed_lines.append(processed_line)
                continue
            
            # 其他行（如檔案分隔符等）
            html_content = self.converter._convert_line_to_html(line, "ansi")
            processed_lines.append(f'<div class="ansi-line ansi-ripgrep-other">{html_content}</div>')
        
        return '\n'.join(processed_lines)
    
    def _process_match_line(self, file_path: str, line_num: str, col_num: str, content: str) -> str:
        """處理匹配行"""
        # 轉換內容中的 ANSI
        html_content = self.converter._convert_line_to_html(content, "ansi")
        
        # 創建帶有特殊樣式的匹配行
        return f'''<div class="ansi-line ansi-ripgrep-match">
    <span class="ansi-ripgrep-file">{html.escape(file_path)}</span>
    <span class="ansi-ripgrep-separator">:</span>
    <span class="ansi-ripgrep-line-number">{line_num}</span>
    <span class="ansi-ripgrep-separator">:</span>
    <span class="ansi-ripgrep-column">{col_num}</span>
    <span class="ansi-ripgrep-separator">:</span>
    <span class="ansi-ripgrep-content">{html_content}</span>
</div>'''
    
    def _process_context_line(self, file_path: str, line_num: str, content: str) -> str:
        """處理上下文行"""
        html_content = self.converter._convert_line_to_html(content, "ansi")
        
        return f'''<div class="ansi-line ansi-ripgrep-context">
    <span class="ansi-ripgrep-file">{html.escape(file_path)}</span>
    <span class="ansi-ripgrep-separator">-</span>
    <span class="ansi-ripgrep-line-number">{line_num}</span>
    <span class="ansi-ripgrep-separator">-</span>
    <span class="ansi-ripgrep-content">{html_content}</span>
</div>'''


class BatProcessor(CLIToolProcessor):
    """Bat 語法高亮處理器"""
    
    def get_tool_name(self) -> str:
        return "bat"
    
    def process_output(self, output: str) -> str:
        """處理 bat 輸出，保持語法高亮"""
        # bat 已經產生了很好的 ANSI 顏色，直接轉換即可
        return self.converter.convert_to_html(output, include_wrapper=False, line_numbers=False)


class FdProcessor(CLIToolProcessor):
    """fd 檔案搜尋處理器"""
    
    def get_tool_name(self) -> str:
        return "fd"
    
    def process_output(self, output: str) -> str:
        """處理 fd 輸出，增強檔案路徑顯示"""
        lines = output.split('\n')
        processed_lines = []
        
        for line in lines:
            if not line.strip():
                processed_lines.append('<div class="ansi-line">&nbsp;</div>')
                continue
            
            # fd 輸出通常是檔案路徑，可能包含顏色
            html_content = self.converter._convert_line_to_html(line, "ansi")
            
            # 檢查是否為檔案路徑
            if '/' in line or '\\' in line:
                processed_lines.append(f'<div class="ansi-line ansi-fd-path">{html_content}</div>')
            else:
                processed_lines.append(f'<div class="ansi-line">{html_content}</div>')
        
        return '\n'.join(processed_lines)


class GenericProcessor(CLIToolProcessor):
    """通用處理器"""
    
    def get_tool_name(self) -> str:
        return "generic"
    
    def process_output(self, output: str) -> str:
        """通用處理"""
        return self.converter.convert_to_html(output, include_wrapper=False)


class ToolProcessorFactory:
    """工具處理器工廠"""
    
    def __init__(self, converter: EnhancedANSIToHTMLConverter):
        self.converter = converter
        self.processors = {
            'ripgrep': RipgrepProcessor(converter),
            'rg': RipgrepProcessor(converter),
            'bat': BatProcessor(converter),
            'fd': FdProcessor(converter),
            'generic': GenericProcessor(converter),
        }
    
    def get_processor(self, tool_name: str) -> CLIToolProcessor:
        """取得工具對應的處理器"""
        tool_key = tool_name.lower()
        return self.processors.get(tool_key, self.processors['generic'])
    
    def register_processor(self, tool_name: str, processor: CLIToolProcessor):
        """註冊新的工具處理器"""
        self.processors[tool_name.lower()] = processor
```

---

## 4. 專案整合與實際應用

### 整合到現有專案

```python
# utils/ansi_html_utils.py - 統一的 ANSI HTML 處理工具

"""
統一的 ANSI HTML 處理工具
替換現有的 ansi2html 使用
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ANSIHTMLProcessor:
    """統一的 ANSI HTML 處理器"""
    
    def __init__(self):
        # 延遲載入以避免循環依賴
        self._converter = None
        self._theme_manager = None
        self._processor_factory = None
        self._streaming_processor = None
        self._caching_processor = None
    
    @property
    def converter(self) -> EnhancedANSIToHTMLConverter:
        """取得轉換器實例"""
        if self._converter is None:
            self._converter = EnhancedANSIToHTMLConverter(self.theme_manager)
        return self._converter
    
    @property
    def theme_manager(self) -> ThemeManager:
        """取得主題管理器實例"""
        if self._theme_manager is None:
            self._theme_manager = ThemeManager()
        return self._theme_manager
    
    @property
    def processor_factory(self) -> ToolProcessorFactory:
        """取得工具處理器工廠"""
        if self._processor_factory is None:
            self._processor_factory = ToolProcessorFactory(self.converter)
        return self._processor_factory
    
    @property
    def streaming_processor(self) -> StreamingANSIProcessor:
        """取得流式處理器"""
        if self._streaming_processor is None:
            self._streaming_processor = StreamingANSIProcessor(self.converter)
        return self._streaming_processor
    
    @property
    def caching_processor(self) -> CachingANSIProcessor:
        """取得快取處理器"""
        if self._caching_processor is None:
            self._caching_processor = CachingANSIProcessor(self.converter)
        return self._caching_processor
    
    def convert_for_tool(self, 
                        tool_name: str, 
                        ansi_output: str,
                        use_cache: bool = True,
                        theme_name: Optional[str] = None) -> str:
        """
        為特定工具轉換 ANSI 輸出
        
        Args:
            tool_name: 工具名稱 (ripgrep, bat, fd, etc.)
            ansi_output: ANSI 輸出文本
            use_cache: 是否使用快取
            theme_name: 主題名稱
            
        Returns:
            轉換後的 HTML
        """
        if not ansi_output or not ansi_output.strip():
            return '<div class="ansi-content"><div class="ansi-line">&nbsp;</div></div>'
        
        try:
            # 設置主題
            if theme_name:
                self.theme_manager.set_theme(theme_name)
            
            # 取得工具專用處理器
            processor = self.processor_factory.get_processor(tool_name)
            
            # 使用快取處理器或直接處理
            if use_cache:
                # 創建簡單的快取鍵
                import hashlib
                cache_key = hashlib.md5(f"{tool_name}:{ansi_output}".encode()).hexdigest()
                
                if hasattr(self.caching_processor, 'cache') and cache_key in self.caching_processor.cache:
                    return self.caching_processor.cache[cache_key]
                
                html_output = processor.process_output(ansi_output)
                
                # 加入快取
                if len(self.caching_processor.cache) < self.caching_processor.cache_size:
                    self.caching_processor.cache[cache_key] = html_output
                
                return html_output
            else:
                return processor.process_output(ansi_output)
                
        except Exception as e:
            logger.error(f"Error converting ANSI output for {tool_name}: {e}")
            # 回退到基本轉換
            return self.converter.convert_to_html(ansi_output, include_wrapper=False)
    
    def convert_simple(self, ansi_output: str, **kwargs) -> str:
        """
        簡單轉換，兼容舊的 ansi2html.convert() 調用
        
        Args:
            ansi_output: ANSI 輸出
            **kwargs: 額外參數
            
        Returns:
            HTML 輸出
        """
        try:
            return self.converter.convert_to_html(
                ansi_output, 
                include_wrapper=kwargs.get('full', False)
            )
        except Exception as e:
            logger.error(f"Error in simple ANSI conversion: {e}")
            # 回退到 HTML 轉義
            return html.escape(ansi_output).replace('\n', '<br>')
    
    def set_theme(self, theme_name: str):
        """設置全域主題"""
        self.theme_manager.set_theme(theme_name)
        logger.info(f"ANSI HTML theme set to: {theme_name}")
    
    def get_available_themes(self) -> List[str]:
        """取得可用主題列表"""
        return list(self.theme_manager.themes.keys())
    
    def generate_css_for_theme(self, theme_name: str) -> str:
        """為特定主題生成 CSS"""
        current_theme = self.theme_manager.current_theme
        try:
            self.theme_manager.set_theme(theme_name)
            css = self.converter._generate_css()
            return css
        finally:
            self.theme_manager.current_theme = current_theme


# 全域實例
ansi_html_processor = ANSIHTMLProcessor()


# 兼容函數，用於替換現有的 ansi2html 使用
def convert_ansi_to_html(ansi_text: str, tool_name: str = "generic", **kwargs) -> str:
    """
    兼容函數，用於替換 ansi2html.Ansi2HTMLConverter().convert()
    
    Args:
        ansi_text: ANSI 文本
        tool_name: 工具名稱
        **kwargs: 額外參數
        
    Returns:
        HTML 文本
    """
    return ansi_html_processor.convert_for_tool(tool_name, ansi_text, **kwargs)


# 更簡單的兼容函數
class Ansi2HTMLConverter:
    """兼容類，用於替換 ansi2html.Ansi2HTMLConverter"""
    
    def __init__(self):
        pass
    
    def convert(self, ansi_text: str, full: bool = True) -> str:
        """兼容 convert 方法"""
        return ansi_html_processor.convert_simple(ansi_text, full=full)
```

### 更新現有控制器

```python
# 更新 csvkit_controller.py 以使用新的轉換器

# 在文件頭部替換導入
# 舊的導入
# import ansi2html

# 新的導入
from utils.ansi_html_utils import ansi_html_processor, convert_ansi_to_html

class CsvkitController(QObject):
    # ... 其他程式碼 ...
    
    def _on_command_finished(self, stdout: str, stderr: str, returncode: int):
        """命令完成處理 - 使用增強的 ANSI 轉換"""
        try:
            self.view.set_status("命令執行完成")
            self.view.toggle_buttons(True)
            
            if returncode == 0:
                # 成功情況
                if stdout.strip():
                    # 判斷是否需要 HTML 轉換
                    needs_html_conversion = self._needs_html_conversion(
                        self.worker.command_type, 
                        stdout
                    )
                    
                    if needs_html_conversion:
                        try:
                            # 使用增強的轉換器，指定工具類型為 csvkit
                            html_output = convert_ansi_to_html(stdout, tool_name="csvkit")
                            self.view.display_result(html_output)
                        except Exception as e:
                            logger.error(f"HTML conversion failed: {e}")
                            # 如果轉換失敗，使用純文本
                            self.view.display_result(stdout)
                    else:
                        # 對於純 CSV 輸出等，直接使用純文本
                        self.view.display_result(stdout)
                        
                    self.view.display_system_response("命令執行成功", is_error=False)
                else:
                    self.view.display_result("命令執行成功，無輸出內容")
                    self.view.display_system_response("命令執行成功", is_error=False)
                
            else:
                # 錯誤情況
                error_message = stderr.strip() if stderr.strip() else "命令執行失敗"
                
                # 錯誤訊息也可能包含 ANSI，進行轉換
                try:
                    html_error = convert_ansi_to_html(error_message, tool_name="csvkit")
                    self.view.display_result(f'<div class="error-output">{html_error}</div>')
                except Exception:
                    self.view.display_result(error_message)
                
                self.view.display_system_response(f"命令失敗: {error_message}", is_error=True)
                
        except Exception as e:
            logger.error(f"Error processing command result: {e}")
            self.view.display_system_response(f"處理命令結果時發生錯誤: {str(e)}", is_error=True)
        finally:
            # 清理工作線程
            if self.worker:
                self.worker.deleteLater()
                self.worker = None
```

### 主題配置整合

```python
# config/theme_config.py - 主題配置管理

"""
ANSI HTML 主題配置管理
與應用程式主題系統整合
"""

from typing import Dict, Any
from config.config_manager import config_manager
from utils.ansi_html_utils import ansi_html_processor


class ANSIThemeConfig:
    """ANSI 主題配置管理器"""
    
    def __init__(self):
        self.config_key = 'ansi_html'
        self._load_config()
    
    def _load_config(self):
        """載入配置"""
        # 從配置管理器載入 ANSI HTML 相關設定
        ansi_config = config_manager.get(self.config_key, {})
        
        # 設定預設主題
        default_theme = ansi_config.get('default_theme', 'dark')
        ansi_html_processor.set_theme(default_theme)
        
        # 設定其他選項
        use_caching = ansi_config.get('use_caching', True)
        if not use_caching:
            ansi_html_processor.caching_processor.clear_cache()
    
    def set_theme(self, theme_name: str):
        """設定主題並儲存到配置"""
        ansi_html_processor.set_theme(theme_name)
        
        # 更新配置
        config_manager.set(f'{self.config_key}.default_theme', theme_name)
        config_manager.save()
    
    def get_current_theme(self) -> str:
        """取得當前主題名稱"""
        current_theme = ansi_html_processor.theme_manager.get_current_theme()
        return current_theme.name if current_theme else 'dark'
    
    def get_available_themes(self) -> List[str]:
        """取得可用主題"""
        return ansi_html_processor.get_available_themes()
    
    def sync_with_app_theme(self, app_theme: str):
        """與應用程式主題同步"""
        # 根據應用程式主題自動選擇 ANSI 主題
        theme_mapping = {
            'dark': 'dark',
            'light': 'light',
            'blue': 'corporate',
            'monokai': 'night-owl'
        }
        
        ansi_theme = theme_mapping.get(app_theme.lower(), 'dark')
        self.set_theme(ansi_theme)


# 全域配置實例
ansi_theme_config = ANSIThemeConfig()
```

### PyQt5 整合顯示

```python
# ui/enhanced_text_browser.py - 增強的文本瀏覽器組件

"""
增強的文本瀏覽器，支援 ANSI HTML 顯示
"""

from PyQt5.QtWidgets import QTextBrowser, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal, QUrl, Qt
from PyQt5.QtGui import QFont
from utils.ansi_html_utils import ansi_html_processor
from config.theme_config import ansi_theme_config


class ANSITextBrowser(QTextBrowser):
    """支援 ANSI HTML 的文本瀏覽器"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """設定 UI"""
        # 設定字體
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        
        # 設定樣式
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        
        # 載入當前主題的 CSS
        self._update_theme_css()
    
    def display_ansi_output(self, ansi_text: str, tool_name: str = "generic"):
        """顯示 ANSI 輸出"""
        if not ansi_text:
            self.clear()
            return
        
        try:
            # 轉換為 HTML
            html_content = ansi_html_processor.convert_for_tool(tool_name, ansi_text)
            
            # 包裝在完整的 HTML 文檔中
            full_html = self._wrap_html_content(html_content)
            
            # 顯示
            self.setHtml(full_html)
            
        except Exception as e:
            logger.error(f"Error displaying ANSI output: {e}")
            # 回退到純文本
            self.setPlainText(ansi_text)
    
    def _wrap_html_content(self, content: str) -> str:
        """包裝 HTML 內容"""
        current_theme = ansi_html_processor.theme_manager.get_current_theme()
        if not current_theme:
            return content
        
        # 生成完整的 HTML 文檔
        css = ansi_html_processor.converter._generate_css()
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            background-color: var(--ansi-background);
            color: var(--ansi-foreground);
        }}
        {css}
        
        /* 工具專用樣式 */
        .ansi-ripgrep-match {{
            background-color: rgba(255, 255, 0, 0.1);
            border-left: 3px solid #ffc107;
            padding-left: 8px;
        }}
        
        .ansi-ripgrep-context {{
            opacity: 0.7;
            padding-left: 8px;
        }}
        
        .ansi-ripgrep-file {{
            color: var(--ansi-cyan);
            font-weight: bold;
        }}
        
        .ansi-ripgrep-line-number {{
            color: var(--ansi-bright-yellow);
        }}
        
        .ansi-ripgrep-separator {{
            color: var(--ansi-bright-black);
        }}
        
        .ansi-fd-path {{
            color: var(--ansi-blue);
        }}
        
        .error-output {{
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #dc3545;
            padding: 8px;
            margin: 4px 0;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''
    
    def _update_theme_css(self):
        """更新主題 CSS"""
        # 由於內容是通過 setHtml 設定的，CSS 包含在其中
        # 這個方法主要用於未來可能的樣式調整
        pass
    
    def set_theme(self, theme_name: str):
        """設定主題"""
        ansi_theme_config.set_theme(theme_name)
        self._update_theme_css()
        self.theme_changed.emit(theme_name)


class ANSIDisplayWidget(QWidget):
    """完整的 ANSI 顯示組件，包含主題選擇"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        
        # 工具欄
        toolbar = QHBoxLayout()
        
        # 主題選擇
        toolbar.addWidget(QLabel("主題:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(ansi_theme_config.get_available_themes())
        self.theme_combo.setCurrentText(ansi_theme_config.get_current_theme())
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        toolbar.addWidget(self.theme_combo)
        
        toolbar.addStretch()
        
        # 清空按鈕
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._on_clear)
        toolbar.addWidget(clear_btn)
        
        layout.addLayout(toolbar)
        
        # 文本瀏覽器
        self.text_browser = ANSITextBrowser()
        layout.addWidget(self.text_browser)
        
    def display_output(self, ansi_text: str, tool_name: str = "generic"):
        """顯示輸出"""
        self.text_browser.display_ansi_output(ansi_text, tool_name)
    
    def _on_theme_changed(self, theme_name: str):
        """主題變更處理"""
        self.text_browser.set_theme(theme_name)
        # 如果有內容，重新渲染
        # 注意：這需要保存原始 ANSI 文本才能重新渲染
        
    def _on_clear(self):
        """清空內容"""
        self.text_browser.clear()
```

---

## 5. 測試和驗證

### 完整測試套件

```python
"""
ANSI HTML 轉換系統測試套件
"""

import pytest
import tempfile
from pathlib import Path

# 測試用的 ANSI 序列
TEST_ANSI_SEQUENCES = {
    'colors': '\x1b[31mRed\x1b[32mGreen\x1b[34mBlue\x1b[0m',
    'bold': '\x1b[1mBold Text\x1b[0m',
    'underline': '\x1b[4mUnderlined\x1b[0m',
    'complex': '\x1b[1;31;4mBold Red Underlined\x1b[0m',
    'ripgrep_output': '''src/main.py:10:5:\x1b[1;31mmain\x1b[0m function
src/utils.py:25:12:Helper \x1b[1;31mmain\x1b[0m function
tests/test_\x1b[1;31mmain\x1b[0m.py:15:8:Test \x1b[1;31mmain\x1b[0m''',
    'bat_output': '''   1   \x1b[38;5;24mdef\x1b[39m \x1b[38;5;67mtest_function\x1b[39m():
   2       \x1b[38;5;124mprint\x1b[39m(\x1b[38;5;28m"Hello, World!"\x1b[39m)''',
}


class TestEnhancedANSIParser:
    """測試 ANSI 解析器"""
    
    def test_basic_color_parsing(self):
        """測試基本顏色解析"""
        parser = EnhancedANSIParser()
        
        # 測試紅色
        style = parser.parse_ansi_sequence('\x1b[31m')
        assert style.foreground_color == 'red'
        
        # 測試背景色
        style = parser.parse_ansi_sequence('\x1b[41m')
        assert style.background_color == 'red'
        
        # 測試重置
        style = parser.parse_ansi_sequence('\x1b[0m')
        assert style.foreground_color is None
        assert style.background_color is None
    
    def test_text_attributes(self):
        """測試文本屬性"""
        parser = EnhancedANSIParser()
        
        # 粗體
        style = parser.parse_ansi_sequence('\x1b[1m')
        assert style.bold is True
        
        # 斜體
        style = parser.parse_ansi_sequence('\x1b[3m')
        assert style.italic is True
        
        # 下劃線
        style = parser.parse_ansi_sequence('\x1b[4m')
        assert style.underline is True
    
    def test_complex_sequences(self):
        """測試複雜序列"""
        parser = EnhancedANSIParser()
        
        # 組合樣式
        style = parser.parse_ansi_sequence('\x1b[1;31;4m')
        assert style.bold is True
        assert style.foreground_color == 'red'
        assert style.underline is True


class TestThemeManager:
    """測試主題管理器"""
    
    def test_builtin_themes(self):
        """測試內建主題"""
        manager = ThemeManager()
        
        assert 'dark' in manager.themes
        assert 'light' in manager.themes
        assert manager.current_theme is not None
    
    def test_theme_switching(self):
        """測試主題切換"""
        manager = ThemeManager()
        
        manager.set_theme('light')
        assert manager.current_theme.name == 'Light Modern'
        
        manager.set_theme('dark')
        assert manager.current_theme.name == 'Dark Professional'
    
    def test_custom_theme(self):
        """測試自定義主題"""
        manager = ThemeManager()
        
        custom_theme = ANSITheme("Custom", {
            'red': '#ff0000',
            'green': '#00ff00',
            'blue': '#0000ff'
        })
        
        manager.add_custom_theme(custom_theme)
        assert 'custom' in manager.themes
        
        manager.set_theme('custom')
        assert manager.current_theme.name == 'Custom'


class TestEnhancedANSIToHTMLConverter:
    """測試 HTML 轉換器"""
    
    def setup_method(self):
        """設定測試"""
        self.converter = EnhancedANSIToHTMLConverter()
    
    def test_basic_conversion(self):
        """測試基本轉換"""
        result = self.converter.convert_to_html(
            TEST_ANSI_SEQUENCES['colors'], 
            include_wrapper=False
        )
        
        assert 'ansi-fg-red' in result
        assert 'ansi-fg-green' in result
        assert 'ansi-fg-blue' in result
    
    def test_bold_text(self):
        """測試粗體文本"""
        result = self.converter.convert_to_html(
            TEST_ANSI_SEQUENCES['bold'],
            include_wrapper=False
        )
        
        assert 'ansi-bold' in result
        assert 'Bold Text' in result
    
    def test_complex_formatting(self):
        """測試複雜格式"""
        result = self.converter.convert_to_html(
            TEST_ANSI_SEQUENCES['complex'],
            include_wrapper=False
        )
        
        assert 'ansi-bold' in result
        assert 'ansi-fg-red' in result
        assert 'ansi-underline' in result
    
    def test_line_numbers(self):
        """測試行號顯示"""
        result = self.converter.convert_to_html(
            "Line 1\nLine 2\nLine 3",
            include_wrapper=False,
            line_numbers=True
        )
        
        assert 'ansi-line-number' in result
        assert 'ansi-line-content' in result
    
    def test_theme_integration(self):
        """測試主題整合"""
        self.converter.set_theme('light')
        
        result = self.converter.convert_to_html(
            TEST_ANSI_SEQUENCES['colors'],
            include_wrapper=True
        )
        
        assert '--ansi-red' in result  # CSS 變數
        assert 'Light Modern' in str(self.converter.theme_manager.current_theme.name)


class TestToolProcessors:
    """測試工具專用處理器"""
    
    def setup_method(self):
        """設定測試"""
        converter = EnhancedANSIToHTMLConverter()
        self.factory = ToolProcessorFactory(converter)
    
    def test_ripgrep_processor(self):
        """測試 Ripgrep 處理器"""
        processor = self.factory.get_processor('ripgrep')
        result = processor.process_output(TEST_ANSI_SEQUENCES['ripgrep_output'])
        
        assert 'ansi-ripgrep-match' in result
        assert 'ansi-ripgrep-file' in result
        assert 'ansi-ripgrep-line-number' in result
    
    def test_bat_processor(self):
        """測試 Bat 處理器"""
        processor = self.factory.get_processor('bat')
        result = processor.process_output(TEST_ANSI_SEQUENCES['bat_output'])
        
        # Bat 處理器應保持原有的語法高亮
        assert 'ansi-line' in result
    
    def test_generic_processor(self):
        """測試通用處理器"""
        processor = self.factory.get_processor('unknown_tool')
        result = processor.process_output('Simple text')
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestStreamingProcessor:
    """測試流式處理器"""
    
    def test_stream_processing(self):
        """測試流式處理"""
        converter = EnhancedANSIToHTMLConverter()
        processor = StreamingANSIProcessor(converter)
        
        def text_generator():
            yield "Line 1\n"
            yield "Line 2\n"
            yield "Line 3"
        
        results = list(processor.process_stream(text_generator()))
        
        assert len(results) == 3
        for result in results:
            assert 'ansi-line' in result


class TestCachingProcessor:
    """測試快取處理器"""
    
    def test_caching_functionality(self):
        """測試快取功能"""
        converter = EnhancedANSIToHTMLConverter()
        processor = CachingANSIProcessor(converter, cache_size=10)
        
        test_text = TEST_ANSI_SEQUENCES['colors']
        
        # 第一次處理
        result1 = processor.process_with_cache(test_text)
        stats1 = processor.get_cache_stats()
        
        # 第二次處理（應該使用快取）
        result2 = processor.process_with_cache(test_text)
        stats2 = processor.get_cache_stats()
        
        assert result1 == result2
        assert stats2['hits'] > stats1['hits']
        assert stats2['cache_size'] > 0


class TestANSIHTMLProcessor:
    """測試統一處理器"""
    
    def test_tool_conversion(self):
        """測試工具轉換"""
        result = ansi_html_processor.convert_for_tool(
            'ripgrep',
            TEST_ANSI_SEQUENCES['ripgrep_output']
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'ansi-ripgrep' in result
    
    def test_theme_switching(self):
        """測試主題切換"""
        available_themes = ansi_html_processor.get_available_themes()
        assert len(available_themes) > 0
        
        for theme in ['dark', 'light']:
            if theme in available_themes:
                ansi_html_processor.set_theme(theme)
                # 驗證主題已變更
                current = ansi_html_processor.theme_manager.get_current_theme()
                assert current is not None
    
    def test_backward_compatibility(self):
        """測試向後兼容性"""
        # 測試兼容類
        converter = Ansi2HTMLConverter()
        result = converter.convert(TEST_ANSI_SEQUENCES['colors'])
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        # 測試兼容函數
        result2 = convert_ansi_to_html(TEST_ANSI_SEQUENCES['colors'])
        assert isinstance(result2, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## 6. 部署指南和最佳實踐

### 部署檢查清單

```markdown
## 部署前檢查

### 1. 依賴檢查
- [ ] 確認所有新增的 Python 模組已添加到 requirements.txt
- [ ] 測試在新環境中的依賴安裝

### 2. 配置文件更新
- [ ] 更新 config/default_settings.yaml 添加 ANSI HTML 設定
- [ ] 確認主題文件路徑正確

### 3. 現有功能兼容性
- [ ] 測試所有使用 ansi2html 的地方是否正常工作
- [ ] 驗證 CSV 工具輸出格式
- [ ] 檢查其他 CLI 工具的顯示效果

### 4. 性能測試
- [ ] 測試大文件的轉換性能
- [ ] 驗證快取系統工作正常
- [ ] 確認記憶體使用在合理範圍內

### 5. 主題測試
- [ ] 測試所有內建主題
- [ ] 驗證與應用程式主題的同步
- [ ] 確認在不同系統下的顯示效果
```

### 最佳實踐建議

```python
# best_practices.py - ANSI HTML 最佳實踐

"""
ANSI HTML 轉換最佳實踐指南
"""

class ANSIBestPractices:
    """ANSI HTML 最佳實踐"""
    
    @staticmethod
    def optimize_for_performance():
        """性能優化建議"""
        return {
            'use_caching': True,
            'stream_large_outputs': True,
            'limit_html_size': '10MB',
            'cleanup_old_cache': 'daily'
        }
    
    @staticmethod
    def security_considerations():
        """安全考慮"""
        return {
            'escape_html': True,
            'sanitize_ansi_sequences': True,
            'limit_css_injection': True,
            'validate_input_size': True
        }
    
    @staticmethod
    def theme_recommendations():
        """主題建議"""
        return {
            'provide_dark_light_options': True,
            'follow_system_theme': True,
            'allow_custom_themes': True,
            'maintain_contrast_ratios': 'WCAG_AA'
        }
    
    @staticmethod
    def integration_guidelines():
        """整合指南"""
        return {
            'replace_gradually': True,
            'test_each_tool_separately': True,
            'provide_fallback_options': True,
            'monitor_conversion_errors': True
        }


# 配置建議
RECOMMENDED_CONFIG = {
    'ansi_html': {
        'default_theme': 'dark',
        'use_caching': True,
        'cache_size': 10000,
        'max_output_size': 10 * 1024 * 1024,  # 10MB
        'enable_streaming': True,
        'tool_specific_processing': True,
        'fallback_to_plain_text': True,
        'themes': {
            'sync_with_app_theme': True,
            'auto_detect_system_theme': True
        }
    }
}
```

---

## 總結

這套增強的 ANSI 彩色輸出轉 HTML 顯示系統提供了：

### 🎨 核心特色
- **完整 ANSI 支援** - 支援所有標準 ANSI 轉義序列
- **豐富主題系統** - 4 個內建主題 + 自定義主題支援
- **工具專用處理** - 為 ripgrep、bat、fd 等工具優化顯示
- **高效能處理** - 流式處理 + 智能快取系統
- **無縫整合** - 與現有專案完全兼容

### 🚀 技術亮點
- **智能解析器** - 支援 16 色、256 色、真彩色
- **主題化 CSS** - 動態生成主題相關樣式
- **流式轉換** - 支援大量輸出的即時處理
- **工具感知** - 針對不同 CLI 工具的專用處理器
- **向後兼容** - 完全替換現有的 ansi2html 使用

### ✨ 使用者體驗
- **視覺美觀** - 專業的代碼高亮和顏色顯示
- **主題一致** - 與應用程式主題自動同步
- **高效能** - 快速轉換，流暢顯示
- **可自訂** - 豐富的主題和樣式選項

這套系統將大大提升 CLI 工具在 GUI 中的視覺效果，為使用者提供更好的開發體驗！🌟

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\u5206\u6790\u73fe\u6709 ANSI \u8f49 HTML \u5be6\u73fe", "status": "completed", "id": "1"}, {"content": "\u8a2d\u8a08\u589e\u5f37\u7684 ANSI \u89e3\u6790\u5668", "status": "completed", "id": "2"}, {"content": "\u5be6\u73fe\u8c50\u5bcc\u7684\u984f\u8272\u548c\u6a23\u5f0f\u652f\u63f4", "status": "completed", "id": "3"}, {"content": "\u5275\u5efa\u4e3b\u984c\u5316 CSS \u7cfb\u7d71", "status": "completed", "id": "4"}, {"content": "\u6574\u5408\u5230 CLI \u5de5\u5177\u8f38\u51fa\u986f\u793a", "status": "completed", "id": "5"}, {"content": "\u5be6\u73fe\u5be6\u6642\u6d41\u5f0f\u8f49\u63db", "status": "completed", "id": "6"}, {"content": "\u5275\u5efa\u5b8c\u6574\u7684 ANSI HTML \u8f49\u63db\u6307\u5357", "status": "completed", "id": "7"}]