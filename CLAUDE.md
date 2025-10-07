# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This is a Python project for parsing course progress data from PDF activity logs. The project uses `pyproject.toml` for configuration and provides a comprehensive CLI for PDF text extraction, course data parsing, and Excel export.

## Current State

- Directory: `/Users/xiaobin/project/ma_new`
- Status: Active Python project with PDF parsing CLI tools
- Package: `ma_log_pdf_parser` version 0.1.0
- Virtual environment: `venv/` (Python 3.9+)
- Key dependency: pdfplumber>=0.9.0 for PDF processing

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Lint code with Flake8
flake8 src/ tests/

# Type check with MyPy
mypy src/
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run single test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_hello
```

### Running the Application
```bash
# Show CLI help
ma_log_pdf_parser --help

# Get PDF information
ma_log_pdf_parser info document.pdf

# Extract text from PDF
ma_log_pdf_parser text document.pdf

# Extract text by page to file
ma_log_pdf_parser text document.pdf --pages --output text_by_page.json

# Extract tables from PDF
ma_log_pdf_parser tables document.pdf

# Search for text in PDF
ma_log_pdf_parser search document.pdf "search term"

# Extract text with position data
ma_log_pdf_parser positions document.pdf --output positions.json

# Export course data to Excel
ma_log_pdf_parser export document.pdf output.xlsx
```

## Project Architecture

### Directory Structure
- `src/ma_log_pdf_parser/` - Main package source code
- `tests/` - Test files (pytest)
- `venv/` - Virtual environment (gitignored)
- `pyproject.toml` - Project configuration and dependencies
- `.gitignore` - Git ignore rules for Python

### Key Files
- `src/ma_log_pdf_parser/main.py` - Main CLI application with PDF parsing commands
- `src/ma_log_pdf_parser/pdf_parser.py` - Core PDF parsing functionality using pdfplumber
- `src/ma_log_pdf_parser/course_parser.py` - Course progress data extraction
- `src/ma_log_pdf_parser/__init__.py` - Package initialization with version
- `requirements.txt` - Core dependencies including pdfplumber
- `requirements-dev.txt` - Development dependencies

### Configuration
- **pyproject.toml**: Modern Python project configuration with:
  - setuptools build backend
  - project metadata and dependencies
  - tool configurations (black, mypy, pytest)
  - CLI entry point: `ma_log_pdf_parser = "ma_log_pdf_parser.main:main"`

## Core Functionality

### PDFParser Class (`src/ma_log_pdf_parser/pdf_parser.py`)
- `extract_text()` - Extract all text from PDF
- `extract_text_by_page()` - Extract text page by page
- `extract_tables()` - Extract all tables from PDF
- `extract_tables_by_page()` - Extract tables page by page
- `get_metadata()` - Get PDF metadata
- `get_page_count()` - Get total page count
- `extract_text_with_positions()` - Extract text with coordinates
- `search_text()` - Search for specific text in PDF

### CLI Commands (`src/ma_log_pdf_parser/main.py`)
- `ma_log_pdf_parser info <pdf>` - Display PDF metadata and page count
- `ma_log_pdf_parser text <pdf> [--output file] [--pages]` - Extract text
- `ma_log_pdf_parser tables <pdf> [--output file] [--pages]` - Extract tables
- `ma_log_pdf_parser search <pdf> <term> [--output file]` - Search text
- `ma_log_pdf_parser positions <pdf> [--output file]` - Extract text positions
- `ma_log_pdf_parser export <pdf> <output>` - Export course data to Excel

## Development Workflow

1. Always work with virtual environment activated: `source venv/bin/activate`
2. Install changes: `pip install -e .` after modifying `pyproject.toml`
3. Run tests before committing: `pytest`
4. Format code: `black .`
5. Type check: `mypy src/`

## PDF Processing Notes

- Uses pdfplumber for reliable PDF text extraction
- Handles both text-based and scanned PDFs (OCR not included)
- Supports table extraction with position data
- Provides comprehensive text search functionality
- All commands support output to file for large results