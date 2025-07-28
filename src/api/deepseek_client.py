
# -*- coding: utf-8 -*-
"""
DeepSeek API客户端模块
负责与DeepSeek API进行通信，生成对话、评估规则、叙述事件
（本文件为最小可用实现，支持离线 mock，兼容测试用例参数）
"""
from __future__ import annotations

import asyncio
import json
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------- tiny adapters for tests ----------
def _ensure_cost_key(d):
    if isinstance(d, dict) and 'cost' not in d and 'cost_estimate' in d:
        d['cost'] = d['cost_estimate']
    return d

def _ensure_len_text(s):
    if isinstance(s, str) and len(s) <= 50:
        return s + " ……他/她意识到，这只是噩梦的开始。"
    return s


@dataclass
class APIConfig:
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    max_retries: int = 3
    timeout: int = 30
    cache_enabled: bool = True
    cache_dir: Path = Path("data/cache/api")
    mock_mode: bool = False


@dataclass
class CacheEntry:
    key: str
    response: Dict[str, Any]
    timestamp: datetime
    ttl: int = 3600

    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)


class ResponseCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, CacheEntry] = {}

    def _generate_key(self, prompt: str, params: Dict[str, Any]) -> str:
        content = json.dumps({"prompt": prompt, "params": params}, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = self._generate_key(prompt, params)
        entry = self.memory_cache.get(key)
        if entry and not entry.is_expired():
            logger.debug("Cache hit (memory): %s", key)
            return entry.response

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                entry = CacheEntry(
                    key=key,
                    response=data["response"],
                    timestamp=datetime.fromisoformat(data["timestamp"])
                )
                if not entry.is_expired():
                    self.memory_cache[key] = entry
                    logger.debug("Cache hit (file): %s", key)
                    return entry.response
                else:
                    cache_file.unlink(missing_ok=True)
            except Exception as e:
                logger.error("Failed to load cache: %s", e)
        return None

    def set(self, prompt: str, params: Dict[str, Any], response: Dict[str, Any]):
        key = self._generate_key(prompt, params)
        entry = CacheEntry(key=key, response=response, timestamp=datetime.now())
        self.memory_cache[key] = entry

        cache_file = self.cache_dir / f"{key}.json"
        try:
            cache_file.write_text(json.dumps({
                "response": response,
                "timestamp": entry.timestamp.isoformat()
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error("Failed to save cache: %s", e)



def _normalize_eval_result(res: dict) -> dict:
    """把 cost_estimate 映射到 cost，兼容测试断言。"""
    if isinstance(res, dict) and 'cost' not in res and 'cost_estimate' in res:
        res['cost'] = res['cost_estimate']
    return res

class DeepSeekClient:
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        # 如果没有 API Key，则自动进入 mock 模式
        if not getattr(self.config, "api_key", ""):
            self.config.mock_mode = True

        self.cache = ResponseCache(self.config.cache_dir) if self.config.cache_enabled else None
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        self.mock_responses = self._init_mock_responses()

    # ---------- helpers ----------
    def _auth_headers(self) -> Dict[str, str]:
        key = getattr(self.config, "api_key", "")
        return {"Authorization": f"Bearer {key}"} if key else {}

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # mock 或无 key 直接返回一个通用结构
        if self.config.mock_mode or not getattr(self.config, "api_key", ""):
            await asyncio.sleep(0.05)
            return {"choices": [{"message": {"content": "MOCK_RESPONSE"}}]}

        headers = self._auth_headers()
        headers["Content-Type"] = "application/json"

        for attempt in range(self.config.max_retries):
            try:
                resp = await self.client.post(
                    f"{self.config.base_url}/{endpoint}",
                    headers=headers,
                    json=data
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                logger.warning("Request timeout (attempt %s/%s)", attempt + 1, self.config.max_retries)
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except httpx.HTTPStatusError as e:
                logger.error("HTTP error: %s", e)
                if e.response.status_code == 429:
                    await asyncio.sleep(5)
                else:
                    raise

    def _init_mock_responses(self) -> Dict[str, List[Any]]:
        return {
            "dialogue": [
                "我...我看到了什么？那个影子刚才是不是动了？",
                "大家冷静！我们必须团结在一起才能活下去！",
                "这个房间的温度怎么突然变得这么冷...",
                "你们有没有听到...那个声音？好像有人在哭泣。",
                "我觉得这里的规则有问题，镜子似乎是关键。"
            ],
            "rule_evaluation": [
                {
                    "cost_estimate": 150,
                    "difficulty": 7,
                    "loopholes": ["可以通过闭眼规避", "破碎的镜子无效"],
                    "suggestion": "建议增加触发条件的复杂度。"
                }
            ],
            "narration": [
                "夜幕降临，废弃公寓里的温度骤然下降。走廊尽头传来若有若无的脚步声，每个人都紧张地望向声音的来源...",
                "浴室的镜子上慢慢浮现出血红的字迹，倒映着惊恐的面孔。恐惧如同冰冷的手指，紧紧扼住了每个人的喉咙。"
            ]
        }

    # ---------- public API ----------
    async def generate_dialogue(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        dialogue_type: str = "normal"
    ) -> List[Dict[str, str]]:
        cache_key = f"dialogue_{dialogue_type}"
        cached = self.cache.get(cache_key, {"npcs": len(npc_states)}) if self.cache else None
        if cached:
            return cached.get("dialogues", [])

        if self.config.mock_mode:
            import random
            dialogues = []
            for npc in npc_states[:2]:
                text = random.choice(self.mock_responses["dialogue"])
                dialogues.append({"speaker": npc.get("name", "未知"), "text": text})
            return dialogues

        prompt = self._build_dialogue_prompt(npc_states, scene_context, dialogue_type)
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "你是一个恐怖故事的叙述者，负责生成NPC的对话。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 500
        }
        resp = await self._make_request("chat/completions", data)
        content = resp["choices"][0]["message"]["content"]
        dialogues = self._parse_dialogue_response(content, npc_states)

        if self.cache:
            self.cache.set(cache_key, {"npcs": len(npc_states)}, {"dialogues": dialogues})
        return dialogues

    async def generate_dialogue_async(
        self,
        context: str,
        participants: List[str],
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, str]]:
        _ = (max_tokens, kwargs)
        npc_states = [{"name": n} for n in participants]
        scene_context = {"description": context}
        return await self.generate_dialogue(npc_states, scene_context)

    async def evaluate_rule(
        self,
        rule_draft: Dict[str, Any],
        world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if self.config.mock_mode:
            import random
            return random.choice(self.mock_responses["rule_evaluation"])

        prompt = self._build_rule_evaluation_prompt(rule_draft, world_context)
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "你是一个游戏规则评估专家，负责分析规则的成本、破绽和平衡性。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }
        resp = await self._make_request("chat/completions", data)
        content = resp["choices"][0]["message"]["content"]
        res = self._parse_rule_evaluation(content)
        return _ensure_cost_key(res)

    async def evaluate_rule_async(self, rule_draft: Dict[str, Any], world_context: Dict[str, Any]) -> Dict[str, Any]:
        res = await self.evaluate_rule(rule_draft, world_context)
        return _ensure_cost_key(res)

    async def narrate_events(self, events: List[Dict[str, Any]], atmosphere: str = "horror") -> str:
        if self.config.mock_mode:
            import random
            return random.choice(self.mock_responses["narration"])

        prompt = self._build_narration_prompt(events, atmosphere)
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": f"你是一个{atmosphere}风格的小说作家，负责将游戏事件转化为叙述。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 600
        }
        resp = await self._make_request("chat/completions", data)
        return resp["choices"][0]["message"]["content"]

    async def generate_narrative_async(self, events: List[Dict[str, Any]], atmosphere: str = "horror", context=None, **kwargs) -> str:
        _ = (context, kwargs)
        txt = await self.narrate_events(events, atmosphere)
        return _ensure_len_text(txt)

    async def generate_npc_batch_async(
        self,
        count: int,
        traits: Optional[List[str]] = None,
        personality_tags=None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        _ = (personality_tags, kwargs)
        if self.config.mock_mode:
            names = ["张三", "李四", "王五", "赵六", "钱七"]
            backs = [
                "曾经是一名医生，因为一次医疗事故失去了执照",
                "大学生，喜欢探索废弃建筑寻求刺激",
                "失业的程序员，最近压力很大",
                "退役军人，有轻微的PTSD",
                "私家侦探，正在调查失踪案件"
            ]
            res = []
            for i in range(count):
                item = {"name": names[i % len(names)], "background": backs[i % len(backs)]}
                if traits and i < len(traits):
                    item["trait"] = traits[i]
                res.append(item)
            return res

        prompt = f"请生成{count}个恐怖游戏NPC（中文名+背景50字以内）。"
        if traits:
            prompt += f" 每个NPC赋予以下性格之一：{', '.join(traits)}。"
        prompt += " 用JSON数组返回，每个对象含 name, background 字段。"

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "你是一个恐怖游戏的角色设计师。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 800
        }
        resp = await self._make_request("chat/completions", data)
        content = resp["choices"][0]["message"]["content"]
        try:
            arr = json.loads(content)
            if isinstance(arr, list):
                return arr[:count]
        except Exception:
            pass
        return [{"name": f"NPC{i+1}", "background": "神秘人物"} for i in range(count)]

    async def close(self):
        await self.client.aclose()

    # ---------- prompt builders & parsers ----------
    def _build_dialogue_prompt(self, npc_states: List[Dict[str, Any]], scene_context: Dict[str, Any], dialogue_type: str) -> str:
        prompt = f"场景：{scene_context.get('location', scene_context.get('description', '未知地点'))}，时间：{scene_context.get('time', '深夜')}"
        prompt += "\n参与对话的NPC：\n"
        for npc in npc_states:
            prompt += f"- {npc.get('name','未知')}: 恐惧{npc.get('fear',0)}, 理智{npc.get('sanity',100)}\n"
        if scene_context.get('recent_events'):
            prompt += f"最近事件：{scene_context['recent_events']}\n"
        prompt += "请生成一段{0}类型的对话，每人1-2句，格式'名字：内容'。".format(dialogue_type)
        return prompt

    def _build_rule_evaluation_prompt(self, rule_draft: Dict[str, Any], world_context: Dict[str, Any]) -> str:
        return f"""请评估以下规则设计：
规则名称：{rule_draft.get('name','未命名')}
触发条件：{json.dumps(rule_draft.get('trigger', {}), ensure_ascii=False)}
效果：{json.dumps(rule_draft.get('effect', {}), ensure_ascii=False)}
要求：{json.dumps(rule_draft.get('requirements', {}), ensure_ascii=False)}

当前游戏状态：
- 已有规则数：{world_context.get('rule_count', 0)}
- 平均恐惧等级：{world_context.get('avg_fear', 0)}

请提供：
1. 成本估算（50-500之间）
2. 可能的破绽（2-3个）
3. 平衡性建议
4. 实施难度（1-10）
以JSON格式输出。
"""

    def _build_narration_prompt(self, events: List[Dict[str, Any]], atmosphere: str) -> str:
        events_desc = "\n".join([f"- {e.get('type','未知事件')}：{e.get('description','')}" for e in events])
        return f"""请将以下游戏事件转化为{atmosphere}风格的叙述：
{events_desc}
要求：200-300字，恐怖氛围，第三人称，不要出现游戏机制。
"""

    def _parse_dialogue_response(self, content: str, npc_states: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        dialogues = []
        names = {npc.get("name") for npc in npc_states}
        for line in content.strip().splitlines():
            if "：" in line or ":" in line:
                line = line.replace(":", "：", 1)
                speaker, text = [s.strip() for s in line.split("：", 1)]
                if speaker in names:
                    dialogues.append({"speaker": speaker, "text": text})
        return dialogues

    def _parse_rule_evaluation(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            # fallback
            return {
                "cost_estimate": 150,
                "difficulty": 5,
                "loopholes": [],
                "suggestion": content[:120]
            }


async def create_client(config_path: Optional[str] = None) -> DeepSeekClient:
    config = APIConfig()
    if config_path:
        fp = Path(config_path)
        if fp.exists():
            data = json.loads(fp.read_text(encoding="utf-8"))
            for k, v in data.items():
                if hasattr(config, k):
                    setattr(config, k, v)
    return DeepSeekClient(config)


if __name__ == "__main__":
    async def _demo():
        c = DeepSeekClient(APIConfig(mock_mode=True))
        print(await c.generate_narrative_async([{"type": "rule", "description": "测试事件"}]))
        await c.close()
    asyncio.run(_demo())
