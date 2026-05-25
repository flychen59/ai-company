"""5 Agent 日报生成器 - 跑出精美 HTML 版"""
import os, requests, json, time, re
from datetime import datetime
from tools.search_tools import github_trending

os.environ['https_proxy'] = 'http://127.0.0.1:7897'

API_URL = 'https://yutou.virtualgoods.top/v1/chat/completions'
API_KEY = 'sk-o9nGSiite6eroOpxPdCvD5bZxa3lDkVhW8Fpkzi52GV6rOqe'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}

def call(system, user):
    for attempt in range(2):
        try:
            r = requests.post(API_URL, headers=HEADERS, json={
                'model': 'moonshotai/kimi-k2.6',
                'messages': [{'role':'system','content':system},{'role':'user','content':user}],
                'temperature': 0.3,
            }, proxies={'https':'http://127.0.0.1:7897'}, timeout=300)
            d = r.json()
            c = d['choices'][0]['message']
            return c.get('content') or c.get('reasoning_content','')
        except Exception as e:
            print(f'  重试 {attempt+1}: {str(e)[:80]}')
            time.sleep(5)
    return 'ERROR'

today = datetime.now().strftime('%Y-%m-%d')

# Step 0: 采集
print('📡 采集数据...')
raw = github_trending._run(since='daily')
print(f'  ✅ 抓取完成 ({len(raw)} chars)')

# Step 1: 研究员
print('🔍 研究员分析...')
r1 = call('你是资深研究员。分析GitHub Trending数据。只输出结果。',
    '分析并排序：\n' + raw + '\n\n输出：项目名|描述|语言|总star数|领域分类')

# Step 2: 编辑
print('✍️ 编辑整理...')
r2 = call('你是内容编辑。整理成Markdown日报。只输出结果。',
    '日期' + today + '，数据：\n' + r1 + '\n\n输出日报：标题+编者按+项目表格+相关动态')

# Step 3: 分析师
print('📊 分析师洞察...')
r3 = call('你是数据分析师。分析语言分布+趋势+建议。只输出结果。',
    '日报：\n' + r2 + '\n\n输出趋势分析')

# Step 4: 视觉设计师 — 核心！
print('🎨 视觉设计师渲染 HTML（这步最关键）...')
design_prompt = (
    '你是一个顶级网页视觉设计师和前端工程师。把日报渲染成精美HTML页面。\n\n'
    '设计要求：\n'
    '- 深色主题 #0d1117，GitHub风格但更精美\n'
    '- 前3名金/银/铜色排名标记（渐变色块）\n'
    '- 每个项目用卡片布局，hover有边框变色效果\n'
    '- star数要大要醒目，橙色高亮\n'
    '- 语言分布用彩色进度条（每种语言不同颜色）\n'
    '- 趋势用带火焰标记的卡片，🔥 数量表示强度\n'
    '- 建议用2x2网格卡片\n'
    '- 顶部渐变header（深蓝到深紫），含编者按\n'
    '- Agent徽章：研究员蓝/编辑紫/分析师绿/设计师粉/审查员橙\n'
    '- 响应式布局，手机能看\n'
    '- CSS用内联style标签，不用外部文件\n'
    '- 整体要有高级感，让人一眼就觉得专业、抓人眼球\n'
    '- 加一些微动画：卡片hover上浮、进度条渐入\n\n'
    '直接输出完整HTML文件（<!DOCTYPE html>开头）。不要用markdown代码块包裹。'
)
html = call(design_prompt,
    '日期：' + today + '\n\n编辑日报：\n' + r2 + '\n\n分析师洞察：\n' + r3)

# Step 5: 审查员
print('👁️ 审查员把关...')
review = call('你是质量审查员。简短审查HTML日报。30字以内。',
    '审查这个日报的数据和视觉效果：\n' + html[:2000])

print(f'\n📝 审查意见: {review[:150]}')

# 清理 HTML
html = re.sub(r'^```html?\n?', '', html.strip())
html = re.sub(r'\n?```$', '', html.strip())

os.makedirs('output', exist_ok=True)
fn = f'output/daily_{today}_v2.html'
with open(fn, 'w') as f:
    f.write(html)

print(f'\n✅ HTML日报已保存: {fn}')
print(f'文件大小: {len(html)} 字符')

# 验证是合法 HTML
if html.strip().startswith('<!DOCTYPE') or html.strip().startswith('<html'):
    print('✅ 格式验证: 合法 HTML')
else:
    print('⚠️ 格式验证: 可能不是完整 HTML，检查文件')
