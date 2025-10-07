# MathAcademyLogAnalyzer

MathAcademyLogAnalyzer 是一个专门用于解析和分析 Math Academy PDF 活动日志中课程进度数据的 Python 工具。该工具提供了全面的命令行界面（CLI），支持 PDF 文本提取、课程数据解析、Excel 导出以及交互式图表生成功能。

## 核心功能

### 📄 PDF 处理能力
- **文本提取**：从 Math Academy 活动日志 PDF 中提取完整文本内容
- **表格解析**：智能识别和提取 PDF 中的表格数据
- **元数据获取**：读取 PDF 文件信息和页面数量
- **位置定位**：提取文本的精确坐标位置信息
- **全文搜索**：在 PDF 文档中快速查找特定内容

### 📊 数据分析与导出
- **课程进度解析**：自动识别课程名称、任务类型、XP 值等关键信息
- **多格式导出**：支持 Excel 和 JSON 两种主流数据格式
- **数据验证**：自动检测和处理数据异常，确保数据质量
- **统计分析**：提供详细的 XP 统计和学习效率分析

### 📈 可视化图表生成
- **7种图表类型**：包括 XP 趋势、任务分布、学习效率等
- **交互式仪表板**：所有图表整合到单个 HTML 页面
- **多种输出格式**：支持交互式 HTML 和静态 PNG 图表
- **响应式设计**：适配各种屏幕尺寸和设备

### 🖥️ 命令行界面
- **用户友好**：简洁直观的命令结构
- **帮助系统**：完整的帮助文档和使用示例
- **批处理支持**：支持批量处理多个 PDF 文件

## 系统要求

- **Python 版本**：3.8 或更高版本
- **操作系统**：Windows、macOS、Linux
- **内存要求**：建议 4GB 以上 RAM
- **存储空间**：至少 100MB 可用空间

## 安装指南

### 1. 环境准备
```bash
# 确保已安装 Python 3.8+
python --version

# 克隆项目仓库
git clone <repository-url>
cd MathAcademyLogAnalyzer
```

### 2. 虚拟环境设置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 安装依赖
```bash
# 安装核心功能
pip install -e .

# 安装开发工具（可选）
pip install -e ".[dev]"
```

### 4. 验证安装
```bash
# 检查工具是否正常工作
mathacademy-analyzer --help
```

## 使用教程

### 基础操作

#### 查看 PDF 信息
```bash
# 获取 PDF 文件基本信息
mathacademy-analyzer info activity_log.pdf

# 输出示例：
# 文件：activity_log.pdf
# 页数：15
# 创建时间：2025-01-15 10:30:45
# 大小：2.3 MB
```

#### 文本提取
```bash
# 提取全部文本
mathacademy-analyzer text activity_log.pdf

# 按页面提取并保存到文件
mathacademy-analyzer text activity_log.pdf --pages --output text_by_page.json

# 提取带位置信息的文本
mathacademy-analyzer positions activity_log.pdf --output positions.json
```

#### 表格提取
```bash
# 提取所有表格
mathacademy-analyzer tables activity_log.pdf

# 保存表格数据到文件
mathacademy-analyzer tables activity_log.pdf --output tables.json
```

#### 文本搜索
```bash
# 搜索特定文本
mathacademy-analyzer search activity_log.pdf "Quiz"

# 搜索并保存结果
mathacademy-analyzer search activity_log.pdf "Lesson" --output search_results.json
```

### 高级功能

#### 课程数据导出
```bash
# 导出为 Excel 格式
mathacademy-analyzer export activity_log.xlsx course_data.xlsx

# 导出为 JSON 格式
mathacademy-analyzer export activity_log.pdf --json-only output.json

# 同时导出两种格式
mathacademy-analyzer export activity_log.pdf output.xlsx
```

#### 图表生成
```bash
# 生成综合仪表板
mathacademy-analyzer chart course_data.json --chart-type dashboard

# 生成特定类型图表
mathacademy-analyzer chart course_data.json --chart-type xp          # XP 趋势图
mathacademy-analyzer chart course_data.json --chart-type task-type   # 任务类型分布
mathacademy-analyzer chart course_data.json --chart-type weekly-daily # 周/日对比
mathacademy-analyzer chart course_data.json --chart-type efficiency   # 学习效率
mathacademy-analyzer chart course_data.json --chart-type weekday     # 工作日分布
mathacademy-analyzer chart course_data.json --chart-type daily-dist  # 每日分布

# 生成静态图表
mathacademy-analyzer chart course_data.json --static

# 指定输出目录
mathacademy-analyzer chart course_data.json --output charts/
```

#### 统计分析
```bash
# 显示详细统计信息
mathacademy-analyzer stats course_data.json

# 输出包括：
# - 总 XP 获得
# - 学习天数
# - 平均每日 XP
# - 任务完成统计
# - 课程进度详情
```

## 图表类型详解

### 1. XP 趋势分析 (`xp`)
- **累计 XP 图表**：展示学习期间的累计 XP 增长曲线
- **每日 XP 图表**：显示每日获得的 XP 数量柱状图
- **XP 增长率**：计算和分析 XP 增长趋势

### 2. 任务类型分布 (`task-type`)
- **饼图分析**：不同任务类型的占比分布
- **任务类型**：Quiz、Lesson、Review、Multistep、Placement
- **详细统计**：各类型任务的数量和 XP 贡献

### 3. 周/日统计对比 (`weekly-daily`)
- **对比分析**：每周和每日的平均 XP 对比
- **趋势识别**：帮助发现学习模式的变化
- **周期性分析**：识别学习的周期性规律

### 4. 学习效率趋势 (`efficiency`)
- **效率曲线**：显示每个任务的平均 XP 变化
- **效率指标**：计算学习效率的综合指标
- **趋势预测**：基于历史数据预测效率趋势

### 5. 工作日学习模式 (`weekday`)
- **工作日分布**：周一到周日的学习活跃度
- **模式识别**：识别一周内的学习偏好
- **时间管理**：帮助优化学习时间安排

### 6. 每日 XP 分布 (`daily-dist`)
- **分布直方图**：每日 XP 数量的分布情况
- **强度分析**：学习强度的分布特征
- **异常检测**：识别学习强度异常的日期

### 7. 综合仪表板 (`dashboard`)
- **一体化展示**：所有图表整合到单个页面
- **性能卡片**：关键性能指标的可视化展示
- **响应式设计**：适配桌面和移动设备
- **交互功能**：支持图表间的交互和数据钻取

## 输出格式说明

### Excel 输出格式
生成的 Excel 文件包含多个工作表：

#### Course Progress 工作表
| 列名 | 描述 | 示例 |
|------|------|------|
| Date | 活动日期 | 2025-01-15 |
| Course | 课程名称 | 4th Grade Math |
| Task | 任务类型 | Quiz |
| XP_Earned | 获得的 XP | 25 |
| XP_Possible | 可能的 XP | 30 |
| Completion | 完成度 | 83.3% |

#### Summary 工作表
- **总体统计**：总 XP、学习天数、任务数量等
- **课程分解**：每个课程的详细统计
- **性能指标**：平均 XP、最高/最低记录等

### JSON 输出格式
结构化的 JSON 数据，包含：
```json
{
  "metadata": {
    "total_xp": 1250,
    "study_days": 30,
    "total_tasks": 156
  },
  "activities": [
    {
      "date": "2025-01-15",
      "course": "4th Grade Math",
      "task": "Quiz",
      "xp_earned": 25,
      "xp_possible": 30
    }
  ],
  "statistics": {
    "daily_average": 41.67,
    "most_productive_day": "2025-01-20",
    "favorite_course": "4th Grade Math"
  }
}
```

### 图表输出格式
- **交互式 HTML**：使用 Plotly 生成，支持缩放、悬停、筛选
- **静态 PNG**：使用 Matplotlib 生成，适合文档和报告
- **仪表板 HTML**：单文件包含所有图表和交互功能

## 数据处理特性

### 智能数据识别
- **课程名称提取**：保留原始课程名称和级别信息
- **任务类型识别**：自动分类不同类型的学术任务
- **XP 计算逻辑**：精确跟踪已获得和潜在的 XP 值
- **时间戳处理**：处理各种日期和时间格式

### 数据质量保证
- **异常检测**：自动识别和处理数据异常值
- **完整性验证**：确保数据的完整性和一致性
- **错误恢复**：在遇到格式问题时提供替代方案
- **日志记录**：详细记录处理过程和警告信息

## 批处理脚本

### 批量处理多个文件
```bash
#!/bin/bash
# batch_process.sh

for pdf_file in data/*.pdf; do
    filename=$(basename "$pdf_file" .pdf)
    output_dir="output/$filename"

    mkdir -p "$output_dir"

    echo "处理文件: $pdf_file"

    # 导出数据
    mathacademy-analyzer export "$pdf_file" "$output_dir/data.xlsx"

    # 生成图表
    mathacademy-analyzer chart "$output_dir/data.json" --chart-type dashboard --output "$output_dir/charts/"

    # 生成统计报告
    mathacademy-analyzer stats "$output_dir/data.json" > "$output_dir/stats.txt"

    echo "完成: $filename"
done

echo "所有文件处理完成！"
```

### 自动化分析脚本
```python
# automated_analysis.py
import os
import subprocess
from pathlib import Path

def analyze_student_data(pdf_path, output_base):
    """自动化分析学生数据"""

    # 创建输出目录
    output_dir = Path(output_base)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 步骤1：导出数据
    print("步骤1：导出课程数据...")
    subprocess.run([
        "mathacademy-analyzer", "export", pdf_path,
        str(output_dir / "course_data.xlsx")
    ])

    # 步骤2：生成图表
    print("步骤2：生成可视化图表...")
    subprocess.run([
        "mathacademy-analyzer", "chart", str(output_dir / "course_data.json"),
        "--chart-type", "dashboard",
        "--output", str(output_dir / "charts/")
    ])

    # 步骤3：生成统计报告
    print("步骤3：生成统计报告...")
    with open(output_dir / "report.txt", "w") as f:
        subprocess.run([
            "mathacademy-analyzer", "stats", str(output_dir / "course_data.json")
        ], stdout=f)

    print(f"分析完成！结果保存在：{output_dir}")

# 使用示例
analyze_student_data("data/student_report.pdf", "output/student_analysis")
```

## 故障排除

### 常见问题及解决方案

#### 1. PDF 解析失败
**问题症状**：程序无法读取 PDF 文件或输出空白内容
**可能原因**：
- PDF 文件损坏或格式不正确
- PDF 为扫描件，需要 OCR 处理
- PDF 受密码保护

**解决方案**：
```bash
# 检查 PDF 文件状态
mathacademy-analyzer info problem_file.pdf

# 如果是扫描件，使用 OCR 工具预处理
# 推荐使用：ocrmypdf 或 Adobe Acrobat

# 尝试提取部分内容进行测试
mathacademy-analyzer text problem_file.pdf --output test_output.txt
```

#### 2. 图表生成失败
**问题症状**：图表生成过程中出现错误或输出空白
**可能原因**：
- JSON 数据格式不正确
- 数据内容为空或格式异常
- 输出目录权限不足

**解决方案**：
```bash
# 验证 JSON 数据格式
python -m json.tool course_data.json

# 检查数据内容
mathacademy-analyzer stats course_data.json

# 手动指定输出目录
mathacademy-analyzer chart course_data.json --output /tmp/charts/
```

#### 3. 依赖安装问题
**问题症状**：pip install 过程中出错
**可能原因**：
- Python 版本不兼容
- 网络连接问题
- 系统依赖缺失

**解决方案**：
```bash
# 检查 Python 版本
python --version

# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 如果仍有问题，尝试逐个安装依赖
pip install click pdfplumber openpyxl pandas matplotlib plotly
```

#### 4. 内存不足
**问题症状**：处理大型 PDF 文件时程序崩溃
**解决方案**：
```bash
# 增加虚拟内存（Linux/macOS）
export MALLOC_ARENA_MAX=2

# 分段处理大文件
# 先提取文本，再分批处理
mathacademy-analyzer text large_file.pdf --pages --output pages/
```

### 调试技巧

#### 启用详细日志
```bash
# 设置环境变量启用调试模式
export DEBUG=1
mathacademy-analyzer export file.pdf output.xlsx
```

#### 验证中间结果
```bash
# 逐步验证处理流程
mathacademy-analyzer info file.pdf          # 步骤1：检查文件
mathacademy-analyzer text file.pdf          # 步骤2：提取文本
mathacademy-analyzer export file.pdf test.xlsx  # 步骤3：导出数据
```

## 扩展开发

### 添加新的图表类型
1. 在 `src/ma_log_pdf_parser/chart_generator.py` 中添加新函数
2. 更新 `main.py` 中的图表类型选项
3. 添加相应的测试用例
4. 更新文档说明

### 集成新的数据源
1. 在 `src/ma_log_pdf_parser/course_parser.py` 中添加解析逻辑
2. 更新数据模型以支持新的字段
3. 修改导出功能以包含新数据
4. 添加相应的 CLI 命令

### 性能优化
- 使用多进程处理大型文件
- 实现增量更新机制
- 添加缓存层减少重复计算
- 优化内存使用

## 技术支持

### 获取帮助
- **GitHub Issues**：报告 bug 和功能请求
- **文档网站**：详细的使用指南和 API 文档
- **社区论坛**：与其他用户交流经验

### 贡献指南
1. Fork 项目仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交 Pull Request

### 开发环境设置
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install

# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 代码格式化
black src/ tests/
```

## 版本历史

### v0.1.0 (当前版本)
- ✅ PDF 文本提取功能
- ✅ 课程数据解析和导出
- ✅ 7种可视化图表类型
- ✅ 综合仪表板功能
- ✅ 完整的 CLI 界面
- ✅ 中英文双语文档

### 未来计划
- 🔄 Web 界面支持
- 🔄 实时数据处理
- 🔄 机器学习预测模型
- 🔄 移动端应用
- 🔄 云端部署支持

---

**MathAcademyLogAnalyzer** - 让 Math Academy 学习数据分析变得简单高效！

如有任何问题或建议，欢迎通过 GitHub Issues 与我们联系。