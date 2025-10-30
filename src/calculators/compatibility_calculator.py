"""
사주 궁합 계산기
두 사람의 사주를 비교하여 궁합 점수와 분석 제공
"""

from typing import List
from src.models.saju import SajuResult
from src.models.compatibility import CompatibilityAnalysis, CompatibilityScore


class CompatibilityCalculator:
    """사주 궁합 계산기"""

    # 오행 상생 관계: (오행1, 오행2) -> 점수
    ELEMENT_HARMONY = {
        ("목", "목"): 70,  # 같은 오행
        ("목", "화"): 90,  # 목생화 (상생)
        ("목", "토"): 40,  # 목극토 (상극)
        ("목", "금"): 30,  # 금극목 (피극)
        ("목", "수"): 85,  # 수생목 (피생)

        ("화", "화"): 70,
        ("화", "토"): 90,  # 화생토
        ("화", "금"): 40,  # 화극금
        ("화", "수"): 30,  # 수극화
        ("화", "목"): 85,  # 목생화

        ("토", "토"): 70,
        ("토", "금"): 90,  # 토생금
        ("토", "수"): 40,  # 토극수
        ("토", "목"): 30,  # 목극토
        ("토", "화"): 85,  # 화생토

        ("금", "금"): 70,
        ("금", "수"): 90,  # 금생수
        ("금", "목"): 40,  # 금극목
        ("금", "화"): 30,  # 화극금
        ("금", "토"): 85,  # 토생금

        ("수", "수"): 70,
        ("수", "목"): 90,  # 수생목
        ("수", "화"): 40,  # 수극화
        ("수", "토"): 30,  # 토극수
        ("수", "금"): 85,  # 금생수
    }

    # 일주 궁합 (천간 + 지지 조합에 따른 궁합)
    # 실제로는 더 복잡하지만 여기서는 간단히 구현
    PERFECT_MATCH_PILLARS = {
        "갑자": ["기축", "병인", "정묘"],
        "을축": ["경인", "정묘", "무진"],
        # ... (실제로는 모든 60갑자 조합 필요)
    }

    def calculate_compatibility(
        self, saju1: SajuResult, saju2: SajuResult
    ) -> CompatibilityAnalysis:
        """
        두 사람의 사주 궁합 계산

        Args:
            saju1: 첫 번째 사람의 사주
            saju2: 두 번째 사람의 사주

        Returns:
            CompatibilityAnalysis: 궁합 분석 결과
        """
        detailed_scores = []

        # 1. 오행 균형 궁합 (40점)
        element_score = self._calculate_element_compatibility(saju1, saju2)
        detailed_scores.append(CompatibilityScore(
            category="오행 균형",
            score=element_score,
            description=self._get_element_description(element_score)
        ))

        # 2. 십성 궁합 (30점)
        ten_gods_score = self._calculate_ten_gods_compatibility(saju1, saju2)
        detailed_scores.append(CompatibilityScore(
            category="십성 조화",
            score=ten_gods_score,
            description=self._get_ten_gods_description(ten_gods_score)
        ))

        # 3. 일주 궁합 (30점)
        day_pillar_score = self._calculate_day_pillar_compatibility(saju1, saju2)
        detailed_scores.append(CompatibilityScore(
            category="일주 궁합",
            score=day_pillar_score,
            description=self._get_day_pillar_description(day_pillar_score)
        ))

        # 종합 점수 계산 (가중 평균)
        overall_score = int(
            (element_score * 0.4) +
            (ten_gods_score * 0.3) +
            (day_pillar_score * 0.3)
        )

        # 장점과 단점 분석
        strengths = self._analyze_strengths(
            saju1, saju2, element_score, ten_gods_score, day_pillar_score
        )
        weaknesses = self._analyze_weaknesses(
            saju1, saju2, element_score, ten_gods_score, day_pillar_score
        )

        # 조언 생성
        advice = self._generate_advice(overall_score, strengths, weaknesses)

        return CompatibilityAnalysis(
            person1_saju=saju1,
            person2_saju=saju2,
            overall_score=overall_score,
            detailed_scores=detailed_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            advice=advice
        )

    def _calculate_element_compatibility(
        self, saju1: SajuResult, saju2: SajuResult
    ) -> int:
        """오행 궁합 계산"""
        # 두 사람의 일간 오행 추출
        elem1 = self._get_element(saju1.day_master)
        elem2 = self._get_element(saju2.day_master)

        # 오행 궁합 점수
        base_score = self.ELEMENT_HARMONY.get((elem1, elem2), 50)

        # 오행 균형도 고려
        # 서로 부족한 오행을 보완해주면 좋음
        balance_bonus = self._calculate_balance_bonus(saju1, saju2)

        return min(100, base_score + balance_bonus)

    def _calculate_ten_gods_compatibility(
        self, saju1: SajuResult, saju2: SajuResult
    ) -> int:
        """십성 궁합 계산"""
        # 기본 점수
        score = 50

        # 상생하는 십성 조합이면 가산점
        # 예: 한 사람이 재성이 많고 다른 사람이 식상이 많으면 좋음
        # 식상 -> 재성 (식상생재)

        person1_gods = saju1.ten_gods
        person2_gods = saju2.ten_gods

        # 식상 + 재성 조합
        if (person1_gods.식신 + person1_gods.상관) > 2 and \
           (person2_gods.편재 + person2_gods.정재) > 2:
            score += 15

        # 인성 + 비겁 조합
        if (person1_gods.편인 + person1_gods.정인) > 2 and \
           (person2_gods.bijeon + person2_gods.겁재) > 2:
            score += 15

        # 관성이 너무 많으면 상호 극함
        if (person1_gods.편관 + person1_gods.정관) > 3 and \
           (person2_gods.편관 + person2_gods.정관) > 3:
            score -= 10

        return max(0, min(100, score))

    def _calculate_day_pillar_compatibility(
        self, saju1: SajuResult, saju2: SajuResult
    ) -> int:
        """일주 궁합 계산"""
        score = 50

        # 일간 같으면 보통
        if saju1.day_master == saju2.day_master:
            score = 60

        # 음양이 조화로우면 좋음
        if self._is_yin_yang_harmony(saju1.day_pillar, saju2.day_pillar):
            score += 20

        # 지지가 삼합, 육합이면 매우 좋음
        if self._is_harmonious_branch(
            saju1.day_pillar.earthly_branch,
            saju2.day_pillar.earthly_branch
        ):
            score += 20

        # 지지가 충(沖)이면 감점
        if self._is_conflicting_branch(
            saju1.day_pillar.earthly_branch,
            saju2.day_pillar.earthly_branch
        ):
            score -= 30

        return max(0, min(100, score))

    def _get_element(self, stem: str) -> str:
        """천간의 오행 반환"""
        element_map = {
            "갑": "목", "을": "목",
            "병": "화", "정": "화",
            "무": "토", "기": "토",
            "경": "금", "신": "금",
            "임": "수", "계": "수"
        }
        return element_map.get(stem, "목")

    def _calculate_balance_bonus(
        self, saju1: SajuResult, saju2: SajuResult
    ) -> int:
        """오행 균형 보너스 계산"""
        bonus = 0

        # 한 사람이 부족한 오행을 다른 사람이 가지고 있으면 보너스
        elem1_weak = saju1.five_elements.get_weakest()
        elem2_strong = saju2.five_elements.get_strongest()

        if elem1_weak == elem2_strong:
            bonus += 10

        elem2_weak = saju2.five_elements.get_weakest()
        elem1_strong = saju1.five_elements.get_strongest()

        if elem2_weak == elem1_strong:
            bonus += 10

        return bonus

    def _is_yin_yang_harmony(self, pillar1, pillar2) -> bool:
        """음양 조화 확인 (간단 버전)"""
        # 실제로는 더 복잡한 판단 필요
        return True  # 임시

    def _is_harmonious_branch(self, branch1: str, branch2: str) -> bool:
        """지지 육합/삼합 확인"""
        # 육합(六合): 자축합토, 인해합목, 묘술합화, 진유합금, 사신합수, 오미합화
        hexagram_pairs = [
            ("자", "축"), ("인", "해"), ("묘", "술"),
            ("진", "유"), ("사", "신"), ("오", "미")
        ]

        for pair in hexagram_pairs:
            if (branch1, branch2) in [pair, pair[::-1]]:
                return True

        return False

    def _is_conflicting_branch(self, branch1: str, branch2: str) -> bool:
        """지지 충(沖) 확인"""
        # 육충(六沖): 자오충, 축미충, 인신충, 묘유충, 진술충, 사해충
        conflict_pairs = [
            ("자", "오"), ("축", "미"), ("인", "신"),
            ("묘", "유"), ("진", "술"), ("사", "해")
        ]

        for pair in conflict_pairs:
            if (branch1, branch2) in [pair, pair[::-1]]:
                return True

        return False

    def _analyze_strengths(
        self, saju1, saju2, elem_score, ten_gods_score, day_score
    ) -> List[str]:
        """장점 분석"""
        strengths = []

        if elem_score >= 80:
            strengths.append("오행이 서로 조화롭게 보완됩니다")

        if ten_gods_score >= 75:
            strengths.append("십성 구조가 서로 도움이 됩니다")

        if day_score >= 80:
            strengths.append("일주가 매우 잘 어울립니다")

        if not strengths:
            strengths.append("노력을 통해 더 좋은 관계를 만들 수 있습니다")

        return strengths

    def _analyze_weaknesses(
        self, saju1, saju2, elem_score, ten_gods_score, day_score
    ) -> List[str]:
        """약점 분석"""
        weaknesses = []

        if elem_score < 50:
            weaknesses.append("오행 상극 관계가 있어 조율이 필요합니다")

        if ten_gods_score < 50:
            weaknesses.append("성향 차이로 인한 갈등 가능성이 있습니다")

        if day_score < 50:
            weaknesses.append("일주 충돌로 인한 마찰을 조심하세요")

        if not weaknesses:
            weaknesses.append("특별한 약점이 보이지 않습니다")

        return weaknesses

    def _generate_advice(
        self, overall_score: int, strengths: List[str], weaknesses: List[str]
    ) -> str:
        """조언 생성"""
        if overall_score >= 80:
            return "매우 좋은 궁합입니다. 서로를 존중하며 관계를 발전시켜 나가세요."
        elif overall_score >= 60:
            return "좋은 궁합입니다. 서로의 차이를 이해하고 노력한다면 행복한 관계가 될 것입니다."
        elif overall_score >= 40:
            return "보통 궁합입니다. 서로를 이해하려는 노력과 배려가 중요합니다."
        else:
            return "도전적인 궁합입니다. 많은 노력과 이해가 필요하지만, 그만큼 성장할 수 있는 관계입니다."

    def _get_element_description(self, score: int) -> str:
        """오행 점수 설명"""
        if score >= 80:
            return "오행이 매우 조화롭습니다"
        elif score >= 60:
            return "오행이 대체로 잘 맞습니다"
        elif score >= 40:
            return "오행이 보통 수준입니다"
        else:
            return "오행 조화에 노력이 필요합니다"

    def _get_ten_gods_description(self, score: int) -> str:
        """십성 점수 설명"""
        if score >= 80:
            return "성향이 매우 잘 맞습니다"
        elif score >= 60:
            return "성향이 대체로 조화롭습니다"
        elif score >= 40:
            return "성향 차이가 약간 있습니다"
        else:
            return "성향 차이에 유의가 필요합니다"

    def _get_day_pillar_description(self, score: int) -> str:
        """일주 점수 설명"""
        if score >= 80:
            return "일주가 완벽하게 조화롭습니다"
        elif score >= 60:
            return "일주가 좋은 편입니다"
        elif score >= 40:
            return "일주가 보통입니다"
        else:
            return "일주 충돌을 주의하세요"
