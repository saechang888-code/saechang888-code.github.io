# 개인 홈페이지 시안: blog.json(카테고리·대표글) + 작품 이미지 -> index.html (단일 파일)
import json, base64, html, os, re

D = os.path.dirname(os.path.abspath(__file__))
BLOG = 'https://blog.naver.com/saechang888'
data = json.load(open(os.path.join(D, 'blog.json'), encoding='utf-8'))
cats = {c['no']: c for c in data['cats']}
P = {int(k): v for k, v in data['posts'].items()}
cnt = lambda no: cats[no]['cnt']
TOTAL = sum(c['cnt'] for c in data['cats'] if not c['parent'])

def esc(s): return html.escape(s, quote=True)
def url(p): return f"{BLOG}/{p['logNo']}"
def caturl(no): return f'https://blog.naver.com/PostList.naver?blogId=saechang888&categoryNo={no}'
def img(name): return 'assets/' + name

def body(p):
    b = html.unescape(p['brief']).strip()
    t = re.sub(r'^\(.+?\)\s*', '', html.unescape(p['title']))
    t = re.sub(r'^팡세\s*\d+\s*', '', t)
    for head in (t, t.split('(')[0].strip()):
        if head and b.startswith(head):
            b = b[len(head):].strip(); break
    return b

def clip(s, n): return s if len(s) <= n else s[:n].rstrip() + '…'

# ---------- 설교 ----------
SERV = re.compile(r'^(\S*(?:예배|기도회)\S*)\s+(\d{4}년\s*\d+월\s*\d+일\([^)]*\))\s*')
def sermon(p):
    m = re.match(r'\((.+?)\)\s*(.+)', html.unescape(p['title']))
    ref, head = (m.group(1), m.group(2)) if m else ('', p['title'])
    b = body(p); where = ''
    s = SERV.match(b)
    if s: where, b = f'{s.group(1)} · {s.group(2)}', b[s.end():]
    return f'''<li class="card"><a href="{esc(url(p))}" target="_blank" rel="noopener">
<span class="ref">{esc(ref)}</span><h4>{esc(head)}</h4><p>{esc(clip(b, 80))}</p><span class="meta">{esc(where or p['date'])}</span></a></li>'''
sermons = ''.join(sermon(p) for p in P[101][:6])
theory = P[179][0]

# ---------- 성경 책장 ----------
bible = [c for c in data['cats'] if c['parent'] == 101 and c['name'] not in ('구분선', '게시판', '나의 설교론')]
names = [c['name'] for c in bible]
split = names.index('마태복음')
mx = max(c['cnt'] for c in bible)
def spines(lst):
    out = []
    for c in lst:
        h = 46 + round(100 * (c['cnt'] / mx) ** 0.6) if c['cnt'] else 46
        cls = 'spine on' if c['cnt'] else 'spine'
        out.append(f'<li><a class="{cls}" style="height:{h}px" href="{caturl(c["no"])}" target="_blank" rel="noopener" title="{esc(c["name"])} {c["cnt"]}편"><span>{esc(c["name"])}</span><b>{c["cnt"] or ""}</b></a></li>')
    return ''.join(out)
covered = sum(1 for c in bible if c['cnt'])

# ---------- 시 ----------
POEMS = [(91, '자연을 노래하다'), (92, '삶의 자리에서'), (93, '나를 돌아보다'), (94, '하나님께 드리는 노래')]
def poem_col(no, sub):
    lis = ''.join(f'<li><a href="{esc(url(p))}" target="_blank" rel="noopener"><strong>{esc(html.unescape(p["title"]))}</strong><span>{esc(clip(body(p), 46))}</span></a></li>' for p in P[no])
    return f'''<div class="pcol"><div class="pcol-h"><h4>{esc(cats[no]["name"])}</h4><span class="n">{cnt(no)}편</span></div><p class="sub">{sub}</p><ul>{lis}</ul><a class="more" href="{caturl(no)}" target="_blank" rel="noopener">더 읽기 →</a></div>'''
poems = ''.join(poem_col(no, s) for no, s in POEMS)

# ---------- 팡세 ----------
def pensee(p):
    t = html.unescape(p['title']); m = re.match(r'팡세\s*(\d+)\s*(.*)', t)
    num, head = (m.group(1), m.group(2)) if m else ('', t)
    return f'<li><a href="{esc(url(p))}" target="_blank" rel="noopener"><span class="num">{num}</span><div><h4>{esc(head)}</h4><p>{esc(clip(body(p), 70))}</p></div></a></li>'
pensees = ''.join(pensee(p) for p in P[36])

# ---------- 독서 마당 ----------
READ = [(46, '신앙과 신학'), (47, '세상을 읽다'), (45, '고전에서 배우다'), (90, '자녀를 키우는 책')]
def shelf_col(no, sub):
    lis = ''.join(f'<li><a href="{esc(url(p))}" target="_blank" rel="noopener">{esc(html.unescape(p["title"]))}</a><span class="meta">{p["date"]}</span></li>' for p in P[no])
    return f'<div class="rcol"><div class="pcol-h"><h4>{esc(cats[no]["name"])}</h4><span class="n">{cnt(no)}권</span></div><p class="sub">{sub}</p><ol>{lis}</ol><a class="more" href="{caturl(no)}" target="_blank" rel="noopener">목록 보기 →</a></div>'
reads = ''.join(shelf_col(no, s) for no, s in READ)

# ---------- 유튜브 「어음성경」 ----------
YT = data.get('youtube') or {'channel': '', 'videos': [], 'count': None}
YT_URL = 'https://www.youtube.com/@%EB%8F%85%EC%84%9C%ED%8A%B9%EA%B8%B0'
PREVIEW = os.environ.get('PREVIEW') == '1'   # 미리보기는 외부 이미지가 막혀 썸네일을 파일 안에 넣는다
def thumb(vid):
    u = f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg'
    if not PREVIEW: return u
    import urllib.request
    return 'data:image/jpeg;base64,' + base64.b64encode(urllib.request.urlopen(u, timeout=30).read()).decode()
def video(v):
    name = re.sub(r'^어음성경\((.+)\)$', r'\1', v['title'])
    return f'''<li class="vid"><a href="https://www.youtube.com/watch?v={esc(v['id'])}" target="_blank" rel="noopener">
<span class="thumb"><img src="{thumb(v['id'])}" alt="" width="320" height="180" loading="lazy"><span class="play" aria-hidden="true">▶</span></span>
<h4>{esc(name)}</h4><span class="meta">{v['date']}</span></a></li>'''
videos = ''.join(video(v) for v in YT['videos'][:6])
yt_count = f'영상 {YT["count"]}편' if YT.get('count') else '영상'

# ---------- 예화 ----------
stories = ''.join(f'<li><a href="{esc(url(p))}" target="_blank" rel="noopener">{esc(html.unescape(p["title"]))}</a></li>' for p in P[161])

STATS = [(cnt(101), '편', '설교와 성경연구', '#sermon'), (cnt(38), '권', '독후감', '#reading'),
         (cnt(44), '편', '시', '#poems'), (cnt(36), '편', '팡세', '#pensees')]
stats = ''.join(f'<li><a href="{h}"><b>{n:,}</b><small>{u}</small><span>{l}</span></a></li>' for n, u, l, h in STATS)

page = f'''<title>독서주특기</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap">
<style>
/* layout: a reading desk - sticky contents rail on the left, each body of writing gets its own "room": sermons as cards + Bible bookshelf, poems as four anthologies, pensées as a numbered notebook, reading as four shelves */
:root{{
  --paper:#f6f5f0; --sheet:#fffefa; --ink:#1f2a2e; --muted:#62706f; --rule:#dcd8cc;
  --green:#2f5d50; --gold:#a07b32; --tint:#ecebe3;
  --display:"Nanum Myeongjo","Batang",serif; --body:"IBM Plex Sans KR","Malgun Gothic",system-ui,sans-serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#141819;--sheet:#1b2122;--ink:#e8e6df;--muted:#9eaaa7;--rule:#2f3738;--green:#8cc4ad;--gold:#d6b46c;--tint:#20282a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--paper:#141819;--sheet:#1b2122;--ink:#e8e6df;--muted:#9eaaa7;--rule:#2f3738;--green:#8cc4ad;--gold:#d6b46c;--tint:#20282a;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.7;padding-inline:16px;padding-block:0}}
a{{color:inherit}}
a:focus-visible{{outline:2px solid var(--green);outline-offset:3px}}
.wrap{{max-width:1140px;margin:0 auto;display:grid;grid-template-columns:190px minmax(0,1fr);gap:56px}}
nav{{position:sticky;top:env(safe-area-inset-top,0px);align-self:start;padding-block:48px;display:grid;gap:16px}}
.mono{{width:60px;height:60px;border-radius:50%;background:var(--green);color:var(--paper);display:grid;place-items:center;font-family:var(--display);font-weight:800;font-size:1.3rem}}
.blogname{{font-family:var(--display);font-weight:800;font-size:1.15rem}}
nav ol{{list-style:none;margin:0;padding:0;display:grid;gap:4px;font-size:.92rem}}
nav ol a{{text-decoration:none;color:var(--muted);display:flex;justify-content:space-between;gap:8px}}
nav ol a small{{font-variant-numeric:tabular-nums;color:var(--rule)}}
nav ol a:hover{{color:var(--green)}}
main{{display:grid;gap:84px;padding-block:48px 64px}}
.eyebrow{{font-size:.75rem;letter-spacing:.14em;color:var(--gold);font-weight:600}}
h1,h2,h3{{font-family:var(--display);font-weight:800;margin:0;text-wrap:balance}}
h1{{font-size:clamp(2.3rem,6vw,4rem);line-height:1.18}}
h2{{font-size:1.8rem}}
h4{{margin:0}}
.hero{{display:grid;gap:20px}}
.who{{font-size:1.05rem;color:var(--muted);margin:0;max-width:38em}}
.hero blockquote{{margin:0;font-family:var(--display);font-size:1.2rem;line-height:1.85;max-width:34em;border-left:3px solid var(--gold);padding-left:18px}}
.stats{{list-style:none;margin:8px 0 0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid var(--rule)}}
.stats a{{display:grid;grid-template-columns:auto 1fr;align-items:baseline;column-gap:4px;padding:16px 12px;text-decoration:none}}
.stats li+li a{{border-left:1px solid var(--rule)}}
.stats b{{font-family:var(--display);font-size:1.9rem;font-variant-numeric:tabular-nums}}
.stats small{{color:var(--muted)}}
.stats span{{grid-column:1/-1;font-size:.85rem;color:var(--muted)}}
.stats a:hover b{{color:var(--green)}}
section{{display:grid;gap:24px;scroll-margin-top:24px}}
.head{{display:grid;gap:6px}}
.head .row{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px}}
.head .row a{{font-size:.9rem;color:var(--green)}}
.lede{{margin:0;color:var(--muted);max-width:40em}}
.cards{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule)}}
.card a{{display:grid;grid-template-rows:auto auto 1fr auto;gap:6px;height:100%;padding:20px;background:var(--sheet);text-decoration:none}}
.card a:hover h4{{color:var(--green)}}
.ref{{font-size:.78rem;color:var(--gold);font-weight:600}}
.card h4{{font-family:var(--display);font-size:1.12rem;line-height:1.45}}
.card p{{margin:0;color:var(--muted);font-size:.88rem;line-height:1.6}}
.meta{{font-size:.76rem;color:var(--muted);font-variant-numeric:tabular-nums}}
.theory{{display:grid;grid-template-columns:auto 1fr;gap:4px 16px;align-items:baseline;background:var(--tint);padding:18px 20px;text-decoration:none}}
.theory .ref{{grid-row:span 2}}
.theory strong{{font-family:var(--display);font-size:1.1rem}}
.theory span.q{{color:var(--muted);font-size:.9rem}}
.theory:hover strong{{color:var(--green)}}
.shelf{{display:grid;gap:8px}}
.shelf h3{{font-family:var(--body);font-size:.8rem;color:var(--muted);font-weight:600;letter-spacing:.08em}}
.books-scroll{{overflow-x:auto;padding-bottom:4px}}
.books{{list-style:none;margin:0;padding:0;display:flex;gap:3px;align-items:flex-end;border-bottom:3px solid var(--ink);width:max-content;min-width:100%}}
.spine{{width:22px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:5px 0 4px;font-size:.62rem;color:var(--muted);background:var(--rule);border-radius:2px 2px 0 0;text-decoration:none}}
.spine span{{writing-mode:vertical-rl;overflow:hidden;max-height:calc(100% - 16px)}}
.spine.on{{background:var(--green);color:var(--paper)}}
.spine.on:hover{{background:var(--gold)}}
.spine b{{font-size:.6rem;font-variant-numeric:tabular-nums}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:28px}}
.pcol,.rcol{{display:grid;gap:10px;align-content:start;border-top:2px solid var(--ink);padding-top:14px}}
.pcol-h{{display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
.pcol-h h4{{font-family:var(--display);font-size:1.15rem}}
.n{{font-size:.8rem;color:var(--gold);font-weight:600;font-variant-numeric:tabular-nums}}
.sub{{margin:0;font-size:.82rem;color:var(--muted)}}
.pcol ul,.rcol ol{{list-style:none;margin:0;padding:0;display:grid;gap:12px}}
.pcol li a{{display:grid;gap:2px;text-decoration:none}}
.pcol li strong{{font-family:var(--display);font-size:1.02rem}}
.pcol li span{{font-family:var(--display);font-size:.88rem;color:var(--muted);line-height:1.6}}
.pcol li a:hover strong,.rcol li a:hover{{color:var(--green)}}
.rcol li{{display:grid;gap:0}}
.rcol li a{{text-decoration:none;font-weight:500}}
.more{{font-size:.85rem;color:var(--green)}}
.notebook{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:0 32px}}
.notebook a{{display:grid;grid-template-columns:3.2rem 1fr;gap:12px;padding:16px 0;border-bottom:1px solid var(--rule);text-decoration:none}}
.notebook .num{{font-family:var(--display);font-size:1.7rem;color:var(--gold);line-height:1.1;font-variant-numeric:tabular-nums}}
.notebook h4{{font-family:var(--display);font-size:1.08rem}}
.notebook p{{margin:2px 0 0;color:var(--muted);font-size:.87rem;line-height:1.6}}
.notebook a:hover h4{{color:var(--green)}}
.vids{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:22px 18px}}
.vid a{{display:grid;gap:8px;text-decoration:none}}
.thumb{{position:relative;display:block;aspect-ratio:16/9;background:var(--tint);overflow:hidden;border-radius:3px}}
.thumb img{{width:100%;height:100%;object-fit:cover;display:block}}
.play{{position:absolute;right:10px;bottom:10px;width:34px;height:34px;border-radius:50%;background:var(--green);color:var(--paper);display:grid;place-items:center;font-size:.8rem;padding-left:2px}}
.vid h4{{font-family:var(--display);font-size:1.05rem}}
.vid a:hover h4{{color:var(--green)}}
.btn{{justify-self:start;display:inline-block;padding:10px 18px;border:1px solid var(--green);color:var(--green);text-decoration:none;border-radius:2px;font-weight:600;font-size:.92rem}}
.btn:hover{{background:var(--green);color:var(--paper)}}
.stories{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}}
.stories a{{display:inline-block;padding:6px 14px;border:1px solid var(--rule);border-radius:999px;text-decoration:none;font-size:.9rem;background:var(--sheet)}}
.stories a:hover{{border-color:var(--green);color:var(--green)}}
.works{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:20px}}
.work{{display:grid;gap:8px;align-content:start}}
.work img{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}
.song{{aspect-ratio:2/3;border:1px solid var(--rule);background:var(--sheet);display:grid;place-content:center;gap:8px;text-align:center;padding:20px}}
.song .clef{{font-family:var(--display);font-size:2.6rem;color:var(--gold);line-height:1}}
.song strong{{font-family:var(--display);font-size:1.3rem}}
.work h4{{font-size:1rem}}
.work p{{margin:0;font-size:.85rem;color:var(--muted)}}
.church{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:28px;background:var(--sheet);border:1px solid var(--rule);padding:28px}}
.church dl{{margin:0;display:grid;grid-template-columns:auto 1fr;gap:6px 18px;font-size:.95rem}}
.church dt{{color:var(--muted)}}
.church dd{{margin:0;font-variant-numeric:tabular-nums}}
footer{{border-top:1px solid var(--rule);padding-top:20px;color:var(--muted);font-size:.85rem;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px}}
@media (max-width:860px){{
  .wrap{{grid-template-columns:minmax(0,1fr);gap:0}}
  nav{{position:static;padding-block:28px 0;grid-template-columns:auto 1fr;align-items:center}}
  nav ol{{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:4px 16px}}
  nav ol a small{{display:none}}
  main{{padding-block:32px 48px;gap:64px}}
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .stats li:nth-child(3) a{{border-left:0}}
  .stats li:nth-child(n+3) a{{border-top:1px solid var(--rule)}}
}}
@media (prefers-reduced-motion:no-preference){{a{{transition:color .15s,background .15s,border-color .15s}}}}
</style>
<div class="wrap">
<nav aria-label="목차">
  <div class="mono" aria-hidden="true">재선</div>
  <div class="blogname">독서주특기</div>
  <ol>
    <li><a href="#about">소개</a></li>
    <li><a href="#sermon">설교 <small>{cnt(101):,}</small></a></li>
    <li><a href="#youtube">유튜브 <small>{YT.get("count") or ""}</small></a></li>
    <li><a href="#poems">시 <small>{cnt(44)}</small></a></li>
    <li><a href="#pensees">팡세 <small>{cnt(36)}</small></a></li>
    <li><a href="#reading">독후감 <small>{cnt(38)}</small></a></li>
    <li><a href="#stories">예화 <small>{cnt(161)}</small></a></li>
    <li><a href="#works">작품</a></li>
    <li><a href="#church">새암교회</a></li>
  </ol>
</nav>
<main>
  <header class="hero" id="about">
    <span class="eyebrow">새암교회 · 30년 설교자</span>
    <h1>읽고, 묵상하고,<br>삶으로 남기다</h1>
    <p class="who">이재선 목사가 말씀을 전하고, 시를 쓰고, 생각을 적고, 책을 읽은 기록 {TOTAL:,}편을 한곳에 모았습니다.</p>
    <blockquote>독서는 취미가 아닙니다. 특기이며, 특기를 넘어 주특기가 됩니다. 독서로 나의 세계를 바꾸기를 희망하며……</blockquote>
    <ul class="stats">{stats}</ul>
  </header>

  <section id="sermon" aria-labelledby="sermon-h">
    <div class="head"><span class="eyebrow">성경연구와 설교</span><div class="row"><h2 id="sermon-h">강단에서 전한 말씀</h2><a href="{caturl(101)}" target="_blank" rel="noopener">설교 전체 {cnt(101):,}편 →</a></div>
    <p class="lede">주일낮예배와 금요기도회에서 전한 설교입니다. 아래 책장에서 성경 권별로 찾아 읽을 수 있습니다.</p></div>
    <a class="theory" href="{esc(url(theory))}" target="_blank" rel="noopener"><span class="ref">나의 설교론</span><strong>{esc(html.unescape(theory["title"]))}</strong><span class="q">{esc(clip(body(theory), 70))}</span></a>
    <ul class="cards">{sermons}</ul>
    <div class="shelf"><h3>구약 39권 · 성경 책장</h3><div class="books-scroll"><ul class="books">{spines(bible[:split])}</ul></div></div>
    <div class="shelf"><h3>신약 27권</h3><div class="books-scroll"><ul class="books">{spines(bible[split:])}</ul></div></div>
    <p class="lede">66권 가운데 {covered}권을 설교했습니다. 책등이 높을수록 글이 많고, 책을 누르면 그 권의 설교 목록이 열립니다.</p>
  </section>

  <section id="youtube" aria-labelledby="youtube-h">
    <div class="head"><span class="eyebrow">유튜브 · 어음성경</span><div class="row"><h2 id="youtube-h">들으면서 읽는 성경</h2><a href="{YT_URL}" target="_blank" rel="noopener">채널 바로가기 · {yt_count} →</a></div>
    <p class="lede">창세기부터 요한계시록까지 성경 66권 전 장을 음악으로 만드는 통독 프로젝트입니다. 자막의 말씀을 따라 읽거나, 큐티와 기도 시간에 틀어 두고 들을 수 있습니다.</p></div>
    <ul class="vids">{videos}</ul>
    <a class="btn" href="{YT_URL}?sub_confirmation=1" target="_blank" rel="noopener">구독하고 새 영상 받기</a>
  </section>

  <section id="poems" aria-labelledby="poems-h">
    <div class="head"><span class="eyebrow">시</span><div class="row"><h2 id="poems-h">네 권의 시집</h2><a href="{caturl(44)}" target="_blank" rel="noopener">시 전체 {cnt(44)}편 →</a></div></div>
    <div class="cols">{poems}</div>
  </section>

  <section id="pensees" aria-labelledby="pensees-h">
    <div class="head"><span class="eyebrow">나의 팡세</span><div class="row"><h2 id="pensees-h">생각의 노트</h2><a href="{caturl(36)}" target="_blank" rel="noopener">팡세 전체 {cnt(36)}편 →</a></div>
    <p class="lede">목회와 신앙, 삶에 대해 떠오른 생각을 번호를 매겨 적어 온 노트입니다.</p></div>
    <ol class="notebook">{pensees}</ol>
  </section>

  <section id="reading" aria-labelledby="reading-h">
    <div class="head"><span class="eyebrow">독서 마당</span><div class="row"><h2 id="reading-h">읽은 책, 남긴 생각</h2><a href="{caturl(38)}" target="_blank" rel="noopener">독후감 전체 {cnt(38)}편 →</a></div></div>
    <div class="cols">{reads}</div>
  </section>

  <section id="stories" aria-labelledby="stories-h">
    <div class="head"><span class="eyebrow">은혜되는 예화</span><div class="row"><h2 id="stories-h">설교에 쓰는 이야기</h2><a href="{caturl(161)}" target="_blank" rel="noopener">예화 전체 {cnt(161)}편 →</a></div></div>
    <ul class="stories">{stories}</ul>
  </section>

  <section id="works" aria-labelledby="works-h">
    <div class="head"><span class="eyebrow">작품</span><h2 id="works-h">만든 것들</h2></div>
    <ul class="works">
      <li class="work"><img src="{img('invite.jpg')}" alt="행복나눔축제 초대장: 12월 6일 주일 오전 11시 새암교회 본당, 특별강사 이성미 집사" width="480" height="720"><h4>행복나눔축제 초대장</h4><p>2026 전도집회 · 새암교회 본당</p></li>
      <li class="work"><img src="{img('poster.jpg')}" alt="행복나눔축제 포스터: 함께 음식을 나누는 가족과 이웃 일러스트" width="480" height="679"><h4>행복나눔축제 포스터</h4><p>A3 인쇄용 · 일러스트</p></li>
      <li class="work"><div class="song"><span class="clef" aria-hidden="true">𝄞</span><strong>태초에 말씀이</strong><span class="meta">요한복음 1장 · G · ♩=76</span></div><h4>찬양 「태초에 말씀이」</h4><p>요한복음 1장 CCM 찬양</p></li>
    </ul>
  </section>

  <section id="church" aria-labelledby="church-h">
    <div class="head"><span class="eyebrow">섬기는 교회</span><h2 id="church-h">새암교회</h2></div>
    <div class="church">
      <dl><dt>교단</dt><dd>대한예수교장로회(합동)</dd><dt>주소</dt><dd>경기도 용인시 수지구 고기로 165<br>(동천동)</dd><dt>전화</dt><dd>031-262-3440</dd></dl>
      <dl><dt>주일예배</dt><dd>오전 11시</dd><dt>새벽기도회</dt><dd>매일 오전 6시</dd><dt>금요기도회</dt><dd>금요일 오후 8시 30분</dd></dl>
    </div>
  </section>

  <footer><span>독서주특기 · 이재선</span><a href="{BLOG}" target="_blank" rel="noopener">blog.naver.com/saechang888</a></footer>
</main>
</div>'''
open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(page)
print('ok total', TOTAL, 'bible books covered', covered, 'of', len(bible))
