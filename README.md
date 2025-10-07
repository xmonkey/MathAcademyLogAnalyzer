# MathAcademyLogAnalyzer

MathAcademyLogAnalyzer is a Python tool for analyzing course progress data from mathacademy.com's PDF activity logs, built with Claude Code.

*Inspired by [rng.eth](https://x.com/crackedmonk/status/1962663418089107666)*

[中文文档](README_zh.md)

## Quick Start

### 1. Installation
```bash
# Clone and install
git clone <repository-url>
cd MathAcademyLogAnalyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 2. Download Activity Log PDF
1. Log in to [mathacademy.com](https://mathacademy.com) with parent account
2. Click student's settings icon (⚙️) → "Documentation"
3. Under "Activity Log", click "Request..."
4. Set time frame (recommended: from first day of learning)
5. Click "Preview" → Download PDF

### 3. Analyze and Generate Charts
```bash
# Extract course data to Excel and JSON
mathacademy-analyzer export activity_log.pdf output.xlsx

# Generate interactive HTML charts (default)
mathacademy-analyzer chart output.json --output ./charts/

# Generate static PNG images
mathacademy-analyzer chart output.json --static --output ./charts/

# View XP statistics
mathacademy-analyzer stats output.json
```

## Output Formats
- **Interactive HTML** (default): Interactive charts with zoom, hover, and tooltips
- **Static PNG**: Static image files suitable for documents and sharing

## More Useful Commands
```bash
# Get PDF information
mathacademy-analyzer info activity_log.pdf

# Extract text or tables
mathacademy-analyzer text activity_log.pdf
mathacademy-analyzer tables activity_log.pdf

# Search content
mathacademy-analyzer search activity_log.pdf "search term"
```

---

*Documentation optimized with Claude Code*