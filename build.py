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
    # 옮겨 온 설교 글 머리의 [제목]·[카테고리]·[원본 파일 경로] 꼬리표는 요약에서 뺀다
    b = re.sub(r'^.*?\[원본 파일\].*?\.(?:hwpx?|docx?|txt)\s*', '', b, flags=re.S | re.I)
    b = re.sub(r'\[(?:제목|카테고리)\][^\[]*', '', b).replace('[본문]', '본문:').strip()
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

AN = len(json.load(open(os.path.join(D, 'anshik_poems.json'), encoding='utf-8'))) if os.path.exists(os.path.join(D, 'anshik_poems.json')) else 0
STATS = [(cnt(101), '편', '설교와 성경연구', '#sermon'), (cnt(38), '권', '독후감', '#reading'),
         (cnt(44) + AN, '편', '시', '#poems'), (cnt(36), '편', '팡세', '#pensees')]
stats = ''.join(f'<li><a href="{h}"><b>{n:,}</b><small>{u}</small><span>{l}</span></a></li>' for n, u, l, h in STATS)

page = f'''<title>독서주특기 · 이재선 목사</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600;700;900&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
/* 대문: 창가 책상 그림 위에 큰 명조 제목 · 본문: 프리텐다드 · 색: 짙은 숲색 + 아이보리 + 금색 */
:root{{
  --paper:#f7f4ec; --sheet:#fffdf8; --ink:#1c2624; --muted:#66706c; --rule:#e5dece;
  --green:#23443a; --green2:#2f5d50; --gold:#b08a3e; --gold2:#d9b86a; --tint:#efeadf; --cream:#f6efe0;
  --shadow:0 1px 2px rgba(28,38,36,.05),0 8px 24px -12px rgba(28,38,36,.18);
  --display:"Noto Serif KR","Nanum Myeongjo","Batang",serif;
  --body:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--green2:#8cc4ad;--gold:#d9b86a;--tint:#1f2826;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px -12px rgba(0,0,0,.6);color-scheme:dark}}}}
:root[data-theme="dark"]{{--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--green2:#8cc4ad;--gold:#d9b86a;--tint:#1f2826;--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px -12px rgba(0,0,0,.6);color-scheme:dark}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:84px}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:16.5px;line-height:1.75;word-break:keep-all;-webkit-font-smoothing:antialiased}}
a{{color:inherit}}
a:focus-visible{{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}}
.container{{max-width:1180px;margin:0 auto;padding-inline:24px}}
h1,h2,h3{{font-family:var(--display);margin:0;text-wrap:balance;letter-spacing:-.02em}}
h4{{margin:0}}

/* 머리 막대 */
.topbar{{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--paper) 86%,transparent);backdrop-filter:saturate(1.4) blur(12px);-webkit-backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--rule);padding-top:env(safe-area-inset-top,0px)}}
.topbar .container{{display:flex;align-items:center;gap:28px;height:68px}}
.brand{{display:flex;align-items:center;gap:12px;text-decoration:none;flex:none}}
.mono{{width:40px;height:40px;border-radius:50%;background:var(--green);color:var(--cream);display:grid;place-items:center;font-family:var(--display);font-weight:700;font-size:.92rem;box-shadow:inset 0 0 0 2px color-mix(in srgb,var(--gold2) 70%,transparent)}}
.brand b{{font-family:var(--display);font-weight:700;font-size:1.18rem;letter-spacing:-.02em;display:block;line-height:1.2}}
.brand small{{display:block;font-size:.72rem;color:var(--muted);letter-spacing:.06em}}
nav.menu{{margin-left:auto;min-width:0}}
nav.menu ol{{list-style:none;margin:0;padding:0;display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
nav.menu ol::-webkit-scrollbar{{display:none}}
nav.menu a{{display:block;white-space:nowrap;text-decoration:none;color:var(--muted);font-size:.92rem;font-weight:500;padding:8px 12px;border-radius:99px}}
nav.menu a small{{display:none}}
nav.menu a:hover{{color:var(--ink);background:var(--tint)}}

/* 행사 띠 (event.py가 대문 앞에 넣는다) */
.evbanner{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;background:linear-gradient(90deg,#7a1f33,#a3324b);color:#fff;padding:12px max(24px,calc((100% - 1132px)/2));text-decoration:none;font-size:.93rem}}
.evbanner b{{font-family:var(--display);font-size:1.05rem}}
.evbanner .dd{{background:#fff;color:#a3324b;border-radius:99px;padding:1px 11px;font-weight:700;font-variant-numeric:tabular-nums}}
.evbanner a{{color:#fff;font-weight:600;margin-left:auto;text-underline-offset:3px}}

/* 대문: 왼쪽 글·예화 찾기, 오른쪽 '오늘의 예화' 카드, 아래 숫자 띠 */
.hero{{position:relative;color:var(--cream);background:#1d3530 url(assets/hero.jpg) 72% 50%/cover no-repeat;isolation:isolate}}
.hero::before{{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(14,28,24,.96) 0%,rgba(14,28,24,.86) 42%,rgba(14,28,24,.42) 70%,rgba(14,28,24,.2) 100%),linear-gradient(0deg,rgba(14,28,24,.92),rgba(14,28,24,0) 38%)}}
.hero .container{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);align-items:center;gap:40px 56px;padding-block:clamp(56px,9vh,104px) 36px}}
.hero-main{{display:grid;gap:24px;align-content:center}}
.hero .eyebrow{{color:var(--gold2)}}
.hero .eyebrow::before{{background:var(--gold2)}}
.hero h1{{font-size:clamp(2.5rem,5.8vw,4.6rem);line-height:1.16;font-weight:700;text-shadow:0 2px 24px rgba(0,0,0,.3)}}
.hero h1 em{{font-style:normal;color:var(--gold2)}}
.who{{font-size:1.08rem;margin:0;max-width:33em;color:rgba(246,239,224,.86);line-height:1.85}}
.who b{{color:#fff;font-weight:600}}
.finder{{display:grid;gap:12px;max-width:560px}}
.finder label{{font-size:.86rem;letter-spacing:.04em;color:rgba(246,239,224,.72)}}
.finder form{{display:flex;align-items:center;background:rgba(253,250,243,.97);border-radius:99px;padding:6px 6px 6px 22px;box-shadow:0 18px 40px -18px rgba(0,0,0,.6),inset 0 0 0 1px rgba(217,184,106,.5)}}
.finder input{{flex:1;min-width:0;border:0;background:transparent;font:inherit;font-size:1.02rem;color:#1c2624;outline:0;padding:8px 0}}
.finder input::placeholder{{color:#8a918d}}
.finder button{{flex:none;border:0;border-radius:99px;background:var(--green);color:var(--cream);font:inherit;font-weight:600;font-size:.95rem;padding:11px 22px;cursor:pointer}}
.finder button:hover{{background:#1a332c}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chips a{{text-decoration:none;font-size:.86rem;color:rgba(246,239,224,.9);border:1px solid rgba(246,239,224,.24);border-radius:99px;padding:4px 13px;background:rgba(246,239,224,.05)}}
.chips a:hover{{border-color:var(--gold2);color:var(--gold2)}}
.finder .msg{{margin:0;font-size:.85rem;color:var(--gold2);min-height:1.2em}}
.today{{position:relative;display:grid;gap:14px;align-content:start;padding:28px 28px 24px;border-radius:20px;background:rgba(20,36,31,.62);border:1px solid rgba(217,184,106,.32);backdrop-filter:blur(14px) saturate(1.2);-webkit-backdrop-filter:blur(14px) saturate(1.2);box-shadow:0 30px 60px -30px rgba(0,0,0,.7);text-decoration:none;color:var(--cream)}}
.today .tag{{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:.78rem;letter-spacing:.14em;color:var(--gold2);font-weight:700}}
.today .tag span{{letter-spacing:0;font-weight:500;color:rgba(246,239,224,.6);font-variant-numeric:tabular-nums}}
.today .kw{{justify-self:start;font-size:.8rem;color:#1d2a26;background:var(--gold2);border-radius:99px;padding:2px 12px;font-weight:700}}
.today h2{{font-size:1.45rem;line-height:1.45;font-weight:700;color:#fff}}
.today p{{margin:0;font-family:var(--display);font-size:.98rem;line-height:1.85;color:rgba(246,239,224,.84)}}
.today .verse{{font-size:.88rem;color:rgba(246,239,224,.62);border-top:1px solid rgba(246,239,224,.14);padding-top:12px}}
.today .go{{font-size:.9rem;font-weight:600;color:var(--gold2)}}
.today:hover{{border-color:var(--gold2)}}
.today:hover h2{{color:var(--gold2)}}
.motto{{margin:0;font-family:var(--display);font-size:.95rem;color:rgba(246,239,224,.62)}}
.motto::before{{content:"“";color:var(--gold2);margin-right:4px}}
.motto::after{{content:"”";color:var(--gold2);margin-left:2px}}
.cta{{display:flex;flex-wrap:wrap;gap:12px}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:13px 22px;border-radius:99px;text-decoration:none;font-weight:600;font-size:.95rem;border:1px solid var(--green2);color:var(--green2)}}
.btn:hover{{background:var(--green2);color:var(--paper)}}
.btn.gold{{background:var(--gold2);border-color:var(--gold2);color:#1d2a26}}
.btn.gold:hover{{background:#e8cb84;color:#1d2a26}}
.btn.ghost{{border-color:rgba(246,239,224,.5);color:var(--cream)}}
.btn.ghost:hover{{background:rgba(246,239,224,.12);color:var(--cream)}}
.stats{{grid-column:1/-1;list-style:none;margin:8px 0 0;padding:22px 0 0;display:flex;flex-wrap:wrap;border-top:1px solid rgba(246,239,224,.16)}}
.stats li{{flex:1 1 140px}}
.stats li+li a{{border-left:1px solid rgba(246,239,224,.14)}}
.stats a{{display:grid;grid-template-columns:auto 1fr;align-items:baseline;column-gap:4px;padding:6px 22px;text-decoration:none}}
.stats li:first-child a{{padding-left:0}}
.stats b{{font-family:var(--display);font-size:clamp(1.5rem,2.4vw,2rem);font-weight:600;font-variant-numeric:tabular-nums;color:#fff}}
.stats small{{color:rgba(246,239,224,.6)}}
.stats span{{grid-column:1/-1;font-size:.82rem;letter-spacing:.04em;color:rgba(246,239,224,.68)}}
.stats a:hover b{{color:var(--gold2)}}

/* 본문 */
main{{display:grid;grid-template-columns:minmax(0,1fr);gap:104px;padding-block:96px 104px}}
section{{display:grid;grid-template-columns:minmax(0,1fr);gap:28px}}
.shelf,.head{{min-width:0}}
.eyebrow{{display:inline-flex;align-items:center;gap:10px;font-size:.78rem;letter-spacing:.16em;color:var(--gold);font-weight:700}}
.eyebrow::before{{content:"";width:22px;height:1.5px;background:var(--gold)}}
.head{{display:grid;gap:10px}}
.head .row{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px 20px}}
.head h2{{font-size:clamp(1.8rem,3.4vw,2.4rem);font-weight:700;line-height:1.25}}
.head .row a{{font-size:.92rem;font-weight:600;color:var(--green2);text-decoration:none;border-bottom:1px solid currentColor;padding-bottom:1px}}
.lede{{margin:0;color:var(--muted);max-width:42em;font-size:1.02rem}}
.cards{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:18px}}
.card a{{display:grid;grid-template-rows:auto auto 1fr auto;gap:8px;height:100%;padding:24px 24px 20px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;box-shadow:var(--shadow);text-decoration:none}}
.card a:hover{{transform:translateY(-3px);border-color:color-mix(in srgb,var(--gold) 45%,var(--rule))}}
.card a:hover h4{{color:var(--green2)}}
.ref{{justify-self:start;font-size:.74rem;color:var(--gold);font-weight:700;letter-spacing:.04em;background:color-mix(in srgb,var(--gold) 12%,transparent);padding:2px 10px;border-radius:99px}}
.card h4{{font-family:var(--display);font-size:1.16rem;font-weight:600;line-height:1.5}}
.card p{{margin:0;color:var(--muted);font-size:.9rem;line-height:1.65}}
.meta{{font-size:.78rem;color:var(--muted);font-variant-numeric:tabular-nums}}
.theory{{display:grid;grid-template-columns:auto 1fr;gap:4px 18px;align-items:baseline;background:var(--green);color:var(--cream);padding:22px 26px;border-radius:16px;text-decoration:none}}
.theory .ref{{grid-row:span 2;background:rgba(217,184,106,.18);color:var(--gold2)}}
.theory strong{{font-family:var(--display);font-size:1.2rem;font-weight:600}}
.theory span.q{{color:rgba(246,239,224,.75);font-size:.92rem}}
.theory:hover strong{{color:var(--gold2)}}
.shelf{{display:grid;gap:10px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;padding:20px 22px 16px}}
.shelf h3{{font-family:var(--body);font-size:.8rem;color:var(--muted);font-weight:700;letter-spacing:.1em}}
.books-scroll{{overflow-x:auto;padding-bottom:6px}}
.books{{list-style:none;margin:0;padding:0;display:flex;gap:3px;align-items:flex-end;border-bottom:4px solid #6b4f2e;width:max-content;min-width:100%}}
.spine{{width:23px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:6px 0 4px;font-size:.62rem;color:var(--muted);background:var(--tint);border-radius:3px 3px 0 0;text-decoration:none}}
.spine span{{writing-mode:vertical-rl;overflow:hidden;max-height:calc(100% - 16px)}}
.spine.on{{background:linear-gradient(180deg,var(--gold) 0 4px,var(--green) 4px);color:var(--cream)}}
.books li:nth-child(3n+2) .spine.on{{background:linear-gradient(180deg,var(--gold) 0 4px,#355f52 4px)}}
.books li:nth-child(3n) .spine.on{{background:linear-gradient(180deg,var(--gold) 0 4px,#1b382f 4px)}}
.books .spine.on:hover{{background:var(--gold);color:#1d2a26}}
.spine b{{font-size:.6rem;font-variant-numeric:tabular-nums}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}}
.pcol,.rcol{{display:grid;gap:12px;align-content:start;background:var(--sheet);border:1px solid var(--rule);border-top:3px solid var(--green2);border-radius:14px;padding:22px}}
.pcol-h{{display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
.pcol-h h4{{font-family:var(--display);font-size:1.18rem;font-weight:700}}
.n{{font-size:.8rem;color:var(--gold);font-weight:700;font-variant-numeric:tabular-nums}}
.sub{{margin:0;font-size:.84rem;color:var(--muted)}}
.pcol ul,.rcol ol{{list-style:none;margin:0;padding:0;display:grid;gap:14px}}
.pcol li a{{display:grid;gap:2px;text-decoration:none}}
.pcol li strong{{font-family:var(--display);font-size:1.03rem;font-weight:600}}
.pcol li span{{font-family:var(--display);font-size:.88rem;color:var(--muted);line-height:1.65}}
.pcol li a:hover strong,.rcol li a:hover{{color:var(--green2)}}
.rcol li{{display:grid;gap:0;padding-bottom:10px;border-bottom:1px dashed var(--rule)}}
.rcol li a{{text-decoration:none;font-weight:500}}
.more{{font-size:.88rem;font-weight:600;color:var(--green2);text-decoration:none}}
.notebook{{list-style:none;margin:0;padding:8px 28px;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:0 40px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;background-image:linear-gradient(90deg,transparent 0 calc(100% - 1px),var(--rule) 0);background-size:100% 100%}}
.notebook a{{display:grid;grid-template-columns:3.4rem 1fr;gap:14px;padding:20px 0;border-bottom:1px solid var(--rule);text-decoration:none}}
.notebook .num{{font-family:var(--display);font-size:1.9rem;font-weight:500;color:var(--gold);line-height:1.1;font-variant-numeric:tabular-nums}}
.notebook h4{{font-family:var(--display);font-size:1.1rem;font-weight:600}}
.notebook p{{margin:4px 0 0;color:var(--muted);font-size:.88rem;line-height:1.65}}
.notebook a:hover h4{{color:var(--green2)}}
.yt{{background:var(--green);color:var(--cream);border-radius:24px;padding:clamp(24px,4vw,48px)}}
.yt .eyebrow{{color:var(--gold2)}}.yt .eyebrow::before{{background:var(--gold2)}}
.yt .lede{{color:rgba(246,239,224,.78)}}
.yt .head .row a{{color:var(--gold2)}}
.vids{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:26px 20px}}
.vid a{{display:grid;gap:10px;text-decoration:none}}
.thumb{{position:relative;display:block;aspect-ratio:16/9;background:rgba(0,0,0,.2);overflow:hidden;border-radius:12px;box-shadow:0 10px 30px -14px rgba(0,0,0,.6)}}
.thumb img{{width:100%;height:100%;object-fit:cover;display:block}}
.play{{position:absolute;right:10px;bottom:10px;width:38px;height:38px;border-radius:50%;background:var(--gold2);color:#1d2a26;display:grid;place-items:center;font-size:.8rem;padding-left:2px}}
.vid h4{{font-family:var(--display);font-size:1.04rem;font-weight:600;line-height:1.45}}
.vid .meta{{color:rgba(246,239,224,.6)}}
.vid a:hover h4{{color:var(--gold2)}}
.vid a:hover img{{transform:scale(1.04)}}
.thumb img{{transition:transform .4s}}
.yt .btn{{justify-self:start}}
.stories{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:10px}}
.stories a{{display:inline-block;padding:8px 16px;border:1px solid var(--rule);border-radius:999px;text-decoration:none;font-size:.92rem;background:var(--sheet)}}
.stories a:hover{{border-color:var(--gold);color:var(--green2)}}
.works{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}
.work{{display:grid;gap:10px;align-content:start}}
.work img{{width:100%;height:auto;display:block;border-radius:12px;box-shadow:var(--shadow)}}
.song{{aspect-ratio:2/3;border-radius:12px;background:var(--green);color:var(--cream);display:grid;place-content:center;gap:10px;text-align:center;padding:20px;box-shadow:var(--shadow)}}
.song .clef{{font-family:var(--display);font-size:3rem;color:var(--gold2);line-height:1}}
.song strong{{font-family:var(--display);font-size:1.35rem}}
.song .meta{{color:rgba(246,239,224,.7)}}
.work h4{{font-size:1rem;font-weight:600}}
.work p{{margin:0;font-size:.86rem;color:var(--muted)}}
.church{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:28px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;padding:30px;box-shadow:var(--shadow)}}
.church dl{{margin:0;display:grid;grid-template-columns:auto 1fr;gap:8px 20px;font-size:.97rem}}
.church dt{{color:var(--muted)}}
.church dd{{margin:0;font-variant-numeric:tabular-nums}}
footer{{background:#16261f;color:rgba(246,239,224,.7);font-size:.88rem;padding-bottom:env(safe-area-inset-bottom,0px)}}
footer .container{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;padding-block:36px}}
footer b{{font-family:var(--display);color:var(--cream);font-size:1.05rem}}
footer a{{color:var(--gold2);text-decoration:none}}
@media (max-width:860px){{
  .topbar .container{{height:auto;flex-wrap:wrap;gap:4px 16px;padding-block:10px 6px}}
  nav.menu{{margin-left:0;width:100%}}
  nav.menu a{{padding:6px 10px;font-size:.88rem}}
  html{{scroll-padding-top:120px}}
  .hero{{background-position:78% 50%}}
  .hero::before{{background:linear-gradient(180deg,rgba(14,28,24,.78),rgba(14,28,24,.94))}}
  .hero .container{{grid-template-columns:minmax(0,1fr);padding-block:52px 32px;gap:32px}}
  .stats li{{flex:1 1 33%}}
  .stats li a,.stats li+li a{{border-left:0;padding:8px 12px 8px 0}}
  main{{gap:76px;padding-block:64px 72px}}
  .notebook{{padding:4px 20px;background-image:none}}
}}
/* 새로 쓴 예화 */
.fsrc{{list-style:none;margin:0 0 18px;padding:0;display:flex;flex-wrap:wrap;gap:10px}}
.fsrc li{{display:flex;align-items:baseline;gap:6px;background:var(--sheet);border:1px solid var(--rule);border-radius:99px;padding:6px 16px}}
.fsrc b{{font-family:var(--display);font-size:1.15rem;color:var(--green);font-variant-numeric:tabular-nums}}
.fsrc span{{font-size:.9rem;color:var(--muted)}}
.fcards{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:16px}}
.fcards a{{height:100%;display:grid;align-content:start;gap:8px;background:var(--sheet);border:1px solid var(--rule);border-top:3px solid var(--gold);border-radius:14px;padding:20px 22px;text-decoration:none;box-shadow:var(--shadow)}}
.fcards a:hover{{border-color:var(--gold);transform:translateY(-2px)}}
.fcards .fk{{font-size:.82rem;font-weight:700;color:var(--gold)}}
.fcards h3{{font-size:1.12rem;line-height:1.45}}
.fcards p{{margin:0;color:var(--muted);font-size:.94rem;line-height:1.75}}
.fcards .fs{{font-size:.8rem;color:var(--muted);border-top:1px dashed var(--rule);padding-top:8px;margin-top:4px}}
@media (prefers-reduced-motion:no-preference){{a{{transition:color .2s,background .2s,border-color .2s,transform .25s}}}}
@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
</style>
<header class="topbar">
<div class="container">
  <a class="brand" href="#about"><span class="mono" aria-hidden="true">재선</span><span><b>독서주특기</b><small>이재선 목사 · 새암교회</small></span></a>
  <nav class="menu" aria-label="목차">
  <ol>
    <li><a href="#sermon">설교 <small>{cnt(101):,}</small></a></li>
    <li><a href="#youtube">유튜브 <small>{YT.get("count") or ""}</small></a></li>
    <li><a href="#poems">시 <small>{cnt(44) + AN}</small></a></li>
    <li><a href="#pensees">팡세 <small>{cnt(36)}</small></a></li>
    <li><a href="#reading">독후감 <small>{cnt(38)}</small></a></li>
    <li><a href="#stories">예화 <small>{cnt(161)}</small></a></li>
    <li><a href="#works">작품</a></li>
    <li><a href="#church">새암교회</a></li>
  </ol>
  </nav>
</div>
</header>
<header class="hero" id="about">
  <div class="container">
    <div class="hero-main">
      <span class="eyebrow">새암교회 담임 · 이재선 목사의 서재</span>
      <h1>말씀을 읽고,<br><em>이야기</em>로 전하다</h1>
      <p class="who">30년 강단에서 전한 설교, <b><!--YH-K-->153</b>가지 주제로 엮은 예화 <b><!--YH-N-->여러</b>편. 설교자료와 목회 자료집, 독후감에서 좋은 이야기를 골라 새 문장으로 다시 쓴 예화 <b><!--YH-NEW-->여러</b>편이 날마다 더해집니다. 설교를 준비하는 동역자와 말씀을 사랑하는 모든 분께 이 서재를 열어 둡니다.</p>
      <!--YH-FIND-->
      <div class="cta"><a class="btn gold" href="yehwa/index.html">주제별 예화 →</a><a class="btn ghost" href="#sermon">설교 읽기</a><a class="btn ghost" href="{YT_URL}" target="_blank" rel="noopener">▶ 어음성경</a></div>
      <p class="motto">독서는 취미가 아닙니다. 특기를 넘어 주특기가 됩니다.</p>
    </div>
    <!--YH-TODAY-->
    <ul class="stats">{stats}</ul>
  </div>
</header>
<main class="container">
  <!--YH-FRESH-->
  <section id="sermon" aria-labelledby="sermon-h">
    <div class="head"><span class="eyebrow">성경연구와 설교</span><div class="row"><h2 id="sermon-h">강단에서 전한 말씀</h2><a href="{caturl(101)}" target="_blank" rel="noopener">설교 전체 {cnt(101):,}편 →</a></div>
    <p class="lede">주일낮예배와 금요기도회에서 전한 설교입니다. 아래 책장에서 성경 권별로 찾아 읽을 수 있습니다.</p></div>
    <a class="theory" href="{esc(url(theory))}" target="_blank" rel="noopener"><span class="ref">나의 설교론</span><strong>{esc(html.unescape(theory["title"]))}</strong><span class="q">{esc(clip(body(theory), 70))}</span></a>
    <ul class="cards">{sermons}</ul>
    <div class="shelf"><h3>구약 39권 · 성경 책장</h3><div class="books-scroll"><ul class="books">{spines(bible[:split])}</ul></div></div>
    <div class="shelf"><h3>신약 27권</h3><div class="books-scroll"><ul class="books">{spines(bible[split:])}</ul></div></div>
    <p class="lede">66권 가운데 {covered}권을 설교했습니다. 책등이 높을수록 글이 많고, 책을 누르면 그 권의 설교 목록이 열립니다.</p>
  </section>

  <section id="youtube" class="yt" aria-labelledby="youtube-h">
    <div class="head"><span class="eyebrow">유튜브 · 어음성경</span><div class="row"><h2 id="youtube-h">들으면서 읽는 성경</h2><a href="{YT_URL}" target="_blank" rel="noopener">채널 바로가기 · {yt_count} →</a></div>
    <p class="lede">창세기부터 요한계시록까지 성경 66권 전 장을 음악으로 만드는 통독 프로젝트입니다. 자막의 말씀을 따라 읽거나, 큐티와 기도 시간에 틀어 두고 들을 수 있습니다.</p></div>
    <ul class="vids">{videos}</ul>
    <a class="btn gold" href="{YT_URL}?sub_confirmation=1" target="_blank" rel="noopener">구독하고 새 영상 받기</a>
  </section>

  <section id="poems" aria-labelledby="poems-h">
    <div class="head"><span class="eyebrow">시</span><div class="row"><h2 id="poems-h">시와 찬양시</h2><a href="anshik/index.html">안식월 시집 {AN}편 →</a></div></div>
    <!--ANSHIK-->
    <div class="cols">{poems}</div>
  </section>

  <section id="pensees" aria-labelledby="pensees-h">
    <div class="head"><span class="eyebrow">나의 팡세</span><div class="row"><h2 id="pensees-h">생각의 노트</h2><a href="{caturl(36)}" target="_blank" rel="noopener">팡세 전체 {cnt(36)}편 →</a></div>
    <p class="lede">목회와 신앙, 삶에 대해 떠오른 생각을 번호를 매겨 적어 온 노트입니다.</p></div>
    <!--ANSHIK-M-->
    <ol class="notebook">{pensees}</ol>
  </section>

  <section id="reading" aria-labelledby="reading-h">
    <div class="head"><span class="eyebrow">독서 마당</span><div class="row"><h2 id="reading-h">읽은 책, 남긴 생각</h2><a href="{caturl(38)}" target="_blank" rel="noopener">독후감 전체 {cnt(38)}편 →</a></div></div>
    <div class="cols">{reads}</div>
  </section>

  <section id="stories" aria-labelledby="stories-h">
    <div class="head"><span class="eyebrow">은혜되는 예화</span><div class="row"><h2 id="stories-h">설교에 쓰는 이야기</h2><a href="https://saechang888.blogspot.com/2026/10/blog-post_16.html" target="_blank" rel="noopener">블로그 예화 목차 →</a></div></div>
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
</main>
<footer><div class="container"><span><b>독서주특기</b> · 이재선 목사 · 대한예수교장로회 새암교회</span><a href="{BLOG}" target="_blank" rel="noopener">blog.naver.com/saechang888 →</a></div></footer>'''
if not PREVIEW:
    page = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="이재선 목사의 서재 — 주제별 설교 예화, 설교와 성경연구, 독후감, 시와 팡세, 유튜브 어음성경">\n'
            + page.replace('</style>', '</style>\n</head>\n<body>', 1) + '\n</body>\n</html>\n')
open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(page)
print('ok total', TOTAL, 'bible books covered', covered, 'of', len(bible))
