"""
AI 日报生成器 — 4 Agent 全链路协作

策略：工具采集 → Agent 协作
  1. 先用真实工具采集 GitHub Trending 数据
  2. 把真实数据注入研究员的任务描述
  3. 研究员 → 分析数据
  4. 编辑 → 整理成日报
  5. 分析师 → 趋势洞察
  6. 审查员 → 最终把关

这样研究员不需要自己调工具（kimi-k2.6 的 tool_call 和 CrewAI 不兼容），
但每个 Agent 仍然各司其职，处理真实数据。

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
from agents.team import researcher, editor, analyst, reviewer
from tasks.task_templates import (
    make_research_task,
    make_edit_task,
    make_analysis_task,
    make_review_task,
)


def collect_real_data() -> str:
    """用真实工具采集数据"""
    from tools.search_tools import github_trending, web_search
    print("📡 正在采集真实数据...")
    
    # 1. GitHub Trending
    trending_data = github_trending._run(since="daily")
    print(f"  ✅ GitHub Trending: 抓取成功")
    
    # 2. Web 搜索补充
    search_data = web_search._run("GitHub trending projects analysis AI developer tools 2026")
    print(f"  ✅ Web 搜索: 搜索完成")
    
    return f"=== GitHub Trending 数据 ===\n{trending_data}\n\n=== 相关搜索 ===\n{search_data}"


def run_task(topic: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"🔥 AI 日报生成器 — 4 Agent 全链路")
    print(f"📅 {today} | 主题: {topic}")
    print(f"{'='*60}")
    
    # Step 0: 采集真实数据
    raw_data = collect_real_data()
    print(f"\n👥 Agent 分工：")
    print(f"  🔍 研究员 → 分析采集到的真实数据")
    print(f"  ✍️  编辑   → 整理成日报")
    print(f"  📊 分析师 → 趋势分析+洞察")
    print(f"  👁️  审查员 → 最终质量把关")
    print(f"\n🚀 开始执行...\n")

    # 构建 4 个任务，把真实数据注入研究员的任务
    task_research = make_research_task(topic, researcher, raw_data)
    task_edit = make_edit_task(topic, today, editor, task_research)
    task_analysis = make_analysis_task(topic, analyst, task_edit)
    task_review = make_review_task(reviewer, task_edit, task_analysis)

    crew = Crew(
        agents=[researcher, editor, analyst, reviewer],
        tasks=[task_research, task_edit, task_analysis, task_review],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    # 保存
    os.makedirs("output", exist_ok=True)
    filename = f"output/daily_{today}_{topic.replace(' ', '_')}.md"
    with open(filename, "w") as f:
        f.write(str(result))

    print(f"\n{'='*60}")
    print(f"✅ 日报已生成: {filename}")
    print(f"{'='*60}\n")
    print(str(result))
    return str(result)


def list_reports():
    if not os.path.exists("output"):
        print("还没有生成过日报")
        return
    files = [f for f in os.listdir("output") if f.startswith("daily_") and f.endswith(".md")]
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
        run_task("GitHub 高星项目")
    elif sys.argv[1] == "--list":
        list_reports()
    else:
        topic = " ".join(sys.argv[1:])
        run_task(topic)
