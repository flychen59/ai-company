"""
搜索工具 — 用 DuckDuckGo 搜索真实数据，返回结构化结果
作为 CrewAI 的 custom tool 给研究员使用
"""
import os
os.environ["https_proxy"] = "http://127.0.0.1:7897"
os.environ["http_proxy"] = "http://127.0.0.1:7897"

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS


class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")


class WebSearchTool(BaseTool):
    """DuckDuckGo 搜索工具 — 返回真实搜索结果"""
    name: str = "web_search"
    description: str = "用 DuckDuckGo 搜索互联网信息。输入搜索关键词，返回标题、摘要、链接。适用于：调研、信息采集、趋势分析。"

    def _run(self, query: str) -> str:
        try:
            results = DDGS(proxy="http://127.0.0.1:7897").text(query, max_results=8)
            if not results:
                return f"搜索「{query}」无结果"
            output = []
            for r in results:
                output.append(
                    f"📌 {r['title']}\n"
                    f"   {r['body']}\n"
                    f"   🔗 {r['href']}"
                )
            return "\n\n".join(output)
        except Exception as e:
            return f"搜索出错: {e}"


class GitHubTrendingTool(BaseTool):
    """GitHub Trending 抓取工具 — 直接抓取 trending 页面数据"""
    name: str = "github_trending"
    description: str = "抓取 GitHub Trending 页面的热门项目数据。可选参数：since（daily/weekly/monthly）、language（编程语言筛选）。返回项目名称、描述、star数、语言。"

    def _run(self, since: str = "daily", language: str = "") -> str:
        import requests
        from bs4 import BeautifulSoup

        url = f"https://github.com/trending?since={since}"
        if language:
            url += f"&l={language}"

        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                proxies={"https": "http://127.0.0.1:7897"},
                timeout=15,
            )
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            articles = soup.select("article.Box-row")

            results = []
            for i, article in enumerate(articles[:25], 1):
                # 项目名
                name_el = article.select_one("h2 a")
                name = name_el.get_text(strip=True).replace("\n", "").replace(" ", "") if name_el else "N/A"

                # 描述
                desc_el = article.select_one("p")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                # 语言
                lang_el = article.select_one("[itemprop='programmingLanguage']")
                lang = lang_el.get_text(strip=True) if lang_el else ""

                # 今日 star
                today_el = article.select_one("a[href*='stargazers'] + span")
                today_stars = today_el.get_text(strip=True) if today_el else ""

                # 总 star 数（从链接取）
                star_links = article.select("a.Link--muted")
                total_stars = ""
                for sl in star_links:
                    if "stargazers" in sl.get("href", ""):
                        total_stars = sl.get_text(strip=True).strip()
                        break

                results.append(
                    f"{i}. **{name}**\n"
                    f"   描述: {desc}\n"
                    f"   语言: {lang}\n"
                    f"   今日⭐: {today_stars}\n"
                    f"   总⭐: {total_stars}"
                )

            header = f"📊 GitHub Trending ({since}) — 共 {len(results)} 个项目\n{'='*60}\n\n"
            return header + "\n\n".join(results)

        except Exception as e:
            return f"抓取出错: {e}"


# 导出工具实例
web_search = WebSearchTool()
github_trending = GitHubTrendingTool()
