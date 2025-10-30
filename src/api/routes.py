"""
FastAPI 라우트 정의
사주 계산 및 해석 API 엔드포인트
"""

import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional

from src.models.saju import (
    BirthInfo,
    SajuResult,
    InterpretationRequest,
    InterpretationResponse,
    FullAnalysisRequest,
    FullAnalysisResponse
)
from src.models.compatibility import (
    CompatibilityRequest,
    CompatibilityAnalysis,
    CompatibilityFullResponse
)
from src.calculators.saju_calculator import SajuCalculator
from src.calculators.compatibility_calculator import CompatibilityCalculator
from src.services.interpretation_service import InterpretationService
from src.services.cache_service import CacheService


router = APIRouter()

# 서비스 인스턴스 (싱글톤처럼 사용)
_saju_calculator = None
_compatibility_calculator = None
_interpretation_service = None
_cache_service = None


def get_saju_calculator() -> SajuCalculator:
    """사주 계산기 인스턴스 가져오기"""
    global _saju_calculator
    if _saju_calculator is None:
        _saju_calculator = SajuCalculator()
    return _saju_calculator


def get_compatibility_calculator() -> CompatibilityCalculator:
    """궁합 계산기 인스턴스 가져오기"""
    global _compatibility_calculator
    if _compatibility_calculator is None:
        _compatibility_calculator = CompatibilityCalculator()
    return _compatibility_calculator


def get_interpretation_service() -> InterpretationService:
    """해석 서비스 인스턴스 가져오기"""
    global _interpretation_service
    if _interpretation_service is None:
        _interpretation_service = InterpretationService()
    return _interpretation_service


def get_cache_service() -> CacheService:
    """캐시 서비스 인스턴스 가져오기"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


@router.post("/calculate", response_model=SajuResult)
async def calculate_saju(
    birth_info: BirthInfo,
    calculator: SajuCalculator = Depends(get_saju_calculator),
    cache: CacheService = Depends(get_cache_service)
):
    """
    사주 계산 엔드포인트

    생년월일시를 입력받아 사주팔자, 십성, 오행, 대운을 계산합니다.

    **Parameters:**
    - year: 출생 연도 (양력)
    - month: 출생 월 (1-12)
    - day: 출생 일 (1-31)
    - hour: 출생 시 (0-23)
    - minute: 출생 분 (0-59, 기본값 0)
    - gender: 성별 (male/female, 선택사항)

    **Returns:**
    - 계산된 사주팔자 정보
    """
    try:
        # 캐시 확인
        cache_key = cache.get_cache_key_for_saju(
            birth_info.year, birth_info.month, birth_info.day, birth_info.hour
        )
        cached_result = await cache.get(cache_key)

        if cached_result:
            # 캐시에서 가져옴
            return SajuResult.model_validate_json(cached_result)

        # 사주 계산
        result = calculator.calculate(birth_info)

        # 캐시에 저장
        await cache.set(cache_key, result.model_dump_json())

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사주 계산 오류: {str(e)}")


@router.post("/interpret", response_model=InterpretationResponse)
async def interpret_saju(
    request: InterpretationRequest,
    service: InterpretationService = Depends(get_interpretation_service),
    cache: CacheService = Depends(get_cache_service)
):
    """
    사주 해석 엔드포인트

    계산된 사주 데이터를 받아서 Claude API를 통해 해석을 생성합니다.

    **Parameters:**
    - saju_result: 계산된 사주 데이터
    - question: 특정 질문 (예: "제 연애운은 어떤가요?", 선택사항)
    - detail_level: 상세도 (brief/normal/detailed, 기본값 normal)
    - tone: 어조 (formal/friendly/casual, 기본값 friendly)

    **Returns:**
    - 해석 결과
    """
    try:
        # 캐시 확인 (선택적)
        # 해석은 매번 조금 다를 수 있으므로 캐시를 사용할지는 선택사항
        # 여기서는 동일한 입력에 대해 캐시 사용

        # 해석 생성
        result = await service.interpret(request)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"해석 생성 오류: {str(e)}")


@router.post("/interpret/stream")
async def interpret_saju_stream(
    request: InterpretationRequest,
    service: InterpretationService = Depends(get_interpretation_service)
):
    """
    사주 해석 스트리밍 엔드포인트

    실시간으로 해석을 생성하여 스트리밍 방식으로 반환합니다.

    **Parameters:**
    - 동일한 InterpretationRequest

    **Returns:**
    - 텍스트 스트림
    """
    try:
        async def generate():
            async for chunk in service.interpret_stream(request):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스트리밍 해석 오류: {str(e)}")


@router.post("/full-analysis", response_model=FullAnalysisResponse)
async def full_analysis(
    request: FullAnalysisRequest,
    calculator: SajuCalculator = Depends(get_saju_calculator),
    service: InterpretationService = Depends(get_interpretation_service),
    cache: CacheService = Depends(get_cache_service)
):
    """
    전체 분석 엔드포인트

    생년월일시를 입력받아 사주 계산과 해석을 한번에 수행합니다.

    **Parameters:**
    - birth_info: 생년월일시 정보
    - question: 특정 질문 (선택사항)
    - detail_level: 상세도 (기본값 normal)
    - tone: 어조 (기본값 friendly)

    **Returns:**
    - 사주 계산 결과 + 해석 결과
    """
    try:
        # 1. 사주 계산 (캐시 확인)
        cache_key = cache.get_cache_key_for_saju(
            request.birth_info.year,
            request.birth_info.month,
            request.birth_info.day,
            request.birth_info.hour
        )
        cached_saju = await cache.get(cache_key)

        if cached_saju:
            saju_result = SajuResult.model_validate_json(cached_saju)
        else:
            saju_result = calculator.calculate(request.birth_info)
            await cache.set(cache_key, saju_result.model_dump_json())

        # 2. 해석 생성
        interpretation_request = InterpretationRequest(
            saju_result=saju_result,
            question=request.question,
            detail_level=request.detail_level,
            tone=request.tone
        )
        interpretation = await service.interpret(interpretation_request)

        return FullAnalysisResponse(
            saju_result=saju_result,
            interpretation=interpretation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 분석 오류: {str(e)}")


@router.get("/health")
async def health_check():
    """
    헬스체크 엔드포인트

    API 서버의 상태를 확인합니다.
    """
    return {
        "status": "healthy",
        "service": "사주 API",
        "version": "1.0.0"
    }


@router.delete("/cache/clear")
async def clear_cache(
    cache: CacheService = Depends(get_cache_service)
):
    """
    캐시 초기화 엔드포인트

    모든 캐시를 삭제합니다.
    """
    try:
        success = await cache.clear_all()
        if success:
            return {"message": "캐시가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=500, detail="캐시 삭제 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐시 삭제 오류: {str(e)}")


@router.post("/compatibility", response_model=CompatibilityFullResponse)
async def calculate_compatibility(
    request: CompatibilityRequest,
    saju_calculator: SajuCalculator = Depends(get_saju_calculator),
    compatibility_calculator: CompatibilityCalculator = Depends(get_compatibility_calculator),
    interpretation_service: InterpretationService = Depends(get_interpretation_service)
):
    """
    사주 궁합 분석 엔드포인트

    두 사람의 생년월일시를 입력받아 사주 궁합을 분석합니다.

    **Parameters:**
    - person1_birth: 첫 번째 사람의 생년월일시
    - person2_birth: 두 번째 사람의 생년월일시
    - detail_level: 상세도 (기본값 normal)

    **Returns:**
    - 궁합 분석 결과 + AI 해석
    """
    try:
        # 1. 두 사람의 사주 계산
        person1_birth_info = BirthInfo(**request.person1_birth)
        person2_birth_info = BirthInfo(**request.person2_birth)

        saju1 = saju_calculator.calculate(person1_birth_info)
        saju2 = saju_calculator.calculate(person2_birth_info)

        # 2. 궁합 분석
        compatibility_analysis = compatibility_calculator.calculate_compatibility(
            saju1, saju2
        )

        # 3. AI 해석 생성
        compatibility_text = f"""
## 사주 궁합 분석 결과

**종합 궁합 점수**: {compatibility_analysis.overall_score}점

**세부 점수**:
"""
        for score in compatibility_analysis.detailed_scores:
            compatibility_text += f"- {score.category}: {score.score}점 ({score.description})\n"

        compatibility_text += f"\n**긍정적인 면**:\n"
        for strength in compatibility_analysis.strengths:
            compatibility_text += f"- {strength}\n"

        compatibility_text += f"\n**주의할 점**:\n"
        for weakness in compatibility_analysis.weaknesses:
            compatibility_text += f"- {weakness}\n"

        # AI가 더 자세한 해석 생성
        interpretation_prompt = f"""
{compatibility_text}

위 궁합 분석 결과를 바탕으로, 두 사람의 관계에 대해 자세히 설명해주세요.
구체적인 조언과 함께 관계를 발전시킬 수 있는 방법을 제시해주세요.
"""

        # InterpretationRequest 생성 (첫 번째 사람 사주 기준)
        from src.models.saju import InterpretationRequest

        interp_request = InterpretationRequest(
            saju_result=saju1,
            question=interpretation_prompt,
            detail_level=request.detail_level,
            tone="friendly"
        )

        interpretation_response = await interpretation_service.interpret(interp_request)

        return CompatibilityFullResponse(
            compatibility_analysis=compatibility_analysis,
            interpretation=interpretation_response.interpretation,
            tokens_used=interpretation_response.tokens_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"궁합 분석 오류: {str(e)}")
