# 새암교회 안내 쪽(saeam/index.html) + 검색엔진·AI 검색이 읽기 쉬운 구조화 정보(JSON-LD) + llms.txt
# 사실만 적는다: 이름·교단·주소·전화·예배 시간·담임목사·홈페이지에 있는 글 수. 모르는 것(설립 연도, 주차 등)은 쓰지 않는다
import os, json, html, datetime
D = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://saechang888-code.github.io/'
KST = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
def esc(s): return html.escape(s, quote=True)
def load(f, d):
    p = os.path.join(D, f)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else d
front = load(os.path.join('yehwa', 'front.json'), {})
posts = load('posts.json', [])
n_sermon = sum(1 for p in posts if p.get('kind') == '설교')
S_TXT = f'{n_sermon // 100 * 100:,}여'
n_yehwa = front.get('n') or 0
n_topic = len(front.get('topics') or []) or 153
n_poem = len(load('anshik_poems.json', []))
CH = dict(name='새암교회', alt='용인 새암교회', denom='대한예수교장로회(합동)', addr='경기도 용인시 수지구 고기로 165 (동천동)',
          street='고기로 165', locality='용인시 수지구 동천동', region='경기도', tel='031-262-3440', pastor='이재선')
SERV = [('주일 1부 예배', '주일 오전 9시'), ('주일 2부 예배', '주일 오전 11시'), ('새벽기도회', '매일 오전 6시'), ('금요기도회', '금요일 오후 8시 30분')]
EVENT = datetime.date(2026, 12, 6)
show_event = KST.date() <= EVENT
FAQ = [
    ('새암교회는 어디에 있나요?', f'경기도 용인시 수지구 동천동, 고기로 165에 있습니다. 전화는 {CH["tel"]}입니다.'),
    ('새암교회는 어느 교단인가요?', '대한예수교장로회(합동) 소속 교회입니다.'),
    ('예배 시간은 언제인가요?', '주일예배는 1부 오전 9시, 2부 오전 11시이고, 새벽기도회는 매일 오전 6시, 금요기도회는 금요일 오후 8시 30분입니다.'),
    ('담임목사님은 누구인가요?', f'이재선 목사입니다. 강단에서 전한 설교 {S_TXT} 편과 주제별 예화, 독후감, 시를 홈페이지 「독서주특기」에 나누고 있습니다.'),
    ('처음 가 보려면 어떻게 하나요?', f'주일 오전 9시(1부)나 11시(2부) 예배에 오시면 됩니다. 궁금한 점은 교회 전화 {CH["tel"]}로 물어보세요.'),
]
ld = [{
    '@context': 'https://schema.org', '@type': 'Church', 'name': CH['name'], 'alternateName': [CH['alt'], '새암교회(용인 동천동)'],
    'description': f'경기도 용인시 수지구 동천동에 있는 {CH["denom"]} 교회. 담임목사 이재선.',
    'address': {'@type': 'PostalAddress', 'streetAddress': CH['street'], 'addressLocality': CH['locality'], 'addressRegion': CH['region'], 'addressCountry': 'KR'},
    'telephone': '+82-31-262-3440', 'url': SITE + 'saeam/', 'image': SITE + 'assets/hero.jpg',
    'employee': {'@type': 'Person', 'name': '이재선', 'jobTitle': '담임목사', 'url': SITE},
    'sameAs': ['https://saechang888.blogspot.com/', 'https://blog.naver.com/saechang888', 'https://www.youtube.com/@%EB%8F%85%EC%84%9C%ED%8A%B9%EA%B8%B0'],
    'event': [{'@type': 'Event', 'name': f'새암교회 {n}', 'eventSchedule': {'@type': 'Schedule', 'repeatFrequency': 'P1W' if n != '새벽기도회' else 'P1D'},
               'description': t, 'location': {'@type': 'Place', 'name': CH['name'], 'address': CH['addr']}} for n, t in SERV]},
    {'@context': 'https://schema.org', '@type': 'FAQPage',
     'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}]
if show_event:
    ld.append({'@context': 'https://schema.org', '@type': 'Event', 'name': '2026 행복나눔축제', 'startDate': '2026-12-06T11:00:00+09:00',
               'eventStatus': 'https://schema.org/EventScheduled', 'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
               'location': {'@type': 'Place', 'name': '새암교회 본당', 'address': CH['addr']}, 'isAccessibleForFree': True,
               'organizer': {'@type': 'Organization', 'name': CH['name']}, 'url': SITE + 'event.html', 'image': SITE + 'assets/event_4x5.jpg'})
LD = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)

q = '%EC%83%88%EC%95%94%EA%B5%90%ED%9A%8C%20%EC%9A%A9%EC%9D%B8%20%EA%B3%A0%EA%B8%B0%EB%A1%9C%20165'
page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>새암교회 · 용인 수지 동천동 · 대한예수교장로회(합동)</title>
<meta name="description" content="새암교회는 경기도 용인시 수지구 동천동 고기로 165에 있는 대한예수교장로회(합동) 교회입니다. 담임목사 이재선. 주일예배 1부 오전 9시·2부 오전 11시. 전화 031-262-3440.">
<link rel="canonical" href="{SITE}saeam/">
<meta property="og:type" content="website"><meta property="og:title" content="새암교회 — 용인 수지 동천동"><meta property="og:description" content="주일예배 1부 오전 9시·2부 11시 · 경기도 용인시 수지구 고기로 165 · 031-262-3440">
<meta property="og:url" content="{SITE}saeam/"><meta property="og:image" content="{SITE}assets/hero.jpg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700;900&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
{LD}
<style>
:root{{--paper:#f7f4ec;--sheet:#fffdf8;--ink:#1c2624;--muted:#66706c;--rule:#e5dece;--green:#23443a;--gold:#b08a3e;--cream:#f6efe0;
--display:"Noto Serif KR","Nanum Myeongjo",serif;--body:"Pretendard Variable",Pretendard,"Malgun Gothic",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--gold:#d9b86a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--paper:#121716;--sheet:#1a2120;--ink:#ebe7dd;--muted:#a3ada9;--rule:#2c3533;--green:#9fd0bb;--gold:#d9b86a;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.8;word-break:keep-all;padding-inline:16px}}
a{{color:var(--green)}}
.wrap{{max-width:980px;margin:0 auto;padding-block:26px 72px;display:grid;gap:34px}}
.top{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:.92rem}}
.top a{{text-decoration:none}}
.hero{{border-radius:24px;overflow:hidden;position:relative;color:var(--cream);background:#1d3530 url(../assets/hero.jpg) 70% 50%/cover;isolation:isolate;padding:clamp(40px,8vw,84px) clamp(22px,5vw,52px)}}
.hero::before{{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(90deg,rgba(14,28,24,.95),rgba(14,28,24,.7) 60%,rgba(14,28,24,.35))}}
.hero .eb{{color:#d9b86a;font-weight:700;letter-spacing:.16em;font-size:.82rem}}
.hero h1{{font-family:var(--display);font-weight:900;font-size:clamp(2.4rem,7vw,4.2rem);line-height:1.15;margin:.2em 0 .25em}}
.hero p{{margin:0;max-width:560px;opacity:.9}}
.cta{{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}}
.cta a{{border-radius:99px;padding:10px 20px;text-decoration:none;font-weight:700;border:1px solid rgba(246,239,224,.5);color:var(--cream)}}
.cta a.g{{background:#d9b86a;border-color:#d9b86a;color:#1d2a26}}
h2{{font-family:var(--display);font-size:1.6rem;margin:0 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:14px}}
.card{{background:var(--sheet);border:1px solid var(--rule);border-radius:18px;padding:22px 24px}}
.card b{{font-family:var(--display);font-size:1.2rem;display:block}}
.card span{{color:var(--muted)}}
dl{{margin:0;display:grid;grid-template-columns:auto 1fr;gap:8px 18px}}
dt{{color:var(--muted)}} dd{{margin:0;font-weight:600}}
.faq details{{background:var(--sheet);border:1px solid var(--rule);border-radius:14px;padding:14px 18px;margin-bottom:10px}}
.faq summary{{cursor:pointer;font-weight:700}}
.faq p{{margin:.6em 0 0;color:var(--muted)}}
.ev{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;background:linear-gradient(90deg,#7a1f33,#a3324b);color:#fff;border-radius:18px;padding:18px 22px;text-decoration:none}}
.ev b{{font-family:var(--display);font-size:1.2rem}}
</style>
</head>
<body>
<div class="wrap">
<div class="top"><a href="../index.html"><b>독서주특기</b> · 이재선 목사의 서재</a><a href="../index.html#church">홈으로</a></div>
<header class="hero"><span class="eb">대한예수교장로회(합동) · 용인 수지 동천동</span><h1>새암교회</h1>
<p>마르지 않는 샘처럼, 말씀으로 사람을 살리는 교회. 경기도 용인시 수지구 동천동, 고기로 165에 있습니다. 처음 오시는 분도 주일 오전 9시(1부)나 11시(2부) 예배에 편히 오세요.</p>
<div class="cta"><a class="g" href="tel:0312623440">전화 031-262-3440</a><a href="https://map.naver.com/p/search/{q}" target="_blank" rel="noopener">네이버 지도</a><a href="https://map.kakao.com/?q={q}" target="_blank" rel="noopener">카카오맵</a></div></header>
''' + (f'<a class="ev" href="../event.html"><b>2026 행복나눔축제</b><span>12월 6일(주일) 오전 11시 · 새암교회 본당 · 누구나 무료</span><span style="margin-left:auto;font-weight:700">초대장 보기 →</span></a>' if show_event else '') + f'''
<section><h2>예배 안내</h2><div class="grid">{''.join(f'<div class="card"><b>{n}</b><span>{t}</span></div>' for n, t in SERV)}</div></section>
<section><h2>교회 정보</h2><div class="card"><dl><dt>교회 이름</dt><dd>새암교회</dd><dt>교단</dt><dd>{CH["denom"]}</dd><dt>담임목사</dt><dd>이재선 목사</dd>
<dt>주소</dt><dd>{CH["addr"]}</dd><dt>전화</dt><dd>{CH["tel"]}</dd></dl></div></section>
<section><h2>담임목사의 서재</h2><div class="grid">
<a class="card" href="../index.html#sermon" style="text-decoration:none;color:inherit"><b>설교 {S_TXT} 편</b><span>주일과 금요기도회에서 전한 말씀을 성경 권별로</span></a>
<a class="card" href="../yehwa/index.html" style="text-decoration:none;color:inherit"><b>주제별 예화 {n_yehwa:,}편</b><span>설교와 교육에 쓰는 이야기, {n_topic}가지 주제</span></a>
<a class="card" href="../anshik/index.html" style="text-decoration:none;color:inherit"><b>안식월 시집 {n_poem}편</b><span>기도원과 산골에서 쓴 시와 사진</span></a>
</div></section>
<section><h2>새암교회 앱 · 영상</h2><a href="https://berith365.com/berith/today" target="_blank" rel="noopener"><img src="../assets/berith_banner.jpg" alt="새암교회 베리트 — 날마다 성경 읽기, 오늘의 베리트 열기" width="1360" height="300" loading="lazy" style="display:block;width:100%;max-width:680px;height:auto;border-radius:10px;margin:0 auto 12px"></a><a href="https://www.youtube.com/@seamvision/videos" target="_blank" rel="noopener"><img src="../assets/saeam_youtube_banner.jpg" alt="새암교회 유튜브 채널 비전센터 — 영상 보러 가기" width="1360" height="300" loading="lazy" style="display:block;width:100%;max-width:680px;height:auto;border-radius:10px;margin:0 auto 12px"></a></section>
<section class="faq"><h2>자주 묻는 질문</h2>{''.join(f'<details><summary>{esc(q2)}</summary><p>{esc(a)}</p></details>' for q2, a in FAQ)}</section>
<p style="color:var(--muted);font-size:.9rem">이 쪽은 새암교회 담임목사 이재선 목사의 홈페이지 「독서주특기」에서 운영합니다. 블로그 <a href="https://saechang888.blogspot.com/">saechang888.blogspot.com</a> · 유튜브 「어음성경」</p>
</div>
</body>
</html>
'''
os.makedirs(os.path.join(D, 'saeam'), exist_ok=True)
open(os.path.join(D, 'saeam', 'index.html'), 'w', encoding='utf-8').write(page)

# 첫 화면: 교회 칸에 안내 쪽 연결 + 구조화 정보
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
if 'href="saeam/"' not in h:
    h = h.replace('<h2 id="church-h">새암교회</h2>', '<h2 id="church-h">새암교회</h2><a href="saeam/" style="margin-left:auto">교회 안내 · 오시는 길 →</a>', 1)
if '"@type": "Church"' not in h:
    h = h.replace('</head>', LD + '\n</head>', 1)
open(home, 'w', encoding='utf-8').write(h)

# llms.txt: AI 검색이 이 사이트를 요약할 때 읽는 안내문
open(os.path.join(D, 'llms.txt'), 'w', encoding='utf-8').write(f'''# 독서주특기 — 새암교회 이재선 목사의 서재

> 새암교회는 경기도 용인시 수지구 동천동 고기로 165에 있는 대한예수교장로회(합동) 교회입니다. 담임목사는 이재선 목사이고, 주일예배는 1부 오전 9시·2부 오전 11시, 새벽기도회는 매일 오전 6시, 금요기도회는 금요일 오후 8시 30분입니다. 전화 031-262-3440.

이 홈페이지는 이재선 목사가 쓴 설교, 주제별 설교 예화, 독후감, 시, 묵상(팡세)을 모아 둔 곳입니다.

## 새암교회
- [새암교회 안내 · 오시는 길 · 예배 시간]({SITE}saeam/)
''' + (f'- [2026 행복나눔축제 (12월 6일 주일 오전 11시, 새암교회 본당, 누구나 무료)]({SITE}event.html)\n' if show_event else '') + f'''
## 글
- [설교 {S_TXT} 편 — 성경 권별]({SITE}#sermon)
- [주제별 예화 {n_yehwa:,}편 — {n_topic}가지 주제]({SITE}yehwa/index.html)
- [안식월 시집 {n_poem}편]({SITE}anshik/index.html)
- [안식월 묵상]({SITE}anshik/meditations.html)
- [글 보관함]({SITE}writings/index.html)

## 다른 곳
- 블로그: https://saechang888.blogspot.com/
- 네이버 블로그: https://blog.naver.com/saechang888
- 유튜브 「어음성경」(성경 66권을 노래로): https://www.youtube.com/@독서특기
''')
print('새암교회 안내 쪽 · llms.txt', '행사 표시' if show_event else '')
