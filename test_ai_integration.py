"""
测试AI集成功能
"""
import asyncio
import logging
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from web.backend.services.game_service import GameService
from web.backend.models import AITurnRequest, AIRuleEvaluationRequest, AINarrativeRequest

# 设置日志
logger = setup_logger("test_ai_integration")


async def test_ai_functions():
    """测试AI功能"""
    logger.info("开始测试AI集成功能...")
    
    # 1. 创建游戏服务
    game_service = GameService(npc_count=4)
    await game_service.initialize()
    logger.info(f"游戏服务初始化完成: {game_service.game_id}")
    
    # 2. 初始化AI
    logger.info("初始化AI管线...")
    success = await game_service.init_ai_pipeline()
    if not success:
        logger.error("AI初始化失败")
        return
    
    logger.info("AI初始化成功")
    
    # 3. 测试AI回合生成
    logger.info("\n测试AI回合生成...")
    try:
        ai_turn_result = await game_service.run_ai_turn(force_dialogue=True)
        logger.info(f"生成了 {len(ai_turn_result['dialogue'])} 条对话")
        logger.info(f"生成了 {len(ai_turn_result['actions'])} 个行动")
        
        # 打印对话示例
        if ai_turn_result['dialogue']:
            logger.info("\n对话示例:")
            for d in ai_turn_result['dialogue'][:2]:
                logger.info(f"  {d['speaker']}: {d['text']}")
        
        # 打印行动示例
        if ai_turn_result['actions']:
            logger.info("\n行动示例:")
            for a in ai_turn_result['actions'][:2]:
                logger.info(f"  {a['npc']} -> {a['action']} {a.get('target', '')}")
    except Exception as e:
        logger.error(f"AI回合生成失败: {e}")
    
    # 4. 测试规则评估
    logger.info("\n测试自然语言规则评估...")
    try:
        rule_description = "晚上10点后不能开灯，否则会吸引怪物"
        eval_result = await game_service.evaluate_rule_nl(rule_description)
        logger.info(f"规则名称: {eval_result['name']}")
        logger.info(f"成本: {eval_result['cost']}")
        logger.info(f"难度: {eval_result['difficulty']}")
        logger.info(f"破绽: {eval_result['loopholes']}")
        logger.info(f"建议: {eval_result['suggestion']}")
    except Exception as e:
        logger.error(f"规则评估失败: {e}")
    
    # 5. 测试叙事生成
    logger.info("\n测试叙事生成...")
    try:
        # 先推进一个回合产生一些事件
        await game_service.advance_turn()
        
        narrative = await game_service.generate_narrative(include_hidden=False)
        logger.info(f"生成叙事长度: {len(narrative)} 字")
        logger.info(f"叙事片段: {narrative[:100]}...")
    except Exception as e:
        logger.error(f"叙事生成失败: {e}")
    
    # 6. 清理
    await game_service.cleanup()
    logger.info("\n测试完成！")


async def test_web_api():
    """测试Web API端点"""
    import httpx
    
    logger.info("\n测试Web API端点...")
    
    # 启动一个测试服务器（需要先运行 web/backend/app.py）
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. 创建游戏
            response = await client.post(f"{base_url}/api/games", json={
                "difficulty": "normal",
                "npc_count": 4
            })
            if response.status_code == 200:
                game_data = response.json()
                game_id = game_data["game_id"]
                logger.info(f"创建游戏成功: {game_id}")
            else:
                logger.error(f"创建游戏失败: {response.status_code}")
                return
            
            # 2. 初始化AI
            response = await client.post(f"{base_url}/api/games/{game_id}/ai/init")
            if response.status_code == 200:
                logger.info("AI初始化成功")
            else:
                logger.error(f"AI初始化失败: {response.status_code}")
                return
            
            # 3. 检查AI状态
            response = await client.get(f"{base_url}/api/games/{game_id}/ai/status")
            if response.status_code == 200:
                ai_status = response.json()
                logger.info(f"AI状态: {ai_status}")
            
            # 4. 测试AI回合
            response = await client.post(f"{base_url}/api/games/{game_id}/ai/turn", json={
                "force_dialogue": True
            })
            if response.status_code == 200:
                ai_turn = response.json()
                logger.info(f"AI回合生成成功: {len(ai_turn['dialogue'])} 条对话")
            else:
                logger.error(f"AI回合生成失败: {response.status_code}")
            
            # 5. 测试规则评估
            response = await client.post(f"{base_url}/api/games/{game_id}/ai/evaluate-rule", json={
                "rule_description": "午夜时分不能照镜子"
            })
            if response.status_code == 200:
                eval_result = response.json()
                logger.info(f"规则评估成功: {eval_result['name']} - 成本{eval_result['cost']}")
            else:
                logger.error(f"规则评估失败: {response.status_code}")
                
        except httpx.ConnectError:
            logger.error("无法连接到API服务器，请确保服务器正在运行")
        except Exception as e:
            logger.error(f"测试失败: {e}")


if __name__ == "__main__":
    # 选择测试模式
    print("选择测试模式:")
    print("1. 测试AI功能（直接调用）")
    print("2. 测试Web API（需要先启动服务器）")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(test_ai_functions())
    elif choice == "2":
        asyncio.run(test_web_api())
    else:
        print("无效选择")
