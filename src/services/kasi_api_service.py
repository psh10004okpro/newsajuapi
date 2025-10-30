"""
한국천문연구원 API 연동 서비스
천문우주지식정보 API를 통해 정확한 24절기 데이터 가져오기

참고: 실제 사용을 위해서는 한국천문연구원 API 키가 필요합니다.
API 신청: https://astro.kasi.re.kr/
"""

import os
from typing import Optional, Dict
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class KASIApiService:
    """
    한국천문연구원(KASI) API 서비스

    참고: 이 서비스는 실제 API가 활성화되어 있어야 동작합니다.
    현재는 구조만 구현되어 있으며, 실제 엔드포인트는 확인이 필요합니다.
    """

    def __init__(self):
        """초기화"""
        self.api_key = os.getenv("KASI_API_KEY")
        self.base_url = os.getenv(
            "KASI_API_BASE_URL",
            "https://astro.kasi.re.kr/api"  # 예시 URL
        )
        self.enabled = bool(self.api_key)

        if not self.enabled:
            print("⚠️  KASI API 키가 설정되지 않았습니다. 로컬 데이터를 사용합니다.")

    async def get_solar_term(self, year: int, term_name: str) -> Optional[Dict]:
        """
        특정 년도의 특정 절기 정보 가져오기

        Args:
            year: 년도
            term_name: 절기 이름 (예: "입춘")

        Returns:
            절기 정보 (날짜, 시각 등)
        """
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 실제 API 엔드포인트는 KASI 문서 참고 필요
                url = f"{self.base_url}/solar-term"
                params = {
                    "year": year,
                    "term": term_name,
                    "key": self.api_key
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    print(f"KASI API 오류: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            print("KASI API 타임아웃")
            return None
        except Exception as e:
            print(f"KASI API 호출 실패: {str(e)}")
            return None

    async def get_all_solar_terms(self, year: int) -> Optional[Dict]:
        """
        특정 년도의 모든 24절기 정보 가져오기

        Args:
            year: 년도

        Returns:
            24절기 전체 정보
        """
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 실제 API 엔드포인트는 KASI 문서 참고 필요
                url = f"{self.base_url}/solar-terms/year"
                params = {
                    "year": year,
                    "key": self.api_key
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    print(f"KASI API 오류: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            print("KASI API 타임아웃")
            return None
        except Exception as e:
            print(f"KASI API 호출 실패: {str(e)}")
            return None

    async def get_lunar_date(self, solar_year: int, solar_month: int, solar_day: int) -> Optional[Dict]:
        """
        양력 날짜를 음력으로 변환

        Args:
            solar_year: 양력 년
            solar_month: 양력 월
            solar_day: 양력 일

        Returns:
            음력 날짜 정보
        """
        if not self.enabled:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/lunar-date"
                params = {
                    "solar_year": solar_year,
                    "solar_month": solar_month,
                    "solar_day": solar_day,
                    "key": self.api_key
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    print(f"KASI API 오류: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            print("KASI API 타임아웃")
            return None
        except Exception as e:
            print(f"KASI API 호출 실패: {str(e)}")
            return None

    def is_enabled(self) -> bool:
        """API가 활성화되어 있는지 확인"""
        return self.enabled


# 싱글톤 인스턴스
_kasi_service = None


def get_kasi_service() -> KASIApiService:
    """KASI API 서비스 인스턴스 가져오기"""
    global _kasi_service
    if _kasi_service is None:
        _kasi_service = KASIApiService()
    return _kasi_service
