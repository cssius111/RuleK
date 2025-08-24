"""
FastAPI 主应用
规则怪谈管理者 Web API 服务
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 存档目录
SAVE_DIR = (project_root / "data" / "saves").resolve()

from src.core.game_state import GameState
from src.models.rule import Rule
from src.models.npc import NPC
from src.core.narrator import Narrator
from src.core.dialogue_system import DialogueSystem
from src.models.map import MapManager
from src.core.npc_behavior import NPCBehavior
from src.core.rule_executor import RuleExecutor
from src.utils.logger import setup_logger

# 导入数据模型
from .models import (
    GameCreateRequest, GameStateResponse, RuleCreateRequest,
    ActionRequest, WebSocketMessage,
    # AI相关模型
    AITurnRequest, AITurnPlanResponse,
    AIRuleEvaluationRequest, AIRuleEvaluationResponse,
    AINarrativeRequest, AINarrativeResponse,
    AIDialogueResponse, AIActionResponse
)
from .services.game_service import GameService
from .services.session_manager import SessionManager
from .services.streaming_service import streaming_service

# 设置日志
logger = setup_logger("api")

# 全局会话管理器
session_manager = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting RuleK Web API...")
    # 启动时的初始化
    yield
    # 关闭时的清理
    logger.info("Shutting down RuleK Web API...")
    await session_manager.cleanup()

# 创建FastAPI应用
app = FastAPI(
    title="规则怪谈管理者 API",
    description="Rule-based Horror Game Management System",
    version="0.3.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue/React开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== API路由 ====================

@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "RuleK API",
        "version": "0.3.0",
        "status": "running",
        "endpoints": {
            "games": "/api/games",
            "docs": "/docs",
            "websocket": "/ws/{game_id}"
        }
    }

@app.post("/api/games", response_model=GameStateResponse)
async def create_game(request: GameCreateRequest):
    """创建新游戏"""
    try:
        game_service = await session_manager.create_game(
            difficulty=request.difficulty,
            npc_count=request.npc_count
        )
        return game_service.get_state_response()
    except Exception as e:
        logger.error(f"Failed to create game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    """获取游戏状态"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_service.get_state_response()

@app.delete("/api/games/{game_id}")
async def delete_game(game_id: str):
    """删除游戏"""
    if not session_manager.remove_game(game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}

@app.post("/api/games/{game_id}/turn")
async def advance_turn(game_id: str):
    """推进游戏回合"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        result = await game_service.advance_turn()
        return result
    except Exception as e:
        logger.error(f"Failed to advance turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules")
async def create_rule(game_id: str, request: RuleCreateRequest):
    """创建新规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        rule_id = await game_service.create_rule(request.model_dump())
        return {"rule_id": rule_id, "cost": request.cost}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}/rules")
async def get_rules(game_id: str):
    """获取游戏规则列表"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game_service.get_rules()

@app.get("/api/games/{game_id}/npcs")
async def get_npcs(game_id: str):
    """获取NPC列表"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game_service.get_npcs()

@app.post("/api/games/{game_id}/save")
async def save_game(game_id: str):
    """保存游戏"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        filename = await game_service.save_game()
        return {"filename": filename, "message": "Game saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/load")
async def load_game(filename: str):
    """加载游戏存档"""
    path = Path(filename)
    if ".." in path.parts:
        raise HTTPException(status_code=400, detail="Invalid filename")

    resolved = (SAVE_DIR / path).resolve()
    if not resolved.is_relative_to(SAVE_DIR):
        raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        relative = resolved.relative_to(SAVE_DIR)
        game_service = await session_manager.load_game(str(relative))
        return game_service.get_state_response()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Save file not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to load game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI相关API ====================

@app.post("/api/games/{game_id}/ai/turn", response_model=AITurnPlanResponse)
async def run_ai_turn(game_id: str, request: AITurnRequest):
    """执行AI驱动的回合"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # 检查游戏是否启用AI
    if not game_service.is_ai_enabled():
        raise HTTPException(status_code=400, detail="AI is not enabled for this game")
    
    try:
        plan = await game_service.run_ai_turn(
            force_dialogue=request.force_dialogue
        )
        return plan
    except Exception as e:
        logger.error(f"Failed to run AI turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/ai/evaluate-rule", response_model=AIRuleEvaluationResponse)
async def evaluate_rule_ai(game_id: str, request: AIRuleEvaluationRequest):
    """使用AI评估自然语言规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game_service.is_ai_enabled():
        raise HTTPException(status_code=400, detail="AI is not enabled for this game")
    
    try:
        result = await game_service.evaluate_rule_nl(
            rule_description=request.rule_description
        )
        return result
    except Exception as e:
        logger.error(f"Failed to evaluate rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/ai/narrative", response_model=AINarrativeResponse)
async def generate_narrative(game_id: str, request: AINarrativeRequest):
    """AI生成回合叙事"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game_service.is_ai_enabled():
        raise HTTPException(status_code=400, detail="AI is not enabled for this game")
    
    try:
        narrative = await game_service.generate_narrative(
            include_hidden=request.include_hidden_events
        )
        return AINarrativeResponse(
            narrative=narrative,
            word_count=len(narrative),
            style=request.style
        )
    except Exception as e:
        logger.error(f"Failed to generate narrative: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}/ai/status")
async def get_ai_status(game_id: str):
    """AI状态检查"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "ai_enabled": game_service.is_ai_enabled(),
        "ai_initialized": game_service.is_ai_initialized(),
        "features": {
            "dialogue_generation": True,
            "action_planning": True,
            "narrative_generation": True,
            "rule_evaluation": True
        }
    }

@app.post("/api/games/{game_id}/ai/init")
async def initialize_ai(game_id: str):
    """初始化AI系统"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        success = await game_service.init_ai_pipeline()
        if success:
            return {"message": "AI initialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize AI")
    except Exception as e:
        logger.error(f"Failed to initialize AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WebSocket ====================

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket连接处理 - 使用StreamingService"""
    # 验证游戏是否存在
    game_service = session_manager.get_game(game_id)
    if not game_service:
        await websocket.close(code=4004, reason="Game not found")
        return
    
    # 使用客户端ID（组合game_id和时间戳）
    import time
    client_id = f"{game_id}_{int(time.time() * 1000)}"
    
    # 通过StreamingService建立连接
    await streaming_service.connect(websocket, client_id)
    
    # 将客户端ID关联到游戏
    game_service.add_websocket_client(client_id)
    
    try:
        while True:
            # 接收客户端消息
            message_text = await websocket.receive_text()
            
            # 处理消息（通过streaming_service）
            await streaming_service.handle_message(client_id, message_text)
            
            # 解析消息来处理游戏逻辑
            try:
                import json
                data = json.loads(message_text)
                msg_type = data.get("type")
                
                if msg_type == "action":
                    # 处理游戏动作
                    result = await game_service.handle_action(data.get("data", {}))
                    
                    # 通过streaming_service广播更新
                    await streaming_service.send_message(client_id, {
                        "type": "game_update",
                        "data": result
                    })
                    
                elif msg_type == "turn":
                    # 处理回合推进
                    result = await game_service.advance_turn()
                    
                    # 流式发送回合结果
                    async def generate_turn_chunks():
                        for event in result.get("events", []):
                            yield json.dumps(event)
                            await asyncio.sleep(0.1)  # 控制流速
                    
                    await streaming_service.send_stream(client_id, generate_turn_chunks())
                    
            except json.JSONDecodeError:
                pass  # 忽略非JSON消息（如ping/pong）
            
    except WebSocketDisconnect:
        # 断开连接
        await streaming_service.disconnect(client_id)
        game_service.remove_websocket_client(client_id)
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await streaming_service.disconnect(client_id)
        game_service.remove_websocket_client(client_id)

# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_games": session_manager.get_active_game_count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


# ==================== 规则管理API ====================

@app.get("/api/rules/templates")
async def get_rule_templates():
    """获取所有规则模板"""
    try:
        # 加载规则模板
        template_file = Path("data/rule_templates.json")
        if template_file.exists():
            import json
            with open(template_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return {"success": True, "templates": templates}
        else:
            return {"success": True, "templates": []}
    except Exception as e:
        logger.error(f"Failed to load rule templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/template")
async def create_rule_from_template(game_id: str, request: Dict):
    """从模板创建规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        template_id = request.get("template_id")
        
        # 从rule_service创建规则
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        rule = rule_service.create_rule_from_template(template_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # 添加到游戏状态
        game_service.game_state.add_rule(rule)
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "cost": rule.cost,
                "trigger": rule.trigger.dict(),
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create rule from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/custom")
async def create_custom_rule(game_id: str, request: Dict):
    """创建自定义规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        
        # 创建自定义规则
        rule = rule_service.create_custom_rule(request)
        
        # 添加到游戏状态
        game_service.game_state.add_rule(rule)
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "cost": rule.cost,
                "trigger": rule.trigger.dict(),
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create custom rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}/rules")
async def get_game_rules(game_id: str):
    """获取游戏中的所有规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    rules = []
    for rule in game_service.game_state.rules:
        rules.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "level": getattr(rule, 'level', 1),
            "is_active": getattr(rule, 'is_active', True),
            "cooldown": getattr(rule, 'cooldown', 0)
        })
    
    return {
        "success": True,
        "rules": rules,
        "total_count": len(rules)
    }

@app.put("/api/games/{game_id}/rules/{rule_id}/toggle")
async def toggle_rule(game_id: str, rule_id: str):
    """切换规则激活状态"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        is_active = rule_service.toggle_rule(rule_id)
        
        return {
            "success": True,
            "rule_id": rule_id,
            "is_active": is_active
        }
    except Exception as e:
        logger.error(f"Failed to toggle rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/games/{game_id}/rules/{rule_id}/upgrade")
async def upgrade_rule(game_id: str, rule_id: str):
    """升级规则"""
    game_service = session_manager.get_game(game_id)
    if not game_service:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        from .services.rule_service import RuleService
        rule_service = RuleService(game_service.game_state)
        rule = rule_service.upgrade_rule(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return {
            "success": True,
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "level": rule.level,
                "effects": [e.dict() for e in rule.effects]
            },
            "remaining_fear_points": game_service.game_state.fear_points
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upgrade rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/parse-rule")
async def parse_rule_with_ai(request: Dict):
    """使用AI解析自然语言规则描述"""
    description = request.get("description", "")
    game_id = request.get("game_id")
    
    if not description:
        raise HTTPException(status_code=400, detail="Description is required")
    
    try:
        # 这里集成AI服务
        # 暂时返回模拟数据
        parsed_rule = {
            "rule_name": "AI解析的规则",
            "description": description,
            "trigger": {
                "type": "condition",
                "conditions": {},
                "probability": 0.7
            },
            "effects": [
                {
                    "type": "fear_increase",
                    "value": 40,
                    "target": "trigger_npc"
                }
            ],
            "estimated_cost": 350,
            "suggestions": [
                "建议添加更具体的触发条件",
                "可以增加冷却时间以平衡游戏性",
                "考虑添加多重效果以增加趣味性"
            ]
        }
        
        return {
            "success": True,
            **parsed_rule
        }
    except Exception as e:
        logger.error(f"Failed to parse rule with AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 规则计算API ====================

@app.post("/api/rules/calculate-cost")
async def calculate_rule_cost(request: Dict):
    """计算规则成本"""
    try:
        from .services.rule_service import RuleService
        
        # 创建临时的RuleService实例来计算成本
        rule_service = RuleService(None)
        cost = rule_service.calculate_rule_cost(request)
        
        return {
            "success": True,
            "cost": cost,
            "breakdown": {
                "base_cost": 100,
                "effect_cost": cost - 100,
                "probability_modifier": request.get("trigger", {}).get("probability", 1.0),
                "cooldown_modifier": request.get("cooldown", 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to calculate rule cost: {e}")
        raise HTTPException(status_code=500, detail=str(e))
