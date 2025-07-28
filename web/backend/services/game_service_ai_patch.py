"""
AI功能集成补丁
添加到GameService类中的方法
"""

# 添加以下导入到GameService文件顶部
# from src.ai.turn_pipeline import AITurnPipeline
# from src.core.game_state import GameStateManager

# 在GameService.__init__方法中添加
# self.ai_enabled = False
# self.ai_pipeline = None
# self.game_state_manager = None

# 添加以下方法到GameService类

async def init_ai_pipeline(self) -> bool:
    """初始化AI管线"""
    try:
        if not self._initialized:
            await self.initialize()
        
        # 创建GameStateManager适配器
        from src.core.game_state import GameStateManager
        self.game_state_manager = GameStateManager()
        
        # 同步游戏状态
        self.game_state_manager.state = self.game_state
        self.game_state_manager.rules = self.rule_manager.active_rules
        self.game_state_manager.npcs = list(self.npc_manager.npcs.values())
        
        # 初始化AI管线
        from src.ai.turn_pipeline import AITurnPipeline
        from src.api.deepseek_client import DeepSeekClient
        from src.config import Config
        
        config = Config()
        ds_client = DeepSeekClient(config.api)
        self.ai_pipeline = AITurnPipeline(self.game_state_manager, ds_client)
        
        self.ai_enabled = True
        logger.info(f"AI pipeline initialized for game: {self.game_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize AI pipeline: {e}")
        self.ai_enabled = False
        return False

def is_ai_enabled(self) -> bool:
    """检查AI是否启用"""
    return self.ai_enabled

def is_ai_initialized(self) -> bool:
    """检查AI是否已初始化"""
    return self.ai_pipeline is not None

async def run_ai_turn(self, force_dialogue: bool = True) -> Dict:
    """执行AI驱动的回合"""
    if not self.ai_enabled or not self.ai_pipeline:
        raise ValueError("AI not initialized")
    
    try:
        # 同步最新状态
        self._sync_state_to_manager()
        
        # 执行AI回合
        plan = await self.ai_pipeline.run_turn_ai()
        
        # 同步状态回游戏
        self._sync_state_from_manager()
        
        # 转换为响应格式
        from ..models import AITurnPlanResponse, AIDialogueResponse, AIActionResponse
        
        dialogue_responses = []
        for d in plan.dialogue:
            dialogue_responses.append(AIDialogueResponse(
                speaker=d.speaker,
                text=d.text,
                emotion=getattr(d, 'emotion', None)
            ))
        
        action_responses = []
        for a in plan.actions:
            action_responses.append(AIActionResponse(
                npc=a.npc,
                action=a.action,
                target=a.target,
                reason=a.reason,
                risk=a.risk,
                priority=getattr(a, 'priority', 1)
            ))
        
        response = AITurnPlanResponse(
            dialogue=dialogue_responses,
            actions=action_responses,
            turn_summary=f"回合{self.game_state.current_turn}：生成了{len(dialogue_responses)}条对话和{len(action_responses)}个行动",
            atmosphere=self.game_state.time_of_day
        )
        
        # 广播AI生成的内容
        await self.broadcast_update({
            "update_type": "ai_turn",
            "data": response.dict()
        })
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"AI turn execution failed: {e}")
        raise

async def evaluate_rule_nl(self, rule_description: str) -> Dict:
    """评估自然语言规则"""
    if not self.ai_enabled or not self.ai_pipeline:
        raise ValueError("AI not initialized")
    
    try:
        result = await self.ai_pipeline.evaluate_player_rule(rule_description)
        
        from ..models import AIRuleEvaluationResponse
        response = AIRuleEvaluationResponse(
            name=result["name"],
            cost=result["cost"],
            difficulty=result["difficulty"],
            loopholes=result["loopholes"],
            suggestion=result["suggestion"],
            estimated_fear_gain=result.get("estimated_fear_gain"),
            parsed_rule=result["parsed_rule"]
        )
        
        return response.dict()
        
    except Exception as e:
        logger.error(f"Rule evaluation failed: {e}")
        raise

async def generate_narrative(self, include_hidden: bool = False) -> str:
    """生成回合叙事"""
    if not self.ai_enabled or not self.ai_pipeline:
        raise ValueError("AI not initialized")
    
    try:
        narrative = await self.ai_pipeline.generate_turn_narrative()
        
        # 如果不包含隐藏事件，过滤掉某些内容
        if not include_hidden:
            # 这里可以添加过滤逻辑
            pass
        
        return narrative
        
    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        raise

def _sync_state_to_manager(self):
    """同步游戏状态到GameStateManager"""
    if not self.game_state_manager:
        return
    
    # 同步基本状态
    self.game_state_manager.state = self.game_state
    
    # 同步规则
    self.game_state_manager.rules = self.rule_manager.active_rules
    
    # 同步NPC（转换格式）
    npcs = []
    for npc_id, npc_data in self.game_state.npcs.items():
        npc_dict = {
            'id': npc_id,
            'name': npc_data.get('name', 'Unknown'),
            'hp': npc_data.get('hp', 100),
            'sanity': npc_data.get('sanity', 100),
            'fear': npc_data.get('fear', 0),
            'location': npc_data.get('location', 'unknown'),
            'traits': npc_data.get('traits', []),
            'status': npc_data.get('status', 'normal'),
            'is_alive': npc_data.get('hp', 100) > 0
        }
        npcs.append(npc_dict)
    self.game_state_manager.npcs = npcs

def _sync_state_from_manager(self):
    """从GameStateManager同步状态回游戏"""
    if not self.game_state_manager:
        return
    
    # 同步事件历史
    self.game_state = self.game_state_manager.state
    
    # 同步NPC状态变化
    for npc in self.game_state_manager.npcs:
        if isinstance(npc, dict):
            npc_id = npc.get('id')
            if npc_id and npc_id in self.game_state.npcs:
                self.game_state.npcs[npc_id].update({
                    'hp': npc.get('hp', 100),
                    'sanity': npc.get('sanity', 100),
                    'fear': npc.get('fear', 0),
                    'location': npc.get('location', 'unknown'),
                    'status': npc.get('status', 'normal')
                })
