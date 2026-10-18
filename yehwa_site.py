# 예화 전체(blogger_yehwa.json)를 홈페이지에 주제별로: yehwa/index.html(가 편 ~ 하 편 목차) + 주제마다 한 쪽
# 블로그 예화 모음과 같은 분류(낱말 주제 kw)를 쓴다. 첫 화면 메뉴와 예화 칸에 링크를 단다.
import os, re, json, html, shutil

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'yehwa')
CHO = '가가나다다라마바바사사아자자차카타파하'
def pyeon(w): return CHO[(ord(w[0]) - 0xAC00) // 588] + ' 편'
def esc(s): return html.escape(s, quote=True)
def slug(w): return 'k-' + '-'.join(f'{ord(c):x}' for c in w)

y = json.load(open(os.path.join(D, 'blogger_yehwa.json'), encoding='utf-8'))
# 둘로스 자료에서 골라 줄거리를 새로 쓴 예화(원글 저자·출처는 credit) — 같은 주제 맨 앞에 둔다
dl = os.path.join(D, 'doulos_yehwa.json')
if os.path.exists(dl): y = json.load(open(dl, encoding='utf-8')) + y
by = {}
for x in y: by.setdefault(x.get('kw') or '지혜', []).append(x)

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700;900&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
:root{{--paper:#f7f4ec;--sheet:#fffdf8;--ink:#1f2a2e;--muted:#62706f;--rule:#e2dccd;--green:#23443a;--gold:#b08a3e;
--display:"Noto Serif KR","Batang",serif;--body:"Pretendard Variable",Pretendard,"Malgun Gothic",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root{{--paper:#141819;--sheet:#1b2122;--ink:#e8e6df;--muted:#9eaaa7;--rule:#2f3738;--green:#8cc4ad;--gold:#d6b46c;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.85;padding-inline:16px;word-break:keep-all}}
a{{color:var(--green)}}
.wrap{{max-width:820px;margin:0 auto;padding-block:32px 64px;display:grid;gap:22px}}
.top{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:.92rem}}
.top a{{text-decoration:none}} .brand{{font-family:var(--display);font-weight:900;color:var(--ink)}}
h1{{font-family:var(--display);font-weight:900;font-size:clamp(1.7rem,4.5vw,2.4rem);margin:0;line-height:1.3}}
.lede{{color:var(--muted);margin:0}}
.jump{{display:flex;flex-wrap:wrap;gap:6px}}
.jump a{{text-decoration:none;border:1px solid var(--rule);background:var(--sheet);border-radius:99px;padding:4px 12px;font-size:.9rem}}
h2{{font-family:var(--display);font-size:1.35rem;margin:.6em 0 .2em;color:var(--green);border-bottom:1px solid var(--rule);padding-bottom:.3em}}
.kws{{display:flex;flex-wrap:wrap;gap:8px 10px}}
.kws a{{text-decoration:none;color:var(--ink);background:var(--sheet);border:1px solid var(--rule);border-radius:8px;padding:6px 12px}}
.kws a:hover{{border-color:var(--gold)}} .kws small{{color:var(--muted);margin-left:4px}}
input[type=search]{{font:inherit;padding:10px 14px;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);width:100%;border-radius:8px}}
.toc{{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:16px 20px;columns:2 18em;column-gap:28px;font-size:.95rem}}
.toc a{{display:block;text-decoration:none;padding:2px 0;break-inside:avoid}}
article{{background:var(--sheet);border:1px solid var(--rule);border-radius:12px;padding:clamp(18px,4vw,32px)}}
article h3{{font-family:var(--display);font-size:1.15rem;margin:0 0 .6em}}
article p{{margin:0 0 .8em}}
.src{{color:var(--muted);font-size:.88rem}}
.nav{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}
</style>
</head>
<body>
<div class="wrap">
<div class="top"><a class="brand" href="../index.html">독서주특기</a><span><a href="../index.html">홈</a> · <a href="index.html">예화 목차</a> · <a href="../writings/index.html">글 보관함</a></span></div>
'''
FOOT = '</div>\n</body>\n</html>\n'

def src_line(x):
    if x.get('credit'): return f'📜 원글: {esc(x["credit"])} — 줄거리를 바탕으로 새로 써서 옮김'
    if x.get('sermon'): return f'📖 인용한 설교: {esc(x["sermon"])}'
    if x.get('book'): return f'📚 독후감 「{esc(x["book"])}」에서'
    if x.get('origin'): return f'📜 출처: {esc(x["origin"])}' + (' (저작권이 끝난 고전을 새로 옮겨 씀)' if x.get('src') == 'classic' else ' (역사 기록을 바탕으로 새로 씀)')
    return ''

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
kws = sorted(by)
for i, kw in enumerate(kws):
    items = by[kw]
    toc = ''.join(f'<a href="#y{j + 1}">{j + 1}. {esc(x["title"])}</a>' for j, x in enumerate(items))
    arts = ''.join(f'<article id="y{j + 1}"><h3>{j + 1}. {esc(x["title"])}</h3>'
                   + ''.join(f'<p>{esc(l.strip())}</p>' for l in x['body'].split('\n') if l.strip())
                   + (f'<p class="src">{src_line(x)}</p>' if src_line(x) else '') + '</article>' for j, x in enumerate(items))
    prev_a = f'<a href="{slug(kws[i - 1])}.html">← 【{esc(kws[i - 1])}】</a>' if i else '<span></span>'
    next_a = f'<a href="{slug(kws[i + 1])}.html">【{esc(kws[i + 1])}】 →</a>' if i + 1 < len(kws) else '<span></span>'
    page = HEAD.format(title=f'【{esc(kw)}】 예화 모음 · 독서주특기') + f'''<header style="display:grid;gap:8px">
<p class="lede">{pyeon(kw)} · 주제별 예화</p>
<h1>【{esc(kw)}】 예화 모음 <small style="font-size:.55em;color:var(--muted)">{len(items)}편</small></h1>
</header>
<nav class="toc" aria-label="이 쪽의 예화">{toc}</nav>
{arts}
<p class="src">※ 설교 중에 인용한 예화, 독후감에서 뽑은 이야기, 고전과 역사 기록이나 여러 예화집의 줄거리를 바탕으로 새로 쓴 이야기입니다. 출처가 분명한 예화는 원 출처를 밝혀 사용해 주세요.</p>
<nav class="nav">{prev_a}{next_a}</nav>
''' + FOOT
    open(os.path.join(OUT, slug(kw) + '.html'), 'w', encoding='utf-8').write(page)

groups = {}
for kw in kws: groups.setdefault(pyeon(kw), []).append(kw)
jump = ''.join(f'<a href="#{p[0]}">{p}</a>' for p in sorted(groups))
secs = ''.join(f'<section id="{p[0]}" data-sec><h2>{p} <small style="font-size:.7em;color:var(--muted)">{len(groups[p])}가지 주제</small></h2><div class="kws">'
               + ''.join(f'<a href="{slug(k)}.html" data-k="{esc(k)}">【{esc(k)}】<small>{len(by[k])}</small></a>' for k in groups[p]) + '</div></section>' for p in sorted(groups))
index = HEAD.format(title='주제별 예화 모음 · 독서주특기') + f'''<header style="display:grid;gap:8px">
<h1>주제별 예화 모음</h1>
<p class="lede">예화 {len(y):,}편을 {len(kws)}가지 주제로 모았습니다. 가 편부터 하 편까지, 주제는 가나다순입니다.</p>
</header>
<label for="q" class="lede">주제 찾기</label>
<input id="q" type="search" placeholder="예: 감사, 기도, 용서">
<nav class="jump" aria-label="편">{jump}</nav>
{secs}
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{{const s=q.value.trim();document.querySelectorAll('[data-sec]').forEach(sec=>{{let n=0;sec.querySelectorAll('[data-k]').forEach(a=>{{const ok=!s||a.dataset.k.includes(s);a.hidden=!ok;if(ok)n++;}});sec.hidden=n===0;}});}});
</script>
''' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index)

# 첫 화면: 메뉴에 '예화 모음', 예화 칸에 '주제별 예화' 버튼
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
if 'href="yehwa/index.html"' not in h:
    h = h.replace('<li><a href="#stories">', '<li><a href="yehwa/index.html">예화 모음</a></li>\n    <li><a href="#stories">', 1)
    h = re.sub(r'(<h2 id="stories-h">[^<]*</h2>)', r'\1<a href="yehwa/index.html">주제별 예화 ' + f'{len(y):,}' + '편 →</a>', h, 1)
open(home, 'w', encoding='utf-8').write(h)
print('예화', len(y), '주제', len(kws))
