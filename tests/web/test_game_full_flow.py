"""
RuleK 完整游戏流程 Playwright 测试
测试用户完整的游戏体验，包括规则创建、回合推进、AI功能等
"""
import pytest
import asyncio
from playwright.async_api import async_playwright, Page, expect
import json
import time
from typing import Dict, Any, Optional

class TestRuleKFullFlow:
    """完整游戏流程测试"""
    
    base_url = "http://localhost:5173"
    api_url = "http://localhost:8000"
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """测试前后设置"""
        # 测试前
        print("\n🎮 开始RuleK游戏测试...")
        self.game_id = None
        self.test_results = []
        
        yield
        
        # 测试后
        print("\n📊 测试结果汇总:")
        for result in self.test_results:
            print(f"  {result}")
    
    async def test_01_homepage_navigation(self, page: Page):
        """测试1: 主页导航"""
        print("\n📍 测试主页导航...")
        
        # 访问主页
        await page.goto(self.base_url)
        await page.wait_for_load_state('networkidle')
        
        # 检查主页元素
        await expect(page).to_have_title("RuleK - 规则怪谈管理者")
        
        # 查找开始游戏按钮
        new_game_btn = page.locator('button:has-text("开始新游戏"), a:has-text("开始新游戏")')
        if await new_game_btn.count() > 0:
            await new_game_btn.first.click()
            await page.wait_for_url("**/new-game", timeout=5000)
            self.test_results.append("✅ 主页导航成功")
        else:
            # 可能直接在游戏配置页
            if "new-game" in page.url:
                self.test_results.append("✅ 已在游戏配置页")
            else:
                self.test_results.append("❌ 找不到开始游戏按钮")
    
    async def test_02_game_creation(self, page: Page):
        """测试2: 创建新游戏"""
        print("\n🎲 测试创建新游戏...")
        
        # 确保在新游戏页面
        if "new-game" not in page.url:
            await page.goto(f"{self.base_url}/new-game")
        
        await page.wait_for_load_state('networkidle')
        
        # 填写游戏配置
        # 设置初始恐惧点数
        fear_input = page.locator('input[type="number"]').filter(has_text="恐惧").or_(
            page.locator('input[placeholder*="恐惧"]')
        ).or_(
            page.locator('input').nth(0)  # 假设第一个输入框
        )
        
        if await fear_input.count() > 0:
            await fear_input.fill("1500")
        
        # 设置NPC数量
        npc_input = page.locator('input[type="number"]').filter(has_text="NPC").or_(
            page.locator('input[placeholder*="NPC"]')
        ).or_(
            page.locator('input').nth(1)  # 假设第二个输入框
        )
        
        if await npc_input.count() > 0:
            await npc_input.fill("4")
        
        # 选择难度
        difficulty_select = page.locator('select').filter(has_text="难度").or_(
            page.locator('button:has-text("normal")')
        )
        
        if await difficulty_select.count() > 0:
            await difficulty_select.select_option("normal")
        
        # 启用AI（如果有选项）
        ai_checkbox = page.locator('input[type="checkbox"]').filter(has_text="AI").or_(
            page.locator('label:has-text("启用AI")')
        )
        
        if await ai_checkbox.count() > 0:
            await ai_checkbox.check()
        
        # 点击创建游戏
        create_btn = page.locator('button:has-text("创建"), button:has-text("开始游戏"), button:has-text("确认")')
        
        if await create_btn.count() > 0:
            # 监听网络请求
            async with page.expect_response(lambda response: "/api/games" in response.url and response.status == 200) as response_info:
                await create_btn.first.click()
                response = await response_info.value
                data = await response.json()
                self.game_id = data.get("game_id")
                print(f"  📝 创建的游戏ID: {self.game_id}")
            
            # 等待跳转到游戏页面
            await page.wait_for_url(f"**/game/{self.game_id}", timeout=10000)
            self.test_results.append(f"✅ 游戏创建成功 (ID: {self.game_id})")
        else:
            self.test_results.append("❌ 找不到创建游戏按钮")
    
    async def test_03_game_dashboard(self, page: Page):
        """测试3: 游戏主界面"""
        print("\n📊 测试游戏主界面...")
        
        if not self.game_id:
            self.test_results.append("⚠️ 跳过: 没有游戏ID")
            return
        
        # 确保在游戏页面
        if f"game/{self.game_id}" not in page.url:
            await page.goto(f"{self.base_url}/game/{self.game_id}")
        
        await page.wait_for_load_state('networkidle')
        
        # 检查游戏状态显示
        checks = {
            "回合数": page.locator('text=/回合.*\\d+/'),
            "恐惧点数": page.locator('text=/恐惧.*\\d+/'),
            "NPC状态": page.locator('text=/NPC|角色|幸存者/'),
            "规则管理": page.locator('button:has-text("规则"), a:has-text("规则")')
        }
        
        for name, locator in checks.items():
            if await locator.count() > 0:
                self.test_results.append(f"✅ {name}显示正常")
            else:
                self.test_results.append(f"❌ {name}未找到")
    
    async def test_04_rule_creation(self, page: Page):
        """测试4: 规则创建功能"""
        print("\n📜 测试规则创建...")
        
        if not self.game_id:
            self.test_results.append("⚠️ 跳过: 没有游戏ID")
            return
        
        # 查找并点击规则管理按钮
        rule_btn = page.locator('button:has-text("规则"), button:has-text("管理规则"), button:has-text("创建规则")')
        
        if await rule_btn.count() > 0:
            await rule_btn.first.click()
            await page.wait_for_timeout(1000)
            
            # 检查规则创建选项
            creation_options = {
                "自定义规则": page.locator('button:has-text("自定义"), button:has-text("创建自定义")')                "模板规则": page.locator('button:has-text("模板"), button:has-text("使用模板")'),
                "AI规则": page.locator('button:has-text("AI"), button:has-text("智能创建")')
            }
            
            for option_name, locator in creation_options.items():
                if await locator.count() > 0:
                    self.test_results.append(f"✅ {option_name}选项存在")
                    
                    # 尝试点击测试
                    if option_name == "模板规则":
                        await locator.first.click()
                        await page.wait_for_timeout(1000)
                        
                        # 查找模板列表
                        templates = page.locator('.template-item, .rule-template, div[class*="template"]')
                        template_count = await templates.count()
                        
                        if template_count > 0:
                            self.test_results.append(f"✅ 找到{template_count}个规则模板")
                            
                            # 尝试创建第一个模板规则
                            await templates.first.click()
                            
                            # 确认创建
                            confirm_btn = page.locator('button:has-text("确认"), button:has-text("创建")')
                            if await confirm_btn.count() > 0:
                                await confirm_btn.first.click()
                                await page.wait_for_timeout(2000)
                                self.test_results.append("✅ 模板规则创建测试完成")
                        else:
                            self.test_results.append("❌ 没有找到规则模板")
                else:
                    self.test_results.append(f"❌ {option_name}选项不存在")
        else:
            self.test_results.append("❌ 找不到规则管理入口")
    
    async def test_05_ai_rule_creation(self, page: Page):
        """测试5: AI规则解析"""
        print("\n🤖 测试AI规则解析...")
        
        if not self.game_id:
            self.test_results.append("⚠️ 跳过: 没有游戏ID")
            return
        
        # 查找AI规则创建选项
        ai_rule_btn = page.locator('button:has-text("AI"), button:has-text("智能"), button:has-text("解析")')
        
        if await ai_rule_btn.count() > 0:
            await ai_rule_btn.first.click()
            await page.wait_for_timeout(1000)
            
            # 输入自然语言规则描述
            rule_input = page.locator('textarea, input[type="text"]').filter(has_text="描述").or_(
                page.locator('textarea').first
            )
            
            if await rule_input.count() > 0:
                test_rule = "如果有人在午夜12点照镜子，镜子里会出现另一个人的影子"
                await rule_input.fill(test_rule)
                
                # 点击解析
                parse_btn = page.locator('button:has-text("解析"), button:has-text("分析"), button:has-text("生成")')
                
                if await parse_btn.count() > 0:
                    # 等待AI响应
                    async with page.expect_response(
                        lambda response: "ai" in response.url.lower(),
                        timeout=30000
                    ) as response_info:
                        await parse_btn.first.click()
                        response = await response_info.value
                        
                        if response.status == 200:
                            self.test_results.append("✅ AI规则解析成功")
                        else:
                            self.test_results.append(f"❌ AI解析失败: {response.status}")
                else:
                    self.test_results.append("❌ 找不到解析按钮")
            else:
                self.test_results.append("❌ 找不到规则输入框")
        else:
            self.test_results.append("⚠️ AI规则功能未启用")
    
    async def test_06_turn_advancement(self, page: Page):
        """测试6: 回合推进"""
        print("\n⏭️ 测试回合推进...")
        
        if not self.game_id:
            self.test_results.append("⚠️ 跳过: 没有游戏ID")
            return
        
        # 返回游戏主界面
        if f"game/{self.game_id}" not in page.url:
            await page.goto(f"{self.base_url}/game/{self.game_id}")
        
        await page.wait_for_load_state('networkidle')
        
        # 查找开始回合按钮
        turn_btn = page.locator('button:has-text("开始回合"), button:has-text("下一回合"), button:has-text("推进")')
        
        if await turn_btn.count() > 0:
            # 记录当前回合数
            turn_text = await page.locator('text=/回合.*\\d+/').text_content() if await page.locator('text=/回合.*\\d+/').count() > 0 else ""
            
            # 点击推进回合
            await turn_btn.first.click()
            await page.wait_for_timeout(3000)
            
            # 检查是否有对话生成
            dialogue = page.locator('.dialogue, .npc-dialogue, div[class*="dialogue"]')
            if await dialogue.count() > 0:
                self.test_results.append("✅ NPC对话生成成功")
            
            # 检查是否有行动生成
            actions = page.locator('.action, .npc-action, div[class*="action"]')
            if await actions.count() > 0:
                self.test_results.append("✅ NPC行动生成成功")
            
            # 检查回合是否推进
            new_turn_text = await page.locator('text=/回合.*\\d+/').text_content() if await page.locator('text=/回合.*\\d+/').count() > 0 else ""
            if new_turn_text != turn_text:
                self.test_results.append("✅ 回合推进成功")
            else:
                self.test_results.append("⚠️ 回合数未变化")
        else:
            self.test_results.append("❌ 找不到回合推进按钮")
    
    async def test_07_save_game(self, page: Page):
        """测试7: 游戏保存"""
        print("\n💾 测试游戏保存...")
        
        if not self.game_id:
            self.test_results.append("⚠️ 跳过: 没有游戏ID")
            return
        
        # 查找保存按钮
        save_btn = page.locator('button:has-text("保存"), button:has-text("存档")')
        
        if await save_btn.count() > 0:
            await save_btn.first.click()
            await page.wait_for_timeout(1000)
            
            # 输入存档名称
            save_input = page.locator('input[type="text"]').filter(has_text="名称").or_(
                page.locator('input[placeholder*="存档"]')
            )
            
            if await save_input.count() > 0:
                save_name = f"test_save_{int(time.time())}"
                await save_input.fill(save_name)
                
                # 确认保存
                confirm_btn = page.locator('button:has-text("确认"), button:has-text("保存")')
                if await confirm_btn.count() > 0:
                    await confirm_btn.first.click()
                    await page.wait_for_timeout(2000)
                    
                    # 检查保存成功提示
                    success_msg = page.locator('text=/保存成功|已保存/')
                    if await success_msg.count() > 0:
                        self.test_results.append(f"✅ 游戏保存成功: {save_name}")
                    else:
                        self.test_results.append("⚠️ 保存状态未知")
            else:
                self.test_results.append("❌ 找不到存档名称输入框")
        else:
            self.test_results.append("❌ 找不到保存按钮")
    
    async def test_08_api_endpoints(self, page: Page):
        """测试8: API端点测试"""
        print("\n🔌 测试API端点...")
        
        # 测试健康检查
        health_response = await page.request.get(f"{self.api_url}/health")
        if health_response.status == 200:
            self.test_results.append("✅ API健康检查正常")
        else:
            self.test_results.append(f"❌ API健康检查失败: {health_response.status}")
        
        # 测试游戏列表
        if self.game_id:
            game_response = await page.request.get(f"{self.api_url}/api/games/{self.game_id}")
            if game_response.status == 200:
                game_data = await game_response.json()
                self.test_results.append(f"✅ 游戏状态API正常 (回合: {game_data.get('current_turn', 0)})")
            else:
                self.test_results.append(f"❌ 游戏状态API失败: {game_response.status}")

async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🎮 RuleK 完整游戏流程测试")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 设置为False以查看浏览器
        context = await browser.new_context()
        page = await context.new_page()
        
        test_suite = TestRuleKFullFlow()
        
        # 运行所有测试
        try:
            await test_suite.test_01_homepage_navigation(page)
            await test_suite.test_02_game_creation(page)
            await test_suite.test_03_game_dashboard(page)
            await test_suite.test_04_rule_creation(page)
            await test_suite.test_05_ai_rule_creation(page)
            await test_suite.test_06_turn_advancement(page)
            await test_suite.test_07_save_game(page)
            await test_suite.test_08_api_endpoints(page)
        except Exception as e:
            print(f"❌ 测试出错: {e}")
        finally:
            # 生成测试报告
            print("\n" + "=" * 60)
            print("📊 测试结果总结")
            print("=" * 60)
            
            success_count = len([r for r in test_suite.test_results if "✅" in r])
            fail_count = len([r for r in test_suite.test_results if "❌" in r])
            warn_count = len([r for r in test_suite.test_results if "⚠️" in r])
            
            print(f"✅ 成功: {success_count}")
            print(f"❌ 失败: {fail_count}")
            print(f"⚠️ 警告: {warn_count}")
            print("-" * 60)
            
            for result in test_suite.test_results:
                print(f"  {result}")
            
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
