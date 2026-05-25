"""
AI 日报生成器 — 5 Agent 全链路协作

流程：采集数据 → 研究员 → 编辑 → 分析师 → 视觉设计师 → 审查员
最终输出：精美 HTML 日报

用法：
    python main.py --demo
    python main.py "Rust"
    python main.py --list
"""
import sys
import os
from datetime import datetime

os.environ["https_proxy"] = "http://127.0.0.1:7897"
os.environ["http_proxy"] = "http://127.0.0.1:7897"

from crewai import Crew, Process
from agents.team import researcher, editor, analyst, designer, reviewer
from tasks.task_templates import (
    make_research_task,
    make_edit_task,
    make_analysis_task,
    make_design_task,
    make_review_task,
)


def collect_real_data() -> str:
    """用真实工具采集数据"""
    from tools.search_tools import github_trending, web_search
    print("📡 正在采集真实数据...")
    trending_data = github_trending._run(since="daily")
    print(f"  ✅ GitHub Trending: 抓取成功")
    search_data = web_search._run("GitHub trending projects analysis AI developer tools 2026")
    print(f"  ✅ Web 搜索: 搜索完成")
    return f"=== GitHub Trending 数据 ===\n{trending_data}\n\n=== 相关搜索 ===\n{search_data}"


def run_task(topic: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"🔥 AI 日报生成器 — 5 Agent 全链路")
    print(f"📅 {today} | 主题: {topic}")
    print(f"{'='*60}")

    raw_data = collect_real_data()
    print(f"\n👥 Agent 分工：")
    print(f"  🔍 研究员     → 分析真实数据")
    print(f"  ✍️  编辑       → 整理成日报")
    print(f"  📊 分析师     → 趋势洞察")
    print(f"  🎨 视觉设计师 → 渲染精美 HTML")
    print(f"  👁️  宩查员     → 最终把关")
    print(f"\n🚀 开始执行...\n")

    task_research = make_research_task(topic, researcher, raw_data)
    task_edit = make_edit_task(topic, today, editor, task_research)
    task_analysis = make_analysis_task(topic, analyst, task_edit)
    task_design = make_design_task(topic, today, designer, task_edit, task_analysis)
    task_review = make_review_task(reviewer, task_design)

    crew = Crew(
        agents=[researcher, editor, analyst, designer, reviewer],
        tasks=[task_research, task_edit, task_analysis, task_design, task_review],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # 保存 HTML
    os.makedirs("output", exist_ok=True)
    html_content = str(result)

    # 确保 HTML 内容干净（去掉可能的 markdown 代码块标记）
    if html_content.startswith("```"):
        html_content = html_content.split("\n", 1)[1]
    if html_content.endswith("```"):
        html_content = html_content.rsplit("```", 1)[0]

    filename = f"output/daily_{today}_{topic.replace(' ', '_')}.html"
    with open(filename, "w") as f:
        f.write(html_content)

    print(f"\n{'='*60}")
    print(f"✅ HTML 日报已生成: {filename}")
    print(f"{'='*60}")
    return html_content


def list_reports():
    if not os.path.exists("output"):
        print("还没有生成过日报")
        return
    files = [f for f in os.listdir("output") if f.startswith("daily_") and f.endswith(".html")]
    if not files:
        print("还没有生成过日报")
        return
    print("已生成的日报：")
    for f in sorted(files, reverse=True):
        print(f"  📄 {f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print('  python main.py "AI Agent"')
        print("  python main.py --demo")
        print("  python main.py --list")
        sys.exit(1)

    if sys.argv[1] == "--demo":
        run_task("GitHub_高星项目")
    elif sys.argv[1] == "--list":
        list_reports()
    else:
        topic = " ".join(sys.argv[1:])
        run_task(topic)
