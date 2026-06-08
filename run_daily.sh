#!/bin/bash
# 每日 GitHub 高星项目日报生成器
# 由 Hermes cronjob 每天早上 8 点触发

cd ~/ai-company
source ~/.bashrc 2>/dev/null
source .venv/bin/activate

echo "🚀 开始生成 $(date +%Y-%m-%d) 日报..."
python main.py --demo 2>&1

# 找到今天生成的 HTML
TODAY=$(date +%Y-%m-%d)
HTML_FILE="output/daily_${TODAY}_GitHub_高星项目.html"

if [ -f "$HTML_FILE" ]; then
    SIZE=$(wc -c < "$HTML_FILE")
    echo "✅ 日报生成成功: $HTML_FILE ($SIZE bytes)"
    echo "FILE_PATH: $HTML_FILE"
else
    echo "❌ 日报生成失败，未找到输出文件"
fi
