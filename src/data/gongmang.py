"""
공망(空亡) 데이터 및 계산

공망은 "하늘이 비어있다"는 의미로, 일주를 기준으로 판단
60갑자를 10개씩 묶었을 때 남는 2개의 지지가 공망
"""

# 60갑자 순환별 공망 지지
# 일주가 속한 순(旬)에 따라 공망 지지가 결정됨
GONGMANG_BY_순 = {
    "갑자순": {
        "pillars": ["갑자", "을축", "병인", "정묘", "무진", "기사", "경오", "신미", "임신", "계유"],
        "gongmang": ["술", "해"],
        "description": "갑자순 - 술해 공망"
    },
    "갑술순": {
        "pillars": ["갑술", "을해", "병자", "정축", "무인", "기묘", "경진", "신사", "임오", "계미"],
        "gongmang": ["신", "유"],
        "description": "갑술순 - 신유 공망"
    },
    "갑신순": {
        "pillars": ["갑신", "을유", "병술", "정해", "무자", "기축", "경인", "신묘", "임진", "계사"],
        "gongmang": ["오", "미"],
        "description": "갑신순 - 오미 공망"
    },
    "갑오순": {
        "pillars": ["갑오", "을미", "병신", "정유", "무술", "기해", "경자", "신축", "임인", "계묘"],
        "gongmang": ["진", "사"],
        "description": "갑오순 - 진사 공망"
    },
    "갑진순": {
        "pillars": ["갑진", "을사", "병오", "정미", "무신", "기유", "경술", "신해", "임자", "계축"],
        "gongmang": ["인", "묘"],
        "description": "갑진순 - 인묘 공망"
    },
    "갑인순": {
        "pillars": ["갑인", "을묘", "병진", "정사", "무오", "기미", "경신", "신유", "임술", "계해"],
        "gongmang": ["자", "축"],
        "description": "갑인순 - 자축 공망"
    }
}

# 일주별 공망 매핑 (빠른 조회용)
GONGMANG_MAP = {}
for 순_name, 순_data in GONGMANG_BY_순.items():
    for pillar in 순_data["pillars"]:
        GONGMANG_MAP[pillar] = {
            "gongmang_branches": 순_data["gongmang"],
            "순": 순_name,
            "description": 순_data["description"]
        }


def get_gongmang_for_day_pillar(day_pillar_str: str) -> dict:
    """
    일주에 해당하는 공망 지지 조회

    Args:
        day_pillar_str: 일주 문자열 (예: "갑자")

    Returns:
        공망 정보 딕셔너리
    """
    return GONGMANG_MAP.get(day_pillar_str, {
        "gongmang_branches": [],
        "순": "알 수 없음",
        "description": "일주 정보 없음"
    })


def check_gongmang_in_saju(day_pillar_str: str, year_branch: str, month_branch: str,
                            day_branch: str, hour_branch: str) -> dict:
    """
    사주에서 공망 검사

    Args:
        day_pillar_str: 일주 문자열
        year_branch: 년지
        month_branch: 월지
        day_branch: 일지
        hour_branch: 시지

    Returns:
        공망 분석 결과
    """
    gongmang_info = get_gongmang_for_day_pillar(day_pillar_str)
    gongmang_branches = gongmang_info.get("gongmang_branches", [])

    found_gongmang = []
    branches = {
        "년지": year_branch,
        "월지": month_branch,
        "일지": day_branch,
        "시지": hour_branch
    }

    for position, branch in branches.items():
        if branch in gongmang_branches:
            found_gongmang.append({
                "position": position,
                "branch": branch,
                "effect": _get_gongmang_effect(position),
                "severity": _get_gongmang_severity(position)
            })

    return {
        "day_pillar_gongmang": gongmang_branches,
        "순": gongmang_info.get("순", ""),
        "found_in_saju": found_gongmang,
        "count": len(found_gongmang),
        "has_gongmang": len(found_gongmang) > 0,
        "interpretation": _interpret_gongmang(found_gongmang, gongmang_branches)
    }


def _get_gongmang_effect(position: str) -> str:
    """공망 위치별 영향"""
    effects = {
        "년지": "조상, 부모, 어린 시절에 영향",
        "월지": "형제, 청년기, 직장에 영향",
        "일지": "배우자, 본인, 중년기에 영향",
        "시지": "자녀, 말년, 노후에 영향"
    }
    return effects.get(position, "알 수 없음")


def _get_gongmang_severity(position: str) -> str:
    """공망 심각도"""
    # 일지 공망이 가장 중요
    if position == "일지":
        return "높음"
    elif position in ["월지", "시지"]:
        return "중간"
    else:
        return "낮음"


def _interpret_gongmang(found_gongmang: list, gongmang_branches: list) -> str:
    """공망 종합 해석"""
    if not found_gongmang:
        return f"사주에 공망({', '.join(gongmang_branches)})이 없습니다. 안정적인 구조입니다."

    count = len(found_gongmang)
    positions = [g["position"] for g in found_gongmang]

    if count == 1:
        pos = positions[0]
        return f"{pos}에 공망이 있어 {_get_gongmang_effect(pos)} 허무함이나 불안정성이 있을 수 있습니다."
    elif count == 2:
        return f"{', '.join(positions)}에 공망이 있어 해당 영역에서 불안정성이 나타날 수 있습니다. 정신적 성장의 기회가 될 수 있습니다."
    else:
        return f"다수({count}개)의 공망이 있습니다. 물질보다 정신적 가치를 추구하는 경향이 강할 수 있습니다."


# 공망의 긍정적/부정적 측면
GONGMANG_ASPECTS = {
    "negative": [
        "허무함, 공허함",
        "불안정성",
        "예상치 못한 변화",
        "성취의 어려움",
        "관계의 불안정"
    ],
    "positive": [
        "물질에 대한 집착이 적음",
        "정신적 성장 가능",
        "종교, 철학, 예술 분야 재능",
        "초월적 사고",
        "자유로운 영혼"
    ],
    "advice": [
        "물질적 성취에만 집중하지 말 것",
        "정신적 가치를 중요시할 것",
        "예술, 종교, 철학 분야 탐구",
        "안정적인 기반 마련 필요",
        "급한 결정 피하기"
    ]
}
