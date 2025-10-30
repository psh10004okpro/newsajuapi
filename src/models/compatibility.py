"""
사주 궁합 데이터 모델
두 사람의 사주를 비교하여 궁합 분석
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from src.models.saju import SajuResult


class CompatibilityScore(BaseModel):
    """궁합 점수"""
    category: str = Field(..., description="카테고리 (오행, 십성, 일주 등)")
    score: int = Field(..., ge=0, le=100, description="점수 (0-100)")
    description: str = Field(..., description="점수 설명")


class CompatibilityAnalysis(BaseModel):
    """궁합 분석 결과"""
    # 입력된 두 사람의 사주
    person1_saju: SajuResult = Field(..., description="첫 번째 사람의 사주")
    person2_saju: SajuResult = Field(..., description="두 번째 사람의 사주")

    # 궁합 점수
    overall_score: int = Field(..., ge=0, le=100, description="종합 궁합 점수")
    detailed_scores: List[CompatibilityScore] = Field(
        default_factory=list,
        description="세부 궁합 점수"
    )

    # 궁합 분석
    strengths: List[str] = Field(default_factory=list, description="긍정적인 면")
    weaknesses: List[str] = Field(default_factory=list, description="주의할 점")
    advice: Optional[str] = Field(None, description="조언")


class CompatibilityRequest(BaseModel):
    """궁합 요청"""
    person1_birth: dict = Field(..., description="첫 번째 사람의 생년월일시")
    person2_birth: dict = Field(..., description="두 번째 사람의 생년월일시")
    detail_level: str = Field("normal", description="상세도 (brief/normal/detailed)")


class CompatibilityInterpretationRequest(BaseModel):
    """궁합 해석 요청"""
    compatibility_analysis: CompatibilityAnalysis = Field(
        ..., description="궁합 분석 결과"
    )
    question: Optional[str] = Field(None, description="특정 질문")
    detail_level: str = Field("normal", description="상세도")
    tone: str = Field("friendly", description="어조")


class CompatibilityFullResponse(BaseModel):
    """전체 궁합 분석 응답"""
    compatibility_analysis: CompatibilityAnalysis = Field(
        ..., description="궁합 분석"
    )
    interpretation: str = Field(..., description="AI 해석")
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수")
