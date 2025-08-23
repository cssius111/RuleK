#!/usr/bin/env python3
"""测试规则创建功能"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
from src.core.game_state import GameState
from web.backend.services.rule_service import RuleService
from src.utils.logger import setup_logger

logger = setup_logger("test_rule_creation")

async def test_rule_creation():
    """测试规则创建功能"""
    logger.info("=" * 60)
    logger.info("测试规则创建功能")
    logger.info("=" * 60)
    
    # 创建游戏状态
    game_state = GameState()
    game_state.fear_points = 1000  # 给足够的恐惧点数
    
    # 初始化规则服务
    rule_service = RuleService(game_state)
    
    # 1. 测试从模板创建规则
    logger.info("\n1. 测试从模板创建规则")
    logger.info("-" * 40)
    
    try:
        # 获取第一个模板
        template_id = "midnight_mirror"
        rule = rule_service.create_rule_from_template(template_id)
        
        if rule:
            logger.info(f"✅ 成功创建规则: {rule.name}")
            logger.info(f"   - ID: {rule.id}")
            logger.info(f"   - 描述: {rule.description}")
            logger.info(f"   - 成本: {rule.cost}")
            logger.info(f"   - 剩余恐惧点数: {game_state.fear_points}")
        else:
            logger.error("❌ 创建规则失败: 模板未找到")
    except Exception as e:
        logger.error(f"❌ 创建规则失败: {e}")
    
    # 2. 测试创建自定义规则
    logger.info("\n2. 测试创建自定义规则")
    logger.info("-" * 40)
    
    custom_rule_data = {
        "name": "测试规则",
        "description": "这是一个测试规则",
        "trigger": {
            "type": "action",
            "conditions": {
                "action": "test_action"
            },
            "probability": 0.8
        },
        "effects": [
            {
                "type": "fear_increase",
                "value": 30,
                "target": "trigger_npc"
            }
        ],
        "cooldown": 2
    }
    
    try:
        # 计算成本
        cost = rule_service.calculate_rule_cost(custom_rule_data)
        logger.info(f"计算的规则成本: {cost}")
        
        # 创建规则
        custom_rule = rule_service.create_custom_rule(custom_rule_data)
        
        if custom_rule:
            logger.info(f"✅ 成功创建自定义规则: {custom_rule.name}")
            logger.info(f"   - ID: {custom_rule.id}")
            logger.info(f"   - 成本: {custom_rule.cost}")
            logger.info(f"   - 剩余恐惧点数: {game_state.fear_points}")
        else:
            logger.error("❌ 创建自定义规则失败")
    except Exception as e:
        logger.error(f"❌ 创建自定义规则失败: {e}")
    
    # 3. 测试规则成本计算
    logger.info("\n3. 测试规则成本计算")
    logger.info("-" * 40)
    
    test_rules = [
        {
            "name": "低成本规则",
            "trigger": {"type": "action", "probability": 1.0},
            "effects": [{"type": "fear_increase", "value": 10}]
        },
        {
            "name": "高成本规则",
            "trigger": {"type": "action", "probability": 1.0},
            "effects": [{"type": "instant_death"}]
        },
        {
            "name": "带冷却的规则",
            "trigger": {"type": "action", "probability": 0.5},
            "effects": [{"type": "fear_increase", "value": 50}],
            "cooldown": 5
        }
    ]
    
    for rule_data in test_rules:
        cost = rule_service.calculate_rule_cost(rule_data)
        logger.info(f"规则 '{rule_data['name']}' 的成本: {cost}")
    
    # 4. 测试获取激活的规则
    logger.info("\n4. 测试获取激活的规则")
    logger.info("-" * 40)
    
    active_rules = rule_service.get_active_rules()
    logger.info(f"当前激活的规则数量: {len(active_rules)}")
    for rule in active_rules:
        logger.info(f"  - {rule.name} (激活: {rule.is_active})")
    
    # 5. 测试规则切换
    logger.info("\n5. 测试规则切换激活状态")
    logger.info("-" * 40)
    
    if active_rules:
        first_rule = active_rules[0]
        logger.info(f"切换规则 '{first_rule.name}' 的激活状态")
        new_state = rule_service.toggle_rule(first_rule.id)
        logger.info(f"新状态: {'激活' if new_state else '禁用'}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ 规则创建功能测试完成")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_rule_creation())
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"测试失败: {e}")
        sys.exit(1)
