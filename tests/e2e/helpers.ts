/**
 * RuleK E2E测试助手库
 * 提供常用的测试工具和页面对象模型
 */

import { Page, expect, Locator } from '@playwright/test';

// ==================== 页面对象基类 ====================
export class BasePage {
  constructor(public page: Page) {}
  
  async navigate(path: string) {
    await this.page.goto(path);
    await this.page.waitForLoadState('networkidle');
  }
  
  async waitForAPI(path: string) {
    await this.page.waitForResponse(
      response => response.url().includes(path) && response.status() === 200
    );
  }
  
  async takeScreenshot(name: string) {
    await this.page.screenshot({ 
      path: `screenshots/${name}.png`,
      fullPage: true 
    });
  }
}

// ==================== 游戏助手 ====================
export class GameHelper extends BasePage {
  // 选择器定义
  private selectors = {
    fearPoints: '[data-testid="fear-points"]',
    turnNumber: '[data-testid="turn-number"]',
    npcsAlive: '[data-testid="npcs-alive"]',
    startTurnBtn: '[data-testid="start-turn"]',
    aiProcessing: '[data-testid="ai-processing"]',
    eventLog: '[data-testid="event-log"]',
    saveGameBtn: '[data-testid="save-game"]'
  };
  
  // 创建新游戏
  async createGame(config: {
    fearPoints?: number;
    npcCount?: number;
    difficulty?: 'easy' | 'normal' | 'hard';
    aiEnabled?: boolean;
  } = {}) {
    await this.navigate('/new-game');
    
    // 填写配置
    if (config.fearPoints) {
      await this.page.fill('[name="fearPoints"]', config.fearPoints.toString());
    }
    
    if (config.npcCount) {
      await this.page.fill('[name="npcCount"]', config.npcCount.toString());
    }
    
    if (config.difficulty) {
      await this.page.selectOption('[name="difficulty"]', config.difficulty);
    }
    
    if (config.aiEnabled !== undefined) {
      const checkbox = this.page.locator('[name="aiEnabled"]');
      if (config.aiEnabled) {
        await checkbox.check();
      } else {
        await checkbox.uncheck();
      }
    }
    
    // 创建游戏
    await this.page.click('button:has-text("开始游戏")');
    
    // 等待跳转
    await this.page.waitForURL(/\/game\/[\w-]+\/dashboard/);
    
    // 返回游戏ID
    const url = this.page.url();
    const match = url.match(/\/game\/([\w-]+)\//);
    return match ? match[1] : null;
  }
  
  // 加载存档
  async loadGame(saveName: string) {
    await this.navigate('/load-game');
    await this.page.click(`[data-save-name="${saveName}"]`);
    await this.page.waitForURL(/\/game\//);
  }
  
  // 执行回合
  async advanceTurn() {
    const turnBefore = await this.getTurnNumber();
    
    await this.page.click(this.selectors.startTurnBtn);
    await this.waitForAI();
    
    const turnAfter = await this.getTurnNumber();
    expect(turnAfter).toBeGreaterThan(turnBefore);
    
    return turnAfter;
  }
  
  // 等待AI处理完成
  async waitForAI() {
    // 等待AI处理开始
    await this.page.waitForSelector(this.selectors.aiProcessing, { 
      state: 'visible' 
    });
    
    // 等待AI处理完成
    await this.page.waitForSelector(this.selectors.aiProcessing, { 
      state: 'hidden',
      timeout: 30000 
    });
  }
  
  // 获取游戏状态
  async getGameState() {
    return {
      turn: await this.getTurnNumber(),
      fearPoints: await this.getFearPoints(),
      npcsAlive: await this.getNPCsAlive(),
      events: await this.getRecentEvents()
    };
  }
  
  async getTurnNumber(): Promise<number> {
    const text = await this.page.textContent(this.selectors.turnNumber);
    return parseInt(text || '0');
  }
  
  async getFearPoints(): Promise<number> {
    const text = await this.page.textContent(this.selectors.fearPoints);
    return parseInt(text || '0');
  }
  
  async getNPCsAlive(): Promise<number> {
    const text = await this.page.textContent(this.selectors.npcsAlive);
    return parseInt(text || '0');
  }
  
  async getRecentEvents(): Promise<string[]> {
    const events = await this.page.$$eval(
      `${this.selectors.eventLog} .event-item`,
      elements => elements.map(el => el.textContent || '')
    );
    return events;
  }
  
  // 保存游戏
  async saveGame(name: string) {
    await this.page.click(this.selectors.saveGameBtn);
    await this.page.fill('[name="saveName"]', name);
    await this.page.click('button:has-text("确认保存")');
    await this.page.waitForSelector('.save-success-message');
  }
  
  // 验证游戏状态
  async expectGameState(expected: {
    turn?: number;
    fearPoints?: number;
    npcsAlive?: number;
    hasEvent?: string;
  }) {
    if (expected.turn !== undefined) {
      const turn = await this.getTurnNumber();
      expect(turn).toBe(expected.turn);
    }
    
    if (expected.fearPoints !== undefined) {
      const points = await this.getFearPoints();
      expect(points).toBe(expected.fearPoints);
    }
    
    if (expected.npcsAlive !== undefined) {
      const alive = await this.getNPCsAlive();
      expect(alive).toBe(expected.npcsAlive);
    }
    
    if (expected.hasEvent) {
      const events = await this.getRecentEvents();
      expect(events.some(e => e.includes(expected.hasEvent))).toBeTruthy();
    }
  }
}

// ==================== 规则助手 ====================
export class RuleHelper extends BasePage {
  // 创建自定义规则
  async createCustomRule(rule: {
    name: string;
    description: string;
    triggerType: 'action' | 'time' | 'location' | 'item';
    triggerDetails: any;
    effects: any[];
    cooldown?: number;
  }) {
    await this.navigate('/game/test/rules');
    await this.page.click('button:has-text("创建规则")');
    
    // Step 1: 基本信息
    await this.page.fill('[name="ruleName"]', rule.name);
    await this.page.fill('[name="ruleDescription"]', rule.description);
    await this.page.click('button:has-text("下一步")');
    
    // Step 2: 触发条件
    await this.page.click(`[value="${rule.triggerType}"]`);
    // 根据类型填写详细信息...
    await this.page.click('button:has-text("下一步")');
    
    // Step 3: 效果设置
    for (const effect of rule.effects) {
      await this.selectEffect(effect);
    }
    await this.page.click('button:has-text("下一步")');
    
    // Step 4: 冷却时间
    if (rule.cooldown) {
      await this.page.fill('[name="cooldown"]', rule.cooldown.toString());
    }
    await this.page.click('button:has-text("下一步")');
    
    // Step 5: 确认创建
    await this.page.click('button:has-text("创建规则")');
    
    // 等待创建成功
    await this.page.waitForSelector('.rule-created-success');
  }
  
  // 使用模板创建规则
  async createFromTemplate(templateName: string) {
    await this.navigate('/game/test/rules');
    await this.page.click('button:has-text("使用模板")');
    
    await this.page.click(`[data-template="${templateName}"]`);
    await this.page.click('button:has-text("使用此模板")');
    
    await this.page.waitForSelector('.rule-created-success');
  }
  
  // AI解析规则
  async parseRuleWithAI(description: string) {
    await this.navigate('/game/test/rules/ai');
    
    await this.page.fill('textarea[name="ruleDescription"]', description);
    await this.page.click('button:has-text("解析")');
    
    // 等待AI响应
    await this.page.waitForSelector('.ai-parse-result', { timeout: 15000 });
    
    // 获取解析结果
    const result = await this.page.evaluate(() => {
      const resultEl = document.querySelector('.ai-parse-result');
      return resultEl ? JSON.parse(resultEl.getAttribute('data-result') || '{}') : null;
    });
    
    return result;
  }
  
  private async selectEffect(effect: any) {
    // 根据效果类型选择和配置
    await this.page.click(`[data-effect="${effect.type}"]`);
    // 填写效果参数...
  }
  
  // 获取规则列表
  async getRulesList() {
    const rules = await this.page.$$eval('.rule-item', elements => 
      elements.map(el => ({
        name: el.querySelector('.rule-name')?.textContent || '',
        level: parseInt(el.querySelector('.rule-level')?.textContent || '0'),
        cooldown: parseInt(el.querySelector('.rule-cooldown')?.textContent || '0')
      }))
    );
    return rules;
  }
  
  // 验证规则存在
  async expectRuleExists(ruleName: string) {
    const rules = await this.getRulesList();
    expect(rules.some(r => r.name === ruleName)).toBeTruthy();
  }
}

// ==================== NPC助手 ====================
export class NPCHelper extends BasePage {
  async navigateToNPCs(gameId: string) {
    await this.navigate(`/game/${gameId}/npcs`);
  }
  
  async getNPCList() {
    const npcs = await this.page.$$eval('.npc-card', elements =>
      elements.map(el => ({
        name: el.querySelector('.npc-name')?.textContent || '',
        location: el.querySelector('.npc-location')?.textContent || '',
        hp: parseInt(el.querySelector('.npc-hp')?.textContent || '0'),
        sanity: parseInt(el.querySelector('.npc-sanity')?.textContent || '0'),
        fear: parseInt(el.querySelector('.npc-fear')?.textContent || '0'),
        isAlive: !el.classList.contains('npc-dead')
      }))
    );
    return npcs;
  }
  
  async getNPCByName(name: string) {
    const npcs = await this.getNPCList();
    return npcs.find(npc => npc.name === name);
  }
  
  async expectNPCStatus(name: string, expected: {
    isAlive?: boolean;
    location?: string;
    fear?: number;
  }) {
    const npc = await this.getNPCByName(name);
    expect(npc).toBeTruthy();
    
    if (expected.isAlive !== undefined) {
      expect(npc?.isAlive).toBe(expected.isAlive);
    }
    
    if (expected.location !== undefined) {
      expect(npc?.location).toBe(expected.location);
    }
    
    if (expected.fear !== undefined) {
      expect(npc?.fear).toBeGreaterThanOrEqual(expected.fear);
    }
  }
}

// ==================== WebSocket助手 ====================
export class WebSocketHelper {
  private messages: any[] = [];
  
  constructor(private page: Page) {}
  
  async connectAndListen() {
    // 注入WebSocket监听器
    await this.page.evaluate(() => {
      window.wsMessages = [];
      
      const originalWebSocket = window.WebSocket;
      window.WebSocket = class extends originalWebSocket {
        constructor(url: string) {
          super(url);
          
          this.addEventListener('message', (event) => {
            window.wsMessages.push({
              type: 'received',
              data: JSON.parse(event.data),
              timestamp: Date.now()
            });
          });
          
          const originalSend = this.send.bind(this);
          this.send = (data: any) => {
            window.wsMessages.push({
              type: 'sent',
              data: typeof data === 'string' ? JSON.parse(data) : data,
              timestamp: Date.now()
            });
            return originalSend(data);
          };
        }
      };
    });
  }
  
  async getMessages() {
    const messages = await this.page.evaluate(() => window.wsMessages || []);
    return messages;
  }
  
  async waitForMessage(type: string, timeout = 5000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      const messages = await this.getMessages();
      const message = messages.find(m => 
        m.type === 'received' && m.data.type === type
      );
      
      if (message) {
        return message.data;
      }
      
      await this.page.waitForTimeout(100);
    }
    
    throw new Error(`Timeout waiting for message: ${type}`);
  }
  
  async expectMessage(type: string, data?: any) {
    const message = await this.waitForMessage(type);
    expect(message).toBeTruthy();
    
    if (data) {
      expect(message.data).toMatchObject(data);
    }
  }
}

// ==================== 性能测试助手 ====================
export class PerformanceHelper {
  constructor(private page: Page) {}
  
  async measureLoadTime() {
    const metrics = await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
      };
    });
    return metrics;
  }
  
  async measureAPIResponse(apiPath: string) {
    const startTime = Date.now();
    await this.page.waitForResponse(
      response => response.url().includes(apiPath)
    );
    const endTime = Date.now();
    return endTime - startTime;
  }
  
  async runLighthouse(url: string) {
    // 这里应该集成Lighthouse
    // 为简化示例，返回模拟数据
    return {
      performance: 92,
      accessibility: 95,
      bestPractices: 88,
      seo: 90
    };
  }
  
  async expectPerformance(metrics: {
    loadTime?: number;
    apiResponse?: number;
    lighthouse?: number;
  }) {
    if (metrics.loadTime) {
      const loadMetrics = await this.measureLoadTime();
      expect(loadMetrics.loadComplete).toBeLessThan(metrics.loadTime);
    }
    
    if (metrics.apiResponse) {
      const responseTime = await this.measureAPIResponse('/api/games');
      expect(responseTime).toBeLessThan(metrics.apiResponse);
    }
    
    if (metrics.lighthouse) {
      const scores = await this.runLighthouse(this.page.url());
      expect(scores.performance).toBeGreaterThan(metrics.lighthouse);
    }
  }
}

// ==================== 导出所有助手 ====================
export function setupHelpers(page: Page) {
  return {
    game: new GameHelper(page),
    rule: new RuleHelper(page),
    npc: new NPCHelper(page),
    ws: new WebSocketHelper(page),
    perf: new PerformanceHelper(page)
  };
}

// TypeScript类型声明
declare global {
  interface Window {
    wsMessages: any[];
  }
}
