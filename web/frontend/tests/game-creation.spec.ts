/**
 * 游戏创建流程测试 - 检查从首页到游戏开始的完整流程
 */

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000';

// 辅助函数：等待并截图
async function waitAndScreenshot(page: Page, name: string, waitTime = 1000) {
  await page.waitForTimeout(waitTime);
  await page.screenshot({ path: `test-results/${name}.png`, fullPage: true });
}

test.describe('游戏创建完整流程测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 设置更长的超时时间
    test.setTimeout(60000);
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('浏览器错误:', msg.text());
      }
    });
    
    // 监听页面崩溃
    page.on('pageerror', error => {
      console.error('页面错误:', error.message);
    });
  });

  test('1. 首页正常加载', async ({ page }) => {
    console.log('🔍 测试首页加载...');
    
    await page.goto(BASE_URL);
    await waitAndScreenshot(page, '1-homepage');
    
    // 检查Vue应用是否挂载
    const appElement = page.locator('#app');
    await expect(appElement).toBeVisible();
    
    // 检查是否有导航菜单或开始按钮
    const startButton = page.locator('text=/开始|新游戏|start/i').first();
    const hasStartButton = await startButton.isVisible().catch(() => false);
    
    if (hasStartButton) {
      console.log('✅ 首页加载成功，找到开始按钮');
    } else {
      console.log('⚠️ 首页加载但未找到开始按钮');
      
      // 尝试查找任何链接到新游戏的元素
      const newGameLink = page.locator('a[href*="new"]').first();
      const hasNewGameLink = await newGameLink.isVisible().catch(() => false);
      
      if (hasNewGameLink) {
        console.log('✅ 找到新游戏链接');
      }
    }
  });

  test('2. 导航到新游戏页面', async ({ page }) => {
    console.log('🔍 测试导航到新游戏页面...');
    
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    // 方法1：直接访问新游戏页面
    await page.goto(`${BASE_URL}/new-game`);
    await waitAndScreenshot(page, '2-new-game-page');
    
    // 检查页面是否加载
    const pageTitle = await page.locator('h1').first().textContent().catch(() => '');
    console.log('页面标题:', pageTitle);
    
    // 检查是否有表单元素
    const formElements = await page.locator('form').count();
    const inputElements = await page.locator('input').count();
    
    console.log(`找到 ${formElements} 个表单, ${inputElements} 个输入框`);
    
    if (formElements > 0 || inputElements > 0) {
      console.log('✅ 新游戏页面加载成功');
    } else {
      console.log('❌ 新游戏页面可能未正确加载');
    }
  });

  test('3. 填写游戏配置表单', async ({ page }) => {
    console.log('🔍 测试游戏配置表单...');
    
    await page.goto(`${BASE_URL}/new-game`);
    await page.waitForLoadState('networkidle');
    
    // 等待表单加载
    await page.waitForTimeout(2000);
    await waitAndScreenshot(page, '3-1-form-initial');
    
    // 尝试填写玩家名称
    const playerNameInput = page.locator('input[type="text"]').first();
    const hasPlayerName = await playerNameInput.isVisible().catch(() => false);
    
    if (hasPlayerName) {
      await playerNameInput.fill('测试玩家');
      console.log('✅ 填写玩家名称');
    }
    
    // 选择难度（点击难度按钮）
    const difficultyButtons = page.locator('button').filter({ hasText: /恐惧|normal|难度/i });
    const difficultyCount = await difficultyButtons.count();
    
    if (difficultyCount > 0) {
      await difficultyButtons.first().click();
      console.log('✅ 选择难度');
    }
    
    // 设置NPC数量（如果有滑块）
    const slider = page.locator('input[type="range"]').first();
    const hasSlider = await slider.isVisible().catch(() => false);
    
    if (hasSlider) {
      await slider.fill('4');
      console.log('✅ 设置NPC数量');
    }
    
    // 设置恐惧点数
    const fearPointsInput = page.locator('input[type="number"]').first();
    const hasFearPoints = await fearPointsInput.isVisible().catch(() => false);
    
    if (hasFearPoints) {
      await fearPointsInput.fill('1000');
      console.log('✅ 设置恐惧点数');
    }
    
    await waitAndScreenshot(page, '3-2-form-filled');
  });

  test('4. 创建游戏并检查错误', async ({ page }) => {
    console.log('🔍 测试游戏创建...');
    
    await page.goto(`${BASE_URL}/new-game`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // 填写必要的表单字段
    const playerNameInput = page.locator('input[type="text"]').first();
    if (await playerNameInput.isVisible().catch(() => false)) {
      await playerNameInput.fill('测试玩家');
    }
    
    // 查找并点击创建游戏按钮
    const createButtons = page.locator('button').filter({ hasText: /开启|创建|开始|start|召唤/i });
    const submitButton = page.locator('button[type="submit"]').first();
    
    let buttonClicked = false;
    
    // 尝试点击提交按钮
    if (await submitButton.isVisible().catch(() => false)) {
      console.log('点击提交按钮...');
      await submitButton.click();
      buttonClicked = true;
    } else if (await createButtons.count() > 0) {
      console.log('点击创建游戏按钮...');
      await createButtons.last().click();
      buttonClicked = true;
    }
    
    if (!buttonClicked) {
      console.log('❌ 未找到创建游戏按钮');
      await waitAndScreenshot(page, '4-no-button');
      return;
    }
    
    // 等待响应
    await page.waitForTimeout(3000);
    await waitAndScreenshot(page, '4-after-click');
    
    // 检查是否有错误消息
    const errorMessages = await page.locator('text=/error|错误|失败|failed/i').allTextContents();
    if (errorMessages.length > 0) {
      console.log('❌ 发现错误消息:', errorMessages);
    }
    
    // 检查是否成功跳转到游戏页面
    const currentUrl = page.url();
    if (currentUrl.includes('/game')) {
      console.log('✅ 成功跳转到游戏页面');
    } else {
      console.log('⚠️ 未跳转，当前URL:', currentUrl);
      
      // 检查是否有加载指示器
      const loadingIndicator = page.locator('text=/加载|loading/i').first();
      if (await loadingIndicator.isVisible().catch(() => false)) {
        console.log('⏳ 检测到加载状态');
        await page.waitForTimeout(5000);
        await waitAndScreenshot(page, '4-loading');
      }
    }
  });

  test('5. 检查API连接', async ({ page, request }) => {
    console.log('🔍 测试API连接...');
    
    // 检查后端健康状态
    try {
      const healthResponse = await request.get(`${API_URL}/health`);
      if (healthResponse.ok()) {
        console.log('✅ 后端API健康检查通过');
      } else {
        console.log('❌ 后端API健康检查失败:', healthResponse.status());
      }
    } catch (error) {
      console.log('❌ 无法连接到后端API:', error);
    }
    
    // 检查前端是否正确配置API地址
    await page.goto(`${BASE_URL}/new-game`);
    
    // 注入脚本检查环境变量
    const apiConfig = await page.evaluate(() => {
      // @ts-ignore
      return {
        apiUrl: import.meta.env.VITE_API_BASE_URL,
        useMock: import.meta.env.VITE_USE_MOCK_DATA,
        useRealApi: import.meta.env.VITE_USE_REAL_API
      };
    });
    
    console.log('前端API配置:', apiConfig);
    
    if (!apiConfig.apiUrl) {
      console.log('❌ 前端未配置API地址');
    } else if (apiConfig.apiUrl !== API_URL) {
      console.log(`⚠️ API地址不匹配: 期望 ${API_URL}, 实际 ${apiConfig.apiUrl}`);
    } else {
      console.log('✅ API地址配置正确');
    }
  });

  test('6. 调试：检查控制台错误和网络请求', async ({ page }) => {
    console.log('🔍 深度调试...');
    
    // 收集控制台日志
    const consoleLogs: string[] = [];
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      } else {
        consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
      }
    });
    
    // 监听网络请求
    const networkRequests: string[] = [];
    page.on('request', request => {
      if (request.url().includes('api') || request.url().includes('8000')) {
        networkRequests.push(`${request.method()} ${request.url()}`);
      }
    });
    
    page.on('response', response => {
      if (response.url().includes('api') || response.url().includes('8000')) {
        console.log(`响应: ${response.status()} ${response.url()}`);
      }
    });
    
    // 访问新游戏页面并尝试创建游戏
    await page.goto(`${BASE_URL}/new-game`);
    await page.waitForTimeout(2000);
    
    // 尝试创建游戏
    const submitButton = page.locator('button[type="submit"]').first();
    if (await submitButton.isVisible().catch(() => false)) {
      await submitButton.click();
      await page.waitForTimeout(3000);
    }
    
    // 输出收集的信息
    console.log('\n=== 控制台错误 ===');
    consoleErrors.forEach(err => console.log('❌', err));
    
    console.log('\n=== 网络请求 ===');
    networkRequests.forEach(req => console.log('📡', req));
    
    console.log('\n=== 控制台日志 ===');
    consoleLogs.slice(-10).forEach(log => console.log(log));
    
    // 检查Store
    const storeInfo = await page.evaluate(() => {
      try {
        // @ts-ignore
        const store = window.__PINIA__;
        if (!store) return 'Pinia未初始化';
        
        const storeNames = Object.keys(store.state.value);
        return `Stores: ${storeNames.join(', ')}`;
      } catch (error) {
        return `Store检查失败: ${error}`;
      }
    });
    
    console.log('\n=== Store状态 ===');
    console.log(storeInfo);
  });
});

// 测试完成后输出总结
test.afterAll(async () => {
  console.log('\n' + '='.repeat(60));
  console.log('🎮 游戏创建流程测试完成！');
  console.log('请检查 test-results 目录中的截图');
  console.log('='.repeat(60) + '\n');
});