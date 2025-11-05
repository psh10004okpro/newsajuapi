"""
정밀 시주 계산기

경도 차이를 고려한 진시(眞時) 계산
Phase 3 정확도 개선
"""

from datetime import datetime, timedelta
from typing import Dict, Optional


class PreciseTimeCalculator:
    """정밀 시주 계산기"""

    # 주요 도시 경도 (동경 기준)
    CITY_LONGITUDE = {
        # 한국
        "서울": 126.9784,
        "부산": 129.0756,
        "대구": 128.6014,
        "인천": 126.7052,
        "광주": 126.8526,
        "대전": 127.3845,
        "울산": 129.3167,
        "세종": 127.2890,
        "수원": 127.0289,
        "제주": 126.5312,
        "춘천": 127.7342,
        "강릉": 128.8961,
        "청주": 127.4897,
        "전주": 127.1480,
        "포항": 129.3650,
        "창원": 128.6811,

        # 북한
        "평양": 125.7625,
        "개성": 126.5578,
        "원산": 127.4436,
        "함흥": 127.5364,

        # 기타 주요 도시
        "베이징": 116.4074,
        "상하이": 121.4737,
        "도쿄": 139.6917,
        "뉴욕": -74.0060,
        "런던": -0.1278,
        "파리": 2.3522
    }

    # 한국 표준시 경도 (동경 135도)
    KOREA_STANDARD_LONGITUDE = 135.0

    # 지지별 시간 범위
    EARTHLY_BRANCH_HOURS = {
        "자": (23, 1),   # 23:00-01:00
        "축": (1, 3),    # 01:00-03:00
        "인": (3, 5),    # 03:00-05:00
        "묘": (5, 7),    # 05:00-07:00
        "진": (7, 9),    # 07:00-09:00
        "사": (9, 11),   # 09:00-11:00
        "오": (11, 13),  # 11:00-13:00
        "미": (13, 15),  # 13:00-15:00
        "신": (15, 17),  # 15:00-17:00
        "유": (17, 19),  # 17:00-19:00
        "술": (19, 21),  # 19:00-21:00
        "해": (21, 23)   # 21:00-23:00
    }

    def calculate_true_time(self, solar_time: datetime,
                           longitude: float = 126.9784) -> datetime:
        """
        진시(眞時) 계산

        진시 = 표준시 + 경도차 보정
        경도 15도 = 1시간 차이

        Args:
            solar_time: 표준시 (양력 시간)
            longitude: 관측 지점의 경도 (동경 기준)

        Returns:
            진시(眞時)
        """
        # 경도 차이에 따른 시간 보정 (분 단위)
        # 경도 1도 = 4분
        time_diff_minutes = (longitude - self.KOREA_STANDARD_LONGITUDE) * 4

        # 진시 계산
        true_time = solar_time + timedelta(minutes=time_diff_minutes)

        return true_time

    def get_hour_branch(self, time: datetime) -> str:
        """
        시간으로부터 시지(時支) 결정

        Args:
            time: 시간 (진시 또는 표준시)

        Returns:
            시지 (자, 축, 인, ...)
        """
        hour = time.hour

        # 시지 결정
        if 23 <= hour or hour < 1:
            return "자"
        elif 1 <= hour < 3:
            return "축"
        elif 3 <= hour < 5:
            return "인"
        elif 5 <= hour < 7:
            return "묘"
        elif 7 <= hour < 9:
            return "진"
        elif 9 <= hour < 11:
            return "사"
        elif 11 <= hour < 13:
            return "오"
        elif 13 <= hour < 15:
            return "미"
        elif 15 <= hour < 17:
            return "신"
        elif 17 <= hour < 19:
            return "유"
        elif 19 <= hour < 21:
            return "술"
        else:  # 21 <= hour < 23
            return "해"

    def calculate_precise_hour_branch(self, solar_time: datetime,
                                     city: str = "서울",
                                     longitude: Optional[float] = None) -> Dict:
        """
        정밀 시지 계산 (경도 보정 포함)

        Args:
            solar_time: 표준시 출생 시각
            city: 출생 도시 (경도를 자동으로 찾음)
            longitude: 직접 지정한 경도 (city보다 우선)

        Returns:
            정밀 시지 계산 결과
        """
        # 경도 결정
        if longitude is None:
            longitude = self.CITY_LONGITUDE.get(city, 126.9784)

        # 진시 계산
        true_time = self.calculate_true_time(solar_time, longitude)

        # 표준시와 진시의 시지
        standard_branch = self.get_hour_branch(solar_time)
        true_branch = self.get_hour_branch(true_time)

        # 시지가 다른지 확인
        is_different = standard_branch != true_branch

        # 시간 차이 (분)
        time_diff_minutes = (longitude - self.KOREA_STANDARD_LONGITUDE) * 4

        return {
            "표준시": {
                "시각": solar_time.strftime("%H:%M:%S"),
                "시지": standard_branch,
                "시간대": self.EARTHLY_BRANCH_HOURS[standard_branch]
            },
            "진시": {
                "시각": true_time.strftime("%H:%M:%S"),
                "시지": true_branch,
                "시간대": self.EARTHLY_BRANCH_HOURS[true_branch]
            },
            "경도정보": {
                "도시": city,
                "경도": longitude,
                "표준경도": self.KOREA_STANDARD_LONGITUDE,
                "경도차": longitude - self.KOREA_STANDARD_LONGITUDE,
                "시간보정": f"{time_diff_minutes:+.1f}분"
            },
            "시지변경여부": is_different,
            "권장시지": true_branch,
            "설명": self._get_explanation(
                solar_time, true_time, standard_branch, true_branch, is_different
            )
        }

    def _get_explanation(self, solar_time: datetime, true_time: datetime,
                        standard_branch: str, true_branch: str,
                        is_different: bool) -> str:
        """시지 계산 설명"""

        if not is_different:
            return (
                f"표준시와 진시 모두 {true_branch}시로 동일합니다. "
                f"경도 보정을 적용해도 시지에 변화가 없습니다."
            )

        return (
            f"표준시 기준으로는 {standard_branch}시이지만, "
            f"경도를 고려한 진시 기준으로는 {true_branch}시입니다. "
            f"정확한 사주 계산을 위해 {true_branch}시를 사용하는 것을 권장합니다."
        )

    def get_available_cities(self) -> Dict[str, float]:
        """사용 가능한 도시 목록 반환"""
        return self.CITY_LONGITUDE.copy()

    def is_boundary_time(self, time: datetime, tolerance_minutes: int = 30) -> Dict:
        """
        시지 경계 시간 근처인지 확인

        시지 경계 시간 (매 홀수 시간: 01:00, 03:00, 05:00, ...)에서
        tolerance_minutes 이내인지 확인

        Args:
            time: 확인할 시간
            tolerance_minutes: 허용 오차 (분)

        Returns:
            경계 시간 정보
        """
        hour = time.hour
        minute = time.minute

        # 홀수 시간이 경계
        boundaries = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]

        for boundary_hour in boundaries:
            # 경계 시간과의 차이 계산
            if hour == boundary_hour and minute <= tolerance_minutes:
                return {
                    "is_boundary": True,
                    "boundary_hour": boundary_hour,
                    "minutes_from_boundary": minute,
                    "warning": f"{boundary_hour:02d}:00 경계 시간에서 {minute}분 떨어져 있습니다. "
                              f"경도 보정이 시지에 영향을 줄 수 있으니 주의하세요."
                }
            elif hour == boundary_hour - 1 and minute >= (60 - tolerance_minutes):
                return {
                    "is_boundary": True,
                    "boundary_hour": boundary_hour,
                    "minutes_from_boundary": 60 - minute,
                    "warning": f"{boundary_hour:02d}:00 경계 시간에서 {60 - minute}분 떨어져 있습니다. "
                              f"경도 보정이 시지에 영향을 줄 수 있으니 주의하세요."
                }

        # 자시 특별 처리 (23:00 경계)
        if hour == 23 and minute >= (60 - tolerance_minutes):
            return {
                "is_boundary": True,
                "boundary_hour": 23,
                "minutes_from_boundary": 60 - minute,
                "warning": f"23:00 경계 시간에서 {60 - minute}분 떨어져 있습니다. "
                          f"자시 전반/후반 구분에 주의하세요."
            }
        elif hour == 0 and minute <= tolerance_minutes:
            return {
                "is_boundary": True,
                "boundary_hour": 0,
                "minutes_from_boundary": minute,
                "warning": f"00:00 경계 시간에서 {minute}분 떨어져 있습니다. "
                          f"자시 전반/후반 구분에 주의하세요."
            }

        return {
            "is_boundary": False,
            "boundary_hour": None,
            "minutes_from_boundary": None,
            "warning": None
        }


def get_precise_time_calculator():
    """정밀 시간 계산기 인스턴스 반환 (싱글톤)"""
    return PreciseTimeCalculator()
