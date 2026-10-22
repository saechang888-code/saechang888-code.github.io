# 예약일(한국 시간)이 된 글을 구글 블로거에 올린다. 올린 글은 blogger_done.json에 남겨 두 번 올리지 않는다.
#  - posts.json: 설교·독후감·팡세·교회 소식 (예화 '묶음' 글은 블로거에는 올리지 않는다)
#  - blogger_yehwa.json: 예화를 한 편씩, 하루 3편
# 열쇠(BLOGGER_CLIENT_ID / BLOGGER_CLIENT_SECRET / BLOGGER_REFRESH_TOKEN)가 없으면 아무것도 하지 않는다.
# REFRESH_ONLY=1 이면 이미 올린 글의 본문만 지금 디자인으로 다시 입힌다.
import os, re, json, html, datetime, urllib.request, urllib.parse, urllib.error, time, sys

D = os.path.dirname(os.path.abspath(__file__))
BLOG = '5791371153360346841'
SITE = 'https://saechang888-code.github.io/'
MAX_PER_RUN = int(os.environ.get('BLOGGER_MAX', '30'))       # 밀린 글이 많아도 하루에 이만큼만 (스팸 판정 방지)
TODAY = os.environ.get('TODAY') or (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
KIND_LABEL = {'행사': '교회 소식', '설교': '설교', '예화': '예화', '독후감': '독후감', '팡세/예화': '팡세', '시': '시'}
# 블로그 카테고리(= 첫 번째 라벨). 글 맨 위 메뉴도 이 순서로 보인다
CATS = ['예화', '설교', '묵상', '팡세', '독후감', '시', '기타']
CAT_OF = {'예화': '예화', '설교': '설교', '독후감': '독후감', '팡세/예화': '팡세', '묵상': '묵상', '시': '시', '행사': '기타'}
BLOG_URL = 'https://saechang888.blogspot.com/'
YEHWA_INDEX = BLOG_URL + '2026/10/blog-post_16.html'   # [예화] 주제별 예화 목차 — 가 편 ~ 하 편

cid, secret, refresh = (os.environ.get(k) for k in ('BLOGGER_CLIENT_ID', 'BLOGGER_CLIENT_SECRET', 'BLOGGER_REFRESH_TOKEN'))
if not (cid and secret and refresh):
    print('blogger: 열쇠가 없어 건너뜀'); sys.exit(0)

def call(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

token = call('https://oauth2.googleapis.com/token', urllib.parse.urlencode(dict(
    client_id=cid, client_secret=secret, refresh_token=refresh, grant_type='refresh_token')).encode())['access_token']
AUTH = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json; charset=utf-8'}

# ---------- 글 디자인 (테마와 상관없이 보이도록 인라인 스타일) ----------
INK, MUTED, GOLD, GREEN, SOFT = '#24302f', '#6b7775', '#a07b32', '#2f5d50', '#f7f3ea'
WRAP = f'font-family:Noto Serif KR,Nanum Myeongjo,Batang,serif;color:{INK};font-size:17px;line-height:1.95;word-break:keep-all;max-width:680px;margin:0 auto'
P = 'margin:0 0 1.1em'
BADGE = f'display:inline-block;font-family:Noto Sans KR,Malgun Gothic,sans-serif;font-size:13px;letter-spacing:.04em;color:{GOLD};border:1px solid {GOLD};border-radius:99px;padding:2px 12px;margin:0 6px 6px 0'
H3 = f'font-size:19px;color:{GREEN};margin:1.8em 0 .5em;padding-bottom:.3em;border-bottom:1px solid #e3ddd0'
NOTE = f'background:{SOFT};border-left:3px solid {GOLD};padding:12px 16px;margin:1.6em 0;font-size:15px;color:{MUTED};font-family:Noto Sans KR,Malgun Gothic,sans-serif;line-height:1.7'
FOOT = f'margin-top:2.2em;padding-top:1em;border-top:1px solid #e3ddd0;font-size:14px;color:{MUTED};font-family:Noto Sans KR,Malgun Gothic,sans-serif'

def esc(s): return html.escape(s, quote=False)
def link(s): return re.sub(r'(https://[^\s<]+)', rf'<a href="\1" style="color:{GREEN}">\1</a>', s)
def paras(text):
    out = []
    for para in re.split(r'\n\s*\n', text.strip()):
        para = para.strip('\n')
        if not para.strip(): continue
        if para.startswith('■'):
            out.append(f'<h3 style="{H3}">{esc(para.lstrip("■ ").strip())}</h3>')
        elif para.startswith(('— ', '※')):
            out.append(f'<p style="{P};font-size:15px;color:{MUTED}">{link(esc(para)).replace(chr(10), "<br>")}</p>')
        else:
            for line in para.split('\n'):           # 한 줄 한 문단: 모바일에서 읽기 편하게
                if line.strip(): out.append(f'<p style="{P}">{link(esc(line.strip()))}</p>')
    return out

def nav(cur):
    a = []
    for c in CATS:
        st = f'color:{GREEN};text-decoration:none;font-weight:700;border-bottom:2px solid {GOLD}' if c == cur else f'color:{MUTED};text-decoration:none'
        # '예화'는 글 목록 대신 주제별 목차(가 편 ~ 하 편)로 바로 간다
        href = YEHWA_INDEX if c == '예화' else f'{BLOG_URL}search/label/{urllib.parse.quote(c)}'
        a.append(f'<a href="{href}" style="{st}">{c}</a>')
    return (f'<p style="font-family:Noto Sans KR,Malgun Gothic,sans-serif;font-size:14px;margin:0 0 1.6em;padding:10px 0;border-top:1px solid #e3ddd0;border-bottom:1px solid #e3ddd0;text-align:center;word-spacing:.2em">'
            + ' &nbsp;·&nbsp; '.join(a) + '</p>')

def badges(words): return '<p style="margin:0 0 1.4em">' + ''.join(f'<span style="{BADGE}">{esc(w)}</span>' for w in words) + '</p>'
# 모든 글 맨 아래: 홈페이지 배너(누르면 홈페이지로)와 주소
BANNER = (f'<p style="margin:2em 0 0;text-align:center"><a href="{SITE}"><img src="{SITE}assets/blog_banner.jpg" '
          f'alt="독서주특기 홈페이지 바로가기" style="width:100%;max-width:680px;height:auto;border:0;border-radius:10px"></a></p>')
def footer(extra=''):
    return (BANNER + f'<div style="{FOOT}">✍ 독서주특기 · 이재선 목사 (대한예수교장로회 새암교회)<br>'
            f'🏠 홈페이지 주소: <a href="{SITE}" style="color:{GREEN}">{SITE}</a><br>'
            f'{extra}<a href="{SITE}" style="color:{GREEN}">홈페이지</a> · <a href="https://blog.naver.com/saechang888" style="color:{GREEN}">네이버 블로그</a> · '
            f'<a href="https://www.youtube.com/@독서특기" style="color:{GREEN}">유튜브 「어음성경」</a></div>')

def render_post(p):
    cat = CAT_OF.get(p['kind'], '기타')
    out = [nav(cat), badges(labels_post(p))]
    if p['kind'] == '행사':
        out.append(f'<p style="{P}"><a href="{SITE}event.html"><img src="{SITE}assets/event_4x5.jpg" alt="행복나눔축제 초대장" style="max-width:100%;height:auto;border-radius:6px"></a></p>')
    out += paras(p['body'])
    out.append(footer(f'<a href="{SITE}writings/{p["id"]}.html" style="color:{GREEN}">홈페이지에서 이 글 보기</a> · '))
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'

def render_yehwa(y):
    out = [nav('예화'), badges([y['topic'], y['topic'] + ' › ' + y['sub']])]
    out += paras(y['body'])
    if y['sermon']:
        out.append(f'<div style="{NOTE}">📖 이 예화를 인용한 설교<br><b style="color:{INK}">{esc(y["sermon"])}</b></div>')
    out.append(f'<p style="{P};font-size:14px;color:{MUTED}">※ 설교 중에 인용한 예화, 독후감에서 뽑은 이야기, 고전과 역사 기록을 바탕으로 새로 쓴 이야기입니다. 출처가 분명한 예화는 원 출처를 밝혀 사용해 주세요.</p>')
    out.append(footer())
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'

# ---------- 예화 모음: 낱말 주제(감사·겸손·기도…)마다 한 글, 가 편·나 편… 초성별로 묶는다 ----------
CHUNK = 30
NUMS = '①②③④⑤⑥⑦⑧⑨⑩'
CHO = '가가나다다라마바바사사아자자차카타파하'          # 초성 19개 → 편 이름 (ㄲ은 가 편, ㄸ은 다 편 …)
def pyeon(word): return CHO[(ord(word[0]) - 0xAC00) // 588] + ' 편'
def label_url(l): return f'{BLOG_URL}search/label/{urllib.parse.quote(l)}'
def yehwa_groups(yehwa):
    by = {}
    for y in yehwa: by.setdefault(y['kw'], []).append(y)
    out = []
    for kw in sorted(by):
        items = by[kw]
        parts = [items[i:i + CHUNK] for i in range(0, len(items), CHUNK)]
        for k, part in enumerate(parts):
            no = f' {NUMS[k]}' if len(parts) > 1 else ''
            out.append(dict(id=f'yk-{kw}-{k + 1}', kw=kw, pyeon=pyeon(kw), total=len(items), items=part, title=f'【{kw}】 예화 모음{no} — {len(part)}편'))
    return out
def render_group(g):
    out = [nav('예화'), badges([g['pyeon'], g['kw'] + ' 예화'])]
    out.append(f'<div style="{NOTE}">「{esc(g["kw"])}」을 주제로 한 예화 {len(g["items"])}편입니다. 제목을 누르면 바로 내려갑니다.<br>'
               + '<br>'.join(f'<a href="#y{i + 1}" style="color:{GREEN}">{i + 1}. {esc(y["title"])}</a>' for i, y in enumerate(g['items'])) + '</div>')
    for i, y in enumerate(g['items']):
        out.append(f'<h3 id="y{i + 1}" style="{H3}">{i + 1}. {esc(y["title"])}</h3>')
        out += paras(y['body'])
        if y['sermon']: out.append(f'<p style="{P};font-size:14px;color:{MUTED}">📖 인용한 설교: {esc(y["sermon"])}</p>')
        if y.get('book'): out.append(f'<p style="{P};font-size:14px;color:{MUTED}">📚 독후감 「{esc(y["book"])}」에서</p>')
        if y.get('origin'): out.append(f'<p style="{P};font-size:14px;color:{MUTED}">📜 출처: {esc(y["origin"])}' + (' (저작권이 끝난 고전을 새로 옮겨 씀)' if y.get('src') == 'classic' else ' (역사 기록을 바탕으로 새로 씀)') + '</p>')
    out.append(f'<p style="{P};font-size:14px;color:{MUTED}">※ 설교 중에 인용한 예화, 독후감에서 뽑은 이야기, 고전과 역사 기록을 바탕으로 새로 쓴 이야기입니다. 출처가 분명한 예화는 원 출처를 밝혀 사용해 주세요.</p>')
    out.append(f'<p style="{P};font-size:15px"><a href="{label_url("예화 주제 목차")}" style="color:{GREEN}">← 주제별 예화 목차(가 편 ~ 하 편) 보기</a> · '
               f'<a href="{label_url(g["pyeon"])}" style="color:{GREEN}">{esc(g["pyeon"])} 주제 모두 보기</a></p>')
    out.append(footer())
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'
def render_index(groups):
    n = sum(len(g['items']) for g in groups); kws = {}
    for g in groups: kws[g['kw']] = g['total']
    out = [nav('예화'), f'<p style="{P}">설교 중에 인용한 예화 {n:,}편을 {len(kws)}가지 주제로 모았습니다. 주제는 가나다순, 가 편부터 하 편까지입니다. 주제를 누르면 그 주제의 예화 모음이 열립니다.</p>']
    by = {}
    for kw in sorted(kws): by.setdefault(pyeon(kw), []).append(kw)
    for p in sorted(by):
        out.append(f'<h3 style="{H3}"><a href="{label_url(p)}" style="color:{GREEN};text-decoration:none">{esc(p)}</a> <span style="font-size:14px;color:{MUTED}">{len(by[p])}가지 주제</span></h3>')
        out.append(f'<p style="{P};line-height:2.2">' + ' &nbsp;'.join(f'<a href="{label_url(kw + " 예화")}" style="color:{INK};text-decoration:none;white-space:nowrap">【{esc(kw)}】<span style="font-size:13px;color:{MUTED}">{kws[kw]}편</span></a>' for kw in by[p]) + '</p>')
    out.append(footer())
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'

# ---------- 새로 쓴 예화(둘로스·sermon-jesus·설교·독후감에서 줄거리를 새로 쓴 것): 들어온 차례대로 10편씩 한 글 ----------
YN_SIZE = 10
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
    if '게재)' in c: return c   # 신문·잡지에 실린 글을 소재로 쓴 예화 (출처: 「원제」 (매체 게재))
    if '아름다운 글)' in c: return c   # 네이버·구글에 올라온 좋은 글을 소재로 쓴 예화 (출처: 온라인에 공유된 아름다운 글)
    if '목회 프리미엄' in c: return re.sub(r'\s*\(목회 프리미엄.*\)$', '', c) + ' (온라인에 공유된 감동적인 글)'
    if '설교 「' in c: return '온라인에 공유된 감동적인 예화'   # 둘로스 설교 원고 속에서 뽑은 예화
    p = press(c)
    if p: t = re.search(r'「[^」]*」', c); return (t.group(0) + ' ' if t else '') + f'({p} 게재)'
    # 둘로스 자료에서 고른 글은 원글 제목만 두고 출처는 '온라인에 공개된 감동적인 예화'로 적는다
    t = re.search(r'「[^」]*」', c)
    return (t.group(0) + ' ' if t else '') + '(온라인에 공개된 감동적인 예화)'
def src_note(y):
    if y.get('credit'): return f'📜 원글: {esc(credit_txt(y["credit"]))} — 줄거리를 바탕으로 새로 써서 옮김'
    if y.get('book'): return f'📚 독후감 「{esc(y["book"])}」에서'
    if y.get('origin'): return f'📜 출처: {esc(y["origin"])} (기록을 바탕으로 새로 씀)'
    return ''
def render_new(k, items):
    out = [nav('예화'), badges(['새로 쓴 예화', f'제{k}집'] + sorted({y['kw'] for y in items})[:6])]
    out.append(f'<div style="{NOTE}">설교에 바로 쓸 수 있도록 줄거리를 새로 쓰고 적용과 말씀(개역개정)을 붙인 예화 {len(items)}편입니다. 제목을 누르면 바로 내려갑니다.<br>'
               + '<br>'.join(f'<a href="#y{i + 1}" style="color:{GREEN}">{i + 1}. 【{esc(y["kw"])}】 {esc(y["title"])}</a>' for i, y in enumerate(items)) + '</div>')
    for i, y in enumerate(items):
        out.append(f'<h3 id="y{i + 1}" style="{H3}">{i + 1}. 【{esc(y["kw"])}】 {esc(y["title"])}</h3>')
        out += paras(y['body'])
        if src_note(y): out.append(f'<p style="{P};font-size:14px;color:{MUTED}">{src_note(y)}</p>')
    out.append(f'<p style="{P};font-size:15px"><a href="{SITE}yehwa/index.html" style="color:{GREEN}">홈페이지에서 주제별 예화 모두 보기 →</a> · '
               f'<a href="{label_url("새로 쓴 예화")}" style="color:{GREEN}">새로 쓴 예화 모음 전체</a></p>')
    out.append(footer())
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'

def labels_post(p):
    # 라벨은 카테고리 하나 + 세부 주제 하나만 (라벨 목록이 깔끔하게)
    ls = [CAT_OF.get(p['kind'], '기타')]
    leaf = p['category'].split('>')[-1].strip()
    if p['kind'] == '설교':                     # 설교는 성경 권별 (예: '시편 설교')
        leaf = (leaf + ' 설교') if '>' in p['category'] else '주제 설교'
    if p['kind'] == '팡세/예화': leaf = ''
    if leaf and leaf not in ls and leaf != '성경별 예화': ls.append(leaf)
    return [l.replace(',', ' ') for l in ls]

def labels_yehwa(y): return ['예화', y['topic'], y['topic'] + ' › ' + y['sub']]

# ---------- 시 (네이버 블로그 '시' 카테고리에서 가져온 poems.json) ----------
POEM_BASE = {'자연시': '자연시', '생활시': '생활시', '기탄잘리(찬양시)': '찬양시', '자아성찰시': '묵상시'}
def load_poems():
    path = os.path.join(D, 'poems.json')
    if not os.path.exists(path): return []
    fix = {}
    for c, ids in json.load(open(os.path.join(D, 'poem_cats.json'), encoding='utf-8-sig')).items():
        if not c.startswith('_'): fix.update({i: c for i in ids})
    seen, out = set(), []
    for p in sorted(json.load(open(path, encoding='utf-8')), key=lambda p: (p['date'], p['logNo'])):
        body = p.get('body', '').strip()
        k = re.sub(r'\W', '', body)[:80]
        if len(body) < 30 or k in seen: continue          # 빈 글·같은 시 두 번 올린 것은 한 번만
        seen.add(k)
        lines = body.split('\n')
        title = lines[0].strip() if len(lines[0].strip()) <= 30 else p['title']
        rest = '\n'.join(lines[1:]).strip() if lines[0].strip() == title else body
        out.append(dict(id=f'p{p["logNo"]}', sub=fix.get(p['logNo'], POEM_BASE.get(p['cat'], '묵상시')), title=title, body=rest,
                        src=f'https://blog.naver.com/saechang888/{p["logNo"]}'))
    return out

def render_poem(p):
    lines = []
    for l in p['body'].split('\n'):
        if l.startswith('*'):
            lines.append(f'<p style="{P};font-size:14px;color:{MUTED};margin-top:2em">{esc(l.lstrip("* "))}</p>')
        else:
            lines.append(f'<p style="margin:0;min-height:1em">{esc(l)}</p>')
    return (f'<div style="{WRAP}">' + nav('시') + badges(['시', p['sub']]) +
            f'<h2 style="font-size:24px;text-align:center;margin:.6em 0 1.4em;color:{INK}">{esc(p["title"])}</h2>' +
            f'<div style="text-align:center;line-height:2.1">' + '\n'.join(lines) + '</div>' + footer() + '</div>')

# ---------- 할 일 목록 ----------
all_posts = json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8'))
posts = [p for p in all_posts if p['kind'] != '예화']
yehwa = json.load(open(os.path.join(D, 'blogger_yehwa.json'), encoding='utf-8'))
# 블로거는 홈페이지와 따로, 분야(카테고리)마다 하루 PER_CAT편씩 BSTART부터 차례로 올린다. 교회 소식은 정해진 날짜 그대로.
BSTART, PER_CAT = datetime.date(2026, 10, 11), 6
queues = {}
for p in sorted(posts, key=lambda p: (p['date'], p['id'])):
    if p['kind'] != '행사': queues.setdefault(CAT_OF.get(p['kind'], '기타'), []).append(p)
bdate = {p['id']: p['date'] for p in posts if p['kind'] == '행사'}
old_poems = load_poems()
for cat, q in queues.items():
    off = len(old_poems) if cat == '시' else 0          # 컴퓨터에서 찾은 시는 네이버에서 옮긴 시 다음 차례로
    for i, p in enumerate(q, off): bdate[p['id']] = (BSTART + datetime.timedelta(days=i // PER_CAT)).isoformat()
def render_any(p):
    if p['kind'] == '시': return render_poem(dict(sub=p['category'].split('>')[-1].strip(), title=p['title'], body=p['body']))
    return render_post(p)
jobs = [dict(id=p['id'], date=bdate[p['id']], title=p['title'], render=lambda p=p: render_any(p), labels=labels_post(p)) for p in posts]
# 예화는 낱개 대신 주제별 모음 글로 모두 올린다 (목차 1편 + 소주제별 모음). 하루 YG_PER편씩 YG_START부터
YG_START, YG_PER = datetime.date(2026, 10, 17), 8
groups = yehwa_groups(yehwa)
jobs.append(dict(id='yg-index', date=YG_START.isoformat(), title='[예화] 주제별 예화 목차 — 가 편 ~ 하 편', render=lambda: render_index(groups), labels=['예화', '예화 주제 목차']))
for i, g in enumerate(groups):
    jobs.append(dict(id=g['id'], date=(YG_START + datetime.timedelta(days=(i + 1) // YG_PER)).isoformat(), title=g['title'], render=lambda g=g: render_group(g), labels=['예화', g['pyeon'], g['kw'] + ' 예화']))
# 새로 쓴 예화: 10편이 다 찬 묶음만 올린다(묶음 내용이 바뀌지 않게). 하루 YN_PER편까지
YN_START, YN_PER = datetime.date(2026, 10, 19), 12
newy = []
for f in ('doulos_yehwa.json', 'yehwa_ai.json'):
    fp = os.path.join(D, f)
    if os.path.exists(fp): newy += json.load(open(fp, encoding='utf-8'))
for k in range(len(newy) // YN_SIZE):
    part = newy[k * YN_SIZE:(k + 1) * YN_SIZE]
    jobs.append(dict(id=f'yn-{k + 1:04d}', date=YN_START.isoformat(), title=f'[새로 쓴 예화 {k + 1}] ' + ' · '.join(dict.fromkeys(y['kw'] for y in part)),
                     render=lambda k=k, part=part: render_new(k + 1, part), labels=['예화', '새로 쓴 예화']))
# 이미 올린 낱개 예화는 디자인 다시 입히기(REFRESH_ONLY)용으로만 남긴다
for y in yehwa:
    by_y = dict(id=y['id'], date='9999-12-31', title=f'[{y["topic"]} 예화] {y["title"]}', render=lambda y=y: render_yehwa(y), labels=labels_yehwa(y))
    jobs.append(by_y)
for i, p in enumerate(old_poems):
    jobs.append(dict(id=p['id'], date=(BSTART + datetime.timedelta(days=i // PER_CAT)).isoformat(), title=p['title'], render=lambda p=p: render_poem(p), labels=['시', p['sub']]))
# 안식월 시집(anshik_poems.json): 사진이 있으면 맨 위에. 하루 AN_PER편씩
AN_START, AN_PER = datetime.date(2026, 10, 20), 12
def render_anshik(p):
    lines = ''.join(f'<p style="margin:0;min-height:1em">{esc(l)}</p>' for l in p['body'].split('\n'))
    photo = (f'<p style="margin:0 0 1.4em"><img src="{SITE}{p["photo"]}" alt="「{esc(p["title"])}」을 쓴 곳에서 찍은 사진" style="width:100%;height:auto;border-radius:10px"></p>'
             if p['photo'] else '')
    note = f'<p style="{P};font-size:14px;color:{MUTED};margin-top:2em;text-align:left">✎ {esc(p["note"])}</p>' if p['note'] else ''
    return (f'<div style="{WRAP}">' + nav('시') + badges(['시', p['sub'], '안식월 시집']) + photo +
            f'<h2 style="font-size:24px;text-align:center;margin:.6em 0 1.4em;color:{INK}">{esc(p["title"])}</h2>' +
            f'<div style="text-align:center;line-height:2.1">{lines}</div>{note}' +
            footer(f'<a href="{SITE}anshik/{p["id"]}.html" style="color:{GREEN}">홈페이지 안식월 시집에서 보기</a> · ') + '</div>')
ap = os.path.join(D, 'anshik_poems.json')
# 이미 올린 시(posts.json에 있는 것, dup)는 다시 올리지 않는다
for i, p in enumerate([p for p in (json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else []) if not p.get('dup')]):
    jobs.append(dict(id='an-' + p['id'], date=(AN_START + datetime.timedelta(days=i // AN_PER)).isoformat(), title=p['title'],
                     render=lambda p=p: render_anshik(p), labels=['시', p['sub'], '안식월 시집']))
# 안식월 묵상(anshik_pensees.json) → 블로그 '팡세'. 하루 AN_PER편씩 시와 함께
def render_med(m):
    out = [nav('팡세'), badges(['팡세', '안식월 묵상']), f'<h2 style="font-size:24px;margin:.4em 0 1.2em;color:{INK}">{esc(m["title"])}</h2>']
    for para in m['body'].split('\n'):
        para = para.strip()
        if not para: continue
        out.append(f'<p style="{NOTE}">{esc(para[2:])}</p>' if para.startswith('▸ ') else f'<p style="{P}">{esc(para)}</p>')
    out.append(footer(f'<a href="{SITE}anshik/{m["id"]}.html" style="color:{GREEN}">홈페이지 안식월 묵상에서 보기</a> · '))
    return f'<div style="{WRAP}">' + '\n'.join(out) + '</div>'
mp = os.path.join(D, 'anshik_pensees.json')
for i, m in enumerate(json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else []):
    jobs.append(dict(id='an-' + m['id'], date=(AN_START + datetime.timedelta(days=i // 4)).isoformat(), title=f'[팡세] {m["title"]}',
                     render=lambda m=m: render_med(m), labels=['팡세', '안식월 묵상']))
# 새암교회 안내 글 한 편 (검색에서 교회를 찾는 분들을 위해)
def render_church():
    rows = [('교단', '대한예수교장로회(합동)'), ('담임목사', '이재선 목사'), ('주소', '경기도 용인시 수지구 고기로 165 (동천동)'), ('전화', '031-262-3440'),
            ('주일예배', '주일 오전 11시'), ('새벽기도회', '매일 오전 6시'), ('금요기도회', '금요일 오후 8시 30분')]
    tb = ''.join(f'<tr><td style="padding:8px 14px 8px 0;color:{MUTED};white-space:nowrap">{a}</td><td style="padding:8px 0;font-weight:700">{b}</td></tr>' for a, b in rows)
    return (f'<div style="{WRAP}">' + nav('기타') + badges(['새암교회', '교회 안내']) +
            f'<p style="{P}">새암교회는 경기도 용인시 수지구 동천동, 고기로 165에 있는 대한예수교장로회(합동) 교회입니다. 처음 오시는 분도 주일 오전 11시 예배에 편히 오세요.</p>'
            f'<table style="border-collapse:collapse;margin:0 0 1.4em;font-family:Noto Sans KR,Malgun Gothic,sans-serif;font-size:16px">{tb}</table>'
            f'<p style="{P}"><a href="{SITE}saeam/" style="color:{GREEN};font-weight:700">새암교회 안내 · 오시는 길 (지도) →</a></p>'
            f'<p style="{P}"><a href="{SITE}event.html" style="color:{GREEN}">2026 행복나눔축제 — 12월 6일(주일) 오전 11시, 새암교회 본당, 누구나 무료</a></p>' + footer() + '</div>')
jobs.append(dict(id='church-guide', date='2026-10-20', title='새암교회 안내 — 용인 수지 동천동 · 예배 시간 · 오시는 길', render=render_church, labels=['기타', '새암교회']))
# e북 「Exodus 엑서더스 — 새암교회 이야기」 소개 글 (본문은 홈페이지 saeam/exodus/, ebook_exodus.py로 만든다)
def render_exodus():
    L = [l.strip() for l in open(os.path.join(D, 'ebook_exodus.txt'), encoding='utf-8').read().split('\n')]
    toc = L.index(next(t for t in L if re.sub(r'\s', '', t) == '목차'))
    pro = [t for t in L[18:toc] if t and len(t) > 60][:4]       # 프롤로그 앞부분 몇 문단
    url = SITE + 'saeam/exodus/'
    return (f'<div style="{WRAP}">' + nav('기타') + badges(['e북', '새암교회', '전도', '간증']) +
            f'<p style="{P}"><b>『Exodus 엑서더스 — 새암교회 이야기』</b>(이재선 목사 지음)를 e북으로 엮었습니다. 40년 된 교회가 무기력한 신앙생활을 벗고 영혼 구원하는 교회로 다시 태어난 이야기와, 새 가족·제자·사명자로 자라 간 성도들의 간증을 담았습니다.</p>'
            f'<p style="{P}"><a href="{url}" style="color:{GREEN};font-weight:700">홈페이지에서 전체 읽기 →</a> · <a href="{url}exodus.epub" style="color:{GREEN};font-weight:700">전자책(EPUB) 내려받기</a></p>'
            f'<h3 style="font-size:20px;margin:1.6em 0 .6em;color:{INK}">프롤로그에서</h3>' + ''.join(f'<p style="{P}">{esc(t)}</p>' for t in pro) +
            f'<p style="{P}"><b>차례</b> — 출정식 · 제1장 엑서더스의 비법 · 제2장 애굽의 삶 · 제3장 광야의 삶 · 제1숙영지 새 가족들의 증언 · 제2숙영지 제자들의 증언 · 제3숙영지 사명자들의 증언 · 가나안에 도착하다</p>'
            f'<p style="{P}"><a href="{url}" style="color:{GREEN};font-weight:700">이어서 읽기 →</a></p>' + footer() + '</div>')
jobs.append(dict(id='ebook-exodus', date='2026-10-22', title='[e북] Exodus 엑서더스 — 새암교회 이야기 (이재선 목사)', render=render_exodus, labels=['기타', '새암교회', 'e북']))
by_id = {j['id']: j for j in jobs}
# 예전에 올린 예화 묶음 글도 디자인을 다시 입힐 수 있게
for p in all_posts:
    if p['kind'] == '예화': by_id.setdefault(p['id'], dict(id=p['id'], title=p['title'], render=lambda p=p: render_post(p), labels=labels_post(p)))

def add_more(s, n=4):
    # 첫 화면에는 앞부분만 보이게 '더 보기' 자리(<!--more-->)를 넣는다 (블로거는 첫 화면 크기에 한도가 있어 긴 글이면 몇 편만 보인다)
    if '<!--more-->' in s: return s
    i = -1
    for _ in range(n):
        i = s.find('</p>', i + 1)
        if i < 0: return s
    i += 4
    return s[:i] + '<!--more-->' + s[i:]

done_path = os.path.join(D, 'blogger_done.json')
done = json.load(open(done_path, encoding='utf-8')) if os.path.exists(done_path) else {}

if os.environ.get('REFRESH_ONLY'):
    # 이미 올린 글의 제목·본문을 지금 디자인으로 다시 입힌다
    posted = {}
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG}/posts?maxResults=500&fetchBodies=false&status=live&status=scheduled'
    tok = ''
    while True:  # 글이 500편을 넘어도 다 찾도록 쪽마다 넘겨 가며 읽는다
        r = call(url + (f'&pageToken={tok}' if tok else ''), headers=AUTH)
        for it in r.get('items', []): posted[it['url']] = it['id']
        tok = r.get('nextPageToken')
        if not tok: break
    n = 0
    for jid, u in done.items():
        j, pid = by_id.get(jid), posted.get(u)
        if not (j and pid): continue
        call(f'https://www.googleapis.com/blogger/v3/blogs/{BLOG}/posts/{pid}', json.dumps(dict(title=j['title'], content=add_more(j['render']()), labels=j['labels']), ensure_ascii=False).encode('utf-8'), AUTH, 'PATCH')
        n += 1; time.sleep(2)
    print('blogger: refreshed', n); sys.exit(0)

due = sorted((j for j in jobs if j['date'] <= TODAY and j['id'] not in done), key=lambda j: (j['id'] != 'ebook-exodus', j['date'], j['id']))   # e북 소개 글은 맨 먼저
n = fails = 0
# 예화 모음 글은 따로 하루 YG_PER편까지 (다른 글의 MAX_PER_RUN 몫을 빼앗지 않게)
reg = [j for j in due if not j['id'].startswith(('yg', 'yk', 'yn', 'an-'))][:MAX_PER_RUN]
due = (reg[:3] + [j for j in due if j['id'].startswith('yn')][:YN_PER]             # 일반 글 몇 편 → 새로 쓴 예화 → 안식월 시 → 나머지
       + [j for j in due if j['id'].startswith('an-')][:AN_PER]
       + [j for j in due if j['id'].startswith(('yg', 'yk'))][:YG_PER + 1] + reg[3:])
# 한 번에 너무 많이 올리면 블로거가 글쓰기를 막는다(2026-10-19 21편 뒤 403) → 하루 BLOGGER_TOTAL편까지만, 간격도 넉넉히
due = due[:int(os.environ.get('BLOGGER_TOTAL', '12'))]
for j in due:
    body = dict(kind='blogger#post', title=j['title'], content=add_more(j['render']()), labels=j['labels'])
    if j['date'] < TODAY:                        # 밀린 글은 원래 날짜 아침으로 (블로그 글 순서 유지)
        body['published'] = f'{j["date"]}T07:{n % 60:02d}:00+09:00'
    r, code = None, 0
    for wait in (120, 300, 600, 900, 0):        # 블로거는 짧은 시간에 글을 많이 올리면 429를 준다 → 쉬었다가 다시
        try:
            r = call(f'https://www.googleapis.com/blogger/v3/blogs/{BLOG}/posts/', json.dumps(body, ensure_ascii=False).encode('utf-8'), AUTH, 'POST')
            break
        except urllib.error.HTTPError as e:
            code = e.code
            print('blogger: 실패', j['id'], code, e.read()[:300].decode('utf-8', 'replace'))
            if code != 429 or not wait: break
            print('blogger: 잠시 쉼', wait, '초'); time.sleep(wait)
    if r is None:
        fails += 1
        if code == 401 or (code in (403, 429) and fails >= 3): break   # 403·429가 세 번 거듭되면 오늘은 그만
        continue
    fails = 0
    done[j['id']] = r.get('url', '')
    n += 1
    json.dump(done, open(done_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    time.sleep(150)
print('blogger: today', TODAY, 'posted', n, '· waiting', len(due) - n, '· total done', len(done))
