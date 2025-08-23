"""测试DeepSeekClient注入HTTP客户端"""
import json
from pathlib import Path

import httpx
import pytest

from src.api.deepseek_client import APIConfig, DeepSeekClient


@pytest.mark.asyncio
async def test_http_client_injection():
    """使用MockTransport注入HTTP客户端并记录请求"""
    records: list[dict[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        records.append({
            "method": request.method,
            "url": str(request.url),
            "body": request.content.decode()
        })
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    config = APIConfig(api_key="test", base_url="https://mock.api", mock_mode=False)
    client = DeepSeekClient(config, http_client=http_client)

    await client._make_request("test", {"foo": "bar"})
    await client.close()

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    trace_file = artifacts_dir / "deepseek_http_trace.jsonl"
    with trace_file.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    assert trace_file.exists()
    assert records and records[0]["url"].endswith("/test")
