"""
poisson-love: Math-driven AI engagement engine.
Turn missing someone into a measurable curve.
"""

from .core.engine import PoissonEngine
from .core.config import Config
from .core.models import TickResult, Action, LogEntry

__version__ = "0.1.0"
__all__ = ["PoissonEngine", "Config", "TickResult", "Action", "LogEntry"]
