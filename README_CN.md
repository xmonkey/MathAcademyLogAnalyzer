# MathAcademyLogAnalyzer

MathAcademyLogAnalyzer 是一个用于分析 Math Academy PDF 活动日志中课程进度数据的 Python 工具，由 Claude Code 构建。

*灵感来源于 [rng.eth](https://x.com/crackedmonk/status/1962663418089107666)*

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

## 获取帮助
```bash
# 显示所有可用命令
mathacademy-analyzer --help
```

---

*文档由 Claude Code 优化*