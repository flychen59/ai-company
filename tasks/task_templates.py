"""
AI 一人公司 — 任务模板（真实数据注入版）
研究员不再自己调工具（kimi-k2.6 tool_call 不兼容），
而是直接拿到采集好的真实数据进行分析
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
            f"3. 标注每个项目的领域分类（如 AI工具、系统工具、教育等）\n"
            f"4. 总结搜索结果中的关键信息\n\n"
            f"要求：\n"
            f"- 只使用上面提供的数据，不要编造\n"
            f"- 输出完整的结构化分析\n"
            f"- 每条信息都要标注来源"
        ),
        expected_output="结构化分析报告：项目列表（排序后）+ 领域分类 + 搜索结果摘要",
        agent=agent,
    )


def make_edit_task(topic: str, date: str, agent, research_task: Task) -> Task:
    """编辑的任务：整理成日报"""
    return Task(
        description=(
            f"根据研究员的分析结果，整理「{topic}」日报。日期：{date}\n\n"
            f"⚠️ 必须使用研究员提供的真实数据！\n\n"
            f"输出格式（Markdown）：\n"
            f"# 🔥 GitHub 每日高星日报 | {date}\n\n"
            f"> 编者按：50字以内导读\n\n"
            f"## 📊 今日热门项目\n\n"
            f"| # | 项目 | 描述 | 语言 | ⭐ |\n"
            f"|---|------|------|------|----|\n\n"
            f"## 📰 相关动态\n\n"
            f"---\n"
            f"*数据来源：GitHub Trending | 由 AI 一人公司自动生成*"
        ),
        expected_output="格式规范的 Markdown 日报，使用真实数据",
        agent=agent,
        context=[research_task],
    )


def make_analysis_task(topic: str, agent, edit_task: Task) -> Task:
    """分析师的任务：趋势分析"""
    return Task(
        description=(
            f"分析「{topic}」日报数据，补充深度洞察。\n\n"
            f"工作内容：\n"
            f"1. 统计日报中项目的语言分布\n"
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


def make_review_task(agent, edit_task: Task, analysis_task: Task) -> Task:
    """审查员的任务：Review + 输出最终版"""
    return Task(
        description=(
            "你是最终把关人。审查编辑的日报和分析师的洞察。\n\n"
            "检查：\n"
            "1. 数据准确性\n"
            "2. 格式规范\n"
            "3. 分析质量\n"
            "4. 完整性\n"
            "5. 可读性\n\n"
            "直接输出最终版完整日报（日报正文 + 趋势分析 + 审查修正）。"
        ),
        expected_output="最终版完整日报（Markdown）",
        agent=agent,
        context=[edit_task, analysis_task],
    )
