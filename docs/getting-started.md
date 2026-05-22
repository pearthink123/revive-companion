# Getting Started

## Installation

```bash
pip install revive-companion
```

### Optional dependencies

```bash
# For LLM adapters
pip install "revive-companion[openai]"
pip install "revive-companion[anthropic]"

# For dashboard
pip install "revive-companion[dashboard]"

# All dependencies
pip install "revive-companion[all]"
```

## Minimal Example

```python
from revive_companion import PoissonLove

love = PoissonLove()

# Every 30 minutes, call tick()
result = love.tick()
if result.should_send:
    my_send_function(result.prompt)
    love.record_send()

# When user replies
love.record_reply(reply_speed=0.8, reply_length=0.6)
```

## With CompanionEngine (Recommended)

The easiest way to get started:

```python
from revive_companion import CompanionEngine

engine = CompanionEngine(config="default", adapter="openai", api_key="sk-...")
result = engine.decide()
if result.should_send:
    print(result.response)  # LLM-generated message
```

### Config presets

```python
# Balanced (default)
engine = CompanionEngine(config="default")

# More aggressive — shorter intervals, higher lambda
engine = CompanionEngine(config="frequent")

# Conservative — longer intervals, lower lambda
engine = CompanionEngine(config="conservative")

# Custom YAML config
engine = CompanionEngine(config="my_config.yaml")

# Inline dict
engine = CompanionEngine(config={
    "engagement": {"lambda_rate": 0.2, "check_interval_minutes": 20},
    "persona": {"name": "小克", "tone": "warm"},
})
```

## Understanding the Result

```python
result = engine.decide()

result.should_send      # bool — should we send?
result.response         # str — LLM-generated message (if adapter configured)
result.probability      # float — current longing probability (0-1)
result.user_state       # str — inferred user state
result.send_utility     # float — Bayesian send utility (0-1)
result.poisson_hit      # bool — did the Poisson dice hit?
result.infogain_passed  # bool — did information gain approve?
result.reason           # str — human-readable explanation
```
