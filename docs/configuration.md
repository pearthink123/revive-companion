# Configuration

## YAML Config File

```yaml
engagement:
  lambda_rate: 0.15              # Base longing rate (events/hour)
  check_interval_minutes: 30     # How often to roll the dice
  growth_factor: 0.08            # Probability increase per miss
  max_probability: 0.95          # Probability cap
  min_interval_hours: 1.0        # Anti-spam cooldown

  adjudication:
    quiet_hours:
      start: "00:00"
      end: "08:00"
    lunch_hours:
      start: "12:00"
      end: "14:00"
    late_hours:
      start: "23:00"
      end: "24:00"
    normal_send_probability: 0.7

persona:
  name: Companion
  tone: warm-brief
  context: "You are a caring companion checking in on your person."
```

## Parameters

### Engagement

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lambda_rate` | float | 0.15 | Poisson rate. Higher = more frequent "hits" |
| `check_interval_minutes` | int | 30 | How often to evaluate (minutes) |
| `growth_factor` | float | 0.08 | Probability growth per miss (0-1) |
| `max_probability` | float | 0.95 | Probability ceiling |
| `min_interval_hours` | float | 1.0 | Minimum time between sends |

### Adjudication

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `quiet_hours` | dict | 00:00-08:00 | No messages during this window |
| `normal_send_probability` | float | 0.7 | Chance to send during normal hours |
| `lunch_hours` | dict | — | Optional lunch window (30% send chance) |
| `late_hours` | dict | — | Optional late night window (30% send chance) |

### Persona

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "Companion" | AI persona name |
| `tone` | str | "warm" | Communication tone |
| `context` | str | "" | System prompt context |

## Config Presets

```python
from revive_companion import get_default_config

# Available presets
get_default_config("default")       # Balanced
get_default_config("frequent")      # Aggressive (lambda=0.30, 15min)
get_default_config("conservative")  # Cautious (lambda=0.08, 60min)
```
