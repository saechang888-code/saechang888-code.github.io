# 예화 주제를 sermon-jesus.tistory.com 예화 모음(417주제)처럼 세밀하게 다시 나눈다 (주인님 지시 2026-10-23)
# 원본 예화 파일(kw)은 그대로 두고, 나눈 결과만 yehwa_topics.json({"원래주제|제목": "새 주제"})에 적는다 — yehwa_site.py가 읽어 쓴다.
# 나누는 순서: ① 원글이 그 사이트 【주제】 모음에서 왔으면 그 주제 ② 제목에 나오는 주제어(가장 구체적인 것)
#             ③ 원래 주제(이름이 다르면 가까운 주제로) ④ 원래 주제가 목록에 없으면 적용 문장에 나오는 주제어
# 사용: python yehwa_topics.py   (다시 돌려도 같은 결과)
import os, re, json, glob, collections
D = os.path.dirname(os.path.abspath(__file__))

TOPICS = '''가난 가정 가치 간증 감동 감사 개혁 거듭남 거룩 거짓 건강 검소 게으름 격려 결심 결혼 겸손 경건 경고 경영 경외 고난 고백 고아 고통 고향 고독
공의 과거 과학 관심 관용 교만 교사 교육 교제 교회 교훈 구원 구제 국가 그리스도인 근면 근심 긍정 긍휼 기다림 기도 기부 기쁨 기억 기적 기초 기회 길 깨달음 꿈
나그네 나눔 나태 낙심 남편 내일 노동 노력 노인 농담 눈 눈물 능력 뇌물 다툼 단순 단점 대접 도덕 도둑 도박 도우심 돈 동물 동행 도전 두려움 뜻
레마 로고스 링컨 마귀 마음 만남 만족 말 말씀 맡김 면류관 명예 명절 모범 목표 목회 무신론 무지 문제 문화 물질 미래 미련함 민족 믿음
바라봄 박해 반석 반성 발 배려 배신 율법 변명 변화 보물 보호 복 복수 복음 복종 봉사 부모 부부 부자 부정 부활 분노 분수 분쟁 불평 불행 비교 비밀 비판 비유 비전 빚 빛
사람 사랑 사망 사명 사치 사탄 사회 살인 삶 상담 상처 새출발 생각 생명 생수 선교 선물 선택 선행 설교 섬김 섭리 성윤리 성공 성급함 성령 성실 성장 성탄절 세례 세상 소망 소명 속죄 소금 손 순결 순교 순종 술 스승 스포츠 슬픔 습관 승리 시간 시기 시련 시작 시험 식물 신뢰 신앙 실수 실천 실패 심판 십자가 씨앗
아내 아름다움 아버지 안식 애국 약속 양보 양심 어리석음 어린이 어머니 언어 애통 얼굴 여성 여행 역경 역사 연습 연약함 열등감 열매 열심 염려 영광 영생 영성 영원 영혼 예배 예술 예식 예언 예절 오늘 오직예수 오해 온유 외모 외식 욕심 용기 용서 우상 우선순위 우연 우정 운명 웃음 원망 위로 위선 유머 유언 유월절 유혹 윤리 은밀 은사 은혜 음식 음행 응답 의 의심 의지 이기심 이단 이웃 인간 인간관계 인격 인과응보 인내 인도 인물 인생 인자 일
자랑 자비 자살 자세 자식 자신감 자아 자연 자유 작은 잠 장수 장애 재능 재림 재물 적 적극 전도 전쟁 전화위복 절기 절망 절제 정신 정의 정직 정치 제자 조국 조급 조화 존경 종교개혁 죄 주인 주일 죽음 준비 증오 증인 지도자 지식 지옥 지체 지혜 직분 직업 진리 진실 질병 질서 징계
착각 찬송 창조 책 책임 천국 천사 철학 청결 청빈 청소년 초청 최선 추석 축복 충고 충성 치유 친구 친절 침묵 칭찬 쾌락 탈무드 태도 타락 판단 편견 평등 평안 평화 피 피난처 핍박
하나님 하나됨 학문 행복 행함 향기 허무 헌금 헌신 협동 형제 형통 화목 화평 환경 회개 효도 후회 훈련 휴식 흡연 희락 희망 희생 힘'''.split()
TS = set(TOPICS)
# 제목에 흔히 나오지만 주제를 가려 주지 못하는 말 — 다른 주제어가 없을 때만 쓴다
WEAK = {'하나님', '사람', '인간', '삶', '인생', '말', '일', '적', '의', '작은', '길', '눈', '손', '발', '피', '힘', '복', '뜻', '잠', '책', '빛', '꿈', '돈', '술', '죄', '오늘', '시간', '마음', '생각', '세상',
        # 다른 뜻으로 더 자주 쓰이는 말 (이 시기, 인도하심, 역사하심, 문제, 시작…)
        '시기', '인도', '역사', '문제', '시작', '과거', '정신', '자세', '장수', '부정', '기초', '인물', '분수', '단순', '조화', '적극', '사회', '문화', '경고', '주인', '내일', '가치', '보호'}
# 지금 주제 가운데 이름이 다른 것 → 가까운 주제
ALIAS = {'성탄': '성탄절', '비젼': '비전', '법': '율법', '특권': '은혜', '자녀': '자식', '교인': '그리스도인', '성경': '말씀', '목사': '목회',
         '고향': '고향', '부흥': '교회', '예수님': '오직예수', '예수': '오직예수', '봉헌': '헌금', '십일조': '헌금', '전도자': '전도', '이웃사랑': '이웃', '거짓말': '거짓', '찬양': '찬송'}
JOSA = '은는이가을를의에과와도로만께요며고서야'

def pat(t):
    # 한 글자 주제(눈·발·손·말·일…)는 낱말로 쓰였을 때만 — '눈물'의 눈, '발견'의 발은 아니다
    if len(t) == 1: return re.compile(rf'(?<![가-힣]){t}(?=$|[^가-힣]|[{JOSA}](?:$|[^가-힣]))')
    return re.compile(re.escape(t))
PAT = {t: pat(t) for t in TOPICS}

def found(text):
    # 주제어와 그 끝자리 — 우리말은 뒤에 오는 말이 중심이다 ('어머니의 기도'는 기도, '십자가의 능력'은 능력)
    out = {}
    for t in TOPICS:
        for m in PAT[t].finditer(text): out[t] = max(out.get(t, 0), m.end())
    return out

def best(cands, freq):
    strong = {t: e for t, e in cands.items() if t not in WEAK}
    pool = strong or cands
    # 맨 뒤에 나오는 말, 같은 자리면 긴 이름(더 구체적)
    return max(pool, key=lambda t: (pool[t], len(t), -freq.get(t, 0))) if pool else None

def load():
    y = json.load(open(os.path.join(D, 'blogger_yehwa.json'), encoding='utf-8'))
    for f in ('doulos_yehwa.json', 'yehwa_ai.json'):
        p = os.path.join(D, f)
        if os.path.exists(p): y += json.load(open(p, encoding='utf-8'))
    return y

def classify(y):
    title_freq = collections.Counter(t for x in y for t in found(x['title']))
    out, how = {}, collections.Counter()
    for x in y:
        kw = x.get('kw', ''); key = f'{kw}|{x["title"]}'
        m = re.search(r'【([^】]+)】', x.get('credit', '') or '')
        tag = ALIAS.get(m.group(1), m.group(1)) if m else None
        if tag in TS: out[key] = tag; how['원글 모음 주제'] += 1; continue
        t = best(found(x['title']), title_freq)
        if t and t not in WEAK: out[key] = t; how['제목'] += 1; continue
        k = ALIAS.get(kw, kw)
        if k in TS: out[key] = k; how['원래 주제'] += 1; continue
        ap = (re.search(r'▸ 적용:(.*)', x['body']) or [None, ''])[1]
        a = best(found(ap), title_freq)
        if a and a not in WEAK: out[key] = a; how['적용 문장'] += 1; continue
        out[key] = t or a or kw; how['그 밖'] += 1
    return out, how

if __name__ == '__main__':
    y = load()
    out, how = classify(y)
    json.dump(out, open(os.path.join(D, 'yehwa_topics.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    c = collections.Counter(out.values())
    print('예화', len(y), '주제', len(c), dict(how))
    print('많은 주제', c.most_common(20))
    print('1~2편 주제', sum(1 for v in c.values() if v <= 2))
    print('목록에 없는 주제', [k for k in c if k not in TS])
