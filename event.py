# 행복나눔축제 홍보: event.html(행사 안내 + D-day) 생성, 첫 화면에 행사 배너 삽입 (행사일이 지나면 배너 자동 제거)
import os, re, datetime
D = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.fromisoformat(os.environ.get('TODAY') or (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d'))
EVENT = datetime.date(2026, 12, 6)
left = (EVENT - TODAY).days
SITE = 'https://saechang888-code.github.io/'
MAP = 'https://map.naver.com/p/search/%EC%9A%A9%EC%9D%B8%EC%8B%9C%20%EC%88%98%EC%A7%80%EA%B5%AC%20%EA%B3%A0%EA%B8%B0%EB%A1%9C%20165'
dday = 'D-DAY' if left == 0 else (f'D-{left}' if left > 0 else '')

page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>행복나눔축제 · 12월 6일 새암교회</title>
<meta name="description" content="2026년 12월 6일(주일) 오전 11시 새암교회 본당. 개그우먼 이성미 집사 간증. 누구나 무료.">
<meta property="og:title" content="행복나눔축제 — 12월 6일(주일) 오전 11시 · 새암교회 본당">
<meta property="og:description" content="개그우먼 이성미 집사의 웃음과 희망 이야기. 이웃 누구나 무료로 초대합니다.">
<meta property="og:image" content="{SITE}assets/event_1x1.jpg">
<meta property="og:url" content="{SITE}event.html">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@800&family=IBM+Plex+Sans+KR:wght@400;600&display=swap">
<style>
:root{{--paper:#f6f5f0;--sheet:#fffefa;--ink:#1f2a2e;--muted:#62706f;--rule:#dcd8cc;--green:#1e5c3a;--gold:#b8862b;--pink:#d6336c}}
@media (prefers-color-scheme:dark){{:root{{--paper:#141819;--sheet:#1b2122;--ink:#e8e6df;--muted:#9eaaa7;--rule:#2f3738;--green:#8cc4ad;--gold:#e2b860;--pink:#ff8fb3;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:"IBM Plex Sans KR","Malgun Gothic",sans-serif;line-height:1.7;padding-inline:16px}}
.wrap{{max-width:980px;margin:0 auto;padding-block:28px 64px;display:grid;gap:28px}}
.top{{display:flex;justify-content:space-between;font-size:.92rem}} .top a{{color:var(--green);text-decoration:none}}
.grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px;align-items:start}}
@media (max-width:760px){{.grid{{grid-template-columns:1fr}}}}
img{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}
.dday{{display:inline-block;background:var(--pink);color:#fff;font-weight:600;padding:4px 14px;border-radius:99px;font-variant-numeric:tabular-nums}}
h1{{font-family:"Nanum Myeongjo",serif;font-size:clamp(2rem,6vw,3rem);margin:8px 0 0;line-height:1.2}}
dl{{display:grid;grid-template-columns:auto 1fr;gap:8px 18px;margin:0;font-size:1.05rem}}
dt{{color:var(--muted)}} dd{{margin:0;font-weight:600}}
.lead{{font-size:1.05rem;margin:0}}
.btns{{display:flex;flex-wrap:wrap;gap:10px}}
.btns a,.btns button{{font:inherit;font-weight:600;padding:11px 18px;border-radius:4px;border:1px solid var(--green);color:var(--green);background:var(--sheet);text-decoration:none;cursor:pointer}}
.btns .main{{background:var(--green);color:var(--paper)}}
.note{{color:var(--muted);font-size:.88rem}}
</style>
</head>
<body>
<div class="wrap">
<div class="top"><a href="index.html">← 독서주특기 홈</a><span>대한예수교장로회(합동) 새암교회</span></div>
<div class="grid">
  <img src="assets/event_4x5.jpg" alt="행복나눔축제 포스터: 12월 6일 주일 오전 11시 새암교회 본당, 특별강사 개그우먼 이성미 집사" width="900" height="1125">
  <div style="display:grid;gap:22px">
    <div>{f'<span class="dday">{dday}</span>' if dday else ''}<h1>행복나눔축제</h1></div>
    <p class="lead">웃음으로 많은 사람에게 희망을 전해 온 개그우먼 <b>이성미 집사</b>가 전하는 하나님의 은혜와 행복한 인생 이야기. 이웃 여러분 누구나 무료로 오세요.</p>
    <dl>
      <dt>일시</dt><dd>2026년 12월 6일(주일) 오전 11시</dd>
      <dt>장소</dt><dd>새암교회 본당<br><span style="font-weight:400">경기도 용인시 수지구 고기로 165 (수지성모요양원 앞)</span></dd>
      <dt>문의</dt><dd>031-262-3440</dd>
      <dt>참가비</dt><dd>없음 · 누구나 환영</dd>
    </dl>
    <div class="btns">
      <a class="main" href="{MAP}" target="_blank" rel="noopener">네이버 지도로 길찾기</a>
      <button type="button" id="share">이 초대장 공유하기</button>
    </div>
    <p class="note" id="msg" aria-live="polite"></p>
  </div>
</div>
</div>
<script>
document.getElementById('share').addEventListener('click', async () => {{
  const data = {{ title: '행복나눔축제 · 12월 6일 새암교회', text: '개그우먼 이성미 집사 간증 · 12/6(주일) 오전 11시 · 누구나 무료', url: location.href }};
  const msg = document.getElementById('msg');
  try {{
    if (navigator.share) {{ await navigator.share(data); }}
    else {{ await navigator.clipboard.writeText(data.url); msg.textContent = '주소를 복사했습니다. 카카오톡에 붙여넣어 보내세요.'; }}
  }} catch (e) {{ msg.textContent = '공유를 취소했습니다.'; }}
}});
</script>
</body>
</html>
'''
open(os.path.join(D, 'event.html'), 'w', encoding='utf-8').write(page)

# 첫 화면 배너 (행사일까지만)
home = os.path.join(D, 'index.html')
h = open(home, encoding='utf-8').read()
h = re.sub(r'<aside class="evbanner".*?</aside>\s*', '', h, flags=re.S)
if left >= 0:
    css = ('.evbanner{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;background:var(--green);color:var(--paper);padding:14px 20px;border-radius:4px;text-decoration:none}'
           '.evbanner b{font-family:var(--display);font-size:1.15rem}.evbanner .dd{background:#d6336c;color:#fff;border-radius:99px;padding:2px 12px;font-weight:600;font-variant-numeric:tabular-nums}'
           '.evbanner a{color:var(--paper);font-weight:600;margin-left:auto}')
    if '.evbanner{' not in h: h = h.replace('</style>', css + '\n</style>', 1)
    banner = (f'<aside class="evbanner" aria-label="행사 안내"><span class="dd">{dday}</span><b>행복나눔축제</b>'
              f'<span>12월 6일(주일) 오전 11시 · 새암교회 본당 · 개그우먼 이성미 집사 간증 · 누구나 무료</span>'
              f'<a href="event.html">초대장 보기 →</a></aside>\n  ')
    h = h.replace('<header class="hero" id="about">', banner + '<header class="hero" id="about">', 1)
open(home, 'w', encoding='utf-8').write(h)
print('event page ok, today', TODAY, dday or '(행사 종료)')
