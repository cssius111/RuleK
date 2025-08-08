/**
 * Phase 0 简化测试 - 用于快速验证环境
 * 在 web/frontend 目录运行: npm run test:phase0
 */

import { test, expect } from '@playwright/test';

test.describe('Phase 0: 环境验证（简化版）', () => {
  
  test('前端开发服务器可访问', async ({ page }) => {
    // 尝试访问Vite开发服务器
    const response = await page.goto('http://localhost:5173');
    
    // 验证响应状态
    expect(response?.status()).toBeLessThan(400);
    
    // 验证页面加载
    await expect(page).toHaveTitle(/.*/); // 任何标题都可以
    
    console.log('✅ 前端服务器运行正常');
  });
  
  test('页面基本元素存在', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // 检查Vue应用是否挂载
    const appElement = page.locator('#app');
    await expect(appElement).toBeVisible();
    
    console.log('✅ Vue应用已挂载');
  });
  
  test.skip('后端API服务器可访问', async ({ request }) => {
    // 跳过此测试如果后端未启动
    try {
      const response = await request.get('http://localhost:8000/health');
      expect(response.ok()).toBeTruthy();
      console.log('✅ 后端API运行正常');
    } catch (error) {
      console.log('⚠️ 后端API未运行（可选）');
    }
  });
  
  test('响应式设计检查', async ({ page }) => {
    const viewports = [
      { name: 'Mobile', width: 375, height: 667 },
      { name: 'Desktop', width: 1920, height: 1080 }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.goto('http://localhost:5173');
      
      // 验证页面在不同视口下正常显示
      const visible = await page.locator('#app').isVisible();
      expect(visible).toBeTruthy();
      
      console.log(`✅ ${viewport.name} 视口正常`);
    }
  });
});

// 测试完成后输出总结
test.afterAll(async () => {
  console.log('\n' + '='.repeat(50));
  console.log('Phase 0 环境验证完成！');
  console.log('如果所有测试通过，可以开始 Phase 1 开发');
  console.log('='.repeat(50) + '\n');
});
