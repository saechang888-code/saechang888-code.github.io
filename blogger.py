# 예약일(한국 시간)이 된 글을 구글 블로거에 올린다. 올린 글은 blogger_done.json에 남겨 두 번 올리지 않는다.
#  - posts.json: 설교·독후감·팡세·교회 소식 (예화 '묶음' 글은 블로거에는 올리지 않는다)
#  - blogger_yehwa.json: 예화를 한 편씩, 하루 3편
# 열쇠(BLOGGER_CLIENT_ID / BLOGGER_CLIENT_SECRET / BLOGGER_REFRESH_TOKEN)가 없으면 아무것도 하지 않는다.
# REFRESH_ONLY=1 이면 이미 올린 글의 본문만 지금 디자인으로 다시 입힌다.
import os, re, json, html, datetime, urllib.request, urllib.parse, urllib.error, time, sys

D = os.path.dirname(os.path.abspath(__file__))
BLOG = '5791371153360346841'
SITE = 'https://saechang888-code.github.io/'
MAX_PER_RUN = int(os.environ.get('BLOGGER_MAX', '12'))       # 밀린 글이 많아도 하루에 이만큼만 (스팸 판정 방지)
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
def footer(extra=''):
    return (f'<div style="{FOOT}">✍ 독서주특기 · 이재선 목사 (대한예수교장로회 새암교회)<br>'
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
BSTART, PER_CAT = datetime.date(2026, 10, 11), 2
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
# 이미 올린 낱개 예화는 디자인 다시 입히기(REFRESH_ONLY)용으로만 남긴다
for y in yehwa:
    by_y = dict(id=y['id'], date='9999-12-31', title=f'[{y["topic"]} 예화] {y["title"]}', render=lambda y=y: render_yehwa(y), labels=labels_yehwa(y))
    jobs.append(by_y)
for i, p in enumerate(old_poems):
    jobs.append(dict(id=p['id'], date=(BSTART + datetime.timedelta(days=i // PER_CAT)).isoformat(), title=p['title'], render=lambda p=p: render_poem(p), labels=['시', p['sub']]))
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
    for it in call(url, headers=AUTH).get('items', []): posted[it['url']] = it['id']
    n = 0
    for jid, u in done.items():
        j, pid = by_id.get(jid), posted.get(u)
        if not (j and pid): continue
        call(f'https://www.googleapis.com/blogger/v3/blogs/{BLOG}/posts/{pid}', json.dumps(dict(title=j['title'], content=add_more(j['render']()), labels=j['labels']), ensure_ascii=False).encode('utf-8'), AUTH, 'PATCH')
        n += 1; time.sleep(2)
    print('blogger: refreshed', n); sys.exit(0)

due = sorted((j for j in jobs if j['date'] <= TODAY and j['id'] not in done), key=lambda j: (j['date'], j['id']))
n = 0
# 예화 모음 글은 따로 하루 YG_PER편까지 (다른 글의 MAX_PER_RUN 몫을 빼앗지 않게)
due = [j for j in due if not j['id'].startswith(('yg', 'yk'))][:MAX_PER_RUN] + [j for j in due if j['id'].startswith(('yg', 'yk'))][:YG_PER + 1]
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
        if code in (401, 403, 429): break
        continue
    done[j['id']] = r.get('url', '')
    n += 1
    json.dump(done, open(done_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    time.sleep(45)
print('blogger: today', TODAY, 'posted', n, '· waiting', len(due) - n, '· total done', len(done))
