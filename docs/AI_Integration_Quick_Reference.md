# AI集成快速参考

## 文件结构

```
src/
├── api/
│   ├── schemas.py         # Pydantic数据模型
│   ├── prompts.py         # Prompt模板管理
│   └── deepseek_client.py # DeepSeek API客户端
├── ai/
│   └── turn_pipeline.py   # AI回合管线
└── managers/
    └── game_state_manager.py # 添加AI集成方法
```

## 关键类和方法

### Schemas (src/api/schemas.py)
- `DialogueTurn`: 对话回合
- `PlannedAction`: 计划行动
- `TurnPlan`: 回合计划（对话+行动）
- `NarrativeOut`: 叙事输出
- `RuleEvalResult`: 规则评估结果

### DeepSeek Client (src/api/deepseek_client.py)
```python
async def generate_turn_plan(...) -> TurnPlan
async def generate_narrative_text(...) -> str
async def evaluate_rule_nl(...) -> RuleEvalResult
```

### AI Pipeline (src/ai/turn_pipeline.py)
```python
async def run_turn_ai() -> TurnPlan
async def generate_turn_narrative() -> str
async def evaluate_player_rule(rule_description: str) -> Dict
```

## 环境变量

```bash
DEEPSEEK_API_KEY=your_api_key_here
AI_ENABLED=true
AI_MODEL=deepseek-chat
AI_TIMEOUT=30
```

## 配置示例

```json
{
  "game": {
    "ai_enabled": true
  },
  "api": {
    "deepseek_api_key": "${DEEPSEEK_API_KEY}",
    "model": "deepseek-chat",
    "timeout": 30,
    "max_retries": 3
  }
}
```

## CLI命令示例

```python
# 初始化AI
await game_mgr.init_ai_pipeline()

# 运行AI回合
plan = await game_mgr.run_ai_turn()

# 生成叙事
narrative = await game_mgr.generate_narrative()

# 评估规则
result = await game_mgr.ai_pipeline.evaluate_player_rule("晚上10点后不能开灯")
```

## Prompt关键字段

### 回合计划输入
- `npcs`: NPC状态列表
- `time_of_day`: 时间段
- `location`: 当前位置
- `recent_events`: 最近事件
- `available_places`: 可用地点

### 叙事生成输入
- `events`: 事件列表
- `time_of_day`: 时间段

### 规则评估输入
- `rule_nl`: 自然语言规则
- `rule_count`: 已有规则数
- `avg_fear`: 平均恐惧值
- `places`: 地点列表

## 错误处理模式

```python
try:
    result = await ai_operation()
except Exception as e:
    logger.error(f"AI操作失败: {str(e)}")
    # 使用降级方案
    return fallback_result
```

## 测试命令

```bash
# 运行AI相关测试
python -m pytest tests/test_ai_integration.py -v

# 测试单个功能
python -m pytest tests/test_ai_integration.py::test_turn_plan_generation -v

# 带日志的测试
python -m pytest tests/test_ai_integration.py -v -s --log-cli-level=DEBUG
```

## 性能优化建议

1. **缓存策略**
   - 缓存相似prompt的响应
   - TTL设置为5分钟

2. **并发控制**
   - 使用asyncio.Semaphore限制并发
   - 最大并发数：3

3. **Token优化**
   - 限制prompt长度
   - 使用temperature=0.7-0.9

## 故障排查

### 常见问题

1. **JSON解析失败**
   - 检查prompt中的JSON示例
   - 使用正则提取JSON部分

2. **超时错误**
   - 增加timeout值
   - 检查网络连接

3. **Schema验证失败**
   - 检查AI返回的字段
   - 添加默认值

### 日志位置
```
logs/
├── rulek.log          # 主日志
├── ai_requests.log    # AI请求日志
└── ai_errors.log      # AI错误日志
```

## 监控指标

- 平均响应时间
- 成功率
- Token使用量
- 错误类型分布

---

*更新时间：2024-12-20*
