"""
격국(格局) 분석기

격국은 사주의 전체적인 구조와 패턴을 판단
월지와 일간을 중심으로 천간에 투출된 십성으로 판단
"""

from typing import Dict, List, Tuple, Optional


class GyeokgukAnalyzer:
    """격국 분석기"""

    # 격국 설명
    GYEOKGUK_DESC = {
        "정관격": {
            "name": "正官格",
            "description": "정관이 월지 또는 천간에 투출",
            "characteristics": ["정직함", "책임감", "안정 추구", "사회적 명예"],
            "career": ["공무원", "관리직", "법조인", "교육자"],
            "strength": "상",
            "fortune_type": "안정형"
        },
        "편관격": {
            "name": "偏官格 (七殺格)",
            "description": "편관(칠살)이 월지 또는 천간에 투출",
            "characteristics": ["강한 추진력", "도전적", "카리스마", "결단력"],
            "career": ["군인", "경찰", "사업가", "정치인"],
            "strength": "상",
            "fortune_type": "역동형"
        },
        "정재격": {
            "name": "正財格",
            "description": "정재가 월지 또는 천간에 투출",
            "characteristics": ["성실함", "검소함", "계획적", "축재"],
            "career": ["금융", "회계", "부동산", "경영"],
            "strength": "중상",
            "fortune_type": "재물형"
        },
        "편재격": {
            "name": "偏財格",
            "description": "편재가 월지 또는 천간에 투출",
            "characteristics": ["활동적", "사교적", "다재다능", "변화 추구"],
            "career": ["영업", "무역", "서비스업", "투자"],
            "strength": "중상",
            "fortune_type": "활동형"
        },
        "정인격": {
            "name": "正印格",
            "description": "정인이 월지 또는 천간에 투출",
            "characteristics": ["학문적", "온화함", "인자함", "보수적"],
            "career": ["교육", "연구", "문화", "종교"],
            "strength": "중",
            "fortune_type": "학문형"
        },
        "편인격": {
            "name": "偏印格",
            "description": "편인이 월지 또는 천간에 투출",
            "characteristics": ["독창적", "직관적", "신비주의", "변덕"],
            "career": ["예술", "철학", "심리학", "대체의학"],
            "strength": "중",
            "fortune_type": "창작형"
        },
        "식신격": {
            "name": "食神格",
            "description": "식신이 월지 또는 천간에 투출",
            "characteristics": ["낙천적", "여유로움", "재능", "복록"],
            "career": ["요식업", "문화", "예술", "서비스"],
            "strength": "중상",
            "fortune_type": "복록형"
        },
        "상관격": {
            "name": "傷官格",
            "description": "상관이 월지 또는 천간에 투출",
            "characteristics": ["재능", "표현력", "비판적", "창의적"],
            "career": ["예술", "방송", "작가", "디자이너"],
            "strength": "중",
            "fortune_type": "재능형"
        },
        "건록격": {
            "name": "建祿格",
            "description": "월지가 일간의 건록지",
            "characteristics": ["독립심", "자립", "강한 자아", "실행력"],
            "career": ["자영업", "전문직", "기술직"],
            "strength": "상",
            "fortune_type": "자립형"
        },
        "양인격": {
            "name": "羊刃格",
            "description": "월지가 일간의 양인",
            "characteristics": ["강함", "과격", "승부욕", "극단적"],
            "career": ["무술", "군인", "외과의", "운동선수"],
            "strength": "상",
            "fortune_type": "강인형"
        },
        "종격": {
            "name": "從格",
            "description": "일간이 너무 약해 다른 오행을 따름",
            "characteristics": ["유연함", "적응력", "협조적", "의존적"],
            "career": ["협력", "보조", "서비스"],
            "strength": "특수",
            "fortune_type": "순응형"
        },
        "일반격": {
            "name": "一般格",
            "description": "특정 격국에 해당하지 않는 일반적 사주",
            "characteristics": ["평범함", "균형", "다양성"],
            "career": ["다양"],
            "strength": "중",
            "fortune_type": "평범형"
        }
    }

    # 건록지 매핑 (일간이 제왕인 지지)
    GEOLLOK_MAP = {
        "갑": "인", "을": "묘",
        "병": "사", "정": "오",
        "무": "사", "기": "오",
        "경": "신", "신": "유",
        "임": "해", "계": "자"
    }

    # 양인 매핑
    YANGIN_MAP = {
        "갑": "묘", "을": "인",
        "병": "오", "정": "사",
        "무": "오", "기": "사",
        "경": "유", "신": "신",
        "임": "자", "계": "해"
    }

    def __init__(self, saju_calculator):
        """
        Args:
            saju_calculator: SajuCalculator 인스턴스 (십성 계산에 필요)
        """
        self.saju_calculator = saju_calculator

    def analyze_gyeokguk(self, day_master: str, month_branch: str,
                         year_stem: str, month_stem: str, day_stem: str, hour_stem: str,
                         ten_gods: Dict) -> Dict:
        """
        격국 분석

        Args:
            day_master: 일간
            month_branch: 월지
            year_stem: 년간
            month_stem: 월간
            day_stem: 일간 (동일)
            hour_stem: 시간
            ten_gods: 십성 정보

        Returns:
            격국 분석 결과
        """
        # 1. 건록격/양인격 먼저 체크
        if month_branch == self.GEOLLOK_MAP.get(day_master):
            gyeokguk_type = "건록격"
        elif month_branch == self.YANGIN_MAP.get(day_master):
            gyeokguk_type = "양인격"
        else:
            # 2. 월지를 통한 십성 확인
            month_branch_ten_god = self._get_ten_god_for_branch(day_master, month_branch)

            # 3. 천간에 투출된 십성 확인
            transparent_ten_gods = self._get_transparent_ten_gods(
                day_master, year_stem, month_stem, hour_stem
            )

            # 4. 격국 결정
            gyeokguk_type = self._determine_gyeokguk(
                month_branch_ten_god, transparent_ten_gods, ten_gods
            )

        # 5. 격국 강도 평가
        strength = self._evaluate_gyeokguk_strength(gyeokguk_type, ten_gods)

        # 6. 격국 정보 반환
        gyeokguk_info = self.GYEOKGUK_DESC.get(gyeokguk_type, self.GYEOKGUK_DESC["일반격"])

        return {
            "type": gyeokguk_type,
            "name": gyeokguk_info["name"],
            "description": gyeokguk_info["description"],
            "characteristics": gyeokguk_info["characteristics"],
            "suitable_careers": gyeokguk_info["career"],
            "strength": strength,
            "fortune_type": gyeokguk_info["fortune_type"],
            "interpretation": self._interpret_gyeokguk(gyeokguk_type, strength)
        }

    def _get_ten_god_for_branch(self, day_master: str, branch: str) -> Optional[str]:
        """지지의 십성 확인"""
        # 지지의 본기(本氣) 오행으로 십성 판단
        day_element = self.saju_calculator.ELEMENT_MAP.get(day_master)
        branch_element = self.saju_calculator.ELEMENT_MAP.get(branch)

        if not day_element or not branch_element:
            return None

        # 음양 판단
        yin_yang = "same" if self._is_same_yin_yang(day_master, branch) else "diff"

        # 십성 결정
        ten_god = self.saju_calculator.TEN_GODS_MAP.get((day_element, branch_element, yin_yang))
        return ten_god

    def _is_same_yin_yang(self, item1: str, item2: str) -> bool:
        """음양이 같은지 판단"""
        yang_items = ["갑", "병", "무", "경", "임", "자", "인", "진", "오", "신", "술"]
        yin_items = ["을", "정", "기", "신", "계", "축", "묘", "사", "미", "유", "해"]

        item1_yang = item1 in yang_items
        item2_yang = item2 in yang_items

        return item1_yang == item2_yang

    def _get_transparent_ten_gods(self, day_master: str,
                                   year_stem: str, month_stem: str, hour_stem: str) -> List[str]:
        """천간에 투출된 십성들"""
        transparent = []
        stems = [year_stem, month_stem, hour_stem]  # 일간 제외

        day_element = self.saju_calculator.ELEMENT_MAP.get(day_master)

        for stem in stems:
            if stem == day_master:
                continue

            stem_element = self.saju_calculator.ELEMENT_MAP.get(stem)
            if not stem_element:
                continue

            yin_yang = "same" if self._is_same_yin_yang(day_master, stem) else "diff"
            ten_god = self.saju_calculator.TEN_GODS_MAP.get((day_element, stem_element, yin_yang))

            if ten_god:
                transparent.append(ten_god)

        return transparent

    def _determine_gyeokguk(self, month_ten_god: Optional[str],
                           transparent_ten_gods: List[str], ten_gods: Dict) -> str:
        """격국 결정"""
        # 월지의 십성이 있고, 천간에도 투출되면 해당 격국
        if month_ten_god and month_ten_god in transparent_ten_gods:
            if month_ten_god == "정관":
                return "정관격"
            elif month_ten_god == "편관":
                return "편관격"
            elif month_ten_god == "정재":
                return "정재격"
            elif month_ten_god == "편재":
                return "편재격"
            elif month_ten_god == "정인":
                return "정인격"
            elif month_ten_god == "편인":
                return "편인격"
            elif month_ten_god == "식신":
                return "식신격"
            elif month_ten_god == "상관":
                return "상관격"

        # 천간에 투출되지 않았지만 월지에 있으면 약한 격국
        if month_ten_god:
            if month_ten_god == "정관":
                return "정관격"
            elif month_ten_god == "편관":
                return "편관격"
            elif month_ten_god in ["정재", "편재"]:
                return "정재격" if month_ten_god == "정재" else "편재격"
            elif month_ten_god in ["식신", "상관"]:
                return "식신격" if month_ten_god == "식신" else "상관격"

        # 특정 격국에 해당하지 않으면 일반격
        return "일반격"

    def _evaluate_gyeokguk_strength(self, gyeokguk_type: str, ten_gods: Dict) -> str:
        """격국 강도 평가"""
        gyeokguk_info = self.GYEOKGUK_DESC.get(gyeokguk_type)
        base_strength = gyeokguk_info.get("strength", "중")

        # 십성 개수로 강도 조정
        # (실제로는 더 복잡한 판단이 필요하지만 간단하게 구현)

        return base_strength

    def _interpret_gyeokguk(self, gyeokguk_type: str, strength: str) -> str:
        """격국 해석"""
        gyeokguk_info = self.GYEOKGUK_DESC.get(gyeokguk_type, {})
        name = gyeokguk_info.get("name", "")
        desc = gyeokguk_info.get("description", "")

        if gyeokguk_type == "일반격":
            return "특정 격국에 해당하지 않는 일반적인 사주입니다. 균형잡힌 발전이 가능합니다."

        return f"{name}입니다. {desc} 강도는 '{strength}' 수준입니다."
