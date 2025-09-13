### Setup Sequence for the Flexygent Framework

The Flexygent system, as represented in the UML class diagram, is a modular framework for AI agents that requires a specific sequence of initialization steps to ensure all dependencies (e.g., LLM providers, tools, registries, memory, policies) are properly set up before handling user inputs. This sequence is derived from the class relationships and constructors in the diagram, where components like `AgentFactory` depend on registries, and agents depend on LLMs, tools, and other elements.

Below is the recommended **step-by-step setup sequence** for bootstrapping and running the system. This assumes you're implementing this in code (e.g., Python, based on the class signatures). The sequence starts from configuration loading and ends with processing user inputs. I've included rationale for each step, key classes involved, and example pseudo-code snippets for clarity.

#### 1. **Load Configurations**

- **Why First?**: Configurations (e.g., YAML files) are needed to initialize most components, such as LLM settings, tool policies, and agent types. This uses utilities from `config_loader.py`.
- **Key Classes Involved**: Utilities like `load_config()`, `get_openrouter_cfg()`, `get_llm_provider_cfg()`.
- **What to Do**: Merge default and custom configs, expanding environment variables.
- **Pseudo-Code Example**:

  ```
  from config_loader import load_config, get_openrouter_cfg

  config = load_config(paths=['config/default.yaml', 'config/custom.yaml'])
  llm_config = get_openrouter_cfg(config)
  ```

#### 2. **Create LLM Provider Instance**

- **Why Next?**: The LLM (e.g., `OpenRouterProvider`) is a core dependency for agents and orchestrators. It needs config details like API keys, models, and timeouts.
- **Key Classes Involved**: `OpenRouterProvider` (or `SimpleLLMProvider` for basic use), implementing `LLMProvider` and `ChatLLMProvider`.
- **What to Do**: Instantiate using the loaded config. If using a factory pattern, create via `from_config()`.
- **Pseudo-Code Example**:

  ```
  from providers import OpenRouterProvider

  llm_provider = OpenRouterProvider.from_config(llm_config)
  # Or manually: llm_provider = OpenRouterProvider(api_key='your_key', model='qwen/qwen3-coder:free')
  ```

#### 3. **Create Tool Registry and Register Tools**

- **Why Next?**: Tools (e.g., `EchoTool`, `AskUserTool`, `FetchTool`) must be registered before agents or orchestrators can use them. The `ToolRegistry` manages this.
- **Key Classes Involved**: `ToolRegistry`, `BaseTool` and its subclasses.
- **What to Do**: Instantiate the registry, then register individual tools or bulk-register them. Optionally filter by tags.
- **Pseudo-Code Example**:

  ```
  from tools import ToolRegistry, EchoTool, AskUserTool, FetchTool

  tool_registry = ToolRegistry()
  tools = [EchoTool(), AskUserTool(), FetchTool()]  # Instantiate concrete tools
  tool_registry.bulk_register(tools)
  ```

#### 4. **Create Agent Registry and Register Agent Classes**

- **Why Next?**: The `AgentRegistry` holds agent types (e.g., `ToolCallingAgent`), which the `AgentFactory` will use to create instances.
- **Key Classes Involved**: `AgentRegistry`, agent classes like `BaseAgent` or `ToolCallingAgent`.
- **What to Do**: Instantiate the registry and register available agent classes by type.
- **Pseudo-Code Example**:

  ```
  from agents import AgentRegistry, ToolCallingAgent

  agent_registry = AgentRegistry()
  agent_registry.register('tool_calling', ToolCallingAgent)
  ```

#### 5. **Create Memory Instances (Short-Term and Long-Term)**

- **Why Next?**: Memory is optional but often required for agents and orchestrators to maintain context. It depends on configs but not on other registries.
- **Key Classes Involved**: `AgentMemory`, `InMemoryShortTerm`, `FileLongTerm`.
- **What to Do**: Create short-term and long-term implementations, then wrap them in `AgentMemory`.
- **Pseudo-Code Example**:

  ```
  from memory import InMemoryShortTerm, FileLongTerm, AgentMemory

  short_term = InMemoryShortTerm(max_history_per_key=50)
  long_term = FileLongTerm(file_path='~/.flexygent/long_term_memory.json')
  agent_memory = AgentMemory(short_term=short_term, long_term=long_term, enable_long_term=True)
  ```

#### 6. **Create Tool Use Policy**

- **Why Next?**: The policy governs tool usage (e.g., autonomy levels) and is needed for orchestrators and agents.
- **Key Classes Involved**: `ToolUsePolicy`, `AutonomyLevel` enum.
- **What to Do**: Instantiate with desired settings from config.
- **Pseudo-Code Example**:

  ```
  from policy import ToolUsePolicy, AutonomyLevel

  policy = ToolUsePolicy(autonomy=AutonomyLevel.confirm, max_steps=8, allow_tools={'echo', 'fetch'})
  ```

#### 7. **Create UI Adapter**

- **Why Next?**: The UI handles user interactions (e.g., confirmations, prompts) and is a dependency for orchestrators and agents.
- **Key Classes Involved**: `UIAdapter` or `NoopUIAdapter`.
- **What to Do**: Use a no-op version for non-interactive setups or a custom implementation.
- **Pseudo-Code Example**:

  ```
  from ui import NoopUIAdapter

  ui_adapter = NoopUIAdapter()
  ```

#### 8. **Create Agent Factory**

- **Why Next?**: The factory depends on the registries (tools and agents) and is used to create agent instances.
- **Key Classes Involved**: `AgentFactory`, referencing `AgentRegistry` and `ToolRegistry`.
- **What to Do**: Pass in the registries (and optionally LLM factory if separate).
- **Pseudo-Code Example**:

  ```
  from agents import AgentFactory

  agent_factory = AgentFactory(agent_registry=agent_registry, tool_registry=tool_registry)
  ```

#### 9. **Create Tool Call Orchestrator**

- **Why Next?**: The orchestrator coordinates LLM-tool interactions and is often injected into agents. It depends on LLM, policy, UI, and (implicitly) tool registry.
- **Key Classes Involved**: `ToolCallOrchestrator`.
- **What to Do**: Instantiate with the LLM, policy, UI, and optional system prompt.
- **Pseudo-Code Example**:

  ```
  from orchestration import ToolCallOrchestrator

  orchestrator = ToolCallOrchestrator(llm=llm_provider, policy=policy, ui=ui_adapter, default_system_prompt='You are a helpful agent.')
  ```

#### 10. **Create Agent Instance**

- **Why Next?**: The agent (e.g., `ToolCallingAgent`) is the main runtime component. It depends on most prior elements: name/config, LLM, tools (via registry), memory, policy, UI, and orchestrator.
- **Key Classes Involved**: `BaseAgent` or `ToolCallingAgent`, created via `AgentFactory`.
- **What to Do**: Use the factory to create from config, file, or dict. For `ToolCallingAgent`, ensure it gets the orchestrator reference if needed.
- **Pseudo-Code Example**:
  ```
  agent_config = {'type': 'tool_calling', 'name': 'MyAgent', ...}  # From loaded config
  agent = agent_factory.create_from_dict(agent_config)
  # Manually: agent = ToolCallingAgent(name='MyAgent', config=config, llm=llm_provider, tools=tool_registry.list_tools(), memory=agent_memory, policy=policy, ui=ui_adapter, system_prompt='...')
  ```

#### 11. **Receive User Input and Process It**

- **Why Last?**: This is the runtime phase after setup. The agent is now fully initialized and ready to handle tasks.
- **Key Classes Involved**: `BaseAgent`/`ToolCallingAgent`, which calls `process_task(task: str)`.
- **What to Do**: In a loop or event handler, take user input (e.g., via console, API, or UI), pass it to the agent, and handle the output. This may involve internal calls to orchestrator, tools, memory, etc.
- **Pseudo-Code Example**:
  ```
  while True:
      user_input = input("Enter your task: ")  # Or from API/UI
      if user_input.lower() == 'exit':
          break
      response = agent.process_task(user_input)
      print("Response:", response)
      # Optionally update memory or emit events via UIAdapter
  ```

### Additional Notes on the Setup Sequence

- **Dependencies and Rationale**: The order ensures acyclic dependencies (e.g., registries before factories, LLM before agents). From the UML, composition (`*--`) and dependency (`..>`) relationships dictate this flow—e.g., `AgentFactory` composes registries, and `ToolCallingAgent` depends on `ToolCallOrchestrator`.
- **Customization**: If not using tools, skip steps 3 and 6. For minimal setups, use defaults (e.g., no long-term memory).
- **Error Handling**: Add checks after each step (e.g., validate config, ensure registrations succeed).
- **Runtime Loop**: After setup, the system enters a processing loop where user inputs trigger agent methods, potentially looping internally (e.g., via orchestrator's `max_steps`).
- **Scalability**: For production, wrap this in a main script or app entry point. Registries allow dynamic additions (e.g., register new tools at runtime).

This sequence should get the framework up and running end-to-end. If you need code examples for a specific language or more details on any step, let me know!
