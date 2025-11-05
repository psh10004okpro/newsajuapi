"""
합충형해파(合沖刑害破) 데이터
천간과 지지의 상호 작용 관계

합(合): 화합, 조화
충(沖): 충돌, 대립
형(刑): 형벌, 고통
해(害): 해침, 방해
파(破): 파괴, 손상
"""

# ========== 천간 ==========

# 천간합(天干合) - 합화오행
HEAVENLY_STEM_HARMONY = {
    ("갑", "기"): {"result": "토", "name": "갑기합화토", "effect": "긍정적", "description": "중정지합, 신의"},
    ("기", "갑"): {"result": "토", "name": "갑기합화토", "effect": "긍정적", "description": "중정지합, 신의"},

    ("을", "경"): {"result": "금", "name": "을경합화금", "effect": "긍정적", "description": "인의지합"},
    ("경", "을"): {"result": "금", "name": "을경합화금", "effect": "긍정적", "description": "인의지합"},

    ("병", "신"): {"result": "수", "name": "병신합화수", "effect": "긍정적", "description": "위엄지합"},
    ("신", "병"): {"result": "수", "name": "병신합화수", "effect": "긍정적", "description": "위엄지합"},

    ("정", "임"): {"result": "목", "name": "정임합화목", "effect": "긍정적", "description": "인자지합"},
    ("임", "정"): {"result": "목", "name": "정임합화목", "effect": "긍정적", "description": "인자지합"},

    ("무", "계"): {"result": "화", "name": "무계합화화", "effect": "긍정적/주의", "description": "무정지합, 욕정"},
    ("계", "무"): {"result": "화", "name": "무계합화화", "effect": "긍정적/주의", "description": "무정지합, 욕정"}
}

# 천간충(天干沖) - 대립
HEAVENLY_STEM_CONFLICT = [
    ("갑", "경"),  # 목금충
    ("경", "갑"),
    ("을", "신"),
    ("신", "을"),
    ("병", "임"),  # 화수충
    ("임", "병"),
    ("정", "계"),
    ("계", "정")
]

# ========== 지지 ==========

# 지지 육합(六合)
EARTHLY_SIX_HARMONY = {
    ("자", "축"): {"result": "토", "name": "자축합토", "description": "음양의 조화"},
    ("축", "자"): {"result": "토", "name": "자축합토", "description": "음양의 조화"},

    ("인", "해"): {"result": "목", "name": "인해합목", "description": "목의 생성"},
    ("해", "인"): {"result": "목", "name": "인해합목", "description": "목의 생성"},

    ("묘", "술"): {"result": "화", "name": "묘술합화", "description": "화의 생성"},
    ("술", "묘"): {"result": "화", "name": "묘술합화", "description": "화의 생성"},

    ("진", "유"): {"result": "금", "name": "진유합금", "description": "금의 생성"},
    ("유", "진"): {"result": "금", "name": "진유합금", "description": "금의 생성"},

    ("사", "신"): {"result": "수", "name": "사신합수", "description": "수의 생성"},
    ("신", "사"): {"result": "수", "name": "사신합수", "description": "수의 생성"},

    ("오", "미"): {"result": "화토", "name": "오미합", "description": "화토의 조화"},
    ("미", "오"): {"result": "화토", "name": "오미합", "description": "화토의 조화"}
}

# 지지 삼합(三合) - 3개가 모여야 함
EARTHLY_THREE_HARMONY = {
    "목국": {
        "branches": ["해", "묘", "미"],
        "result": "목",
        "description": "목국 삼합, 인자애 증가",
        "effect": "긍정적"
    },
    "화국": {
        "branches": ["인", "오", "술"],
        "result": "화",
        "description": "화국 삼합, 열정과 활동",
        "effect": "긍정적"
    },
    "금국": {
        "branches": ["사", "유", "축"],
        "result": "금",
        "description": "금국 삼합, 결단력 증가",
        "effect": "긍정적"
    },
    "수국": {
        "branches": ["신", "자", "진"],
        "result": "수",
        "description": "수국 삼합, 지혜 증가",
        "effect": "긍정적"
    }
}

# 지지 방합(方合) - 3개가 모여야 함
EARTHLY_DIRECTION_HARMONY = {
    "동방": {
        "branches": ["인", "묘", "진"],
        "result": "목",
        "description": "동방 목국"
    },
    "남방": {
        "branches": ["사", "오", "미"],
        "result": "화",
        "description": "남방 화국"
    },
    "서방": {
        "branches": ["신", "유", "술"],
        "result": "금",
        "description": "서방 금국"
    },
    "북방": {
        "branches": ["해", "자", "축"],
        "result": "수",
        "description": "북방 수국"
    }
}

# 지지 육충(六沖) - 정면 대립
EARTHLY_SIX_CONFLICT = {
    ("자", "오"): {"name": "자오충", "description": "수화 대립, 마음 불안", "effect": "강한 충돌"},
    ("오", "자"): {"name": "자오충", "description": "수화 대립, 마음 불안", "effect": "강한 충돌"},

    ("축", "미"): {"name": "축미충", "description": "토토 충돌, 고민", "effect": "중간 충돌"},
    ("미", "축"): {"name": "축미충", "description": "토토 충돌, 고민", "effect": "중간 충돌"},

    ("인", "신"): {"name": "인신충", "description": "목금 대립, 변화", "effect": "강한 충돌"},
    ("신", "인"): {"name": "인신충", "description": "목금 대립, 변화", "effect": "강한 충돌"},

    ("묘", "유"): {"name": "묘유충", "description": "목금 대립, 손상", "effect": "강한 충돌"},
    ("유", "묘"): {"name": "묘유충", "description": "목금 대립, 손상", "effect": "강한 충돌"},

    ("진", "술"): {"name": "진술충", "description": "토토 충돌, 변동", "effect": "중간 충돌"},
    ("술", "진"): {"name": "진술충", "description": "토토 충돌, 변동", "effect": "중간 충돌"},

    ("사", "해"): {"name": "사해충", "description": "화수 대립, 갈등", "effect": "강한 충돌"},
    ("해", "사"): {"name": "사해충", "description": "화수 대립, 갈등", "effect": "강한 충돌"}
}

# 지지 삼형(三刑)
EARTHLY_THREE_PENALTY = {
    "인사신형": {
        "branches": ["인", "사", "신"],
        "name": "인사신 삼형(무은지형)",
        "description": "은혜를 저버림, 배신",
        "effect": "부정적"
    },
    "축술미형": {
        "branches": ["축", "술", "미"],
        "name": "축술미 삼형(지세지형)",
        "description": "세력 다툼, 고집",
        "effect": "부정적"
    },
    "자묘형": {
        "branches": ["자", "묘"],
        "name": "자묘형(무례지형)",
        "description": "예의 없음, 무례",
        "effect": "부정적"
    }
}

# 자형 (스스로 형)
SELF_PENALTY = ["진", "오", "유", "해"]  # 진진형, 오오형, 유유형, 해해형

# 지지 육해(六害)
EARTHLY_SIX_HARM = {
    ("자", "미"): {"name": "자미해", "description": "방해, 손해"},
    ("미", "자"): {"name": "자미해", "description": "방해, 손해"},

    ("축", "오"): {"name": "축오해", "description": "고통, 어려움"},
    ("오", "축"): {"name": "축오해", "description": "고통, 어려움"},

    ("인", "사"): {"name": "인사해", "description": "질투, 방해"},
    ("사", "인"): {"name": "인사해", "description": "질투, 방해"},

    ("묘", "진"): {"name": "묘진해", "description": "손상, 피해"},
    ("진", "묘"): {"name": "묘진해", "description": "손상, 피해"},

    ("신", "해"): {"name": "신해해", "description": "갈등, 해침"},
    ("해", "신"): {"name": "신해해", "description": "갈등, 해침"},

    ("유", "술"): {"name": "유술해", "description": "손실, 해침"},
    ("술", "유"): {"name": "유술해", "description": "손실, 해침"}
}

# 지지 육파(六破)
EARTHLY_SIX_BREAK = {
    ("자", "유"): {"name": "자유파", "description": "파괴, 손상"},
    ("유", "자"): {"name": "자유파", "description": "파괴, 손상"},

    ("축", "진"): {"name": "축진파", "description": "파괴, 손상"},
    ("진", "축"): {"name": "축진파", "description": "파괴, 손상"},

    ("인", "해"): {"name": "인해파", "description": "파괴, 손상"},
    ("해", "인"): {"name": "인해파", "description": "파괴, 손상"},

    ("묘", "오"): {"name": "묘오파", "description": "파괴, 손상"},
    ("오", "묘"): {"name": "묘오파", "description": "파괴, 손상"},

    ("사", "신"): {"name": "사신파", "description": "파괴, 손상"},
    ("신", "사"): {"name": "사신파", "description": "파괴, 손상"},

    ("미", "술"): {"name": "미술파", "description": "파괴, 손상"},
    ("술", "미"): {"name": "미술파", "description": "파괴, 손상"}
}


def check_harmony_conflict(pillars):
    """
    합충형해파 확인

    Args:
        pillars: 사주 4기둥 리스트

    Returns:
        발견된 관계 리스트
    """
    results = {
        "harmonies": [],   # 합
        "conflicts": [],   # 충
        "penalties": [],   # 형
        "harms": [],       # 해
        "breaks": []       # 파
    }

    # 천간 추출
    stems = [p.heavenly_stem for p in pillars]
    # 지지 추출
    branches = [p.earthly_branch for p in pillars]

    # 천간합 확인
    for i in range(len(stems)):
        for j in range(i+1, len(stems)):
            pair = (stems[i], stems[j])
            if pair in HEAVENLY_STEM_HARMONY:
                results["harmonies"].append({
                    "type": "천간합",
                    **HEAVENLY_STEM_HARMONY[pair]
                })

    # 지지 육합 확인
    for i in range(len(branches)):
        for j in range(i+1, len(branches)):
            pair = (branches[i], branches[j])
            if pair in EARTHLY_SIX_HARMONY:
                results["harmonies"].append({
                    "type": "지지육합",
                    **EARTHLY_SIX_HARMONY[pair]
                })

    # 지지 육충 확인
    for i in range(len(branches)):
        for j in range(i+1, len(branches)):
            pair = (branches[i], branches[j])
            if pair in EARTHLY_SIX_CONFLICT:
                results["conflicts"].append({
                    "type": "육충",
                    **EARTHLY_SIX_CONFLICT[pair]
                })

    # 지지 육해 확인
    for i in range(len(branches)):
        for j in range(i+1, len(branches)):
            pair = (branches[i], branches[j])
            if pair in EARTHLY_SIX_HARM:
                results["harms"].append({
                    "type": "육해",
                    **EARTHLY_SIX_HARM[pair]
                })

    return results
