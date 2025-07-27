"""
对话系统管理器
管理NPC之间的对话生成、对话轮次和对话历史
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

from src.models.npc import NPC, NPCStatus
from src.api.deepseek_client import DeepSeekClient, APIConfig

logger = logging.getLogger(__name__)


class DialogueType(str, Enum):
    """对话类型枚举"""
    MORNING = "morning"          # 早间对话
    NIGHT = "night"              # 夜间对话
    EMERGENCY = "emergency"      # 紧急对话（如目睹死亡）
    DISCOVERY = "discovery"      # 发现线索对话
    SUSPICION = "suspicion"      # 怀疑对话
    COOPERATION = "cooperation"  # 合作对话
    PANIC = "panic"             # 恐慌对话


@dataclass
class DialogueContext:
    """对话上下文"""
    location: str
    time: str
    participants: List[str]  # NPC IDs
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    mood: str = "tense"  # tense, fearful, suspicious, cooperative
    discovered_clues: List[str] = field(default_factory=list)


@dataclass
class DialogueEntry:
    """对话记录条目"""
    turn: int
    timestamp: datetime
    dialogue_type: DialogueType
    context: DialogueContext
    dialogues: List[Dict[str, str]]  # [{"speaker": "name", "text": "..."}]
    effects: List[Dict[str, Any]] = field(default_factory=list)  # 对话产生的效果
    

class DialogueHistory:
    """对话历史管理"""
    
    def __init__(self, max_entries: int = 50):
        self.entries: List[DialogueEntry] = []
        self.max_entries = max_entries
        
    def add_entry(self, entry: DialogueEntry):
        """添加对话记录"""
        self.entries.append(entry)
        # 保持历史记录在限制内
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_recent_dialogues(self, count: int = 5) -> List[DialogueEntry]:
        """获取最近的对话"""
        return self.entries[-count:] if self.entries else []
    
    def get_dialogues_by_type(self, dialogue_type: DialogueType) -> List[DialogueEntry]:
        """获取特定类型的对话"""
        return [e for e in self.entries if e.dialogue_type == dialogue_type]
    
    def get_npc_dialogues(self, npc_id: str) -> List[Tuple[DialogueEntry, str]]:
        """获取特定NPC参与的对话"""
        result = []
        for entry in self.entries:
            for dialogue in entry.dialogues:
                if dialogue.get("speaker_id") == npc_id:
                    result.append((entry, dialogue["text"]))
        return result


class DialogueSystem:
    """对话系统核心"""
    
    def __init__(self, api_client: Optional[DeepSeekClient] = None):
        self.api_client = api_client or DeepSeekClient(APIConfig(mock_mode=True))
        self.history = DialogueHistory()
        self.dialogue_templates = self._init_dialogue_templates()
        
    def _init_dialogue_templates(self) -> Dict[str, List[str]]:
        """初始化对话模板（用于Mock模式或API失败时的备选）"""
        return {
            DialogueType.MORNING: [
                "早上好...昨晚你睡得怎么样？",
                "我做了个噩梦，梦见...",
                "今天我们必须想办法离开这里。",
                "有人看到{name}了吗？"
            ],
            DialogueType.NIGHT: [
                "天快黑了，大家小心点。",
                "我觉得今晚会发生什么不好的事...",
                "要不我们轮流守夜？",
                "这个时候最危险，都别单独行动。"
            ],
            DialogueType.EMERGENCY: [
                "天啊！{name}他...他死了！",
                "快跑！这里不安全！",
                "到底发生了什么？！",
                "我们必须冷静下来，想想办法！"
            ],
            DialogueType.DISCOVERY: [
                "你们看，我发现了这个...",
                "等等，这个线索说明{clue}",
                "我明白了！原来规则是这样的！",
                "如果我的推理没错的话..."
            ],
            DialogueType.PANIC: [
                "我受不了了！我要出去！",
                "都是你的错！要不是你...",
                "我们都会死在这里的！",
                "不...不要过来！"
            ]
        }
    
    async def generate_dialogue_round(
        self,
        npcs: List[NPC],
        context: DialogueContext,
        dialogue_type: DialogueType,
        current_turn: int
    ) -> DialogueEntry:
        """
        生成一轮对话
        
        Args:
            npcs: 参与对话的NPC列表
            context: 对话上下文
            dialogue_type: 对话类型
            current_turn: 当前回合数
            
        Returns:
            对话记录条目
        """
        # 筛选可以说话的NPC
        speaking_npcs = [
            npc for npc in npcs 
            if npc.status not in [NPCStatus.DEAD, NPCStatus.INSANE] 
            and npc.id in context.participants
        ]
        
        if not speaking_npcs:
            logger.warning("No NPCs available for dialogue")
            return DialogueEntry(
                turn=current_turn,
                timestamp=datetime.now(),
                dialogue_type=dialogue_type,
                context=context,
                dialogues=[]
            )
        
        # 根据NPC状态决定谁会说话
        speakers = self._select_speakers(speaking_npcs, dialogue_type)
        
        # 准备NPC状态数据
        npc_states = []
        for npc in speakers:
            state = {
                "id": npc.id,
                "name": npc.name,
                "fear": npc.fear,
                "sanity": npc.sanity,
                "status": npc.status.value,
                "rationality": npc.personality.rationality,
                "courage": npc.personality.courage,
                "personality": {
                    "rationality": npc.personality.rationality,
                    "courage": npc.personality.courage,
                    "curiosity": npc.personality.curiosity,
                    "sociability": npc.personality.sociability
                }
            }
            
            # 添加记忆相关信息
            if npc.memory.known_rules:
                state["knows_rules"] = True
                state["known_rules_count"] = len(npc.memory.known_rules)
            
            npc_states.append(state)
        
        # 准备场景上下文
        scene_context = {
            "location": context.location,
            "time": context.time,
            "mood": context.mood,
            "recent_events": self._format_recent_events(context.recent_events),
            "discovered_clues": context.discovered_clues
        }
        
        # 调用API生成对话
        try:
            dialogues = await self.api_client.generate_dialogue(
                npc_states,
                scene_context,
                dialogue_type.value
            )
            
            # 添加speaker_id到对话中
            for dialogue in dialogues:
                speaker_name = dialogue["speaker"]
                speaker_npc = next((npc for npc in speakers if npc.name == speaker_name), None)
                if speaker_npc:
                    dialogue["speaker_id"] = speaker_npc.id
            
        except Exception as e:
            logger.error(f"Failed to generate dialogue via API: {e}")
            # 使用备选模板生成
            dialogues = self._generate_fallback_dialogue(speakers, dialogue_type, context)
        
        # 计算对话效果
        effects = self._calculate_dialogue_effects(speakers, dialogues, dialogue_type)
        
        # 创建对话记录
        entry = DialogueEntry(
            turn=current_turn,
            timestamp=datetime.now(),
            dialogue_type=dialogue_type,
            context=context,
            dialogues=dialogues,
            effects=effects
        )
        
        # 保存到历史
        self.history.add_entry(entry)
        
        # 应用对话效果到NPC
        self._apply_dialogue_effects(npcs, effects)
        
        return entry
    
    def _select_speakers(self, npcs: List[NPC], dialogue_type: DialogueType) -> List[NPC]:
        """选择会说话的NPC"""
        # 根据对话类型和NPC状态选择
        speakers = []
        
        for npc in npcs:
            speak_chance = 0.5  # 基础概率
            
            # 根据性格调整
            speak_chance += (npc.personality.sociability - 5) * 0.1
            
            # 根据状态调整
            if npc.status == NPCStatus.PANICKED:
                if dialogue_type == DialogueType.PANIC:
                    speak_chance += 0.3
                else:
                    speak_chance -= 0.2
            elif npc.status == NPCStatus.FRIGHTENED:
                speak_chance += 0.1
            
            # 根据对话类型调整
            if dialogue_type == DialogueType.DISCOVERY and npc.memory.known_rules:
                speak_chance += 0.4
            elif dialogue_type == DialogueType.COOPERATION and npc.personality.sociability > 6:
                speak_chance += 0.3
            
            # 限制说话人数
            if len(speakers) < 3 and random.random() < speak_chance:
                speakers.append(npc)
        
        # 确保至少有一个人说话
        if not speakers and npcs:
            speakers = [random.choice(npcs)]
        
        return speakers
    
    def _format_recent_events(self, events: List[Dict[str, Any]]) -> str:
        """格式化最近事件描述"""
        if not events:
            return "无特殊事件"
        
        descriptions = []
        for event in events[-3:]:  # 只取最近3个事件
            event_type = event.get("type", "unknown")
            if event_type == "npc_death":
                descriptions.append(f"{event.get('victim', '某人')}死亡")
            elif event_type == "rule_triggered":
                descriptions.append(f"触发了{event.get('rule_name', '未知规则')}")
            elif event_type == "discovery":
                descriptions.append(f"发现了{event.get('item', '某物')}")
        
        return "；".join(descriptions)
    
    def _generate_fallback_dialogue(
        self,
        speakers: List[NPC],
        dialogue_type: DialogueType,
        context: DialogueContext
    ) -> List[Dict[str, str]]:
        """生成备选对话（当API失败时）"""
        dialogues = []
        templates = self.dialogue_templates.get(dialogue_type, ["..."])
        
        for i, npc in enumerate(speakers[:2]):  # 最多2人
            template = random.choice(templates)
            
            # 简单的模板替换
            text = template
            if "{name}" in text and context.recent_events:
                # 如果有死亡事件，替换为死者名字
                for event in context.recent_events:
                    if event.get("type") == "npc_death":
                        text = text.replace("{name}", event.get("victim", "某人"))
                        break
            
            if "{clue}" in text and context.discovered_clues:
                text = text.replace("{clue}", random.choice(context.discovered_clues))
            
            dialogues.append({
                "speaker": npc.name,
                "speaker_id": npc.id,
                "text": text
            })
        
        return dialogues
    
    def _calculate_dialogue_effects(
        self,
        speakers: List[NPC],
        dialogues: List[Dict[str, str]],
        dialogue_type: DialogueType
    ) -> List[Dict[str, Any]]:
        """计算对话产生的效果"""
        effects = []
        
        # 基于对话类型的效果
        if dialogue_type == DialogueType.PANIC:
            # 恐慌对话增加周围人的恐惧
            effects.append({
                "type": "fear_spread",
                "targets": "all_nearby",
                "amount": 10
            })
        
        elif dialogue_type == DialogueType.COOPERATION:
            # 合作对话减少恐惧，增加信任
            for speaker in speakers:
                effects.append({
                    "type": "reduce_fear",
                    "target": speaker.id,
                    "amount": 5
                })
                effects.append({
                    "type": "increase_trust",
                    "source": speaker.id,
                    "amount": 2
                })
        
        elif dialogue_type == DialogueType.DISCOVERY:
            # 发现线索可能让其他人学到规则
            effects.append({
                "type": "share_knowledge",
                "probability": 0.5
            })
        
        elif dialogue_type == DialogueType.EMERGENCY:
            # 紧急情况大幅增加恐惧
            effects.append({
                "type": "fear_spike",
                "targets": "all",
                "amount": 20
            })
        
        # 基于对话内容的效果（简单关键词匹配）
        for dialogue in dialogues:
            text = dialogue["text"].lower()
            
            if any(word in text for word in ["冷静", "团结", "一起"]):
                effects.append({
                    "type": "morale_boost",
                    "source": dialogue["speaker_id"],
                    "amount": 5
                })
            
            elif any(word in text for word in ["死", "杀", "鬼", "诡异"]):
                effects.append({
                    "type": "fear_increase",
                    "targets": "listeners",
                    "amount": 5
                })
        
        return effects
    
    def _apply_dialogue_effects(self, all_npcs: List[NPC], effects: List[Dict[str, Any]]):
        """应用对话效果到NPC"""
        for effect in effects:
            effect_type = effect.get("type")
            
            if effect_type == "fear_spread":
                amount = effect.get("amount", 10)
                for npc in all_npcs:
                    if npc.status != NPCStatus.DEAD:
                        npc.add_fear(amount)
            
            elif effect_type == "reduce_fear":
                target_id = effect.get("target")
                amount = effect.get("amount", 5)
                target_npc = next((npc for npc in all_npcs if npc.id == target_id), None)
                if target_npc:
                    target_npc.reduce_fear(amount)
            
            elif effect_type == "increase_trust":
                source_id = effect.get("source")
                source_npc = next((npc for npc in all_npcs if npc.id == source_id), None)
                if source_npc:
                    # 增加与其他参与者的信任度
                    for npc in all_npcs:
                        if npc.id != source_id and npc.id in source_npc.relationships:
                            source_npc.relationships[npc.id] += effect.get("amount", 2)
            
            elif effect_type == "share_knowledge":
                # 概率性分享规则知识
                probability = effect.get("probability", 0.5)
                knowledgeable_npcs = [npc for npc in all_npcs if npc.memory.known_rules]
                
                for teacher in knowledgeable_npcs:
                    for student in all_npcs:
                        if (student.id != teacher.id and 
                            random.random() < probability and
                            student.personality.rationality >= 5):
                            # 随机学习一条规则
                            if teacher.memory.known_rules:
                                rule = random.choice(teacher.memory.known_rules)
                                student.memory.remember_rule(rule)
                                logger.info(f"{student.name} learned rule {rule} from {teacher.name}")
    
    def should_trigger_dialogue(
        self,
        game_state: Dict[str, Any],
        last_dialogue_turn: int
    ) -> Optional[DialogueType]:
        """判断是否应该触发对话"""
        current_turn = game_state.get("current_turn", 0)
        time_of_day = game_state.get("time_of_day", "morning")
        recent_events = game_state.get("recent_events", [])
        
        # 固定时间点对话
        if time_of_day == "morning" and current_turn > last_dialogue_turn:
            return DialogueType.MORNING
        elif time_of_day == "night" and current_turn > last_dialogue_turn:
            return DialogueType.NIGHT
        
        # 事件触发对话
        for event in recent_events:
            event_type = event.get("type")
            event_turn = event.get("turn", 0)
            
            # 如果事件刚发生且还没有对话响应
            if event_turn == current_turn:
                if event_type == "npc_death":
                    return DialogueType.EMERGENCY
                elif event_type == "rule_discovered":
                    return DialogueType.DISCOVERY
                elif event_type == "panic_event":
                    return DialogueType.PANIC
        
        return None
    
    def get_dialogue_summary(self, turn_range: Optional[Tuple[int, int]] = None) -> str:
        """获取对话摘要"""
        entries = self.history.entries
        
        if turn_range:
            entries = [e for e in entries if turn_range[0] <= e.turn <= turn_range[1]]
        
        if not entries:
            return "暂无对话记录"
        
        summary = []
        for entry in entries[-5:]:  # 最近5轮对话
            summary.append(f"\n回合{entry.turn} - {entry.dialogue_type.value}对话：")
            for dialogue in entry.dialogues:
                summary.append(f"  {dialogue['speaker']}: {dialogue['text']}")
        
        return "\n".join(summary)


# 测试代码
if __name__ == "__main__":
    async def test_dialogue_system():
        # 创建测试NPC
        from src.models.npc import generate_random_npc
        
        npcs = [
            generate_random_npc("小明"),
            generate_random_npc("小红"),
            generate_random_npc("老王")
        ]
        
        # 设置一些状态
        npcs[0].add_fear(60)  # 小明很害怕
        npcs[1].memory.remember_rule("mirror_death")  # 小红知道一条规则
        
        # 创建对话系统
        dialogue_system = DialogueSystem()
        
        # 创建对话上下文
        context = DialogueContext(
            location="废弃客厅",
            time="深夜",
            participants=[npc.id for npc in npcs],
            recent_events=[{
                "type": "strange_sound",
                "description": "楼上传来脚步声",
                "turn": 1
            }],
            mood="fearful"
        )
        
        # 生成早间对话
        print("=== 早间对话 ===")
        morning_dialogue = await dialogue_system.generate_dialogue_round(
            npcs, context, DialogueType.MORNING, 1
        )
        
        for d in morning_dialogue.dialogues:
            print(f"{d['speaker']}: {d['text']}")
        
        # 模拟发生死亡事件后的紧急对话
        print("\n=== 紧急对话 ===")
        context.recent_events.append({
            "type": "npc_death",
            "victim": "张三",
            "turn": 2
        })
        
        emergency_dialogue = await dialogue_system.generate_dialogue_round(
            npcs, context, DialogueType.EMERGENCY, 2
        )
        
        for d in emergency_dialogue.dialogues:
            print(f"{d['speaker']}: {d['text']}")
        
        # 显示对话摘要
        print("\n=== 对话摘要 ===")
        print(dialogue_system.get_dialogue_summary())
        
        # 关闭API客户端
        await dialogue_system.api_client.close()
    
    # 运行测试
    asyncio.run(test_dialogue_system())
