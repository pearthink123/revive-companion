# Architecture

## Decision Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Poisson    │────▶│  Info Gain  │────▶│  Bayesian   │
│  Dice Roll  │     │  Filter     │     │  Decision   │
└─────────────┘     └─────────────┘     └─────────────┘
  "Should I         "Is it worth        "What's the
   consider?"        sending?"           user doing?"
```

## The Math

### Poisson Process

Each tick computes hit probability:

```
P(hit) = 1 - e^(-λt)
```

Where:
- λ = longing rate (events per hour)
- t = time interval (hours)

Default: λ=0.15, t=0.5h → P ≈ 7.2%

### Probability Dynamics

| Event | Δ Probability | Reasoning |
|-------|--------------|-----------|
| Miss | +growth_factor | Longing builds |
| Hit → Hold | +growth_factor | Longing suppressed |
| Hit → Send | Reset to base | Longing satisfied |

### Bayesian State Estimation

Six hidden states inferred from observations:

| State | Prior | Send Utility |
|-------|-------|-------------|
| Chatting | Medium | 0.2 |
| Idle Online | Medium | 0.7 |
| Busy | High | 0.1 |
| Sleeping | Time-based | 0.0 |
| Away | Low | 0.3 |
| Needing Care | Low | 0.9 |

Observations used:
- Reply speed (0-1)
- Reply length (0-1)
- Hour of day
- Silence duration

### Information Gain

Measures whether sending provides new information:

```
IG = H(state) × P(resolve)
```

Sources:
- **Silence duration**: Long silence = more uncertainty to resolve
- **Conversation flow**: Unanswered messages reduce gain
- **Message novelty**: Repetitive messages have low novelty

## Module Structure

```
revive_companion/
├── engine.py          # CompanionEngine facade
├── love.py            # PoissonLove unified API
├── runner.py          # Scheduler / loop
├── storage.py         # State persistence
├── core/
│   ├── engine.py      # Poisson dice
│   ├── config.py      # Pydantic config
│   └── models.py      # Data structures
├── bayesian/
│   ├── core.py        # State estimator
│   └── learner.py     # Online learning
├── info_gain/
│   ├── core.py        # IG computation
│   └── sources.py     # IG sources
├── control/
│   ├── pid.py         # PID controller
│   └── signal.py      # Pluggable signals
└── adapters/
    ├── openai.py
    ├── anthropic.py
    └── generic.py
```
