"""
추가 신살(神殺) 데이터

학당귀인, 문창귀인, 금여귀인, 월덕귀인, 천덕귀인, 고란살, 홍염살
Phase 3 정확도 개선
"""

from typing import List, Dict, Optional


# 학당귀인 (學堂貴人) - 학문 재능
HAKDANG_GWIN = {
    "갑": "사",
    "을": "오",
    "병": "신",
    "정": "유",
    "무": "신",
    "기": "유",
    "경": "해",
    "신": "자",
    "임": "인",
    "계": "묘"
}

# 문창귀인 (文昌貴人) - 문학 재능
MUNCHANG_GWIN = {
    "갑": "사",
    "을": "오",
    "병": "신",
    "정": "유",
    "무": "신",
    "기": "유",
    "경": "해",
    "신": "자",
    "임": "인",
    "계": "묘"
}

# 금여귀인 (金輿貴人) - 부귀
GEUMYEO_GWIN = {
    "갑": "인",
    "을": "해",
    "병": "사",
    "정": "사",
    "무": "사",
    "기": "사",
    "경": "신",
    "신": "신",
    "임": "해",
    "계": "해"
}

# 월덕귀인 (月德貴人) - 월별 덕성
WEOLDEOK_GWIN = {
    1: "병",   # 정월 (인월)
    2: "갑",   # 2월 (묘월)
    3: "임",   # 3월 (진월)
    4: "신",   # 4월 (사월)
    5: "을",   # 5월 (오월)
    6: "기",   # 6월 (미월)
    7: "정",   # 7월 (신월)
    8: "경",   # 8월 (유월)
    9: "을",   # 9월 (술월)
    10: "무",  # 10월 (해월)
    11: "계",  # 11월 (자월)
    12: "무"   # 12월 (축월)
}

# 천덕귀인 (天德貴人) - 월별 하늘의 덕
CHEONDEOK_GWIN = {
    1: "정",   # 정월 (인월)
    2: "신",   # 2월 (묘월)
    3: "임",   # 3월 (진월)
    4: "신",   # 4월 (사월)
    5: "해",   # 5월 (오월)
    6: "갑",   # 6월 (미월)
    7: "계",   # 7월 (신월)
    8: "인",   # 8월 (유월)
    9: "병",   # 9월 (술월)
    10: "을",  # 10월 (해월)
    11: "사",  # 11월 (자월)
    12: "경"   # 12월 (축월)
}

# 고란살 (孤鸞殺) - 독신, 고독
# 특정 일주에만 해당
GORAN_SAL_DAYS = [
    "갑인", "을사", "무신", "임자", "계축",
    "정사", "신해", "병오", "무오", "기사"
]

# 홍염살 (紅艶殺) - 이성 관계, 매력
HONGYEOM_SAL = {
    "갑": "오",
    "을": "신",
    "병": "인",
    "정": "미",
    "무": "인",
    "기": "신",
    "경": "술",
    "신": "유",
    "임": "자",
    "계": "해"
}


def check_additional_divine_spirits(
    year_stem: str, month_stem: str, day_stem: str, hour_stem: str,
    year_branch: str, month_branch: str, day_branch: str, hour_branch: str,
    birth_month: int,
    day_pillar_str: str
) -> List[Dict]:
    """
    추가 신살 확인

    Args:
        year_stem: 년간
        month_stem: 월간
        day_stem: 일간
        hour_stem: 시간
        year_branch: 년지
        month_branch: 월지
        day_branch: 일지
        hour_branch: 시지
        birth_month: 출생월 (1-12)
        day_pillar_str: 일주 문자열 (예: "갑인")

    Returns:
        발견된 추가 신살 목록
    """
    spirits = []

    # 모든 천간과 지지
    stems = [year_stem, month_stem, day_stem, hour_stem]
    branches = [year_branch, month_branch, day_branch, hour_branch]
    positions = ["년간", "월간", "일간", "시간"]
    branch_positions = ["년지", "월지", "일지", "시지"]

    # 1. 학당귀인 (일간 기준)
    hakdang_branch = HAKDANG_GWIN.get(day_stem)
    if hakdang_branch:
        for i, branch in enumerate(branches):
            if branch == hakdang_branch:
                spirits.append({
                    "name": "학당귀인(學堂貴人)",
                    "location": branch_positions[i],
                    "type": "학문/지식",
                    "effect": "긍정적",
                    "description": "학문적 재능과 지식에 대한 열정",
                    "characteristics": ["총명함", "학문 성취", "지식 탐구", "교육 재능", "연구 능력"],
                    "advice": "학문, 연구, 교육 분야에서 큰 성공 가능"
                })

    # 2. 문창귀인 (일간 기준)
    munchang_branch = MUNCHANG_GWIN.get(day_stem)
    if munchang_branch:
        for i, branch in enumerate(branches):
            if branch == munchang_branch:
                spirits.append({
                    "name": "문창귀인(文昌貴人)",
                    "location": branch_positions[i],
                    "type": "문학/예술",
                    "effect": "긍정적",
                    "description": "문학적 재능과 예술적 감각",
                    "characteristics": ["문학 재능", "필력", "표현력", "창작", "예술 감각"],
                    "advice": "작가, 시인, 예술가로서 뛰어난 재능 발휘"
                })

    # 3. 금여귀인 (일간 기준)
    geumyeo_branch = GEUMYEO_GWIN.get(day_stem)
    if geumyeo_branch:
        for i, branch in enumerate(branches):
            if branch == geumyeo_branch:
                spirits.append({
                    "name": "금여귀인(金輿貴人)",
                    "location": branch_positions[i],
                    "type": "부귀/재물",
                    "effect": "긍정적",
                    "description": "부귀와 재물을 상징하는 길신",
                    "characteristics": ["부귀", "재물운", "경제적 안정", "호화로움", "물질적 풍요"],
                    "advice": "재물운이 좋으며 경제적으로 안정된 삶 가능"
                })

    # 4. 월덕귀인 (출생월 + 천간/지지 확인)
    weoldeok_stem = WEOLDEOK_GWIN.get(birth_month)
    if weoldeok_stem:
        for i, stem in enumerate(stems):
            if stem == weoldeok_stem:
                spirits.append({
                    "name": "월덕귀인(月德貴人)",
                    "location": positions[i],
                    "type": "덕성/복록",
                    "effect": "매우 긍정적",
                    "description": "월의 덕성을 받아 복록이 많음",
                    "characteristics": ["덕성", "복록", "선행", "화해", "구원"],
                    "advice": "어려움을 잘 극복하고 타인으로부터 도움을 많이 받음"
                })

    # 5. 천덕귀인 (출생월 + 천간/지지 확인)
    cheondeok_item = CHEONDEOK_GWIN.get(birth_month)
    if cheondeok_item:
        # 천간 확인
        for i, stem in enumerate(stems):
            if stem == cheondeok_item:
                spirits.append({
                    "name": "천덕귀인(天德貴人)",
                    "location": positions[i],
                    "type": "하늘의 덕",
                    "effect": "매우 긍정적",
                    "description": "하늘의 덕을 받아 재난을 면함",
                    "characteristics": ["천복", "재난 회피", "보호", "장수", "평안"],
                    "advice": "큰 재난과 사고에서 보호받으며 평안한 삶"
                })

        # 지지 확인
        for i, branch in enumerate(branches):
            if branch == cheondeok_item:
                spirits.append({
                    "name": "천덕귀인(天德貴人)",
                    "location": branch_positions[i],
                    "type": "하늘의 덕",
                    "effect": "매우 긍정적",
                    "description": "하늘의 덕을 받아 재난을 면함",
                    "characteristics": ["천복", "재난 회피", "보호", "장수", "평안"],
                    "advice": "큰 재난과 사고에서 보호받으며 평안한 삶"
                })

    # 6. 고란살 (일주 확인)
    if day_pillar_str in GORAN_SAL_DAYS:
        spirits.append({
            "name": "고란살(孤鸞殺)",
            "location": "일주",
            "type": "고독/독신",
            "effect": "주의",
            "description": "고독하고 독신의 기운",
            "characteristics": ["고독", "독립", "이별", "독신 가능성", "내적 성장"],
            "advice": "결혼운이 약하거나 독신 가능성. 정신적 성장의 기회로 삼을 수 있음"
        })

    # 7. 홍염살 (일간 기준)
    hongyeom_branch = HONGYEOM_SAL.get(day_stem)
    if hongyeom_branch:
        for i, branch in enumerate(branches):
            if branch == hongyeom_branch:
                spirits.append({
                    "name": "홍염살(紅艶殺)",
                    "location": branch_positions[i],
                    "type": "이성/매력",
                    "effect": "중립",
                    "description": "이성에게 매력적이며 연애운 왕성",
                    "characteristics": ["매력", "이성운", "연애", "외모", "풍류"],
                    "advice": "이성에게 인기가 많으나 감정 관리 필요. 외모와 매력을 잘 활용할 것"
                })

    return spirits


def get_spirit_description(spirit_name: str) -> Optional[Dict]:
    """
    신살 상세 설명 조회

    Args:
        spirit_name: 신살 이름

    Returns:
        신살 상세 정보
    """
    descriptions = {
        "학당귀인": {
            "full_name": "學堂貴人",
            "category": "귀인신",
            "importance": "높음",
            "detailed_description": """
학당귀인은 학문과 지식을 상징하는 길신입니다.
이 신살이 있는 사람은 총명하고 학문적 재능이 뛰어나며,
교육, 연구, 학술 분야에서 큰 성과를 이룰 수 있습니다.
평생 배움을 즐기고 지식을 추구하는 성향이 강합니다.
            """.strip(),
            "historical_reference": "고대 중국 명리학에서 과거 급제와 관련된 길신으로 여겨짐"
        },
        "문창귀인": {
            "full_name": "文昌貴人",
            "category": "귀인신",
            "importance": "높음",
            "detailed_description": """
문창귀인은 문학과 예술을 상징하는 길신입니다.
뛰어난 필력과 표현력을 가지며 창작 활동에 재능이 있습니다.
작가, 시인, 기자, 예술가 등 창의적 직업에 적합합니다.
말과 글로 사람들에게 감동을 줄 수 있는 능력이 있습니다.
            """.strip(),
            "historical_reference": "문창성(文昌星)의 기운을 받은 사람"
        },
        "금여귀인": {
            "full_name": "金輿貴人",
            "category": "귀인신",
            "importance": "중상",
            "detailed_description": """
금여귀인은 황금 수레를 의미하며 부귀를 상징합니다.
재물운이 좋고 경제적으로 안정된 삶을 살 가능성이 높습니다.
편안하고 호화로운 생활을 즐길 수 있으며,
물질적으로 풍요로운 환경에서 성장할 수 있습니다.
            """.strip(),
            "historical_reference": "귀인이 황금 수레를 타고 다니는 모습에서 유래"
        },
        "월덕귀인": {
            "full_name": "月德貴人",
            "category": "귀인신",
            "importance": "매우 높음",
            "detailed_description": """
월덕귀인은 달의 덕성을 받는 매우 강력한 길신입니다.
어려운 상황에서도 잘 극복하고 타인으로부터 도움을 받습니다.
덕망이 있어 주변 사람들에게 존경받으며,
평생 복록이 많고 화를 면하는 운이 강합니다.
            """.strip(),
            "historical_reference": "천덕귀인과 함께 있으면 그 길함이 배가됨"
        },
        "천덕귀인": {
            "full_name": "天德貴人",
            "category": "귀인신",
            "importance": "매우 높음",
            "detailed_description": """
천덕귀인은 하늘의 덕을 받는 최고의 길신 중 하나입니다.
큰 재난과 사고에서 보호받으며 장수할 운이 있습니다.
위기 상황에서 기적처럼 도움을 받거나 화를 면합니다.
평안하고 안정된 삶을 살 수 있는 천복이 있습니다.
            """.strip(),
            "historical_reference": "월덕귀인과 함께 있으면 천월덕(天月德)이라 하여 최고의 길신"
        },
        "고란살": {
            "full_name": "孤鸞殺",
            "category": "흉살",
            "importance": "중간",
            "detailed_description": """
고란살은 외로운 난새를 의미하며 고독의 기운을 상징합니다.
결혼운이 약하거나 독신으로 사는 경향이 있습니다.
하지만 독립적이고 자기만의 세계를 구축하는 능력이 있으며,
정신적으로 성숙하고 내적 성장을 이룰 수 있습니다.
            """.strip(),
            "historical_reference": "옛날 도사나 승려들이 가졌던 신살로 여겨짐"
        },
        "홍염살": {
            "full_name": "紅艶殺",
            "category": "중립신",
            "importance": "중간",
            "detailed_description": """
홍염살은 붉은 빛의 아름다움을 의미하며 매력을 상징합니다.
이성에게 매력적으로 보이며 연애운이 왕성합니다.
외모가 뛰어나거나 풍류를 즐기는 성향이 있습니다.
다만 감정 관리를 잘 해야 하며, 과도한 이성 관계는 주의가 필요합니다.
            """.strip(),
            "historical_reference": "예술가, 연예인에게서 많이 발견되는 신살"
        }
    }

    return descriptions.get(spirit_name)
