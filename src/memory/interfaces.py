from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Short-Term Memory Protocol (extends base MemoryStore)
class ShortTermMemoryProtocol(ABC):
    """
    Protocol for short-term (ephemeral/session) memory: Ordered, prunable history.
    E.g., recent chat messages or tool outputs.
    """
    
    @abstractmethod
    def append(self, key: str, value: Any) -> None:
        """Append a value to the key's ordered history (e.g., conversation)."""
        ...
    
    @abstractmethod
    def get_recent(self, key: str, n: int = 10) -> List[Any]:
        """Retrieve the most recent N values for a key (deserialized)."""
        ...
    
    @abstractmethod
    def prune(self, key: str, max_size: int = 100) -> None:
        """Prune oldest entries for a key to max_size (FIFO)."""
        ...

# Long-Term Memory Protocol (extends base MemoryStore)
class LongTermMemoryProtocol(ABC):
    """
    Protocol for long-term (persistent/cross-session) memory: Durable, searchable storage.
    E.g., user preferences or summarized facts.
    """
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store a value with optional metadata (e.g., timestamp, tags, agent_id)."""
        ...
    
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for entries matching query (key-pattern or semantic; returns key/value/metadata)."""
        ...
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key and its value."""
        ...