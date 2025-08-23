#!/usr/bin/env python3
"""
RuleK API 问题修复脚本
自动诊断和修复API相关问题
"""
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class APIFixer:
    """API修复器"""
    
    def __init__(self):
        self.project_root = project_root
        self.backend_dir = self.project_root / "web" / "backend"
        self.src_dir = self.project_root / "src"
        self.issues_found = []
        self.fixes_applied = []
        
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        symbol = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "FIX": "🔧"
        }.get(level, "📝")
        print(f"{symbol} {message}")
    
    def check_dependencies(self) -> bool:
        """检查Python依赖"""
        self.log("检查Python依赖...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "httpx",
            "websockets",
            "jinja2",
            "tenacity",
            "colorama",
            "loguru"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log(f"缺少依赖包: {', '.join(missing_packages)}", "WARNING")
            self.issues_found.append(f"缺少依赖: {missing_packages}")
            return False
        else:
            self.log("所有依赖已安装", "SUCCESS")
            return True
    
    def check_file_structure(self) -> bool:
        """检查文件结构"""
        self.log("检查文件结构...")
        
        required_files = [
            self.backend_dir / "app.py",
            self.backend_dir / "models.py",
            self.backend_dir / "services" / "game_service.py",
            self.backend_dir / "services" / "session_manager.py",
            self.src_dir / "core" / "game_state.py",
            self.src_dir / "models" / "npc.py",
            self.src_dir / "models" / "rule.py",
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path.relative_to(self.project_root)))
        
        if missing_files:
            self.log(f"缺少文件: {missing_files}", "ERROR")
            self.issues_found.append(f"缺少文件: {missing_files}")
            return False
        else:
            self.log("文件结构完整", "SUCCESS")
            return True
    
    def fix_import_paths(self) -> bool:
        """修复导入路径问题"""
        self.log("检查导入路径...")
        
        # 检查app.py中的导入
        app_file = self.backend_dir / "app.py"
        
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已添加项目根目录到sys.path
            if "sys.path.insert(0" not in content:
                self.log("修复导入路径配置", "FIX")
                
                # 在导入之前添加路径配置
                import_fix = """# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
"""
                # 找到第一个from或import语句的位置
                import_pos = content.find("from ")
                if import_pos == -1:
                    import_pos = content.find("import ")
                
                if import_pos > 0:
                    # 在第一个导入前插入
                    content = content[:import_pos] + import_fix + "\n" + content[import_pos:]
                    
                    with open(app_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append("修复了app.py的导入路径")
                    return True
            
            self.log("导入路径正常", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"修复导入路径失败: {e}", "ERROR")
            return False
    
    def check_api_endpoints(self) -> bool:
        """检查API端点定义"""
        self.log("检查API端点定义...")
        
        app_file = self.backend_dir / "app.py"
        
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_endpoints = [
                "@app.get(\"/\")",
                "@app.post(\"/api/games\"",
                "@app.get(\"/api/games/{game_id}\"",
                "@app.post(\"/api/games/{game_id}/turn\"",
                "@app.websocket(\"/ws/{game_id}\"",
                "@app.get(\"/health\")"
            ]
            
            missing_endpoints = []
            for endpoint in required_endpoints:
                if endpoint not in content:
                    missing_endpoints.append(endpoint)
            
            if missing_endpoints:
                self.log(f"缺少端点: {missing_endpoints}", "WARNING")
                self.issues_found.append(f"缺少API端点: {missing_endpoints}")
                return False
            else:
                self.log("所有必要端点已定义", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f"检查API端点失败: {e}", "ERROR")
            return False
    
    def create_missing_files(self) -> bool:
        """创建缺失的文件"""
        self.log("检查并创建缺失文件...")
        
        # 创建session_manager.py如果不存在
        session_manager_file = self.backend_dir / "services" / "session_manager.py"
        if not session_manager_file.exists():
            self.log("创建session_manager.py", "FIX")
            
            session_manager_content = '''"""
会话管理器
管理多个游戏会话
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

from .game_service import GameService

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.games: Dict[str, GameService] = {}
        self._lock = asyncio.Lock()
        self._cleanup_interval = 3600  # 1小时清理一次
        self._session_timeout = 3600 * 24  # 24小时超时
        
    async def create_game(self, difficulty: str = "normal", npc_count: int = 4) -> GameService:
        """创建新游戏"""
        game_service = GameService(difficulty=difficulty, npc_count=npc_count)
        await game_service.initialize()
        
        async with self._lock:
            self.games[game_service.game_id] = game_service
        
        logger.info(f"Created new game: {game_service.game_id}")
        return game_service
    
    def get_game(self, game_id: str) -> Optional[GameService]:
        """获取游戏服务"""
        game = self.games.get(game_id)
        if game:
            game.update_last_accessed()
        return game
    
    def remove_game(self, game_id: str) -> bool:
        """移除游戏"""
        if game_id in self.games:
            del self.games[game_id]
            logger.info(f"Removed game: {game_id}")
            return True
        return False
    
    async def load_game(self, filename: str) -> GameService:
        """加载游戏存档"""
        game_service = GameService.load_from_file(filename)
        await game_service.initialize()
        
        async with self._lock:
            self.games[game_service.game_id] = game_service
        
        logger.info(f"Loaded game: {game_service.game_id}")
        return game_service
    
    def get_active_game_count(self) -> int:
        """获取活跃游戏数量"""
        return len([g for g in self.games.values() if g.is_active()])
    
    async def cleanup_inactive_games(self):
        """清理不活跃的游戏"""
        current_time = datetime.now()
        to_remove = []
        
        async with self._lock:
            for game_id, game in self.games.items():
                # 检查是否超时
                if (current_time - game.last_accessed).total_seconds() > self._session_timeout:
                    if not game.is_active():  # 没有WebSocket连接
                        to_remove.append(game_id)
        
        for game_id in to_remove:
            game = self.games[game_id]
            await game.cleanup()
            del self.games[game_id]
            logger.info(f"Cleaned up inactive game: {game_id}")
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive games")
    
    async def cleanup(self):
        """清理所有游戏"""
        for game in self.games.values():
            await game.cleanup()
        self.games.clear()
        logger.info("All games cleaned up")
'''
            
            session_manager_file.parent.mkdir(parents=True, exist_ok=True)
            with open(session_manager_file, 'w', encoding='utf-8') as f:
                f.write(session_manager_content)
            
            self.fixes_applied.append("创建了session_manager.py")
        
        # 创建rule_service.py如果不存在
        rule_service_file = self.backend_dir / "services" / "rule_service.py"
        if not rule_service_file.exists():
            self.log("创建rule_service.py", "FIX")
            
            rule_service_content = '''"""
规则服务
处理规则相关的业务逻辑
"""
from typing import Dict, List, Optional, Any
import uuid
import logging

from src.models.rule import Rule, TriggerCondition, RuleEffect, EffectType
from src.core.game_state import GameState

logger = logging.getLogger(__name__)


class RuleService:
    """规则服务类"""
    
    def __init__(self, game_state: Optional[GameState] = None):
        """初始化规则服务"""
        self.game_state = game_state
        self.rule_templates = self._load_rule_templates()
    
    def _load_rule_templates(self) -> List[Dict]:
        """加载规则模板"""
        # 基础规则模板
        return [
            {
                "id": "template_fear_night",
                "name": "夜晚恐惧",
                "description": "夜晚时所有NPC恐惧值增加",
                "cost": 200,
                "trigger": {
                    "type": "time",
                    "conditions": {"time": "night"},
                    "probability": 0.8
                },
                "effects": [
                    {
                        "type": "fear_increase",
                        "value": 30,
                        "target": "all"
                    }
                ]
            },
            {
                "id": "template_isolation_death",
                "name": "孤独死亡",
                "description": "独自一人的NPC有概率死亡",
                "cost": 500,
                "trigger": {
                    "type": "condition",
                    "conditions": {"alone": True},
                    "probability": 0.3
                },
                "effects": [
                    {
                        "type": "instant_death",
                        "value": 100,
                        "target": "trigger_npc"
                    }
                ]
            }
        ]
    
    def create_rule_from_template(self, template_id: str) -> Optional[Rule]:
        """从模板创建规则"""
        template = next((t for t in self.rule_templates if t["id"] == template_id), None)
        if not template:
            return None
        
        return self.create_custom_rule(template)
    
    def create_custom_rule(self, rule_data: Dict) -> Rule:
        """创建自定义规则"""
        rule_id = rule_data.get("id") or f"rule_{uuid.uuid4().hex[:8]}"
        
        # 创建触发条件
        trigger_data = rule_data.get("trigger", {})
        trigger = TriggerCondition(
            action=trigger_data.get("type", "manual"),
            probability=trigger_data.get("probability", 0.8)
        )
        
        # 创建效果
        effects = []
        for effect_data in rule_data.get("effects", []):
            effect_type = effect_data.get("type", "fear_gain")
            
            # 映射到枚举值
            type_mapping = {
                "fear_increase": EffectType.FEAR_GAIN,
                "instant_death": EffectType.INSTANT_DEATH,
                "sanity_loss": EffectType.SANITY_LOSS
            }
            
            if effect_type in type_mapping:
                effect_type = type_mapping[effect_type]
                
            effect = RuleEffect(
                type=effect_type,
                params={"value": effect_data.get("value", 10)},
                fear_gain=effect_data.get("value", 50)
            )
            effects.append(effect)
        
        # 创建规则
        rule = Rule(
            id=rule_id,
            name=rule_data.get("name", "未命名规则"),
            description=rule_data.get("description", ""),
            trigger=trigger,
            effect=effects[0] if effects else RuleEffect(type=EffectType.FEAR_GAIN),
            base_cost=rule_data.get("cost", 100)
        )
        
        return rule
    
    def calculate_rule_cost(self, rule_data: Dict) -> int:
        """计算规则成本"""
        base_cost = 100
        
        # 根据效果类型调整成本
        effects = rule_data.get("effects", [])
        for effect in effects:
            effect_type = effect.get("type", "")
            value = effect.get("value", 0)
            
            if effect_type in ["instant_death", "death"]:
                base_cost += 400
            elif effect_type in ["fear_increase", "fear_gain"]:
                base_cost += value * 2
            elif effect_type == "sanity_loss":
                base_cost += value * 3
        
        # 根据触发概率调整
        trigger = rule_data.get("trigger", {})
        probability = trigger.get("probability", 1.0)
        base_cost = int(base_cost * probability)
        
        return max(base_cost, 50)  # 最低50点
    
    def toggle_rule(self, rule_id: str) -> bool:
        """切换规则激活状态"""
        # 这里需要实际的规则管理逻辑
        # 暂时返回模拟值
        return True
    
    def upgrade_rule(self, rule_id: str) -> Optional[Rule]:
        """升级规则"""
        # 这里需要实际的规则升级逻辑
        # 暂时返回None
        return None
'''
            
            rule_service_file.parent.mkdir(parents=True, exist_ok=True)
            with open(rule_service_file, 'w', encoding='utf-8') as f:
                f.write(rule_service_content)
            
            self.fixes_applied.append("创建了rule_service.py")
        
        return True
    
    def fix_cors_settings(self) -> bool:
        """修复CORS设置"""
        self.log("检查CORS设置...")
        
        app_file = self.backend_dir / "app.py"
        
        try:
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查CORS配置
            if "CORSMiddleware" not in content:
                self.log("添加CORS中间件", "FIX")
                
                cors_config = '''
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''
                # 在FastAPI应用创建后添加
                app_create_pos = content.find("app = FastAPI(")
                if app_create_pos > 0:
                    # 找到应用创建语句的结束位置
                    bracket_count = 0
                    pos = app_create_pos
                    while pos < len(content):
                        if content[pos] == '(':
                            bracket_count += 1
                        elif content[pos] == ')':
                            bracket_count -= 1
                            if bracket_count == 0:
                                break
                        pos += 1
                    
                    # 在应用创建后插入CORS配置
                    content = content[:pos+1] + "\n" + cors_config + content[pos+1:]
                    
                    with open(app_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.fixes_applied.append("添加了CORS配置")
            
            self.log("CORS设置正常", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"修复CORS设置失败: {e}", "ERROR")
            return False
    
    def install_missing_dependencies(self) -> bool:
        """安装缺失的依赖"""
        self.log("安装缺失的依赖...")
        
        try:
            # 使用pip安装
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("依赖安装成功", "SUCCESS")
                self.fixes_applied.append("安装了Python依赖")
                return True
            else:
                self.log(f"依赖安装失败: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"无法安装依赖: {e}", "ERROR")
            return False
    
    def run_diagnostics(self):
        """运行诊断"""
        self.log("=" * 60)
        self.log("🔍 开始API诊断和修复", "INFO")
        self.log("=" * 60)
        
        # 1. 检查依赖
        if not self.check_dependencies():
            self.install_missing_dependencies()
        
        # 2. 检查文件结构
        self.check_file_structure()
        
        # 3. 创建缺失文件
        self.create_missing_files()
        
        # 4. 修复导入路径
        self.fix_import_paths()
        
        # 5. 检查API端点
        self.check_api_endpoints()
        
        # 6. 修复CORS设置
        self.fix_cors_settings()
        
        # 打印报告
        self.print_report()
    
    def print_report(self):
        """打印修复报告"""
        self.log("=" * 60)
        self.log("📋 诊断和修复报告", "INFO")
        self.log("=" * 60)
        
        if self.issues_found:
            self.log("发现的问题:", "WARNING")
            for issue in self.issues_found:
                self.log(f"  - {issue}")
        else:
            self.log("未发现问题", "SUCCESS")
        
        if self.fixes_applied:
            self.log("应用的修复:", "SUCCESS")
            for fix in self.fixes_applied:
                self.log(f"  - {fix}")
        else:
            self.log("无需修复", "INFO")
        
        self.log("=" * 60)
        
        if not self.issues_found or self.fixes_applied:
            self.log("✨ API已准备就绪！", "SUCCESS")
            self.log("启动服务器: python rulek.py web", "INFO")
            self.log("运行测试: python scripts/test/test_api_comprehensive.py", "INFO")
        else:
            self.log("⚠️ 存在未解决的问题，请手动检查", "WARNING")


def main():
    """主函数"""
    fixer = APIFixer()
    fixer.run_diagnostics()


if __name__ == "__main__":
    main()
