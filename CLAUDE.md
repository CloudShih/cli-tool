# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A PyQt5-based GUI application that integrates multiple CLI tools into a unified interface. The application follows an MVC architecture pattern with tools for file search (`fd`), text search (`ripgrep`), markdown viewing (`glow`), document conversion (`pandoc`), PDF manipulation (`poppler`), and syntax highlighting (`bat`).

## Architecture

### Core Structure
- **Main Application**: `main_app.py` - Entry point with tabbed interface and dark theme
- **Tools System**: Modular MVC pattern in `tools/` directory
  - `tools/fd/` - File search tool wrapper for the `fd` command-line utility
  - `tools/ripgrep/` - Text search tool with advanced pattern matching using ripgrep
  - `tools/glow/` - Markdown viewer with theme support using glow
  - `tools/pandoc/` - Universal document converter using pandoc
  - `tools/poppler/` - PDF manipulation tools using Poppler utilities and QPDF
  - `tools/bat/` - Syntax highlighting file viewer using bat
  - `tools/glances/` - System monitoring tool for real-time resource tracking
  - `tools/csvkit/` - CSV data processing toolkit with multiple utilities
  - `tools/dust/` - Disk space analyzer with tree-like visualization
- **Utilities**: `pdf_decryptor.py` - Standalone PDF decryption utility using pikepdf

### MVC Pattern Implementation
Each tool follows strict MVC separation:
- **Model**: Business logic and external command execution
- **View**: PyQt5 UI components and user interactions  
- **Controller**: Connects view events to model operations

### Key Dependencies
- **PyQt5**: GUI framework with dark theme styling
- **ansi2html**: Converts command-line output to HTML for display
- **pikepdf**: PDF manipulation and decryption
- **subprocess**: External tool execution
- **pytest**: Testing framework

## Running the Application

### Main Application
```bash
# Run the main GUI application
python main_app.py
```

### Standalone PDF Decryptor
```bash
# Run the PDF decryptor utility
python pdf_decryptor.py
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/cli_tool/test_pdf_decryptor.py
pytest tests/cli_tool/tools/poppler/test_poppler_model.py

# Run with verbose output
pytest -v tests/
```

### Test Structure
- Tests mirror the source structure under `tests/cli_tool/`
- Uses pytest fixtures for setup and teardown
- Mock external dependencies and file operations

## External Dependencies

### Required CLI Tools
The application wraps these external command-line tools:

**fd Tool**:
- Path configured in `FdModel`: `C:\Users\cloudchshih\AppData\Local\Microsoft\WinGet\Packages\sharkdp.fd_Microsoft.WinGet.Source_8wekyb3d8bbwe\fd-v10.2.0-x86_64-pc-windows-msvc\fd.exe`
- Used for fast file and directory searching

**ripgrep (rg) Tool**:
- Expected in system PATH or configurable path
- Ultra-fast text search with regex support and multiple output formats
- Unicode-aware with proper UTF-8 encoding handling

**Poppler Utils**: Expected in system PATH
- `pdfinfo` - PDF metadata extraction
- `pdftotext` - PDF to text conversion
- `pdfimages` - Image extraction from PDFs
- `pdfseparate` - Split PDF pages
- `pdfunite` - Merge PDF files
- `pdftoppm` - PDF to image conversion
- `pdftohtml` - PDF to HTML conversion

**QPDF**: Used for PDF decryption
- `qpdf` - Advanced PDF manipulation

**Glow**: Expected in system PATH
- `glow` - Terminal markdown reader with styling

**Pandoc**: Expected in system PATH  
- `pandoc` - Universal document converter

**Bat**: Expected in system PATH
- `bat` - Syntax highlighting file viewer

**Glances**: Expected in system PATH or via pip
- `glances` - System monitoring tool for real-time performance metrics

**csvkit**: Expected via pip installation
- `in2csv`, `csvcut`, `csvgrep`, `csvstat`, `csvlook`, `csvjoin`, etc. - CSV processing utilities

**dust**: Expected in system PATH
- `dust` - Fast disk usage analyzer

## Architecture Patterns

### Command Execution Pattern
All external tool integrations follow this pattern:
1. Build command array with proper arguments
2. Execute via `subprocess.Popen` with explicit UTF-8 encoding and error handling
3. Convert output to HTML using `ansi2html` for GUI display
4. Handle errors gracefully with user-friendly messages

**Critical Encoding Configuration**:
```python
subprocess.Popen(command, 
    encoding='utf-8',      # Force UTF-8 encoding
    errors='replace',      # Handle encoding errors gracefully
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

### GUI State Management
- Button state changes during operations (disabled with "wait..." text)
- Real-time UI updates using `QApplication.processEvents()`
- Consistent dark theme styling applied at application level

### Error Handling Strategy
- FileNotFoundError for missing external tools
- UnicodeDecodeError for encoding issues
- Graceful degradation with informative error messages
- All errors converted to HTML for consistent display

## Development Guidelines

### Adding New Tools
1. Create new directory under `tools/` with MVC structure
2. Implement model class with `_execute_command()` method
3. Create PyQt5 view with consistent styling
4. Connect view and model through controller
5. Add tab to main application
6. Include comprehensive tests

### External Tool Integration
- Validate tool availability before use
- Use absolute paths or PATH-based execution
- Convert all output to HTML for GUI display
- Handle encoding issues and special characters
- Provide clear error messages for missing dependencies

### Testing New Features
- Create fixtures for temporary files and directories
- Mock external command execution where appropriate
- Test both success and failure scenarios
- Validate file operations and cleanup