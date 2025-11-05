"""
지지 장간(地支藏干) 데이터

지지 안에 숨어있는 천간들
정확한 십성 및 오행 강약 계산에 필수
"""

from typing import Dict, List

# 지지 장간 데이터
# 본기(本氣): 주된 기운
# 중기(中氣): 중간 기운
# 여기(餘氣): 나머지 기운
EARTHLY_BRANCH_HIDDEN_STEMS = {
    "자": {
        "본기": "계",
        "중기": [],
        "여기": [],
        "all": ["계"],
        "description": "자(子) - 계수만 있음, 순수한 수"
    },
    "축": {
        "본기": "기",
        "중기": ["신"],
        "여기": ["계"],
        "all": ["기", "계", "신"],
        "description": "축(丑) - 기토, 계수, 신금 (토→수→금)"
    },
    "인": {
        "본기": "갑",
        "중기": ["병"],
        "여기": ["무"],
        "all": ["갑", "병", "무"],
        "description": "인(寅) - 갑목, 병화, 무토 (목→화→토)"
    },
    "묘": {
        "본기": "을",
        "중기": [],
        "여기": [],
        "all": ["을"],
        "description": "묘(卯) - 을목만 있음, 순수한 목"
    },
    "진": {
        "본기": "무",
        "중기": ["계"],
        "여기": ["을"],
        "all": ["무", "을", "계"],
        "description": "진(辰) - 무토, 을목, 계수 (토→목→수)"
    },
    "사": {
        "본기": "병",
        "중기": ["경"],
        "여기": ["무"],
        "all": ["병", "경", "무"],
        "description": "사(巳) - 병화, 경금, 무토 (화→금→토)"
    },
    "오": {
        "본기": "정",
        "중기": [],
        "여기": ["기"],
        "all": ["정", "기"],
        "description": "오(午) - 정화, 기토 (화→토)"
    },
    "미": {
        "본기": "기",
        "중기": ["정"],
        "여기": ["을"],
        "all": ["기", "을", "정"],
        "description": "미(未) - 기토, 을목, 정화 (토→목→화)"
    },
    "신": {
        "본기": "경",
        "중기": ["임"],
        "여기": ["무"],
        "all": ["경", "무", "임"],
        "description": "신(申) - 경금, 무토, 임수 (금→토→수)"
    },
    "유": {
        "본기": "신",
        "중기": [],
        "여기": [],
        "all": ["신"],
        "description": "유(酉) - 신금만 있음, 순수한 금"
    },
    "술": {
        "본기": "무",
        "중기": ["정"],
        "여기": ["신"],
        "all": ["무", "신", "정"],
        "description": "술(戌) - 무토, 신금, 정화 (토→금→화)"
    },
    "해": {
        "본기": "임",
        "중기": [],
        "여기": ["갑"],
        "all": ["임", "갑"],
        "description": "해(亥) - 임수, 갑목 (수→목)"
    }
}


# 장간 투출력(透出力) - 천간에 나타날 때의 힘
HIDDEN_STEM_POWER = {
    "본기": 100,  # 본기가 천간에 투출되면 가장 강함
    "중기": 70,   # 중기 투출
    "여기": 40    # 여기 투출
}


# 월령(月令) 장간력 - 월지의 장간은 특별히 강함
MONTH_BRANCH_POWER_MULTIPLIER = 1.5


def get_hidden_stems(branch: str) -> Dict:
    """
    지지의 장간 조회

    Args:
        branch: 지지 (자, 축, 인...)

    Returns:
        장간 정보 딕셔너리
    """
    return EARTHLY_BRANCH_HIDDEN_STEMS.get(branch, {
        "본기": None,
        "중기": [],
        "여기": [],
        "all": [],
        "description": "알 수 없는 지지"
    })


def get_all_stems_in_branch(branch: str) -> List[str]:
    """지지 안의 모든 천간 반환"""
    hidden_info = get_hidden_stems(branch)
    return hidden_info.get("all", [])


def get_main_stem(branch: str) -> str:
    """지지의 본기(주된 천간) 반환"""
    hidden_info = get_hidden_stems(branch)
    return hidden_info.get("본기", "")


def calculate_stem_power_in_branch(
    stem: str,
    branch: str,
    is_month_branch: bool = False
) -> int:
    """
    지지 내 천간의 힘 계산

    Args:
        stem: 찾으려는 천간
        branch: 지지
        is_month_branch: 월지 여부

    Returns:
        힘의 정도 (0-150)
    """
    hidden_info = get_hidden_stems(branch)

    # 본기인지 확인
    if hidden_info["본기"] == stem:
        power = HIDDEN_STEM_POWER["본기"]
    # 중기인지 확인
    elif stem in hidden_info["중기"]:
        power = HIDDEN_STEM_POWER["중기"]
    # 여기인지 확인
    elif stem in hidden_info["여기"]:
        power = HIDDEN_STEM_POWER["여기"]
    else:
        # 해당 지지에 없음
        return 0

    # 월지라면 힘이 더 강함
    if is_month_branch:
        power = int(power * MONTH_BRANCH_POWER_MULTIPLIER)

    return power


def find_branches_containing_stem(stem: str) -> List[str]:
    """
    특정 천간을 포함하는 지지들 찾기

    Args:
        stem: 천간

    Returns:
        해당 천간을 포함하는 지지 리스트
    """
    branches = []

    for branch, info in EARTHLY_BRANCH_HIDDEN_STEMS.items():
        if stem in info["all"]:
            branches.append(branch)

    return branches


def analyze_branch_composition(branch: str) -> Dict:
    """
    지지의 구성 분석

    Returns:
        {
            "주오행": "목",
            "부오행": ["화", "토"],
            "천간들": ["갑", "병", "무"],
            "특징": "..."
        }
    """
    from src.calculators.saju_calculator import SajuCalculator

    hidden_info = get_hidden_stems(branch)
    element_map = SajuCalculator.ELEMENT_MAP

    main_stem = hidden_info["본기"]
    all_stems = hidden_info["all"]

    elements = [element_map.get(s) for s in all_stems if s]
    main_element = element_map.get(main_stem) if main_stem else None

    return {
        "지지": branch,
        "본기": main_stem,
        "중기": hidden_info["중기"],
        "여기": hidden_info["여기"],
        "주오행": main_element,
        "모든천간": all_stems,
        "모든오행": list(set(elements)),
        "설명": hidden_info["description"]
    }


# 사계절별 지지의 왕쇠(旺衰)
SEASONAL_BRANCH_STRENGTH = {
    "봄": {  # 목왕, 화상, 수휴, 금수, 토사
        "인": "왕", "묘": "왕", "진": "여기",
        "사": "상", "오": "상", "미": "상",
        "신": "수", "유": "수", "술": "수",
        "해": "휴", "자": "휴", "축": "휴"
    },
    "여름": {  # 화왕, 토상, 목휴, 수수, 금사
        "사": "왕", "오": "왕", "미": "여기",
        "신": "사", "유": "사", "술": "여기",
        "인": "휴", "묘": "휴", "진": "휴",
        "해": "수", "자": "수", "축": "수"
    },
    "가을": {  # 금왕, 수상, 토휴, 화수, 목사
        "신": "왕", "유": "왕", "술": "여기",
        "해": "상", "자": "상", "축": "상",
        "진": "휴", "미": "휴", "술": "휴",
        "인": "사", "묘": "사", "사": "수", "오": "수"
    },
    "겨울": {  # 수왕, 목상, 금휴, 토수, 화사
        "해": "왕", "자": "왕", "축": "여기",
        "인": "상", "묘": "상", "진": "상",
        "신": "휴", "유": "휴", "술": "휴",
        "사": "사", "오": "사", "미": "수", "진": "수"
    }
}


def get_branch_seasonal_strength(branch: str, month: int) -> str:
    """
    계절에 따른 지지의 왕쇠

    Args:
        branch: 지지
        month: 월 (1-12)

    Returns:
        왕쇠 상태 (왕/상/휴/수/사/여기)
    """
    if month in [2, 3, 4]:
        season = "봄"
    elif month in [5, 6, 7]:
        season = "여름"
    elif month in [8, 9, 10]:
        season = "가을"
    else:
        season = "겨울"

    return SEASONAL_BRANCH_STRENGTH[season].get(branch, "중")
