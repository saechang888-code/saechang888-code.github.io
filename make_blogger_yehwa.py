# 예화 묶음 글(posts.json, 10편씩)을 한 편씩 나눠 블로거용 예화 목록(blogger_yehwa.json)을 만든다.
# 주제를 돌아가며 섞고, 하루 PER편씩 START부터 날짜를 붙인다. (한 번만 돌리면 된다)
import os, re, json, datetime, collections

D = os.path.dirname(os.path.abspath(__file__))
START = datetime.date(2026, 10, 11)
PER = 2

posts = json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8'))
items, by_key = [], {}

def key(text): return re.sub(r'\W', '', text)[:60]

for p in posts:
    if p['kind'] != '예화': continue
    book = None
    m = re.match(r'\[성경별 예화\] (\S+)', p['title'])
    if m: book = m.group(1)
    topic = None if book else p['category'].split('>')[-1].strip()
    for sec in re.split(r'\n■ \d+\. ', '\n' + p['body'])[1:]:
        head, _, rest = sec.partition('\n')
        sm = re.search(r'\n— 인용한 설교: (.+)', rest)
        sermon = sm.group(1).strip() if sm else ''
        body = rest[:sm.start()] if sm else rest
        body = re.sub(r'\n※.*$', '', body.strip(), flags=re.S).strip()
        if len(body) < 80: continue
        k = key(body)
        it = by_key.get(k)
        if not it:
            it = by_key[k] = dict(body=body, sermon=sermon, topic=None, books=[])
            items.append(it)
        if topic and not it['topic']: it['topic'] = topic
        if book and book not in it['books']: it['books'].append(book)

GENERIC = re.compile(r'(이야기가|예화가|일화가|글이|말이|내용이|사건이|얘기가)\s*(있습니다|있다|있어요|전해|나옵니다)|^(이런|이러한|어떤|한) (이야기|예화|일화)|들었습니다\.?$|소개합니다')

def title_of(body):
    sents = [re.sub(r'\s+', ' ', s.strip(' "“”\'')) for s in re.split(r'(?<=[.!?。])\s+|\n', body.strip()) if s.strip()]
    s = next((x for x in sents if len(x) >= 14 and not GENERIC.search(x)), sents[0])
    if len(s) <= 34: return s.rstrip('.')
    cut = s[:34]
    cut = cut[:cut.rfind(' ')] if ' ' in cut[12:] else cut
    return cut.rstrip(',.') + '…'

# 손으로 다듬은 제목(yehwa_titles_*.txt: id<TAB>제목, 'SKIP<TAB>id'는 예화가 아니라 뺌)
import glob
TITLES, SKIP = {}, set()
for f in sorted(glob.glob(os.path.join(D, 'yehwa_titles_*.txt'))):
    for line in open(f, encoding='utf-8'):
        a, _, b = line.rstrip('\n').partition('\t')
        if a == 'SKIP': SKIP.add(b.strip())
        elif b.strip(): TITLES[a.strip()] = b.strip()

# 주제별 줄을 세워 하나씩 돌아가며 뽑는다 (같은 주제가 연달아 나오지 않게)
lanes = collections.OrderedDict()
for it in items:
    lanes.setdefault(it['topic'] or '성경별 예화', []).append(it)
order = []
while any(lanes.values()):
    for t in list(lanes):
        if lanes[t]: order.append(lanes[t].pop(0))

# 처음 만든 순서의 번호(y0001…)를 그대로 유지해 제목 파일과 맞춘다
for i, it in enumerate(order): it['id'] = f'y{i + 1:04d}'
order = [it for it in order if it['id'] not in SKIP]
out = []
for i, it in enumerate(order):
    d = START + datetime.timedelta(days=i // PER)
    out.append(dict(id=it['id'], date=d.isoformat(), topic=it['topic'] or '성경 이야기',
                    books=it['books'], sermon=it['sermon'], title=TITLES.get(it['id']) or title_of(it['body']), body=it['body']))
json.dump(out, open(os.path.join(D, 'blogger_yehwa.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('예화', len(out), '편 ·', out[0]['date'], '~', out[-1]['date'])
print(collections.Counter(o['topic'] for o in out).most_common())
for o in out[:6]: print(o['date'], o['topic'], o['books'], '|', o['title'])
