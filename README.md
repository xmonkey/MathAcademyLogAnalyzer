# MathAcademyLogAnalyzer

[English](#english) | [中文](#中文)

---

## English

MathAcademyLogAnalyzer is a Python tool for parsing and analyzing course progress data from Math Academy PDF activity logs. It provides comprehensive CLI commands for PDF text extraction, course data parsing, and Excel export functionality.

## Features

- **PDF Text Extraction**: Extract text content from Math Academy activity logs
- **Data Analysis**: Parse course progress and performance data
- **Export Functionality**: Export structured data to Excel format
- **Interactive Charts**: Generate visualization charts and dashboards
- **Command Line Interface**: User-friendly CLI for all operations

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd MathAcademyLogAnalyzer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

## Getting Activity Logs from Math Academy

### How to Download PDF Activity Logs

Before using this tool, you need to download the activity log PDF from Math Academy:

1. **Log in to Parent/Supervising Account**
   - Go to [mathacademy.com](https://mathacademy.com)
   - Sign in with your parent or supervising account credentials

2. **Navigate to Student Settings**
   - Click on the student's settings icon (⚙️) next to their name
   - Select **"Documentation"** from the menu

3. **Request Activity Log**
   - Under **"Activity Log"** section, click **"Request..."**
   - Set your desired **Time Frame** (e.g., Last 30 days, Last 3 months, Custom range)
   - Click **"Preview"** to generate the activity log

4. **Download PDF**
   - Wait for the preview to load
   - Download the PDF file using your browser's download option
   - Save it with a descriptive name (e.g., `student_activity_log_2025-01.pdf`)

### Best Practices
- **File Naming**: Use descriptive names to easily identify different reports
- **Time Frame**: Include the learning period you want to analyze, recommended to start from the first day of learning

## Usage

### Basic Commands
```bash
# Show help
mathacademy-analyzer --help

# Get PDF information
mathacademy-analyzer info activity_log.pdf

# Extract text from PDF
mathacademy-analyzer text activity_log.pdf

# Extract tables from PDF
mathacademy-analyzer tables activity_log.pdf

# Search for specific text
mathacademy-analyzer search activity_log.pdf "search term"

# Export course data to Excel
mathacademy-analyzer export activity_log.pdf output.xlsx

# Extract text with position data
mathacademy-analyzer positions activity_log.pdf --output positions.json
```

### Advanced Features
```bash
# Extract text by pages
mathacademy-analyzer text activity_log.pdf --pages --output text_by_page.json

# Generate comprehensive analysis
python generate_analysis.py activity_log.pdf

# Create visualization charts
python simple_charts.py
```

## Project Structure

```
MathAcademyLogAnalyzer/
├── src/ma_log_pdf_parser/          # Main package source code
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # CLI application entry point
│   ├── pdf_parser.py               # Core PDF parsing functionality
│   ├── course_parser.py            # Course data extraction logic
│   └── chart_generator.py          # Chart and visualization generation
├── tests/                          # Test files
├── docs/                           # Documentation
├── data/                           # Sample data
├── output/                         # Generated outputs
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Core dependencies
├── requirements-dev.txt            # Development dependencies
└── README.md                       # This file
```

## Development

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

### Dependencies
- **pdfplumber**: PDF text extraction
- **openpyxl**: Excel file handling
- **pandas**: Data manipulation
- **matplotlib**: Plotting
- **plotly**: Interactive charts
- **click**: CLI framework

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.

---

## 中文

MathAcademyLogAnalyzer 是一个用于解析和分析 Math Academy PDF 活动日志中课程进度数据的 Python 工具。它提供全面的 CLI 命令，支持 PDF 文本提取、课程数据解析和 Excel 导出功能。

## 功能特性

- **PDF 文本提取**：从 Math Academy 活动日志中提取文本内容
- **数据分析**：解析课程进度和表现数据
- **导出功能**：将结构化数据导出为 Excel 格式
- **交互式图表**：生成可视化图表和仪表板
- **命令行界面**：为所有操作提供用户友好的 CLI

## 安装

### 系统要求
- Python 3.8 或更高版本
- 虚拟环境（推荐）

### 设置步骤
```bash
# 克隆仓库
git clone <repository-url>
cd MathAcademyLogAnalyzer

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装包
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

## 使用方法

### 基本命令
```bash
# 显示帮助
mathacademy-analyzer --help

# 获取 PDF 信息
mathacademy-analyzer info activity_log.pdf

# 从 PDF 提取文本
mathacademy-analyzer text activity_log.pdf

# 从 PDF 提取表格
mathacademy-analyzer tables activity_log.pdf

# 搜索特定文本
mathacademy-analyzer search activity_log.pdf "搜索词"

# 导出课程数据到 Excel
mathacademy-analyzer export activity_log.pdf output.xlsx

# 提取带位置数据的文本
mathacademy-analyzer positions activity_log.pdf --output positions.json
```

### 高级功能
```bash
# 按页面提取文本
mathacademy-analyzer text activity_log.pdf --pages --output text_by_page.json

# 生成综合分析
python generate_analysis.py activity_log.pdf

# 创建可视化图表
python simple_charts.py
```

## 项目结构

```
MathAcademyLogAnalyzer/
├── src/ma_log_pdf_parser/          # 主要包源代码
│   ├── __init__.py                 # 包初始化
│   ├── main.py                     # CLI 应用程序入口点
│   ├── pdf_parser.py               # 核心 PDF 解析功能
│   ├── course_parser.py            # 课程数据提取逻辑
│   └── chart_generator.py          # 图表和可视化生成
├── tests/                          # 测试文件
├── docs/                           # 文档
├── data/                           # 示例数据
├── output/                         # 生成的输出
├── pyproject.toml                  # 项目配置
├── requirements.txt                # 核心依赖
├── requirements-dev.txt            # 开发依赖
└── README.md                       # 本文件
```

## 开发

### 代码质量
```bash
# 格式化代码
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=term-missing
```

### 依赖项
- **pdfplumber**：PDF 文本提取
- **openpyxl**：Excel 文件处理
- **pandas**：数据处理
- **matplotlib**：绘图
- **plotly**：交互式图表
- **click**：CLI 框架

## 许可证

MIT 许可证 - 详见 LICENSE 文件。

## 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 为新功能添加测试
5. 运行测试套件
6. 提交 pull request

## 支持

如有问题和疑问，请使用 GitHub 问题跟踪器。