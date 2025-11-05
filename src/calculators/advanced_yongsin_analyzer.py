"""
고급 용신(用神) 분석기

통관용신, 병약용신, 전왕용신 등 정밀한 용신 선정
Phase 1의 정밀 강약 계산 활용
Phase 2 정확도 개선
"""

from typing import Dict, List, Tuple, Optional


class AdvancedYongsinAnalyzer:
    """고급 용신 분석기"""

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

    # 계절별 특성
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
            element_map: 천간/지지의 오행 매핑
        """
        self.element_map = element_map

    def analyze_comprehensive_yongsin(self, day_master: str, five_elements: Dict,
                                      month_branch: str, birth_month: int,
                                      element_strength: int, ten_gods: Dict) -> Dict:
        """
        종합 용신 분석 (Phase 2 정밀)

        Args:
            day_master: 일간
            five_elements: 오행 분포
            month_branch: 월지
            birth_month: 출생 월
            element_strength: Phase 1에서 계산한 일간 강도 (0-200+)
            ten_gods: 십성 정보

        Returns:
            종합 용신 분석 결과
        """
        day_element = self.element_map.get(day_master)

        # 오행 분포 통일
        element_counts = {
            "목": five_elements.get("wood", 0),
            "화": five_elements.get("fire", 0),
            "토": five_elements.get("earth", 0),
            "금": five_elements.get("metal", 0),
            "수": five_elements.get("water", 0)
        }

        # 1. 억부용신 (정밀 강약 기반)
        yeobu_yongsin = self._determine_precise_yeobu_yongsin(
            day_element, element_strength, element_counts
        )

        # 2. 조후용신
        johu_yongsin = self._determine_johu_yongsin(
            day_element, month_branch, birth_month
        )

        # 3. 통관용신 (새로 추가)
        tonggwan_yongsin = self._determine_tonggwan_yongsin(
            day_element, element_counts, ten_gods
        )

        # 4. 병약용신 (새로 추가)
        byungyak_yongsin = self._determine_byungyak_yongsin(
            day_element, element_counts, ten_gods, element_strength
        )

        # 5. 전왕용신 (새로 추가)
        jeonwang_yongsin = self._determine_jeonwang_yongsin(
            day_element, element_strength, element_counts
        )

        # 용신들을 종합 판단
        primary, secondary, yongsin_type = self._综合_all_yongsin(
            yeobu_yongsin, johu_yongsin, tonggwan_yongsin,
            byungyak_yongsin, jeonwang_yongsin, element_strength
        )

        # 희신, 기신
        heesin = self._determine_heesin(primary)
        gisin = self._determine_gisin(primary)

        return {
            "primary_yongsin": {
                "element": primary,
                "name": f"{primary}(用神)",
                "type": yongsin_type,
                "reason": self._get_comprehensive_reason(
                    primary, yeobu_yongsin, johu_yongsin, tonggwan_yongsin,
                    byungyak_yongsin, jeonwang_yongsin
                ),
                "importance": "매우 높음"
            },
            "secondary_yongsin": {
                "element": secondary,
                "name": f"{secondary}(輔用神)" if secondary else None,
                "importance": "높음" if secondary else None
            } if secondary else None,
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
            "yongsin_analysis": {
                "억부용신": yeobu_yongsin,
                "조후용신": johu_yongsin,
                "통관용신": tonggwan_yongsin,
                "병약용신": byungyak_yongsin,
                "전왕용신": jeonwang_yongsin
            },
            "interpretation": self._interpret_yongsin(primary, secondary, yongsin_type, day_element),
            "recommendations": self._get_recommendations(primary, heesin, gisin)
        }

    def _determine_precise_yeobu_yongsin(self, day_element: str,
                                         element_strength: int,
                                         element_counts: Dict) -> str:
        """
        정밀 억부용신 결정 (Phase 1 강도 활용)

        Args:
            day_element: 일간 오행
            element_strength: 정밀 강도 (0-200+)
            element_counts: 오행 개수

        Returns:
            억부용신
        """
        # Phase 1 등급 기준:
        # 150+: 태왕(太旺)
        # 100-149: 왕(旺)
        # 50-99: 중화(中和)
        # 20-49: 약(弱)
        # 0-19: 태약(太弱)

        if element_strength >= 150:
            # 태왕 - 강하게 설기(洩氣)
            return self.ELEMENT_GENERATION[day_element]
        elif element_strength >= 100:
            # 왕 - 설기 또는 극
            return self.ELEMENT_GENERATION[day_element]
        elif element_strength >= 50:
            # 중화 - 이상적, 조후용신 우선
            return None  # 조후용신에 의존
        elif element_strength >= 20:
            # 약 - 생조(生助)
            return self._get_supporting_element(day_element)
        else:
            # 태약 - 강하게 생조 또는 종격
            return self._get_supporting_element(day_element)

    def _determine_johu_yongsin(self, day_element: str, month_branch: str,
                                birth_month: int) -> Optional[str]:
        """조후용신 결정"""
        season_info = self.SEASON_ELEMENT.get(month_branch, {})
        temperature = season_info.get("temperature")

        # 겨울 (차가움) - 화, 목 필요
        if temperature == "차가움":
            if day_element in ["금", "수"]:
                return "화"  # 따뜻하게
            else:
                return "목"  # 생기

        # 여름 (뜨거움) - 수, 금 필요
        elif temperature == "뜨거움":
            if day_element in ["화", "목"]:
                return "수"  # 시원하게
            else:
                return "금"  # 조절

        # 봄/가을 - 균형
        return None

    def _determine_tonggwan_yongsin(self, day_element: str, element_counts: Dict,
                                    ten_gods: Dict) -> Optional[str]:
        """
        통관용신 결정

        충돌하는 두 오행 사이를 중재하는 용신
        예: 목극토 충돌 시 -> 화(木生火, 火生土) 통관
        """
        # 십성 충돌 감지
        conflicts = self._detect_conflicts(ten_gods, element_counts, day_element)

        if not conflicts:
            return None

        # 가장 심각한 충돌에 대한 통관용신
        most_severe_conflict = max(conflicts, key=lambda x: x["severity"])

        # 중재 오행 찾기
        mediator = self._get_mediator_element(
            most_severe_conflict["element1"],
            most_severe_conflict["element2"]
        )

        return mediator

    def _detect_conflicts(self, ten_gods: Dict, element_counts: Dict,
                         day_element: str) -> List[Dict]:
        """오행 충돌 감지"""
        conflicts = []

        # 십성 개수 집계
        ten_god_counts = {}
        for pillar_name, gods in ten_gods.items():
            for god_name, count in gods.items():
                ten_god_counts[god_name] = ten_god_counts.get(god_name, 0) + count

        # 관살 vs 식상 충돌
        gwan_count = ten_god_counts.get("정관", 0) + ten_god_counts.get("편관", 0)
        sik_count = ten_god_counts.get("식신", 0) + ten_god_counts.get("상관", 0)

        if gwan_count >= 2 and sik_count >= 2:
            # 관살이 일간을 극하고, 식상이 관살을 극함 -> 충돌
            gwan_element = self.ELEMENT_DESTROYED_BY[day_element]  # 관살의 오행
            sik_element = self.ELEMENT_GENERATION[day_element]  # 식상의 오행

            conflicts.append({
                "type": "관살vs식상",
                "element1": gwan_element,
                "element2": sik_element,
                "severity": gwan_count + sik_count,
                "description": "관살과 식상이 충돌하고 있습니다"
            })

        # 재성 vs 인성 충돌
        jae_count = ten_god_counts.get("정재", 0) + ten_god_counts.get("편재", 0)
        in_count = ten_god_counts.get("정인", 0) + ten_god_counts.get("편인", 0)

        if jae_count >= 2 and in_count >= 2:
            jae_element = self.ELEMENT_DESTRUCTION[day_element]  # 재성의 오행
            in_element = self._get_supporting_element(day_element)  # 인성의 오행

            conflicts.append({
                "type": "재성vs인성",
                "element1": jae_element,
                "element2": in_element,
                "severity": jae_count + in_count,
                "description": "재성과 인성이 충돌하고 있습니다"
            })

        return conflicts

    def _get_mediator_element(self, element1: str, element2: str) -> str:
        """
        두 오행 사이를 중재하는 오행 찾기

        상생 순서: 목 -> 화 -> 토 -> 금 -> 수
        element1 -> 중재자 -> element2
        """
        # element1이 생하는 오행
        child1 = self.ELEMENT_GENERATION.get(element1)

        # element2를 생하는 오행
        parent2 = self._get_supporting_element(element2)

        # 같으면 그것이 중재자
        if child1 == parent2:
            return child1

        # 아니면 element1이 생하는 것을 우선
        return child1

    def _determine_byungyak_yongsin(self, day_element: str, element_counts: Dict,
                                    ten_gods: Dict, element_strength: int) -> Optional[Dict]:
        """
        병약용신 결정

        병(病): 사주의 문제점
        약(藥): 그 문제를 해결하는 용신
        """
        # 십성 개수 집계
        ten_god_counts = {}
        for pillar_name, gods in ten_gods.items():
            for god_name, count in gods.items():
                ten_god_counts[god_name] = ten_god_counts.get(god_name, 0) + count

        diseases = []

        # 병 1: 상관견관 (傷官見官)
        if ten_god_counts.get("상관", 0) > 0 and ten_god_counts.get("정관", 0) > 0:
            diseases.append({
                "병": "상관견관",
                "description": "상관이 정관을 극함",
                "약": "재성",  # 재성이 상관을 설기하고 관을 생함
                "severity": "높음"
            })

        # 병 2: 편인탈식 (偏印奪食)
        if ten_god_counts.get("편인", 0) > 0 and ten_god_counts.get("식신", 0) > 0:
            diseases.append({
                "병": "편인탈식",
                "description": "편인이 식신을 극함",
                "약": "재성",  # 재성이 편인을 극함
                "severity": "매우높음"
            })

        # 병 3: 비겁탈재 (比劫奪財)
        bigup_count = ten_god_counts.get("비견", 0) + ten_god_counts.get("겁재", 0)
        jae_count = ten_god_counts.get("정재", 0) + ten_god_counts.get("편재", 0)

        if bigup_count >= 3 and jae_count > 0:
            diseases.append({
                "병": "비겁탈재",
                "description": "비겁이 재성을 탈취",
                "약": "관살",  # 관살이 비겁을 제어
                "severity": "중간"
            })

        # 병 4: 재다신약 (財多身弱)
        if jae_count >= 3 and element_strength < 50:
            diseases.append({
                "병": "재다신약",
                "description": "재성이 많으나 일간이 약함",
                "약": "비겁",  # 비겁이 일간을 돕고 재를 제어
                "severity": "높음"
            })

        # 가장 심각한 병 선택
        if not diseases:
            return None

        most_severe = max(diseases, key=lambda x:
            {"매우높음": 4, "높음": 3, "중간": 2, "낮음": 1}.get(x["severity"], 0)
        )

        return most_severe

    def _determine_jeonwang_yongsin(self, day_element: str, element_strength: int,
                                    element_counts: Dict) -> Optional[str]:
        """
        전왕용신 결정

        일간이 너무 강하면 종세(從勢)하여 그 기세를 따름
        """
        # 태왕 (150+) 또는 일간 오행이 50% 이상
        total = sum(element_counts.values())
        if total == 0:
            return None

        day_element_ratio = element_counts.get(day_element, 0) / total

        if element_strength >= 150 or day_element_ratio >= 0.6:
            # 전왕 - 그 기세를 따라 더욱 강화
            # 일간을 생하는 것이 아니라, 일간이 생하는 것을 용신으로
            return self.ELEMENT_GENERATION[day_element]

        return None

    def _综合_all_yongsin(self, yeobu: Optional[str], johu: Optional[str],
                         tonggwan: Optional[str], byungyak: Optional[Dict],
                         jeonwang: Optional[str], element_strength: int) -> Tuple[str, Optional[str], str]:
        """
        모든 용신을 종합 판단

        Returns:
            (주용신, 보용신, 용신유형)
        """
        # 우선순위
        # 1. 병약용신 (가장 급함)
        if byungyak:
            # 약을 오행으로 변환
            yak_element_map = {
                "재성": None,  # 문맥에 따라 다름
                "관살": None,
                "비겁": None,
                "식상": None,
                "인성": None
            }
            # 간단하게 처리 (실제로는 더 복잡)
            return yeobu or johu or "목", None, "병약용신"

        # 2. 전왕용신 (종격 상황)
        if jeonwang:
            return jeonwang, None, "전왕용신"

        # 3. 통관용신 (충돌 해결)
        if tonggwan:
            return tonggwan, yeobu or johu, "통관용신"

        # 4. 조후용신 (계절 조절)
        if johu and yeobu == johu:
            return johu, None, "조후용신+억부용신"
        elif johu:
            return johu, yeobu, "조후용신"

        # 5. 억부용신 (기본)
        if yeobu:
            return yeobu, None, "억부용신"

        # 6. 기본값
        return "목", None, "일반용신"

    def _get_supporting_element(self, element: str) -> str:
        """오행을 생하는 오행"""
        for parent, child in self.ELEMENT_GENERATION.items():
            if child == element:
                return parent
        return element

    def _determine_heesin(self, yongsin: str) -> str:
        """희신 - 용신을 돕는 오행"""
        return self._get_supporting_element(yongsin)

    def _determine_gisin(self, yongsin: str) -> str:
        """기신 - 용신을 극하는 오행"""
        return self.ELEMENT_DESTROYED_BY.get(yongsin, "")

    def _get_comprehensive_reason(self, primary: str, yeobu: Optional[str],
                                  johu: Optional[str], tonggwan: Optional[str],
                                  byungyak: Optional[Dict], jeonwang: Optional[str]) -> str:
        """종합 용신 선정 이유"""
        reasons = []

        if byungyak and primary:
            reasons.append(f"{byungyak['병']}의 병을 치료하기 위해")

        if jeonwang and primary == jeonwang:
            reasons.append("일간이 극강하여 그 기세를 따르기 위해")

        if tonggwan and primary == tonggwan:
            reasons.append("충돌하는 오행을 중재하기 위해")

        if johu and primary == johu:
            reasons.append("계절의 한열을 조절하기 위해")

        if yeobu and primary == yeobu:
            reasons.append("일간의 강약을 조절하기 위해")

        return ", ".join(reasons) if reasons else "사주 균형을 위해"

    def _interpret_yongsin(self, primary: str, secondary: Optional[str],
                          yongsin_type: str, day_element: str) -> str:
        """용신 해석"""
        type_desc = {
            "억부용신": "일간의 강약을 조절하는",
            "조후용신": "계절의 한열을 조절하는",
            "통관용신": "충돌을 중재하는",
            "병약용신": "사주의 병을 치료하는",
            "전왕용신": "극강한 기세를 따르는",
            "조후용신+억부용신": "강약과 한열을 모두 조절하는",
            "일반용신": "균형을 맞추는"
        }

        interpretation = f"{type_desc.get(yongsin_type, '')} {primary} 오행이 가장 중요합니다. "

        if secondary:
            interpretation += f"{secondary} 오행도 함께 보완하면 좋습니다. "

        element_names = {"목": "나무/목재", "화": "불/열/빛", "토": "흙/대지", "금": "금속/광물", "수": "물"}
        interpretation += f"\n\n{element_names.get(primary, primary)}과 관련된 색상, 방향, 직업이 유리합니다."

        return interpretation

    def _get_recommendations(self, yongsin: str, heesin: str, gisin: str) -> Dict:
        """용신 기반 추천사항"""
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
