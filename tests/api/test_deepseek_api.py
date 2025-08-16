"""
API测试模块 - 测试DeepSeek集成
"""
import pytest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.deepseek_client import DeepSeekClient
from unittest.mock import patch, MagicMock, AsyncMock


class TestDeepSeekAPI:
    """DeepSeek API测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        # 不管是否有API密钥，都创建客户端（没有密钥会自动使用mock模式）
        return DeepSeekClient()
    
    @pytest.fixture
    def mock_client(self):
        """创建模拟客户端"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test_key"}):
            return DeepSeekClient()
    
    @pytest.mark.asyncio
    async def test_api_connection(self, client):
        """测试API连接"""
        print("测试API连接...")
        
        # 测试简单的对话生成
        try:
            response = await client.generate_dialogue_async(
                context="测试场景：玩家们在客厅相遇",
                participants=["张三", "李四"],
                max_tokens=100,
            )

            assert response is not None
            assert isinstance(response, list)
            assert len(response) > 0
            assert all("speaker" in d and "text" in d for d in response)
            print(f"✓ API响应成功: {response[0]['text'][:50]}...")
            
        except Exception as e:
            pytest.fail(f"API连接失败: {e}")
    
    @pytest.mark.asyncio
    async def test_rule_evaluation(self, client):
        """测试规则评估"""
        print("测试规则评估...")
        
        rule_data = {
            "name": "午夜照镜",
            "trigger": {
                "action": "look_mirror",
                "time": "00:00-04:00"
            },
            "effect": {
                "type": "instant_death",
                "fear_gain": 200
            }
        }
        
        try:
            evaluation = await client.evaluate_rule_async(
                rule_data,
                {"existing_rules": [], "map_size": 5}
            )
            
            assert isinstance(evaluation, dict)
            assert "cost" in evaluation
            assert "loopholes" in evaluation
            assert evaluation["cost"] > 0
            print(f"✓ 规则评估成功: 成本={evaluation['cost']}")
            
        except Exception as e:
            pytest.fail(f"规则评估失败: {e}")
    
    @pytest.mark.asyncio
    async def test_narrative_generation(self, client):
        """测试叙事生成"""
        print("测试叙事生成...")
        
        events = [
            "玩家A进入浴室",
            "玩家A在镜子前停留",
            "午夜钟声响起",
            "镜子中出现异常"
        ]
        
        try:
            narrative = await client.generate_narrative_async(
                events=events,
                context={"fear_level": 5, "time": "00:00"}
            )
            
            assert narrative is not None
            assert isinstance(narrative, str)
            assert len(narrative) > 50
            print(f"✓ 叙事生成成功: {narrative[:80]}...")
            
        except Exception as e:
            pytest.fail(f"叙事生成失败: {e}")
    
    @pytest.mark.asyncio
    async def test_sync_methods(self, mock_client):
        """测试同步方法（使用模拟）"""
        print("测试同步方法...")

        # 模拟API响应
        mock_response = {
            "choices": [{
                "message": {
                    "content": "测试NPC：这是一个测试响应"
                }
            }]
        }

        npc_states = [{
            "name": "测试NPC",
            "fear": 0,
            "sanity": 100,
            "status": "normal",
            "rationality": 5,
            "courage": 5,
        }]
        scene_context = {"location": "测试地点", "time": "白天"}

        with patch.object(mock_client, "_make_request", new=AsyncMock(return_value=mock_response)):
            dialogues = await mock_client.generate_dialogue(npc_states, scene_context)

            assert dialogues == [{"speaker": "测试NPC", "text": "这是一个测试响应"}]
            print("✓ 同步方法测试通过")
    
    @pytest.mark.asyncio
    async def test_batch_npc_generation(self, client):
        """测试批量NPC生成"""
        print("测试批量NPC生成...")
        
        try:
            names_and_backgrounds = await client.generate_npc_batch_async(
                count=3,
                personality_tags=["勇敢", "聪明", "谨慎"]
            )
            
            assert len(names_and_backgrounds) == 3
            for npc_data in names_and_backgrounds:
                assert "name" in npc_data
                assert "background" in npc_data
                assert isinstance(npc_data["name"], str)
                assert isinstance(npc_data["background"], str)
                print(f"✓ 生成NPC: {npc_data['name']}")
                
        except Exception as e:
            pytest.fail(f"批量NPC生成失败: {e}")


@pytest.mark.integration
class TestAPIIntegration:
    """API集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_game_cycle(self):
        """测试完整游戏周期"""
        # 创建客户端（没有API密钥会自动使用mock模式）
        client = DeepSeekClient()
        
        print("\n开始完整游戏周期测试...")
        
        # 1. 生成NPC
        print("1. 生成NPC...")
        npcs = await client.generate_npc_batch_async(2, ["神秘", "理性"])
        assert len(npcs) == 2
        print(f"   ✓ NPC生成: {[npc['name'] for npc in npcs]}")
        
        # 2. 生成开场对话
        print("2. 生成开场对话...")
        dialogue = await client.generate_dialogue_async(
            context="夜晚，两个陌生人被困在了一栋诡异的房子里",
            participants=[npc["name"] for npc in npcs],
            max_tokens=150,
        )
        assert isinstance(dialogue, list)
        assert len(dialogue) > 0
        print(f"   ✓ 对话生成: {dialogue[0]['text'][:80]}...")
        
        # 3. 评估规则
        print("3. 评估规则...")
        rule = {
            "name": "禁止回头",
            "trigger": {"action": "look_back"},
            "effect": {"type": "fear", "amount": 50}
        }
        evaluation = await client.evaluate_rule_async(rule, {})
        assert "cost" in evaluation
        print(f"   ✓ 规则评估: 成本={evaluation['cost']}")
        
        # 4. 生成事件叙事
        print("4. 生成事件叙事...")
        narrative = await client.generate_narrative_async(
            events=["NPC1听到身后传来脚步声", "NPC1忍不住回头看"],
            context={"fear_level": 3}
        )
        assert narrative is not None
        print(f"   ✓ 叙事生成: {narrative[:80]}...")
        
        print("\n✅ 完整游戏周期测试通过!")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
