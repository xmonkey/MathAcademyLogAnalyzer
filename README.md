# MathAcademyLogAnalyzer

[English](#english) | [中文](#中文)

---

## English

MathAcademyLogAnalyzer is a Python tool for analyzing course progress data from Math Academy PDF activity logs, built with Claude Code.

*Inspired by [rng.eth](https://x.com/crackedmonk/status/1962663418089107666)*

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
# Extract course data to Excel
mathacademy-analyzer export activity_log.pdf output.xlsx

# Generate analysis and charts
mathacademy-analyzer chart output.xlsx --chart-type dashboard

# View XP statistics
mathacademy-analyzer stats output.xlsx
```

## Get Help
```bash
# Show all available commands
mathacademy-analyzer --help
```

---

*Documentation optimized with Claude Code*

---

## 中文

MathAcademyLogAnalyzer 是一个用于分析 Math Academy PDF 活动日志中课程进度数据的 Python 工具。

## 快速开始

### 1. 安装
```bash
# 克隆并安装
git clone <repository-url>
cd MathAcademyLogAnalyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 2. 下载活动日志 PDF
1. 使用家长账户登录 [mathacademy.com](https://mathacademy.com)
2. 点击学生设置图标 (⚙️) → "Documentation"
3. 在 "Activity Log" 下点击 "Request..."
4. 设置时间范围（建议：从第一天学习开始）
5. 点击 "Preview" → 下载 PDF

### 3. 分析并生成图表
```bash
# 提取课程数据到 Excel
mathacademy-analyzer export activity_log.pdf output.xlsx

# 生成分析和图表
mathacademy-analyzer chart output.xlsx --chart-type dashboard

# 查看 XP 统计
mathacademy-analyzer stats output.xlsx
```

## 其他实用命令
```bash
# 显示所有命令
mathacademy-analyzer --help

# 获取 PDF 信息
mathacademy-analyzer info activity_log.pdf

# 提取文本
mathacademy-analyzer text activity_log.pdf

# 搜索特定内容
mathacademy-analyzer search activity_log.pdf "搜索词"
```