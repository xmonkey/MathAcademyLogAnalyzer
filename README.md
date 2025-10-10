# MathAcademyLogAnalyzer

MathAcademyLogAnalyzer is a Python tool for analyzing course progress data from mathacademy.com's PDF activity logs, built with Claude Code.

*Inspired by [rng.eth](https://x.com/crackedmonk/status/1962663418089107666)*

[中文文档](README_zh.md)

## Quick Start

### 1. Install
```bash
# Clone and install
git clone https://github.com/xmonkey/MathAcademyLogAnalyzer.git
cd MathAcademyLogAnalyzer
pip install -e .
```

**Windows users:**
```cmd
pip install -e .
```

### 2. Download Activity Log PDF
1. Log in to [mathacademy.com](https://mathacademy.com) with parent account
2. Click student's settings icon (⚙️) → "Documentation"
3. Under "Activity Log", click "Request..."
4. Set time frame (recommended: from first day of learning)
5. Click "Preview" → Download PDF

### 3. Analyze
```bash
# Option 1: Quick analysis
mathacademy-analyzer export activity_log.pdf output.xlsx
mathacademy-analyzer chart output.json

# Option 2: Generate all outputs at once (Recommended)
mathacademy-analyzer generate-all activity_log.pdf -o output_folder

# View statistics
mathacademy-analyzer stats output.json
```

## Output Formats
- **Interactive HTML** (default): Interactive charts with zoom, hover, and tooltips
- **Static PNG**: Static image files suitable for documents and sharing
- **Excel**: Structured data with course details and activity logs
- **JSON**: Raw data for custom analysis

## Generate All Command

The `generate-all` command creates comprehensive analysis with all output formats:

```bash
mathacademy-analyzer generate-all activity_log.pdf -o analysis_results
```

**Generated files:**
- `data.json` - Raw extracted data
- `export.xlsx` - Excel with course details and activities
- `comprehensive_dashboard.html` - Interactive web dashboard
- `cumulative_xp.png` - Cumulative XP progress chart
- `daily_xp.png` - Daily XP distribution chart
- `task_types.png` - Task type distribution chart
- `weekly_activity.png` - Weekly activity pattern chart
- `efficiency.png` - Learning efficiency trend chart
- `weekday_distribution.png` - Weekday learning pattern chart
- `daily_xp_distribution.png` - Daily XP histogram chart
- `weekly_daily_stats.png` - Weekly and daily statistics chart

**Options:**
- `--output-dir, -o` - Output directory (default: current directory)
- `--name, -n` - Base name for generated files
- `--static-only` - Generate only static charts
- `--interactive-only` - Generate only interactive charts
- `--data-only` - Generate only data files (Excel/JSON)
- `--charts-only` - Generate only chart files

## More Useful Commands
```bash
# Get PDF information
mathacademy-analyzer info activity_log.pdf

# Extract text or tables
mathacademy-analyzer text activity_log.pdf
mathacademy-analyzer tables activity_log.pdf

# Search content
mathacademy-analyzer search activity_log.pdf "search term"

# Generate specific chart types
mathacademy-analyzer chart data.json --chart-type cumulative_xp
mathacademy-analyzer chart data.json --chart-type dashboard
```

## Global Installation (Optional)

Install from any directory to use globally:

```bash
cd MathAcademyLogAnalyzer
python3 -m pip install -e .
```

## Upgrade

```bash
# Get latest code
git pull

# Reinstall
pip install -e .
```

## Troubleshooting

**Command not found?**
```bash
# Remove old version first
pip uninstall ma-log-pdf-parser -y

# Reinstall
python3 -m pip install -e .
```

---

*Documentation optimized with Claude Code*