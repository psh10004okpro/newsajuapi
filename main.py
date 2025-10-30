"""
사주 API 메인 애플리케이션
FastAPI 서버 진입점
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.routes import router

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="사주 API",
    description="""
    **LLM 기반 사주 계산 및 해석 API**

    이 API는 생년월일시를 입력받아 사주팔자를 계산하고,
    Claude AI를 활용하여 일반인도 이해하기 쉬운 해석을 제공합니다.

    ## 주요 기능

    - 🔢 **정확한 사주 계산**: 24절기 절입시각을 고려한 정확한 사주팔자 계산
    - 🤖 **AI 해석**: Claude AI를 활용한 자연스럽고 이해하기 쉬운 해석
    - ⚡ **고성능 캐싱**: Redis 또는 메모리 캐싱으로 빠른 응답
    - 📊 **십성 및 오행 분석**: 상세한 명리학 분석 제공
    - 🔮 **대운 계산**: 10년 단위 대운 흐름 파악

    ## 엔드포인트

    - `POST /calculate`: 사주 계산만 수행
    - `POST /interpret`: 계산된 사주 해석 생성
    - `POST /interpret/stream`: 스트리밍 방식 해석 생성
    - `POST /full-analysis`: 계산 + 해석 한번에 수행
    - `GET /health`: 헬스체크
    - `DELETE /cache/clear`: 캐시 초기화
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (필요시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix="/api/v1", tags=["사주 API"])


@app.on_event("startup")
async def startup_event():
    """서버 시작시 실행"""
    print("=" * 60)
    print("🔮 사주 API 서버 시작")
    print("=" * 60)
    print(f"📍 문서: http://localhost:8000/docs")
    print(f"📍 ReDoc: http://localhost:8000/redoc")
    print(f"🤖 LLM 모델: {os.getenv('LLM_MODEL', 'claude-3-5-sonnet-20241022')}")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료시 실행"""
    print("\n👋 사주 API 서버 종료")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "사주 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "calculate": "/api/v1/calculate",
            "interpret": "/api/v1/interpret",
            "interpret_stream": "/api/v1/interpret/stream",
            "full_analysis": "/api/v1/full-analysis",
            "health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # 환경 변수에서 설정 가져오기
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    # 서버 실행
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # 개발 모드에서 자동 리로드
        log_level="info"
    )
