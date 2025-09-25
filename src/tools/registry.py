from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from pydantic import BaseModel

from .base_tool import BaseTool, ToolDescriptor
import logging

# Configure logging once at the top of your project
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ToolAlreadyRegisteredError(Exception):
    pass


class ToolNotFoundError(Exception):
    pass


class ToolRegistry:
    """
    Central registry for discovering and managing tools.

    Responsibilities:
    - Register tool instances (unique by name)
    - Retrieve a tool by name
    - List tools with optional tag filtering
    - Provide JSON schemas for LLM tool/function-calling
    - Resolve tools available to a given agent based on a simple policy mapping

    Usage patterns:
    - Register at startup with concrete tool instances.
    - Agents/coordinator query registry for tools and their schemas.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    # Registration --------------------------------------------------------------

    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool instance by its unique name."""
        name = tool.name
        if name in self._tools:
            logging.warning(f"Attempted to register '{name}', but it's already registered.")
            raise ToolAlreadyRegisteredError(f"Tool '{name}' is already registered.")
        self._tools[name] = tool
        logging.info(f"Tool '{name}' registered successfully.")


    def bulk_register(self, tools: Iterable[BaseTool]) -> None:
        """Register multiple tools; fails fast on duplicates."""
        for t in tools:
            self.register_tool(t)

    # Lookup -------------------------------------------------------------------

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by its unique name."""
        try:
            return self._tools[name]
        except KeyError as e:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.") from e

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    # Listing and metadata ------------------------------------------------------

    def list_tool_names(self, *, tags: Optional[Set[str]] = None) -> List[str]:
        """
        List tool names; optionally filter by tags (tool must include all provided tags).
        """
        if tags:
            return sorted(
                name
                for name, tool in self._tools.items()
                if tags.issubset(set(tool.tags))
            )
        return sorted(self._tools.keys())

    def list_tools(self, *, tags: Optional[Set[str]] = None) -> List[BaseTool]:
        """List tool instances, optionally filtered by tags."""
        if tags:
            return [
                tool for tool in self._tools.values()
                if tags.issubset(set(tool.tags))
            ]
        return list(self._tools.values())

    def list_descriptors(self, *, tags: Optional[Set[str]] = None) -> List[ToolDescriptor]:
        """Return lightweight descriptors suitable for discovery and UIs."""
        return [t.to_descriptor() for t in self.list_tools(tags=tags)]

    def get_llm_function_specs(self, *, tool_names: Optional[Sequence[str]] = None) -> List[dict]:
        """
        Return an array of JSON-compatible tool/function specifications for LLMs.
        If tool_names is provided, restrict to that subset (error on unknown).
        """
        tools: List[BaseTool]
        if tool_names is None:
            tools = list(self._tools.values())
        else:
            tools = [self.get_tool(n) for n in tool_names]
        return [t.get_schema() for t in tools]

    # Agent policy resolution ---------------------------------------------------

    def get_tools_for_agent(
        self,
        agent_name: str,
        *,
        policy: Optional[Dict[str, Sequence[str]]] = None,
        fallback_tags: Optional[Set[str]] = None,
    ) -> List[BaseTool]:
        """
        Determine which tools an agent can use.

        - If 'policy' is provided (mapping agent_name -> allowed tool names),
          return those tools (error if any are not registered).
        - Else if 'fallback_tags' provided, return tools that match tags.
        - Else return all tools (you may want to restrict this in production).
        """
        if policy and agent_name in policy:
            names = policy[agent_name]
            return [self.get_tool(n) for n in names]

        if fallback_tags:
            return self.list_tools(tags=fallback_tags)

        return list(self._tools.values())


# A global registry instance you can import
registry = ToolRegistry()


# def load_builtin_tools() -> None:
#     """
#     Import modules that auto-register their tools at import time.
#     Call this during app startup if you want built-ins available.
#     """
#     # System tools
#     from .system import echo  # noqa: F401  # side-effect: registers echo tool