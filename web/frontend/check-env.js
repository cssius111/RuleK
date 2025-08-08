#!/usr/bin/env node

/**
 * RuleK Web 环境验证脚本
 * 检查所有依赖和配置是否正确
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

const log = {
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.blue}ℹ️  ${msg}${colors.reset}`),
  title: (msg) => console.log(`\n${colors.cyan}━━━ ${msg} ━━━${colors.reset}\n`)
};

async function checkEnvironment() {
  log.title('RuleK Web 环境检查');
  
  const checks = {
    node: false,
    npm: false,
    frontendDir: false,
    backendDir: false,
    packageJson: false,
    dependencies: false,
    viteConfig: false,
    devServer: false,
    apiServer: false
  };
  
  // 1. 检查Node.js版本
  try {
    const { stdout } = await execAsync('node --version');
    const version = stdout.trim();
    const major = parseInt(version.split('.')[0].substring(1));
    if (major >= 16) {
      log.success(`Node.js ${version} (需要 >= 16)`);
      checks.node = true;
    } else {
      log.error(`Node.js版本过低: ${version} (需要 >= 16)`);
    }
  } catch (e) {
    log.error('未检测到Node.js');
  }
  
  // 2. 检查npm
  try {
    const { stdout } = await execAsync('npm --version');
    log.success(`npm ${stdout.trim()}`);
    checks.npm = true;
  } catch (e) {
    log.error('未检测到npm');
  }
  
  // 3. 检查目录结构
  const projectRoot = path.resolve(__dirname, '../..');
  const frontendDir = path.resolve(__dirname);
  const backendDir = path.resolve(projectRoot, 'web/backend');
  
  if (fs.existsSync(frontendDir)) {
    log.success(`前端目录: ${frontendDir}`);
    checks.frontendDir = true;
  } else {
    log.error('前端目录不存在');
  }
  
  if (fs.existsSync(backendDir)) {
    log.success(`后端目录: ${backendDir}`);
    checks.backendDir = true;
  } else {
    log.warning('后端目录不存在');
  }
  
  // 4. 检查package.json
  const packageJsonPath = path.join(frontendDir, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    log.success(`package.json已配置 (${Object.keys(pkg.scripts || {}).length}个脚本)`);
    checks.packageJson = true;
    
    // 列出关键脚本
    const keyScripts = ['dev', 'build', 'test:phase0', 'track:phase0', 'setup:playwright'];
    console.log('\n  关键脚本:');
    keyScripts.forEach(script => {
      if (pkg.scripts && pkg.scripts[script]) {
        console.log(`    ✓ ${script}`);
      } else {
        console.log(`    ✗ ${script} (缺失)`);
      }
    });
  } else {
    log.error('package.json不存在');
  }
  
  // 5. 检查依赖安装
  const nodeModulesPath = path.join(frontendDir, 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    const modules = fs.readdirSync(nodeModulesPath);
    log.success(`依赖已安装 (${modules.length}个包)`);
    checks.dependencies = true;
  } else {
    log.warning('依赖未安装，请运行: npm install');
  }
  
  // 6. 检查Vite配置
  const viteConfigPath = path.join(frontendDir, 'vite.config.ts');
  if (fs.existsSync(viteConfigPath)) {
    log.success('Vite配置文件存在');
    checks.viteConfig = true;
  } else {
    log.warning('Vite配置文件不存在');
  }
  
  // 7. 检查开发服务器
  try {
    const response = await fetch('http://localhost:5173');
    if (response.ok) {
      log.success('开发服务器运行中 (http://localhost:5173)');
      checks.devServer = true;
    }
  } catch (e) {
    log.info('开发服务器未运行 (运行 npm run dev 启动)');
  }
  
  // 8. 检查API服务器
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      log.success('API服务器运行中 (http://localhost:8000)');
      checks.apiServer = true;
    }
  } catch (e) {
    log.info('API服务器未运行 (运行 python ../../start_web_server.py 启动)');
  }
  
  // 总结
  log.title('检查结果');
  
  const passed = Object.values(checks).filter(v => v).length;
  const total = Object.keys(checks).length;
  
  console.log(`\n通过: ${passed}/${total} 项\n`);
  
  // 建议
  log.title('下一步建议');
  
  if (!checks.dependencies) {
    console.log('1. 安装依赖:');
    console.log('   npm install\n');
  }
  
  if (!checks.devServer) {
    console.log('2. 启动开发服务器:');
    console.log('   npm run dev\n');
  }
  
  if (!checks.apiServer) {
    console.log('3. 启动API服务器:');
    console.log('   cd ../.. && python start_web_server.py\n');
  }
  
  if (checks.dependencies && checks.packageJson) {
    console.log('4. 安装Playwright (E2E测试):');
    console.log('   npm run setup:playwright\n');
    
    console.log('5. 运行环境验证测试:');
    console.log('   npm run test:phase0\n');
    
    console.log('6. 查看进度报告:');
    console.log('   npm run track:phase0\n');
  }
  
  // 常用命令
  log.title('常用命令');
  console.log('开发:');
  console.log('  npm run dev           # 启动开发服务器');
  console.log('  npm run build         # 构建生产版本');
  console.log('');
  console.log('测试:');
  console.log('  npm run test:phase0   # 运行Phase 0测试');
  console.log('  npm run track:phase0  # 生成进度报告');
  console.log('');
  console.log('其他:');
  console.log('  npm run lint          # 代码检查');
  console.log('  npm run format        # 代码格式化');
  
  return passed === total;
}

// 主函数
async function main() {
  const success = await checkEnvironment();
  process.exit(success ? 0 : 1);
}

main().catch(console.error);
