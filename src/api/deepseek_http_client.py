from __future__ import annotations

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger("deepseek.http")


class APIConfig:
    """Configuration for DeepSeek API access."""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        max_retries: int = 3,
        timeout: int = 30,
        cache_enabled: bool = True,
        cache_dir: str | Path = "data/cache/api",
        mock_mode: bool = False,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(cache_dir)
        self.mock_mode = mock_mode or not api_key
        if not api_key and not mock_mode:
            logger.warning("未配置API Key，自动启用Mock模式")
            self.mock_mode = True


class ResponseCache:
    """Simple cache for API responses."""

    def __init__(self, cache_dir: Path, default_ttl: int = 3600) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, prompt: str, params: Dict[str, Any]) -> str:
        content = json.dumps(
            {"prompt": prompt, "params": params}, sort_keys=True, ensure_ascii=False
        )
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[Any]:
        key = self._generate_key(prompt, params)
        error_file = self.cache_dir / f"{key}.error"
        if error_file.exists():
            try:
                error_file.unlink()
            except OSError as exc:
                logger.warning("删除错误标记失败: %s", exc)
            return None
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if datetime.now() < entry["expires_at"]:
                logger.debug("缓存命中（内存）: %s", key[:8])
                return entry["data"]
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with cache_file.open("r", encoding="utf-8") as fh:
                    entry = json.load(fh)
                expires_at = datetime.fromisoformat(entry["expires_at"])
                if datetime.now() < expires_at:
                    self.memory_cache[key] = {
                        "data": entry["data"],
                        "expires_at": expires_at,
                    }
                    logger.debug("缓存命中（文件）: %s", key[:8])
                    return entry["data"]
                cache_file.unlink()
            except Exception as exc:
                logger.error("读取缓存失败: %s", exc)
        return None

    def set(
        self, prompt: str, params: Dict[str, Any], data: Any, ttl: Optional[int] = None
    ) -> None:
        key = self._generate_key(prompt, params)
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        self.memory_cache[key] = {"data": data, "expires_at": expires_at}
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with cache_file.open("w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "data": data,
                        "expires_at": expires_at.isoformat(),
                        "prompt_hash": key,
                        "created_at": datetime.now().isoformat(),
                    },
                    fh,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as exc:
            logger.error("保存缓存失败: %s", exc)
            error_file = self.cache_dir / f"{key}.error"
            try:
                error_file.write_text(str(exc), encoding="utf-8")
            except Exception as write_exc:
                logger.error("创建错误标记失败: %s", write_exc)


class DeepSeekHTTPClient:
    """Low-level HTTP client for DeepSeek API."""

    def __init__(
        self, config: APIConfig, http_client: httpx.AsyncClient | None = None
    ) -> None:
        self.config = config
        self.client = http_client or httpx.AsyncClient(timeout=config.timeout)
        self.cache = (
            ResponseCache(self.config.cache_dir) if self.config.cache_enabled else None
        )
        self._mock_responses = self._init_mock_responses()

    async def __aenter__(self) -> "DeepSeekHTTPClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("request %s", endpoint)
        if self.config.mock_mode:
            await asyncio.sleep(0.1)
            result = self._generate_mock_response(endpoint, data)
            logger.info("response %s mock", endpoint)
            return result
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }
        try:
            json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
            response = await self.client.post(
                f"{self.config.base_url}/{endpoint}",
                headers=headers,
                content=json_data,
            )
            response.raise_for_status()
            if not response.content or not response.text.strip():
                logger.error("空响应: %s", endpoint)
                raise ValueError(f"Empty response from {endpoint}")
            try:
                res_data = response.json()
                logger.info("response %s %s", endpoint, response.status_code)
                return res_data
            except json.JSONDecodeError as exc:
                logger.error("非JSON响应: %s", response.text)
                raise ValueError(
                    f"Invalid JSON response from {endpoint}: {response.text[:100]}"
                ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP错误 %s: %s", exc.response.status_code, exc.response.text)
            if exc.response.status_code == 429:
                await asyncio.sleep(5)
            raise
        except Exception as exc:
            logger.error("请求失败: %s", exc)
            raise

    def _generate_mock_response(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        mock_payload = {
            "dialogue": [
                {
                    "speaker": "张三",
                    "text": "这是一个测试对话。",
                    "emotion": "neutral",
                }
            ],
            "actions": [
                {
                    "npc": "张三",
                    "action": "wait",
                    "target": None,
                    "reason": "mock",
                    "priority": 1,
                }
            ],
            "turn_summary": "测试回合",
            "atmosphere": "calm",
        }
        content = json.dumps(mock_payload, ensure_ascii=False)
        return {
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 100},
        }

    def _init_mock_responses(self) -> Dict[str, List[str]]:
        return {
            "narration": [
                "夜幕降临，废弃的建筑物里弥漫着腐朽的气息。墙壁上的影子仿佛有了生命，在昏暗的灯光下扭曲蠕动。每一声细微的响动都让人心跳加速，仿佛有什么不可名状的存在正在暗中窥视。空气变得粘稠而压抑，让人喘不过气来。",
                "走廊尽头传来若有若无的哭泣声，像是来自另一个世界的召唤。地板吱呀作响，每一步都像是踩在命运的琴弦上。镜子里映出的不再是熟悉的面孔，而是扭曲的、陌生的存在。恐惧如潮水般涌来，吞噬着每个人的理智。",
                "时钟的指针在夜停止了转动，时间仿佛凝固在这一刻。房间的温度骤然下降，呼出的气息化作白雾。墙上的血迹开始蠕动，组成了诡异的文字。这不是幻觉，这是真实存在的噩梦。",
            ]
        }

    async def close(self) -> None:
        await self.client.aclose()
