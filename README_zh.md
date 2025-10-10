# MathAcademyLogAnalyzer

MathAcademyLogAnalyzer 是一个用于分析 mathacademy.com PDF 活动日志中课程进度数据的 Python 工具。

*灵感来源于 [rng.eth](https://x.com/crackedmonk/status/1962663418089107666)*

[English Documentation](README.md)

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
# 选项1：逐步分析
mathacademy-analyzer export activity_log.pdf output.xlsx
mathacademy-analyzer chart output.json

# 选项2：一键生成所有输出（推荐）
mathacademy-analyzer generate-all activity_log.pdf -o analysis_results

# 查看 XP 统计
mathacademy-analyzer stats output.json
```

## 输出格式
- **交互式HTML**（默认）：支持缩放、悬停和提示的交互图表
- **静态PNG**：适合文档和分享的静态图片文件
- **Excel**：包含课程详情和活动日志的结构化数据
- **JSON**：用于自定义分析的原始数据

## Generate All 命令

`generate-all` 命令创建包含所有输出格式的综合分析：

```bash
mathacademy-analyzer generate-all activity_log.pdf -o analysis_results
```

**生成的文件：**
- `data.json` - 原始提取数据
- `export.xlsx` - Excel 格式的课程详情和活动记录
- `comprehensive_dashboard.html` - 交互式网页仪表板
- `cumulative_xp.png` - 累积 XP 进度图表
- `daily_xp.png` - 每日 XP 分布图表
- `task_types.png` - 任务类型分布图表
- `weekly_activity.png` - 每周活动模式图表
- `efficiency.png` - 学习效率趋势图表
- `weekday_distribution.png` - 工作日学习模式图表
- `daily_xp_distribution.png` - 每日 XP 直方图
- `weekly_daily_stats.png` - 每周和每日统计图表

**选项：**
- `--output-dir, -o` - 输出目录（默认：当前目录）
- `--name, -n` - 生成文件的基础名称
- `--static-only` - 仅生成静态图表
- `--interactive-only` - 仅生成交互式图表
- `--data-only` - 仅生成数据文件（Excel/JSON）
- `--charts-only` - 仅生成图表文件

## 更多实用命令
```bash
# 获取 PDF 信息
mathacademy-analyzer info activity_log.pdf

# 提取文本或表格
mathacademy-analyzer text activity_log.pdf
mathacademy-analyzer tables activity_log.pdf

# 搜索内容
mathacademy-analyzer search activity_log.pdf "搜索词"

# 生成特定类型的图表
mathacademy-analyzer chart data.json --chart-type cumulative_xp
mathacademy-analyzer chart data.json --chart-type dashboard
```

---

*文档由 Claude Code 优化*