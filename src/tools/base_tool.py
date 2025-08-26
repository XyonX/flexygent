

import abc
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, Set, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError


# Type parameters for input/output models
TIn = TypeVar("TIn", bound=BaseModel)
TOut = TypeVar("TOut", bound=BaseModel)


class ToolExecutionError(Exception):
    """Raised when a tool fails during execution."""

    def __init__(self, message: str, *, cause: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.cause = cause


# fronzen to true means we can reassign the var later
@dataclass(frozen=True)
class ToolDescriptor:
    """
    A lightweight descriptor for discovery/registration and for exposing to the LLM/router.
    """
    name: str
    description: str
    tags: Set[str]
    requires_network: bool
    requires_filesystem: bool
    timeout_seconds: Optional[float]
    max_concurrency: Optional[int]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

class BaseTool(Generic[TIn, TOut], metaclass=abc.ABCMeta):

    """
    Base class for all tools.

    Key features:
    - Strongly typed input/output via Pydantic models
    - Automatic input validation
    - Optional timeout enforcement
    - Optional concurrency limits
    - JSON schema exposure for function-calling/tool-calling LLMs

    """

    name:str
    description: str
    input_model: Type[TIn]
    output_model: Type[TOut]

    # Operational knobs
    timeout_seconds: Optional[float] = 30.0
    max_concurrency: Optional[int] = None  # None means unlimited
    requires_network: bool = False
    requires_filesystem: bool = False
    tags: Set[str] = frozenset()

    def __init__(self) -> None:
        if not getattr(self, "name", None):
            raise ValueError(f"{self.__class__.__name__} must define a non-empty 'name'.")
        if not getattr(self, "description", None):
            raise ValueError(f"{self.__class__.__name__} must define a non-empty 'description'.")
        if not getattr(self, "input_model", None) or not issubclass(self.input_model, BaseModel):
            raise ValueError(f"{self.__class__.__name__} must define 'input_model' as a Pydantic BaseModel subclass.")
        if not getattr(self, "output_model", None) or not issubclass(self.output_model, BaseModel):
            raise ValueError(f"{self.__class__.__name__} must define 'output_model' as a Pydantic BaseModel subclass.")

        self._semaphore: Optional[asyncio.Semaphore] = (
            asyncio.Semaphore(self.max_concurrency) if self.max_concurrency and self.max_concurrency > 0 else None
        )

        # Public API ---------------------------------------------------------------

    def get_schema(self) -> Dict[str, Any]:
        """
        Return a JSON-compatible schema describing this tool and its I/O contracts.
        Suitable for LLM tool/function-calling.
        """
        # Pydantic v2 uses model_json_schema()
        input_schema = self.input_model.model_json_schema()
        output_schema = self.output_model.model_json_schema()
        return {
            "name": self.name,
            "description": self.description,
            "parameters": input_schema,
            "returns": output_schema,
            "requires_network": self.requires_network,
            "requires_filesystem": self.requires_filesystem,
            "timeout_seconds": self.timeout_seconds,
            "max_concurrency": self.max_concurrency,
            "tags": sorted(self.tags),
        }


    def to_descriptor(self) -> ToolDescriptor:
            """Return a ToolDescriptor for registry/discovery."""
            return ToolDescriptor(
                name=self.name,
                description=self.description,
                tags=set(self.tags),
                requires_network=self.requires_network,
                requires_filesystem=self.requires_filesystem,
                timeout_seconds=self.timeout_seconds,
                max_concurrency=self.max_concurrency,
                input_schema=self.input_model.model_json_schema(),
                output_schema=self.output_model.model_json_schema(),
            )

    async def __call__(self, data: Union[Dict[str, Any], TIn], *, context: Optional[Dict[str, Any]] = None) -> TOut:
        """
        Validate input and execute with timeout and concurrency controls.
        'context' can carry request_id, auth, tracing, budgets, etc.
        """
        params = self._validate_input(data)

        async def _run() -> TOut:
            return await self._execute_with_handling(params, context=context)

        # Concurrency limit if configured
        if self._semaphore is not None:
            async with self._semaphore:
                return await self._maybe_timeout(_run)
        else:
            return await self._maybe_timeout(_run)

    # To be implemented by subclasses -----------------------------------------

    @abc.abstractmethod
    async def execute(self, params: TIn, *, context: Optional[Dict[str, Any]] = None) -> TOut:
        """
        Implement the actual tool logic.
        Must be async. Use 'context' for cross-cutting concerns (e.g., tracing, budgets).
        """
        raise NotImplementedError

    # Helpers ------------------------------------------------------------------

    def _validate_input(self, data: Union[Dict[str, Any], TIn]) -> TIn:
        if isinstance(data, self.input_model):
            return data
        if isinstance(data, dict):
            try:
                return self.input_model.model_validate(data)
            except ValidationError as ve:
                raise ToolExecutionError(f"Invalid input for tool '{self.name}': {ve}") from ve
        raise ToolExecutionError(
            f"Invalid input type for tool '{self.name}': expected dict or {self.input_model.__name__}, got {type(data)}"
        )

    async def _execute_with_handling(self, params: TIn, *, context: Optional[Dict[str, Any]]) -> TOut:
        try:
            result = await self.execute(params, context=context)
        except ToolExecutionError:
            # Re-raise explicit tool errors unchanged
            raise
        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"Tool '{self.name}' failed: {e}", cause=e) from e

        # Validate output against declared output_model
        try:
            if isinstance(result, self.output_model):
                return result
            # Support returning a dict which we then validate/coerce
            if isinstance(result, dict):
                return self.output_model.model_validate(result)
        except ValidationError as ve:
            raise ToolExecutionError(f"Invalid output from tool '{self.name}': {ve}") from ve

        raise ToolExecutionError(
            f"Invalid output type from tool '{self.name}': expected dict or {self.output_model.__name__}, got {type(result)}"
        )

    async def _maybe_timeout(self, coro_factory) -> TOut:
        if self.timeout_seconds is None or self.timeout_seconds <= 0:
            return await coro_factory()
        try:
            return await asyncio.wait_for(coro_factory(), timeout=self.timeout_seconds)
        except asyncio.TimeoutError as te:
            raise ToolExecutionError(f"Tool '{self.name}' timed out after {self.timeout_seconds}s") from te



    






