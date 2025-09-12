# Agent Configuration System Design for Flexygent

## Overview of the Proposed Design

The core idea is to create a configuration-based system that allows you to:
1. Define agent configurations in JSON/YAML
2. Have factory classes that instantiate agents based on these configurations
3. Maintain a registry of agent types that can be referenced

Here's a high-level architecture diagram of the proposed system:

```
                      ┌─────────────────┐
                      │  Configuration  │
                      │  (JSON/YAML)    │
                      └────────┬────────┘
                               │
                               ▼
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Agent     │◄──────┤  Agent Factory  ├───────►   Agent Registry │
│  Instance   │       └─────────────────┘       └─────────────────┘
└─────────────┘                │                         │
                               │                         │
                               ▼                         ▼
                     ┌─────────────────┐       ┌─────────────────┐
                     │    Base Agent   │       │  Tool Registry  │
                     │     Classes     │       └─────────────────┘
                     └─────────────────┘
```

## Key Components to Implement

Let's design the following components:

### 1. Agent Configuration Schema

```python name=agent_config.py
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    tool_name: str
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key_env: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)

class AgentConfig(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str  # Reference to a base agent type in registry
    description: Optional[str] = None
    system_prompt: str
    tools: List[str] = Field(default_factory=list)  # List of tool names to use
    tool_configs: Dict[str, ToolConfig] = Field(default_factory=dict)  # Tool-specific configurations
    max_tool_calls: int = 5
    llm_config: LLMConfig
    memory_enabled: bool = True
    memory_config: Dict[str, Any] = Field(default_factory=dict)
    additional_params: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Agent Factory

```python name=agent_factory.py
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
```

### 3. Agent Registry

```python name=agent_registry.py
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
```

### 4. Example Specialized Agents for Registration

```python name=specialized_agents.py
from .base_agent import BaseAgent
from .agent_registry import AgentRegistry

class ToolCallingAgent(BaseAgent):
    """Agent specialized for optimal tool calling capabilities."""
    
    def __init__(self, agent_id, name, system_prompt, llm, tools=None, max_tool_calls=5, **kwargs):
        # Enhanced prompt that emphasizes proper tool usage
        tool_focused_prompt = (
            f"{system_prompt}\n\n"
            f"You have access to tools that can help you complete tasks. "
            f"Always consider if a tool would help solve the problem before answering. "
            f"You may use up to {max_tool_calls} tool calls per conversation."
        )
        super().__init__(
            agent_id=agent_id, 
            name=name,
            system_prompt=tool_focused_prompt,
            llm=llm,
            tools=tools,
            max_tool_calls=max_tool_calls,
            **kwargs
        )

class LocalAgent(BaseAgent):
    """Agent optimized for local execution with reduced API calls."""
    
    def __init__(self, agent_id, name, system_prompt, llm, tools=None, max_tool_calls=3, **kwargs):
        # Configure for more conservative resource usage
        local_prompt = (
            f"{system_prompt}\n\n"
            f"You are optimized for local execution. Be concise and minimize resource usage."
        )
        super().__init__(
            agent_id=agent_id, 
            name=name,
            system_prompt=local_prompt,
            llm=llm,
            tools=tools,
            max_tool_calls=max_tool_calls,
            **kwargs
        )
        # Override default behaviors to optimize for local execution
        self.streaming_enabled = kwargs.get('streaming_enabled', False)
        self.batch_tool_calls = True

class CloudAgent(BaseAgent):
    """Agent optimized for cloud deployment with scalability features."""
    
    def __init__(self, agent_id, name, system_prompt, llm, tools=None, max_tool_calls=10, **kwargs):
        cloud_prompt = (
            f"{system_prompt}\n\n"
            f"You are running in a cloud environment with access to more computational resources."
        )
        super().__init__(
            agent_id=agent_id, 
            name=name,
            system_prompt=cloud_prompt,
            llm=llm,
            tools=tools,
            max_tool_calls=max_tool_calls,
            **kwargs
        )
        # Configure for cloud optimizations
        self.streaming_enabled = kwargs.get('streaming_enabled', True)
        self.parallel_tool_execution = kwargs.get('parallel_tool_execution', True)


def register_specialized_agents(registry: AgentRegistry):
    """Register all specialized agents with the registry."""
    registry.register("tool_calling", ToolCallingAgent)
    registry.register("local", LocalAgent)
    registry.register("cloud", CloudAgent)
```

### 5. Main CLI Integration

```python name=main.py
#!/usr/bin/env python
import argparse
import os
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any

from flexygent.agent_factory import AgentFactory
from flexygent.agent_registry import AgentRegistry
from flexygent.tool_registry import ToolRegistry
from flexygent.specialized_agents import register_specialized_agents

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file."""
    path = Path(config_path)
    
    if not path.exists():
        print(f"Error: Config file {config_path} not found")
        sys.exit(1)
        
    try:
        if path.suffix.lower() == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        else:
            print(f"Error: Unsupported config format: {path.suffix}")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="FlexyGent CLI - Flexible Agent Framework")
    
    # Main command groups
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Agent operations")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command", help="Agent command")
    
    # Run agent command
    run_parser = agent_subparsers.add_parser("run", help="Run an agent")
    run_parser.add_argument("config", help="Path to agent configuration file (JSON or YAML)")
    run_parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    # List agent types command
    list_parser = agent_subparsers.add_parser("list", help="List available agent types")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up registries
    agent_registry = AgentRegistry()
    tool_registry = ToolRegistry()
    
    # Register specialized agents
    register_specialized_agents(agent_registry)
    
    # Register available tools (this would come from your tool implementation)
    # register_tools(tool_registry)
    
    # Create agent factory
    factory = AgentFactory(agent_registry=agent_registry, tool_registry=tool_registry)
    
    # Execute command
    if args.command == "agent":
        if args.agent_command == "run":
            config_data = load_config(args.config)
            agent = factory.create_from_dict(config_data)
            
            if args.interactive:
                print(f"Running agent '{agent.name}' in interactive mode. Type 'exit' to quit.")
                while True:
                    user_input = input("> ")
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    response = agent.process_message(user_input)
                    print(response)
            else:
                # Non-interactive mode would typically be used with API or other integration
                print(f"Agent '{agent.name}' initialized. Use with API or other integration.")
                
        elif args.agent_command == "list":
            agent_types = agent_registry.list_agent_types()
            print("Available agent types:")
            for agent_type in agent_types:
                print(f"- {agent_type}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

### 6. Example Configuration File

```yaml name=example_agent.yaml
agent_id: "assistant_001"
agent_name: "General Assistant"
agent_type: "tool_calling"
description: "A general-purpose assistant with tool-calling capabilities"
system_prompt: "You are a helpful AI assistant that can use tools to answer questions and solve problems."
tools:
  - "web_search"
  - "calculator"
  - "weather_api"
tool_configs:
  web_search:
    tool_name: "web_search"
    enabled: true
    parameters:
      search_engine: "google"
      max_results: 5
  calculator:
    tool_name: "calculator"
    enabled: true
  weather_api:
    tool_name: "weather_api"
    enabled: true
    parameters:
      api_key_env: "WEATHER_API_KEY"
max_tool_calls: 5
llm_config:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2048
memory_enabled: true
memory_config:
  type: "conversation_buffer"
  max_messages: 10
```

## Benefits of This Design

1. **Flexibility**: Agents can be defined in configuration files without code changes
2. **Reusability**: Base agent types provide specialized behavior that can be reused
3. **Maintainability**: Clear separation between agent configuration and implementation
4. **Extensibility**: Easy to add new agent types or tools
5. **Consistency**: Standardized approach to agent creation
6. **Testability**: Easy to create test configurations and mock components

## Implementation Steps

1. Start by implementing the core classes (`AgentConfig`, `AgentFactory`, `AgentRegistry`)
2. Update your existing base agent class to work with this configuration system
3. Implement the specialized agent types 
4. Update the main CLI to use the factory pattern
5. Create example configuration files
6. Add documentation on how to create new agent configurations

This approach will give you a much more flexible system where you can create many agent instances with different capabilities without having to write new agent classes for each variation.