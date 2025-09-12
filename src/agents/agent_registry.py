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