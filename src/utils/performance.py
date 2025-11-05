"""
성능 최적화 유틸리티

계산 병렬화, 캐싱, 프로파일링
"""

import asyncio
import time
import functools
from typing import Callable, Any, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import hashlib
import json


# 전역 Thread Pool (재사용)
_thread_pool = ThreadPoolExecutor(max_workers=4)


def async_timer(func):
    """비동기 함수 실행 시간 측정 데코레이터"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"⏱ {func.__name__}: {elapsed:.3f}초")
        return result
    return wrapper


def sync_timer(func):
    """동기 함수 실행 시간 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"⏱ {func.__name__}: {elapsed:.3f}초")
        return result
    return wrapper


def memoize(func):
    """함수 결과 메모이제이션 데코레이터"""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 캐시 키 생성
        key_data = (args, tuple(sorted(kwargs.items())))
        key = hashlib.md5(str(key_data).encode()).hexdigest()

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrapper


async def run_parallel_async(tasks: List[Callable]) -> List[Any]:
    """
    비동기 함수들을 병렬로 실행

    Args:
        tasks: 비동기 함수 리스트 (이미 호출된 코루틴)

    Returns:
        결과 리스트
    """
    return await asyncio.gather(*tasks, return_exceptions=False)


async def run_parallel_sync(funcs: List[Tuple[Callable, tuple, dict]]) -> List[Any]:
    """
    동기 함수들을 Thread Pool에서 병렬로 실행

    Args:
        funcs: (함수, args, kwargs) 튜플 리스트

    Returns:
        결과 리스트
    """
    loop = asyncio.get_event_loop()
    tasks = []

    for func, args, kwargs in funcs:
        task = loop.run_in_executor(_thread_pool, func, *args, **kwargs)
        tasks.append(task)

    return await asyncio.gather(*tasks, return_exceptions=False)


def batch_process(items: List[Any], func: Callable, batch_size: int = 10) -> List[Any]:
    """
    아이템들을 배치로 나눠서 처리

    Args:
        items: 처리할 아이템 리스트
        func: 각 아이템에 적용할 함수
        batch_size: 배치 크기

    Returns:
        처리된 결과 리스트
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [func(item) for item in batch]
        results.extend(batch_results)
    return results


class PerformanceMonitor:
    """성능 모니터링 클래스"""

    def __init__(self):
        self.timings = {}
        self.call_counts = {}

    def record(self, name: str, elapsed: float):
        """실행 시간 기록"""
        if name not in self.timings:
            self.timings[name] = []
            self.call_counts[name] = 0

        self.timings[name].append(elapsed)
        self.call_counts[name] += 1

    def get_stats(self, name: str) -> dict:
        """통계 조회"""
        if name not in self.timings:
            return None

        times = self.timings[name]
        return {
            "count": self.call_counts[name],
            "total": sum(times),
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }

    def print_report(self):
        """성능 리포트 출력"""
        print("\n" + "="*60)
        print("성능 모니터링 리포트")
        print("="*60)

        for name in sorted(self.timings.keys()):
            stats = self.get_stats(name)
            print(f"\n{name}:")
            print(f"  호출 횟수: {stats['count']}")
            print(f"  총 시간: {stats['total']:.3f}초")
            print(f"  평균 시간: {stats['average']:.3f}초")
            print(f"  최소 시간: {stats['min']:.3f}초")
            print(f"  최대 시간: {stats['max']:.3f}초")

        print("="*60 + "\n")


# 전역 성능 모니터
performance_monitor = PerformanceMonitor()


def profile(name: Optional[str] = None):
    """프로파일링 데코레이터"""
    def decorator(func):
        profile_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            performance_monitor.record(profile_name, elapsed)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            performance_monitor.record(profile_name, elapsed)
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class LRUCache:
    """간단한 LRU 캐시 구현"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key in self.cache:
            # 접근 순서 업데이트
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """캐시에 값 저장"""
        if key in self.cache:
            # 이미 있으면 순서만 업데이트
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # 가득 차면 가장 오래된 것 제거
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = value
        self.access_order.append(key)

    def clear(self):
        """캐시 초기화"""
        self.cache.clear()
        self.access_order.clear()

    def size(self) -> int:
        """현재 캐시 크기"""
        return len(self.cache)


# 전역 LRU 캐시 인스턴스
lru_cache = LRUCache(max_size=1000)
