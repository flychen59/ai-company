# AI 一人公司 — 4 Agent GitHub 高星日报生成器

## 产品介绍

用 4 个 AI Agent 协作，自动生成 GitHub 每日高星项目日报。

## 4 Agent 分工

| Agent | 职责 | 说明 |
|-------|------|------|
| 🔍 **研究员** | 数据分析 | 分析 GitHub Trending 真实数据，提取项目信息，按 star 排序，标注领域分类 |
| ✍️ **编辑** | 内容整理 | 把研究员的分析结果整理成 Markdown 格式日报 |
| 📊 **分析师** | 趋势洞察 | 统计语言分布、发现趋势模式、给开发者建议 |
| 👁️ **审查员** | 质量把关 | 审查数据准确性、格式规范、分析质量，输出最终可发布版本 |

## 架构

```
数据采集（GitHub Trending API）→ 研究员 → 编辑 → 分析师 → 审查员 → 最终日报
```

- **框架**：CrewAI（多 Agent 编排）
- **LLM**：kimi-k2.6（via YuTou 中转站）
- **数据源**：GitHub Trending（requests + BeautifulSoup）
- **搜索**：DuckDuckGo Search

## 用法

```bash
cd ~/ai-company
source .venv/bin/activate

# 生成默认日报（GitHub 高星项目）
python main.py --demo

# 生成指定主题日报
python main.py "Rust"

# 列出已生成的日报
python main.py --list
```

## 目录结构

```
ai-company/
├── main.py              # 主入口
├── agents/
│   └── team.py          # 4 Agent 角色定义
├── tasks/
│   └── task_templates.py # 任务模板
├── tools/
│   ├── __init__.py
│   └── search_tools.py  # 搜索工具（GitHub Trending + DuckDuckGo）
├── output/              # 生成的日报
└── README.md
```

## 示例输出

见 `output/` 目录下的 Markdown 文件。

## 技术栈

- Python 3.12
- CrewAI（多 Agent 框架）
- kimi-k2.6（LLM）
- DuckDuckGo Search
- BeautifulSoup4（HTML 解析）
- browser-use（视觉爬虫，备用）
