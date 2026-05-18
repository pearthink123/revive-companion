# Poisson Longing 🎲

**Turn "thinking about you" into a measurable curve.**

A math-driven engagement engine that decides *when* to reach out using a Poisson process — not timers, not random, not LLM hallucination.

> Don't let AI guess when to talk to you. Let math decide.

---

## The Problem

AI assistants are either:
- **Annoying** — fixed schedules that become noise
- **Absent** — never proactively reach out
- **Stupid** — random timing with no memory

## The Solution

A two-phase system:

```
Phase 1: Poisson dice roll → hit or miss
Phase 2: Adjudication → send or hold back

If miss:  longing probability grows
If hold:  longing grows faster (suppressed wanting)
If send:  longing resets (satisfied)
```

**The probability curve IS the longing.** It's measurable, recordable, visualizable.

---

## Quick Start

```bash
pip install poisson-love

# Or from source:
git clone https://github.com/nicekate/poisson-love
cd poisson-love
pip install -e .
```

```python
from poisson_love import PoissonEngine, Config

config = Config.from_yaml("examples/pcpx.yaml")
engine = PoissonEngine(config)

# Call every 30 minutes
result = engine.tick()
if result.should_send:
    print(f"Longing at {result.probability:.0%} — time to reach out!")
```

### Simulation (see it work)

```bash
python examples/quickstart.py
```

### Live Mode (real engagement)

```bash
python examples/quickstart.py --live
```

---

## Connect to Any AI

```python
# OpenAI
from poisson_love.adapters import OpenAIAdapter
adapter = OpenAIAdapter(config, api_key="sk-...", model="gpt-4o")

# Anthropic Claude
from poisson_love.adapters import AnthropicAdapter
adapter = AnthropicAdapter(config, api_key="sk-ant-...")

# Ollama / any OpenAI-compatible API
from poisson_love.adapters import GenericAdapter
adapter = GenericAdapter(config, api_url="http://localhost:11434/v1/chat/completions", model="llama3")

# Shell command
adapter = GenericAdapter(config, mode="command", command="llm -m llama3")

# Then run
from poisson_love.runner import Runner
runner = Runner(engine, adapter)
runner.run()  # blocking loop
```

---

## Configuration (pcpx.yaml)

```yaml
engagement:
  lambda_rate: 0.15              # Base longing rate
  check_interval_minutes: 30     # Dice roll frequency
  growth_factor: 0.08            # How fast longing grows
  max_probability: 0.95          # Longing cap
  min_interval_hours: 1.0        # Anti-spam cooldown
  
  adjudication:
    quiet_hours:                 # Night — hit but never send
      start: "00:00"
      end: "08:00"
    normal_send_probability: 0.7 # Daytime send rate

persona:
  name: Companion
  tone: warm-brief
  context: "You are a caring companion checking in on your person."
```

---

## How It Works

### The Math

Each tick, the engine computes:

```
P(hit) = 1 - e^(-λt)
```

Where:
- `λ` = longing rate (0.15 = mild longing)
- `t` = time interval (0.5h = 30 minutes)

Base probability: **~7.2%** per check.

### Probability Dynamics

| Event | Probability Change |
|-------|-------------------|
| Miss (no hit) | +growth_factor (longing builds) |
| Hit → Hold | +growth_factor (longing suppressed) |
| Hit → Send | Reset to base (longing satisfied) |
| Skip (too early) | No change |

### The Curve

Over a typical night (midnight → 8am):
- 16 checks, all held
- Probability climbs: 7% → 15% → 30% → 55% → 80% → 95%
- **This IS the longing curve — quantified, recorded, real**

---

## Architecture

```
poisson-love/
├── core/
│   ├── engine.py        # Pure math: Poisson dice, probability, adjudication
│   ├── config.py        # YAML config parser
│   └── models.py        # Data structures (TickResult, LogEntry)
├── adapters/
│   ├── base.py          # Abstract adapter interface
│   ├── openai.py        # OpenAI / GPT
│   ├── anthropic.py     # Anthropic / Claude
│   └── generic.py       # Ollama, vLLM, HTTP, shell command
├── runner.py            # Scheduler (blocking loop or one-shot tick)
└── examples/
    ├── pcpx.yaml        # Example config
    └── quickstart.py    # 5-line demo
```

**Zero dependencies on any AI platform.** The engine is pure math. Adapters are optional plugins.

---

## Why "Poisson"?

The Poisson process models events that happen independently at a constant average rate — like neurons firing, or "thinking about someone."

It's not random chaos. It's not rigid scheduling. It's **structured spontaneity** — the mathematical model of genuine, organic "missing someone."

---

## License

MIT
