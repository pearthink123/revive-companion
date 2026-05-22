# revive-companion 💘

**让 AI 主动找你时，像真人一样"想你了"，而不是"该发消息了"。**

用泊松过程 + 贝叶斯推断 + 信息增益，决定**该不该**、**什么时候**打扰用户。

## 核心理念

AI 伴侣的主动消息要么太机械（定时任务），要么太随机（没有记忆）。revive-companion 用数学建模"想你了"这个人类行为：

- 🎲 **泊松过程** — 像真人"突然想你了"一样随机触发
- 📊 **信息论** — 如果已知用户状态，就别打扰了
- 🧠 **贝叶斯推断** — 推断用户在做什么，做对应决策

## 快速开始

```bash
pip install revive-companion
```

```python
from revive_companion import CompanionEngine

engine = CompanionEngine(config="default", adapter="openai", api_key="sk-...")
result = engine.decide()
if result.should_send:
    print(result.response)
```

## 了解更多

- [Getting Started](getting-started.md) — 安装和基本用法
- [API Reference](api.md) — 完整 API 文档
- [Configuration](configuration.md) — 配置参数详解
- [Architecture](architecture.md) — 数学原理和架构设计
- [Integrations](integrations.md) — Telegram/Discord/Slack 集成
