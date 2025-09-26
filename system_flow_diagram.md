# Flexygent System Flow - From Input to Output

## 🏗️ **System Initialization Flow**

### **Step 1: App Startup (`app.py`)**
```
FlexygentApp.__init__() 
├── load_dotenv()                    # Load environment variables
├── load_config()                    # Load YAML configs from config/
├── get_llm_provider_cfg()           # Extract OpenRouter config
├── OpenRouterProvider.from_config() # Create LLM provider
├── ToolRegistry()                   # Create tool registry
├── load_builtin_tools()             # Register 15 built-in tools
├── AgentRegistry()                  # Create agent registry  
├── register_builtin_agents()        # Register 8 agent types
├── AgentFactory()                   # Create agent factory
└── agent_factory.from_config()      # Create Genesis master agent
```

### **Step 2: Tool Registration**
**File**: `src/tools/builtin_loader.py`
```
load_builtin_tools()
├── EchoTool()           # system.echo
├── AskUserTool()        # ui.ask  
├── FetchTool()          # web.fetch
├── SearchTool()         # web.search
├── CodeRunTool()        # code.run
├── CodeAnalyzeTool()    # code.analyze
├── CodeFormatTool()     # code.format
├── WebSearchTool()      # research.web_search
├── ResearchSummarizeTool() # research.summarize
├── ContentGenerateTool()  # content.generate
├── GrammarCheckTool()   # writing.grammar_check
├── DataAnalyzeTool()    # data.analyze
├── ProjectPlanTool()    # project.plan
└── CreativeIdeasTool()  # creative.ideas
```

### **Step 3: Agent Registration**
**File**: `src/agents/agent_registry.py`
```
register_builtin_agents()
├── ToolCallingAgent     # tool_calling
├── LLMToolAgent         # llm_tool
├── ReasoningToolAgent   # reasoning
├── AdaptiveToolAgent    # adaptive
├── GeneralToolAgent     # general
├── ResearchAgent        # research
├── RAGAgent            # rag
└── MasterAgent         # master
```

### **Step 4: Genesis Agent Creation**
**File**: `src/agents/agent_factory.py`
```
AgentFactory.from_config(genesis_config)
├── Get MasterAgent class from registry
├── Create OpenRouterProvider via resolver
├── Resolve tools: ['echo', 'fetch']
├── Create ToolUsePolicy (autonomy: auto, max_steps: 10)
├── Create MasterAgent instance
└── Create default team of 6 specialized agents
```

## 🔄 **Runtime Processing Flow**

### **Step 5: User Input Processing**
```
User Input: "hi"
├── FlexygentApp.run()
├── input("Enter your task for Genesis: ")
└── self.agent.process_task(user_input)
```

### **Step 6: Genesis Task Analysis**
**File**: `src/agents/master_agent.py`
```
MasterAgent.process_task()
├── _run_sync()                    # Convert async to sync
├── _process_task_async()
│   ├── _analyze_task()            # Analyze task requirements
│   ├── _determine_strategy()      # Choose execution strategy
│   ├── _execute_strategy()        # Delegate to agents
│   └── _synthesize_results()      # Combine results
└── Return structured response
```

### **Step 7: Task Analysis Details**
```
_analyze_task()
├── Create analysis prompt
├── _get_orchestrator()            # Get ToolCallOrchestrator
├── orchestrator.run()             # Use LLM to analyze
├── Parse JSON response
└── Return analysis dict
```

### **Step 8: Strategy Determination**
```
_determine_strategy()
├── Create strategy prompt with analysis
├── orchestrator.run()             # Use LLM to plan
├── Parse JSON response
└── Return strategy dict
```

### **Step 9: Strategy Execution**
```
_execute_strategy()
├── Check if single agent or multiple needed
├── For each required agent:
│   ├── _select_agent_for_task()   # Choose best agent
│   ├── Get agent from _available_agents
│   ├── agent.process_task()       # Delegate to agent
│   └── Store result
└── Return results dict
```

### **Step 10: Agent Selection Logic**
```
_select_agent_for_task()
├── Simple keyword matching
├── Check task keywords against agent capabilities
├── Return best matching agent name
└── Fallback to general_assistant
```

### **Step 11: Delegated Agent Processing**
```
GeneralToolAgent.process_task()
├── _run_sync()                    # Convert async to sync
├── _process_task_async()
│   ├── _build_system_prompt()     # Get agent-specific prompt
│   ├── _build_context()           # Add context
│   ├── orchestrator.run()         # Execute with tools
│   └── Return result
└── Return response
```

### **Step 12: Tool Orchestration**
**File**: `src/orchestration/tool_call_orchestrator.py`
```
ToolCallOrchestrator.run()
├── Build messages list
├── Get tool specs from ToolRegistry
├── LLM chat with tools
├── Parse tool calls from LLM response
├── Execute tools in parallel
├── Format tool results
├── Continue conversation loop
└── Return final response
```

### **Step 13: Tool Execution**
```
Tool Execution Flow
├── Parse tool call from LLM
├── Get tool from ToolRegistry
├── Validate input with Pydantic
├── Execute tool.async_execute()
├── Format result as tool message
└── Continue conversation
```

### **Step 14: Result Synthesis**
```
_synthesize_results()
├── Create synthesis prompt with all results
├── orchestrator.run()             # Use LLM to combine
└── Return final response
```

## 📊 **Data Flow Summary**

### **Input**: User text ("hi")
### **Processing**: 
1. Genesis analyzes → determines simple greeting
2. Selects general_assistant agent
3. Agent processes with LLM
4. Returns greeting response
### **Output**: Structured response with strategy and result

## 🔧 **Key Classes and Their Roles**

### **Core Classes**:
- `FlexygentApp`: Main application orchestrator
- `MasterAgent`: Task coordinator and delegator
- `AgentFactory`: Creates agent instances from config
- `ToolCallOrchestrator`: Manages LLM-tool interactions
- `OpenRouterProvider`: LLM API interface

### **Registry Classes**:
- `AgentRegistry`: Manages agent types
- `ToolRegistry`: Manages available tools

### **Agent Classes**:
- `GeneralToolAgent`: Handles general tasks
- `ResearchAgent`: Specialized for research
- `ReasoningToolAgent`: Advanced reasoning
- `AdaptiveToolAgent`: Learns from outcomes

### **Tool Classes**:
- `EchoTool`: Basic testing
- `FetchTool`: Web content retrieval
- `SearchTool`: Web search
- `CodeRunTool`: Code execution
- And 11 more specialized tools

## 🎯 **Configuration Files Used**

### **Main Config**: `config/default.yaml`
- LLM provider settings
- Model configurations

### **Agent Configs**: `config/*.yaml`
- Individual agent configurations
- Tool allowlists
- System prompts
- Policy settings

## 🔄 **Complete Flow Example**

```
User: "hi"
↓
FlexygentApp.run()
↓
Genesis.process_task("hi")
↓
Genesis._analyze_task() → "Simple greeting"
↓
Genesis._determine_strategy() → "Use general_assistant"
↓
Genesis._execute_strategy() → Delegate to general_assistant
↓
GeneralToolAgent.process_task()
↓
ToolCallOrchestrator.run() → LLM generates response
↓
Genesis._synthesize_results() → "Hello! How can I help you today?"
↓
Return: {"strategy": {...}, "final_response": "Hello! How can I help you today?"}
```

This is the complete flow from user input to system output in the Flexygent multi-agent system.
