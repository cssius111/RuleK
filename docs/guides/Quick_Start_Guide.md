# 立即开始：MCP驱动的游戏框架生成计划

## 第一步：生成核心游戏框架

### 1. 项目结构初始化脚本
```bash
# 使用MCP生成项目结构
mkdir -p src/{core,managers,models,api,utils}
mkdir -p data/{schemas,templates,saves}
mkdir -p web/{static/{css,js,assets},templates}
mkdir -p tests/{unit,integration}
mkdir -p docs/{api,game_design}
```

### 2. 核心数据模型 (使用MCP生成)

#### 2.1 Rule.py - 规则数据模型
```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class EffectType(Enum):
    INSTANT_DEATH = "instant_death"
    FEAR_GAIN = "fear_gain"
    SANITY_LOSS = "sanity_loss"
    TELEPORT = "teleport"
    TRANSFORM = "transform"

class Rule(BaseModel):
    id: str
    name: str
    level: int = 1
    cost: int
    description: str
    
    # 触发条件
    requirements: Dict = Field(default_factory=dict)
    trigger: Dict = Field(default_factory=dict)
    
    # 效果
    effect_type: EffectType
    effect_params: Dict = Field(default_factory=dict)
    
    # 破绽系统
    loopholes: List[Dict] = Field(default_factory=list)
    detectable: bool = True
    reverse_risk: float = 0.0
    
    # 状态
    active: bool = True
    cooldown: int = 0
```

#### 2.2 NPC.py - NPC模型
```python
class NPCPersonality(BaseModel):
    rationality: int = Field(ge=1, le=10)
    courage: int = Field(ge=1, le=10)
    curiosity: int = Field(ge=1, le=10)
    sociability: int = Field(ge=1, le=10)

class NPCStats(BaseModel):
    hp: int = 100
    sanity: int = 100
    stamina: int = 100
    fear: int = 0
    suspicion: int = 0

class NPC(BaseModel):
    id: str
    name: str
    background: str
    
    stats: NPCStats
    personality: NPCPersonality
    
    location: str
    inventory: List[str] = Field(default_factory=list)
    memories: List[Dict] = Field(default_factory=list)
    relationships: Dict[str, int] = Field(default_factory=dict)
```

### 3. 管理器类框架

#### 3.1 GameManager - 主游戏控制器
```python
class GameManager:
    def __init__(self):
        self.rule_manager = RuleManager()
        self.npc_manager = NPCManager()
        self.spirit_manager = SpiritManager()
        self.map_manager = MapManager()
        self.resource_system = ResourceSystem()
        self.turn_engine = TurnEngine()
        
    async def initialize_game(self, config: Dict):
        """初始化新游戏"""
        pass
        
    async def run_turn(self):
        """执行一个回合"""
        pass
        
    async def save_game(self, save_name: str):
        """保存游戏状态"""
        pass
```

### 4. DeepSeek API接口封装

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    async def generate_text(self, prompt: str, context: Dict) -> str:
        """调用DeepSeek生成文本"""
        pass
        
    async def evaluate_rule(self, rule_draft: Dict) -> Dict:
        """评估规则成本和破绽"""
        pass
        
    async def generate_dialogue(self, participants: List[Dict], 
                              event_context: Dict) -> List[str]:
        """生成NPC对话"""
        pass
```

### 5. 第一个可运行的Demo

```python
# demo.py - 最小可运行版本
async def minimal_game_loop():
    # 1. 初始化游戏
    game = GameManager()
    await game.initialize_game({
        "map_size": "small",
        "npc_count": 4,
        "starting_fear_points": 1000
    })
    
    # 2. 创建第一条规则
    rule = await game.rule_manager.create_rule({
        "name": "午夜镜子",
        "trigger": "look_mirror_at_midnight",
        "effect": "instant_death"
    })
    
    # 3. 运行3个回合
    for i in range(3):
        print(f"\n=== 回合 {i+1} ===")
        await game.run_turn()
        
    # 4. 显示结果
    game.show_summary()
```

### 6. MCP任务队列

以下是需要MCP依次生成的代码模块：

1. **基础设施** (Day 1)
   - [ ] models/base.py - 基础模型类
   - [ ] utils/validators.py - 数据验证器
   - [ ] utils/logger.py - 日志系统
   - [ ] config/settings.py - 配置管理

2. **核心系统** (Day 2-3)
   - [ ] managers/rule_manager.py
   - [ ] managers/npc_manager.py
   - [ ] core/turn_engine.py
   - [ ] core/event_system.py

3. **AI集成** (Day 4)
   - [ ] api/deepseek_client.py
   - [ ] api/prompt_templates.py
   - [ ] utils/text_processor.py

4. **游戏逻辑** (Day 5)
   - [ ] core/rule_executor.py
   - [ ] core/npc_ai.py
   - [ ] core/fear_calculator.py

5. **Web界面** (Day 6-7)
   - [ ] web/app.py - FastAPI主程序
   - [ ] web/websocket_handler.py
   - [ ] web/static/game.js

### 7. 测试用例模板

```python
# tests/test_rule_system.py
import pytest
from src.models.rule import Rule
from src.managers.rule_manager import RuleManager

class TestRuleSystem:
    @pytest.fixture
    def rule_manager(self):
        return RuleManager()
        
    def test_create_basic_rule(self, rule_manager):
        """测试创建基础规则"""
        rule_data = {
            "name": "测试规则",
            "trigger": "test_action",
            "effect_type": "fear_gain"
        }
        rule = rule_manager.create_rule(rule_data)
        assert rule.name == "测试规则"
        
    def test_rule_trigger_conditions(self, rule_manager):
        """测试规则触发条件"""
        pass
```

### 8. 快速启动指令

```bash
# 1. 安装依赖
pip install fastapi pydantic httpx tenacity pytest

# 2. 运行测试
pytest tests/

# 3. 启动开发服务器
uvicorn web.app:app --reload

# 4. 运行demo
python demo.py
```

---

## 今日必做清单

1. **[立即]** 创建项目目录结构
2. **[30分钟]** 使用MCP生成基础数据模型
3. **[1小时]** 实现GameManager框架
4. **[1小时]** 创建第一个可运行的demo
5. **[30分钟]** 编写第一个测试用例

## MCP Prompts 模板

### 生成数据模型
```
请根据以下Schema生成Pydantic模型类：
[插入JSON Schema]
要求：
1. 使用Python 3.10+ 类型注解
2. 添加数据验证
3. 包含必要的方法
4. 写明文档字符串
```

### 生成管理器类
```
请生成[XXX]Manager类，需要包含：
1. 初始化方法
2. CRUD操作
3. 业务逻辑方法
4. 错误处理
5. 日志记录
参考设计模式：单例模式/工厂模式
```

### 生成测试用例
```
为[模块名]生成pytest测试用例：
1. 覆盖所有public方法
2. 包含正常和异常情况
3. 使用fixture和mock
4. 测试覆盖率>80%
```

---

*开始执行！第一个可玩Demo目标：3天内完成*