"""
사주 API 사용 예제
Python에서 API를 호출하는 방법을 보여줍니다
"""

import requests
import json

# API 베이스 URL
BASE_URL = "http://localhost:8000/api/v1"


def test_health_check():
    """헬스체크 테스트"""
    print("=" * 60)
    print("1. 헬스체크 테스트")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_calculate_saju():
    """사주 계산 테스트"""
    print("=" * 60)
    print("2. 사주 계산 테스트")
    print("=" * 60)

    birth_info = {
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "gender": "male"
    }

    response = requests.post(
        f"{BASE_URL}/calculate",
        json=birth_info
    )

    if response.status_code == 200:
        data = response.json()
        print(f"생년월일시: {data['birth_info']['year']}년 {data['birth_info']['month']}월 {data['birth_info']['day']}일 {data['birth_info']['hour']}시")
        print(f"\n사주팔자:")
        print(f"  년주(年柱): {data['year_pillar']['heavenly_stem']}{data['year_pillar']['earthly_branch']}")
        print(f"  월주(月柱): {data['month_pillar']['heavenly_stem']}{data['month_pillar']['earthly_branch']}")
        print(f"  일주(日柱): {data['day_pillar']['heavenly_stem']}{data['day_pillar']['earthly_branch']}")
        print(f"  시주(時柱): {data['hour_pillar']['heavenly_stem']}{data['hour_pillar']['earthly_branch']}")
        print(f"\n일간(日干): {data['day_master']}")

        print(f"\n오행 분포:")
        elements = data['five_elements']
        print(f"  목(木): {elements['wood']}개")
        print(f"  화(火): {elements['fire']}개")
        print(f"  토(土): {elements['earth']}개")
        print(f"  금(金): {elements['metal']}개")
        print(f"  수(水): {elements['water']}개")

        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def test_full_analysis():
    """전체 분석 테스트 (계산 + 해석)"""
    print("\n" + "=" * 60)
    print("3. 전체 분석 테스트 (계산 + AI 해석)")
    print("=" * 60)

    request_data = {
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "gender": "male"
        },
        "question": "전체적인 성격과 운세를 알려주세요",
        "detail_level": "normal",
        "tone": "friendly"
    }

    print("⏳ AI 해석 생성 중... (10-20초 소요)")

    try:
        response = requests.post(
            f"{BASE_URL}/full-analysis",
            json=request_data,
            timeout=60  # 60초 타임아웃
        )

        if response.status_code == 200:
            data = response.json()

            print("\n" + "=" * 60)
            print("📊 사주 계산 결과")
            print("=" * 60)
            saju = data['saju_result']
            print(f"사주팔자: {saju['year_pillar']['heavenly_stem']}{saju['year_pillar']['earthly_branch']} "
                  f"{saju['month_pillar']['heavenly_stem']}{saju['month_pillar']['earthly_branch']} "
                  f"{saju['day_pillar']['heavenly_stem']}{saju['day_pillar']['earthly_branch']} "
                  f"{saju['hour_pillar']['heavenly_stem']}{saju['hour_pillar']['earthly_branch']}")

            print("\n" + "=" * 60)
            print("🤖 AI 해석 결과")
            print("=" * 60)
            interpretation = data['interpretation']
            print(interpretation['interpretation'])

            print(f"\n📈 사용 정보:")
            print(f"  - 토큰 사용: {interpretation.get('tokens_used', 'N/A')}개")
            print(f"  - 캐시 사용: {'예' if interpretation.get('cached', False) else '아니오'}")
            print(f"  - 다룬 주제: {', '.join(interpretation.get('topics_covered', []))}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("❌ 타임아웃 오류: 서버 응답 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")


def test_specific_question():
    """특정 질문 테스트"""
    print("\n" + "=" * 60)
    print("4. 특정 질문 테스트 (연애운)")
    print("=" * 60)

    request_data = {
        "birth_info": {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "gender": "female"
        },
        "question": "제 연애운과 결혼운은 어떤가요?",
        "detail_level": "detailed",
        "tone": "friendly"
    }

    print("⏳ AI 해석 생성 중...")

    try:
        response = requests.post(
            f"{BASE_URL}/full-analysis",
            json=request_data,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print("💕 연애운 해석")
            print("=" * 60)
            print(data['interpretation']['interpretation'])
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")


def main():
    """메인 함수"""
    print("\n🔮 사주 API 사용 예제\n")

    # 1. 헬스체크
    test_health_check()

    # 2. 사주 계산만
    test_calculate_saju()

    # 서버가 실행중이고 API 키가 설정되어 있는지 확인
    print("\n⚠️  다음 테스트는 Anthropic API 키가 필요합니다.")
    print("    .env 파일에 ANTHROPIC_API_KEY가 설정되어 있는지 확인하세요.")

    user_input = input("\n계속하시겠습니까? (y/n): ")
    if user_input.lower() != 'y':
        print("\n테스트를 종료합니다.")
        return

    # 3. 전체 분석 (계산 + 해석)
    test_full_analysis()

    # 4. 특정 질문
    user_input = input("\n특정 질문 테스트를 진행하시겠습니까? (y/n): ")
    if user_input.lower() == 'y':
        test_specific_question()

    print("\n✅ 모든 테스트가 완료되었습니다!")
    print("📖 더 많은 정보는 http://localhost:8000/docs 에서 확인하세요.")


if __name__ == "__main__":
    main()
