#!/usr/bin/env python3
"""
规则怪谈游戏 - 快速启动脚本
使用这个脚本可以快速初始化项目结构并运行第一个demo
"""

import os
import sys
import json
from pathlib import Path


def create_project_structure():
    """创建项目目录结构"""
    print("🏗️  创建项目结构...")
    
    directories = [
        "src/core",
        "src/managers", 
        "src/models",
        "src/api",
        "src/utils",
        "data/schemas",
        "data/templates",
        "data/saves",
        "web/static/css",
        "web/static/js",
        "web/static/assets",
        "web/templates",
        "tests/unit",
        "tests/integration",
        "docs/api",
        "docs/game_design"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    # 创建__init__.py文件
    for dir_path in ["src", "src/core", "src/managers", "src/models", "src/api", "src/utils"]:
        init_file = Path(dir_path) / "__init__.py"
        init_file.touch(exist_ok=True)
        
    print("✅ 项目结构创建完成！")


def create_config_file():
    """创建基础配置文件"""
    print("⚙️  创建配置文件...")
    
    config = {
        "game": {
            "initial_fear_points": 1000,
            "max_npcs": 8,
            "max_rules": 20,
            "turn_duration": 300  # 秒
        },
        "api": {
            "deepseek_endpoint": "https://api.deepseek.com/v1/chat/completions",
            "max_retries": 3,
            "timeout": 30
        },
        "debug": {
            "enable_logging": True,
            "log_level": "INFO",
            "save_replay": True
        }
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    print("✅ 配置文件创建完成！")


def create_requirements_file():
    """创建依赖文件"""
    print("📦 创建依赖文件...")
    
    requirements = """# 核心依赖
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.23
alembic==1.13.0

# HTTP客户端
httpx==0.25.2
tenacity==8.2.3

# 工具库
python-dotenv==1.0.0
loguru==0.7.2
pytest==7.4.3
pytest-asyncio==0.21.1

# 前端相关
jinja2==3.1.2
python-socketio==5.10.0

# AI相关
tiktoken==0.5.2
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
        
    print("✅ requirements.txt 创建完成！")


def create_demo_game():
    """创建演示游戏脚本"""
    print("🎮 创建演示游戏...")
    
    demo_code = '''"""
规则怪谈游戏 - 最小可运行演示
这是一个简化版的游戏循环，展示核心机制
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List

# 导入我们的模型（假设已经创建）
try:
    from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
except ImportError:
    print("请先运行 quick_start.py 创建项目结构")
    exit(1)


class SimpleGameDemo:
    """简化版游戏演示"""
    
    def __init__(self):
        self.fear_points = 1000
        self.turn = 0
        self.npcs = []
        self.rules = []
        self.game_log = []
        
    def log(self, message: str):
        """记录游戏日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.game_log.append(log_entry)
        print(log_entry)
        
    async def create_demo_rule(self):
        """创建一个演示规则"""
        rule = Rule(
            id="demo_rule_001",
            name="禁止回头",
            description="在走廊里回头会看到不该看到的东西",
            trigger=TriggerCondition(
                action="turn_around",
                location=["corridor"],
                probability=0.7
            ),
            effect=RuleEffect(
                type=EffectType.FEAR_GAIN,
                fear_gain=50,
                side_effects=["see_shadow", "hear_whisper"]
            ),
            base_cost=100
        )
        
        cost = rule.calculate_total_cost()
        if self.fear_points >= cost:
            self.fear_points -= cost
            self.rules.append(rule)
            self.log(f"✨ 创建规则 [{rule.name}]，花费 {cost} 恐惧点数")
        else:
            self.log("❌ 恐惧点数不足！")
            
    def create_demo_npcs(self):
        """创建演示NPC"""
        npc_names = ["小明", "小红", "老王", "阿姨"]
        for name in npc_names:
            npc = {
                "name": name,
                "hp": 100,
                "sanity": random.randint(70, 100),
                "location": random.choice(["living_room", "corridor", "bedroom"]),
                "fear": 0
            }
            self.npcs.append(npc)
            self.log(f"👤 {name} 进入了游戏")
            
    async def simulate_turn(self):
        """模拟一个回合"""
        self.turn += 1
        self.log(f"\\n{'='*50}")
        self.log(f"🌙 第 {self.turn} 回合开始")
        self.log(f"💰 当前恐惧点数: {self.fear_points}")
        
        # 模拟NPC行动
        for npc in self.npcs:
            if npc["hp"] <= 0:
                continue
                
            # 随机行动
            actions = ["move", "investigate", "talk", "turn_around"]
            action = random.choice(actions)
            
            # 检查是否触发规则
            for rule in self.rules:
                if rule.active and action == rule.trigger.action:
                    if random.random() < rule.trigger.probability:
                        self.log(f"⚡ {npc['name']} 触发了规则 [{rule.name}]!")
                        
                        # 应用效果
                        if rule.effect.type == EffectType.FEAR_GAIN:
                            gained = rule.effect.fear_gain
                            self.fear_points += gained
                            npc["fear"] += 20
                            self.log(f"😱 获得 {gained} 恐惧点数！")
                            
                        # 副作用
                        for side_effect in rule.effect.side_effects:
                            self.log(f"   💀 {side_effect}")
                            
            # 更新NPC状态
            if npc["fear"] > 50:
                npc["sanity"] -= 10
                if npc["sanity"] <= 0:
                    self.log(f"🤯 {npc['name']} 精神崩溃了！")
                    npc["hp"] = 0
                    
    async def run_game(self, turns: int = 5):
        """运行游戏"""
        self.log("🎮 游戏开始！")
        self.log("📖 这是一个简化的规则怪谈游戏演示")
        
        # 初始化
        self.create_demo_npcs()
        await self.create_demo_rule()
        
        # 游戏循环
        for _ in range(turns):
            await self.simulate_turn()
            await asyncio.sleep(1)  # 模拟延迟
            
            # 检查游戏结束条件
            alive_npcs = [npc for npc in self.npcs if npc["hp"] > 0]
            if not alive_npcs:
                self.log("\\n💀 所有NPC都已经倒下，游戏结束！")
                break
                
        # 游戏总结
        self.log(f"\\n{'='*50}")
        self.log("📊 游戏总结")
        self.log(f"   总回合数: {self.turn}")
        self.log(f"   最终恐惧点数: {self.fear_points}")
        self.log(f"   存活NPC: {len([n for n in self.npcs if n['hp'] > 0])}/{len(self.npcs)}")
        

async def main():
    """主函数"""
    print("\\n" + "="*60)
    print("🎭 规则怪谈管理者 - 游戏演示")
    print("="*60 + "\\n")
    
    game = SimpleGameDemo()
    await game.run_game(turns=5)
    
    print("\\n演示结束！下一步：")
    print("1. 查看 src/models/rule.py 了解规则系统")
    print("2. 运行 pip install -r requirements.txt 安装依赖")
    print("3. 开始构建完整的游戏系统")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("demo_game.py", "w", encoding="utf-8") as f:
        f.write(demo_code)
        
    print("✅ 演示游戏创建完成！")


def create_readme():
    """创建项目README"""
    print("📝 创建README...")
    
    readme = """# 规则怪谈管理者 (Rule-based Horror Manager)

一个创新的恐怖游戏，玩家扮演规则制定者，通过创建诡异规则来收集恐惧点数。

## 🚀 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行演示**
   ```bash
   python demo_game.py
   ```

3. **启动开发服务器**
   ```bash
   uvicorn web.app:app --reload
   ```

## 📁 项目结构

```
RuleK/
├── src/              # 源代码
│   ├── core/         # 核心游戏逻辑
│   ├── managers/     # 管理器类
│   ├── models/       # 数据模型
│   └── api/          # API接口
├── data/             # 游戏数据
├── web/              # Web界面
└── tests/            # 测试用例
```

## 🎮 游戏特色

- **双重身份**：既是规则制定者，也可亲自下场
- **动态规则系统**：创建、升级、修补规则
- **AI驱动叙事**：使用DeepSeek生成沉浸式文本
- **策略深度**：平衡恐惧收益与规则成本

## 🛠️ 技术栈

- **后端**：Python + FastAPI
- **前端**：HTML/CSS/JavaScript + Vue.js
- **AI**：DeepSeek API
- **数据库**：SQLite (开发) / PostgreSQL (生产)

## 📖 文档

- [游戏设计文档](docs/game_design/)
- [API文档](docs/api/)
- [开发指南](docs/development/)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
"""
    
    # 保存到现有的readme.md旁边
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
        
    print("✅ README创建完成！")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          🎭 规则怪谈管理者 - 快速启动工具 🎭            ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查是否在正确的目录
    if not os.path.exists("readme.md"):
        print("⚠️  警告：未找到readme.md，请确保在项目根目录运行此脚本")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            return
    
    # 执行初始化步骤
    create_project_structure()
    create_config_file()
    create_requirements_file()
    create_demo_game()
    create_readme()
    
    print("\n🎉 项目初始化完成！")
    print("\n下一步：")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行演示: python demo_game.py")
    print("3. 查看生成的代码并开始开发")
    print("\n祝您开发愉快！👻")


if __name__ == "__main__":
    main()
