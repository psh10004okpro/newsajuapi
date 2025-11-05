"""
60갑자 일주론 데이터
각 일주별 성격, 재능, 특성

일주는 본인을 나타내는 가장 중요한 기둥
"""

# 60갑자 일주 정보 (주요 일주만 상세 설명, 나머지는 기본 정보)
SIXTY_JIAZI_INFO = {
    # 갑 일주 (甲日柱)
    "갑자": {
        "name": "갑자일주(甲子日柱)",
        "element": "목",
        "yin_yang": "양",
        "strength": "중상",
        "description": "총명하고 지혜로우며 학문에 재능이 있음",
        "personality": ["총명함", "지혜로움", "활동적", "호기심 많음"],
        "strengths": ["학습 능력 우수", "적응력 좋음", "창의적"],
        "weaknesses": ["현실감 부족", "이상주의", "변덕"],
        "career": ["교육", "연구", "IT", "예술"],
        "health": ["신경계 주의", "간 건강 관리"],
        "relationship": "적극적이나 변화 많음"
    },

    "갑인": {
        "name": "갑인일주(甲寅日柱)",
        "element": "목",
        "yin_yang": "양",
        "strength": "강",
        "description": "강하고 독립적이며 리더십이 있음",
        "personality": ["독립적", "강한 의지", "정직함", "직선적"],
        "strengths": ["리더십", "추진력", "정직"],
        "weaknesses": ["융통성 부족", "고집", "성급함"],
        "career": ["경영", "공무원", "군인", "교육"],
        "health": ["간 건강", "근골격계"],
        "relationship": "강하고 주도적"
    },

    # 을 일주 (乙日柱)
    "을축": {
        "name": "을축일주(乙丑日柱)",
        "element": "목",
        "yin_yang": "음",
        "strength": "중",
        "description": "부드럽고 끈기있으며 축재 능력이 있음",
        "personality": ["부드러움", "끈기", "인내", "절약"],
        "strengths": ["끈기", "재물 관리", "안정 추구"],
        "weaknesses": ["소극적", "우유부단", "걱정 많음"],
        "career": ["금융", "회계", "부동산", "요식업"],
        "health": ["소화기", "피부"],
        "relationship": "온화하고 헌신적"
    },

    "을묘": {
        "name": "을묘일주(乙卯日柱)",
        "element": "목",
        "yin_yang": "음",
        "strength": "강",
        "description": "섬세하고 예술적 재능이 뛰어남",
        "personality": ["섬세함", "예술적", "감성적", "친절함"],
        "strengths": ["예술 재능", "인간관계", "섬세함"],
        "weaknesses": ["예민함", "우유부단", "의존적"],
        "career": ["예술", "디자인", "상담", "서비스"],
        "health": ["신경계", "간"],
        "relationship": "다정하고 배려심 많음"
    },

    # 병 일주 (丙日柱)
    "병오": {
        "name": "병오일주(丙午日柱)",
        "element": "화",
        "yin_yang": "양",
        "strength": "최강",
        "description": "열정적이고 활동적이며 명예욕이 강함",
        "personality": ["열정적", "활동적", "명예중시", "솔직함"],
        "strengths": ["리더십", "열정", "추진력"],
        "weaknesses": ["성급함", "과격함", "독선적"],
        "career": ["경영", "정치", "스포츠", "영업"],
        "health": ["심장", "혈압", "눈"],
        "relationship": "열정적이나 자기중심적"
    },

    "병자": {
        "name": "병자일주(丙子日柱)",
        "element": "화",
        "yin_yang": "양",
        "strength": "중",
        "description": "밝고 사교적이며 인기가 있음",
        "personality": ["밝음", "사교적", "낙천적", "활발함"],
        "strengths": ["인기", "사교성", "적응력"],
        "weaknesses": ["경박함", "집중력 부족", "산만함"],
        "career": ["연예", "방송", "영업", "서비스"],
        "health": ["신장", "방광", "심장"],
        "relationship": "인기 많고 사교적"
    },

    # 무 일주 (戊日柱)
    "무술": {
        "name": "무술일주(戊戌日柱)",
        "element": "토",
        "yin_yang": "양",
        "strength": "강",
        "description": "신념이 강하고 리더십이 있음, 괴강살",
        "personality": ["강함", "신념", "리더십", "고집"],
        "strengths": ["리더십", "결단력", "신념"],
        "weaknesses": ["고집", "융통성 부족", "독선"],
        "career": ["경영", "정치", "군인", "종교"],
        "health": ["위장", "피부"],
        "relationship": "강하고 주도적"
    },

    # 경 일주 (庚日柱)
    "경진": {
        "name": "경진일주(庚辰日柱)",
        "element": "금",
        "yin_yang": "양",
        "strength": "강",
        "description": "강하고 날카로우며 결단력이 있음, 괴강살",
        "personality": ["강함", "결단력", "냉철함", "정의감"],
        "strengths": ["결단력", "정의감", "리더십"],
        "weaknesses": ["냉정함", "융통성 부족", "날카로움"],
        "career": ["법조", "군인", "경찰", "의사"],
        "health": ["폐", "대장", "피부"],
        "relationship": "강하나 냉정할 수 있음"
    },

    # 임 일주 (壬日柱)
    "임진": {
        "name": "임진일주(壬辰日柱)",
        "element": "수",
        "yin_yang": "양",
        "strength": "강",
        "description": "지혜롭고 변화에 능하며 괴강살",
        "personality": ["지혜로움", "변화", "유연함", "강함"],
        "strengths": ["지혜", "적응력", "전략"],
        "weaknesses": ["변덕", "불안정", "과욕"],
        "career": ["무역", "IT", "금융", "연구"],
        "health": ["신장", "방광", "귀"],
        "relationship": "지혜롭고 변화 많음"
    },

    # 계 일주 (癸日柱)
    "계사": {
        "name": "계사일주(癸巳日柱)",
        "element": "수",
        "yin_yang": "음",
        "strength": "중",
        "description": "섬세하고 지혜로우며 신비로움",
        "personality": ["섬세함", "지혜", "신비로움", "예민함"],
        "strengths": ["직관력", "섬세함", "사색"],
        "weaknesses": ["예민함", "우울", "소극적"],
        "career": ["예술", "종교", "철학", "상담"],
        "health": ["신장", "신경계"],
        "relationship": "섬세하고 감성적"
    }
}

# 나머지 일주는 기본 정보만 (천간과 지지 조합)
# 실제 서비스에서는 AI가 해석하므로 상세 정보는 주요 일주만 있어도 충분

HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]


def _get_element(stem):
    """천간의 오행 반환"""
    element_map = {
        "갑": "목", "을": "목",
        "병": "화", "정": "화",
        "무": "토", "기": "토",
        "경": "금", "신": "금",
        "임": "수", "계": "수"
    }
    return element_map.get(stem, "목")


def _get_yin_yang(stem):
    """천간의 음양 반환"""
    yang_stems = ["갑", "병", "무", "경", "임"]
    return "양" if stem in yang_stems else "음"


# 60갑자 전체 목록 생성
SIXTY_JIAZI_LIST = []
for i in range(60):
    stem = HEAVENLY_STEMS[i % 10]
    branch = EARTHLY_BRANCHES[i % 12]
    jiazi = stem + branch
    SIXTY_JIAZI_LIST.append(jiazi)

    # 상세 정보가 없는 일주는 기본 정보 생성
    if jiazi not in SIXTY_JIAZI_INFO:
        SIXTY_JIAZI_INFO[jiazi] = {
            "name": f"{jiazi}일주",
            "element": _get_element(stem),
            "yin_yang": _get_yin_yang(stem),
            "description": f"{stem}{branch} 조합의 일주"
        }


def get_jiazi_info(day_pillar_str):
    """
    일주 정보 조회

    Args:
        day_pillar_str: 일주 문자열 (예: "갑자")

    Returns:
        일주 정보 딕셔너리
    """
    return SIXTY_JIAZI_INFO.get(day_pillar_str, {
        "name": f"{day_pillar_str}일주",
        "description": "일주 정보"
    })
