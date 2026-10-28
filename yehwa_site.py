# 예화 전체(blogger_yehwa.json)를 홈페이지에 주제별로: yehwa/index.html(가 편 ~ 하 편 목차) + 주제마다 한 쪽
# 블로그 예화 모음과 같은 분류(낱말 주제 kw)를 쓴다. 첫 화면 메뉴와 예화 칸에 링크를 단다.
import os, re, json, html, shutil
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credit_author import credit_txt_with

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
# 둘로스·sermon-jesus 예화와 둘로스 설교 속 예화를 제미나이로 새로 쓴 것(예화작업/export.py가 만든다) — 손으로 쓴 것 다음에
ai = os.path.join(D, 'yehwa_ai.json')
if os.path.exists(ai):
    n_hand = sum(1 for x in y if x.get('credit'))
    y = y[:n_hand] + json.load(open(ai, encoding='utf-8')) + y[n_hand:]
# 주제를 sermon-jesus 예화 모음처럼 세밀하게(400여 주제) 다시 나눈다 — 원본 kw는 그대로, 나누는 규칙은 yehwa_topics.py
from yehwa_topics import classify, ALIAS
_old_kws = {x.get('kw') for x in y}
_tm, _ = classify(y)
for x in y: x['kw'] = _tm.get(f"{x.get('kw', '')}|{x['title']}", x.get('kw'))
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
# 쪽 끝마다 블로그 이웃·공감·댓글을 권하는 안내 (막지 않고 권하기만 한다)
CHB = 'text-decoration:none;font-weight:700;border-radius:99px;padding:9px 16px;font-size:.92rem;'
BLOG_ASK = ('<aside style="background:linear-gradient(150deg,#1d3a32,#162c26);color:#f6efe0;border:1px solid #b08a3e;border-radius:14px;padding:22px clamp(18px,4vw,28px);display:grid;gap:12px">'
            '<span style="font-size:.78rem;letter-spacing:.16em;color:#d9b86a">독서주특기를 더 가까이</span>'
            '<p style="margin:0;font-family:\'Noto Serif KR\',serif;font-size:1.15rem;font-weight:700;line-height:1.5">이 글이 도움이 되셨나요? 블로그 이웃이 되어 ❤ 공감과 댓글로 마음을 나눠 주세요.</p>'
            '<p style="margin:0;opacity:.8;font-size:.9rem">새 예화와 설교 소식을 가장 먼저 받아 보실 수 있습니다.</p><div style="display:flex;flex-wrap:wrap;gap:8px">'
            f'<a href="https://blog.naver.com/saechang888" target="_blank" rel="noopener" style="{CHB}background:#03c75a;color:#fff">N 네이버 블로그 이웃 되기</a>'
            f'<a href="https://www.youtube.com/@%EB%8F%85%EC%84%9C%ED%8A%B9%EA%B8%B0?sub_confirmation=1" target="_blank" rel="noopener" style="{CHB}background:#e62117;color:#fff">▶ 유튜브 구독</a>'
            f'<a href="https://saechang888-code.github.io/links.html" style="{CHB}border:1px solid #d9b86a;color:#d9b86a">모든 바로가기 →</a></div></aside>\n')
FOOT = BLOG_ASK + '</div>\n</body>\n</html>\n'

# 목회 프리미엄 골드(USB)에서 고른 글은 '온라인에 공유된 감동적인 글', 둘로스 자료는 '온라인에 공개된 감동적인 예화'로 적는다
# 원글이 신문·잡지에 실린 것이면 매체 이름과 날짜로 적는다 (예: '(국민960930)' → '국민일보 1996.9.30', '(광야9811)' → '「광야」 1998년 11월호')
PRESS = [('국민일보', '국민일보'), ('국민', '국민일보'), ('오늘의 ?양식', '「오늘의 양식」'), ('생명의 ?샘가', '「생명의 샘가」'), ('낮은 ?울타리', '「낮은울타리」'),
         ('좋은 ?생각', '「좋은생각」'), ('가이드포스트', '「가이드포스트」'), ('광야', '「광야」'), ('작은창', '「작은창」'), ('목마르거든', '「목마르거든」'),
         ('푸른직장', '「푸른직장」'), ('여의주', '「여의주」'), ('([가-힣 ]*(?:신문|일보))', None)]
def press_date(t, mag):
    d = re.sub(r'(월호|호)$', '', t.strip())
    if not re.fullmatch(r'\d{4}|\d{6}|\d{8}', d): return ''      # 날짜를 확실히 읽을 수 없으면 매체 이름만
    if len(d) == 6 and d[:2] in ('19', '20'): y, m, dd = d[:4], d[4:], None
    elif len(d) == 8: y, m, dd = d[:4], d[4:6], d[6:]
    else: y, m, dd = ('19' if int(d[:2]) >= 60 else '20') + d[:2], d[2:4], (d[4:] or None)
    if not (1960 <= int(y) <= 2026 and 1 <= int(m) <= 12 and (dd is None or 1 <= int(dd) <= 31)): return ''
    if mag and dd is None: return f' {y}년 {int(m)}월호'
    return f' {y}.{int(m)}' + (f'.{int(dd)}' if dd else '')
def press(c):
    m = re.search(r'\(([^()]*)\)\s*$', c)
    if not m or '게재' in m.group(1): return None
    for p, name in PRESS:
        k = re.match(p + r'(?![가-힣])\s*[,/]?\s*(.*)$', m.group(1).strip())
        if k: name = name or k.group(1).strip(); return name + press_date(k.groups()[-1], name.startswith('「'))
    return None
def credit_txt(c):
    # 저자·원제·매체·책이 분명하면 그대로 밝히고, 불분명할 때만 '온라인에 공개된 감동적인 예화'로 적는다
    return credit_txt_with(c, press)
def src_line(x):
    if x.get('credit'): return f'📜 원글: {esc(credit_txt(x["credit"]))} — 줄거리를 바탕으로 새로 써서 옮김'
    if x.get('sermon'): return f'📖 인용한 설교: {esc(x["sermon"])}'
    if x.get('book'): return f'📚 독후감 「{esc(x["book"])}」에서'
    if x.get('origin'): return f'📜 출처: {esc(x["origin"])}' + (' (저작권이 끝난 고전을 새로 옮겨 씀)' if x.get('src') == 'classic' else ' (역사 기록을 바탕으로 새로 씀)')
    return ''

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
kws = sorted(by)
PER = 100                                     # 한 쪽에 예화 100편씩, 넘으면 2쪽·3쪽…
def paras(body):     # 문단 없이 길게 이어진 이야기는 문장 4개 안팎씩 문단으로 나눠 읽기 좋게 (주인님 지시 2026-10-28)
    out = []
    for l in (l.strip() for l in body.split('\n')):
        if not l: continue
        ss = re.split(r'(?<=[.!?][”"’)])\s+|(?<=[.!?])\s+(?=\S)', l)
        if l.startswith('▸') or len(ss) < 7: out.append(l); continue
        n = -(-len(ss) // 4); k = -(-len(ss) // n)
        out += [' '.join(ss[i:i + k]) for i in range(0, len(ss), k)]
    return out
def pname(kw, p): return slug(kw) + ('' if p == 1 else f'-{p}') + '.html'
for i, kw in enumerate(kws):
    allit = by[kw]; npg = (len(allit) + PER - 1) // PER
    for p in range(1, npg + 1):
        items = allit[(p - 1) * PER:p * PER]; base = (p - 1) * PER
        toc = ''.join(f'<a href="#y{base + j + 1}">{base + j + 1}. {esc(x["title"])}</a>' for j, x in enumerate(items))
        arts = ''.join(f'<article id="y{base + j + 1}"><h3>{base + j + 1}. {esc(x["title"])}</h3>'
                       + ''.join(f'<p>{esc(l)}</p>' for l in paras(x['body']))
                       + (f'<p class="src">{src_line(x)}</p>' if src_line(x) else '') + '</article>' for j, x in enumerate(items))
        pager = '' if npg == 1 else '<nav class="jump" aria-label="쪽">' + ''.join(
            f'<a href="{pname(kw, q)}"' + (' style="border-color:var(--gold);font-weight:700"' if q == p else '') + f'>{(q - 1) * PER + 1}~{min(q * PER, len(allit))}</a>' for q in range(1, npg + 1)) + '</nav>'
        prev_a = f'<a href="{slug(kws[i - 1])}.html">← 【{esc(kws[i - 1])}】</a>' if i else '<span></span>'
        next_a = f'<a href="{slug(kws[i + 1])}.html">【{esc(kws[i + 1])}】 →</a>' if i + 1 < len(kws) else '<span></span>'
        page = HEAD.format(title=f'【{esc(kw)}】 예화 모음' + (f' {p}쪽' if p > 1 else '') + ' · 독서주특기') + f'''<header style="display:grid;gap:8px">
<p class="lede">{pyeon(kw)} · 주제별 예화</p>
<h1>【{esc(kw)}】 예화 모음 <small style="font-size:.55em;color:var(--muted)">{len(allit)}편{f' · {p}/{npg}쪽' if npg > 1 else ''}</small></h1>
</header>
{pager}
<nav class="toc" aria-label="이 쪽의 예화">{toc}</nav>
{arts}
{pager}
<p class="src">※ 설교 중에 인용한 예화, 독후감에서 뽑은 이야기, 고전과 역사 기록이나 여러 예화집·설교집의 줄거리를 바탕으로 새로 쓴 이야기입니다. 출처가 분명한 예화는 원 출처를 밝혀 사용해 주세요.</p>
<nav class="nav">{prev_a}{next_a}</nav>
''' + FOOT
        open(os.path.join(OUT, pname(kw, p)), 'w', encoding='utf-8').write(page)

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
const u=new URLSearchParams(location.search).get('q');
q.addEventListener('input',()=>{{const s=q.value.trim();document.querySelectorAll('[data-sec]').forEach(sec=>{{let n=0;sec.querySelectorAll('[data-k]').forEach(a=>{{const ok=!s||a.dataset.k.includes(s);a.hidden=!ok;if(ok)n++;}});sec.hidden=n===0;}});}});
if(u){{q.value=u;q.dispatchEvent(new Event('input'));}}
</script>
''' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index)
# 예전 153주제 가운데 이름이 사라진 주제의 주소는 가까운 새 주제로 넘겨준다 (블로그·검색에 걸린 옛 링크)
for _k in _old_kws - set(kws):
    _to = ALIAS.get(_k) if ALIAS.get(_k) in by else None
    _href = f'{slug(_to)}.html' if _to else 'index.html'
    open(os.path.join(OUT, slug(_k) + '.html'), 'w', encoding='utf-8').write(
        f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={_href}"><link rel="canonical" href="{_href}">'
        f'<title>【{esc(_k)}】 예화 모음</title><p>주제가 새로 나뉘었습니다. <a href="{_href}">새 주제로 가기</a></p>')

# 첫 화면: 메뉴에 '예화 모음', 예화 칸에 '주제별 예화' 버튼
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
if 'href="yehwa/index.html"' not in h:
    h = h.replace('<li><a href="#stories">', '<li><a href="yehwa/index.html">예화 모음</a></li>\n    <li><a href="#stories">', 1)
    h = re.sub(r'(<h2 id="stories-h">[^<]*</h2>)', r'\1<a href="yehwa/index.html">주제별 예화 ' + f'{len(y):,}' + '편 →</a>', h, 1)
# 첫 화면 '설교에 쓰는 이야기' 칸: 설교 쓰임새별 묶음 → 주제 → 예화 쪽. 블로그 글 목록은 접어서 아래에
GROUPS = [('신앙의 기초', '믿음 기도 말씀 은혜 구원 회개 복음 찬양 예배 성령 하나님 예수님 십자가 부활'),
          ('성품과 태도', '감사 겸손 교만 인내 정직 성실 태도 욕심 말 생각 마음 습관'),
          ('사랑과 관계', '사랑 용서 섬김 나눔 희생 신뢰 친구 이웃 선행 배려'),
          ('가정', '가정 부부 어머니 아버지 자녀 효도'),
          ('고난과 소망', '고난 시련 희망 소망 섭리 실패 변화 위로 죽음 천국'),
          ('사명과 인생', '사명 헌신 순종 전도 선교 지도자 지혜 인생 선택 꿈 비전 도전 노력 시간 가치 삶')]
# 설교 칸처럼 책꽂이: 묶음마다 한 칸, 주제마다 책등(예화가 많을수록 높게)
used = {k for _, ks in GROUPS for k in ks.split()}
rest = ' '.join(sorted((k for k in by if k not in used and len(by[k]) >= 15), key=lambda k: -len(by[k]))[:40])
GROUPS.append(('더 많은 주제', rest))
# 블로그 예화 목차처럼 가 편 ~ 하 편(주제 가나다순)으로 책꽂이를 나눈다
# 주제가 400여 개로 늘어 대문 책꽂이에는 편마다 예화가 많은 주제 14개만 꽂고(가나다순), 나머지는 '더 보기' 책으로 목차에 잇는다
SHELF = 14
GROUPS = [(p, ' '.join(sorted(sorted(groups[p], key=lambda k: -len(by[k]))[:SHELF]))) for p in sorted(groups)]
new_kw = {x['kw'] for x in y if x.get('credit')}
mx = max(len(v) for v in by.values())
def spine(k):
    n = len(by[k]); hgt = 46 + round(100 * (n / mx) ** 0.6)
    tip = f'{k} 예화 {n}편' + (' · 새로 쓴 예화 포함' if k in new_kw else '')
    return (f'<li><a class="spine on{" big" if n >= 200 else ""}" style="height:{hgt}px" href="yehwa/{slug(k)}.html" title="{esc(tip)}">'
            f'<span>{esc(k)}</span><b>{n}</b></a></li>')
cards = ''.join(f'<div class="shelf"' + (' style="grid-column:1/-1"' if len([k for k in ks.split() if k in by]) > 17 else '') + f'><h3>{g} · {sum(len(by[k]) for k in groups[g]):,}편</h3><div class="books-scroll"><ul class="books">'
                + ''.join(spine(k) for k in ks.split() if k in by)
                + (f'<li><a class="spine" style="height:84px" href="yehwa/index.html#{g[0]}" title="{g} 주제 모두 보기"><span>더보기</span><b>+{len(groups[g]) - SHELF}</b></a></li>' if len(groups[g]) > SHELF else '')
                + '</ul></div></div>' for g, ks in GROUPS)
STY = ('<style>.ygrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:14px;margin:6px 0 14px}'
       '.yblog summary{cursor:pointer;color:var(--muted);margin:4px 0 10px}.ymore{margin:0 0 12px;font-size:.92rem}</style>')
m = re.search(r'(<section id="stories"[^>]*>.*?</div></div>\s*)(?:<style>\.ygrid.*?</details>|<ul class="stories">.*?</ul>)', h, re.S)
if m:
    blog = re.search(r'<ul class="stories">.*?</ul>', h[m.start():], re.S).group(0)
    body = (STY + f'<div class="ygrid">{cards}</div>'
            + f'<p class="ymore"><a href="yehwa/index.html">주제 {len(kws)}가지 · 예화 {len(y):,}편 모두 보기 →</a></p>'
            + f'<details class="yblog"><summary>블로그에 올린 예화 글 보기</summary>{blog}</details>')
    h = h[:m.start()] + m.group(1) + body + h[m.end():]
h = re.sub(r'주제별 예화 [\d,]+편 →', f'주제별 예화 {len(y):,}편 →', h)
# 예화를 맨 앞으로: 메뉴 첫 칸 + 대문 바로 아래 첫 칸
h = re.sub(r'\s*<li><a href="yehwa/index.html">예화 모음</a></li>', '', h)
h = re.sub(r'\s*<li><a href="#stories">예화[^<]*(?:<small>[^<]*</small>)?</a></li>', '', h)
h = h.replace('<li><a href="#new">', f'<li><a href="#stories">예화 <small>{len(y):,}</small></a></li>\n    <li><a href="#new">', 1)
h = re.sub(r'<li><a href="#stories"><b>[\d,]+</b><small>편</small><span>예화</span></a></li>', '', h)
h = h.replace('<ul class="stats">', f'<ul class="stats"><li><a href="#stories"><b>{len(y):,}</b><small>편</small><span>예화</span></a></li>', 1)
sec = re.search(r'\s*<section id="stories".*?</section>', h, re.S)
if sec and h.find('<section id="new"') < sec.start():
    h = h[:sec.start()] + h[sec.end():]
    i = h.find('<section id="new"'); h = h[:i] + sec.group(0).strip() + '\n\n  ' + h[i:]

# ---------- 대문: 예화 수 · 예화 찾기 · 오늘의 예화 (블로그 대문도 같은 것을 yehwa/*.json으로 받아 쓴다) ----------
import datetime, random
KST = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
SITE = 'https://saechang888-code.github.io/'
T = {k: slug(k) for k in kws}
POP = [k for k in '감사 기도 사랑 믿음 용서 고난 소망 겸손 가정 전도'.split() if k in by]
find = ('<div class="finder"><label for="yq">어떤 주제의 예화가 필요하세요?</label>'
        '<form id="yfind" role="search" action="yehwa/index.html"><input id="yq" name="q" list="ykws" placeholder="예: 감사, 용서 · 또는 풍랑 속에서 지킨 믿음" autocomplete="off" enterkeyhint="search">'
        '<button type="submit">예화 찾기</button></form>'
        '<datalist id="ykws">' + ''.join(f'<option value="{esc(k)}">' for k in kws) + '</datalist>'
        '<div class="chips">' + ''.join(f'<a href="yehwa/{slug(k)}.html">{esc(k)}</a>' for k in POP) + f'<a href="yehwa/index.html">주제 {len(kws)}가지 모두</a><a href="search/index.html">🔎 뜻으로 찾기</a></div>'
        '<p class="msg" id="ymsg" aria-live="polite"></p></div>\n'
        '<script>(function(){var T=' + json.dumps(T, ensure_ascii=False) + ';'
        "var f=document.getElementById('yfind'),q=document.getElementById('yq'),m=document.getElementById('ymsg');"
        # 주제 이름이 아니거나 문장으로 적으면 뜻으로 찾기(search/)로 넘긴다
        "var S=function(){location.href='search/index.html?q='+encodeURIComponent(q.value.trim());};"
        "f.addEventListener('submit',function(e){e.preventDefault();var s=q.value.replace(/[【】\\s]/g,'');if(!s)return;"
        "if(T[s]){location.href='yehwa/'+T[s]+'.html';return;}"
        "if(/\\s/.test(q.value.trim())){S();return;}"
        "var k=Object.keys(T).filter(function(k){return k.indexOf(s)>=0||s.indexOf(k)>=0;});"
        "if(k.length===1){location.href='yehwa/'+T[k[0]]+'.html';return;}"
        "if(!k.length){S();return;}"
        "m.innerHTML='비슷한 주제: '+k.slice(0,8).map(function(x){return '<a href=\"yehwa/'+T[x]+'.html\" style=\"color:inherit\">'+x+'</a>';}).join(' · ')"
        "+' · <a href=\"search/index.html?q='+encodeURIComponent(q.value.trim())+'\" style=\"color:inherit\">내용으로 찾기 →</a>';});})();</script>")
# 새로 쓴 예화: 온라인에 공개된 감동적인 예화 · 온라인에 공유된 감동적인 글 · 독후감 · 역사와 고전에서 골라 새 문장으로 쓴 것
def is_new(x): return bool(x.get('credit') or x.get('book') or x.get('origin'))
def src_of(x):
    if x.get('book'): return '독후감'
    if x.get('origin'): return '역사와 고전'
    if '게재)' in x.get('credit', '') or press(x.get('credit', '')): return '신문·잡지에 실린 글'
    if '아름다운 글)' in x.get('credit', ''): return '온라인에 공유된 아름다운 글'
    return '온라인에 공유된 감동적인 글' if '목회 프리미엄' in x.get('credit', '') else '온라인에 공개된 감동적인 예화'
def excerpt_of(x, n=120):
    story = x['body'].split('\n\n')[0].strip()
    cut = story[:n]; dot = max(cut.rfind('다. '), cut.rfind('니다.'))
    return (cut[:dot + 2] if dot > 50 else cut.rstrip() + '…').strip()
def ref_of(x): return (re.search(r'▸ 말씀:.*\(([^()]+)\)\s*$', x['body'], re.M) or [None, ''])[1]
where = {id(x): (k2, i2) for k2 in kws for i2, x in enumerate(by[k2])}
def url_of(x):
    k2, i2 = where[id(x)]; return f'yehwa/{pname(k2, i2 // PER + 1)}#y{i2 + 1}'
newy = [x for x in y if is_new(x)]
SRCS = ['온라인에 공개된 감동적인 예화', '온라인에 공유된 감동적인 글', '온라인에 공유된 아름다운 글', '신문·잡지에 실린 글', '독후감', '역사와 고전']
src_n = {s: sum(1 for x in newy if src_of(x) == s) for s in SRCS}
# 짧았던 예화를 15문장 안팎으로 넉넉히 다시 쓴 것: expand.py가 고칠 때 적는 다시 쓴 때(re)로 센다 — 가장 최근에 다시 쓴 것이 맨 앞
rewritten = sorted((x for x in newy if x.get('re')), key=lambda x: x['re'], reverse=True)
rich = len(rewritten)
rich_today = sum(1 for x in rewritten if x['re'].startswith(KST.strftime('%Y-%m-%d')))
recent = rewritten[:6]
fcards = ''.join(f'<li><a href="{url_of(x)}"><span class="fk">【{esc(x["kw"])}】</span><h3>{esc(x["title"])}</h3>'
                 f'<p>{esc(excerpt_of(x, 90))}</p><span class="fs">{esc(src_of(x))}에서</span></a></li>' for x in recent)
fsrc = ''.join(f'<li><b>{src_n[s]:,}</b><span>{s}</span></li>' for s in SRCS if src_n[s])
fresh = ('<section id="fresh" aria-labelledby="fresh-h"><div class="head"><span class="eyebrow">새로 쓴 예화</span>'
         f'<div class="row"><h2 id="fresh-h">좋은 이야기를 골라, 새 문장으로</h2><a href="yehwa/index.html">새로 쓴 예화 {len(newy):,}편 · 주제별로 보기 →</a></div>'
         '<p class="lede">온라인에 공개된 감동적인 예화와 글, 그리고 제가 읽은 책의 독후감에서 설교에 쓸 만한 이야기를 골라 사실을 확인하고 새 문장으로 다시 썼습니다. '
         '편마다 적용과 개역개정 말씀을 붙이고, 원글의 저자와 출처를 밝혀 두었습니다. '
         f'짧았던 예화는 사실을 더 확인해 15문장 안팎의 넉넉한 이야기로 다시 쓰고 있으며, 지금까지 <b>{rich:,}편</b>을 고쳤습니다.</p></div>'
         f'<ul class="fsrc">{fsrc}</ul><ul class="fcards">{fcards}</ul></section>')
# 오늘의 예화: 새로 쓴 예화 가운데 날짜마다 하나
pool = [(k2, i2) for k2 in kws for i2, x in enumerate(by[k2]) if is_new(x)]
k, i = random.Random(int(KST.strftime('%Y%m%d'))).choice(pool)
x = by[k][i]
excerpt = excerpt_of(x)
ref = ref_of(x)
url = url_of(x)
today = (f'<a class="today" href="{url}"><span class="tag">오늘의 예화<span>{KST.month}월 {KST.day}일</span></span>'
         f'<span class="kw">【{esc(k)}】</span><h2>{esc(x["title"])}</h2><p>{esc(excerpt)}</p>'
         + (f'<span class="verse">말씀 · {esc(ref)}</span>' if ref else '') + '<span class="go">이야기 전체 읽기 →</span></a>')
h = (h.replace('<!--YH-N-->여러', f'{len(y):,}').replace('<!--YH-K-->153', f'{len(kws)}').replace('<!--YH-NEW-->여러', f'{len(newy):,}')
     .replace('<!--YH-FIND-->', find).replace('<!--YH-TODAY-->', today).replace('<!--YH-FRESH-->', fresh))
json.dump({'n': len(y), 'topics': [[k2, slug(k2), len(by[k2])] for k2 in kws], 'pop': POP,
           'new': len(newy), 'rich': rich, 'rich_today': rich_today, 'src': [[s, src_n[s]] for s in SRCS if src_n[s]],
           'recent': [{'kw': x['kw'], 'title': x['title'], 'excerpt': excerpt_of(x, 90), 'src': src_of(x), 'url': SITE + url_of(x)} for x in recent],
           'today': {'kw': k, 'title': x['title'], 'excerpt': excerpt, 'ref': ref, 'url': SITE + url, 'date': f'{KST.month}월 {KST.day}일'}},
          open(os.path.join(OUT, 'front.json'), 'w', encoding='utf-8'), ensure_ascii=False)
# 대문 맨 위 알림 띠: 예화 전체 수 · 새로 쓴 예화 · 넉넉히 다시 쓴 예화 · 가장 최근에 올린 예화
h = re.sub(r'<aside class="yhnews".*?</aside>\s*', '', h, flags=re.S)
latest = recent[0] if recent else None
news = ('<aside class="yhnews" aria-label="예화 새 소식" style="background:#f7f3ea;border-bottom:1px solid #e3ddd0;padding:10px max(24px,calc((100% - 1132px)/2));font-size:.93rem;line-height:1.6">'
        f'<b style="color:#2f5d50">예화 새 소식</b> · {KST.month}월 {KST.day}일 기준 예화 <b>{len(y):,}편</b> — '
        f'새로 쓴 예화 <b>{len(newy):,}편</b>, 짧았던 예화를 넉넉히 다시 쓴 것 <b>{rich:,}편</b>' + (f'(오늘 {rich_today:,}편)' if rich_today else '')
        + (f' · 최근에 다시 쓴 예화 <a href="{url_of(latest)}" style="color:#2f5d50">「{esc(latest["title"])}」</a>' if latest else '')
        + ' · <a href="#fresh" style="color:#2f5d50;font-weight:600">새로 올라온 예화 보기 →</a></aside>\n')
h = h.replace('<main class="container">', news + '<main class="container">', 1)
open(home, 'w', encoding='utf-8').write(h)
# 뜻으로 찾기(search_site.py)가 쓸 예화 목록 — 배포하지 않는 작업 파일
json.dump([{'t': x['title'], 'kw': k2, 'u': url_of(x), 'b': x['body']} for k2 in kws for x in by[k2]],
          open(os.path.join(D, '_yehwa_list.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('예화', len(y), '주제', len(kws))
