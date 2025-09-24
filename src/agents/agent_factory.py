# from typing import Dict, Type, Any, Optional
# import json
# import yaml
# from pathlib import Path

# from .agent_config import AgentConfig
# from .base_agent import BaseAgent
# from .agent_registry import AgentRegistry
# from .tool_registry import ToolRegistry
# from .llm import LLMFactory

# class AgentFactory:
#     def __init__(self, agent_registry=None, tool_registry=None):
#         self.agent_registry = agent_registry or AgentRegistry()
#         self.tool_registry = tool_registry or ToolRegistry()
#         self.llm_factory = LLMFactory()
    
#     def create_from_config(self, config: AgentConfig) -> BaseAgent:
#         """Create an agent instance from a configuration object."""
#         # Get the appropriate agent class from the registry
#         agent_class = self.agent_registry.get_agent_class(config.agent_type)
        
#         # Set up the LLM
#         llm = self.llm_factory.create_llm(config.llm_config)
        
#         # Set up the tools
#         tools = []
#         for tool_name in config.tools:
#             tool_config = config.tool_configs.get(tool_name, None)
#             tool = self.tool_registry.get_tool(tool_name)
#             if tool and (tool_config is None or tool_config.enabled):
#                 tools.append(tool)
        
#         # Create the agent instance
#         agent = agent_class(
#             agent_id=config.agent_id,
#             name=config.agent_name,
#             system_prompt=config.system_prompt,
#             llm=llm,
#             tools=tools,
#             max_tool_calls=config.max_tool_calls,
#             memory_enabled=config.memory_enabled,
#             memory_config=config.memory_config,
#             **config.additional_params
#         )
        
#         return agent
    
#     def create_from_file(self, file_path: str) -> BaseAgent:
#         """Create an agent instance from a configuration file (JSON or YAML)."""
#         path = Path(file_path)
        
#         if path.suffix.lower() == '.json':
#             with open(path, 'r') as f:
#                 config_data = json.load(f)
#         elif path.suffix.lower() in ['.yml', '.yaml']:
#             with open(path, 'r') as f:
#                 config_data = yaml.safe_load(f)
#         else:
#             raise ValueError(f"Unsupported file format: {path.suffix}")
        
#         config = AgentConfig(**config_data)
#         return self.create_from_config(config)
    
#     def create_from_dict(self, config_dict: Dict[str, Any]) -> BaseAgent:
#         """Create an agent instance from a configuration dictionary."""
#         config = AgentConfig(**config_dict)
#         return self.create_from_config(config)


from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional, Type

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Optional dependency

from .base_agent import BaseAgent, LLMProvider, MemoryStore
from .tool_calling_agent import ToolCallingAgent, LLMToolAgent
from .reasoning_tool_agent import ReasoningToolAgent
from .adaptive_tool_agent import AdaptiveToolAgent
from .general_tool_agent import GeneralToolAgent
from ..tools.registry import registry
from ..orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel
from ..orchestration.tool_call_orchestrator import UIAdapter


AgentClass = Type[BaseAgent]


class AgentFactory:
    """
    Factory to create agents from JSON/YAML configs.

    External integration points:
      - provider_resolver(llm_cfg) -> LLMProvider
      - memory_resolver(mem_cfg) -> MemoryStore
      - ui_resolver(ui_cfg) -> UIAdapter

    Example top-level config schema:
      name: "researcher"
      type: "reasoning"   # "tool-calling" | "reasoning" | "adaptive" | "general" | "llm-tool" (alias)
      llm:
        provider: "openrouter"
        model: "openai/gpt-4o"
        # ... anything your resolver needs ...
      memory:
        type: "redis"
        url: "redis://localhost:6379/0"
      ui:
        kind: "cli"
      tools:
        allowlist: ["web_search", "code_run"]
      policy:
        autonomy: "auto"  # "manual" | "assisted" | "auto"
        max_steps: 8
      prompts:
        system: "Domain specific instructions..."
      reasoning:
        mode: "plan-act-reflect"
        plan_depth: 2
        reflection: true
      config:
        temperature: 0.3
        max_tokens: 2000
    """

    TYPE_MAP: Dict[str, AgentClass] = {
        "tool-calling": ToolCallingAgent,
        "llm-tool": LLMToolAgent,        # alias/compat
        "reasoning": ReasoningToolAgent,
        "adaptive": AdaptiveToolAgent,
        "general": GeneralToolAgent,
    }

    def __init__(
        self,
        *,
        provider_resolver: Callable[[Dict[str, Any]], LLMProvider],
        memory_resolver: Optional[Callable[[Dict[str, Any]], MemoryStore]] = None,
        ui_resolver: Optional[Callable[[Dict[str, Any]], UIAdapter]] = None,
    ) -> None:
        self._provider_resolver = provider_resolver
        self._memory_resolver = memory_resolver
        self._ui_resolver = ui_resolver

    # --------------------------- Public API -----------------------------------

    def from_file(self, path: str) -> BaseAgent:
        cfg = self._load(path)
        return self.from_config(cfg)

    def from_config(self, cfg: Dict[str, Any]) -> BaseAgent:
        agent_type = str(cfg.get("type", "tool-calling")).lower()
        name = str(cfg.get("name", "agent"))

        agent_cls = self.TYPE_MAP.get(agent_type)
        if not agent_cls:
            raise ValueError(f"Unknown agent type: {agent_type}. Supported: {list(self.TYPE_MAP)}")

        llm_cfg = cfg.get("llm") or {}
        mem_cfg = cfg.get("memory")
        ui_cfg = cfg.get("ui")

        llm = self._provider_resolver(llm_cfg)
        memory = self._memory_resolver(mem_cfg) if (self._memory_resolver and mem_cfg) else None
        ui = self._ui_resolver(ui_cfg) if (self._ui_resolver and ui_cfg) else None

        tools_cfg = (cfg.get("tools") or {})
        allowlist = tools_cfg.get("allowlist")
        tools = None
        # Optionally resolve tool objects if tool params are configured at creation time
        # Otherwise, let the agent resolve with allowlist or default to registry
        if isinstance(allowlist, list) and tools_cfg.get("resolve_objects"):
            tools = [registry.get_tool(n) for n in allowlist if registry.has_tool(n)]

        prompts_cfg = (cfg.get("prompts") or {})
        system_prompt = prompts_cfg.get("system")

        policy_cfg = (cfg.get("policy") or {})
        autonomy = str(policy_cfg.get("autonomy", "auto")).lower()
        autonomy_map = {
            "manual": AutonomyLevel.manual,
            "assisted": AutonomyLevel.assisted,
            "auto": AutonomyLevel.auto,
        }
        policy = ToolUsePolicy(
            autonomy=autonomy_map.get(autonomy, AutonomyLevel.auto),
            max_steps=int(policy_cfg.get("max_steps", 6)),
        )

        # Merge agent-specific configuration under "config" plus any top-level known knobs
        agent_config = dict(cfg.get("config") or {})
        # Smooth common knobs
        if "temperature" in cfg:
            agent_config["temperature"] = cfg["temperature"]
        if "max_tokens" in cfg:
            agent_config["max_tokens"] = cfg["max_tokens"]
        # Include reasoning/adaptation params; subclasses can read from self.config
        if "reasoning" in cfg:
            agent_config["reasoning"] = cfg["reasoning"]
        if "adaptation" in cfg:
            agent_config["adaptation"] = cfg["adaptation"]

        # Construct the agent
        agent = agent_cls(
            name=name,
            config=agent_config,
            llm=llm,
            tools=tools,
            memory=memory,
            policy=policy,
            ui=ui,
            system_prompt=system_prompt,
            tool_allowlist=allowlist if tools is None else None,
        )

        return agent

    # --------------------------- Helpers --------------------------------------

    @staticmethod
    def _load(path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        _, ext = os.path.splitext(path.lower())
        with open(path, "r", encoding="utf-8") as f:
            if ext in (".yaml", ".yml"):
                if not yaml:
                    raise RuntimeError("PyYAML is not installed. Install pyyaml to load YAML configs.")
                return yaml.safe_load(f)  # type: ignore
            elif ext == ".json":
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file extension: {ext}. Use .yaml/.yml or .json")