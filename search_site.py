# 뜻으로 찾기: 예화·설교·독후감·시를 '뜻 벡터'로 바꿔 search/ 에 두고, 검색어도 브라우저에서 같은 방법으로 바꿔 가까운 글을 찾는다.
# 낱말 표(search_data/)는 무료 정적 임베딩 potion-multilingual-128M에서 뽑았다(tools/semsearch/make_vocab.py). 서버·요금 없음.
# 글자 나누기·평균 내기는 search.html 의 자바스크립트와 똑같이 한다 — 한쪽을 고치면 다른 쪽도 고친다.
import os, re, json, html, unicodedata
from datetime import datetime, timedelta, timezone
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
SD, OUT = os.path.join(D, 'search_data'), os.path.join(D, 'search')
V = json.load(open(os.path.join(SD, 'vocab.json'), encoding='utf-8'))
DIM = V['dim']
PIECE = {p: i for i, p in enumerate(V['p'])}
SCORE = V['s']
MAXLEN = max(len(p) for p in V['p'])
VEC = np.fromfile(os.path.join(SD, 'vecs.bin'), dtype=np.int8).reshape(-1, DIM).astype(np.float32) \
      * np.fromfile(os.path.join(SD, 'scale.bin'), dtype=np.float32)[:, None]
PUNCT = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
MAX_TOK = 512                                          # 긴 글은 앞부분 512조각만 (모델과 같다)

def norm(t):
    t = unicodedata.normalize('NFKC', t)
    for c in PUNCT: t = t.replace(c, f' {c} ')
    return re.sub(r'\s+', ' ', t).strip()

def tokenize(t):
    out = []
    for w in norm(t).split(' '):
        s = '▁' + w; n = len(s)
        best = [(-1e18, -1)] * (n + 1); best[0] = (0.0, -1)
        for i in range(n):
            if best[i][0] <= -1e18: continue
            for j in range(i + 1, min(n, i + MAXLEN) + 1):
                k = PIECE.get(s[i:j])
                if k is not None:
                    sc = best[i][0] + SCORE[k]
                    if sc > best[j][0]: best[j] = (sc, i)
            if best[i + 1][0] <= -1e18: best[i + 1] = (best[i][0] - 100, i)   # 표에 없는 글자는 건너뛴다
        ids, j = [], n
        while j > 0:
            i = best[j][1]; k = PIECE.get(s[i:j])
            if k is not None: ids.append(k)
            j = i
        out += ids[::-1]
        if len(out) >= MAX_TOK: break
    return out[:MAX_TOK]

def embed(t, idf):
    """조각 벡터를 흔한 정도(idf)로 무게를 달아 더한 뒤 길이 1로 — '은/는/이야기' 같은 흔한 조각은 덜 반영된다"""
    ids = tokenize(t)
    if not ids: return np.zeros(DIM, np.float32)
    v = (VEC[ids] * idf[ids, None]).sum(0); n = np.linalg.norm(v)
    return v / n if n else v

if __name__ == '__main__':
    def esc(s): return html.escape(s, quote=True)
    docs = []
    # 예화: yehwa_site.py가 남긴 목록(제목·주제·쪽 주소·본문)
    for x in json.load(open(os.path.join(D, '_yehwa_list.json'), encoding='utf-8')):
        docs.append(dict(k='예화', t=x['t'], kw=x['kw'], u=x['u'], b=x['b']))
    # 설교·독후감·시: 예약일이 된 글만 (writings.py와 같은 기준)
    TODAY = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d')
    KIND = {'설교': '설교', '독후감': '독후감', '시': '시', '예화': '예화', '팡세/예화': '팡세'}
    for p in json.load(open(os.path.join(D, 'posts.json'), encoding='utf-8')):
        if p['date'] <= TODAY and p['kind'] in KIND:
            docs.append(dict(k=KIND[p['kind']], t=p['title'], kw='', u=f"writings/{p['id']}.html", b=p['body']))
    os.makedirs(OUT, exist_ok=True)
    texts = [d['t'] + ' ' + d['t'] + ' ' + d['b'] for d in docs]           # 제목을 두 번 넣어 조금 더 무겁게
    toks = [tokenize(t) for t in texts]
    df = np.zeros(len(V['p']), np.float32)
    for t in toks: df[list(set(t))] += 1
    idf = np.log((len(toks) + 1) / (df + 1)).astype(np.float32)
    idf.tofile(os.path.join(OUT, 'idf.bin'))
    M = np.stack([embed(t, idf) for t in texts])
    np.round(M * 127).clip(-127, 127).astype(np.int8).tofile(os.path.join(OUT, 'docs.bin'))
    def head(b):                                       # 낱말 맞추기와 미리 보기에 쓰는 첫머리 (적용·말씀 앞까지)
        return re.sub(r'\s+', ' ', b.split('▸')[0]).strip()[:350]
    json.dump({'dim': DIM, 'd': [[d['k'], d['t'], d['kw'], d['u'], head(d['b'])] for d in docs]},
              open(os.path.join(OUT, 'docs.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for f in ('vocab.json', 'vecs.bin', 'scale.bin', 'index.html'):
        open(os.path.join(OUT, f), 'wb').write(open(os.path.join(SD, f), 'rb').read())
    print('뜻 찾기 글', len(docs))
