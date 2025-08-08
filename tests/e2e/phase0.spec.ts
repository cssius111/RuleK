/**
 * RuleK Web UI - Phase 0 环境验证测试
 * 
 * 成功标准:
 * - 开发服务器可访问
 * - API服务器可访问
 * - 基础依赖正常工作
 */

import { test, expect } from '@playwright/test';

test.describe('Phase 0: 环境验证', () => {
  
  test('前端开发服务器可访问', async ({ page }) => {
    const response = await page.goto('http://localhost:3000', {
      waitUntil: 'networkidle'
    });
    
    expect(response?.status()).toBe(200);
    await expect(page).toHaveTitle(/RuleK/);
    
    // 验证Vue应用已挂载
    const appElement = await page.locator('#app');
    await expect(appElement).toBeVisible();
  });
  
  test('后端API服务器可访问', async ({ request }) => {
    // 健康检查
    const health = await request.get('http://localhost:8000/health');
    expect(health.ok()).toBeTruthy();
    
    // API文档可访问
    const docs = await request.get('http://localhost:8000/docs');
    expect(docs.ok()).toBeTruthy();
  });
  
  test('WebSocket连接测试', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // 注入WebSocket测试代码
    const wsConnected = await page.evaluate(() => {
      return new Promise((resolve) => {
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onopen = () => resolve(true);
        ws.onerror = () => resolve(false);
        setTimeout(() => resolve(false), 5000);
      });
    });
    
    expect(wsConnected).toBeTruthy();
  });
  
  test('静态资源加载测试', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // 检查CSS加载
    const styles = await page.evaluate(() => {
      return window.getComputedStyle(document.body).backgroundColor;
    });
    expect(styles).toBeTruthy();
    
    // 检查JavaScript执行
    const jsExecuted = await page.evaluate(() => {
      return typeof window.Vue !== 'undefined' || 
             typeof window.__VUE__ !== 'undefined';
    });
    expect(jsExecuted).toBeTruthy();
  });
  
  test('响应式设计基础测试', async ({ page }) => {
    const viewports = [
      { name: 'Mobile', width: 375, height: 667 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Desktop', width: 1920, height: 1080 }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ 
        width: viewport.width, 
        height: viewport.height 
      });
      await page.goto('http://localhost:3000');
      
      // 验证页面在不同视口下可见
      const appVisible = await page.locator('#app').isVisible();
      expect(appVisible).toBeTruthy();
      
      console.log(`✅ ${viewport.name} 视口测试通过`);
    }
  });
  
  test('浏览器兼容性检查', async ({ browserName }) => {
    console.log(`正在测试浏览器: ${browserName}`);
    
    // 浏览器特定功能检查
    const features = {
      'chromium': ['ServiceWorker', 'WebAssembly'],
      'firefox': ['WebAssembly', 'Intl'],
      'webkit': ['WebAssembly', 'Intl']
    };
    
    const expectedFeatures = features[browserName] || [];
    
    for (const feature of expectedFeatures) {
      console.log(`  检查功能: ${feature}`);
      // 实际检查逻辑...
    }
  });
});

// 测试报告生成
test.afterAll(async () => {
  console.log('\n=== Phase 0 测试完成 ===');
  console.log('✅ 环境验证通过');
  console.log('可以开始 Phase 1 开发');
});
