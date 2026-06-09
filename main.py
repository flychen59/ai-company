"""
AI 日报生成器 — 5 Agent 全链路协作

流程：采集数据 → 研究员 → 编辑 → 分析师 → 视觉设计师 → 审查员
最终输出：精美 HTML 日报

用法：
    python main.py --demo          # 默认主题：GitHub 高星项目
    python main.py "Rust"          # 自定义主题
    python main.py --list          # 查看已生成报告
"""
import os
import sys
import re
import time
import requests
from datetime import datetime

os.environ["https_proxy"] = "http://127.0.0.1:7897"
os.environ["http_proxy"] = "http://127.0.0.1:7897"

from tools.search_tools import github_trending

API_URL = "https://tinyapi.nykjsd.cn/v1/chat/completions"
API_KEY = os.environ.get("OPENAI_API_KEY", "")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}


def call_llm(system: str, user: str, timeout: int = 300) -> str:
    """调用 LLM，自动重试一次"""
    for attempt in range(2):
        try:
            r = requests.post(
                API_URL,
                headers=HEADERS,
                json={
                    "model": "glm-5-turbo",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 16384,
                },
                proxies={"https": "http://127.0.0.1:7897"},
                timeout=timeout,
            )
            d = r.json()
            c = d["choices"][0]["message"]
            return c.get("content") or c.get("reasoning_content", "")
        except Exception as e:
            print(f"  ⚠️ 重试 {attempt + 1}: {str(e)[:80]}")
            time.sleep(5)
    return "ERROR"


# ─── Agent 定义 ──────────────────────────────────────────────

AGENTS = {
    "researcher": {
        "system": "你是资深研究员。分析 GitHub Trending 数据。只输出结果。",
        "icon": "🔍",
        "name": "研究员",
    },
    "editor": {
        "system": "你是内容编辑。整理成 Markdown 日报。只输出结果。",
        "icon": "✍️",
        "name": "编辑",
    },
    "analyst": {
        "system": "你是数据分析师。分析语言分布+趋势+建议。只输出结果。",
        "icon": "📊",
        "name": "分析师",
    },
    "designer": {
        "system": (
            "你是一个顶级网页视觉设计师和前端工程师。把日报渲染成精美HTML页面。\n\n"
            "设计要求：\n"
            "- 深色主题 #0d1117，GitHub风格但更精美\n"
            "- 前3名金/银/铜色排名标记（渐变色块）\n"
            "- 每个项目用卡片布局，hover有边框变色效果\n"
            "- star数要大要醒目，橙色高亮\n"
            "- 语言分布用彩色进度条（每种语言不同颜色）\n"
            "- 趋势用带火焰标记的卡片，🔥 数量表示强度\n"
            "- 建议用2x2网格卡片\n"
            "- 顶部渐变header（深蓝到深紫），含编者按\n"
            "- Agent徽章：研究员蓝/编辑紫/分析师绿/设计师粉/审查员橙\n"
            "- 响应式布局，手机能看\n"
            "- CSS用内联style标签，不用外部文件\n"
            "- 整体要有高级感，让人一眼就觉得专业、抓人眼球\n"
            "- 加一些微动画：卡片hover上浮、进度条渐入\n\n"
            "直接输出完整HTML文件（<!DOCTYPE html>开头）。不要用markdown代码块包裹。"
        ),
        "icon": "🎨",
        "name": "视觉设计师",
    },
    "reviewer": {
        "system": "你是质量审查员。简短审查HTML日报。50字以内。",
        "icon": "👁️",
        "name": "审查员",
    },
}


def run_task(topic: str) -> str:
    """执行完整 5 Agent 流程"""
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'=' * 60}")
    print(f"🔥 AI 日报生成器 — 5 Agent 全链路")
    print(f"📅 {today} | 主题: {topic}")
    print(f"{'=' * 60}")

    # Step 0: 采集数据
    print("\n📡 采集真实数据...")
    raw_data = github_trending._run(since="daily")
    print(f"  ✅ 抓取完成 ({len(raw_data)} chars)")

    # Agent 工作分配
    agent_order = ["researcher", "editor", "analyst", "designer", "reviewer"]
    print("\n👥 Agent 分工：")
    for key in agent_order:
        a = AGENTS[key]
        print(f"  {a['icon']}  {a['name']}")

    print("\n🚀 开始执行...\n")

    # Step 1: 研究员
    a = AGENTS["researcher"]
    print(f"{a['icon']} {a['name']}分析...")
    research = call_llm(
        a["system"],
        f"分析并排序：\n{raw_data}\n\n输出：项目名|描述|语言|总star数|领域分类",
    )

    # Step 2: 编辑
    a = AGENTS["editor"]
    print(f"{a['icon']} {a['name']}整理...")
    editorial = call_llm(
        a["system"],
        f"日期{today}，数据：\n{research}\n\n输出日报：标题+编者按+项目表格+相关动态",
    )

    # Step 3: 分析师
    a = AGENTS["analyst"]
    print(f"{a['icon']} {a['name']}洞察...")
    analysis = call_llm(
        a["system"],
        f"日报：\n{editorial}\n\n输出趋势分析",
    )

    # Step 4: 视觉设计师（核心）
    a = AGENTS["designer"]
    print(f"{a['icon']} {a['name']}渲染 HTML（这步最关键）...")
    html = call_llm(
        a["system"],
        f"日期：{today}\n\n编辑日报：\n{editorial}\n\n分析师洞察：\n{analysis}",
    )

    # Step 5: 审查员
    a = AGENTS["reviewer"]
    print(f"{a['icon']} {a['name']}把关...")
    review = call_llm(
        a["system"],
        f"审查这个日报的数据和视觉效果：\n{html[:2000]}",
    )
    print(f"\n📝 审查意见: {review[:150]}")

    # 清理 HTML
    html = re.sub(r"^```html?\n?", "", html.strip())
    html = re.sub(r"\n?```$", "", html.strip())

    # 保存
    os.makedirs("output", exist_ok=True)
    filename = f"output/daily_{today}_{topic.replace(' ', '_')}.html"
    with open(filename, "w") as f:
        f.write(html)

    print(f"\n{'=' * 60}")
    print(f"✅ HTML 日报已生成: {filename}")
    print(f"📏 文件大小: {len(html)} 字符")

    # 验证
    if html.strip().startswith("<!DOCTYPE") or html.strip().startswith("<html"):
        print("✅ 格式验证: 合法 HTML")
    else:
        print("⚠️ 格式验证: 可能不是完整 HTML")

    print(f"{'=' * 60}")
    return html


def list_reports():
    """查看已生成的报告"""
    if not os.path.exists("output"):
        print("还没有生成过日报")
        return
    files = [f for f in os.listdir("output") if f.startswith("daily_") and f.endswith(".html")]
    if not files:
        print("还没有生成过日报")
        return
    print("已生成的日报：")
    for f in sorted(files, reverse=True):
        size = os.path.getsize(f"output/{f}")
        print(f"  📄 {f} ({size // 1024}KB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：")
        print('  python main.py "AI Agent"    # 自定义主题')
        print("  python main.py --demo         # 默认主题：GitHub 高星项目")
        print("  python main.py --list         # 查看已生成报告")
        sys.exit(1)

    if sys.argv[1] == "--demo":
        run_task("GitHub_高星项目")
    elif sys.argv[1] == "--list":
        list_reports()
    else:
        topic = " ".join(sys.argv[1:])
        run_task(topic)
