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
# 둘로스·sermon-jesus 예화와 둘로스 설교 속 예화를 제미나이로 새로 쓴 것(예화작업/export.py가 만든다) — 손으로 쓴 것 다음에
ai = os.path.join(D, 'yehwa_ai.json')
if os.path.exists(ai):
    n_hand = sum(1 for x in y if x.get('credit'))
    y = y[:n_hand] + json.load(open(ai, encoding='utf-8')) + y[n_hand:]
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

# 목회 프리미엄 골드(USB)에서 고른 글은 '온라인에 공유된 감동적인 글', 둘로스 자료는 '온라인에 공개된 감동적인 예화'로 적는다
def credit_txt(c):
    if '목회 프리미엄' in c: return re.sub(r'\s*\(목회 프리미엄.*\)$', '', c) + ' (온라인에 공유된 감동적인 글)'
    # 둘로스 자료에서 고른 글은 원글 제목만 두고 출처는 '온라인에 공개된 감동적인 예화'로 적는다
    t = re.search(r'「[^」]*」', c)
    return (t.group(0) + ' ' if t else '') + '(온라인에 공개된 감동적인 예화)'
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
def pname(kw, p): return slug(kw) + ('' if p == 1 else f'-{p}') + '.html'
for i, kw in enumerate(kws):
    allit = by[kw]; npg = (len(allit) + PER - 1) // PER
    for p in range(1, npg + 1):
        items = allit[(p - 1) * PER:p * PER]; base = (p - 1) * PER
        toc = ''.join(f'<a href="#y{base + j + 1}">{base + j + 1}. {esc(x["title"])}</a>' for j, x in enumerate(items))
        arts = ''.join(f'<article id="y{base + j + 1}"><h3>{base + j + 1}. {esc(x["title"])}</h3>'
                       + ''.join(f'<p>{esc(l.strip())}</p>' for l in x['body'].split('\n') if l.strip())
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
GROUPS = [(p, ' '.join(groups[p])) for p in sorted(groups)]
new_kw = {x['kw'] for x in y if x.get('credit')}
mx = max(len(v) for v in by.values())
def spine(k):
    n = len(by[k]); hgt = 46 + round(100 * (n / mx) ** 0.6)
    tip = f'{k} 예화 {n}편' + (' · 새로 쓴 예화 포함' if k in new_kw else '')
    return (f'<li><a class="spine on" style="height:{hgt}px" href="yehwa/{slug(k)}.html" title="{esc(tip)}">'
            f'<span>{esc(k)}{"✦" if k in new_kw else ""}</span><b>{n}</b></a></li>')
cards = ''.join(f'<div class="shelf"' + (' style="grid-column:1/-1"' if len([k for k in ks.split() if k in by]) > 17 else '') + f'><h3>{g} · {sum(len(by[k]) for k in ks.split() if k in by):,}편</h3><div class="books-scroll"><ul class="books">'
                + ''.join(spine(k) for k in ks.split() if k in by) + '</ul></div></div>' for g, ks in GROUPS)
STY = ('<style>.ygrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:14px;margin:6px 0 14px}'
       '.yblog summary{cursor:pointer;color:var(--muted);margin:4px 0 10px}.ymore{margin:0 0 12px;font-size:.92rem}</style>')
m = re.search(r'(<section id="stories"[^>]*>.*?</div></div>\s*)(?:<style>\.ygrid.*?</details>|<ul class="stories">.*?</ul>)', h, re.S)
if m:
    blog = re.search(r'<ul class="stories">.*?</ul>', h[m.start():], re.S).group(0)
    body = (STY + f'<div class="ygrid">{cards}</div>'
            + f'<p class="ymore">✦ 표시는 새로 쓴 예화가 들어 있는 주제입니다. <a href="yehwa/index.html">주제 {len(kws)}가지 · 예화 {len(y):,}편 모두 보기 →</a></p>'
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
        '<form id="yfind" role="search" action="yehwa/index.html"><input id="yq" name="q" list="ykws" placeholder="예: 감사, 용서, 고난, 부부" autocomplete="off" enterkeyhint="search">'
        '<button type="submit">예화 찾기</button></form>'
        '<datalist id="ykws">' + ''.join(f'<option value="{esc(k)}">' for k in kws) + '</datalist>'
        '<div class="chips">' + ''.join(f'<a href="yehwa/{slug(k)}.html">{esc(k)}</a>' for k in POP) + f'<a href="yehwa/index.html">주제 {len(kws)}가지 모두</a></div>'
        '<p class="msg" id="ymsg" aria-live="polite"></p></div>\n'
        '<script>(function(){var T=' + json.dumps(T, ensure_ascii=False) + ';'
        "var f=document.getElementById('yfind'),q=document.getElementById('yq'),m=document.getElementById('ymsg');"
        "f.addEventListener('submit',function(e){e.preventDefault();var s=q.value.replace(/[【】\\s]/g,'');if(!s)return;"
        "if(T[s]){location.href='yehwa/'+T[s]+'.html';return;}"
        "var k=Object.keys(T).filter(function(k){return k.indexOf(s)>=0||s.indexOf(k)>=0;});"
        "if(k.length===1){location.href='yehwa/'+T[k[0]]+'.html';return;}"
        "m.innerHTML=k.length?'비슷한 주제: '+k.slice(0,8).map(function(x){return '<a href=\"yehwa/'+T[x]+'.html\" style=\"color:inherit\">'+x+'</a>';}).join(' · ')"
        ":'「'+s.replace(/[<>&]/g,'')+'」 주제는 아직 없습니다. <a href=\"yehwa/index.html\" style=\"color:inherit\">주제 목록 보기 →</a>';});})();</script>")
# 새로 쓴 예화: 온라인에 공개된 감동적인 예화 · 온라인에 공유된 감동적인 글 · 독후감 · 역사와 고전에서 골라 새 문장으로 쓴 것
def is_new(x): return bool(x.get('credit') or x.get('book') or x.get('origin'))
def src_of(x):
    if x.get('book'): return '독후감'
    if x.get('origin'): return '역사와 고전'
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
SRCS = ['온라인에 공개된 감동적인 예화', '온라인에 공유된 감동적인 글', '독후감', '역사와 고전']
src_n = {s: sum(1 for x in newy if src_of(x) == s) for s in SRCS}
# 가장 최근에 쓴 것: yehwa_ai.json 끝에서부터 (export.py가 새 예화를 뒤에 붙인다)
recent = (json.load(open(ai, encoding='utf-8')) if os.path.exists(ai) else [])[::-1]
ttl = {(x.get('kw'), x['title']): x for x in newy}
recent = [ttl[(r.get('kw'), r['title'])] for r in recent if (r.get('kw'), r['title']) in ttl][:6]
fcards = ''.join(f'<li><a href="{url_of(x)}"><span class="fk">【{esc(x["kw"])}】</span><h3>{esc(x["title"])}</h3>'
                 f'<p>{esc(excerpt_of(x, 90))}</p><span class="fs">{esc(src_of(x))}에서</span></a></li>' for x in recent)
fsrc = ''.join(f'<li><b>{src_n[s]:,}</b><span>{s}</span></li>' for s in SRCS if src_n[s])
fresh = ('<section id="fresh" aria-labelledby="fresh-h"><div class="head"><span class="eyebrow">새로 쓴 예화</span>'
         f'<div class="row"><h2 id="fresh-h">좋은 이야기를 골라, 새 문장으로</h2><a href="yehwa/index.html">새로 쓴 예화 {len(newy):,}편 · 주제별로 보기 →</a></div>'
         '<p class="lede">온라인에 공개된 감동적인 예화와 글, 그리고 제가 읽은 책의 독후감에서 설교에 쓸 만한 이야기를 골라 사실을 확인하고 새 문장으로 다시 썼습니다. '
         '편마다 적용과 개역개정 말씀을 붙이고, 원글의 저자와 출처를 밝혀 두었습니다.</p></div>'
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
           'new': len(newy), 'src': [[s, src_n[s]] for s in SRCS if src_n[s]],
           'recent': [{'kw': x['kw'], 'title': x['title'], 'excerpt': excerpt_of(x, 90), 'src': src_of(x), 'url': SITE + url_of(x)} for x in recent],
           'today': {'kw': k, 'title': x['title'], 'excerpt': excerpt, 'ref': ref, 'url': SITE + url, 'date': f'{KST.month}월 {KST.day}일'}},
          open(os.path.join(OUT, 'front.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(home, 'w', encoding='utf-8').write(h)
print('예화', len(y), '주제', len(kws))
