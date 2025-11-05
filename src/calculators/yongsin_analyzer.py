"""
용신(用神) 분석기

용신은 사주의 균형을 맞추기 위해 필요한 오행
사주가 치우쳐 있거나 부족한 부분을 보완하는 핵심 오행
"""

from typing import Dict, List, Tuple, Optional


class YongsinAnalyzer:
    """용신 분석기"""

    # 오행 상생 관계
    ELEMENT_GENERATION = {
        "목": "화",  # 목생화
        "화": "토",  # 화생토
        "토": "금",  # 토생금
        "금": "수",  # 금생수
        "수": "목"   # 수생목
    }

    # 오행 상극 관계
    ELEMENT_DESTRUCTION = {
        "목": "토",  # 목극토
        "화": "금",  # 화극금
        "토": "수",  # 토극수
        "금": "목",  # 금극목
        "수": "화"   # 수극화
    }

    # 역상극 (누가 나를 극하는가)
    ELEMENT_DESTROYED_BY = {
        "목": "금",
        "화": "수",
        "토": "목",
        "금": "화",
        "수": "토"
    }

    # 계절별 특성 (월지 기준)
    SEASON_ELEMENT = {
        "인": {"season": "봄", "element": "목", "temperature": "따뜻"},
        "묘": {"season": "봄", "element": "목", "temperature": "따뜻"},
        "진": {"season": "봄", "element": "토", "temperature": "따뜻"},
        "사": {"season": "여름", "element": "화", "temperature": "뜨거움"},
        "오": {"season": "여름", "element": "화", "temperature": "뜨거움"},
        "미": {"season": "여름", "element": "토", "temperature": "뜨거움"},
        "신": {"season": "가을", "element": "금", "temperature": "시원"},
        "유": {"season": "가을", "element": "금", "temperature": "시원"},
        "술": {"season": "가을", "element": "토", "temperature": "시원"},
        "해": {"season": "겨울", "element": "수", "temperature": "차가움"},
        "자": {"season": "겨울", "element": "수", "temperature": "차가움"},
        "축": {"season": "겨울", "element": "토", "temperature": "차가움"}
    }

    def __init__(self, element_map: Dict):
        """
        Args:
            element_map: 천간/지지의 오행 매핑 정보
        """
        self.element_map = element_map

    def analyze_yongsin(self, day_master: str, five_elements: Dict,
                        month_branch: str, birth_month: int) -> Dict:
        """
        용신 분석

        Args:
            day_master: 일간
            five_elements: 오행 분포 (목, 화, 토, 금, 수)
            month_branch: 월지
            birth_month: 출생 월 (1-12)

        Returns:
            용신 분석 결과
        """
        day_element = self.element_map.get(day_master)

        # 1. 억부용신 (강약 조절)
        yeobu_yongsin = self._determine_yeobu_yongsin(day_element, five_elements)

        # 2. 조후용신 (계절 조절)
        johu_yongsin = self._determine_johu_yongsin(day_element, month_branch, birth_month)

        # 3. 용신 종합 판단
        primary_yongsin, secondary_yongsin = self._综合_yongsin(
            yeobu_yongsin, johu_yongsin, five_elements
        )

        # 4. 희신, 기신 판단
        heesin = self._determine_heesin(primary_yongsin)
        gisin = self._determine_gisin(primary_yongsin)

        return {
            "primary_yongsin": {
                "element": primary_yongsin,
                "name": f"{primary_yongsin}(用神)",
                "reason": self._get_yongsin_reason(primary_yongsin, yeobu_yongsin, johu_yongsin),
                "importance": "매우 높음"
            },
            "secondary_yongsin": {
                "element": secondary_yongsin,
                "name": f"{secondary_yongsin}(輔用神)" if secondary_yongsin else None,
                "importance": "높음" if secondary_yongsin else None
            } if secondary_yongsin else None,
            "heesin": {
                "element": heesin,
                "name": f"{heesin}(喜神)",
                "description": "용신을 돕는 오행",
                "importance": "중상"
            },
            "gisin": {
                "element": gisin,
                "name": f"{gisin}(忌神)",
                "description": "피해야 할 오행",
                "importance": "부정적"
            },
            "interpretation": self._interpret_yongsin(primary_yongsin, secondary_yongsin, day_element),
            "recommendations": self._get_recommendations(primary_yongsin, heesin, gisin)
        }

    def _determine_yeobu_yongsin(self, day_element: str, five_elements: Dict) -> str:
        """
        억부용신 결정 (강약 조절)
        일간이 강하면 설기/극, 약하면 생/비겁
        """
        # 일간 오행의 개수
        element_counts = {
            "목": five_elements.get("wood", 0),
            "화": five_elements.get("fire", 0),
            "토": five_elements.get("earth", 0),
            "금": five_elements.get("metal", 0),
            "수": five_elements.get("water", 0)
        }

        day_element_count = element_counts.get(day_element, 0)
        total_count = sum(element_counts.values())
        day_element_ratio = day_element_count / total_count if total_count > 0 else 0

        # 일간을 생해주는 오행 개수
        supporting_element = self._get_supporting_element(day_element)
        supporting_count = element_counts.get(supporting_element, 0)

        # 일간 + 지원 오행 비율
        total_support = day_element_count + supporting_count
        support_ratio = total_support / total_count if total_count > 0 else 0

        # 강약 판단
        if support_ratio > 0.5:  # 강함
            # 설기(洩氣): 일간이 생하는 오행
            return self.ELEMENT_GENERATION[day_element]
        elif support_ratio < 0.3:  # 약함
            # 생조(生助): 일간을 생하는 오행
            return supporting_element
        else:  # 중간
            # 약간 약한 쪽으로 판단하여 생조
            return supporting_element

    def _determine_johu_yongsin(self, day_element: str, month_branch: str, birth_month: int) -> Optional[str]:
        """
        조후용신 결정 (계절 조절)
        겨울에 태어났으면 따뜻한 오행, 여름에 태어났으면 시원한 오행
        """
        season_info = self.SEASON_ELEMENT.get(month_branch, {})
        season = season_info.get("season")
        temperature = season_info.get("temperature")

        # 겨울 (차가움) - 화, 목 필요
        if temperature == "차가움":
            if day_element in ["금", "수"]:
                return "화"  # 따뜻하게
            else:
                return "목"  # 생기 필요

        # 여름 (뜨거움) - 수, 금 필요
        elif temperature == "뜨거움":
            if day_element in ["화", "목"]:
                return "수"  # 시원하게
            else:
                return "금"  # 조절

        # 봄/가을 - 균형
        else:
            return None  # 조후용신 불필요

    def _综合_yongsin(self, yeobu: str, johu: Optional[str], five_elements: Dict) -> Tuple[str, Optional[str]]:
        """용신 종합 판단"""
        if johu and yeobu == johu:
            # 억부용신과 조후용신이 같으면 명확
            return yeobu, None
        elif johu:
            # 둘 다 중요하면 조후용신을 우선
            return johu, yeobu
        else:
            # 조후용신이 없으면 억부용신만
            return yeobu, None

    def _determine_heesin(self, yongsin: str) -> str:
        """희신 결정 (용신을 돕는 오행)"""
        # 용신을 생하는 오행
        return self._get_supporting_element(yongsin)

    def _determine_gisin(self, yongsin: str) -> str:
        """기신 결정 (피해야 할 오행)"""
        # 용신을 극하는 오행
        return self.ELEMENT_DESTROYED_BY.get(yongsin, "")

    def _get_supporting_element(self, element: str) -> str:
        """오행을 생하는 오행 찾기"""
        for parent, child in self.ELEMENT_GENERATION.items():
            if child == element:
                return parent
        return element

    def _get_yongsin_reason(self, yongsin: str, yeobu: str, johu: Optional[str]) -> str:
        """용신 선정 이유"""
        reasons = []

        if yongsin == yeobu:
            reasons.append("일간의 강약 조절을 위해")

        if yongsin == johu:
            reasons.append("계절의 한열 조절을 위해")

        return ", ".join(reasons) if reasons else "사주 균형을 위해"

    def _interpret_yongsin(self, primary: str, secondary: Optional[str], day_element: str) -> str:
        """용신 해석"""
        interpretation = f"사주의 균형을 위해 {primary} 오행이 가장 중요합니다. "

        if secondary:
            interpretation += f"{secondary} 오행도 함께 보완하면 좋습니다. "

        element_names = {"목": "나무/목재", "화": "불/열/빛", "토": "흙/대지", "금": "금속/광물", "수": "물"}
        interpretation += f"\n\n{element_names[primary]}과 관련된 색상, 방향, 직업이 유리합니다."

        return interpretation

    def _get_recommendations(self, yongsin: str, heesin: str, gisin: str) -> Dict:
        """용신 기반 추천사항"""
        # 오행별 속성
        element_properties = {
            "목": {
                "colors": ["녹색", "청록색", "연두색"],
                "directions": ["동쪽"],
                "numbers": [3, 8],
                "materials": ["나무", "목재", "식물"],
                "careers": ["임업", "농업", "교육", "출판", "패션"]
            },
            "화": {
                "colors": ["빨강", "주황", "분홍", "보라"],
                "directions": ["남쪽"],
                "numbers": [2, 7],
                "materials": ["불", "열", "전기", "조명"],
                "careers": ["에너지", "요식업", "엔터테인먼트", "IT"]
            },
            "토": {
                "colors": ["노랑", "갈색", "베이지"],
                "directions": ["중앙", "남서", "동북"],
                "numbers": [5, 10],
                "materials": ["흙", "도자기", "부동산"],
                "careers": ["부동산", "건축", "농업", "도자기"]
            },
            "금": {
                "colors": ["흰색", "금색", "은색", "회색"],
                "directions": ["서쪽"],
                "numbers": [4, 9],
                "materials": ["금속", "광물", "보석"],
                "careers": ["금융", "제조", "기계", "보석"]
            },
            "수": {
                "colors": ["검정", "파랑", "남색"],
                "directions": ["북쪽"],
                "numbers": [1, 6],
                "materials": ["물", "유리", "액체"],
                "careers": ["무역", "유통", "해운", "수산업"]
            }
        }

        yongsin_props = element_properties.get(yongsin, {})
        gisin_props = element_properties.get(gisin, {})

        return {
            "beneficial": {
                "colors": yongsin_props.get("colors", []),
                "directions": yongsin_props.get("directions", []),
                "numbers": yongsin_props.get("numbers", []),
                "materials": yongsin_props.get("materials", []),
                "careers": yongsin_props.get("careers", [])
            },
            "avoid": {
                "colors": gisin_props.get("colors", []),
                "directions": gisin_props.get("directions", []),
                "element": gisin
            }
        }
