# posts.json 중 예약일(한국 시간)이 된 글을 구글 블로거에 올린다. 올린 글은 blogger_done.json에 남겨 두 번 올리지 않는다.
# 열쇠(BLOGGER_CLIENT_ID / BLOGGER_CLIENT_SECRET / BLOGGER_REFRESH_TOKEN)가 없으면 아무것도 하지 않는다.
import os, re, json, html, datetime, urllib.request, urllib.parse, urllib.error, time, sys

D = os.path.dirname(os.path.abspath(__file__))
BLOG = '5791371153360346841'
SITE = 'https://saechang888-code.github.io/'
MAX_PER_RUN = int(os.environ.get('BLOGGER_MAX', '12'))       # 밀린 글이 많아도 하루에 이만큼만 (스팸 판정 방지)
TODAY = os.environ.get('TODAY') or (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
KIND_LABEL = {'행사': '교회 소식', '설교': '설교', '예화': '예화', '독후감': '독후감', '팡세/예화': '팡세'}

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

def esc(s): return html.escape(s, quote=False)

def render(p):
    out = []
    if p['kind'] == '행사':
        out.append(f'<p><img src="{SITE}assets/event_4x5.jpg" alt="행복나눔축제 초대장" style="max-width:100%"></p>')
    for para in re.split(r'\n\s*\n', p['body'].strip()):
        para = para.strip('\n')
        if not para.strip(): continue
        if para.startswith('■'):
            out.append(f'<h3>{esc(para.lstrip("■ ").strip())}</h3>')
        else:
            body = esc(para).replace('\n', '<br>')
            body = re.sub(r'(https://[^\s<]+)', r'<a href="\1">\1</a>', body)
            out.append(f'<p style="color:#666">{body}</p>' if para.startswith(('— ', '※')) else f'<p>{body}</p>')
    out.append(f'<p style="color:#666">— 독서주특기 이재선 목사 · <a href="{SITE}writings/{p["id"]}.html">홈페이지에서 보기</a></p>')
    return '\n'.join(out)

def labels(p):
    ls = [KIND_LABEL.get(p['kind'], p['kind'])]
    leaf = p['category'].split('>')[-1].strip()
    if leaf and leaf not in ls: ls.append(leaf)
    for t in p['tags'].split():
        t = t.lstrip('#')
        if t and t not in ls and len(','.join(ls + [t])) <= 180: ls.append(t)
        if len(ls) >= 8: break
    return [l.replace(',', ' ') for l in ls]

done_path = os.path.join(D, 'blogger_done.json')
done = json.load(open(done_path, encoding='utf-8')) if os.path.exists(done_path) else {}
posts = json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8'))
due = sorted((p for p in posts if p['date'] <= TODAY and p['id'] not in done), key=lambda p: (p['date'], p['id']))

n = 0
for p in due[:MAX_PER_RUN]:
    # 원래 예약일 아침 시간으로 발행일을 맞춰 블로그 글 순서가 홈페이지와 같게 한다
    slot = sum(1 for q in posts if q['date'] == p['date'] and q['id'] < p['id'])
    published = f'{p["date"]}T{7 + 3 * min(slot, 5):02d}:00:00+09:00'
    if p['date'] == TODAY:
        published = None                      # 오늘 글은 지금 시각으로
    body = dict(kind='blogger#post', title=p['title'], content=render(p), labels=labels(p))
    if published: body['published'] = published
    try:
        r = call(f'https://www.googleapis.com/blogger/v3/blogs/{BLOG}/posts/', json.dumps(body, ensure_ascii=False).encode('utf-8'), AUTH, 'POST')
    except urllib.error.HTTPError as e:
        print('blogger: 실패', p['id'], e.code, e.read()[:300].decode('utf-8', 'replace'))
        if e.code in (401, 403, 429): break
        continue
    done[p['id']] = r.get('url', '')
    n += 1
    json.dump(done, open(done_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    time.sleep(3)
print('blogger: today', TODAY, 'posted', n, '· waiting', len(due) - n, '· total done', len(done))
