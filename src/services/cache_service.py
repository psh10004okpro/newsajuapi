"""
캐싱 서비스
Redis 또는 메모리 캐싱을 통해 중복 계산/해석 방지
"""

import os
import json
import hashlib
from typing import Optional, Any
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class CacheService:
    """캐싱 서비스"""

    def __init__(self):
        """초기화"""
        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24시간

        # Redis 연결 시도
        try:
            import redis
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))

            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # 연결 테스트
            self.redis_client.ping()
            self.cache_backend = "redis"
            print("✓ Redis 캐시 연결 성공")
        except Exception as e:
            # Redis 연결 실패시 메모리 캐시 사용
            self.redis_client = None
            self.cache_backend = "memory"
            self.memory_cache = {}
            print(f"⚠ Redis 연결 실패, 메모리 캐시 사용: {str(e)}")

    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        캐시 키 생성
        데이터를 해싱하여 고유 키 생성
        """
        # 데이터를 JSON 문자열로 변환
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        # SHA256 해싱
        hash_obj = hashlib.sha256(data_str.encode())
        hash_hex = hash_obj.hexdigest()[:16]  # 앞 16자리만 사용

        return f"{prefix}:{hash_hex}"

    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 값 (없으면 None)
        """
        if not self.enable_cache:
            return None

        try:
            if self.cache_backend == "redis" and self.redis_client:
                value = self.redis_client.get(key)
                return value
            else:
                # 메모리 캐시
                return self.memory_cache.get(key)
        except Exception as e:
            print(f"캐시 조회 실패: {str(e)}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        캐시에 값 저장

        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: TTL (초 단위, None이면 기본값 사용)

        Returns:
            성공 여부
        """
        if not self.enable_cache:
            return False

        if ttl is None:
            ttl = self.ttl_seconds

        try:
            if self.cache_backend == "redis" and self.redis_client:
                self.redis_client.setex(key, ttl, value)
                return True
            else:
                # 메모리 캐시 (TTL 무시)
                self.memory_cache[key] = value
                return True
        except Exception as e:
            print(f"캐시 저장 실패: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        캐시 삭제

        Args:
            key: 캐시 키

        Returns:
            성공 여부
        """
        if not self.enable_cache:
            return False

        try:
            if self.cache_backend == "redis" and self.redis_client:
                self.redis_client.delete(key)
                return True
            else:
                # 메모리 캐시
                if key in self.memory_cache:
                    del self.memory_cache[key]
                return True
        except Exception as e:
            print(f"캐시 삭제 실패: {str(e)}")
            return False

    async def clear_all(self) -> bool:
        """
        모든 캐시 삭제

        Returns:
            성공 여부
        """
        try:
            if self.cache_backend == "redis" and self.redis_client:
                self.redis_client.flushdb()
                return True
            else:
                # 메모리 캐시
                self.memory_cache.clear()
                return True
        except Exception as e:
            print(f"캐시 전체 삭제 실패: {str(e)}")
            return False

    def get_cache_key_for_saju(self, year: int, month: int, day: int, hour: int, minute: int = 0) -> str:
        """사주 계산 결과 캐시 키 생성"""
        return self._generate_key("saju", {
            "year": year, "month": month, "day": day, "hour": hour, "minute": minute
        })

    def get_cache_key_for_interpretation(
        self, saju_key: str, question: Optional[str], detail_level: str, tone: str
    ) -> str:
        """해석 결과 캐시 키 생성"""
        return self._generate_key("interp", {
            "saju": saju_key,
            "question": question or "",
            "detail": detail_level,
            "tone": tone
        })

    def get_cache_key_for_pillar(self, year: int, month: int, day: int) -> str:
        """기둥(년월일주) 캐시 키 생성 - 시주를 제외한 부분 캐싱"""
        return self._generate_key("pillar", {
            "year": year, "month": month, "day": day
        })

    def get_cache_key_for_spirits(self, year_stem: str, month_stem: str,
                                   day_pillar: str, birth_month: int) -> str:
        """신살 캐시 키 생성"""
        return self._generate_key("spirits", {
            "year_stem": year_stem,
            "month_stem": month_stem,
            "day_pillar": day_pillar,
            "birth_month": birth_month
        })

    async def get_stats(self) -> dict:
        """캐시 통계 조회"""
        if self.cache_backend == "redis" and self.redis_client:
            try:
                info = self.redis_client.info("stats")
                return {
                    "backend": "redis",
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "total_keys": self.redis_client.dbsize()
                }
            except:
                return {"backend": "redis", "error": "통계 조회 실패"}
        else:
            return {
                "backend": "memory",
                "total_keys": len(self.memory_cache)
            }

    async def close(self):
        """리소스 정리"""
        if self.redis_client:
            self.redis_client.close()
