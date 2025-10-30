"""
24절기 데이터 생성 스크립트
1900년부터 2050년까지의 24절기 절입시각을 계산

참고: 실제 천문 계산은 매우 복잡하므로, 여기서는 근사값을 사용합니다.
정확한 데이터는 한국천문연구원 API를 통해 가져오는 것이 좋습니다.
"""

from datetime import datetime, timedelta
import json

# 24절기 (절월 기준)
SOLAR_TERMS = [
    "입춘", "우수", "경칩", "춘분", "청명", "곡우",
    "입하", "소만", "망종", "하지", "소서", "대서",
    "입추", "처서", "백로", "추분", "한로", "상강",
    "입동", "소설", "대설", "동지", "소한", "대한"
]

# 기준년도의 절기 날짜 (2000년 기준, 대략적인 날짜)
BASE_YEAR = 2000
BASE_SOLAR_TERMS = {
    "입춘": (2, 4, 6, 30),   # 월, 일, 시, 분
    "우수": (2, 19, 13, 0),
    "경칩": (3, 5, 19, 30),
    "춘분": (3, 20, 13, 30),
    "청명": (4, 4, 22, 0),
    "곡우": (4, 20, 7, 0),
    "입하": (5, 5, 15, 30),
    "소만": (5, 21, 0, 0),
    "망종": (6, 5, 19, 30),
    "하지": (6, 21, 8, 0),
    "소서": (7, 7, 3, 30),
    "대서": (7, 22, 20, 0),
    "입추": (8, 7, 17, 30),
    "처서": (8, 23, 9, 0),
    "백로": (9, 7, 19, 30),
    "추분": (9, 23, 2, 30),
    "한로": (10, 8, 13, 0),
    "상강": (10, 23, 18, 0),
    "입동": (11, 7, 8, 30),
    "소설": (11, 22, 10, 0),
    "대설": (12, 7, 1, 0),
    "동지": (12, 21, 20, 30),
    "소한": (1, 5, 17, 0),
    "대한": (1, 20, 11, 30)
}


def generate_solar_term_date(year: int, term: str) -> str:
    """
    특정 년도의 특정 절기 날짜 계산

    주의: 이것은 근사값입니다. 실제로는 천문학적 계산이 필요합니다.
    """
    base_month, base_day, base_hour, base_minute = BASE_SOLAR_TERMS[term]

    # 년도 차이 계산
    year_diff = year - BASE_YEAR

    # 대략적인 조정 (실제로는 훨씬 복잡)
    # 절기는 평균적으로 365.2422일 주기
    # 4년마다 윤년으로 하루씩 늦춰짐

    # 간단한 보정: 4년마다 -1일 (윤년 효과)
    day_adjustment = -(year_diff // 4)

    # 소한, 대한은 작년 기준
    if term in ["소한", "대한"]:
        year_for_date = year
    else:
        year_for_date = year

    try:
        # 기준 날짜 생성
        dt = datetime(year_for_date, base_month, base_day, base_hour, base_minute)

        # 일 조정 적용
        dt = dt + timedelta(days=day_adjustment)

        # 추가 미세 조정 (년도에 따른 변화)
        # 실제로는 더 복잡한 천문 계산 필요
        minute_adjustment = (year_diff % 4) * 6  # 4년 주기로 약 24분 변화
        dt = dt + timedelta(minutes=minute_adjustment)

        return dt.strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        # 날짜가 유효하지 않은 경우 (예: 2월 30일)
        # 말일로 조정
        if base_day > 28:
            dt = datetime(year_for_date, base_month, 28, base_hour, base_minute)
            dt = dt + timedelta(days=day_adjustment)
            return dt.strftime("%Y-%m-%dT%H:%M")
        else:
            return None


def generate_all_solar_terms(start_year: int = 1900, end_year: int = 2050) -> dict:
    """
    지정된 년도 범위의 모든 24절기 데이터 생성
    """
    data = {
        "description": "24절기 절입시각 데이터 (한국 표준시 기준)",
        "note": "이 데이터는 근사값입니다. 정확한 계산은 천문학적 알고리즘이 필요합니다.",
        "source": "계산된 근사값 (실제 사용시 한국천문연구원 데이터 권장)",
        "solar_terms": {}
    }

    for year in range(start_year, end_year + 1):
        year_data = {}

        for term in SOLAR_TERMS:
            date_str = generate_solar_term_date(year, term)
            if date_str:
                year_data[term] = date_str

        data["solar_terms"][str(year)] = year_data

    # 월별 절기 매핑 추가
    data["monthly_solar_terms"] = {
        "1": "소한",
        "2": "입춘",
        "3": "경칩",
        "4": "청명",
        "5": "입하",
        "6": "망종",
        "7": "소서",
        "8": "입추",
        "9": "백로",
        "10": "한로",
        "11": "입동",
        "12": "대설"
    }

    # 절기 순서 정보
    data["solar_terms_order"] = SOLAR_TERMS

    return data


def main():
    """메인 함수"""
    print("24절기 데이터 생성 시작...")
    print("년도 범위: 1900 ~ 2050")

    data = generate_all_solar_terms(1900, 2050)

    # JSON 파일로 저장
    output_file = "solar_terms_1900_2050.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 완료! {output_file} 파일이 생성되었습니다.")
    print(f"📊 총 {len(data['solar_terms'])}년치 데이터 생성됨")
    print(f"📅 각 년도당 {len(SOLAR_TERMS)}개 절기")

    # 샘플 출력
    print("\n📌 샘플 데이터 (2024년):")
    if "2024" in data["solar_terms"]:
        for term, date in list(data["solar_terms"]["2024"].items())[:5]:
            print(f"  {term}: {date}")


if __name__ == "__main__":
    main()
