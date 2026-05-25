"""
AI 一人公司 — 任务模板（5 Agent 版）
新增视觉设计师 Agent，负责渲染精美 HTML
"""
from crewai import Task


def make_research_task(topic: str, agent, raw_data: str) -> Task:
    """研究员的任务：分析采集到的真实数据"""
    return Task(
        description=(
            f"以下是关于「{topic}」的采集数据：\n\n"
            f"```\n{raw_data}\n```\n\n"
            f"请分析以上真实数据，完成以下工作：\n"
            f"1. 提取所有项目的关键信息（名称、描述、语言、star数）\n"
            f"2. 按 star 数从高到低排序\n"
            f"3. 标注每个项目的领域分类\n"
            f"4. 总结搜索结果中的关键信息\n\n"
            f"要求：只使用提供的数据，不要编造，输出完整的结构化分析。"
        ),
        expected_output="结构化分析报告：项目列表（排序后）+ 领域分类",
        agent=agent,
    )


def make_edit_task(topic: str, date: str, agent, research_task: Task) -> Task:
    """编辑的任务：整理成日报"""
    return Task(
        description=(
            f"根据研究员的分析结果，整理「{topic}」日报。日期：{date}\n\n"
            f"⚠️ 必须使用研究员提供的真实数据！\n\n"
            f"输出格式（Markdown）：\n"
            f"# 🔥 GitHub 每日高星日报 | {date}\n"
            f"> 编者按\n"
            f"## 📊 今日热门项目（表格）\n"
            f"## 📰 相关动态\n"
            f"---\n"
            f"*数据来源：GitHub Trending | AI 一人公司*"
        ),
        expected_output="格式规范的 Markdown 日报",
        agent=agent,
        context=[research_task],
    )


def make_analysis_task(topic: str, agent, edit_task: Task) -> Task:
    """分析师的任务：趋势分析"""
    return Task(
        description=(
            f"分析「{topic}」日报数据，补充深度洞察。\n\n"
            f"工作内容：\n"
            f"1. 统计日报中项目的语言分布（数量+占比）\n"
            f"2. 找出 2-3 个值得关注的趋势\n"
            f"3. 给开发者的实用建议\n\n"
            f"输出格式：\n"
            f"## 💡 趋势分析\n"
            f"### 语言/领域分布\n"
            f"### 值得关注的趋势\n"
            f"### 给开发者的建议"
        ),
        expected_output="基于真实数据的趋势分析",
        agent=agent,
        context=[edit_task],
    )


def make_design_task(topic: str, date: str, agent, edit_task: Task, analysis_task: Task) -> Task:
    """视觉设计师的任务：渲染精美 HTML"""
    return Task(
        description=(
            f"把编辑的日报和分析师的洞察渲染成精美的 HTML 页面。\n"
            f"日期：{date}，主题：{topic}\n\n"
            f"设计要求：\n"
            f"1. 深色主题（#0d1117），GitHub 风格但更精美\n"
            f"2. 前3名项目用金/银/铜色排名标记\n"
            f"3. 项目用卡片布局，hover 有交互效果\n"
            f"4. 语言分布用彩色进度条可视化\n"
            f"5. 趋势用带火焰强度标记的卡片\n"
            f"6. 建议用 2x2 网格卡片\n"
            f"7. 顶部有渐变 header + 编者按 + Agent 徽章\n"
            f"8. 响应式，手机能看\n"
            f"9. 整体要有高级感，让人一眼就觉得专业\n\n"
            f"直接输出完整的 HTML 文件内容（<!DOCTYPE html> 开头），不要用代码块包裹。"
        ),
        expected_output="完整的精美 HTML 文件",
        agent=agent,
        context=[edit_task, analysis_task],
    )


def make_review_task(agent, design_task: Task) -> Task:
    """审查员的任务：Review 全流程 + 确认 HTML 质量"""
    return Task(
        description=(
            "你是最终把关人。审查视觉设计师输出的 HTML 日报。\n\n"
            "检查：\n"
            "1. 数据准确性 — 项目名、star数是否正确\n"
            "2. 视觉质量 — HTML 是否精美、布局是否合理\n"
            "3. 完整性 — 所有板块是否都有\n"
            "4. 响应式 — 手机上是否也能看\n\n"
            "如果 HTML 质量达标，直接确认发布。\n"
            "如果有明显问题，指出问题并修改。"
        ),
        expected_output="审查通过的最终版 HTML 日报",
        agent=agent,
        context=[design_task],
    )
