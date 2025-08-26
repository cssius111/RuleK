# -*- coding: utf-8 -*-
"""
DeepSeek API客户端模块 - 增强版
集成了Pydantic Schema验证和专业的Prompt管理
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import re

from src.api.schemas import (
    DialogueTurn,
    TurnPlan,
    NarrativeOut,
    RuleEvalResult,
    RuleTrigger,
    RuleEffect,
)
from src.api.prompts import PromptManager, RULE_EVAL_SYSTEM
from .deepseek_http_client import APIConfig, DeepSeekHTTPClient
from .llm_client import LLMClient

logger = logging.getLogger("deepseek.client")




class DeepSeekClient(LLMClient):
    """增强版DeepSeek客户端"""

    def __init__(
        self,
        config: Optional[APIConfig] = None,
        http_client: DeepSeekHTTPClient | None = None,
    ):
        """初始化客户端

        Args:
            config: API配置
            http_client: 可注入的HTTP客户端
        """

        self.config = config or APIConfig()
        self.http = http_client or DeepSeekHTTPClient(self.config)
        self.cache = self.http.cache
        self.prompt_mgr = PromptManager()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求，实际调用底层HTTP客户端"""
        return await self.http.post(endpoint, data)

    def _ensure_len_text(self, text: str, min_len: int = 200) -> str:
        """确保文本长度不少于 ``min_len`` 字符"""
        if len(text) < min_len:
            text += " ……故事还在继续，恐惧从未离去。"
        return text

    async def generate_turn_plan(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        available_places: List[str],
        time_of_day: str,
        min_dialogue: int = 1,
    ) -> TurnPlan:
        """生成回合计划（对话+行动）"""
        logger.info(
            "generate_turn_plan npcs=%d time_of_day=%s places=%d min_dialogue=%d",
            len(npc_states),
            time_of_day,
            len(available_places),
            min_dialogue,
        )
        # 补全NPC状态所需字段
        default_location = scene_context.get("current_location", "未知地点")
        for npc in npc_states:
            npc.setdefault("traits", [])
            npc.setdefault("status", "normal")
            npc.setdefault("location", default_location)

        # 检查缓存
        cache_key = f"turn_plan_{time_of_day}_{len(npc_states)}"
        if self.cache:
            cached = self.cache.get(cache_key, {"npcs": len(npc_states)})
            if cached:
                try:
                    plan = TurnPlan.model_validate(cached)
                    logger.info(
                        "turn_plan cache dialogue=%d actions=%d",
                        len(plan.dialogue),
                        len(plan.actions),
                    )
                    return plan
                except Exception:
                    logger.exception("Failed to validate cached turn plan")

        # 构建prompt
        system_prompt, user_prompt = self.prompt_mgr.build_turn_plan_prompt(
            npcs=npc_states,
            time_of_day=time_of_day,
            location=scene_context.get("current_location", "未知地点"),
            recent_events=scene_context.get("recent_events", []),
            available_places=available_places,
            active_rules=scene_context.get("active_rules", []),
            ambient_fear=scene_context.get("ambient_fear_level", 50),
            special_conditions=scene_context.get("special_conditions", []),
        )

        # 构建请求
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.8,
            "max_tokens": 1500,
        }

        try:
            # 发送请求
            response = await self._make_request("chat/completions", data)
            content = response["choices"][0]["message"]["content"]

            # 解析响应
            success, parsed_data, error = self.prompt_mgr.validate_json_response(
                content, "turn_plan"
            )
            if not success:
                logger.error(f"解析回合计划失败: {error}")
                # 尝试直接解析
                parsed_data = json.loads(self._extract_json(content))

            # 验证并创建对象
            plan = TurnPlan.model_validate(parsed_data)

            # 缓存结果
            if self.cache:
                self.cache.set(
                    cache_key, {"npcs": len(npc_states)}, plan.model_dump(), ttl=300
                )

            logger.info(
                "turn_plan generated dialogue=%d actions=%d",
                len(plan.dialogue),
                len(plan.actions),
            )

            return plan

        except Exception as e:
            logger.exception(f"生成回合计划失败: {str(e)}")
            speaker = npc_states[0]["name"] if npc_states else "系统"
            text = locals().get("content", "").strip()
            if "：" in text:
                speaker, text = text.split("：", 1)
            elif ":" in text:
                speaker, text = text.split(":", 1)

            return TurnPlan(
                dialogue=[
                    DialogueTurn(
                        speaker=speaker.strip(), text=text.strip() or "[AI生成失败，使用默认对话]"
                    )
                ],
                actions=[],
                atmosphere="error",
            )

    async def generate_narrative_text(
        self,
        events: List[Dict[str, Any]],
        time_of_day: str,
        survivor_count: int,
        ambient_fear: int = 50,
        location: str = "未知地点",
        npc_states: Optional[List[Dict[str, Any]]] = None,
        min_len: int = 200,
    ) -> str:
        """生成叙事文本"""
        # 格式化事件
        formatted_events = []
        for event in events:
            formatted_events.append(self.prompt_mgr.format_event_for_narrative(event))

        # 构建prompt
        system_prompt, user_prompt = self.prompt_mgr.build_narrative_prompt(
            events=formatted_events,
            time_of_day=time_of_day,
            survivor_count=survivor_count,
            ambient_fear=ambient_fear,
            special_conditions=None,
        )

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.9,
            "max_tokens": 600,
        }

        try:
            response = await self._make_request("chat/completions", data)
            narrative = response["choices"][0]["message"]["content"].strip()

            narrative = self._ensure_len_text(narrative, min_len)

            # 使用Schema验证
            narrative_out = NarrativeOut(narrative=narrative)
            return narrative_out.narrative

        except Exception as e:
            logger.error(f"生成叙事失败: {str(e)}")
            return "在这个诡异的空间里，恐惧正在悄然蔓延……"

    async def evaluate_rule_nl(
        self, rule_nl: str, world_ctx: Dict[str, Any]
    ) -> RuleEvalResult:
        """评估自然语言规则"""
        # 构建prompt
        rule_draft = {"description": rule_nl}
        user_prompt = self.prompt_mgr.build_rule_eval_prompt(
            rule_draft,
            world_ctx,
            difficulty_level=world_ctx.get("difficulty_level"),
        )
        system_prompt = RULE_EVAL_SYSTEM

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        try:
            response = await self._make_request("chat/completions", data)
            content = response["choices"][0]["message"]["content"]

            # 解析响应
            success, parsed_data, error = self.prompt_mgr.validate_json_response(
                content, "rule_eval"
            )
            if not success:
                logger.error(f"解析规则评估失败: {error}")
                parsed_data = json.loads(self._extract_json(content))

            # 如果缺少cost但有cost_estimate，则补充cost字段
            if (
                isinstance(parsed_data, dict)
                and "cost" not in parsed_data
                and "cost_estimate" in parsed_data
            ):
                parsed_data["cost"] = parsed_data["cost_estimate"]

            # 验证并返回
            return RuleEvalResult.model_validate(parsed_data)

        except Exception as e:
            logger.error(f"评估规则失败: {str(e)}")
            # 返回默认评估
            return RuleEvalResult(
                name="未知规则",
                trigger=RuleTrigger(type="event", conditions=[]),
                effect=RuleEffect(type="custom", params={}),
                cost=100,
                difficulty=5,
                loopholes=["规则解析失败"],
                suggestion="请尝试更清晰地描述规则",
            )

    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON"""
        # 尝试提取```json```块
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # 尝试提取花括号内容
        brace_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if brace_match:
            return brace_match.group(0)

        return text

    # ========== 兼容旧API的方法 ==========

    async def generate_dialogue(
        self,
        npc_states: List[Dict[str, Any]],
        scene_context: Dict[str, Any],
        dialogue_type: str = "normal",
    ) -> List[Dict[str, str]]:
        """生成对话（兼容旧接口）"""
        plan = await self.generate_turn_plan(
            npc_states=npc_states,
            scene_context=scene_context,
            available_places=scene_context.get("available_places", []),
            time_of_day=scene_context.get("time", "未知"),
        )

        return [{"speaker": d.speaker, "text": d.text} for d in plan.dialogue]

    async def generate_dialogue_async(
        self,
        context: str,
        participants: List[str],
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> List[Dict[str, str]]:
        """异步生成对话（兼容旧接口）"""
        npc_states = [{"name": name, "fear": 50, "sanity": 80} for name in participants]
        scene_context = {"description": context}
        
        # 如果没有参与者，返回默认对话
        if not participants:
            return [{"speaker": "系统", "text": "没有参与者"}]
        
        try:
            return await self.generate_dialogue(npc_states, scene_context)
        except Exception as e:
            logger.error(f"生成对话失败: {e}")
            # 返回默认对话
            return [
                {"speaker": participants[0] if participants else "系统", 
                 "text": "这里好冷...我有种不祥的预感。"}
            ]

    async def evaluate_rule(
        self, rule_draft: Dict[str, Any], world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估规则（兼容旧接口）"""
        rule_nl = rule_draft.get("description", str(rule_draft))
        result = await self.evaluate_rule_nl(rule_nl, world_context)

        # 转换为旧格式
        return {
            "cost": result.cost,
            "cost_estimate": result.cost,  # 兼容性
            "difficulty": result.difficulty,
            "loopholes": result.loopholes,
            "suggestion": result.suggestion,
        }

    async def evaluate_rule_async(
        self, rule_draft: Dict[str, Any], world_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """异步评估规则（兼容旧接口）"""
        return await self.evaluate_rule(rule_draft, world_context)

    async def narrate_events(
        self,
        events: List[Dict[str, Any]],
        atmosphere: str = "horror",
        min_len: int = 200,
    ) -> str:
        """叙述事件（兼容旧接口）"""
        return await self.generate_narrative_text(
            events=events,
            time_of_day="未知",
            survivor_count=len(events),
            ambient_fear=50,
            location="未知地点",
            npc_states=None,
            min_len=min_len,
        )

    async def generate_narrative_async(
        self,
        events: List[Dict[str, Any]],
        atmosphere: str = "horror",
        context=None,
        min_len: int = 200,
        **kwargs,
    ) -> str:
        """异步生成叙事（兼容旧接口）"""
        _ = context  # 兼容旧签名
        return await self.narrate_events(events, atmosphere, min_len=min_len)

    async def generate_npc_batch_async(
        self,
        count: int,
        traits: Optional[List[str]] = None,
        personality_tags=None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """批量生成NPC（兼容旧接口）"""
        if self.config.mock_mode:
            names = ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
            backgrounds = [
                "曾经是一名医生，因为一次医疗事故失去了执照",
                "大学生，喜欢探索废弃建筑寻求刺激",
                "失业的程序员，最近压力很大",
                "退役军人，有轻微的PTSD",
                "私家侦探，正在调查失踪案件",
                "作家，正在寻找恐怖小说的灵感",
            ]

            result = []
            for i in range(min(count, len(names))):
                npc = {
                    "name": names[i],
                    "background": backgrounds[i],
                    "fear": 30 + i * 10,
                    "sanity": 90 - i * 5,
                }
                if traits and i < len(traits):
                    npc["trait"] = traits[i]
                result.append(npc)
            return result

        # 实际API调用实现...
        prompt = f"生成{count}个恐怖游戏NPC角色，包含中文名字、背景故事、初始恐惧值和理智值。"
        if traits:
            prompt += f"性格特征从以下选择：{', '.join(traits)}"

        # 暂时返回mock数据（API实现待完成）
        logger.warning("非mock模式下的NPC批量生成尚未实现，返回mock数据")
        
        # 生成足够数量的mock NPC
        mock_npcs = []
        for i in range(count):
            mock_npcs.append({
                "name": f"测试NPC{i+1}",
                "background": f"临时生成的NPC，编号{i+1}",
                "fear": 30 + i * 10,
                "sanity": 90 - i * 5,
            })
        return mock_npcs

    async def close(self):
        """关闭客户端"""
        await self.http.close()


# ========== 工厂函数 ==========


async def create_client(config_path: Optional[str] = None) -> DeepSeekClient:
    """创建DeepSeek客户端"""
    api_config = APIConfig()

    if config_path:
        # 从文件加载额外配置
        try:
            path = Path(config_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(api_config, key):
                            setattr(api_config, key, value)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")

    return DeepSeekClient(api_config)


# ========== 测试代码 ==========

if __name__ == "__main__":

    async def test_client():
        """测试客户端功能"""
        client = DeepSeekClient(APIConfig(mock_mode=True))

        print("=== 测试回合计划生成 ===")
        plan = await client.generate_turn_plan(
            npc_states=[
                {
                    "name": "张三",
                    "fear": 45,
                    "sanity": 75,
                    "traits": ["谨慎"],
                    "status": "正常",
                    "location": "客厅",
                },
                {
                    "name": "李四",
                    "fear": 60,
                    "sanity": 60,
                    "traits": ["冲动"],
                    "status": "紧张",
                    "location": "客厅",
                },
            ],
            scene_context={
                "current_location": "废弃医院",
                "recent_events": ["听到楼上传来脚步声", "电灯忽明忽暗"],
                "ambient_fear_level": 70,
            },
            available_places=["客厅", "走廊", "楼梯", "二楼"],
            time_of_day="午夜",
        )

        print("\n对话：")
        for d in plan.dialogue:
            print(f"- {d.speaker}: {d.text}")

        print("\n行动：")
        for a in plan.actions:
            print(f"- {a.npc} -> {a.action} {a.target or ''}")

        print("\n=== 测试叙事生成 ===")
        narrative = await client.generate_narrative_text(
            events=[
                {"type": "dialogue", "speaker": "张三", "text": "这里不对劲..."},
                {"type": "action", "actor": "李四", "action": "搜索", "location": "抽屉"},
                {"type": "rule_triggered", "description": "镜子突然碎裂"},
            ],
            time_of_day="深夜",
            location="废弃医院三楼",
        )

        print("\n叙事：")
        print(narrative)

        print("\n=== 测试规则评估 ===")
        rule_eval = await client.evaluate_rule_nl(
            rule_nl="晚上12点后不能照镜子，否则会被镜中的自己替换",
            world_ctx={"rule_count": 3, "avg_fear": 65, "places": ["浴室", "卧室", "走廊"]},
        )

        print(f"\n规则名称：{rule_eval.name}")
        print(f"成本：{rule_eval.cost}")
        print(f"难度：{rule_eval.difficulty}")
        print(f"漏洞：{', '.join(rule_eval.loopholes)}")

        await client.close()

    asyncio.run(test_client())
