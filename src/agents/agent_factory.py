from typing import Dict, Type, Any, Optional
import json
import yaml
from pathlib import Path

from .agent_config import AgentConfig
from .base_agent import BaseAgent
from .agent_registry import AgentRegistry
from .tool_registry import ToolRegistry
from .llm import LLMFactory

class AgentFactory:
    def __init__(self, agent_registry=None, tool_registry=None):
        self.agent_registry = agent_registry or AgentRegistry()
        self.tool_registry = tool_registry or ToolRegistry()
        self.llm_factory = LLMFactory()
    
    def create_from_config(self, config: AgentConfig) -> BaseAgent:
        """Create an agent instance from a configuration object."""
        # Get the appropriate agent class from the registry
        agent_class = self.agent_registry.get_agent_class(config.agent_type)
        
        # Set up the LLM
        llm = self.llm_factory.create_llm(config.llm_config)
        
        # Set up the tools
        tools = []
        for tool_name in config.tools:
            tool_config = config.tool_configs.get(tool_name, None)
            tool = self.tool_registry.get_tool(tool_name)
            if tool and (tool_config is None or tool_config.enabled):
                tools.append(tool)
        
        # Create the agent instance
        agent = agent_class(
            agent_id=config.agent_id,
            name=config.agent_name,
            system_prompt=config.system_prompt,
            llm=llm,
            tools=tools,
            max_tool_calls=config.max_tool_calls,
            memory_enabled=config.memory_enabled,
            memory_config=config.memory_config,
            **config.additional_params
        )
        
        return agent
    
    def create_from_file(self, file_path: str) -> BaseAgent:
        """Create an agent instance from a configuration file (JSON or YAML)."""
        path = Path(file_path)
        
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                config_data = json.load(f)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        config = AgentConfig(**config_data)
        return self.create_from_config(config)
    
    def create_from_dict(self, config_dict: Dict[str, Any]) -> BaseAgent:
        """Create an agent instance from a configuration dictionary."""
        config = AgentConfig(**config_dict)
        return self.create_from_config(config)