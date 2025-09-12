from __future__ import annotations
import json
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .interfaces import ShortTermMemoryProtocol, LongTermMemoryProtocol
from ..agents.base_agent import MemoryStore  # Base protocol

class InMemoryShortTerm(ShortTermMemoryProtocol):
    """
    Short-term memory: In-memory, ordered lists per key (e.g., conversation history).
    Auto-prunes to max_size; serializes values to JSON for storage.
    """
    
    def __init__(self, max_history_per_key: int = 50) -> None:
        self._store: Dict[str, deque[str]] = {}  # key → deque of serialized values (FIFO)
        self.max_history_per_key = max_history_per_key
    
    def _serialize(self, value: Any) -> str:
        return json.dumps(value, default=str)  # Handle non-JSON (e.g., datetime → str)
    
    def _deserialize(self, serialized: str) -> Any:
        return json.loads(serialized)
    
    def store(self, key: str, value: Any) -> None:
        self.update(key, value)  # Use update for consistency
    
    def retrieve(self, key: str) -> Any:
        if key not in self._store or not self._store[key]:
            raise KeyError(f"Short-term key '{key}' empty/not found.")
        return self._deserialize(list(self._store[key])[-1])  # Most recent
    
    def update(self, key: str, value: Any) -> None:
        if key not in self._store:
            self._store[key] = deque(maxlen=self.max_history_per_key)
        self._store[key].append(self._serialize(value))
        self.prune(key)  # Auto-prune
    
    def append(self, key: str, value: Any) -> None:
        self.update(key, value)  # Append is like update for short-term
    
    def get_recent(self, key: str, n: int = 10) -> List[Any]:
        if key not in self._store:
            return []
        recent_serialized = list(self._store[key])[-n:]
        return [self._deserialize(item) for item in recent_serialized]
    
    def prune(self, key: str, max_size: Optional[int] = None) -> None:
        if key in self._store:
            max_s = max_size or self.max_history_per_key
            current_list = list(self._store[key])
            self._store[key] = deque(current_list[-max_s:], maxlen=max_s)

class FileLongTerm(LongTermMemoryProtocol):
    """
    Long-term memory: JSON file-based, with metadata (timestamp, agent_id, tags).
    Stores as {key: {"value": Any, "metadata": Dict}}.
    Search: Simple key-pattern match (extend for embeddings later).
    """
    
    def __init__(self, file_path: str = "~/.flexygent/long_term_memory.json") -> None:
        self.file_path = Path(file_path).expanduser()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._store: Dict[str, Dict[str, Any]] = {}  # key → {"value": Any, "metadata": Dict}
        self._load()
    
    def _load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self._store = {
                        k: {"value": v["value"], "metadata": v.get("metadata", {})}
                        for k, v in data.items() if isinstance(v, dict)
                    }
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load long-term memory: {e}")
                self._store = {}
    
    def _save(self) -> None:
        try:
            with open(self.file_path, "w") as f:
                json.dump(self._store, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Failed to save long-term memory: {e}")
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        meta = metadata or {}
        meta["timestamp"] = datetime.now().isoformat()
        meta["agent_id"] = meta.get("agent_id", "default")  # Scope by agent
        self._store[key] = {"value": value, "metadata": meta}
        self._save()
    
    def retrieve(self, key: str) -> Any:
        if key not in self._store:
            raise KeyError(f"Long-term key '{key}' not found.")
        return self._store[key]["value"]
    
    def update(self, key: str, value: Any) -> None:
        self.store(key, value)  # Reuse store (updates metadata)
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Simple pattern match on keys
        matches = [k for k in self._store if query.lower() in k.lower()]
        matches = matches[:limit]
        return [
            {"key": k, "value": self._store[k]["value"], "metadata": self._store[k]["metadata"]}
            for k in matches
        ]
    
    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._save()

class AgentMemory(MemoryStore):
    """
    Composite memory: Routes short-term (ephemeral) vs. long-term (persistent) based on key prefix.
    E.g., "short:session_id:last_tool" → short-term; "long:user_pref:color" → long-term.
    Configurable: Enable/disable long-term.
    """
    
    SHORT_PREFIX = "short:"
    LONG_PREFIX = "long:"
    
    def __init__(self, short_term: Optional[ShortTermMemoryProtocol] = None, 
                 long_term: Optional[LongTermMemoryProtocol] = None,
                 enable_long_term: bool = True) -> None:
        self.short_term = short_term or InMemoryShortTerm()
        self.long_term = long_term if long_term else None
        self.enable_long_term = enable_long_term and self.long_term is not None
    
    def _is_short(self, key: str) -> bool:
        return key.startswith(self.SHORT_PREFIX)
    
    def _is_long(self, key: str) -> bool:
        return key.startswith(self.LONG_PREFIX) or (not self._is_short(key) and self.enable_long_term)
    
    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self._is_short(key):
            self.short_term.store(key, value)
        elif self._is_long(key) and self.long_term:
            self.long_term.store(key, value, metadata)
        else:
            raise ValueError(f"Invalid key prefix for memory: {key}. Use 'short:' or 'long:'.")
    
    def retrieve(self, key: str) -> Any:
        if self._is_short(key):
            return self.short_term.retrieve(key)
        elif self._is_long(key) and self.long_term:
            return self.long_term.retrieve(key)
        raise KeyError(f"Key '{key}' not found in short/long-term memory.")
    
    def update(self, key: str, value: Any) -> None:
        if self._is_short(key):
            self.short_term.update(key, value)
        elif self._is_long(key) and self.long_term:
            self.long_term.update(key, value)
    
    # Short-Term Specific
    def append_short(self, key: str, value: Any) -> None:
        full_key = self.SHORT_PREFIX + key
        self.short_term.append(full_key, value)
    
    def get_recent_short(self, key: str, n: int = 10) -> List[Any]:
        full_key = self.SHORT_PREFIX + key
        return self.short_term.get_recent(full_key, n)
    
    # Long-Term Specific
    def store_long(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        if not self.enable_long_term:
            return  # No-op if disabled
        full_key = self.LONG_PREFIX + key
        self.long_term.store(full_key, value, metadata)
    
    def search_long(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.enable_long_term:
            return []
        return self.long_term.search(query, limit)
    
    # Unified Helpers
    def clear_short(self) -> None:
        if hasattr(self.short_term, 'clear'):
            self.short_term.clear()
    
    def clear_long(self) -> None:
        if self.long_term and hasattr(self.long_term, 'clear'):
            self.long_term.clear()