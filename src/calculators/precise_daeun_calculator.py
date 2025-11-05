"""
정밀 대운 기점 계산기

실제 절기까지의 일수를 기반으로 정확한 대운 시작 시기 계산
Phase 2 정확도 개선
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from src.calculators.precise_solar_terms import get_precise_solar_term_calculator


class PreciseDaeunCalculator:
    """정밀 대운 기점 계산기"""

    # 천간 음양
    YANG_STEMS = ["갑", "병", "무", "경", "임"]
    YIN_STEMS = ["을", "정", "기", "신", "계"]

    # 24절기 순서 (절입 절기만)
    SOLAR_TERMS_ORDER = [
        "입춘", "경칩", "청명", "입하", "망종", "소서",
        "입추", "백로", "한로", "입동", "대설", "소한"
    ]

    def __init__(self):
        """초기화"""
        self.solar_calc = get_precise_solar_term_calculator()

    def calculate_precise_daeun_start(self, birth_date: datetime,
                                     year_stem: str, gender: str) -> Dict:
        """
        정밀 대운 기점 계산

        원리:
        - 양남음녀(陽男陰女): 다음 절기까지 일수 / 3 = 대운 시작 연령
        - 음남양녀(陰男陽女): 이전 절기부터 일수 / 3 = 대운 시작 연령
        - 3일 = 1년, 1일 = 4개월

        Args:
            birth_date: 출생 일시
            year_stem: 년간 (음양 판단용)
            gender: 성별 ("male" or "female")

        Returns:
            정밀 대운 기점 정보
        """
        # 1. 음양 판단
        is_yang_year = year_stem in self.YANG_STEMS
        is_male = gender.lower() == "male"

        # 2. 순행/역행 판단
        is_forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

        # 3. 출생월의 절기 찾기
        birth_month_term = self._get_birth_month_solar_term(birth_date)

        if not birth_month_term:
            # 절기를 찾을 수 없으면 기본값 사용
            return self._get_default_daeun_start(is_forward)

        # 4. 일수 계산
        if is_forward:
            # 순행: 다음 절기까지
            next_term = self._get_next_solar_term(birth_date, birth_month_term)
            if next_term:
                days_diff = (next_term - birth_date).days
                direction = "순행(順行)"
            else:
                return self._get_default_daeun_start(is_forward)
        else:
            # 역행: 이전 절기부터
            prev_term = self._get_previous_solar_term(birth_date, birth_month_term)
            if prev_term:
                days_diff = (birth_date - prev_term).days
                direction = "역행(逆行)"
            else:
                return self._get_default_daeun_start(is_forward)

        # 5. 대운 시작 연령 계산
        # 3일 = 1년, 1일 = 4개월
        start_years = days_diff // 3
        remain_days = days_diff % 3
        start_months = remain_days * 4

        # 6. 정확한 대운 시작 일자
        # 출생일 + days_diff일
        if is_forward:
            daeun_start_date = birth_date + timedelta(days=days_diff)
        else:
            # 역행의 경우 이미 days_diff만큼 과거를 계산했으므로
            # 실제 대운 시작은 출생일 기준
            daeun_start_date = birth_date

        # 7. 소수점 포함 정확한 연령
        precise_age = days_diff / 3.0

        return {
            "start_age": {
                "years": start_years,
                "months": start_months,
                "total_days": days_diff,
                "precise_age": round(precise_age, 2),
                "precise_age_text": f"{start_years}세 {start_months}개월"
            },
            "direction": direction,
            "is_forward": is_forward,
            "calculation_method": "정밀 절기 기반 (3일 = 1년)",
            "birth_month_term": birth_month_term,
            "reference_term_time": next_term.strftime("%Y-%m-%d %H:%M") if is_forward and next_term
                                   else prev_term.strftime("%Y-%m-%d %H:%M") if not is_forward and prev_term
                                   else "Unknown",
            "daeun_start_date": daeun_start_date.strftime("%Y-%m-%d"),
            "explanation": self._get_explanation(is_forward, days_diff, start_years, start_months)
        }

    def _get_birth_month_solar_term(self, birth_date: datetime) -> Optional[str]:
        """
        출생월의 절기 찾기

        각 월의 절입 절기:
        1월: 입춘, 2월: 경칩, 3월: 청명, 4월: 입하
        5월: 망종, 6월: 소서, 7월: 입추, 8월: 백로
        9월: 한로, 10월: 입동, 11월: 대설, 12월: 소한
        """
        month = birth_date.month

        # 월별 절입 절기 매핑 (양력 기준 대략)
        month_term_map = {
            1: "소한",   # 1월 5-6일경
            2: "입춘",   # 2월 3-5일경
            3: "경칩",   # 3월 5-6일경
            4: "청명",   # 4월 4-5일경
            5: "입하",   # 5월 5-6일경
            6: "망종",   # 6월 5-7일경
            7: "소서",   # 7월 6-8일경
            8: "입추",   # 8월 7-8일경
            9: "백로",   # 9월 7-8일경
            10: "한로",  # 10월 8-9일경
            11: "입동",  # 11월 7-8일경
            12: "대설"   # 12월 7-8일경
        }

        return month_term_map.get(month)

    def _get_next_solar_term(self, birth_date: datetime,
                            current_term: str) -> Optional[datetime]:
        """다음 절기 시각 찾기"""
        try:
            year = birth_date.year

            # 현재 절기의 시각
            current_term_time = self.solar_calc.get_solar_term_time(year, current_term)

            # 출생일이 절기 이전이면 그 절기가 다음 절기
            if current_term_time and birth_date < current_term_time:
                return current_term_time

            # 출생일이 절기 이후면 다음 절기 찾기
            current_index = self.SOLAR_TERMS_ORDER.index(current_term)
            next_index = (current_index + 1) % len(self.SOLAR_TERMS_ORDER)
            next_term = self.SOLAR_TERMS_ORDER[next_index]

            # 다음 해로 넘어가는 경우
            if next_index < current_index:
                year += 1

            next_term_time = self.solar_calc.get_solar_term_time(year, next_term)
            return next_term_time

        except Exception:
            return None

    def _get_previous_solar_term(self, birth_date: datetime,
                                 current_term: str) -> Optional[datetime]:
        """이전 절기 시각 찾기"""
        try:
            year = birth_date.year

            # 현재 절기의 시각
            current_term_time = self.solar_calc.get_solar_term_time(year, current_term)

            # 출생일이 절기 이후면 그 절기가 이전 절기
            if current_term_time and birth_date > current_term_time:
                return current_term_time

            # 출생일이 절기 이전이면 이전 절기 찾기
            current_index = self.SOLAR_TERMS_ORDER.index(current_term)
            prev_index = (current_index - 1) % len(self.SOLAR_TERMS_ORDER)
            prev_term = self.SOLAR_TERMS_ORDER[prev_index]

            # 이전 해로 넘어가는 경우
            if prev_index > current_index:
                year -= 1

            prev_term_time = self.solar_calc.get_solar_term_time(year, prev_term)
            return prev_term_time

        except Exception:
            return None

    def _get_default_daeun_start(self, is_forward: bool) -> Dict:
        """절기를 찾을 수 없을 때 기본값 반환"""
        default_age = 10 if is_forward else 5

        return {
            "start_age": {
                "years": default_age,
                "months": 0,
                "total_days": default_age * 3,
                "precise_age": default_age,
                "precise_age_text": f"{default_age}세"
            },
            "direction": "순행(順行)" if is_forward else "역행(逆行)",
            "is_forward": is_forward,
            "calculation_method": "기본값 (절기 정보 없음)",
            "birth_month_term": "Unknown",
            "reference_term_time": "Unknown",
            "daeun_start_date": "Unknown",
            "explanation": "절기 정보를 찾을 수 없어 기본값을 사용했습니다."
        }

    def _get_explanation(self, is_forward: bool, days_diff: int,
                        years: int, months: int) -> str:
        """대운 기점 설명"""
        direction_text = "다음 절기까지" if is_forward else "이전 절기부터"

        explanation = f"{direction_text} {days_diff}일입니다. "
        explanation += f"3일 = 1년 규칙에 따라, "
        explanation += f"{years}년 {months}개월(={days_diff}일 / 3)에 대운이 시작됩니다. "

        if is_forward:
            explanation += "(양남음녀 - 순행)"
        else:
            explanation += "(음남양녀 - 역행)"

        return explanation


def get_precise_daeun_calculator():
    """정밀 대운 계산기 인스턴스 반환 (싱글톤)"""
    return PreciseDaeunCalculator()
