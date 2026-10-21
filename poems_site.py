# 안식월 시집: anshik_poems.json(안식월 기간에 쓴 시) → anshik/index.html 과 시 한 편마다 한 쪽
# 사진이 있는 시는 사진을 위에 크게, 없는 시는 계절빛 바탕에 제목을 크게 놓는다. 첫 화면 '시' 칸에도 소개를 넣는다
import os, json, html, re
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'anshik')
P = json.load(open(os.path.join(D, 'anshik_poems.json'), encoding='utf-8'))
def esc(s): return html.escape(s, quote=True)
SEASON = {12: 'w', 1: 'w', 2: 'w', 3: 'sp', 4: 'sp', 5: 'sp', 6: 'su', 7: 'su', 8: 'su', 9: 'au', 10: 'au', 11: 'au'}
SNAME = {'sp': '봄', 'su': '여름', 'au': '가을', 'w': '겨울'}
def season(p): return SEASON.get(int(p['date'][5:7]) if p['date'] else 4, 'sp')
def kdate(p):
    if not p['date']: return p['year'] + '년'
    y, m, d = p['date'].split('-'); return f'{y}년 {int(m)}월 {int(d)}일'
def first_lines(p, n=2):
    ls = [l for l in p['body'].split('\n') if l.strip()]
    return ' / '.join(ls[:n])

CSS = '''
:root{--paper:#f7f4ec;--sheet:#fffdf8;--ink:#1f2a2e;--muted:#66706c;--rule:#e2dccd;--green:#23443a;--gold:#b08a3e;
--poem:"Nanum Pen Script","Gowun Batang","Noto Serif KR",serif;--brush:"Nanum Brush Script","Nanum Pen Script","Noto Serif KR",serif;
--display:"Noto Serif KR","Nanum Myeongjo","Batang",serif;--body:"Pretendard Variable",Pretendard,"Malgun Gothic",system-ui,sans-serif;
--sp1:#f3e3e6;--sp2:#e3efe0;--su1:#dcefee;--su2:#e7f1dc;--au1:#f3e2c8;--au2:#ecd6c4;--w1:#e3e8ee;--w2:#eef0f2}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--gold:#d9b86a;
--sp1:#3a2a2e;--sp2:#25322a;--su1:#1f3332;--su2:#26321f;--au1:#3b2f1f;--au2:#352a22;--w1:#222a33;--w2:#262a2e;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--gold:#d9b86a;
--sp1:#3a2a2e;--sp2:#25322a;--su1:#1f3332;--su2:#26321f;--au1:#3b2f1f;--au2:#352a22;--w1:#222a33;--w2:#262a2e;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.8;word-break:keep-all;padding-inline:16px}
a{color:var(--green)}
.wrap{max-width:1080px;margin:0 auto;padding-block:28px 72px}
.top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:.92rem;margin-bottom:22px}
.top a{text-decoration:none}.brand{font-family:var(--display);font-weight:900;color:var(--ink)}
.sp{--c1:var(--sp1);--c2:var(--sp2)}.su{--c1:var(--su1);--c2:var(--su2)}.au{--c1:var(--au1);--c2:var(--au2)}.w{--c1:var(--w1);--c2:var(--w2)}
'''
HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;900&family=Nanum+Pen+Script&family=Nanum+Brush+Script&family=Gowun+Batang&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<div class="top"><a class="brand" href="../index.html">독서주특기</a><span><a href="../index.html#poems">홈</a> · <a href="index.html">안식월 시집</a></span></div>
'''
# 쪽 끝 블로그·유튜브 안내 (yehwa_site.py·writings.py와 같다)
CHB = 'text-decoration:none;font-weight:700;border-radius:99px;padding:9px 16px;font-size:.92rem;'
BLOG_ASK = ('<aside style="background:linear-gradient(150deg,#1d3a32,#162c26);color:#f6efe0;border:1px solid #b08a3e;border-radius:14px;padding:22px clamp(18px,4vw,28px);display:grid;gap:12px;text-align:left;font-family:var(--body,sans-serif)">'
            '<span style="font-size:.78rem;letter-spacing:.16em;color:#d9b86a">독서주특기를 더 가까이</span>'
            '<p style="margin:0;font-family:\'Noto Serif KR\',serif;font-size:1.15rem;font-weight:700;line-height:1.5">이 시가 마음에 닿으셨나요? 블로그 이웃이 되어 ❤ 공감과 댓글로 마음을 나눠 주세요.</p>'
            '<p style="margin:0;opacity:.8;font-size:.9rem">새 시와 설교 소식을 가장 먼저 받아 보실 수 있습니다.</p><div style="display:flex;flex-wrap:wrap;gap:8px">'
            f'<a href="https://blog.naver.com/saechang888" target="_blank" rel="noopener" style="{CHB}background:#03c75a;color:#fff">N 네이버 블로그 이웃 되기</a>'
            f'<a href="https://www.youtube.com/@%EB%8F%85%EC%84%9C%ED%8A%B9%EA%B8%B0?sub_confirmation=1" target="_blank" rel="noopener" style="{CHB}background:#e62117;color:#fff">▶ 유튜브 구독</a>'
            f'<a href="https://saechang888-code.github.io/links.html" style="{CHB}border:1px solid #d9b86a;color:#d9b86a">모든 바로가기 →</a></div></aside>\n')
FOOT = BLOG_ASK + '</div>\n</body>\n</html>\n'

# ---------- 시 한 편 ----------
PCSS = CSS + '''
.hero{position:relative;border-radius:22px;overflow:hidden;min-height:clamp(300px,56vw,560px);display:grid;align-items:end;background:#efe9f2}
.hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(255,250,246,.35),transparent 55%)}
.hero .cap{position:relative;z-index:1;justify-self:start;max-width:min(560px,calc(100% - 28px));margin:clamp(14px,3vw,28px);padding:clamp(18px,4vw,34px) clamp(20px,4.5vw,40px);color:#3a3346;background:rgba(255,252,248,.74);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-radius:18px;border:1px solid rgba(255,255,255,.7);box-shadow:0 10px 30px rgba(120,100,140,.16)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .hero .cap{background:rgba(26,30,36,.72);color:#efe9f2;border-color:rgba(255,255,255,.12)}}
:root[data-theme="dark"] .hero .cap{background:rgba(26,30,36,.72);color:#efe9f2;border-color:rgba(255,255,255,.12)}
.tint{border-radius:22px;padding:clamp(40px,9vw,96px) clamp(22px,5vw,48px) clamp(26px,5vw,44px);background:radial-gradient(120% 90% at 85% 0%,var(--c1),transparent 60%),radial-gradient(100% 80% at 0% 100%,var(--c2),transparent 60%),var(--sheet);border:1px solid var(--rule);position:relative;overflow:hidden}
.tint::before{content:attr(data-s);position:absolute;right:-.06em;top:-.22em;font-family:var(--display);font-weight:900;font-size:clamp(7rem,26vw,15rem);line-height:1;color:var(--ink);opacity:.05}
.meta{font-size:.86rem;letter-spacing:.06em;opacity:.85;display:flex;gap:10px;flex-wrap:wrap}
.meta span{border:1px solid currentColor;border-radius:99px;padding:1px 10px}
h1{font-family:var(--brush);font-weight:400;font-size:clamp(2.6rem,8vw,4.4rem);line-height:1.15;margin:.2em 0 0;letter-spacing:0}
.poem{max-width:640px;margin:44px auto 0;font-family:var(--poem);font-size:clamp(1.55rem,3.6vw,1.85rem);line-height:1.75;text-align:center;letter-spacing:.01em}
.poem p{margin:0;min-height:1.1em}
.note{max-width:640px;margin:34px auto 0;padding:14px 18px;border-left:3px solid var(--gold);background:var(--sheet);color:var(--muted);font-size:.93rem;line-height:1.75}
.sign{text-align:center;margin-top:26px;color:var(--muted);font-family:var(--poem);font-size:1.4rem}
.nav{max-width:760px;margin:44px auto 0;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.nav a{display:grid;gap:2px;padding:14px 18px;border:1px solid var(--rule);border-radius:14px;background:var(--sheet);text-decoration:none;color:var(--ink)}
.nav a small{color:var(--muted)}.nav .nx{text-align:right}
'''
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith('.html'): os.remove(os.path.join(OUT, f))
for i, p in enumerate(P):
    s = season(p)
    meta = f'<div class="meta"><span>{esc(p["sub"])}</span><span>{kdate(p)}</span><span>{SNAME[s]}</span></div>'
    top = (f'<header class="hero"><img src="../{p["photo"]}" alt="「{esc(p["title"])}」을 쓴 곳에서 찍은 사진" loading="eager"><div class="cap">{meta}<h1>{esc(p["title"])}</h1></div></header>'
           if p['photo'] else f'<header class="tint {s}" data-s="{SNAME[s]}">{meta}<h1>{esc(p["title"])}</h1></header>')
    body = ''.join(f'<p>{esc(l)}</p>' for l in p['body'].split('\n'))
    note = f'<p class="note">✎ {esc(p["note"])}</p>' if p['note'] else ''
    prv = P[i - 1] if i else None; nxt = P[i + 1] if i + 1 < len(P) else None
    nav = ('<nav class="nav">' + (f'<a href="{prv["id"]}.html"><small>← 앞의 시</small>{esc(prv["title"])}</a>' if prv else '<span></span>')
           + (f'<a class="nx" href="{nxt["id"]}.html"><small>다음 시 →</small>{esc(nxt["title"])}</a>' if nxt else '<span></span>') + '</nav>')
    page = HEAD.format(title=f'{esc(p["title"])} · 안식월 시집 · 이재선 목사', desc=esc(f'이재선 목사(새암교회)의 시 「{p["title"]}」 — {first_lines(p)}'), css=PCSS) + \
        top + f'<article class="poem">{body}</article>{note}<p class="sign">— 이재선 목사 · 새암교회</p>{nav}' + FOOT
    open(os.path.join(OUT, p['id'] + '.html'), 'w', encoding='utf-8').write(page)

# ---------- 시집 목차 ----------
ICSS = CSS + '''
.cover{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:center;margin-bottom:34px}
.cover h1{font-family:var(--brush);font-weight:400;font-size:clamp(2.8rem,8vw,4.8rem);line-height:1.2;margin:.2em 0 .3em}
.cover .eb{color:var(--gold);font-weight:700;letter-spacing:.16em;font-size:.82rem}
.cover p{color:var(--muted);margin:0 0 .8em}
.mosaic{display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:110px;gap:8px}
.mosaic img{width:100%;height:100%;object-fit:cover;border-radius:12px}
.mosaic img:first-child{grid-column:span 2;grid-row:span 2}
.bar{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--paper) 90%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);padding:10px 0;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:6px}
.bar button{font:inherit;font-size:.9rem;border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:99px;padding:5px 14px;cursor:pointer}
.bar button[aria-pressed="true"]{background:var(--green);border-color:var(--green);color:var(--paper)}
h2{font-family:var(--display);font-size:1.6rem;margin:34px 0 14px;display:flex;align-items:baseline;gap:10px}
h2 small{font-size:.55em;color:var(--muted);font-family:var(--body)}
.grid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));gap:14px}
.grid a{height:100%;display:grid;grid-template-rows:auto 1fr;text-decoration:none;color:var(--ink);background:var(--sheet);border:1px solid var(--rule);border-radius:16px;overflow:hidden}
.grid a:hover{border-color:var(--gold)}
.grid .ph{aspect-ratio:4/3;background:radial-gradient(120% 90% at 85% 0%,var(--c1),transparent 60%),radial-gradient(100% 80% at 0% 100%,var(--c2),transparent 60%),var(--sheet);display:grid;place-items:center;font-family:var(--display);font-weight:900;font-size:1.25rem;padding:14px;text-align:center}
.grid .ph.has{padding:0;overflow:hidden}.grid .ph img{display:block;width:100%;height:100%;object-fit:cover}
.grid .tx{padding:12px 16px 16px;display:grid;gap:4px;align-content:start}
.grid b{font-family:var(--poem);font-weight:400;font-size:1.5rem;line-height:1.3}
.grid small{color:var(--muted);font-size:.8rem}
.grid span{color:var(--muted);font-size:.88rem;line-height:1.6;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
@media (max-width:720px){.cover{grid-template-columns:1fr}}
'''
years = sorted({p['year'] for p in P})
subs = ['자연시', '생활시', '묵상시', '찬양시']
photos = [p for p in P if p['photo']]
mosaic = ''.join(f'<img src="../{p["photo"]}" alt="" loading="lazy">' for p in photos[:7])
def card(p):
    s = season(p)
    ph = f'<img src="../{p["photo"]}" alt="" loading="lazy">' if p['photo'] else esc(p['title'])
    return (f'<li data-sub="{p["sub"]}"><a href="{p["id"]}.html"><div class="ph {s}{" has" if p["photo"] else ""}">{ph}</div><div class="tx"><b>{esc(p["title"])}</b>'
            f'<small>{esc(p["sub"])} · {kdate(p)}</small><span>{esc(first_lines(p))}</span></div></a></li>')
secs = ''.join(f'<section data-year><h2 id="y{y}">{y}년 <small>{sum(1 for p in P if p["year"] == y)}편</small></h2><ul class="grid">'
               + ''.join(card(p) for p in P if p['year'] == y) + '</ul></section>' for y in years)
index = HEAD.format(title='안식월 시집 · 이재선 목사', desc=f'이재선 목사(새암교회)가 안식월과 기도원에서 쓴 시 {len(P)}편 — 자연시, 생활시, 묵상시, 찬양시', css=ICSS) + f'''
<section class="cover"><div><span class="eb">이재선 목사의 시</span><h1>안식월 시집</h1>
<p>2011년 첫 안식월, 가평 필그림하우스의 밤 개구리 소리를 듣다가 처음 시를 적었습니다. 그 뒤로 광은기도원과 남해, 홍천의 산골에서 쉬고 기도하며 쓴 시가 {len(P)}편이 되었습니다.</p>
<p>산과 나무, 바람과 바다, 그리고 그 사이에서 만난 사람들과 하나님 이야기입니다. 사진은 그때 그 자리에서 찍은 것입니다.</p></div>
<div class="mosaic">{mosaic}</div></section>
<nav class="bar" aria-label="갈래와 해"><button type="button" data-f="" aria-pressed="true">전체 {len(P)}</button>'''
index += ''.join(f'<button type="button" data-f="{s}" aria-pressed="false">{s} {sum(1 for p in P if p["sub"] == s)}</button>' for s in subs)
index += ''.join(f'<a href="#y{y}" style="align-self:center;font-size:.88rem;margin-left:6px">{y}</a>' for y in years)
index += f'''</nav>
{secs}
<script>
document.querySelectorAll('.bar button').forEach(b=>b.addEventListener('click',()=>{{
  document.querySelectorAll('.bar button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  const f=b.dataset.f;
  document.querySelectorAll('[data-year]').forEach(sec=>{{let n=0;sec.querySelectorAll('li').forEach(li=>{{const ok=!f||li.dataset.sub===f;li.hidden=!ok;if(ok)n++;}});sec.hidden=n===0;}});
}}));
</script>
''' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index)

# ---------- 첫 화면 '시' 칸: 안식월 시집 소개 띠 ----------
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
pick = photos[:4]
band = ('<a class="anshik" href="anshik/index.html"><div class="as-ph">' + ''.join(f'<img src="{p["photo"]}" alt="" loading="lazy">' for p in pick) +
        f'</div><div class="as-tx"><span class="eb">새로 엮은 시집</span><h3>안식월 시집 <small>{len(P)}편</small></h3>'
        '<p>안식월과 기도원에서 쓴 시를 한 권으로 엮었습니다. 그 자리에서 찍은 사진과 함께 읽어 보세요.</p><span class="go">시집 펼치기 →</span></div></a>')
STY = ('<style>.anshik{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:0;margin:0 0 22px;border:1px solid var(--rule);border-radius:18px;overflow:hidden;background:var(--sheet);text-decoration:none;color:var(--ink)}'
       '.anshik:hover{border-color:var(--gold)}.as-ph{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:120px;gap:3px}.as-ph img{width:100%;height:100%;object-fit:cover}'
       '.as-tx{padding:26px 28px;display:grid;gap:8px;align-content:center}.as-tx .eb{font-size:.8rem;color:var(--gold);font-weight:700;letter-spacing:.14em}'
       '.as-tx h3{font-size:1.7rem}.as-tx h3 small{font-size:.55em;color:var(--muted);font-family:var(--body)}.as-tx p{margin:0;color:var(--muted)}.as-tx .go{font-weight:700;color:var(--green)}'
       '@media (max-width:720px){.anshik{grid-template-columns:1fr}}</style>')
h = re.sub(r'<style>\.anshik\{.*?</a>', '', h, flags=re.S)
h = h.replace('<!--ANSHIK-->', STY + band, 1)
open(home, 'w', encoding='utf-8').write(h)
print('안식월 시집', len(P), '편 · 사진', len(photos))

# ---------- 안식월 묵상(팡세): anshik/meditations.html + 한 편마다 m###.html ----------
mp = os.path.join(D, 'anshik_pensees.json')
M = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else []
MCSS = PCSS + '''
.mhead{border-radius:22px;padding:clamp(34px,7vw,72px) clamp(22px,5vw,48px) clamp(24px,4vw,36px);background:linear-gradient(135deg,#1d3530,#2f5d50);color:#f6efe0}
.mhead .meta{color:#d9b86a}
.prose{max-width:680px;margin:40px auto 0;font-size:1.06rem;line-height:2}
.prose p{margin:0 0 1.2em}
.prose .vs{font-family:var(--display);color:var(--green);background:var(--sheet);border-left:3px solid var(--gold);padding:10px 16px;margin:1.6em 0 .8em;font-size:.98rem;line-height:1.8}
.mlist{list-style:none;margin:24px 0 0;padding:0;display:grid;gap:12px}
.mlist a{display:grid;grid-template-columns:auto 1fr;gap:4px 18px;padding:18px 22px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;text-decoration:none;color:var(--ink)}
.mlist a:hover{border-color:var(--gold)}
.mlist .n{grid-row:span 2;font-family:var(--display);font-weight:900;font-size:1.5rem;color:var(--gold);min-width:2.2em}
.mlist b{font-family:var(--display);font-size:1.12rem}
.mlist span{color:var(--muted);font-size:.92rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
'''
def mdate(m):
    y, mo, d = m['date'].split('-'); return f'{y}년 {int(mo)}월 {int(d)}일'
for i, m in enumerate(M):
    paras = ''
    for para in m['body'].split('\n'):
        para = para.strip()
        if not para: continue
        paras += f'<p class="vs">{esc(para[2:])}</p>' if para.startswith('▸ ') else f'<p>{esc(para)}</p>'
    prv = M[i - 1] if i else None; nxt = M[i + 1] if i + 1 < len(M) else None
    nav = ('<nav class="nav">' + (f'<a href="{prv["id"]}.html"><small>← 앞의 묵상</small>{esc(prv["title"])}</a>' if prv else '<span></span>')
           + (f'<a class="nx" href="{nxt["id"]}.html"><small>다음 묵상 →</small>{esc(nxt["title"])}</a>' if nxt else '<span></span>') + '</nav>')
    first = re.sub(r'^▸ ', '', m['body'].split('\n')[0])[:110]
    page = HEAD.format(title=f'{esc(m["title"])} · 안식월 묵상 · 이재선 목사', desc=esc(f'이재선 목사(새암교회)의 묵상 「{m["title"]}」 — {first}'), css=MCSS).replace('<a href="index.html">안식월 시집</a>', '<a href="meditations.html">안식월 묵상</a> · <a href="index.html">안식월 시집</a>') + \
        f'<header class="mhead"><div class="meta"><span>나의 팡세 · 안식월 묵상</span><span>{mdate(m)}</span></div><h1>{esc(m["title"])}</h1></header>' + \
        f'<article class="prose">{paras}</article><p class="sign">— 이재선 목사 · 새암교회</p>{nav}' + FOOT
    open(os.path.join(OUT, m['id'] + '.html'), 'w', encoding='utf-8').write(page)
if M:
    items = ''.join(f'<li><a href="{m["id"]}.html"><span class="n">{k}</span><b>{esc(m["title"])}</b><span>{mdate(m)} · {esc(re.sub(r"^▸ ", "", m["body"])[:90])}…</span></a></li>' for k, m in enumerate(M, 1))
    idx = HEAD.format(title='안식월 묵상 · 나의 팡세 · 이재선 목사', desc=f'이재선 목사(새암교회)가 안식월에 말씀을 읽고 기도하며 적은 묵상 {len(M)}편', css=MCSS).replace('<a href="index.html">안식월 시집</a>', '<a href="meditations.html">안식월 묵상</a> · <a href="index.html">안식월 시집</a>') + f'''
<header class="mhead"><div class="meta"><span>나의 팡세</span><span>{len(M)}편</span></div><h1>안식월 묵상</h1>
<p style="margin:.8em 0 0;max-width:640px;opacity:.85">안식월과 기도원에서 성경을 읽고 기도하며 받은 깨달음을 적어 둔 노트입니다. 쉬는 동안 하나님께서 가르쳐 주신 것들을 그대로 옮겼습니다.</p></header>
<ol class="mlist">{items}</ol>''' + FOOT
    open(os.path.join(OUT, 'meditations.html'), 'w', encoding='utf-8').write(idx)
    h = open(home, encoding='utf-8').read()
    band = (f'<a class="anshik am" href="anshik/meditations.html" style="grid-template-columns:1fr"><div class="as-tx"><span class="eb">새로 엮은 팡세</span><h3>안식월 묵상 <small>{len(M)}편</small></h3>'
            f'<p>{" · ".join(esc(m["title"]) for m in M[:6])} …</p><span class="go">묵상 노트 펼치기 →</span></div></a>')
    h = re.sub(r'<a class="anshik am".*?</a>', '', h, flags=re.S)
    h = h.replace('<!--ANSHIK-M-->', band, 1)
    open(home, 'w', encoding='utf-8').write(h)
print('안식월 묵상', len(M), '편')
