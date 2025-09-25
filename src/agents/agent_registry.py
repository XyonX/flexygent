from typing import Dict, Type, Optional
from .base_agent import BaseAgent


class AgentRegistry:
    """Registry for agent types that can be instantiated from configurations."""
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        
    def register(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class with a specific type name."""
        self._agent_classes[agent_type] = agent_class
        
    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        """Get an agent class by its registered type name."""
        if agent_type not in self._agent_classes:
            raise ValueError(f"Agent type '{agent_type}' is not registered")
        return self._agent_classes[agent_type]
        
    def list_agent_types(self) -> list:
        """List all registered agent types."""
        return list(self._agent_classes.keys())

    def is_registered(self, agent_type: str) -> bool:
        """Check if an agent type is registered."""
        return agent_type in self._agent_classes


def register_builtin_agents(registry: AgentRegistry) -> None:
    """Register all built-in agent types with the registry."""
    # Import here to avoid circular imports
    from .tool_calling_agent import ToolCallingAgent, LLMToolAgent
    from .reasoning_tool_agent import ReasoningToolAgent
    from .adaptive_tool_agent import AdaptiveToolAgent
    from .general_tool_agent import GeneralToolAgent
    from .research_agent import ResearchAgent
    from .rag_agent import RAGAgent
    from .master_agent import MasterAgent
    
    # Register all available agent types
    registry.register('tool_calling', ToolCallingAgent)
    registry.register('llm_tool', LLMToolAgent)  # alias for compatibility
    registry.register('reasoning', ReasoningToolAgent)
    registry.register('adaptive', AdaptiveToolAgent)
    registry.register('general', GeneralToolAgent)
    registry.register('research', ResearchAgent)
    registry.register('rag', RAGAgent)
    registry.register('master', MasterAgent)