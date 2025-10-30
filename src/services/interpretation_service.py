"""
Claude API를 사용한 사주 해석 서비스
사주 데이터를 자연어로 변환하고 LLM을 통해 해석 생성
"""

import os
from typing import Optional, AsyncIterator
import anthropic
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from src.models.saju import (
    SajuResult, InterpretationRequest, InterpretationResponse
)

load_dotenv()


class InterpretationService:
    """사주 해석 서비스"""

    def __init__(self):
        """초기화"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    def _saju_to_natural_language(self, saju: SajuResult) -> str:
        """
        사주 데이터를 자연어로 변환
        LLM이 이해하기 쉬운 형태로 구조화
        """
        text = f"""
## 사주팔자 정보

**생년월일시**: {saju.birth_info.year}년 {saju.birth_info.month}월 {saju.birth_info.day}일 {saju.birth_info.hour}시

**사주팔자**:
- 년주(年柱): {saju.year_pillar.heavenly_stem}{saju.year_pillar.earthly_branch}
- 월주(月柱): {saju.month_pillar.heavenly_stem}{saju.month_pillar.earthly_branch}
- 일주(日柱): {saju.day_pillar.heavenly_stem}{saju.day_pillar.earthly_branch}
- 시주(時柱): {saju.hour_pillar.heavenly_stem}{saju.hour_pillar.earthly_branch}

**일간(日干)**: {saju.day_master} (본인의 중심)

**십성(十星) 분포**:
- 비견: {saju.ten_gods.bijeon}개
- 겁재: {saju.ten_gods.겁재}개
- 식신: {saju.ten_gods.식신}개
- 상관: {saju.ten_gods.상관}개
- 편재: {saju.ten_gods.편재}개
- 정재: {saju.ten_gods.정재}개
- 편관: {saju.ten_gods.편관}개
- 정관: {saju.ten_gods.정관}개
- 편인: {saju.ten_gods.편인}개
- 정인: {saju.ten_gods.정인}개

**오행(五行) 분포**:
- 목(木): {saju.five_elements.wood}개
- 화(火): {saju.five_elements.fire}개
- 토(土): {saju.five_elements.earth}개
- 금(金): {saju.five_elements.metal}개
- 수(水): {saju.five_elements.water}개

가장 강한 오행: {saju.five_elements.get_strongest()}
가장 약한 오행: {saju.five_elements.get_weakest()}
"""

        # 대운 정보 추가
        if saju.daeun_periods:
            text += "\n**대운(大運)**:\n"
            for daeun in saju.daeun_periods[:3]:  # 처음 3개만 표시
                text += f"- {daeun.start_age}-{daeun.end_age}세: {daeun.heavenly_stem}{daeun.earthly_branch}\n"

        return text

    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return """당신은 30년 경력의 명리학 전문가입니다. 사주팔자를 해석하여 일반인도 이해하기 쉽게 설명하는 것이 전문입니다.

**당신의 역할**:
- 복잡한 명리학 용어를 쉬운 말로 풀어서 설명
- 긍정적이면서도 현실적인 조언 제공
- 운명론이 아닌, 자기 이해와 성장을 위한 도구로서 사주 해석
- 구체적이고 실용적인 조언 제공

**해석 시 고려사항**:
1. 일간(日干)을 중심으로 해석
2. 십성의 분포를 통해 성격과 재능 파악
3. 오행의 균형을 통해 보완할 점 제시
4. 대운을 통해 인생의 흐름 설명
5. 편향되지 않고 균형잡힌 시각 유지

**어조**: 친근하고 따뜻하며, 격려하는 톤"""

    def _build_user_prompt(
        self,
        saju_natural_language: str,
        question: Optional[str] = None,
        detail_level: str = "normal",
        tone: str = "friendly"
    ) -> str:
        """사용자 프롬프트 생성"""

        prompt = saju_natural_language + "\n\n"

        # 질문이 있으면 특정 주제에 집중
        if question:
            prompt += f"**질문**: {question}\n\n"
            prompt += "위 질문에 대해 사주를 바탕으로 자세히 설명해주세요.\n"
        else:
            prompt += "이 사주를 종합적으로 해석해주세요. 다음 내용을 포함해주세요:\n"
            prompt += "1. 전체적인 성격과 기질\n"
            prompt += "2. 강점과 재능\n"
            prompt += "3. 보완하면 좋을 점\n"
            prompt += "4. 인생 전반의 흐름과 조언\n\n"

        # 상세도에 따른 지시
        if detail_level == "brief":
            prompt += "2-3문단으로 간략하게 요약해주세요."
        elif detail_level == "detailed":
            prompt += "5-6문단으로 자세히 설명해주세요."
        else:  # normal
            prompt += "3-4문단으로 설명해주세요."

        # 어조 설정
        if tone == "formal":
            prompt += " 존댓말을 사용하되 격식있게 작성해주세요."
        elif tone == "casual":
            prompt += " 친구에게 말하듯 편안한 반말로 작성해주세요."
        else:  # friendly
            prompt += " 친근하고 따뜻한 존댓말로 작성해주세요."

        return prompt

    async def interpret(self, request: InterpretationRequest) -> InterpretationResponse:
        """
        사주 해석 생성

        Args:
            request: 해석 요청

        Returns:
            InterpretationResponse: 해석 결과
        """
        # 사주 데이터를 자연어로 변환
        saju_text = self._saju_to_natural_language(request.saju_result)

        # 프롬프트 생성
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            saju_text,
            request.question,
            request.detail_level,
            request.tone
        )

        try:
            # Claude API 호출
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # 응답 추출
            interpretation = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens

            # 다룬 주제 추출 (간단히 키워드 기반)
            topics = []
            if request.question:
                topics.append(request.question)
            else:
                topics = ["전체 운세", "성격", "재능", "인생 조언"]

            return InterpretationResponse(
                interpretation=interpretation,
                topics_covered=topics,
                tokens_used=tokens_used,
                cached=False
            )

        except anthropic.APIError as e:
            raise Exception(f"Claude API 오류: {str(e)}")
        except Exception as e:
            raise Exception(f"해석 생성 실패: {str(e)}")

    async def interpret_stream(
        self, request: InterpretationRequest
    ) -> AsyncIterator[str]:
        """
        스트리밍 방식으로 사주 해석 생성
        실시간으로 해석이 생성되는 것처럼 보임

        Args:
            request: 해석 요청

        Yields:
            str: 해석 텍스트 조각
        """
        # 사주 데이터를 자연어로 변환
        saju_text = self._saju_to_natural_language(request.saju_result)

        # 프롬프트 생성
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            saju_text,
            request.question,
            request.detail_level,
            request.tone
        )

        try:
            # 스트리밍 API 호출
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except anthropic.APIError as e:
            raise Exception(f"Claude API 오류: {str(e)}")
        except Exception as e:
            raise Exception(f"해석 생성 실패: {str(e)}")

    async def close(self):
        """리소스 정리"""
        await self.client.close()
