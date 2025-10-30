# 🔮 사주 API - LLM 기반 사주 계산 및 해석 시스템

> Claude AI를 활용한 정확한 사주팔자 계산과 이해하기 쉬운 해석 서비스

## ✨ 주요 기능

- 📅 **정확한 사주 계산**: 24절기 절입시각을 고려한 정밀한 사주팔자 계산
- 🤖 **AI 기반 해석**: Anthropic Claude를 활용한 자연스럽고 이해하기 쉬운 해석
- ⚡ **고성능 캐싱**: Redis/메모리 캐싱으로 빠른 응답 속도
- 📊 **상세 분석**: 십성, 오행, 대운 등 명리학 요소 분석
- 🌊 **스트리밍 지원**: 실시간 해석 생성 스트리밍
- 🎯 **맞춤 질문**: 연애운, 재물운, 직업운 등 특정 주제 질문 가능

## 🛠 기술 스택

- **Backend**: FastAPI (Python 3.9+)
- **LLM**: Anthropic Claude (claude-3-5-sonnet)
- **Cache**: Redis (선택사항, 없으면 메모리 캐싱)
- **Async**: asyncio, httpx
- **Korean Calendar**: korean-lunar-calendar

## 📦 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd newsajuapi
```

### 2. Python 가상환경 생성 및 활성화

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고, API 키를 설정합니다.

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 Anthropic API 키를 입력합니다:

```env
ANTHROPIC_API_KEY=your_actual_api_key_here
```

> ⚠️ **중요**: Anthropic API 키는 [https://console.anthropic.com/](https://console.anthropic.com/)에서 발급받을 수 있습니다.

### 5. 서버 실행

```bash
python main.py
```

또는 uvicorn 직접 실행:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 다음 주소에서 접속할 수 있습니다:

- **API 문서**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **루트**: http://localhost:8000/

## 🚀 사용 방법

### API 엔드포인트

#### 1. 사주 계산 (`POST /api/v1/calculate`)

생년월일시를 입력하여 사주팔자를 계산합니다.

**요청 예시**:

```bash
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "gender": "male"
  }'
```

**응답 예시**:

```json
{
  "birth_info": {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "gender": "male"
  },
  "year_pillar": {
    "heavenly_stem": "경",
    "earthly_branch": "오"
  },
  "month_pillar": {
    "heavenly_stem": "신",
    "earthly_branch": "사"
  },
  "day_pillar": {
    "heavenly_stem": "무",
    "earthly_branch": "자"
  },
  "hour_pillar": {
    "heavenly_stem": "기",
    "earthly_branch": "미"
  },
  "day_master": "무",
  "ten_gods": {
    "비견": 2,
    "겁재": 1,
    "식신": 1,
    "상관": 0,
    "편재": 1,
    "정재": 1,
    "편관": 0,
    "정관": 1,
    "편인": 1,
    "정인": 0
  },
  "five_elements": {
    "wood": 1,
    "fire": 3,
    "earth": 2,
    "metal": 1,
    "water": 1
  }
}
```

#### 2. 사주 해석 (`POST /api/v1/interpret`)

계산된 사주를 AI로 해석합니다.

**요청 예시**:

```bash
curl -X POST "http://localhost:8000/api/v1/interpret" \
  -H "Content-Type: application/json" \
  -d '{
    "saju_result": { /* 위의 calculate 결과 */ },
    "question": "제 연애운은 어떤가요?",
    "detail_level": "normal",
    "tone": "friendly"
  }'
```

#### 3. 전체 분석 (`POST /api/v1/full-analysis`)

계산과 해석을 한번에 수행합니다. **가장 권장하는 방법**입니다.

**요청 예시**:

```bash
curl -X POST "http://localhost:8000/api/v1/full-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_info": {
      "year": 1990,
      "month": 5,
      "day": 15,
      "hour": 14,
      "minute": 30,
      "gender": "male"
    },
    "question": "전체적인 운세를 알려주세요",
    "detail_level": "normal",
    "tone": "friendly"
  }'
```

**응답 예시**:

```json
{
  "saju_result": { /* 사주 계산 결과 */ },
  "interpretation": {
    "interpretation": "무토 일간을 가진 당신은...",
    "topics_covered": ["전체 운세", "성격", "재능", "인생 조언"],
    "tokens_used": 1523,
    "cached": false
  }
}
```

#### 4. 스트리밍 해석 (`POST /api/v1/interpret/stream`)

실시간으로 해석을 생성하여 스트리밍으로 반환합니다.

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/interpret/stream",
    json={"saju_result": {...}, ...},
    stream=True
)

for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    print(chunk, end='', flush=True)
```

## 🎯 사용 예시

### Python으로 API 호출하기

```python
import requests

# 1. 전체 분석 요청
response = requests.post(
    "http://localhost:8000/api/v1/full-analysis",
    json={
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "gender": "male"
        },
        "question": "제 직업운은 어떤가요?",
        "detail_level": "detailed",
        "tone": "friendly"
    }
)

data = response.json()
print(data["interpretation"]["interpretation"])
```

### JavaScript (fetch)로 API 호출하기

```javascript
fetch('http://localhost:8000/api/v1/full-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    birth_info: {
      year: 1990,
      month: 5,
      day: 15,
      hour: 14,
      minute: 30,
      gender: 'male'
    },
    question: '제 재물운은 어떤가요?',
    detail_level: 'normal',
    tone: 'friendly'
  })
})
.then(response => response.json())
.then(data => console.log(data.interpretation.interpretation));
```

## 📝 주요 매개변수

### BirthInfo (생년월일시)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| year | int | ✅ | 출생 연도 (양력) |
| month | int | ✅ | 출생 월 (1-12) |
| day | int | ✅ | 출생 일 (1-31) |
| hour | int | ✅ | 출생 시 (0-23) |
| minute | int | ❌ | 출생 분 (0-59, 기본값 0) |
| gender | str | ❌ | 성별 (male/female) |

### 해석 옵션

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| question | str | null | 특정 질문 (예: "연애운", "직업운") |
| detail_level | str | normal | 상세도 (brief/normal/detailed) |
| tone | str | friendly | 어조 (formal/friendly/casual) |

## 🔧 환경 변수 설정

`.env` 파일에서 다음 항목을 설정할 수 있습니다:

```env
# 필수: Anthropic API 키
ANTHROPIC_API_KEY=your_api_key_here

# 선택: Redis 설정 (없으면 메모리 캐싱 사용)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 선택: API 설정
API_HOST=0.0.0.0
API_PORT=8000

# 선택: 캐시 설정
ENABLE_CACHE=true
CACHE_TTL_SECONDS=86400

# 선택: LLM 설정
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
```

## 🐳 Docker로 실행하기 (선택사항)

Docker를 사용하면 환경 설정 없이 바로 실행할 수 있습니다.

```bash
# Docker 이미지 빌드
docker build -t saju-api .

# 컨테이너 실행
docker run -d \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_api_key \
  --name saju-api \
  saju-api
```

## 📚 프로젝트 구조

```
newsajuapi/
├── main.py                          # FastAPI 메인 앱
├── requirements.txt                 # Python 의존성
├── .env.example                     # 환경 변수 예시
├── .env                            # 환경 변수 (git 무시)
├── README.md                        # 이 문서
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── saju.py                 # 데이터 모델 (Pydantic)
│   ├── calculators/
│   │   ├── __init__.py
│   │   └── saju_calculator.py      # 사주 계산 엔진
│   ├── services/
│   │   ├── __init__.py
│   │   ├── interpretation_service.py  # Claude API 통합
│   │   └── cache_service.py         # 캐싱 서비스
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # API 라우트
│   └── data/
│       └── solar_terms_2024_2025.json  # 24절기 데이터
└── tests/                           # 테스트 코드
```

## 🧪 테스트

```bash
# 헬스체크
curl http://localhost:8000/api/v1/health

# 간단한 사주 계산 테스트
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{"year": 1990, "month": 5, "day": 15, "hour": 14}'
```

## 💡 유용한 팁

### 1. 특정 주제 질문하기

```json
{
  "question": "제 연애운과 결혼운은 어떤가요?"
}
```

### 2. 상세도 조절

- `brief`: 2-3문단 간략한 요약
- `normal`: 3-4문단 일반적인 설명
- `detailed`: 5-6문단 자세한 분석

### 3. 어조 선택

- `formal`: 격식있는 존댓말
- `friendly`: 친근한 존댓말 (기본값)
- `casual`: 편안한 반말

## 🔒 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- `ANTHROPIC_API_KEY`는 안전하게 보관하세요
- 프로덕션 환경에서는 CORS 설정을 제한하세요
- Rate limiting을 구현하여 API 남용을 방지하세요

## 🐛 문제 해결

### API 키 오류

```
ValueError: ANTHROPIC_API_KEY가 설정되지 않았습니다.
```

➡️ `.env` 파일에 `ANTHROPIC_API_KEY`를 설정하세요.

### Redis 연결 실패

```
⚠ Redis 연결 실패, 메모리 캐시 사용
```

➡️ 정상 동작합니다. Redis 없이 메모리 캐싱으로 실행됩니다.
   Redis를 사용하려면 Redis를 설치하고 실행하세요:

```bash
# Linux/Mac
brew install redis
redis-server

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 모듈 import 오류

```
ModuleNotFoundError: No module named 'xxx'
```

➡️ 의존성을 다시 설치하세요:

```bash
pip install -r requirements.txt
```

## 📖 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [한국천문연구원](https://www.kasi.re.kr/)

## 📄 라이선스

MIT License

## 🤝 기여하기

이슈와 PR을 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ and 🤖 Claude AI**
