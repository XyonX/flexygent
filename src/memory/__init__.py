from __future__ import annotations

# Core Protocol (defined in base_agent.py, re-exported for convenience)
from ..agents.base_agent import MemoryStore

# Short/Long-Term Protocols
from .interfaces import ShortTermMemoryProtocol, LongTermMemoryProtocol

# Implementations
from .stores import (
    InMemoryShortTerm,  # Short-term: Volatile, ordered history
    FileLongTerm,       # Long-term: JSON file-based persistence
    AgentMemory         # Composite: Unified short + long-term
)

__all__ = [
    "MemoryStore",
    "ShortTermMemoryProtocol",
    "LongTermMemoryProtocol",
    "InMemoryShortTerm",
    "FileLongTerm",
    "AgentMemory"
]