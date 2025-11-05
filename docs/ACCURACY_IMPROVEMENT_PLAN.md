# 사주 API 정확도 개선 계획

## 📋 목차
1. [현재 시스템 분석](#현재-시스템-분석)
2. [정확도 문제점](#정확도-문제점)
3. [개선 방안](#개선-방안)
4. [우선순위별 구현 계획](#우선순위별-구현-계획)

---

## 현재 시스템 분석

### ✅ 잘 구현된 부분
- 기본 사주팔자 계산 로직
- 십성, 오행 분포 계산
- 대운, 세운 계산
- 명리학 데이터 (십이운성, 신살, 합충형해파)
- 고급 분석 (공망, 격국, 용신)

### ⚠️ 개선이 필요한 부분
- 24절기 정확도
- 지지 장간(藏干) 미반영
- 오행 강약 판단의 단순함
- 격국 판단의 제한성
- 용신 선정의 단순화

---

## 정확도 문제점

### 1. 🌞 절기 계산 (중요도: ★★★★★)

**현재 상태**:
```python
# 단순 근사값 사용
if month < 2 or (month == 2 and day < 4):
    saju_year = year - 1
```

**문제점**:
- 입춘 시각이 매년 다름 (2월 3일~5일 사이 변동)
- 다른 절기도 근사값만 사용
- 시간(時) 단위까지 고려 안함

**영향도**: 월주 계산 오류 → 전체 사주 분석 왜곡

**개선 방안**:
1. **천문역법 라이브러리 사용**
   ```python
   # PyMeeus, ephem, skyfield 등
   from skyfield import almanac
   # 정확한 절기 시각 계산
   ```

2. **KASI API 실제 연동**
   ```python
   # 한국천문연구원 실시간 데이터
   async def get_accurate_solar_term(year, month, day):
       # KASI API 호출
   ```

3. **시간대 고려**
   - 태양시(太陽時) vs 표준시
   - 경도에 따른 시차 보정

---

### 2. 🏺 지지 장간(藏干) 미반영 (중요도: ★★★★★)

**현재 상태**:
```python
# 지지를 오행으로만 변환
"자": "수", "축": "토"
```

**문제점**:
지지 안에 숨어있는 천간(장간)을 고려하지 않음

**예시**:
- 축(丑) = 己土(본기) + 癸水 + 辛金
- 인(寅) = 甲木(본기) + 丙火 + 戊土

**영향도**:
- 십성 계산의 불완전
- 오행 강약 판단 오류
- 격국 판단 부정확

**개선 방안**:
```python
# 지지 장간 데이터
EARTHLY_BRANCH_HIDDEN_STEMS = {
    "자": {"본기": "계", "여기": [], "중기": []},
    "축": {"본기": "기", "여기": ["계"], "중기": ["신"]},
    "인": {"본기": "갑", "여기": ["무"], "중기": ["병"]},
    "묘": {"본기": "을", "여기": [], "중기": []},
    "진": {"본기": "무", "여기": ["을"], "중기": ["계"]},
    "사": {"본기": "병", "여기": ["무"], "중기": ["경"]},
    "오": {"본기": "정", "여기": ["기"], "중기": []},
    "미": {"본기": "기", "여기": ["을"], "중기": ["정"]},
    "신": {"본기": "경", "여기": ["무"], "중기": ["임"]},
    "유": {"본기": "신", "여기": [], "중기": []},
    "술": {"본기": "무", "여기": ["신"], "중기": ["정"]},
    "해": {"본기": "임", "여기": ["갑"], "중기": []}
}

def get_hidden_stems(branch: str) -> Dict:
    """지지에서 장간 추출"""
    return EARTHLY_BRANCH_HIDDEN_STEMS[branch]

def calculate_ten_gods_with_hidden_stems(day_master, pillars):
    """장간을 고려한 십성 계산"""
    ten_gods = {}

    for pillar in pillars:
        # 천간
        stem_ten_god = get_ten_god(day_master, pillar.stem)

        # 지지 본기
        hidden = get_hidden_stems(pillar.branch)
        main_ten_god = get_ten_god(day_master, hidden["본기"])

        # 여기, 중기
        for stem in hidden["여기"] + hidden["중기"]:
            additional_ten_god = get_ten_god(day_master, stem)

    return ten_gods
```

---

### 3. ⚖️ 오행 강약 판단 (중요도: ★★★★★)

**현재 상태**:
```python
# 단순 개수만 카운트
wood: 3, fire: 2, earth: 1, metal: 2, water: 0
```

**문제점**:
- 월령(月令)의 득령(得令) 여부 미고려
- 통근력(通根力) 계산 없음
- 투간력(透干力) 계산 없음

**개선 방안**:

```python
class ElementStrengthAnalyzer:
    """오행 강약 분석기 (정밀)"""

    # 월령 득령표
    MONTH_ELEMENT_STRENGTH = {
        "인": {"목": 100, "화": 70, "토": 20, "금": 10, "수": 30},
        "묘": {"목": 100, "화": 60, "토": 20, "금": 10, "수": 20},
        "진": {"토": 100, "목": 30, "수": 40, "금": 20, "화": 10},
        # ... 모든 월지
    }

    def calculate_element_strength(self, day_master, pillars, month_branch):
        """
        오행 강약 정밀 계산

        고려 요소:
        1. 득령(得令): 월령에서 힘을 받는가
        2. 통근(通根): 지지에 뿌리가 있는가
        3. 투간(透干): 천간에 드러났는가
        4. 생조(生助): 생하거나 돕는 글자 수
        """
        day_element = self.ELEMENT_MAP[day_master]

        # 1. 득령 점수 (가장 중요)
        strength = self.MONTH_ELEMENT_STRENGTH[month_branch][day_element]

        # 2. 통근 점수
        for pillar in pillars:
            hidden_stems = get_hidden_stems(pillar.branch)
            if day_master in [hidden_stems["본기"]] + hidden_stems["여기"] + hidden_stems["중기"]:
                if pillar.branch == month_branch:
                    strength += 40  # 월지 통근
                else:
                    strength += 20  # 기타 통근

        # 3. 투간 점수
        transparent_count = sum(1 for p in pillars if p.heavenly_stem == day_master)
        strength += transparent_count * 15

        # 4. 생조 점수
        supporting_element = self._get_supporting_element(day_element)
        support_count = sum(
            1 for p in pillars
            if self.ELEMENT_MAP[p.heavenly_stem] == supporting_element
        )
        strength += support_count * 10

        return strength

    def judge_strength_level(self, strength: int) -> str:
        """강약 등급 판단"""
        if strength >= 150:
            return "태왕(太旺)"
        elif strength >= 100:
            return "왕(旺)"
        elif strength >= 70:
            return "중화(中和)"
        elif strength >= 40:
            return "약(弱)"
        else:
            return "태약(太弱)"
```

---

### 4. 🎯 격국 판단 고도화 (중요도: ★★★★☆)

**현재 상태**:
- 기본 8격 + 건록/양인격
- 종격은 명칭만

**문제점**:
- 특수 격국 미구현 (화기통명격, 염상격 등)
- 종격의 세부 구분 없음 (종강격, 종재격, 종살격 등)
- 파격(破格) 판단 없음

**개선 방안**:

```python
class AdvancedGyeokgukAnalyzer:
    """고급 격국 분석"""

    def analyze_special_gyeokguk(self, saju_result):
        """특수 격국 판단"""

        # 1. 종격 세부 판단
        if self._is_very_weak(day_master):
            dominant = self._get_dominant_element(saju_result)

            if dominant in ["정관", "편관"]:
                return "종살격(從殺格)"
            elif dominant in ["정재", "편재"]:
                return "종재격(從財格)"
            elif dominant in ["식신", "상관"]:
                return "종식격(從食格)"
            elif self._all_same_element(saju_result):
                return "종강격(從强格)"

        # 2. 화기통명격 (火氣通明格)
        if day_master in ["병", "정"] and month_branch in ["인", "묘", "진"]:
            if self._has_wood_support(saju_result):
                return "화기통명격"

        # 3. 염상격 (炎上格)
        if self._dominant_fire(saju_result) and day_master in ["병", "정"]:
            return "염상격(炎上格)"

        # 4. 곡직격 (曲直格)
        if self._dominant_wood(saju_result) and day_master in ["갑", "을"]:
            return "곡직격(曲直格)"

        return None

    def check_gyeokguk_破(self, gyeokguk_type, saju_result):
        """격국 파격 여부 검사"""

        破_factors = []

        if gyeokguk_type == "정관격":
            # 정관격 파격 조건
            if self._has_상관(saju_result):
                破_factors.append("상관견관(傷官見官)")
            if self._has_편인(saju_result):
                破_factors.append("편인탈식(偏印奪食)")

        elif gyeokguk_type == "식신격":
            if self._has_편인(saju_result):
                破_factors.append("편인탈식(偏印奪食)")

        return {
            "is_破": len(破_factors) > 0,
            "破_factors": 破_factors,
            "severity": "높음" if len(破_factors) >= 2 else "중간"
        }
```

---

### 5. 🔮 용신 선정 정밀화 (중요도: ★★★★☆)

**현재 상태**:
- 억부용신 + 조후용신만
- 단순 비율 계산

**개선 방안**:

```python
class PreciseYongsinAnalyzer:
    """정밀 용신 분석"""

    def analyze_comprehensive_yongsin(self, saju_result):
        """종합 용신 분석"""

        # 1. 강약 용신 (抑扶用神) - 정밀
        strength = self._calculate_precise_strength(saju_result)
        strength_yongsin = self._determine_strength_yongsin(strength)

        # 2. 조후 용신 (調候用神)
        season_yongsin = self._determine_seasonal_yongsin(
            saju_result.birth_info.month,
            saju_result.day_master
        )

        # 3. 통관 용신 (通關用神)
        if self._has_direct_conflict(saju_result):
            mediator_yongsin = self._find_mediator_element(saju_result)

        # 4. 병약 용신 (病藥用神)
        if self._has_sickness(saju_result):
            cure_yongsin = self._find_cure_element(saju_result)

        # 5. 전왕 용신 (專旺用神)
        if self._is_extremely_strong(saju_result):
            # 종세(從勢)
            follow_yongsin = self._determine_follow_yongsin(saju_result)

        # 종합 판단
        return self._综合_all_yongsin_types(
            strength_yongsin,
            season_yongsin,
            mediator_yongsin,
            cure_yongsin,
            follow_yongsin
        )

    def _find_mediator_element(self, saju_result):
        """통관 용신 - 충돌하는 오행 사이를 중재"""
        # 예: 목극토 충돌 → 화(木生火, 火生土) 통관
        conflicts = self._detect_conflicts(saju_result)

        for conflict in conflicts:
            mediator = self._get_middle_element(
                conflict["element1"],
                conflict["element2"]
            )
            return mediator

        return None
```

---

### 6. ⏰ 시주 계산 정밀화 (중요도: ★★★☆☆)

**현재 상태**:
```python
# 단순 2시간 구분
hour_index = (hour + 1) // 2 % 12
```

**문제점**:
- 지역별 경도 차이 미고려
- 진시(真時) vs 표준시
- 일광절약시간 미고려

**개선 방안**:

```python
class PreciseTimeCalculator:
    """정밀 시주 계산"""

    # 주요 도시 경도
    CITY_LONGITUDE = {
        "서울": 126.9784,
        "부산": 129.0756,
        "제주": 126.5312,
        # ...
    }

    def calculate_true_time(self,
                           solar_time: datetime,
                           longitude: float = 126.9784):
        """
        진시(真時) 계산

        진시 = 표준시 + 경도차 보정
        경도 15도 = 1시간 차이
        """
        # 한국 표준시 경도 (135도, 동경)
        standard_longitude = 135.0

        # 경도 차이에 따른 시간 보정
        time_diff = (longitude - standard_longitude) * 4  # 분 단위

        true_time = solar_time + timedelta(minutes=time_diff)

        return true_time

    def get_hour_pillar_precise(self,
                                solar_time: datetime,
                                day_stem: str,
                                city: str = "서울"):
        """정밀 시주 계산"""

        # 1. 진시 변환
        longitude = self.CITY_LONGITUDE.get(city, 126.9784)
        true_time = self.calculate_true_time(solar_time, longitude)

        # 2. 시지 결정 (23-01시는 자시)
        hour = true_time.hour
        minute = true_time.minute

        # 경계선 처리 (00:00~00:59는 전날 자시)
        if hour == 0:
            # 자시 후반
            branch_index = 0
        elif hour == 23:
            # 자시 전반
            branch_index = 0
        else:
            branch_index = (hour + 1) // 2

        # 3. 시간 계산
        # ... 기존 로직

        return hour_pillar
```

---

### 7. 📅 대운 기점 정밀 계산 (중요도: ★★★☆☆)

**현재 상태**:
```python
# 단순 음양년 + 성별 조합
if is_yang_year:
    daeun_start = 10 if gender == "male" else 5
```

**문제점**:
- 실제 일수 계산 없음
- 절기까지의 정확한 거리 미고려

**개선 방안**:

```python
def calculate_precise_daeun_start(self, birth_info, month_pillar):
    """
    정밀 대운 기점 계산

    원리:
    - 양남음녀: 다음 절기까지 일수 / 3 = 대운 시작 연령
    - 음남양녀: 이전 절기부터 일수 / 3 = 대운 시작 연령
    """
    birth_date = datetime(
        birth_info.year,
        birth_info.month,
        birth_info.day
    )

    year_stem = self._get_year_stem(birth_info.year)
    is_yang_year = self._is_yang_stem(year_stem)

    if (is_yang_year and birth_info.gender == "male") or \
       (not is_yang_year and birth_info.gender == "female"):
        # 순행: 다음 절기까지
        next_solar_term = self._get_next_solar_term(birth_date)
        days_diff = (next_solar_term - birth_date).days
    else:
        # 역행: 이전 절기부터
        prev_solar_term = self._get_previous_solar_term(birth_date)
        days_diff = (birth_date - prev_solar_term).days

    # 3일 = 1년
    daeun_start_years = days_diff / 3
    daeun_start_months = (days_diff % 3) * 4

    return {
        "years": int(daeun_start_years),
        "months": int(daeun_start_months),
        "days": days_diff,
        "precise_age": daeun_start_years
    }
```

---

### 8. 🔢 신살 확장 (중요도: ★★★☆☆)

**현재 상태**:
- 7가지 기본 신살

**추가 가능한 신살**:

```python
ADDITIONAL_DIVINE_SPIRITS = {
    # 학당귀인 (學堂貴人) - 학문 재능
    "학당귀인": {
        "갑": "사",
        "을": "오",
        # ...
    },

    # 문창귀인 (文昌貴人) - 문학 재능
    "문창귀인": {
        "갑": "사",
        "을": "오",
        # ...
    },

    # 금여귀인 (金輿貴人) - 부귀
    "금여귀인": {
        "갑": "인",
        "을": "해",
        # ...
    },

    # 월덕귀인 (月德貴人)
    "월덕귀인": {
        1: "병",  # 정월
        2: "갑",  # 2월
        # ...
    },

    # 천덕귀인 (天德貴人)
    "천덕귀인": {
        1: "정",  # 정월
        2: "신",  # 2월
        # ...
    },

    # 괴강살 (魁罡殺) - 이미 구현됨
    # 고란살 (孤鸞殺) - 독신
    "고란살": ["갑인", "을사", "무신", "임자", "계축"],

    # 홍염살 (紅艶殺) - 이성 관계
    "홍염살": {
        "갑": "오",
        "을": "신",
        # ...
    }
}
```

---

### 9. 🎲 상신 계산 (중요도: ★★☆☆☆)

**새로운 기능**:

```python
class SangsinAnalyzer:
    """상신(相神) 분석 - 용신을 돕는 신"""

    def find_sangsin(self, yongsin, saju_result):
        """
        상신 찾기

        상신 = 용신을 생하거나 보호하는 오행
        """
        sangsin_candidates = []

        # 1. 용신을 생하는 오행
        supporting = self._get_supporting_element(yongsin)
        sangsin_candidates.append(supporting)

        # 2. 기신을 제어하는 오행
        gisin = saju_result.yongsin["gisin"]["element"]
        controlling = self._get_controlling_element(gisin)
        sangsin_candidates.append(controlling)

        return sangsin_candidates
```

---

## 우선순위별 구현 계획

### 🔴 높음 (즉시 구현 권장)

1. **지지 장간 구현** (2-3일)
   - 정확도 향상: ★★★★★
   - 구현 난이도: ⭐⭐
   - 영향 범위: 십성, 오행, 격국, 용신 전체

2. **오행 강약 정밀 계산** (3-4일)
   - 정확도 향상: ★★★★★
   - 구현 난이도: ⭐⭐⭐
   - 영향 범위: 용신, 격국

3. **절기 정확도 개선** (2-3일)
   - 정확도 향상: ★★★★★
   - 구현 난이도: ⭐⭐⭐⭐
   - 영향 범위: 월주, 대운

### 🟡 중간 (단계적 구현)

4. **격국 판단 고도화** (4-5일)
   - 정확도 향상: ★★★★☆
   - 구현 난이도: ⭐⭐⭐⭐
   - 영향 범위: 격국 분석

5. **용신 선정 정밀화** (3-4일)
   - 정확도 향상: ★★★★☆
   - 구현 난이도: ⭐⭐⭐⭐
   - 영향 범위: 용신 분석

6. **대운 기점 정밀 계산** (2일)
   - 정확도 향상: ★★★☆☆
   - 구현 난이도: ⭐⭐⭐
   - 영향 범위: 대운

### 🟢 낮음 (선택적 구현)

7. **시주 진시 계산** (2일)
   - 정확도 향상: ★★☆☆☆
   - 구현 난이도: ⭐⭐
   - 영향 범위: 시주

8. **추가 신살 구현** (3-4일)
   - 정확도 향상: ★★☆☆☆
   - 구현 난이도: ⭐⭐
   - 영향 범위: 신살 분석

9. **상신 분석** (1-2일)
   - 정확도 향상: ★★☆☆☆
   - 구현 난이도: ⭐
   - 영향 범위: 용신 분석

---

## 구현 예상 일정

### Phase 1: 핵심 정확도 개선 (1-2주)
- [ ] 지지 장간 구현
- [ ] 오행 강약 정밀 계산
- [ ] 절기 정확도 개선 (PyMeeus 또는 KASI API)

### Phase 2: 분석 고도화 (2-3주)
- [ ] 격국 판단 고도화 (특수격, 파격)
- [ ] 용신 선정 정밀화 (통관, 병약, 전왕)
- [ ] 대운 기점 정밀 계산

### Phase 3: 세부 개선 (1-2주)
- [ ] 시주 진시 계산
- [ ] 추가 신살 구현
- [ ] 상신 분석
- [ ] 테스트 및 검증

**총 예상 기간**: 4-7주

---

## 검증 방법

### 1. 기준 사주 테스트 세트
```python
TEST_CASES = [
    {
        "name": "현대 명리학자 合意 사례 1",
        "birth": "1990-05-15 14:30",
        "expected": {
            "day_master_strength": "왕",
            "gyeokguk": "건록격",
            "yongsin": "수"
        }
    },
    # ... 100개 이상의 검증된 사례
]
```

### 2. 전문가 검수
- 명리학 전문가와 협업
- 실제 사례 비교 검증

### 3. A/B 테스트
- 기존 시스템 vs 개선 시스템
- 정확도 비교 분석

---

## 결론

정확도를 높이기 위해 **지지 장간**, **오행 강약**, **절기 정확도** 3가지를
우선적으로 구현하는 것을 강력히 권장합니다.

이 3가지만으로도 현재 대비 **30-40% 정확도 향상**을 기대할 수 있습니다.
