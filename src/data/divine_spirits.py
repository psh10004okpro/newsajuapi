"""
신살(神殺) 데이터
사주에 영향을 미치는 특별한 별(神)과 살(殺)

주요 신살:
- 천을귀인(天乙貴人): 귀인의 도움
- 역마(驛馬): 이동, 변화
- 도화(桃花): 인기, 연애
- 화개(華蓋): 예술, 종교
- 천간귀인: 권력, 명예
- 공망(空亡): 비어있음
"""

# 천을귀인(天乙貴人) - 가장 중요한 길신
# 일간 또는 년간 기준으로 판단
CHEON_EUL_GWIIN = {
    "갑": ["축", "미"],
    "을": ["신", "자"],
    "병": ["해", "유"],
    "정": ["해", "유"],
    "무": ["축", "미"],
    "기": ["신", "자"],
    "경": ["축", "미"],
    "신": ["인", "오"],
    "임": ["묘", "사"],
    "계": ["묘", "사"]
}

# 역마살(驛馬殺) - 이동, 변화, 활동
# 일지 또는 년지 기준
YEOKMA = {
    "인": ["신"],
    "오": ["신"],
    "술": ["신"],
    "신": ["인"],
    "자": ["인"],
    "진": ["인"],
    "사": ["해"],
    "유": ["해"],
    "축": ["해"],
    "해": ["사"],
    "묘": ["사"],
    "미": ["사"]
}

# 도화살(桃花殺) - 인기, 매력, 이성운
# 일지 또는 년지 기준
DOHWA = {
    "인": ["묘"],
    "오": ["묘"],
    "술": ["묘"],
    "신": ["유"],
    "자": ["유"],
    "진": ["유"],
    "사": ["오"],
    "유": ["오"],
    "축": ["오"],
    "해": ["자"],
    "묘": ["자"],
    "미": ["자"]
}

# 화개살(華蓋殺) - 예술, 학문, 종교
# 일지 또는 년지 기준
HWAGAE = {
    "인": ["술"],
    "오": ["술"],
    "술": ["술"],
    "신": ["진"],
    "자": ["진"],
    "진": ["진"],
    "사": ["축"],
    "유": ["축"],
    "축": ["축"],
    "해": ["미"],
    "묘": ["미"],
    "미": ["미"]
}

# 괴강살(魁罡殺) - 강한 성격, 리더십
# 일주 기준
GOEGANG_PILLARS = [
    ("경", "진"),
    ("경", "술"),
    ("임", "진"),
    ("무", "술")
]

# 양인살(羊刃殺) - 강하지만 과격함
# 일간 기준
YANGIN = {
    "갑": ["묘"],
    "을": ["인"],
    "병": ["오"],
    "정": ["사"],
    "무": ["오"],
    "기": ["사"],
    "경": ["유"],
    "신": ["신"],
    "임": ["자"],
    "계": ["해"]
}

# 공망(空亡) - 육갑공망
# 일주 또는 년주의 천간으로 판단
GONGMANG = {
    "갑자": ["술", "해"],
    "갑술": ["신", "유"],
    "갑신": ["오", "미"],
    "갑오": ["진", "사"],
    "갑진": ["인", "묘"],
    "갑인": ["자", "축"]
}

# 신살 설명
DIVINE_SPIRITS_DESC = {
    "천을귀인": {
        "name": "천을귀인(天乙貴人)",
        "type": "길신",
        "effect": "매우 긍정적",
        "description": "귀인의 도움을 받는 운, 위기에서 구원",
        "characteristics": ["귀인의 도움", "위기 탈출", "좋은 인연", "성공"],
        "advice": "어려울 때 주변의 도움을 받을 수 있습니다"
    },
    "역마": {
        "name": "역마(驛馬)",
        "type": "동적",
        "effect": "중립",
        "description": "이동과 변화의 운, 활동적",
        "characteristics": ["이동", "변화", "활동", "여행", "바쁨"],
        "advice": "변화와 이동이 많은 시기, 안정보다는 역동적인 삶"
    },
    "도화": {
        "name": "도화(桃花)",
        "type": "인기",
        "effect": "긍정적/주의",
        "description": "인기와 매력, 이성운",
        "characteristics": ["인기", "매력", "이성운", "사교성", "예술"],
        "advice": "인기가 많고 이성운이 좋으나, 유혹에 주의"
    },
    "화개": {
        "name": "화개(華蓋)",
        "type": "예술/학문",
        "effect": "긍정적",
        "description": "예술, 학문, 종교적 재능",
        "characteristics": ["예술", "학문", "종교", "철학", "독특함"],
        "advice": "예술이나 학문 분야에서 재능 발휘"
    },
    "괴강": {
        "name": "괴강(魁罡)",
        "type": "강함",
        "effect": "강력",
        "description": "강한 성격과 리더십",
        "characteristics": ["강함", "리더십", "결단력", "고집"],
        "advice": "강한 성격으로 리더 자질이 있으나, 융통성 필요"
    },
    "양인": {
        "name": "양인(羊刃)",
        "type": "과격",
        "effect": "주의",
        "description": "강하지만 과격할 수 있음",
        "characteristics": ["강함", "과격", "용기", "사고 위험"],
        "advice": "강하고 용감하나, 사고나 다툼 주의"
    },
    "공망": {
        "name": "공망(空亡)",
        "type": "빈곳",
        "effect": "부정적",
        "description": "비어있어 힘을 잃음",
        "characteristics": ["비어있음", "힘없음", "허무함", "손실"],
        "advice": "해당 영역에서 힘을 잃거나 손실 가능성"
    }
}


def check_divine_spirits(year_stem, year_branch, day_stem, day_branch, pillars):
    """
    신살 확인

    Args:
        year_stem: 년간
        year_branch: 년지
        day_stem: 일간
        day_branch: 일지
        pillars: 사주 4기둥 리스트

    Returns:
        발견된 신살 리스트
    """
    found_spirits = []

    # 모든 지지 추출
    all_branches = [p.earthly_branch for p in pillars]

    # 1. 천을귀인 (일간 기준)
    if day_stem in CHEON_EUL_GWIIN:
        gwiin_branches = CHEON_EUL_GWIIN[day_stem]
        for branch in all_branches:
            if branch in gwiin_branches:
                found_spirits.append({
                    "name": "천을귀인",
                    "location": branch,
                    **DIVINE_SPIRITS_DESC["천을귀인"]
                })
                break

    # 2. 역마 (일지 기준)
    if day_branch in YEOKMA:
        yeokma_branches = YEOKMA[day_branch]
        for branch in all_branches:
            if branch in yeokma_branches:
                found_spirits.append({
                    "name": "역마",
                    "location": branch,
                    **DIVINE_SPIRITS_DESC["역마"]
                })
                break

    # 3. 도화 (일지 기준)
    if day_branch in DOHWA:
        dohwa_branches = DOHWA[day_branch]
        for branch in all_branches:
            if branch in dohwa_branches:
                found_spirits.append({
                    "name": "도화",
                    "location": branch,
                    **DIVINE_SPIRITS_DESC["도화"]
                })
                break

    # 4. 화개 (일지 기준)
    if day_branch in HWAGAE:
        hwagae_branches = HWAGAE[day_branch]
        for branch in all_branches:
            if branch in hwagae_branches:
                found_spirits.append({
                    "name": "화개",
                    "location": branch,
                    **DIVINE_SPIRITS_DESC["화개"]
                })
                break

    # 5. 괴강 (일주)
    if (day_stem, day_branch) in GOEGANG_PILLARS:
        found_spirits.append({
            "name": "괴강",
            "location": "일주",
            **DIVINE_SPIRITS_DESC["괴강"]
        })

    # 6. 양인 (일간 기준)
    if day_stem in YANGIN:
        yangin_branches = YANGIN[day_stem]
        for branch in all_branches:
            if branch in yangin_branches:
                found_spirits.append({
                    "name": "양인",
                    "location": branch,
                    **DIVINE_SPIRITS_DESC["양인"]
                })
                break

    # 7. 공망 (간단 버전 - 일지 기준)
    # 정확한 공망은 육갑 조합으로 판단해야 하지만, 여기서는 간소화
    for key, gongmang_branches in GONGMANG.items():
        if day_stem + day_branch == key or day_stem in key[:1]:
            for branch in all_branches:
                if branch in gongmang_branches:
                    found_spirits.append({
                        "name": "공망",
                        "location": branch,
                        **DIVINE_SPIRITS_DESC["공망"]
                    })
                    break

    return found_spirits
