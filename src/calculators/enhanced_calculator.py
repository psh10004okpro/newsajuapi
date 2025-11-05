"""
향상된 사주 계산기 (Enhanced Calculator)

지지 장간을 고려한 정밀 계산
"""

from typing import Dict, List
from src.data.hidden_stems import (
    get_hidden_stems,
    calculate_stem_power_in_branch,
    get_branch_seasonal_strength
)


class EnhancedSajuCalculator:
    """지지 장간을 고려한 향상된 계산기"""

    def calculate_precise_ten_gods(self,
                                   day_master: str,
                                   pillars: List,
                                   element_map: Dict) -> Dict:
        """
        지지 장간을 고려한 정밀 십성 계산

        기존 방식: 천간 4개 + 지지 4개 (지지는 본기만)
        개선 방식: 천간 4개 + 지지 장간 전체

        Returns:
            {
                "천간십성": {...},  # 천간의 십성
                "지지십성": {...},  # 지지 본기의 십성
                "장간십성": {...},  # 모든 장간의 십성 (가중치 적용)
                "종합십성": {...}   # 최종 십성 분포
            }
        """
        from src.calculators.saju_calculator import SajuCalculator

        calculator = SajuCalculator()

        # 1. 천간 십성 (기존과 동일)
        stem_ten_gods = {}
        for pillar in pillars:
            stem = pillar.heavenly_stem
            if stem == day_master:
                continue

            ten_god = self._get_ten_god(
                day_master, stem,
                element_map, calculator.TEN_GODS_MAP
            )
            stem_ten_gods[ten_god] = stem_ten_gods.get(ten_god, 0) + 1

        # 2. 지지 장간 십성 (개선!)
        hidden_ten_gods = {}
        month_branch = pillars[1].earthly_branch if len(pillars) > 1 else None

        for idx, pillar in enumerate(pillars):
            branch = pillar.earthly_branch
            is_month = (branch == month_branch)

            # 지지 안의 모든 장간 확인
            hidden_info = get_hidden_stems(branch)

            # 본기
            main_stem = hidden_info["본기"]
            if main_stem and main_stem != day_master:
                ten_god = self._get_ten_god(
                    day_master, main_stem,
                    element_map, calculator.TEN_GODS_MAP
                )
                power = calculate_stem_power_in_branch(main_stem, branch, is_month)
                weight = power / 100.0  # 0.0 ~ 1.5

                hidden_ten_gods[ten_god] = hidden_ten_gods.get(ten_god, 0) + weight

            # 중기
            for mid_stem in hidden_info["중기"]:
                if mid_stem and mid_stem != day_master:
                    ten_god = self._get_ten_god(
                        day_master, mid_stem,
                        element_map, calculator.TEN_GODS_MAP
                    )
                    power = calculate_stem_power_in_branch(mid_stem, branch, is_month)
                    weight = power / 100.0

                    hidden_ten_gods[ten_god] = hidden_ten_gods.get(ten_god, 0) + weight

            # 여기
            for extra_stem in hidden_info["여기"]:
                if extra_stem and extra_stem != day_master:
                    ten_god = self._get_ten_god(
                        day_master, extra_stem,
                        element_map, calculator.TEN_GODS_MAP
                    )
                    power = calculate_stem_power_in_branch(extra_stem, branch, is_month)
                    weight = power / 100.0

                    hidden_ten_gods[ten_god] = hidden_ten_gods.get(ten_god, 0) + weight

        # 3. 종합 (천간 + 장간)
        total_ten_gods = {}
        all_ten_god_names = set(list(stem_ten_gods.keys()) + list(hidden_ten_gods.keys()))

        for ten_god in all_ten_god_names:
            total_ten_gods[ten_god] = (
                stem_ten_gods.get(ten_god, 0) +
                hidden_ten_gods.get(ten_god, 0.0)
            )

        return {
            "천간십성": stem_ten_gods,
            "장간십성": hidden_ten_gods,
            "종합십성": total_ten_gods,
            "설명": "장간을 고려한 정밀 십성 계산"
        }

    def calculate_precise_element_strength(self,
                                          day_master: str,
                                          pillars: List,
                                          month: int,
                                          element_map: Dict) -> Dict:
        """
        지지 장간과 계절을 고려한 정밀 오행 강약 계산

        Returns:
            {
                "일간오행": "목",
                "강도": 85,
                "등급": "왕",
                "득령": True,
                "통근": ["인", "묘"],
                "투간": 2,
                "분석": "..."
            }
        """
        day_element = element_map.get(day_master)
        month_branch = pillars[1].earthly_branch if len(pillars) > 1 else None

        strength = 0
        analysis_details = []

        # 1. 득령(得令) - 월령에서 왕한가?
        month_strength = get_branch_seasonal_strength(month_branch, month)

        if month_strength == "왕":
            strength += 50
            analysis_details.append(f"득령(得令): 월지 {month_branch}에서 왕함 (+50)")
        elif month_strength == "상":
            strength += 30
            analysis_details.append(f"득령: 월지에서 상함 (+30)")
        elif month_strength == "여기":
            strength += 20
            analysis_details.append(f"득령: 월지에서 여기 (+20)")
        else:
            analysis_details.append(f"실령(失令): 월지에서 약함 (+0)")

        # 2. 통근(通根) - 지지에 뿌리가 있는가?
        rooted_branches = []
        for idx, pillar in enumerate(pillars):
            branch = pillar.earthly_branch
            hidden_info = get_hidden_stems(branch)

            # 일간이 지지 장간에 있는지 확인
            if day_master in hidden_info["all"]:
                power = calculate_stem_power_in_branch(
                    day_master, branch,
                    is_month_branch=(branch == month_branch)
                )

                strength += power // 5  # 20~30점
                rooted_branches.append(branch)

                if branch == month_branch:
                    analysis_details.append(f"통근: 월지 {branch}에 강한 뿌리 (+{power//5})")
                else:
                    position = ["년지", "월지", "일지", "시지"][idx]
                    analysis_details.append(f"통근: {position} {branch}에 뿌리 (+{power//5})")

        # 3. 투간(透干) - 천간에 드러났는가?
        transparent_count = sum(
            1 for p in pillars
            if p.heavenly_stem == day_master
        )
        if transparent_count > 1:  # 일간 제외
            trans_strength = (transparent_count - 1) * 15
            strength += trans_strength
            analysis_details.append(f"투간: 천간에 {transparent_count-1}개 투출 (+{trans_strength})")

        # 4. 생조(生助) - 도움받는 오행
        supporting_elements = self._get_supporting_elements(day_element)

        for pillar in pillars:
            # 천간 생조
            stem_element = element_map.get(pillar.heavenly_stem)
            if stem_element in supporting_elements:
                strength += 10
                analysis_details.append(f"생조: {pillar.heavenly_stem}({stem_element}) (+10)")

        # 강약 등급 판단
        if strength >= 150:
            grade = "태왕(太旺)"
        elif strength >= 100:
            grade = "왕(旺)"
        elif strength >= 70:
            grade = "중화(中和)"
        elif strength >= 40:
            grade = "약(弱)"
        else:
            grade = "태약(太弱)"

        return {
            "일간": day_master,
            "일간오행": day_element,
            "강도점수": strength,
            "강약등급": grade,
            "득령": month_strength in ["왕", "상"],
            "통근지지": rooted_branches,
            "투간수": transparent_count - 1,
            "분석내역": analysis_details,
            "해석": f"{day_master}({day_element}) 일간은 {grade} 상태입니다. "
                   f"강도 {strength}점으로 "
                   f"{'매우 강한' if strength >= 100 else '약한' if strength < 70 else '적당한'} 편입니다."
        }

    def _get_ten_god(self, day_master: str, target: str,
                     element_map: Dict, ten_gods_map: Dict) -> str:
        """십성 판단"""
        day_element = element_map.get(day_master)
        target_element = element_map.get(target)

        if not day_element or not target_element:
            return None

        # 음양 판단
        yang_items = ["갑", "병", "무", "경", "임"]
        is_same_yin_yang = (day_master in yang_items) == (target in yang_items)

        yin_yang = "same" if is_same_yin_yang else "diff"

        return ten_gods_map.get((day_element, target_element, yin_yang))

    def _get_supporting_elements(self, element: str) -> List[str]:
        """오행을 생하거나 돕는 오행들"""
        # 나와 같은 오행 (비겁)
        same = [element]

        # 나를 생하는 오행 (인성)
        generation = {
            "목": "수",
            "화": "목",
            "토": "화",
            "금": "토",
            "수": "금"
        }
        parent = generation.get(element)

        return same + ([parent] if parent else [])


# 사용 예시
"""
enhanced_calc = EnhancedSajuCalculator()

# 정밀 십성 계산
precise_ten_gods = enhanced_calc.calculate_precise_ten_gods(
    day_master="병",
    pillars=[year_pillar, month_pillar, day_pillar, hour_pillar],
    element_map=SajuCalculator.ELEMENT_MAP
)

print("기존 방식:", precise_ten_gods["천간십성"])
print("개선 방식:", precise_ten_gods["종합십성"])

# 정밀 강약 계산
strength_analysis = enhanced_calc.calculate_precise_element_strength(
    day_master="병",
    pillars=[year_pillar, month_pillar, day_pillar, hour_pillar],
    month=5,
    element_map=SajuCalculator.ELEMENT_MAP
)

print("강약 분석:", strength_analysis["해석"])
print("상세 내역:", strength_analysis["분석내역"])
"""
