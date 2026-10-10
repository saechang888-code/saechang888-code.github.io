# 네이버 블로그의 시(자연시·생활시·자아성찰시·기탄잘리) 본문을 모아 poems.json으로 저장 (블로거에 다시 싣기 위한 한 번용)
import os, re, json, html, time, urllib.request
D = os.path.dirname(os.path.abspath(__file__))
BLOG = 'saechang888'
CATS = {91: '자연시', 92: '생활시', 93: '자아성찰시', 94: '기탄잘리(찬양시)'}
UA = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)', 'Referer': f'https://m.blog.naver.com/{BLOG}'}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode('utf-8', 'replace')

def body_of(log_no):
    h = get(f'https://m.blog.naver.com/PostView.naver?blogId={BLOG}&logNo={log_no}')
    m = re.search(r'<div class="se-main-container">(.*?)<div class="(?:post_footer|comment_area|se_doc_footer)', h, re.S) \
        or re.search(r'<div class="se-main-container">(.*)', h, re.S)
    if not m:
        m = re.search(r'id="postViewArea"[^>]*>(.*?)</div>\s*</div>', h, re.S)
    if not m: return ''
    s = m.group(1)
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'</p>|<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('​', '').replace('\xa0', ' ')
    lines = [l.rstrip() for l in s.split('\n')]
    out, blank = [], 0
    for l in lines:
        if l.strip(): out.append(l.strip()); blank = 0
        else:
            blank += 1
            if blank == 1 and out: out.append('')
    return '\n'.join(out).strip()

poems = []
path = os.path.join(D, 'poems.json')
old = {p['logNo']: p for p in json.load(open(path, encoding='utf-8'))} if os.path.exists(path) else {}
for no, cat in CATS.items():
    page = 1
    while True:
        j = json.loads(get(f'https://m.blog.naver.com/api/blogs/{BLOG}/post-list?categoryNo={no}&itemCount=30&page={page}'))
        items = j.get('result', {}).get('items', [])
        if not items: break
        for it in items:
            ln = it['logNo']
            p = old.get(ln) or dict(logNo=ln, title=html.unescape(it.get('titleWithInspectMessage') or it.get('title') or ''), cat=cat,
                                    date=time.strftime('%Y-%m-%d', time.localtime(it.get('addDate', 0) / 1000)) if it.get('addDate') else '')
            if not p.get('body'):
                p['body'] = body_of(ln); time.sleep(0.4)
            poems.append(p)
        page += 1
json.dump(poems, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
import collections
print(len(poems), collections.Counter(p['cat'] for p in poems), 'empty', sum(1 for p in poems if not p['body']))
