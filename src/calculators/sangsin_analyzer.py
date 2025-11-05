"""
상신(相神) 분석기

용신을 돕는 상신 찾기
Phase 3 정확도 개선
"""

from typing import Dict, List, Optional


class SangsinAnalyzer:
    """상신(相神) 분석기"""

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

    def __init__(self, element_map: Dict):
        """
        Args:
            element_map: 천간/지지의 오행 매핑
        """
        self.element_map = element_map

    def analyze_sangsin(self, yongsin: str, gisin: str,
                       five_elements: Dict, ten_gods: Dict) -> Dict:
        """
        상신 분석

        상신의 역할:
        1. 용신을 생하는 오행 (生用神)
        2. 기신을 제어하는 오행 (制忌神)
        3. 용신과 협력하는 오행 (輔用神)

        Args:
            yongsin: 용신 오행
            gisin: 기신 오행
            five_elements: 오행 분포
            ten_gods: 십성 정보

        Returns:
            상신 분석 결과
        """
        # 상신 후보들
        candidates = []

        # 1. 용신을 생하는 오행 (가장 중요)
        yongsin_supporter = self._get_supporting_element(yongsin)
        if yongsin_supporter:
            candidates.append({
                "element": yongsin_supporter,
                "role": "생용신(生用神)",
                "importance": "매우 높음",
                "description": f"{yongsin_supporter}가 {yongsin}(용신)을 생함",
                "mechanism": f"{yongsin_supporter}생{yongsin}",
                "priority": 1,
                "strength": self._calculate_element_presence(yongsin_supporter, five_elements)
            })

        # 2. 기신을 제어하는 오행
        gisin_controller = self.ELEMENT_DESTRUCTION.get(gisin)
        if gisin_controller and gisin_controller != yongsin:
            # 기신을 극하는 오행은 간접적으로 용신을 돕는다
            candidates.append({
                "element": gisin_controller,
                "role": "제기신(制忌神)",
                "importance": "높음",
                "description": f"{gisin_controller}가 {gisin}(기신)을 극하여 용신을 보호",
                "mechanism": f"{gisin_controller}극{gisin}",
                "priority": 2,
                "strength": self._calculate_element_presence(gisin_controller, five_elements)
            })

        # 3. 용신과 협력하는 오행 (용신이 생하는 오행)
        yongsin_child = self.ELEMENT_GENERATION.get(yongsin)
        if yongsin_child and yongsin_child != yongsin:
            candidates.append({
                "element": yongsin_child,
                "role": "설기용신(洩氣用神)",
                "importance": "중간",
                "description": f"{yongsin}(용신)이 {yongsin_child}를 생하여 설기",
                "mechanism": f"{yongsin}생{yongsin_child}",
                "priority": 3,
                "strength": self._calculate_element_presence(yongsin_child, five_elements)
            })

        # 4. 우선순위 정렬 및 주/부 상신 결정
        candidates.sort(key=lambda x: (x["priority"], -x["strength"]))

        # 주상신 (主相神)
        primary_sangsin = candidates[0] if candidates else None

        # 부상신 (副相神)
        secondary_sangsin = candidates[1] if len(candidates) > 1 else None

        # 모든 상신 후보
        all_candidates = candidates

        return {
            "primary_sangsin": primary_sangsin,
            "secondary_sangsin": secondary_sangsin,
            "all_candidates": all_candidates,
            "analysis": {
                "용신": yongsin,
                "기신": gisin,
                "상신_개수": len(candidates),
                "권장사항": self._get_recommendations(primary_sangsin, secondary_sangsin, yongsin)
            },
            "interpretation": self._interpret_sangsin(
                primary_sangsin, secondary_sangsin, yongsin, gisin
            ),
            "practical_advice": self._get_practical_advice(
                primary_sangsin, secondary_sangsin, yongsin
            )
        }

    def _get_supporting_element(self, element: str) -> Optional[str]:
        """오행을 생하는 오행 찾기"""
        for parent, child in self.ELEMENT_GENERATION.items():
            if child == element:
                return parent
        return None

    def _calculate_element_presence(self, element: str, five_elements: Dict) -> int:
        """사주에서 오행의 존재 강도 계산"""
        element_map_reverse = {
            "목": "wood",
            "화": "fire",
            "토": "earth",
            "금": "metal",
            "수": "water"
        }

        key = element_map_reverse.get(element, "")
        return five_elements.get(key, 0)

    def _get_recommendations(self, primary: Optional[Dict],
                           secondary: Optional[Dict], yongsin: str) -> List[str]:
        """상신 기반 권장사항"""
        recommendations = []

        if primary:
            recommendations.append(
                f"{primary['element']} 오행을 강화하면 {yongsin}(용신)이 더욱 힘을 받습니다"
            )
            recommendations.append(
                f"{primary['role']}: {primary['description']}"
            )

        if secondary:
            recommendations.append(
                f"보조적으로 {secondary['element']} 오행도 활용하면 좋습니다"
            )

        return recommendations

    def _interpret_sangsin(self, primary: Optional[Dict], secondary: Optional[Dict],
                          yongsin: str, gisin: str) -> str:
        """상신 해석"""
        if not primary:
            return f"{yongsin}(용신)을 도울 상신을 찾을 수 없습니다."

        interpretation = f"주상신(主相神)은 {primary['element']} 오행입니다.\n"
        interpretation += f"{primary['description']}.\n\n"

        if secondary:
            interpretation += f"부상신(副相神)은 {secondary['element']} 오행입니다.\n"
            interpretation += f"{secondary['description']}.\n\n"

        interpretation += f"용신({yongsin})과 상신({primary['element']}"
        if secondary:
            interpretation += f", {secondary['element']}"
        interpretation += ")을 함께 활용하면 사주의 균형이 더욱 좋아집니다."

        return interpretation

    def _get_practical_advice(self, primary: Optional[Dict],
                             secondary: Optional[Dict], yongsin: str) -> Dict:
        """실용적 조언"""
        if not primary:
            return {}

        # 오행별 속성
        element_properties = {
            "목": {
                "colors": ["녹색", "청록색", "연두색"],
                "directions": ["동쪽"],
                "numbers": [3, 8],
                "activities": ["산책", "등산", "원예", "독서"],
                "foods": ["채소", "과일", "신맛 음식"]
            },
            "화": {
                "colors": ["빨강", "주황", "분홍", "보라"],
                "directions": ["남쪽"],
                "numbers": [2, 7],
                "activities": ["운동", "사교", "강연", "예술 활동"],
                "foods": ["매운 음식", "붉은 고기", "쓴맛 음식"]
            },
            "토": {
                "colors": ["노랑", "갈색", "베이지"],
                "directions": ["중앙", "남서", "동북"],
                "numbers": [5, 10],
                "activities": ["명상", "요가", "정리정돈", "봉사"],
                "foods": ["곡물", "단맛 음식", "건강식"]
            },
            "금": {
                "colors": ["흰색", "금색", "은색", "회색"],
                "directions": ["서쪽"],
                "numbers": [4, 9],
                "activities": ["정리", "계획", "사업", "재정 관리"],
                "foods": ["견과류", "매운맛 음식", "흰색 음식"]
            },
            "수": {
                "colors": ["검정", "파랑", "남색"],
                "directions": ["북쪽"],
                "numbers": [1, 6],
                "activities": ["수영", "목욕", "여행", "사색"],
                "foods": ["해산물", "짠맛 음식", "검은색 음식"]
            }
        }

        primary_props = element_properties.get(primary["element"], {})
        advice = {
            "용신_상신_조합": f"{yongsin} + {primary['element']}",
            "추천_색상": primary_props.get("colors", []),
            "추천_방향": primary_props.get("directions", []),
            "행운의_숫자": primary_props.get("numbers", []),
            "좋은_활동": primary_props.get("activities", []),
            "유리한_음식": primary_props.get("foods", []),
            "시너지_효과": f"{primary['element']}(상신)이 {yongsin}(용신)을 도와 시너지 발생"
        }

        # 부상신 정보 추가
        if secondary:
            secondary_props = element_properties.get(secondary["element"], {})
            advice["보조_색상"] = secondary_props.get("colors", [])
            advice["보조_방향"] = secondary_props.get("directions", [])

        return advice

    def analyze_sangsin_in_saju(self, yongsin_info: Dict, pillars: List,
                               element_map: Dict) -> Dict:
        """
        사주 내에서 상신 찾기

        Args:
            yongsin_info: 용신 분석 결과
            pillars: 사주 4주
            element_map: 오행 매핑

        Returns:
            사주 내 상신 존재 여부 및 위치
        """
        primary_yongsin_element = yongsin_info.get("primary_yongsin", {}).get("element")
        gisin_element = yongsin_info.get("gisin", {}).get("element")

        if not primary_yongsin_element:
            return {"error": "용신 정보가 없습니다"}

        # 상신 오행 계산
        sangsin_element = self._get_supporting_element(primary_yongsin_element)

        if not sangsin_element:
            return {"error": "상신을 찾을 수 없습니다"}

        # 사주에서 상신 찾기
        sangsin_locations = []
        position_names = ["년주", "월주", "일주", "시주"]

        for idx, pillar in enumerate(pillars):
            # 천간 확인
            stem_element = element_map.get(pillar.heavenly_stem)
            if stem_element == sangsin_element:
                sangsin_locations.append({
                    "position": position_names[idx],
                    "type": "천간",
                    "item": pillar.heavenly_stem,
                    "strength": "강함"
                })

            # 지지 확인
            branch_element = element_map.get(pillar.earthly_branch)
            if branch_element == sangsin_element:
                sangsin_locations.append({
                    "position": position_names[idx],
                    "type": "지지",
                    "item": pillar.earthly_branch,
                    "strength": "중간"
                })

        return {
            "상신_오행": sangsin_element,
            "용신_오행": primary_yongsin_element,
            "사주내_존재": len(sangsin_locations) > 0,
            "상신_위치": sangsin_locations,
            "총_개수": len(sangsin_locations),
            "평가": self._evaluate_sangsin_presence(sangsin_locations, sangsin_element)
        }

    def _evaluate_sangsin_presence(self, locations: List[Dict], sangsin_element: str) -> str:
        """상신 존재 평가"""
        count = len(locations)

        if count == 0:
            return f"{sangsin_element}(상신)이 사주에 없어 용신의 힘이 약할 수 있습니다. 대운이나 세운에서 보충이 필요합니다."
        elif count == 1:
            return f"{sangsin_element}(상신)이 사주에 1개 있어 적당합니다. 용신을 적절히 도와줍니다."
        elif count == 2:
            return f"{sangsin_element}(상신)이 사주에 2개 있어 좋습니다. 용신을 잘 도와줍니다."
        else:
            return f"{sangsin_element}(상신)이 사주에 {count}개나 있어 매우 좋습니다. 용신이 강한 힘을 받습니다."


def get_sangsin_analyzer(element_map: Dict):
    """상신 분석기 인스턴스 반환"""
    return SangsinAnalyzer(element_map)
