"""
정밀 24절기 계산기 (PyMeeus 기반)

천문학적으로 정확한 절기 시각 계산
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os


# PyMeeus가 설치되어 있는지 확인
try:
    from pymeeus.Sun import Sun
    from pymeeus.Epoch import Epoch
    PYMEEUS_AVAILABLE = True
except ImportError:
    PYMEEUS_AVAILABLE = False
    print("⚠️  PyMeeus not installed. Using approximate solar terms.")
    print("    Install with: pip install PyMeeus")


class PreciseSolarTermCalculator:
    """정밀 24절기 계산기"""

    # 24절기 태양 황경
    SOLAR_TERMS_LONGITUDE = {
        "입춘": 315,  # 立春
        "우수": 330,  # 雨水
        "경칩": 345,  # 驚蟄
        "춘분": 0,    # 春分
        "청명": 15,   # 清明
        "곡우": 30,   # 穀雨
        "입하": 45,   # 立夏
        "소만": 60,   # 小滿
        "망종": 75,   # 芒種
        "하지": 90,   # 夏至
        "소서": 105,  # 小暑
        "대서": 120,  # 大暑
        "입추": 135,  # 立秋
        "처서": 150,  # 處暑
        "백로": 165,  # 白露
        "추분": 180,  # 秋分
        "한로": 195,  # 寒露
        "상강": 210,  # 霜降
        "입동": 225,  # 立冬
        "소설": 240,  # 小雪
        "대설": 255,  # 大雪
        "동지": 270,  # 冬至
        "소한": 285,  # 小寒
        "대한": 300   # 大寒
    }

    def __init__(self):
        self.use_pymeeus = PYMEEUS_AVAILABLE
        # 기존 근사값 데이터 로드 (fallback용)
        self.approximate_data = self._load_approximate_data()

    def _load_approximate_data(self) -> Dict:
        """기존 근사값 데이터 로드"""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "solar_terms_1900_2050.json"
        )
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get_solar_term_time(self, year: int, term_name: str) -> Optional[datetime]:
        """
        특정 절기의 정확한 시각 계산

        Args:
            year: 연도
            term_name: 절기 이름 (예: "입춘", "경칩")

        Returns:
            절기 시각 (datetime)
        """
        if self.use_pymeeus:
            return self._calculate_precise_term(year, term_name)
        else:
            return self._get_approximate_term(year, term_name)

    def _calculate_precise_term(self, year: int, term_name: str) -> Optional[datetime]:
        """PyMeeus를 사용한 정밀 절기 계산"""
        if not PYMEEUS_AVAILABLE:
            return None

        target_longitude = self.SOLAR_TERMS_LONGITUDE.get(term_name)
        if target_longitude is None:
            return None

        try:
            # 대략적인 시작 시간 (해당 절기가 속한 달의 1일)
            month = self._get_approximate_month(term_name)
            start_epoch = Epoch(year, month, 1.0)

            # 태양 황경이 목표값이 되는 시각 찾기
            # 대략 1개월 범위 내에서 검색
            for day_offset in range(0, 40):
                test_epoch = start_epoch + day_offset

                # 태양의 황경 계산
                sun_longitude = Sun.apparent_longitude(test_epoch)

                # 황경을 0-360도로 정규화
                longitude = float(sun_longitude) % 360

                # 목표 황경과 비교 (±0.5도 오차 허용)
                if abs(longitude - target_longitude) < 0.5 or \
                   abs((longitude - target_longitude + 360) % 360) < 0.5:

                    # 더 정밀한 시각 계산 (시간 단위)
                    for hour in range(24):
                        for minute in [0, 15, 30, 45]:
                            test_time = test_epoch + (hour / 24.0) + (minute / 1440.0)
                            sun_long = float(Sun.apparent_longitude(test_time)) % 360

                            if abs(sun_long - target_longitude) < 0.1 or \
                               abs((sun_long - target_longitude + 360) % 360) < 0.1:

                                # Epoch를 datetime으로 변환
                                year_val = int(test_time.year())
                                month_val = int(test_time.month())
                                day_val = int(test_time.day())
                                time_of_day = (test_time.jde() - int(test_time.jde())) * 24

                                hour_val = int(time_of_day)
                                minute_val = int((time_of_day - hour_val) * 60)

                                return datetime(
                                    year_val, month_val, day_val,
                                    hour_val, minute_val
                                )

        except Exception as e:
            print(f"PyMeeus calculation error: {e}")
            return None

        return None

    def _get_approximate_term(self, year: int, term_name: str) -> Optional[datetime]:
        """근사값 데이터에서 절기 조회"""
        year_str = str(year)
        if year_str in self.approximate_data:
            term_data = self.approximate_data[year_str].get(term_name)
            if term_data:
                # "2024-02-04" 형식을 datetime으로 변환
                date_str = term_data.split()[0] if isinstance(term_data, str) else term_data
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except:
                    pass

        # 기본 근사값
        return self._get_default_approximate(year, term_name)

    def _get_approximate_month(self, term_name: str) -> int:
        """절기가 속하는 대략적인 달"""
        month_map = {
            "입춘": 2, "우수": 2,
            "경칩": 3, "춘분": 3,
            "청명": 4, "곡우": 4,
            "입하": 5, "소만": 5,
            "망종": 6, "하지": 6,
            "소서": 7, "대서": 7,
            "입추": 8, "처서": 8,
            "백로": 9, "추분": 9,
            "한로": 10, "상강": 10,
            "입동": 11, "소설": 11,
            "대설": 12, "동지": 12,
            "소한": 1, "대한": 1
        }
        return month_map.get(term_name, 1)

    def _get_default_approximate(self, year: int, term_name: str) -> datetime:
        """기본 근사값 (간단한 공식)"""
        # 매우 단순한 근사값
        approximate_dates = {
            "입춘": (2, 4),
            "우수": (2, 19),
            "경칩": (3, 6),
            "춘분": (3, 21),
            "청명": (4, 5),
            "곡우": (4, 20),
            "입하": (5, 6),
            "소만": (5, 21),
            "망종": (6, 6),
            "하지": (6, 21),
            "소서": (7, 7),
            "대서": (7, 23),
            "입추": (8, 8),
            "처서": (8, 23),
            "백로": (9, 8),
            "추분": (9, 23),
            "한로": (10, 8),
            "상강": (10, 23),
            "입동": (11, 7),
            "소설": (11, 22),
            "대설": (12, 7),
            "동지": (12, 22),
            "소한": (1, 6),
            "대한": (1, 20)
        }

        month, day = approximate_dates.get(term_name, (1, 1))

        # 소한과 대한은 다음해 1월
        if term_name in ["소한", "대한"]:
            year = year + 1

        return datetime(year, month, day, 0, 0)

    def check_lichun_passed(self, check_date: datetime) -> bool:
        """
        특정 날짜가 입춘을 지났는지 확인

        Args:
            check_date: 확인할 날짜

        Returns:
            입춘 통과 여부
        """
        lichun_time = self.get_solar_term_time(check_date.year, "입춘")

        if lichun_time:
            return check_date >= lichun_time

        # fallback: 간단한 판단
        if check_date.month < 2:
            return False
        elif check_date.month == 2:
            return check_date.day >= 4
        else:
            return True

    def get_saju_year(self, date: datetime) -> int:
        """
        사주 연도 계산 (입춘 기준)

        Args:
            date: 기준 날짜

        Returns:
            사주 연도
        """
        if self.check_lichun_passed(date):
            return date.year
        else:
            return date.year - 1


# 전역 인스턴스
_precise_calculator = None


def get_precise_solar_term_calculator() -> PreciseSolarTermCalculator:
    """전역 절기 계산기 인스턴스 반환"""
    global _precise_calculator
    if _precise_calculator is None:
        _precise_calculator = PreciseSolarTermCalculator()
    return _precise_calculator
