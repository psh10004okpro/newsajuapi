"""
사주 데이터 모델 정의
Pydantic을 사용한 타입 안전성과 검증
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class BirthInfo(BaseModel):
    """생년월일시 정보"""
    year: int = Field(..., description="출생 연도 (양력)")
    month: int = Field(..., ge=1, le=12, description="출생 월 (양력)")
    day: int = Field(..., ge=1, le=31, description="출생 일 (양력)")
    hour: int = Field(..., ge=0, le=23, description="출생 시 (24시간 형식)")
    minute: int = Field(0, ge=0, le=59, description="출생 분")
    is_leap_month: bool = Field(False, description="윤달 여부")
    gender: Optional[str] = Field(None, description="성별 (male/female)")


class SajuPillar(BaseModel):
    """사주의 한 기둥 (년/월/일/시주)"""
    heavenly_stem: str = Field(..., description="천간 (갑을병정...)")
    earthly_branch: str = Field(..., description="지지 (자축인묘...)")

    def __str__(self):
        return f"{self.heavenly_stem}{self.earthly_branch}"


class TenGods(BaseModel):
    """십성 정보"""
    bijeon: int = Field(0, description="비견 개수")
    겁재: int = Field(0, description="겁재 개수")
    식신: int = Field(0, description="식신 개수")
    상관: int = Field(0, description="상관 개수")
    편재: int = Field(0, description="편재 개수")
    정재: int = Field(0, description="정재 개수")
    편관: int = Field(0, description="편관 개수")
    정관: int = Field(0, description="정관 개수")
    편인: int = Field(0, description="편인 개수")
    정인: int = Field(0, description="정인 개수")


class FiveElements(BaseModel):
    """오행 정보"""
    wood: int = Field(0, description="목 개수")
    fire: int = Field(0, description="화 개수")
    earth: int = Field(0, description="토 개수")
    metal: int = Field(0, description="금 개수")
    water: int = Field(0, description="수 개수")

    def get_strongest(self) -> str:
        """가장 강한 오행 반환"""
        elements = {
            "목": self.wood,
            "화": self.fire,
            "토": self.earth,
            "금": self.metal,
            "수": self.water
        }
        return max(elements, key=elements.get)

    def get_weakest(self) -> str:
        """가장 약한 오행 반환"""
        elements = {
            "목": self.wood,
            "화": self.fire,
            "토": self.earth,
            "금": self.metal,
            "수": self.water
        }
        return min(elements, key=elements.get)


class DaeunPeriod(BaseModel):
    """대운 기간"""
    start_age: int = Field(..., description="대운 시작 나이")
    end_age: int = Field(..., description="대운 종료 나이")
    heavenly_stem: str = Field(..., description="대운 천간")
    earthly_branch: str = Field(..., description="대운 지지")

    def __str__(self):
        return f"{self.heavenly_stem}{self.earthly_branch} ({self.start_age}-{self.end_age}세)"


class SaeunYear(BaseModel):
    """세운(歲運) - 특정 년도의 운세"""
    year: int = Field(..., description="해당 년도")
    year_pillar: SajuPillar = Field(..., description="년도의 천간지지")
    age: int = Field(..., description="해당 년도의 나이")
    description: Optional[str] = Field(None, description="세운 설명")

    def __str__(self):
        return f"{self.year}년 ({self.age}세) {self.year_pillar}"


class SajuResult(BaseModel):
    """사주 계산 결과"""
    birth_info: BirthInfo = Field(..., description="입력된 생년월일시")

    # 사주팔자
    year_pillar: SajuPillar = Field(..., description="년주")
    month_pillar: SajuPillar = Field(..., description="월주")
    day_pillar: SajuPillar = Field(..., description="일주")
    hour_pillar: SajuPillar = Field(..., description="시주")

    # 일간 (나의 중심)
    day_master: str = Field(..., description="일간 (본인을 나타내는 천간)")

    # 십성 및 오행
    ten_gods: TenGods = Field(..., description="십성 분포")
    five_elements: FiveElements = Field(..., description="오행 분포")

    # 대운
    daeun_periods: List[DaeunPeriod] = Field(default_factory=list, description="대운 목록")

    # 세운 (연도별 운세)
    saeun_years: List[SaeunYear] = Field(default_factory=list, description="세운 목록 (연도별)")

    # 추가 정보
    lunar_date: Optional[Dict] = Field(None, description="음력 날짜 정보")
    solar_terms: Optional[Dict] = Field(None, description="절기 정보")


class InterpretationRequest(BaseModel):
    """해석 요청"""
    saju_result: SajuResult = Field(..., description="계산된 사주 데이터")
    question: Optional[str] = Field(None, description="특정 질문 (예: 연애운, 재물운)")
    detail_level: str = Field("normal", description="상세도 (brief/normal/detailed)")
    tone: str = Field("friendly", description="어조 (formal/friendly/casual)")


class InterpretationResponse(BaseModel):
    """해석 응답"""
    interpretation: str = Field(..., description="사주 해석 내용")
    topics_covered: List[str] = Field(default_factory=list, description="다룬 주제들")
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수")
    cached: bool = Field(False, description="캐시에서 가져왔는지 여부")


class FullAnalysisRequest(BaseModel):
    """전체 분석 요청 (계산 + 해석)"""
    birth_info: BirthInfo = Field(..., description="생년월일시")
    question: Optional[str] = Field(None, description="특정 질문")
    detail_level: str = Field("normal", description="상세도")
    tone: str = Field("friendly", description="어조")


class FullAnalysisResponse(BaseModel):
    """전체 분석 응답"""
    saju_result: SajuResult = Field(..., description="사주 계산 결과")
    interpretation: InterpretationResponse = Field(..., description="해석 결과")
