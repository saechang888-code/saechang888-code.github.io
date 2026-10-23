# 예화 원글의 출처 표기 — 저자·매체가 분명한 것은 정확히 밝힌다 (주인님 지시 2026-10-23)
# credit 원문 예: '맥스 루케이도, 「사랑으로 맺은 평화조약」 (둘로스 설교자료)', '겨자씨, 「…」 (국민940310)'
# 둘로스·목회 프리미엄·sermon-jesus 같은 모음처 이름은 쓰지 않는다 (feedback_yehwa-premium-credit-label)
import re

# 신문 칼럼 이름은 저자가 아니다 → 매체 이름 뒤에 붙인다
COLUMN = {'겨자씨': '「겨자씨」', '모퉁이돌': '「모퉁이돌」', '모퉁이 돌': '「모퉁이돌」', '작은창': '「작은창」', '길섶에서': '「길섶에서」'}
# 잘려 있거나 영문으로 적힌 저자 이름 바로잡기
ALIAS = {'KIM필곤': '김필곤', 'JOONGON K': '김준곤', '우찌무라 간': '우치무라 간조', '우찌무라 간조': '우치무라 간조',
         '가가와 도요': '가가와 도요히코', '스펄젼': '찰스 스펄전', '오스왈드': '오스왈드 샌더스', '밀드레드': '밀드레드 스탬',
         '범브란트': '리하르트 범브란트', '조엘': '조엘 소넨버그', '임한창 국민일보 기자': '임한창(국민일보 기자)'}
# 저자로 볼 수 없는 말(약어·주제어)
DROP = {'각공', 'kpg', '적극적', '나라', 'kcm'}


def author_of(c):
    m = re.match(r'^(.*?),\s*「', c or '')
    if not m: return '', ''
    a = m.group(1).strip()
    if a in COLUMN: return '', COLUMN[a]
    a = re.sub(r'\(?\s*https?://[^\s)]*\)?', '', a)                 # 누리집 주소
    a = re.sub(r'\s*설교\s*중에서\s*', '', a)
    a = re.sub(r'<([^<>]*)>', r'(\1)', a).strip(' ,|-')
    a = ALIAS.get(a, a)
    if not a or a in DROP or not re.search(r'[가-힣A-Za-z]{2}', a): return '', ''
    return a, ''


def book_of(c, who):
    # 끝 괄호가 책 이름일 때만 — 교회·모음처·설교자료·날짜는 책이 아니다
    m = re.search(r'\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$', c)
    if not m: return ''
    b = m.group(1).strip()
    if not b or b in who or who in b or re.search(r'교회|둘로스|tistory|설교|예화 모음|자료|프리미엄|https?:|\d{4}|^[\d\s.,/-]+$', b): return ''
    return b


def credit_txt_with(c, press):
    if '게재)' in c or '아름다운 글)' in c: return c
    who, col = author_of(c)
    t = re.search(r'「[^」]*」', c); t = t.group(0) if t else ''
    head = ', '.join(x for x in (who, t) if x)
    if '목회 프리미엄' in c:
        return (head or re.sub(r'\s*\(목회 프리미엄.*\)$', '', c)) + ('' if who else ' (온라인에 공유된 감동적인 글)')
    if '설교 「' in c: return '온라인에 공유된 감동적인 예화'      # 둘로스 설교 원고 속에서 뽑은 예화
    p = press(c)
    if p:
        if col: p = re.sub(r'^(\S*일보|「[^」]*」)', r'\1 ' + col, p, 1)
        return (head + ' ' if head else '') + f'({p} 게재)'
    if who: return head + (f' (『{b}』)' if (b := book_of(c, who)) else '')
    return (t + ' ' if t else '') + '(온라인에 공개된 감동적인 예화)'
