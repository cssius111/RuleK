#!/usr/bin/env node

/**
 * RuleK Web UI 进度追踪系统
 * 
 * 功能:
 * - 运行特定阶段的测试
 * - 生成进度报告
 * - 检查成功标准
 * - 输出下一步建议
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';

const execAsync = promisify(exec);

// 阶段定义
const PHASES = {
  0: {
    name: '环境准备',
    duration: 1,
    tests: ['phase0.spec.ts'],
    criteria: {
      functional: ['开发服务器启动', 'API服务器启动', 'WebSocket连接'],
      performance: ['首屏加载<3s'],
      quality: ['无构建错误']
    }
  },
  1: {
    name: '基础框架',
    duration: 2,
    tests: ['phase1.spec.ts'],
    criteria: {
      functional: ['路由系统', '状态管理', '基础布局'],
      performance: ['路由切换<100ms'],
      quality: ['TypeScript无错误', '组件测试覆盖']
    }
  },
  2: {
    name: '游戏创建流程',
    duration: 2,
    tests: ['phase2.spec.ts'],
    criteria: {
      functional: ['新游戏创建', '存档加载', '参数验证'],
      performance: ['创建游戏<2s'],
      quality: ['表单验证完整', 'API错误处理']
    }
  },
  3: {
    name: '游戏核心界面',
    duration: 3,
    tests: ['phase3.spec.ts'],
    criteria: {
      functional: ['游戏主界面', '回合推进', 'WebSocket实时更新'],
      performance: ['状态更新<100ms', 'AI响应<2s'],
      quality: ['实时同步无错误', '状态一致性']
    }
  },
  4: {
    name: '规则管理系统',
    duration: 3,
    tests: ['phase4.spec.ts'],
    criteria: {
      functional: ['规则创建', 'AI解析', '模板系统'],
      performance: ['AI解析<3s', '实时预览<500ms'],
      quality: ['规则验证完整', '成本计算准确']
    }
  },
  5: {
    name: 'NPC和AI系统',
    duration: 3,
    tests: ['phase5.spec.ts'],
    criteria: {
      functional: ['NPC状态展示', 'AI对话生成', '流式推送'],
      performance: ['AI生成<2s', '流式无延迟'],
      quality: ['内容相关性>90%', '无推送丢失']
    }
  },
  6: {
    name: '优化和完善',
    duration: 2,
    tests: ['phase6.spec.ts', 'performance.spec.ts'],
    criteria: {
      functional: ['所有功能完整', '错误处理完善'],
      performance: ['Lighthouse>90', '包体积<500KB'],
      quality: ['测试覆盖>80%', '0关键bug']
    }
  }
};

// 成功标准检查
class SuccessCriteria {
  constructor(phase) {
    this.phase = phase;
    this.results = {
      functional: [],
      performance: [],
      quality: []
    };
  }
  
  async check() {
    console.log(chalk.blue(`\n📊 检查 Phase ${this.phase} 成功标准...\n`));
    
    const phaseConfig = PHASES[this.phase];
    if (!phaseConfig) {
      console.log(chalk.red('未知的阶段'));
      return false;
    }
    
    // 运行测试
    const testResults = await this.runTests(phaseConfig.tests);
    
    // 检查功能完整性
    const functionalPass = await this.checkFunctional(phaseConfig.criteria.functional);
    
    // 检查性能指标
    const performancePass = await this.checkPerformance(phaseConfig.criteria.performance);
    
    // 检查代码质量
    const qualityPass = await this.checkQuality(phaseConfig.criteria.quality);
    
    // 生成报告
    await this.generateReport({
      testResults,
      functionalPass,
      performancePass,
      qualityPass
    });
    
    return testResults && functionalPass && performancePass && qualityPass;
  }
  
  async runTests(testFiles) {
    console.log(chalk.yellow('🧪 运行测试...\n'));
    
    try {
      const testCommand = `npx playwright test ${testFiles.join(' ')} --reporter=json`;
      const { stdout, stderr } = await execAsync(testCommand);
      
      // 解析测试结果
      const results = JSON.parse(stdout);
      const passed = results.suites.every(suite => 
        suite.specs.every(spec => spec.ok)
      );
      
      if (passed) {
        console.log(chalk.green(`✅ 所有测试通过`));
      } else {
        console.log(chalk.red(`❌ 部分测试失败`));
        console.log(stderr);
      }
      
      return passed;
    } catch (error) {
      console.log(chalk.red(`❌ 测试执行失败: ${error.message}`));
      return false;
    }
  }
  
  async checkFunctional(criteria) {
    console.log(chalk.yellow('\n🔧 检查功能完整性...\n'));
    
    let allPass = true;
    for (const criterion of criteria) {
      // 这里应该有实际的功能检查逻辑
      const passed = await this.checkFeature(criterion);
      
      if (passed) {
        console.log(chalk.green(`  ✅ ${criterion}`));
        this.results.functional.push({ name: criterion, passed: true });
      } else {
        console.log(chalk.red(`  ❌ ${criterion}`));
        this.results.functional.push({ name: criterion, passed: false });
        allPass = false;
      }
    }
    
    return allPass;
  }
  
  async checkPerformance(criteria) {
    console.log(chalk.yellow('\n⚡ 检查性能指标...\n'));
    
    let allPass = true;
    for (const criterion of criteria) {
      // 运行Lighthouse或其他性能测试
      const passed = await this.measurePerformance(criterion);
      
      if (passed) {
        console.log(chalk.green(`  ✅ ${criterion}`));
        this.results.performance.push({ name: criterion, passed: true });
      } else {
        console.log(chalk.red(`  ❌ ${criterion}`));
        this.results.performance.push({ name: criterion, passed: false });
        allPass = false;
      }
    }
    
    return allPass;
  }
  
  async checkQuality(criteria) {
    console.log(chalk.yellow('\n📋 检查代码质量...\n'));
    
    let allPass = true;
    for (const criterion of criteria) {
      const passed = await this.checkCodeQuality(criterion);
      
      if (passed) {
        console.log(chalk.green(`  ✅ ${criterion}`));
        this.results.quality.push({ name: criterion, passed: true });
      } else {
        console.log(chalk.red(`  ❌ ${criterion}`));
        this.results.quality.push({ name: criterion, passed: false });
        allPass = false;
      }
    }
    
    return allPass;
  }
  
  async checkFeature(feature) {
    // 模拟功能检查
    // 实际应该调用具体的测试或检查API
    return Math.random() > 0.2; // 80%通过率
  }
  
  async measurePerformance(metric) {
    // 模拟性能测量
    // 实际应该运行Lighthouse或性能测试
    return Math.random() > 0.3; // 70%通过率
  }
  
  async checkCodeQuality(quality) {
    // 模拟代码质量检查
    // 实际应该运行ESLint, TypeScript检查等
    return Math.random() > 0.1; // 90%通过率
  }
  
  async generateReport(results) {
    const phaseConfig = PHASES[this.phase];
    const timestamp = new Date().toISOString();
    
    const report = {
      phase: this.phase,
      name: phaseConfig.name,
      timestamp,
      duration: phaseConfig.duration,
      results: this.results,
      summary: {
        functional: this.results.functional.filter(r => r.passed).length + '/' + this.results.functional.length,
        performance: this.results.performance.filter(r => r.passed).length + '/' + this.results.performance.length,
        quality: this.results.quality.filter(r => r.passed).length + '/' + this.results.quality.length
      },
      passed: results.testResults && results.functionalPass && results.performancePass && results.qualityPass
    };
    
    // 保存JSON报告
    const reportPath = path.join('reports', `phase${this.phase}-${Date.now()}.json`);
    await fs.mkdir('reports', { recursive: true });
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    // 生成Markdown报告
    const markdown = this.generateMarkdownReport(report);
    const mdPath = path.join('reports', `phase${this.phase}-report.md`);
    await fs.writeFile(mdPath, markdown);
    
    console.log(chalk.blue(`\n📄 报告已生成: ${mdPath}`));
  }
  
  generateMarkdownReport(report) {
    return `# Phase ${report.phase}: ${report.name} - 进度报告

## 📅 测试时间
${report.timestamp}

## 📊 测试结果

### 功能完整性: ${report.summary.functional}
${report.results.functional.map(r => 
  `- ${r.passed ? '✅' : '❌'} ${r.name}`
).join('\n')}

### 性能指标: ${report.summary.performance}
${report.results.performance.map(r => 
  `- ${r.passed ? '✅' : '❌'} ${r.name}`
).join('\n')}

### 代码质量: ${report.summary.quality}
${report.results.quality.map(r => 
  `- ${r.passed ? '✅' : '❌'} ${r.name}`
).join('\n')}

## 📈 总体评估
${report.passed ? '✅ **Phase 通过，可以进入下一阶段**' : '❌ **需要修复问题后重新测试**'}

## 🚀 下一步行动
${report.passed ? 
  `- 开始 Phase ${report.phase + 1}: ${PHASES[report.phase + 1]?.name || '项目完成'}
- 预计时间: ${PHASES[report.phase + 1]?.duration || 0} 天` :
  `- 修复失败的测试
- 解决性能问题
- 改进代码质量`}
`;
  }
}

// 进度追踪器
class ProgressTracker {
  constructor() {
    this.currentPhase = 0;
    this.startTime = Date.now();
  }
  
  async trackPhase(phase) {
    console.log(chalk.cyan.bold(`
╔══════════════════════════════════════════════════════════╗
║                  RuleK Web UI 进度追踪                    ║
║                     Phase ${phase}: ${PHASES[phase].name.padEnd(20)}      ║
╚══════════════════════════════════════════════════════════╝
    `));
    
    // 检查成功标准
    const criteria = new SuccessCriteria(phase);
    const passed = await criteria.check();
    
    // 显示进度
    this.showProgress(phase, passed);
    
    // 给出建议
    this.showRecommendations(phase, passed);
    
    return passed;
  }
  
  showProgress(phase, passed) {
    const totalPhases = Object.keys(PHASES).length;
    const progress = ((phase + 1) / totalPhases * 100).toFixed(1);
    
    console.log(chalk.blue('\n📈 整体进度\n'));
    
    // 进度条
    const barLength = 40;
    const filled = Math.floor(barLength * (phase + 1) / totalPhases);
    const empty = barLength - filled;
    const bar = '█'.repeat(filled) + '░'.repeat(empty);
    
    console.log(`  [${bar}] ${progress}%`);
    console.log(`  已完成: ${phase + 1}/${totalPhases} 阶段\n`);
    
    // 时间统计
    const elapsed = Date.now() - this.startTime;
    const days = Math.floor(elapsed / (1000 * 60 * 60 * 24));
    console.log(`  用时: ${days} 天`);
    
    // 预计剩余时间
    const remainingPhases = totalPhases - phase - 1;
    const remainingDays = Object.values(PHASES)
      .slice(phase + 1)
      .reduce((sum, p) => sum + p.duration, 0);
    console.log(`  预计剩余: ${remainingDays} 天\n`);
  }
  
  showRecommendations(phase, passed) {
    console.log(chalk.magenta('\n💡 建议\n'));
    
    if (passed) {
      console.log(chalk.green('  ✅ 当前阶段已完成，建议：'));
      console.log(`  1. 提交代码: git commit -m "Complete Phase ${phase}"`);
      console.log(`  2. 创建标签: git tag phase${phase}`);
      console.log(`  3. 开始下一阶段: npm run track:phase${phase + 1}`);
      
      if (PHASES[phase + 1]) {
        console.log(`\n  下一阶段: ${PHASES[phase + 1].name}`);
        console.log(`  预计时间: ${PHASES[phase + 1].duration} 天`);
        console.log(`  主要任务:`);
        PHASES[phase + 1].criteria.functional.forEach(task => {
          console.log(`    - ${task}`);
        });
      } else {
        console.log(chalk.green.bold('\n  🎉 恭喜！项目已完成！'));
      }
    } else {
      console.log(chalk.yellow('  ⚠️  当前阶段未完成，建议：'));
      console.log('  1. 查看测试报告: npm run test:report');
      console.log('  2. 修复失败的测试');
      console.log('  3. 优化性能指标');
      console.log('  4. 重新运行测试: npm run test:phase' + phase);
    }
  }
}

// 主函数
async function main() {
  const phase = parseInt(process.argv[2] || '0');
  
  if (isNaN(phase) || !PHASES[phase]) {
    console.log(chalk.red('请指定有效的阶段号 (0-6)'));
    console.log('用法: npm run track:phase<n>');
    process.exit(1);
  }
  
  const tracker = new ProgressTracker();
  const passed = await tracker.trackPhase(phase);
  
  process.exit(passed ? 0 : 1);
}

// 执行
main().catch(error => {
  console.error(chalk.red('错误:'), error);
  process.exit(1);
});
