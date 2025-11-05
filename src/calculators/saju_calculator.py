"""
사주 계산 엔진
생년월일시를 천간지지 사주팔자로 변환하고, 십성, 오행, 대운을 계산
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import os
from korean_lunar_calendar import KoreanLunarCalendar

from src.models.saju import (
    BirthInfo, SajuPillar, SajuResult, TenGods, FiveElements, DaeunPeriod, SaeunYear
)
from src.data.twelve_spirits import get_twelve_spirit
from src.data.divine_spirits import check_divine_spirits
from src.data.sixty_jiazi import get_jiazi_info
from src.data.harmony_conflict import check_harmony_conflict
from src.data.gongmang import check_gongmang_in_saju
from src.calculators.gyeokguk_analyzer import GyeokgukAnalyzer
from src.calculators.yongsin_analyzer import YongsinAnalyzer


class SajuCalculator:
    """사주 계산기"""

    # 천간 (10개): 甲乙丙丁戊己庚辛壬癸
    HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]

    # 지지 (12개): 子丑寅卯辰巳午未申酉戌亥
    EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

    # 오행 매핑
    ELEMENT_MAP = {
        # 천간
        "갑": "목", "을": "목",
        "병": "화", "정": "화",
        "무": "토", "기": "토",
        "경": "금", "신": "금",
        "임": "수", "계": "수",
        # 지지
        "인": "목", "묘": "목",
        "사": "화", "오": "화",
        "진": "토", "술": "토", "축": "토", "미": "토",
        "신": "금", "유": "금",
        "해": "수", "자": "수"
    }

    # 십성 매핑 (일간 기준으로 다른 천간/지지를 판단)
    # 일간의 오행을 기준으로: 나(일간) vs 대상의 관계
    TEN_GODS_MAP = {
        # (일간 오행, 대상 오행, 음양 관계) -> 십성
        # 같은 오행
        ("목", "목", "same"): "비견",
        ("목", "목", "diff"): "겁재",
        ("화", "화", "same"): "비견",
        ("화", "화", "diff"): "겁재",
        ("토", "토", "same"): "비견",
        ("토", "토", "diff"): "겁재",
        ("금", "금", "same"): "비견",
        ("금", "금", "diff"): "겁재",
        ("수", "수", "same"): "비견",
        ("수", "수", "diff"): "겁재",

        # 내가 생하는 오행 (식상)
        ("목", "화", "same"): "식신",
        ("목", "화", "diff"): "상관",
        ("화", "토", "same"): "식신",
        ("화", "토", "diff"): "상관",
        ("토", "금", "same"): "식신",
        ("토", "금", "diff"): "상관",
        ("금", "수", "same"): "식신",
        ("금", "수", "diff"): "상관",
        ("수", "목", "same"): "식신",
        ("수", "목", "diff"): "상관",

        # 내가 극하는 오행 (재성)
        ("목", "토", "same"): "편재",
        ("목", "토", "diff"): "정재",
        ("화", "금", "same"): "편재",
        ("화", "금", "diff"): "정재",
        ("토", "수", "same"): "편재",
        ("토", "수", "diff"): "정재",
        ("금", "목", "same"): "편재",
        ("금", "목", "diff"): "정재",
        ("수", "화", "same"): "편재",
        ("수", "화", "diff"): "정재",

        # 나를 극하는 오행 (관성)
        ("목", "금", "same"): "편관",
        ("목", "금", "diff"): "정관",
        ("화", "수", "same"): "편관",
        ("화", "수", "diff"): "정관",
        ("토", "목", "same"): "편관",
        ("토", "목", "diff"): "정관",
        ("금", "화", "same"): "편관",
        ("금", "화", "diff"): "정관",
        ("수", "토", "same"): "편관",
        ("수", "토", "diff"): "정관",

        # 나를 생하는 오행 (인성)
        ("목", "수", "same"): "편인",
        ("목", "수", "diff"): "정인",
        ("화", "목", "same"): "편인",
        ("화", "목", "diff"): "정인",
        ("토", "화", "same"): "편인",
        ("토", "화", "diff"): "정인",
        ("금", "토", "same"): "편인",
        ("금", "토", "diff"): "정인",
        ("수", "금", "same"): "편인",
        ("수", "금", "diff"): "정인",
    }

    def __init__(self):
        """초기화"""
        # 24절기 데이터 로드
        self.solar_terms = self._load_solar_terms()

    def _load_solar_terms(self) -> Dict:
        """24절기 데이터 로드 (1900-2050년 전체)"""
        # 먼저 전체 데이터 파일 시도
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "solar_terms_1900_2050.json"
        )
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 전체 데이터 파일이 없으면 샘플 데이터 사용
            fallback_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "solar_terms_2024_2025.json"
            )
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                # 데이터 파일이 없으면 빈 딕셔너리 반환
                return {"solar_terms": {}}

    def calculate(self, birth_info: BirthInfo) -> SajuResult:
        """
        생년월일시로부터 사주팔자를 계산

        Args:
            birth_info: 생년월일시 정보

        Returns:
            SajuResult: 계산된 사주 정보
        """
        # 1. 년주 계산 (입춘 기준)
        year_pillar = self._calculate_year_pillar(
            birth_info.year, birth_info.month, birth_info.day
        )

        # 2. 월주 계산 (절기 기준)
        month_pillar = self._calculate_month_pillar(
            birth_info.year, birth_info.month, birth_info.day, year_pillar
        )

        # 3. 일주 계산
        day_pillar = self._calculate_day_pillar(
            birth_info.year, birth_info.month, birth_info.day
        )

        # 4. 시주 계산
        hour_pillar = self._calculate_hour_pillar(
            birth_info.hour, day_pillar
        )

        # 5. 일간 (본인의 중심)
        day_master = day_pillar.heavenly_stem

        # 6. 십성 계산
        ten_gods = self._calculate_ten_gods(
            day_master, year_pillar, month_pillar, day_pillar, hour_pillar
        )

        # 7. 오행 계산
        five_elements = self._calculate_five_elements(
            year_pillar, month_pillar, day_pillar, hour_pillar
        )

        # 8. 대운 계산
        daeun_periods = self._calculate_daeun(
            birth_info, year_pillar, month_pillar
        )

        # 9. 세운 계산 (현재 년도 기준 전후 5년)
        current_year = datetime.now().year
        saeun_years = self._calculate_saeun(
            birth_info, current_year - 2, current_year + 5
        )

        # 10. 음력 정보 계산
        lunar_date = self._calculate_lunar_date(
            birth_info.year, birth_info.month, birth_info.day
        )

        # 11. 십이운성 계산 (각 기둥별)
        twelve_spirits = self._calculate_twelve_spirits(
            day_master, year_pillar, month_pillar, day_pillar, hour_pillar
        )

        # 12. 신살 확인
        divine_spirits = check_divine_spirits(
            year_pillar.heavenly_stem,
            year_pillar.earthly_branch,
            day_master,
            day_pillar.earthly_branch,
            [year_pillar, month_pillar, day_pillar, hour_pillar]
        )

        # 13. 60갑자 일주 특성
        jiazi_info = get_jiazi_info(str(day_pillar))

        # 14. 합충형해파 관계
        harmony_conflict = check_harmony_conflict(
            [year_pillar, month_pillar, day_pillar, hour_pillar]
        )

        # 15. 공망 분석
        gongmang = check_gongmang_in_saju(
            str(day_pillar),
            year_pillar.earthly_branch,
            month_pillar.earthly_branch,
            day_pillar.earthly_branch,
            hour_pillar.earthly_branch
        )

        # 16. 격국 분석
        gyeokguk_analyzer = GyeokgukAnalyzer(self)
        gyeokguk = gyeokguk_analyzer.analyze_gyeokguk(
            day_master,
            month_pillar.earthly_branch,
            year_pillar.heavenly_stem,
            month_pillar.heavenly_stem,
            day_master,
            hour_pillar.heavenly_stem,
            ten_gods
        )

        # 17. 용신 분석
        yongsin_analyzer = YongsinAnalyzer(self.ELEMENT_MAP)
        yongsin = yongsin_analyzer.analyze_yongsin(
            day_master,
            {
                "wood": five_elements.wood,
                "fire": five_elements.fire,
                "earth": five_elements.earth,
                "metal": five_elements.metal,
                "water": five_elements.water
            },
            month_pillar.earthly_branch,
            birth_info.month
        )

        return SajuResult(
            birth_info=birth_info,
            year_pillar=year_pillar,
            month_pillar=month_pillar,
            day_pillar=day_pillar,
            hour_pillar=hour_pillar,
            day_master=day_master,
            ten_gods=ten_gods,
            five_elements=five_elements,
            daeun_periods=daeun_periods,
            saeun_years=saeun_years,
            lunar_date=lunar_date,
            twelve_spirits=twelve_spirits,
            divine_spirits=divine_spirits,
            jiazi_info=jiazi_info,
            harmony_conflict=harmony_conflict,
            gongmang=gongmang,
            gyeokguk=gyeokguk,
            yongsin=yongsin
        )

    def _calculate_year_pillar(self, year: int, month: int, day: int) -> SajuPillar:
        """
        년주 계산
        입춘(2월 4일경) 이전이면 전년도로 계산
        """
        # 입춘 확인 (간단히 2월 4일 기준)
        # 실제로는 solar_terms 데이터에서 정확한 입춘 시각을 확인해야 함
        saju_year = year
        if month < 2 or (month == 2 and day < 4):
            saju_year = year - 1

        # 갑자년은 1984년 (갑자 = 천간[0] + 지지[0])
        # 천간은 10년 주기, 지지는 12년 주기
        base_year = 1984
        year_diff = saju_year - base_year

        stem_index = year_diff % 10
        branch_index = year_diff % 12

        return SajuPillar(
            heavenly_stem=self.HEAVENLY_STEMS[stem_index],
            earthly_branch=self.EARTHLY_BRANCHES[branch_index]
        )

    def _calculate_month_pillar(
        self, year: int, month: int, day: int, year_pillar: SajuPillar
    ) -> SajuPillar:
        """
        월주 계산
        각 달의 절기(입춘, 경칩, 청명...)를 기준으로 계산
        """
        # 월주는 년간에 따라 정해진 패턴이 있음
        # 갑기년: 병인월부터, 을경년: 무인월부터, 병신년: 경인월부터,
        # 정임년: 임인월부터, 무계년: 갑인월부터

        year_stem = year_pillar.heavenly_stem
        year_stem_index = self.HEAVENLY_STEMS.index(year_stem)

        # 월주의 지지는 고정 (인월부터 시작)
        # 인(2월), 묘(3월), 진(4월), 사(5월), 오(6월), 미(7월),
        # 신(8월), 유(9월), 술(10월), 해(11월), 자(12월), 축(1월)

        # 월주 지지 매핑 (절기 기준)
        month_branches = {
            2: 0,   # 인월 (입춘 ~ 경칩)
            3: 1,   # 묘월 (경칩 ~ 청명)
            4: 2,   # 진월 (청명 ~ 입하)
            5: 3,   # 사월 (입하 ~ 망종)
            6: 4,   # 오월 (망종 ~ 소서)
            7: 5,   # 미월 (소서 ~ 입추)
            8: 6,   # 신월 (입추 ~ 백로)
            9: 7,   # 유월 (백로 ~ 한로)
            10: 8,  # 술월 (한로 ~ 입동)
            11: 9,  # 해월 (입동 ~ 대설)
            12: 10, # 자월 (대설 ~ 소한)
            1: 11   # 축월 (소한 ~ 입춘)
        }

        branch_offset = month_branches.get(month, 0)
        branch_index = (2 + branch_offset) % 12  # 인(2)부터 시작

        # 월주 천간 계산
        # 갑기년(0,5): 병인월(2)부터 시작
        # 을경년(1,6): 무인월(4)부터 시작
        # 병신년(2,7): 경인월(6)부터 시작
        # 정임년(3,8): 임인월(8)부터 시작
        # 무계년(4,9): 갑인월(0)부터 시작

        stem_start_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}
        stem_start = stem_start_map[year_stem_index]
        stem_index = (stem_start + branch_offset) % 10

        return SajuPillar(
            heavenly_stem=self.HEAVENLY_STEMS[stem_index],
            earthly_branch=self.EARTHLY_BRANCHES[branch_index]
        )

    def _calculate_day_pillar(self, year: int, month: int, day: int) -> SajuPillar:
        """
        일주 계산
        만세력을 기준으로 계산 (기준일로부터의 일수 차이)
        """
        # 기준일: 1900년 1월 1일 = 경진일 (천간 6, 지지 4)
        base_date = datetime(1900, 1, 1)
        target_date = datetime(year, month, day)

        days_diff = (target_date - base_date).days

        # 1900-01-01이 경진일이므로
        stem_index = (6 + days_diff) % 10
        branch_index = (4 + days_diff) % 12

        return SajuPillar(
            heavenly_stem=self.HEAVENLY_STEMS[stem_index],
            earthly_branch=self.EARTHLY_BRANCHES[branch_index]
        )

    def _calculate_hour_pillar(self, hour: int, day_pillar: SajuPillar) -> SajuPillar:
        """
        시주 계산
        23시 ~ 01시: 자시, 01시 ~ 03시: 축시, ...
        """
        # 시간을 시지로 변환
        # 23-01시: 자(0), 01-03시: 축(1), 03-05시: 인(2), ...
        if hour == 23:
            hour_branch_index = 0
        else:
            hour_branch_index = (hour + 1) // 2

        # 시주 천간은 일간에 따라 정해짐
        day_stem = day_pillar.heavenly_stem
        day_stem_index = self.HEAVENLY_STEMS.index(day_stem)

        # 갑기일: 갑자시부터, 을경일: 병자시부터, ...
        stem_start_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
        stem_start = stem_start_map[day_stem_index]
        stem_index = (stem_start + hour_branch_index) % 10

        return SajuPillar(
            heavenly_stem=self.HEAVENLY_STEMS[stem_index],
            earthly_branch=self.EARTHLY_BRANCHES[hour_branch_index]
        )

    def _is_same_yin_yang(self, item1: str, item2: str) -> bool:
        """두 천간 또는 지지의 음양이 같은지 판단"""
        # 천간 또는 지지 리스트에서 인덱스 찾기
        try:
            index1 = self.HEAVENLY_STEMS.index(item1)
        except ValueError:
            try:
                index1 = self.EARTHLY_BRANCHES.index(item1)
            except ValueError:
                return False

        try:
            index2 = self.HEAVENLY_STEMS.index(item2)
        except ValueError:
            try:
                index2 = self.EARTHLY_BRANCHES.index(item2)
            except ValueError:
                return False

        # 짝수 인덱스는 양(陽), 홀수 인덱스는 음(陰)
        return (index1 % 2) == (index2 % 2)

    def _get_ten_god(self, day_master: str, target: str) -> str:
        """일간 기준으로 대상의 십성 판단"""
        day_element = self.ELEMENT_MAP[day_master]
        target_element = self.ELEMENT_MAP[target]

        if day_element == target_element:
            # 같은 오행: 비견 또는 겁재
            yin_yang = "same" if self._is_same_yin_yang(day_master, target) else "diff"
        else:
            # 다른 오행: 관계에 따라 판단
            yin_yang = "same" if self._is_same_yin_yang(day_master, target) else "diff"

        key = (day_element, target_element, yin_yang)
        return self.TEN_GODS_MAP.get(key, "비견")  # 기본값

    def _calculate_ten_gods(
        self,
        day_master: str,
        year_pillar: SajuPillar,
        month_pillar: SajuPillar,
        day_pillar: SajuPillar,
        hour_pillar: SajuPillar
    ) -> TenGods:
        """십성 분포 계산"""
        ten_gods_count = {
            "비견": 0, "겁재": 0, "식신": 0, "상관": 0, "편재": 0,
            "정재": 0, "편관": 0, "정관": 0, "편인": 0, "정인": 0
        }

        # 각 기둥의 천간과 지지를 검사
        pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]

        for pillar in pillars:
            # 천간 십성
            if pillar.heavenly_stem != day_master:  # 일간은 제외
                ten_god = self._get_ten_god(day_master, pillar.heavenly_stem)
                ten_gods_count[ten_god] += 1

            # 지지 십성 (지지의 장간을 천간으로 환산)
            # 간단히 지지도 오행으로 판단
            ten_god = self._get_ten_god(day_master, pillar.earthly_branch)
            ten_gods_count[ten_god] += 1

        return TenGods(**ten_gods_count)

    def _calculate_five_elements(
        self,
        year_pillar: SajuPillar,
        month_pillar: SajuPillar,
        day_pillar: SajuPillar,
        hour_pillar: SajuPillar
    ) -> FiveElements:
        """오행 분포 계산"""
        elements_count = {"wood": 0, "fire": 0, "earth": 0, "metal": 0, "water": 0}
        element_to_key = {"목": "wood", "화": "fire", "토": "earth", "금": "metal", "수": "water"}

        pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]

        for pillar in pillars:
            # 천간
            stem_element = self.ELEMENT_MAP[pillar.heavenly_stem]
            elements_count[element_to_key[stem_element]] += 1

            # 지지
            branch_element = self.ELEMENT_MAP[pillar.earthly_branch]
            elements_count[element_to_key[branch_element]] += 1

        return FiveElements(**elements_count)

    def _calculate_daeun(
        self, birth_info: BirthInfo, year_pillar: SajuPillar, month_pillar: SajuPillar
    ) -> List[DaeunPeriod]:
        """
        대운 계산
        남자 양년생/여자 음년생: 순행
        남자 음년생/여자 양년생: 역행
        """
        daeun_list = []

        # 년간의 음양 판단
        year_stem_index = self.HEAVENLY_STEMS.index(year_pillar.heavenly_stem)
        is_yang_year = (year_stem_index % 2) == 0

        # 대운 방향 결정
        is_male = birth_info.gender == "male" if birth_info.gender else True
        is_forward = (is_male and is_yang_year) or (not is_male and not is_yang_year)

        # 월주 천간/지지 인덱스
        month_stem_index = self.HEAVENLY_STEMS.index(month_pillar.heavenly_stem)
        month_branch_index = self.EARTHLY_BRANCHES.index(month_pillar.earthly_branch)

        # 대운은 보통 10년 단위
        # 기준 나이는 간단히 10세부터 시작 (실제로는 절기 기준 계산)
        start_age = 10

        for i in range(8):  # 80년간의 대운 (8개)
            if is_forward:
                stem_idx = (month_stem_index + i + 1) % 10
                branch_idx = (month_branch_index + i + 1) % 12
            else:
                stem_idx = (month_stem_index - i - 1) % 10
                branch_idx = (month_branch_index - i - 1) % 12

            daeun_list.append(DaeunPeriod(
                start_age=start_age + (i * 10),
                end_age=start_age + ((i + 1) * 10) - 1,
                heavenly_stem=self.HEAVENLY_STEMS[stem_idx],
                earthly_branch=self.EARTHLY_BRANCHES[branch_idx]
            ))

        return daeun_list

    def _calculate_saeun(
        self, birth_info: BirthInfo, start_year: int, end_year: int
    ) -> List[SaeunYear]:
        """
        세운(歲運) 계산
        지정된 년도 범위의 세운을 계산

        Args:
            birth_info: 생년월일시 정보
            start_year: 시작 년도
            end_year: 종료 년도

        Returns:
            세운 목록
        """
        saeun_list = []

        for year in range(start_year, end_year + 1):
            # 해당 년도의 년주 계산
            year_pillar = self._calculate_year_pillar(year, 2, 4)  # 입춘 기준

            # 해당 년도의 나이 계산 (만 나이)
            age = year - birth_info.year

            saeun_list.append(SaeunYear(
                year=year,
                year_pillar=year_pillar,
                age=age
            ))

        return saeun_list

    def _calculate_lunar_date(self, year: int, month: int, day: int) -> Dict:
        """양력을 음력으로 변환"""
        try:
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(year, month, day)
            lunar_date = calendar.LunarIsoFormat()

            return {
                "year": calendar.lunarYear,
                "month": calendar.lunarMonth,
                "day": calendar.lunarDay,
                "is_leap_month": calendar.isLeapMonth,
                "iso_format": lunar_date
            }
        except Exception as e:
            return {
                "error": f"음력 변환 실패: {str(e)}"
            }

    def _calculate_twelve_spirits(
        self,
        day_master: str,
        year_pillar: SajuPillar,
        month_pillar: SajuPillar,
        day_pillar: SajuPillar,
        hour_pillar: SajuPillar
    ) -> Dict[str, Dict]:
        """
        십이운성 계산 (각 기둥별)

        Args:
            day_master: 일간
            year_pillar: 년주
            month_pillar: 월주
            day_pillar: 일주
            hour_pillar: 시주

        Returns:
            각 기둥별 십이운성 정보
        """
        result = {}

        # 년지의 십이운성
        year_spirit = get_twelve_spirit(day_master, year_pillar.earthly_branch)
        if year_spirit:
            result["년지"] = year_spirit

        # 월지의 십이운성
        month_spirit = get_twelve_spirit(day_master, month_pillar.earthly_branch)
        if month_spirit:
            result["월지"] = month_spirit

        # 일지의 십이운성
        day_spirit = get_twelve_spirit(day_master, day_pillar.earthly_branch)
        if day_spirit:
            result["일지"] = day_spirit

        # 시지의 십이운성
        hour_spirit = get_twelve_spirit(day_master, hour_pillar.earthly_branch)
        if hour_spirit:
            result["시지"] = hour_spirit

        return result
