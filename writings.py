# posts.json 중 예약일(한국 시간)이 된 글만 공개: writings/ 글 페이지·보관함 + 첫 화면 '새로 올라온 글'
import os, re, json, html, datetime, shutil, sys

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'writings')
TODAY = os.environ.get('TODAY') or (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
posts = [p for p in json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8')) if p['date'] <= TODAY]
posts.sort(key=lambda p: (p['date'], p['id']), reverse=True)

def esc(s): return html.escape(s, quote=True)
KIND_LABEL = {'행사': '교회 소식', '설교': '설교', '예화': '예화', '독후감': '독후감', '팡세/예화': '팡세·예화'}

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;800&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap">
<style>
:root{{--paper:#f6f5f0;--sheet:#fffefa;--ink:#1f2a2e;--muted:#62706f;--rule:#dcd8cc;--green:#2f5d50;--gold:#a07b32;
--display:"Nanum Myeongjo","Batang",serif;--body:"IBM Plex Sans KR","Malgun Gothic",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root{{--paper:#141819;--sheet:#1b2122;--ink:#e8e6df;--muted:#9eaaa7;--rule:#2f3738;--green:#8cc4ad;--gold:#d6b46c;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.8;padding-inline:16px}}
a{{color:var(--green)}}
.wrap{{max-width:760px;margin:0 auto;padding-block:32px 64px;display:grid;gap:24px}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;font-size:.92rem}}
.top a{{text-decoration:none}}
.brand{{font-family:var(--display);font-weight:800;color:var(--ink)}}
h1{{font-family:var(--display);font-weight:800;font-size:clamp(1.6rem,4.5vw,2.3rem);line-height:1.35;margin:0;text-wrap:balance}}
h3{{font-family:var(--display);font-size:1.2rem;margin:1.6em 0 .4em;color:var(--green)}}
.meta{{color:var(--muted);font-size:.88rem;display:flex;gap:6px 14px;flex-wrap:wrap}}
.tags{{display:flex;flex-wrap:wrap;gap:6px}}
.tags span{{font-size:.8rem;color:var(--gold);border:1px solid var(--rule);border-radius:99px;padding:2px 10px}}
article{{background:var(--sheet);border:1px solid var(--rule);padding:clamp(20px,4vw,40px)}}
article p{{margin:0 0 .9em;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere}}
.src{{color:var(--muted);font-size:.88rem}}
.nav{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:.92rem}}
.filters{{display:flex;flex-wrap:wrap;gap:8px}}
.filters button{{font:inherit;font-size:.9rem;padding:6px 14px;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:99px;cursor:pointer}}
.filters button[aria-pressed="true"]{{background:var(--green);color:var(--paper);border-color:var(--green)}}
input[type=search]{{font:inherit;padding:10px 14px;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);width:100%;border-radius:4px}}
.list{{list-style:none;margin:0;padding:0;border-top:1px solid var(--rule)}}
.list li{{border-bottom:1px solid var(--rule)}}
.list a{{display:grid;grid-template-columns:6.5em 1fr;gap:4px 14px;padding:14px 4px;text-decoration:none;color:var(--ink)}}
.list .k{{font-size:.8rem;color:var(--gold);font-weight:600}}
.list .d{{font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}}
.list .t{{font-family:var(--display);font-size:1.05rem;grid-row:span 2}}
.list a:hover .t{{color:var(--green)}}
.empty{{color:var(--muted)}}
@media (max-width:560px){{.list a{{grid-template-columns:1fr}} .list .t{{grid-row:auto}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="top"><a class="brand" href="{root}index.html">독서주특기</a><span><a href="{root}index.html">홈</a> · <a href="{root}writings/index.html">글 보관함</a></span></div>
'''
FOOT = '</div>\n</body>\n</html>\n'

def render_body(text):
    out = []
    for para in re.split(r'\n\s*\n', text.strip()):
        para = para.strip('\n')
        if not para.strip(): continue
        if para.startswith('■'):
            out.append(f'<h3>{esc(para.lstrip("■ ").strip())}</h3>')
        elif para.startswith('— ') or para.startswith('※'):
            out.append(f'<p class="src">{esc(para)}</p>')
        else:
            out.append(f'<p>{esc(para)}</p>')
    return '\n'.join(out)

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
order = list(reversed(posts))                                   # 날짜 오름차순(이전/다음 글)
for i, p in enumerate(order):
    prev_a = f'<a href="{order[i - 1]["id"]}.html">← {esc(order[i - 1]["title"])}</a>' if i > 0 else '<span></span>'
    next_a = f'<a href="{order[i + 1]["id"]}.html">{esc(order[i + 1]["title"])} →</a>' if i + 1 < len(order) else '<span></span>'
    tags = ''.join(f'<span>{esc(t)}</span>' for t in p['tags'].split()) if p['tags'] else ''
    page = HEAD.format(title=esc(p['title']) + ' · 독서주특기', root='../') + f'''<header style="display:grid;gap:10px">
<div class="meta"><span>{KIND_LABEL.get(p["kind"], p["kind"])}</span><span>{p["date"].replace("-", ".")}</span><span>{esc(p["category"])}</span></div>
<h1>{esc(p["title"])}</h1>
{f'<div class="tags">{tags}</div>' if tags else ''}
</header>
<article>
{render_body(p["body"])}
</article>
<nav class="nav">{prev_a}{next_a}</nav>
''' + FOOT
    open(os.path.join(OUT, p['id'] + '.html'), 'w', encoding='utf-8').write(page)

# 보관함
kinds = [k for k in KIND_LABEL if any(p['kind'] == k for p in posts)]
items = ''.join(f'''<li data-kind="{esc(p["kind"])}" data-q="{esc((p["title"] + " " + p["category"] + " " + p["tags"]).lower())}"><a href="{p["id"]}.html">
<span class="k">{KIND_LABEL.get(p["kind"], p["kind"])}</span><span class="t">{esc(p["title"])}</span><span class="d">{p["date"].replace("-", ".")}</span></a></li>''' for p in posts)
buttons = '<button type="button" aria-pressed="true" data-k="">전체</button>' + ''.join(
    f'<button type="button" aria-pressed="false" data-k="{esc(k)}">{KIND_LABEL[k]}</button>' for k in kinds)
index = HEAD.format(title='글 보관함 · 독서주특기', root='../') + f'''<header style="display:grid;gap:8px">
<h1>글 보관함</h1>
<p class="meta">설교 · 예화 · 독후감 · 팡세가 날마다 새로 올라옵니다. 지금까지 {len(posts)}편.</p>
</header>
<div class="filters" role="group" aria-label="종류">{buttons}</div>
<label for="q" class="meta">제목·카테고리·태그 검색</label>
<input id="q" type="search" placeholder="예: 기도, 창세기, 출애굽기">
<ul class="list" id="list">{items}</ul>
<p class="empty" id="empty" hidden>찾는 글이 없습니다.</p>
<script>
const btns=[...document.querySelectorAll('.filters button')], q=document.getElementById('q'), rows=[...document.querySelectorAll('#list li')], empty=document.getElementById('empty');
let kind='';
function apply(){{const s=q.value.trim().toLowerCase();let n=0;for(const r of rows){{const ok=(!kind||r.dataset.kind===kind)&&(!s||r.dataset.q.includes(s));r.hidden=!ok;if(ok)n++;}}empty.hidden=n>0;}}
btns.forEach(b=>b.addEventListener('click',()=>{{kind=b.dataset.k;btns.forEach(x=>x.setAttribute('aria-pressed',x===b));apply();}}));
q.addEventListener('input',apply);
</script>
''' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index)

# 첫 화면에 '새로 올라온 글' 6편 + 목차 링크
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
latest = ''.join(f'''<li class="card"><a href="writings/{p["id"]}.html"><span class="ref">{KIND_LABEL.get(p["kind"], p["kind"])}</span><h4>{esc(p["title"])}</h4><p>{esc(p["category"])}</p><span class="meta">{p["date"].replace("-", ".")}</span></a></li>''' for p in posts[:6])
section = f'''<section id="new" aria-labelledby="new-h">
    <div class="head"><span class="eyebrow">새로 올라온 글</span><div class="row"><h2 id="new-h">날마다 한 편씩</h2><a href="writings/index.html">글 보관함 {len(posts)}편 →</a></div></div>
    <ul class="cards">{latest}</ul>
  </section>

  ''' if posts else ''
h = re.sub(r'<section id="new".*?</section>\s*', '', h, flags=re.S)
h = h.replace('<section id="sermon"', section + '<section id="sermon"', 1)
if 'href="#new"' not in h:
    h = h.replace('<li><a href="#sermon">', '<li><a href="#new">새 글</a></li>\n    <li><a href="#sermon">', 1)
open(home, 'w', encoding='utf-8').write(h)
print('today', TODAY, 'published', len(posts), 'of', len(json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8'))))
