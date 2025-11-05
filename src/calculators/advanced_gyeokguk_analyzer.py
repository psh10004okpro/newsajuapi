"""
고급 격국(格局) 분석기

특수 격국, 종격 세부 구분, 파격 판단 등 고급 분석 기능 제공
Phase 2 정확도 개선
"""

from typing import Dict, List, Tuple, Optional


class AdvancedGyeokgukAnalyzer:
    """고급 격국 분석기"""

    # 특수 격국 설명
    SPECIAL_GYEOKGUK_DESC = {
        "염상격": {
            "name": "炎上格",
            "description": "화 오행이 극성하여 하늘로 타오르는 형국",
            "characteristics": ["열정적", "창조적", "카리스마", "급함", "직선적"],
            "career": ["예술", "연예", "정치", "홍보", "마케팅"],
            "condition": "여름생 + 병/정 일간 + 화 오행 왕성",
            "strength": "특수",
            "fortune_type": "화염형"
        },
        "곡직격": {
            "name": "曲直格",
            "description": "목 오행이 굽고 곧게 펴지는 형국",
            "characteristics": ["성장지향", "유연함", "인자함", "발전적", "진취적"],
            "career": ["교육", "문화", "출판", "IT", "벤처"],
            "condition": "봄생 + 갑/을 일간 + 목 오행 왕성",
            "strength": "특수",
            "fortune_type": "성장형"
        },
        "윤하격": {
            "name": "潤下格",
            "description": "수 오행이 아래로 흘러내리는 형국",
            "characteristics": ["지혜로움", "유동적", "적응력", "변화", "소통"],
            "career": ["무역", "유통", "외교", "해운", "IT"],
            "condition": "겨울생 + 임/계 일간 + 수 오행 왕성",
            "strength": "특수",
            "fortune_type": "유동형"
        },
        "가색격": {
            "name": "稼穡格",
            "description": "토 오행이 심고 거두는 형국",
            "characteristics": ["신뢰", "안정", "포용", "축적", "보수적"],
            "career": ["부동산", "건축", "농업", "금융", "관리"],
            "condition": "사계절 토월생 + 무/기 일간 + 토 오행 왕성",
            "strength": "특수",
            "fortune_type": "축적형"
        },
        "종혁격": {
            "name": "從革格",
            "description": "금 오행이 변화를 따르는 형국",
            "characteristics": ["결단력", "정의감", "원칙적", "냉철함", "변혁"],
            "career": ["법조", "군인", "경찰", "금융", "제조"],
            "condition": "가을생 + 경/신 일간 + 금 오행 왕성",
            "strength": "특수",
            "fortune_type": "변혁형"
        },
        "화기통명격": {
            "name": "火氣通明格",
            "description": "목생화로 화기가 통명하는 형국",
            "characteristics": ["총명함", "문명", "예술성", "따뜻함", "밝음"],
            "career": ["교육", "문화", "예술", "언론", "IT"],
            "condition": "봄생 + 병/정 일간 + 목 지원",
            "strength": "특수",
            "fortune_type": "통명형"
        }
    }

    # 종격 세부 유형 설명
    JONGGUK_TYPES_DESC = {
        "종강격": {
            "name": "從强格 (從比格)",
            "description": "비겁이 극왕하여 따름",
            "characteristics": ["강한 독립심", "자기중심적", "리더십", "고집"],
            "career": ["자영업", "경영", "독립사업"],
            "condition": "비겁이 사주의 70% 이상",
            "strength": "특수",
            "fortune_type": "독립형"
        },
        "종재격": {
            "name": "從財格",
            "description": "재성이 극왕하여 따름",
            "characteristics": ["물질중시", "실용적", "사교적", "활동적"],
            "career": ["무역", "영업", "금융", "투자"],
            "condition": "재성이 지배적 + 일간 태약",
            "strength": "특수",
            "fortune_type": "재물형"
        },
        "종살격": {
            "name": "從殺格 (從官格)",
            "description": "관살이 극왕하여 따름",
            "characteristics": ["권위추종", "조직적", "순응적", "책임감"],
            "career": ["공무원", "대기업", "군인", "관리직"],
            "condition": "관살이 지배적 + 일간 태약",
            "strength": "특수",
            "fortune_type": "귀속형"
        },
        "종식격": {
            "name": "從食格 (從兒格)",
            "description": "식상이 극왕하여 따름",
            "characteristics": ["재능발휘", "표현력", "창의성", "자유"],
            "career": ["예술", "연예", "작가", "디자이너"],
            "condition": "식상이 지배적 + 일간 태약",
            "strength": "특수",
            "fortune_type": "재능형"
        },
        "종왕격": {
            "name": "從旺格",
            "description": "왕성한 기운을 따름 (복합)",
            "characteristics": ["순응적", "유연함", "적응력", "변화"],
            "career": ["서비스", "협력업", "중개"],
            "condition": "여러 오행 왕성 + 일간 고립",
            "strength": "특수",
            "fortune_type": "순응형"
        }
    }

    # 파격 조건
    PAGUK_CONDITIONS = {
        "정관격": [
            {"factor": "상관", "name": "상관견관(傷官見官)", "severity": "높음",
             "description": "상관이 정관을 극함"},
            {"factor": "편인", "name": "편인탈식(偏印奪食)", "severity": "중간",
             "description": "편인이 식신을 극함"}
        ],
        "편관격": [
            {"factor": "식신", "name": "식신제살(食神制殺)", "severity": "낮음",
             "description": "식신이 편관을 제어 (오히려 좋음)", "beneficial": True}
        ],
        "정재격": [
            {"factor": "비겁", "name": "비겁탈재(比劫奪財)", "severity": "높음",
             "description": "비겁이 정재를 탈취"}
        ],
        "편재격": [
            {"factor": "비겁", "name": "비겁탈재(比劫奪財)", "severity": "중간",
             "description": "비겁이 편재를 탈취"}
        ],
        "정인격": [
            {"factor": "정재", "name": "재다신약(財多身弱)", "severity": "중간",
             "description": "재성이 인성을 극함"}
        ],
        "편인격": [
            {"factor": "편재", "name": "재다신약(財多身弱)", "severity": "중간",
             "description": "재성이 인성을 극함"}
        ],
        "식신격": [
            {"factor": "편인", "name": "편인탈식(偏印奪食)", "severity": "매우높음",
             "description": "편인이 식신을 극함 (가장 나쁜 파격)"}
        ],
        "상관격": [
            {"factor": "정관", "name": "상관견관(傷官見官)", "severity": "높음",
             "description": "상관과 정관의 충돌"}
        ]
    }

    def __init__(self, element_map: Dict):
        """
        Args:
            element_map: 천간/지지의 오행 매핑
        """
        self.element_map = element_map

    def analyze_special_gyeokguk(self, day_master: str, month_branch: str,
                                   pillars: List, five_elements: Dict,
                                   birth_month: int) -> Optional[Dict]:
        """
        특수 격국 분석

        Args:
            day_master: 일간
            month_branch: 월지
            pillars: 사주 4주 리스트
            five_elements: 오행 분포
            birth_month: 출생월 (1-12)

        Returns:
            특수 격국 정보 또는 None
        """
        day_element = self.element_map.get(day_master)

        # 오행 분포 통일된 형식으로 변환
        element_counts = {
            "목": five_elements.get("wood", 0),
            "화": five_elements.get("fire", 0),
            "토": five_elements.get("earth", 0),
            "금": five_elements.get("metal", 0),
            "수": five_elements.get("water", 0)
        }

        total_count = sum(element_counts.values())
        if total_count == 0:
            return None

        # 각 오행의 비율
        element_ratios = {k: v / total_count for k, v in element_counts.items()}

        # 1. 염상격 (炎上格) - 화 왕성
        if day_master in ["병", "정"] and birth_month in [4, 5, 6]:
            if element_ratios["화"] >= 0.5:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["염상격"].copy()
                gyeokguk_info["type"] = "염상격"
                gyeokguk_info["ratio"] = element_ratios["화"]
                return gyeokguk_info

        # 2. 곡직격 (曲直格) - 목 왕성
        if day_master in ["갑", "을"] and birth_month in [1, 2, 3]:
            if element_ratios["목"] >= 0.5:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["곡직격"].copy()
                gyeokguk_info["type"] = "곡직격"
                gyeokguk_info["ratio"] = element_ratios["목"]
                return gyeokguk_info

        # 3. 윤하격 (潤下格) - 수 왕성
        if day_master in ["임", "계"] and birth_month in [10, 11, 12]:
            if element_ratios["수"] >= 0.5:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["윤하격"].copy()
                gyeokguk_info["type"] = "윤하격"
                gyeokguk_info["ratio"] = element_ratios["수"]
                return gyeokguk_info

        # 4. 가색격 (稼穡格) - 토 왕성
        if day_master in ["무", "기"] and month_branch in ["축", "진", "미", "술"]:
            if element_ratios["토"] >= 0.5:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["가색격"].copy()
                gyeokguk_info["type"] = "가색격"
                gyeokguk_info["ratio"] = element_ratios["토"]
                return gyeokguk_info

        # 5. 종혁격 (從革格) - 금 왕성
        if day_master in ["경", "신"] and birth_month in [7, 8, 9]:
            if element_ratios["금"] >= 0.5:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["종혁격"].copy()
                gyeokguk_info["type"] = "종혁격"
                gyeokguk_info["ratio"] = element_ratios["금"]
                return gyeokguk_info

        # 6. 화기통명격 (火氣通明格) - 봄생 화 일간 + 목 지원
        if day_master in ["병", "정"] and birth_month in [1, 2, 3]:
            if element_ratios["목"] >= 0.3 and element_ratios["화"] >= 0.2:
                gyeokguk_info = self.SPECIAL_GYEOKGUK_DESC["화기통명격"].copy()
                gyeokguk_info["type"] = "화기통명격"
                gyeokguk_info["wood_ratio"] = element_ratios["목"]
                gyeokguk_info["fire_ratio"] = element_ratios["화"]
                return gyeokguk_info

        return None

    def analyze_jongguk_type(self, day_master: str, ten_gods: Dict,
                             five_elements: Dict, element_strength: int) -> Optional[Dict]:
        """
        종격 세부 유형 분석

        Args:
            day_master: 일간
            ten_gods: 십성 정보
            five_elements: 오행 분포
            element_strength: 일간 강도 (Phase 1에서 계산)

        Returns:
            종격 세부 유형 정보 또는 None
        """
        # 일간이 태약해야 종격 가능 (강도 < 30)
        if element_strength >= 30:
            return None

        # 십성 개수 집계
        ten_god_counts = {}
        for pillar_name, gods in ten_gods.items():
            for god_name, count in gods.items():
                ten_god_counts[god_name] = ten_god_counts.get(god_name, 0) + count

        total_ten_gods = sum(ten_god_counts.values())
        if total_ten_gods == 0:
            return None

        # 각 십성의 비율
        ten_god_ratios = {k: v / total_ten_gods for k, v in ten_god_counts.items()}

        # 1. 종강격 (從强格) - 비겁 왕성
        bigup_ratio = ten_god_ratios.get("비견", 0) + ten_god_ratios.get("겁재", 0)
        if bigup_ratio >= 0.7:
            jongguk_info = self.JONGGUK_TYPES_DESC["종강격"].copy()
            jongguk_info["type"] = "종강격"
            jongguk_info["ratio"] = bigup_ratio
            return jongguk_info

        # 2. 종재격 (從財格) - 재성 왕성
        jae_ratio = ten_god_ratios.get("정재", 0) + ten_god_ratios.get("편재", 0)
        if jae_ratio >= 0.5:
            jongguk_info = self.JONGGUK_TYPES_DESC["종재격"].copy()
            jongguk_info["type"] = "종재격"
            jongguk_info["ratio"] = jae_ratio
            return jongguk_info

        # 3. 종살격 (從殺格) - 관살 왕성
        gwan_ratio = ten_god_ratios.get("정관", 0) + ten_god_ratios.get("편관", 0)
        if gwan_ratio >= 0.5:
            jongguk_info = self.JONGGUK_TYPES_DESC["종살격"].copy()
            jongguk_info["type"] = "종살격"
            jongguk_info["ratio"] = gwan_ratio
            return jongguk_info

        # 4. 종식격 (從食格) - 식상 왕성
        sik_ratio = ten_god_ratios.get("식신", 0) + ten_god_ratios.get("상관", 0)
        if sik_ratio >= 0.5:
            jongguk_info = self.JONGGUK_TYPES_DESC["종식격"].copy()
            jongguk_info["type"] = "종식격"
            jongguk_info["ratio"] = sik_ratio
            return jongguk_info

        # 5. 종왕격 (從旺格) - 복합적으로 왕성
        if element_strength < 20:  # 매우 약함
            jongguk_info = self.JONGGUK_TYPES_DESC["종왕격"].copy()
            jongguk_info["type"] = "종왕격"
            jongguk_info["strength"] = element_strength
            return jongguk_info

        return None

    def check_paguk(self, gyeokguk_type: str, ten_gods: Dict) -> Dict:
        """
        파격(破格) 검사

        Args:
            gyeokguk_type: 격국 유형
            ten_gods: 십성 정보

        Returns:
            파격 정보 (is_paguk, factors, severity)
        """
        if gyeokguk_type not in self.PAGUK_CONDITIONS:
            return {
                "is_paguk": False,
                "factors": [],
                "severity": "없음",
                "description": "파격 조건 없음"
            }

        # 십성 개수 집계
        ten_god_counts = {}
        for pillar_name, gods in ten_gods.items():
            for god_name, count in gods.items():
                ten_god_counts[god_name] = ten_god_counts.get(god_name, 0) + count

        # 파격 조건 체크
        paguk_factors = []
        max_severity_level = 0
        severity_map = {"낮음": 1, "중간": 2, "높음": 3, "매우높음": 4}

        for condition in self.PAGUK_CONDITIONS[gyeokguk_type]:
            factor = condition["factor"]
            # 상관 -> 상관, 편인 -> 편인 등으로 매핑
            factor_mapping = {
                "상관": "상관",
                "편인": "편인",
                "비겁": ["비견", "겁재"],
                "식신": "식신",
                "정재": "정재",
                "편재": "편재",
                "정관": "정관"
            }

            factor_names = factor_mapping.get(factor, [])
            if isinstance(factor_names, str):
                factor_names = [factor_names]

            # 해당 십성이 있는지 체크
            has_factor = any(ten_god_counts.get(fn, 0) > 0 for fn in factor_names)

            if has_factor:
                # beneficial이 True면 좋은 것 (파격 아님)
                if condition.get("beneficial", False):
                    continue

                paguk_factors.append({
                    "name": condition["name"],
                    "severity": condition["severity"],
                    "description": condition["description"],
                    "count": sum(ten_god_counts.get(fn, 0) for fn in factor_names)
                })

                severity_level = severity_map.get(condition["severity"], 0)
                max_severity_level = max(max_severity_level, severity_level)

        # 파격 여부 및 심각도
        is_paguk = len(paguk_factors) > 0
        severity_reverse_map = {1: "낮음", 2: "중간", 3: "높음", 4: "매우높음"}
        overall_severity = severity_reverse_map.get(max_severity_level, "없음")

        return {
            "is_paguk": is_paguk,
            "factors": paguk_factors,
            "severity": overall_severity,
            "description": self._interpret_paguk(paguk_factors, overall_severity)
        }

    def _interpret_paguk(self, factors: List[Dict], severity: str) -> str:
        """파격 해석"""
        if not factors:
            return "격국이 온전히 보존되어 있습니다."

        if severity == "매우높음":
            base = "격국에 심각한 파격이 있습니다. "
        elif severity == "높음":
            base = "격국에 파격이 있습니다. "
        elif severity == "중간":
            base = "격국에 약간의 파격이 있습니다. "
        else:
            base = "격국에 경미한 파격이 있습니다. "

        factor_names = [f["name"] for f in factors]
        return base + ", ".join(factor_names) + "에 주의가 필요합니다."
