from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

 
@runtime_checkable
class LLMProvider(Protocol):
    """Protocol describing the minimal LLM interface expected by agents."""

    def send_message(self, message: str) -> Any: ...

    def stream_message(self, message: str) -> Any: ...


@runtime_checkable
class MemoryStore(Protocol):
    """Protocol describing the minimal memory interface expected by agents."""

    def store(self, key: str, value: Any) -> None: ...

    def retrieve(self, key: str) -> Any: ...

    def update(self, key: str, value: Any) -> None: ...


class BaseAgent(ABC):
    """Abstract base class for agents.

    Subclasses must implement `process_task` and `handle_tool_calls`.
    A default `update_memory` helper is provided and will no-op when no
    memory implementation is supplied.
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[Any]] = None,
        memory: Optional[MemoryStore] = None,
        registry:Optional[Any]=None
    ) -> None:
        """Initialize common agent state.

        Args:
            name: Human-readable agent identifier.
            config: Agent-specific configuration mapping.
            llm: Object implementing the `LLMProvider` protocol.
            tools: List of tools available to the agent.
            memory: Optional object implementing `MemoryStore` protocol.
        """
        self.name = name
        self.config = config
        self.llm = llm
        self.tools = tools or []
        self.memory = memory
        self.registry=registry

    @abstractmethod
    def process_task(self, task: str) -> Any:
        """Process a task using the LLM and return a response.

        Implementations should use `self.llm` (if provided) to interact with
        the configured language model.
        """
        raise NotImplementedError

    @abstractmethod
    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        """Execute a named tool with the given payload and return the result."""
        raise NotImplementedError

    def update_memory(self, key: str, value: Any) -> None:
        """Persist data to the agent's memory if available (no-op otherwise)."""
        if self.memory is not None:
            self.memory.store(key, value)





