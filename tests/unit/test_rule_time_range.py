"""
测试规则时间范围检查功能
"""
import pytest
from datetime import datetime
from src.core.rule_executor import RuleExecutor
from src.core.game_state import GameStateManager


class TestRuleTimeRange:
    """测试规则时间范围检查"""
    
    @pytest.fixture
    def executor(self):
        """创建规则执行器实例"""
        game_manager = GameStateManager()
        return RuleExecutor(game_manager)
    
    def test_normal_time_range(self, executor):
        """测试正常时间范围（不跨午夜）"""
        # 测试在范围内
        assert executor._check_time_range("10:30", {"from": "09:00", "to": "12:00"}) == True
        assert executor._check_time_range("09:00", {"from": "09:00", "to": "12:00"}) == True
        assert executor._check_time_range("12:00", {"from": "09:00", "to": "12:00"}) == True
        
        # 测试在范围外
        assert executor._check_time_range("08:59", {"from": "09:00", "to": "12:00"}) == False
        assert executor._check_time_range("12:01", {"from": "09:00", "to": "12:00"}) == False
        assert executor._check_time_range("15:00", {"from": "09:00", "to": "12:00"}) == False
    
    def test_midnight_crossing_range(self, executor):
        """测试跨午夜的时间范围"""
        # 测试午夜前的时间（在范围内）
        assert executor._check_time_range("23:30", {"from": "23:00", "to": "02:00"}) == True
        assert executor._check_time_range("23:00", {"from": "23:00", "to": "02:00"}) == True
        
        # 测试午夜后的时间（在范围内）
        assert executor._check_time_range("00:30", {"from": "23:00", "to": "02:00"}) == True
        assert executor._check_time_range("01:59", {"from": "23:00", "to": "02:00"}) == True
        assert executor._check_time_range("02:00", {"from": "23:00", "to": "02:00"}) == True
        
        # 测试在范围外的时间
        assert executor._check_time_range("22:59", {"from": "23:00", "to": "02:00"}) == False
        assert executor._check_time_range("02:01", {"from": "23:00", "to": "02:00"}) == False
        assert executor._check_time_range("10:00", {"from": "23:00", "to": "02:00"}) == False
    
    def test_edge_cases(self, executor):
        """测试边界情况"""
        # 测试单点时间
        assert executor._check_time_range("00:00", {"from": "00:00", "to": "00:00"}) == True
        assert executor._check_time_range("00:01", {"from": "00:00", "to": "00:00"}) == False
        
        # 测试全天时间
        assert executor._check_time_range("12:00", {"from": "00:00", "to": "23:59"}) == True
        assert executor._check_time_range("00:00", {"from": "00:00", "to": "23:59"}) == True
        assert executor._check_time_range("23:59", {"from": "00:00", "to": "23:59"}) == True
    
    def test_invalid_time_format(self, executor):
        """测试无效的时间格式"""
        # 测试格式错误
        assert executor._check_time_range("25:00", {"from": "09:00", "to": "12:00"}) == False
        assert executor._check_time_range("10:60", {"from": "09:00", "to": "12:00"}) == False
        assert executor._check_time_range("10:30", {"from": "9:00", "to": "12:00"}) == False  # 缺少前导零
        assert executor._check_time_range("10:30", {"from": "09:00", "to": "12"}) == False  # 格式不完整
        
        # 测试空值
        assert executor._check_time_range("", {"from": "09:00", "to": "12:00"}) == False
        assert executor._check_time_range("10:30", {"from": "", "to": "12:00"}) == False
    
    def test_real_game_scenarios(self, executor):
        """测试实际游戏场景"""
        # 午夜照镜规则（00:00-04:00）
        midnight_range = {"from": "00:00", "to": "04:00"}
        assert executor._check_time_range("00:00", midnight_range) == True
        assert executor._check_time_range("02:30", midnight_range) == True
        assert executor._check_time_range("04:00", midnight_range) == True
        assert executor._check_time_range("04:01", midnight_range) == False
        assert executor._check_time_range("23:59", midnight_range) == False
        
        # 深夜敲门规则（22:00-06:00）
        night_range = {"from": "22:00", "to": "06:00"}
        assert executor._check_time_range("22:00", night_range) == True
        assert executor._check_time_range("23:30", night_range) == True
        assert executor._check_time_range("00:00", night_range) == True
        assert executor._check_time_range("03:00", night_range) == True
        assert executor._check_time_range("06:00", night_range) == True
        assert executor._check_time_range("06:01", night_range) == False
        assert executor._check_time_range("21:59", night_range) == False
        assert executor._check_time_range("12:00", night_range) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
