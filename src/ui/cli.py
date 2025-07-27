"""
命令行界面
提供简单的文本交互界面
"""
import os
import sys
from typing import Optional, List, Dict, Any
from colorama import init, Fore, Back, Style
import asyncio

# 初始化colorama以支持跨平台颜色
init(autoreset=True)


class Colors:
    """颜色常量"""
    FEAR = Fore.RED
    SUCCESS = Fore.GREEN
    INFO = Fore.CYAN
    WARNING = Fore.YELLOW
    NPC = Fore.MAGENTA
    RULE = Fore.BLUE
    MENU = Fore.WHITE
    ERROR = Fore.RED + Style.BRIGHT


class CLI:
    """命令行界面"""
    
    def __init__(self):
        self.current_menu = "main"
        self.running = True
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "="*60)
        print(f"{Colors.MENU}{title.center(60)}")
        print("="*60 + "\n")
        
    def print_fear_points(self, points: int):
        """显示恐惧点数"""
        print(f"{Colors.FEAR}💀 恐惧点数: {points}")
        
    def print_turn_info(self, turn: int, time: str):
        """显示回合信息"""
        print(f"{Colors.INFO}📅 第 {turn} 回合 - {time}")
        
    def print_separator(self):
        """打印分隔线"""
        print("-" * 60)
        
    def print_menu(self, options: List[tuple]):
        """打印菜单选项
        options: [(key, description), ...]
        """
        print("\n" + Colors.MENU + "请选择操作:")
        for key, desc in options:
            print(f"  [{key}] {desc}")
        print(f"  [0] 返回/退出")
        
    def get_input(self, prompt: str = "> ") -> str:
        """获取用户输入"""
        try:
            return input(Colors.MENU + prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "0"
            
    def print_success(self, message: str):
        """打印成功消息"""
        print(f"{Colors.SUCCESS}✓ {message}")
        
    def print_error(self, message: str):
        """打印错误消息"""
        print(f"{Colors.ERROR}✗ {message}")
        
    def print_warning(self, message: str):
        """打印警告消息"""
        print(f"{Colors.WARNING}⚠ {message}")
        
    def print_info(self, message: str):
        """打印信息"""
        print(f"{Colors.INFO}ℹ {message}")
        
    def print_npc_status(self, npc: Dict[str, Any]):
        """打印NPC状态"""
        status_color = Colors.NPC
        if npc.get("hp", 0) <= 0:
            status_color = Colors.ERROR
        elif npc.get("fear", 0) > 70:
            status_color = Colors.WARNING
            
        print(f"{status_color}👤 {npc['name']} - HP:{npc.get('hp', 100)} "
              f"理智:{npc.get('sanity', 100)} 恐惧:{npc.get('fear', 0)} "
              f"位置:{npc.get('location', '未知')}")
        
    def print_rule(self, rule: Dict[str, Any]):
        """打印规则信息"""
        print(f"{Colors.RULE}📜 [{rule['name']}]")
        print(f"   触发条件: {rule.get('trigger', {}).get('action', '未知')}")
        print(f"   效果: {rule.get('effect', {}).get('type', '未知')}")
        print(f"   成本: {rule.get('base_cost', 0)} 点")
        
    def print_game_log(self, logs: List[str], limit: int = 10):
        """打印游戏日志"""
        print(f"\n{Colors.INFO}📋 最近事件:")
        for log in logs[-limit:]:
            print(f"   {log}")
            
    def confirm(self, message: str) -> bool:
        """确认操作"""
        response = self.get_input(f"{message} (y/n): ")
        return response.lower() in ['y', 'yes', '是', '确认']
        
    def select_from_list(self, items: List[Any], display_func=str) -> Optional[Any]:
        """从列表中选择项目"""
        if not items:
            self.print_warning("没有可选项目")
            return None
            
        print("\n请选择:")
        for i, item in enumerate(items, 1):
            print(f"  [{i}] {display_func(item)}")
            
        choice = self.get_input("选择编号: ")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(items):
                return items[index]
        except ValueError:
            pass
            
        self.print_error("无效的选择")
        return None
        
    def display_progress_bar(self, current: int, total: int, label: str = ""):
        """显示进度条"""
        bar_length = 20
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        percent = current / total * 100
        print(f"\r{label} [{bar}] {percent:.1f}%", end="", flush=True)
        if current >= total:
            print()  # 换行
            
    async def animated_text(self, text: str, delay: float = 0.03):
        """动画文字效果"""
        for char in text:
            print(char, end="", flush=True)
            await asyncio.sleep(delay)
        print()  # 换行
        
    def create_rule_wizard(self) -> Optional[Dict[str, Any]]:
        """规则创建向导"""
        self.print_header("创建新规则")
        
        # 规则名称
        name = self.get_input("规则名称: ")
        if not name:
            return None
            
        # 触发动作
        print("\n选择触发动作:")
        actions = [
            "look_mirror", "turn_around", "open_door", 
            "speak_word", "stay_alone", "touch_object"
        ]
        action = self.select_from_list(actions)
        if not action:
            return None
            
        # 触发地点
        print("\n选择触发地点 (可多选，用逗号分隔):")
        locations_input = self.get_input("地点: ")
        locations = [loc.strip() for loc in locations_input.split(",") if loc.strip()]
        
        # 效果类型
        print("\n选择效果类型:")
        effects = [
            ("instant_death", "即死"),
            ("fear_gain", "获得恐惧"),
            ("sanity_loss", "失去理智"),
            ("teleport", "传送"),
            ("spawn_spirit", "召唤灵体")
        ]
        effect_choice = self.select_from_list(effects, lambda x: f"{x[0]} - {x[1]}")
        if not effect_choice:
            return None
            
        # 构建规则数据
        rule_data = {
            "name": name,
            "trigger": {
                "action": action,
                "location": locations if locations else None,
                "probability": 0.8
            },
            "effect": {
                "type": effect_choice[0],
                "fear_gain": 50 if effect_choice[0] == "fear_gain" else 100
            },
            "base_cost": 100  # 基础成本
        }
        
        # 显示预览
        print("\n规则预览:")
        self.print_rule(rule_data)
        
        if self.confirm("\n确认创建这条规则吗？"):
            return rule_data
        return None
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
游戏指令说明:
  
主菜单:
  [1] 开始新游戏 - 创建新的游戏会话
  [2] 继续游戏 - 加载之前的存档
  [3] 帮助 - 显示此帮助信息
  
游戏中:
  [1] 创建规则 - 消耗恐惧点数创建新规则
  [2] 查看状态 - 查看所有NPC和规则状态
  [3] 推进回合 - 进入下一回合
  [4] 查看日志 - 查看最近发生的事件
  [5] 保存游戏 - 保存当前进度
  
规则系统:
  - 规则需要消耗恐惧点数创建
  - 规则被触发时会获得恐惧点数
  - 某些规则可能被NPC识破
  
游戏目标:
  - 通过规则获取尽可能多的恐惧点数
  - 避免所有NPC死亡导致游戏结束
  - 发现并利用各种规则组合
        """
        print(Colors.INFO + help_text)
        
    def show_credits(self):
        """显示制作信息"""
        self.clear_screen()
        self.print_header("制作团队")
        print(Colors.MENU + """
        游戏设计: 规则怪谈工作室
        程序开发: AI辅助开发
        美术资源: ASCII艺术
        音效音乐: 想象力
        
        特别感谢: 所有测试玩家
        
        版本: v0.1.0 (MVP)
        """.center(60))
        
        self.get_input("\n按回车返回...")


# 创建全局CLI实例
cli = CLI()


# 测试代码
if __name__ == "__main__":
    # 测试各种显示功能
    cli.print_header("测试界面")
    cli.print_fear_points(1000)
    cli.print_turn_info(1, "深夜")
    cli.print_separator()
    
    # 测试NPC显示
    test_npc = {
        "name": "测试员",
        "hp": 80,
        "sanity": 60,
        "fear": 30,
        "location": "走廊"
    }
    cli.print_npc_status(test_npc)
    
    # 测试规则显示
    test_rule = {
        "name": "测试规则",
        "trigger": {"action": "look_mirror"},
        "effect": {"type": "instant_death"},
        "base_cost": 150
    }
    cli.print_rule(test_rule)
    
    # 测试菜单
    cli.print_menu([
        ("1", "创建规则"),
        ("2", "查看状态"),
        ("3", "推进回合")
    ])
    
    # 测试规则创建向导
    # rule = cli.create_rule_wizard()
    # if rule:
    #     print(f"\n创建的规则: {rule}")
