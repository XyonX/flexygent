# Quick Class Summaries for Flexygent

High-level overview: Flexygent is an agent-based system for LLM-driven tasks, focusing on tool calling, policy enforcement, and UI interaction. Core flow: User task → ToolCallingAgent (inherits BaseAgent) → LLM processing (via LLMProvider/ChatLLMProvider implementations like OpenRouterProvider) → Tool execution (with policy checks) → UI confirmation if needed → Memory update.

## LLMProvider (Protocol/Interface)
- **Purpose**: Minimal interface for basic LLM interactions (simple message sending/streaming). Used by BaseAgent for non-chat, non-tool scenarios.
- **Key Methods** (all abstract):
  - `send_message(message: str) -> Any`: Send a single message and get response.
  - `stream_message(message: str) -> Iterable[Any]`: Stream response chunks.
- **Usage**: Implemented by providers like SimpleLLMProvider or OpenRouterProvider; injected into agents.

## ChatLLMProvider (Protocol/Interface)
- **Purpose**: Advanced interface for conversational LLMs with tool-calling support (OpenAI-compatible API). Enables multi-turn chats and function/tool calls.
- **Key Methods** (all abstract):
  - `chat(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, tool_choice: Optional[Any] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, extra_headers: Optional[Dict[str, str]] = None, timeout: Optional[float] = None) -> Dict[str, Any]`: Full chat completion with optional tools.
  - `stream_chat(...) -> Iterable[Any]`: Streaming version of chat.
- **Usage**: Used by ToolCallingAgent; implemented by OpenAI-compatible providers like OpenRouterProvider.

## SimpleLLMProvider (Concrete Class, Implements LLMProvider)
- **Purpose**: Basic, local/testing implementation of LLMProvider. Simulates responses by truncating/echoing input (no real API calls). Useful for development without external dependencies.
- **Key Attributes**:
  - `max_output_chars`: int (default 800) - Limit on simulated response length.
- **Key Methods**:
  - `__init__(max_output_chars: int = 800)`: Sets truncation limit.
  - `send_message(message: str) -> str`: Echoes truncated message with "[SimpleLLM summary]" prefix.
  - `stream_message(message: str) -> Generator[str, None, None]`: Yields small chunks of the simulated response.
- **Usage**: Replace with real providers in production; for quick prototyping.

## OpenRouterProvider (Concrete Class, Implements LLMProvider & ChatLLMProvider)
- **Purpose**: Wrapper for OpenRouter API (OpenAI-compatible endpoints). Handles config loading (env vars, files), API calls for chat/tool-calling, and streaming. Currently in use; has config loading bugs to refactor later. Generalizes OpenAI-compatible providers (OpenRouter uses OpenAI client under the hood).
- **Key Attributes**:
  - `client`: OpenAI - Internal OpenAI client instance.
  - `model`: str (default "qwen/qwen3-coder:free") - LLM model.
  - `system_prompt`: Optional[str] - Global system instructions.
  - `temperature`: float (default 0.2) - Sampling temperature.
  - `max_tokens`: Optional[int] - Max output tokens.
  - `request_timeout`: float (default 60.0) - API timeout.
  - `extra_headers`: Dict[str, str] - Attribution/ custom headers (e.g., for OpenRouter).
- **Key Methods**:
  - `__init__(api_key: Optional[str] = None, base_url: Optional[str] = None, ...)`: Initializes with env fallback (OPENAI_API_KEY, OPENAI_BASE_URL); raises if no key.
  - `from_config(cfg: Dict[str, object]) -> OpenRouterProvider`: Builds from config dict (YAML/JSON), with env precedence and fallbacks.
  - `send_message(message: str) -> str`: Simple user message via chat API.
  - `stream_message(message: str) -> Iterable[str]`: Streaming simple message.
  - `chat(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, ... ) -> Dict[str, Any]`: Full chat with tools (OpenAI format).
  - `stream_chat(...) -> Iterable[Any]`: Streaming chat with tools.
- **Usage**: Primary provider; config via env (OPENAI_API_KEY, etc.) or from_config. OpenRouter-specific (base_url: https://openrouter.ai/api/v1); refactor for general OpenAI support later.

## BaseAgent (Abstract Base Class)
- **Purpose**: Foundation for all agents. Manages common state (name, config, LLM, tools, memory, registry) and provides hooks for task processing, tool handling, and memory updates. Subclasses must implement core logic.
- **Key Attributes**:
  - `name`: str - Agent identifier.
  - `config`: Dict[str, Any] - Agent-specific settings.
  - `llm`: Optional[LLMProvider] - Language model interface.
  - `tools`: List[Any] - Available tools.
  - `memory`: Optional[MemoryStore] - Persistent storage (e.g., key-value).
  - `registry`: Optional[Any] - Tool/agent registry.
- **Key Methods**:
  - `__init__(...)`: Initializes state.
  - `process_task(task: str) -> Any` (abstract): Handles main task via LLM.
  - `handle_tool_calls(tool_name: str, payload: Dict) -> Any` (abstract): Executes tools.
  - `update_memory(key: str, value: Any)`: Stores/retrieves from memory (no-op if none).
- **Usage**: Extended by specialized agents like ToolCallingAgent.

## AutonomyLevel (Enum)
- **Purpose**: Defines tool execution autonomy levels for policies.
- **Values**:
  - `auto`: Run tools without confirmation.
  - `confirm`: Ask user (all or specific tools).
  - `never`: Hide tools from LLM (no execution).
- **Notes**: Controls safety/trust in tool calls; used in ToolUsePolicy.

## ToolUsePolicy (Dataclass)
- **Purpose**: Configures safe, bounded tool usage (limits, permissions). Enforces autonomy and prevents abuse (e.g., infinite loops).
- **Key Attributes**:
  - `autonomy`: AutonomyLevel - Execution mode.
  - `allow_tools`: Optional[Set[str]] - Whitelist of permitted tools.
  - `deny_tools`: Set[str] - Blacklist.
  - `confirm_tools`: Set[str] - Tools needing confirmation (if autonomy=confirm; empty = all).
  - `max_steps`: int (default 8) - Max reasoning steps.
  - `max_tool_calls`: Optional[int] - Total tool call limit.
  - `parallel_tool_calls`: bool (default True) - Allow concurrent calls.
  - `tool_result_truncate`: int (default 8000) - Cap tool output length.
  - `max_wall_time_s`: Optional[float] - Time budget.
- **Key Methods**:
  - `__init__(...)`: Sets defaults.
  - `__post_init__()`: Optional validation (e.g., check conflicts).
- **Usage**: Passed to agents for runtime enforcement.

## UIAdapter (Protocol/Abstract Interface)
- **Purpose**: Abstracts user interaction (confirmations, questions, events). Ensures agents can query users without hardcoding I/O (e.g., CLI vs. GUI).
- **Key Methods** (all abstract):
  - `confirm_tool_call(tool_name: str, arguments: Dict[str, Any], reason: str) -> bool`: Get user approval for a tool.
  - `ask_user(question: List[str], options: List[str], allow_free_text: bool) -> str`: Pose questions with/without choices.
  - `emit_event(kind: str, payload: Dict[str, Any]) -> None`: Log/notify events (e.g., tool success).
- **Usage**: Implemented for specific UIs; injected into agents for confirmations.

## ToolCallingAgent (Concrete Class, Extends BaseAgent)
- **Purpose**: Specialized agent for LLM-driven tool calling. Orchestrates tasks with policy checks, async processing, and UI integration. Handles conversation loops.
- **Key Attributes** (inherits BaseAgent +):
  - `llm`: ChatLLMProvider - Conversational LLM.
  - `tools`: List[BaseTool] - Tool instances.
  - `policy`: ToolUsePolicy - Execution rules.
  - `ui`: UIAdapter - User interface handler.
  - `system_prompt`: str - LLM system instructions.
- **Key Methods**:
  - `__init__(...)`: Initializes with policy/UI.
  - `process_task(task: str) -> Any`: Main entry; triggers async loop.
  - `_process_task_async(task: str) -> Dict[str, Any]`: Internal async handling (private).
  - `handle_tool_calls(tool_name: str, payload: Dict[str, Any]) -> Any`: Executes tools per policy.
  - `_run_sync()`: Synchronous wrapper (private).
- **Usage**: Core agent for tool-heavy tasks; enforces policies before calls.

## High-Level Flow (ASCII Diagram)
```
User Task ──→ ToolCallingAgent.process_task()
             │
             ├── LLM (via llm.chat() / OpenRouterProvider) ──→ Tool Calls Detected? (using get_llm_function_specs from ToolRegistry)
             │     │ No ──→ Direct Response (update_memory)
             │     │ Yes ──→ Check ToolUsePolicy (autonomy, allow/deny)
             │           │ Denied ──→ Skip/Confirm via UIAdapter.ask_user()
             │           │ Allowed ──→ handle_tool_calls() ──→ BaseTool.__call__() ──→ execute() (e.g., FetchTool)
             │                         │
             └── UIAdapter.confirm_tool_call() (if needed; or via AskUserTool) ──→ User Input
                                                    │
                                                    └── Loop until Complete (max_steps)
```

## BaseTool (Abstract Base Class)
- **Purpose**: Foundation for all tools. Enforces typed input/output via Pydantic models, automatic validation, timeouts, concurrency limits, and JSON schema generation for LLM tool-calling. Subclasses implement execute() for specific logic.
- **Key Attributes**:
  - `name`: str - Unique tool identifier.
  - `description`: str - Human/LLM-readable description.
  - `input_model`: Type[TIn] - Pydantic model for input validation.
  - `output_model`: Type[TOut] - Pydantic model for output validation.
  - `timeout_seconds`: Optional[float] = 30.0 - Execution timeout.
  - `max_concurrency`: Optional[int] - Limit concurrent executions.
  - `requires_network`: bool = False - Flag for network access.
  - `requires_filesystem`: bool = False - Flag for FS access.
  - `tags`: Set[str] - Categorization (e.g., "web", "utility").
- **Key Methods**:
  - `__init__()`: Validates class-level attrs (name, description, models).
  - `get_schema() -> Dict[str, Any]`: Generates JSON schema for LLM function-calling.
  - `to_descriptor() -> ToolDescriptor`: Lightweight metadata for registry/UI.
  - `__call__(data: Union[Dict[str, Any], TIn], context: Optional[Dict[str, Any]] = None) -> TOut`: Validates input, applies limits, calls execute().
  - `execute(params: TIn, context: Optional[Dict[str, Any]] = None) -> TOut` (abstract): Core async logic; context for tracing/auth.
  - Internal: `_validate_input`, `_execute_with_handling` (error wrapping), `_maybe_timeout`.
- **Usage**: Subclass for custom tools (e.g., EchoTool); register in ToolRegistry; inject into agents.

## ToolRegistry (Concrete Class)
- **Purpose**: Central manager for tools: registration (unique by name), lookup, listing (with tag filtering), schema generation for LLMs, and policy-based resolution for agents. Ensures tools are discoverable and safely accessible.
- **Key Attributes**:
  - `_tools: Dict[str, BaseTool]` - Internal storage (name → tool instance).
- **Key Methods**:
  - `__init__()`: Empty registry.
  - `register_tool(tool: BaseTool) -> None`: Adds tool; raises if duplicate.
  - `bulk_register(tools: Iterable[BaseTool]) -> None`: Registers multiple; fails on duplicates.
  - `get_tool(name: str) -> BaseTool`: Retrieves by name; raises if not found.
  - `has_tool(name: str) -> bool`: Checks existence.
  - `list_tool_names(tags: Optional[Set[str]] = None) -> List[str]`: Names, filtered by tags (must match all).
  - `list_tools(tags: Optional[Set[str]] = None) -> List[BaseTool]`: Tool instances, filtered.
  - `list_descriptors(tags: Optional[Set[str]] = None) -> List[ToolDescriptor]`: Metadata for UI/discovery.
  - `get_llm_function_specs(tool_names: Optional[Sequence[str]] = None) -> List[dict]`: OpenAI-compatible schemas for subset/all tools.
  - `get_tools_for_agent(agent_name: str, policy: Optional[Dict[str, Sequence[str]]] = None, fallback_tags: Optional[Set[str]] = None) -> List[BaseTool]`: Resolves tools per agent policy or tags; defaults to all.
- **Usage**: Global instance for app startup (e.g., load_builtins()); agents query for available tools/schemas.

## EchoTool (Concrete Class, Subclass of BaseTool)
- **Purpose**: Simple utility tool for testing/debugging: echoes input text with optional uppercase, repetition, and delay. No real side effects.
- **Input Model (EchoInput)**: `text: str` (required), `uppercase: bool=False`, `repeat: int=1` (1-10), `delay_ms: Optional[int]=None` (0-5000ms for latency simulation).
- **Output Model (EchoOutput)**: `result: str` (echoed text), `length: int` (char count).
- **Key Methods**:
  - `execute(params: EchoInput, context: Optional[dict] = None) -> EchoOutput`: Applies uppercase/repeat/delay, returns output.
- **Operational**: timeout=5s, unlimited concurrency, no network/FS, tags={"utility", "testing", "example"}.
- **Usage**: Built-in for validation; auto-registered via builtin_loader.py.

## AskUserTool (Concrete Class, Subclass of BaseTool)
- **Purpose**: Virtual tool for user interaction: schemas LLM to request input (questions/options). Execution intercepted by orchestrator (e.g., routed to UIAdapter.ask_user()); not executed directly.
- **Input Model (AskInput)**: `question: str` (required), `options: Optional[List[str]]` (multi-choice), `allow_free_text: bool=True`.
- **Output Model (AskOutput)**: `answer: str` (user response), `selected_option: Optional[str]` (if options used).
- **Key Methods**:
  - `execute(params: AskInput, context: Optional[dict] = None) -> AskOutput`: Placeholder (returns empty); actual handling external.
- **Operational**: No specific limits/tags defined; virtual (no real execution).
- **Usage**: Exposes UI interaction to LLM; integrated with UIAdapter.

## FetchTool (Concrete Class, Subclass of BaseTool)
- **Purpose**: Web tool for HTTP GET requests: fetches URL content (text/binary), handles redirects/timeouts, truncates large responses. Uses httpx for async HTTP.
- **Input Model (FetchInput)**: `url: str` (required), `timeout_ms: int=8000` (500-60000ms), `max_bytes: int=500000` (1024-5M), `headers: Optional[Dict[str, str]]`, `decode: bool=True` (text vs. raw).
- **Output Model (FetchOutput)**: `status_code: int`, `content_type: Optional[str]`, `body: str` (decoded/truncated), `truncated: bool`.
- **Key Methods**:
  - `execute(params: FetchInput, context: Optional[dict] = None) -> FetchOutput`: Async GET via httpx; decodes if possible, truncates body.
- **Operational**: requires_network=True, timeout=15s, max_concurrency=8, tags={"web", "http", "fetch"}.
- **Usage**: Built-in for web fetching; auto-registered; useful for scraping/research agents.

## Utils: config_loader.py (Module with Functions)
- **Purpose**: Utility functions for loading and manipulating configuration (YAML-based, with env var expansion and deep merging). Supports flexible config for agents/providers (e.g., loading from multiple files, extracting sub-configs). No classes—pure functions for app bootstrapping.
- **Key Functions**:
  - `_deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]`: Internal: Recursively merges two dicts (later overrides earlier).
  - `_expand_env(value: Any) -> Any`: Internal: Recursively expands ${VAR} env vars in strings/dicts/lists.
  - `load_config(paths: Optional[Iterable[str]] = None) -> Dict[str, Any]`: Loads/merges YAML from paths (default: ["config/default.yaml"]), skips missing, expands env vars post-merge.
  - `get_openrouter_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]`: Extracts `cfg["llm"]["openrouter"]` sub-tree (empty dict if missing).
  - `get_llm_provider_cfg(cfg: Dict[str, Any], provider: str) -> Dict[str, Any]`: Extracts `cfg["llm"][provider]` sub-tree (empty if missing).
- **Usage**: Called at startup for agent configs (e.g., OpenRouterProvider.from_config(load_config())); env vars like OPENAI_API_KEY expanded automatically. Handles multi-file overrides (e.g., default + env-specific).

## AgentRegistry (Concrete Class)
- **Purpose**: Registry for agent types/classes, enabling dynamic discovery and instantiation by name (e.g., "tool_calling" → ToolCallingAgent class). Parallels ToolRegistry for agents—populate at startup for extensibility.
- **Key Attributes**:
  - `_agent_classes: Dict[str, Type[BaseAgent]]` - Maps agent_type (str) to BaseAgent subclass.
- **Key Methods**:
  - `__init__()`: Initializes empty dict.
  - `register(agent_type: str, agent_class: Type[BaseAgent]) -> None`: Registers class by type (e.g., "master" → MasterAgent).
  - `get_agent_class(agent_type: str) -> Type[BaseAgent]`: Retrieves class; raises ValueError if unregistered.
  - `list_agent_types() -> list`: Returns all types.
  - `is_registered(agent_type: str) -> bool`: Existence check.
- **Usage**: Startup: registry.register("tool_calling", ToolCallingAgent); used by AgentFactory.get_agent_class().

## AgentFactory (Concrete Class)
- **Purpose**: Factory for instantiating agents from configs (Pydantic AgentConfig model), wiring dependencies (LLM from config via LLMFactory, tools filtered from ToolRegistry, memory if enabled). Supports dict/file input (JSON/YAML)—central for dynamic agent creation.
- **Key Attributes**:
  - `agent_registry: AgentRegistry` - Looks up agent classes.
  - `tool_registry: ToolRegistry` - Resolves tools by name (filters enabled via config).
  - `llm_factory: LLMFactory` - Creates LLMs (e.g., OpenRouterProvider) from config.
- **Key Methods**:
  - `__init__(agent_registry: Optional[AgentRegistry] = None, tool_registry: Optional[ToolRegistry] = None)`: Defaults to global registries.
  - `create_from_config(config: AgentConfig) -> BaseAgent`: Core: Gets class/llm/tools/memory; passes additional_params.
  - `create_from_file(file_path: str) -> BaseAgent`: Loads/parses JSON/YAML as AgentConfig, creates.
  - `create_from_dict(config_dict: Dict[str, Any]) -> BaseAgent`: Validates dict as AgentConfig, creates.
- **Usage**: App entry: factory.create_from_file("config/agents.yaml") → ready agent. Depends on AgentConfig (e.g., agent_id, type, llm_config, tools list, system_prompt).

## ToolCallOrchestrator (Concrete Class)
- **Purpose**: Runtime engine for LLM-tool loops: Manages multi-step chat (OpenAI format), tool execution (parallel/serial, policy enforcement), virtual tools (ui.ask → UIAdapter), confirmations/errors, and events. NoopUIAdapter as silent default. Integrates all components for task processing.
- **Key Attributes**:
  - `llm: OpenRouterProvider` - For chat/tool-calling.
  - `policy: ToolUsePolicy` - Limits/autonomy/confirm/deny.
  - `ui: UIAdapter` - User interactions (default: NoopUIAdapter for headless).
  - `default_system_prompt: str` - LLM instructions (e.g., "Use tools wisely, ask user if needed").
- **Key Methods**:
  - `__init__(llm: OpenRouterProvider, policy: Optional[ToolUsePolicy] = None, ui: Optional[UIAdapter] = None, default_system_prompt: Optional[str] = None)`: Sets defaults.
  - `run(user_message: str, tool_names: List[str], system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`: Async: Builds messages/specs, loops (LLM → tools → results), returns final/messages/steps/finish_reason.
  - Internal: `_filter_tools` (policy allow/deny), `_execute_tool_calls` (parse/confirm/execute/intercept ui.ask/truncate), `_tool_message` (formats tool results).
- **Usage**: Agent delegates: orchestrator.run(task, agent.tools); emits events (e.g., "tool_call"). Handles virtual ui.ask by awaiting UIAdapter.ask_user().

## High-Level Flow (ASCII Diagram)
```
Config Load (via load_config()) ──→ AgentFactory.create_from_config() ──→ Agent Init (e.g., ToolCallingAgent with AgentMemory)
             │
User Task ──→ ToolCallingAgent.process_task() ──→ ToolCallOrchestrator.run() (loop)
             │
             ├── Memory Access (get_recent_short("conversation") for prompt; store_long user facts)
             │
             ├── LLM (via llm.chat() / OpenRouterProvider) ──→ Tool Calls? (specs from ToolRegistry)
             │     │ No ──→ Final Response (update_memory short/long)
             │     │ Yes ──→ Policy Check (allow/deny/confirm via UIAdapter)
             │           │ Denied ──→ Skip/Ask User (ui.ask intercept)
             │           │ Allowed ──→ Execute Tool (BaseTool) ──→ Store Result (append_short/store_long)
             │                         │
             └── UI Events/Confirm (via NoopUIAdapter) ──→ Loop (max_steps)
```

## ShortTermMemoryProtocol / InMemoryShortTerm (Interface/Impl)
- **Purpose**: Ephemeral memory for current session (e.g., recent tool results, chat history). Prunes to avoid bloat (fits LLM windows).
- **Key Methods**: `append(key, value)` (add ordered), `get_recent(key, n)` (last N deserialized), `prune(key, max_size)` (FIFO evict). Inherits store/retrieve/update from MemoryStore.
- **Impl Details (InMemoryShortTerm)**: Uses deque per key (maxlen=50 default); JSON serialize/deserialize values.
- **Usage**: For task context: `memory.append_short("tools_used", result)`; feed `get_recent_short("conversation")` to LLM prompt.

## LongTermMemoryProtocol / FileLongTerm (Interface/Impl)
- **Purpose**: Persistent memory for durable knowledge (e.g., user profiles, learned patterns). Stores with metadata; basic search (key match; extend for vectors).
- **Key Methods**: `store(key, value, metadata: Dict[timestamp, agent_id, tags])`, `search(query, limit)` (pattern match), `delete(key)`. Inherits store/retrieve/update.
- **Impl Details (FileLongTerm)**: JSON file (~/.flexygent/long_term_memory.json); loads/saves on ops. Metadata auto-adds timestamp.
- **Usage**: For facts: `memory.store_long("user_name", "Alice", metadata={"source": "task1"})`; recall: `memory.retrieve("long:user_name")` or `search_long("user")`.

## AgentMemory (Composite Class)
- **Purpose**: Unified memory manager combining short-term (session/ephemeral) and long-term (persistent). Routes by key prefix ("short:..." vs. "long:..."); configurable (disable long-term for simple agents).
- **Key Attributes**:
  - `short_term: ShortTermMemoryProtocol` - In-session history (e.g., InMemoryShortTerm).
  - `long_term: LongTermMemoryProtocol` - Cross-session storage (e.g., FileLongTerm).
  - `enable_long_term: bool` - Toggle persistence.
- **Key Methods**:
  - `__init__(short_term: Optional, long_term: Optional, enable_long_term: bool = True)`: Builds composite.
  - `store/retrieve/update(key: str, value: Any, metadata: Optional[Dict])`: Routes to short/long by prefix.
  - Short: `append_short(key, value)`, `get_recent_short(key, n=10) -> List[Any]`.
  - Long: `store_long(key, value, metadata)`, `search_long(query, limit=5) -> List[Dict[key, value, metadata]]`.
  - Helpers: `clear_short/clear_long`.
- **Usage**: In BaseAgent: `self.memory = AgentMemory(...)`; `self.update_memory("short:conv", msg)` for history; `self.memory.store_long("user_fact", fact)` for prefs. Factory creates from config.memory_type.

This is a starting point—easy to expand. What format or additions next (e.g., update this file, add relationships, or focus back on class diagram)?

## AgentRegistry (Concrete Class)
- **Purpose**: Registry for agent types/classes, enabling dynamic discovery and instantiation by name (e.g., "tool_calling" → ToolCallingAgent class). Parallels ToolRegistry for agents.
- **Key Attributes**:
  - `_agent_classes: Dict[str, Type[BaseAgent]]` - Maps agent_type (str) to class.
- **Key Methods**:
  - `__init__()`: Empty registry.
  - `register(agent_type: str, agent_class: Type[BaseAgent]) -> None`: Adds class by type name.
  - `get_agent_class(agent_type: str) -> Type[BaseAgent]`: Retrieves class; raises ValueError if not registered.
  - `list_agent_types() -> list`: All registered types.
  - `is_registered(agent_type: str) -> bool`: Checks existence.
- **Usage**: Populated at startup (e.g., register("tool_calling", ToolCallingAgent)); used by AgentFactory for creation.

## AgentFactory (Concrete Class)
- **Purpose**: Factory for creating agent instances from configs (dict/file), integrating registries (agents/tools/LLM). Handles wiring (e.g., llm from config, tools filtered by name/enabled). Supports JSON/YAML files.
- **Key Attributes**:
  - `agent_registry: AgentRegistry` - For agent class lookup.
  - `tool_registry: ToolRegistry` - For tool resolution.
  - `llm_factory: LLMFactory` - Placeholder for LLM creation (e.g., OpenRouterProvider from config).
- **Key Methods**:
  - `__init__(agent_registry: Optional[AgentRegistry] = None, tool_registry: Optional[ToolRegistry] = None)`: Uses defaults if none provided.
  - `create_from_config(config: AgentConfig) -> BaseAgent`: Builds agent (gets class/llm/tools from registries/config; filters enabled tools).
  - `create_from_file(file_path: str) -> BaseAgent`: Loads JSON/YAML, validates as AgentConfig, creates.
  - `create_from_dict(config_dict: Dict[str, Any]) -> BaseAgent`: Validates dict as AgentConfig, creates.
- **Usage**: App startup (e.g., factory = AgentFactory(); agent = factory.create_from_file("agents/tool_calling.yaml")). Depends on AgentConfig (Pydantic model for agent specs like type, llm_config, tools).

## ToolCallOrchestrator (Concrete Class)
- **Purpose**: Core engine for the tool-calling loop: Orchestrates LLM chats, tool execution (with policy checks/UI intercepts), virtual tools (e.g., ui.ask routes to UIAdapter), and multi-step reasoning. Handles parallelism, truncation, errors. NoopUIAdapter as default (silent fallback).
- **Key Attributes**:
  - `llm: OpenRouterProvider` - LLM for chat/tool calls.
  - `policy: ToolUsePolicy` - Enforces limits/autonomy.
  - `ui: UIAdapter` - For confirmations/questions (default NoopUIAdapter).
  - `default_system_prompt: str` - Fallback instructions for LLM.
- **Key Methods**:
  - `__init__(llm: OpenRouterProvider, policy: Optional[ToolUsePolicy] = None, ui: Optional[UIAdapter] = None, default_system_prompt: Optional[str] = None)`: Sets defaults.
  - `run(user_message: str, tool_names: List[str], system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`: Async main loop (messages, tool specs, steps; returns final/messages/steps).
  - Internal: `_filter_tools` (policy-based), `_execute_tool_calls` (parallel/serial execution, UI/virtual handling, truncation), `_tool_message` (formats results).
- **Usage**: Called by agents (e.g., ToolCallingAgent delegates to orchestrator.run()); integrates everything (LLM → tools → UI). Emits events via UIAdapter.

This is a starting point—easy to expand. What format or additions next (e.g., update this file, add relationships, or focus back on class diagram)?