# Flexygent 🤖

A flexible, modular multi-agent AI framework built for orchestrating specialized AI agents with tool-calling capabilities. Flexygent enables you to create, configure, and deploy AI agents that can collaborate to solve complex tasks through intelligent delegation and coordination.

## ✨ Features

- **🎯 Multi-Agent Architecture**: Deploy specialized agents for different domains (coding, research, writing, data analysis)
- **🔧 Tool-Calling Framework**: Rich ecosystem of built-in tools for web search, code execution, content generation, and more
- **🧠 Memory Management**: Short-term and long-term memory systems for context retention
- **⚙️ Flexible Configuration**: YAML-based configuration system for easy agent customization
- **🔄 Agent Factory Pattern**: Dynamic agent creation and management
- **🌐 Multi-Provider Support**: Compatible with OpenAI, OpenRouter, and other LLM providers
- **📊 Policy Enforcement**: Configurable autonomy levels and tool usage policies
- **🎨 Extensible Design**: Easy to add new agents, tools, and capabilities

## 🏗️ Architecture

Flexygent follows a modular architecture with clear separation of concerns:

```
src/
├── agents/           # Agent implementations (master, research, coding, etc.)
├── llm/             # LLM provider abstractions and implementations
├── tools/            # Tool ecosystem (web, coding, creative, data, etc.)
├── memory/           # Memory management (short-term, long-term)
├── orchestration/   # Tool calling orchestration and policies
├── rag/             # Retrieval-Augmented Generation capabilities
└── utils/           # Configuration loading and utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key or OpenRouter API key
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flexygent.git
   cd flexygent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root with the following content:
   
   ```bash
   # .env file
   
   # OpenRouter API Configuration (Recommended)
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   
   # Alternative: OpenAI API Configuration
   # OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional: Custom model selection
   OPENAI_MODEL=x-ai/grok-4-fast:free
   
   # Optional: Memory storage path
   MEMORY_PATH=~/.flexygent/long_term_memory.json
   
   # Optional: Logging level
   LOG_LEVEL=INFO
   ```

   **Getting API Keys:**
   - **OpenRouter**: Visit [OpenRouter.ai](https://openrouter.ai/) and create an account
   - **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/) and create an API key

5. **Verify installation**
   ```bash
   python -c "import src.agents; print('Flexygent installed successfully!')"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

### First Run Setup

When you first run Flexygent, you'll see:

```
Genesis Master Agent is running. Type 'exit' to quit.
========================================
    🤖 FLEXYGENT AI FRAMEWORK 🤖
========================================

Available agent types: ['master', 'general', 'research', 'coding', 'writing', 'data', 'creative', 'project']
Available tools: ['system.echo', 'web.search', 'web.fetch', 'web.scrape', 'code.run', 'code.analyze', 'content.generate', ...]
Genesis team members: ['researcher', 'coder', 'writer', 'analyst', 'creative', 'planner']

Enter your task for Genesis: 
```

**Example first interaction:**
```
Enter your task for Genesis: Help me research the latest trends in AI agent frameworks

Genesis is analyzing: 'Help me research the latest trends in AI agent frameworks'
=== Genesis Response ===
Strategy: I'll delegate this research task to our specialized research agent who can search the web and gather comprehensive information about AI agent framework trends.
Result: [Research findings will be displayed here]
==================================================
```

## 🎮 Usage Examples

### Interactive Mode (Recommended)

The easiest way to use Flexygent is through the interactive Genesis interface:

```bash
python app.py
```

**Example interactions:**

1. **Research Task**
   ```
   Enter your task for Genesis: What are the latest developments in AI agent frameworks?
   ```

2. **Coding Task**
   ```
   Enter your task for Genesis: Write a Python function to calculate fibonacci numbers
   ```

3. **Content Creation**
   ```
   Enter your task for Genesis: Create a blog post about the benefits of multi-agent AI systems
   ```

4. **Data Analysis**
   ```
   Enter your task for Genesis: Analyze this CSV data and provide insights: [paste your data]
   ```

### Programmatic Usage

#### Basic Agent Usage

```python
from src.agents.research_agent import ResearchAgent
from src.llm.openrouter_provider import OpenRouterProvider
from src.tools.builtin_loader import load_builtin_tools
from src.utils.config_loader import load_config, get_llm_provider_cfg

# Load configuration
config = load_config()
llm_config = get_llm_provider_cfg(config, "openai")

# Create LLM provider
llm = OpenRouterProvider.from_config(llm_config)

# Load tools
load_builtin_tools()

# Create research agent
agent = ResearchAgent(
    name="researcher",
    config={"max_results": 5},
    llm=llm
)

# Process a task
result = agent.process_task("Latest developments in AI frameworks 2024")
print(result["summary"])
```

#### Master Agent (Genesis) Coordination

```python
from app import FlexygentApp

# Initialize the full application
app = FlexygentApp()

# Genesis will analyze and delegate tasks to appropriate agents
response = app.agent.process_task("Help me write a Python script for data analysis")
print(f"Strategy: {response['strategy']['reasoning']}")
print(f"Result: {response['final_response']}")
```

#### Custom Agent Configuration

```python
from src.agents.agent_factory import AgentFactory
from src.agents.agent_registry import AgentRegistry
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools

# Set up registries
agent_registry = AgentRegistry()
tool_registry = ToolRegistry()
load_builtin_tools(tool_registry)

# Create agent factory
factory = AgentFactory(
    agent_registry=agent_registry,
    tool_registry=tool_registry,
    provider_resolver=lambda cfg: OpenRouterProvider.from_config(cfg)
)

# Create custom agent configuration
custom_config = {
    'type': 'general',
    'name': 'MyCustomAgent',
    'llm': {
        'api_key': 'your-api-key',
        'model': 'gpt-4o-mini',
        'temperature': 0.3
    },
    'tools': {
        'allowlist': ['web.search', 'web.fetch', 'system.echo']
    },
    'policy': {
        'autonomy': 'auto',
        'max_steps': 5
    }
}

# Create agent
agent = factory.from_config(custom_config)
result = agent.process_task("Your task here")
```

### Running Examples

Flexygent includes several example scripts to get you started:

```bash
# Simple research agent
python examples/simple_agent.py

# Tool-calling agent with OpenRouter
python examples/toolcalling_agent.py

# RAG-enabled agent
python examples/rag_agent.py

# Enhanced provider resolver demo
python examples/enhanced_resolver_demo.py
```

## 🤖 Available Agents

### Master Agent
- **Genesis**: Master coordinator that analyzes tasks and delegates to specialized agents

### Specialized Agents
- **Coding Assistant**: Code development, debugging, and programming assistance
- **Research Agent**: Information gathering, web searches, and research
- **Writing Assistant**: Content creation, writing, and text generation
- **Data Analyst**: Data analysis, statistics, and insights
- **Creative Designer**: Creative ideation and design concepts
- **Project Manager**: Project planning, timelines, and management

## 🛠️ Built-in Tools

### Web Tools
- `web.search` - Web search capabilities
- `web.fetch` - HTTP content fetching
- `web.scrape` - Web page scraping
- `web.rss` - RSS feed parsing

### Coding Tools
- `code.run` - Safe code execution
- `code.analyze` - Code quality analysis
- `code.format` - Code formatting

### Creative Tools
- `creative.ideas` - Creative idea generation
- `content.generate` - Content creation
- `writing.grammar_check` - Grammar checking

### Data Tools
- `data.analyze` - Data analysis and insights
- `project.plan` - Project planning

### System Tools
- `system.echo` - Basic system interaction
- `ui.ask` - User interaction

## ⚙️ Configuration

Flexygent uses YAML configuration files for easy customization:

```yaml
# config/genesis.yaml
type: master
name: Genesis
llm:
  provider: openrouter
  model: gpt-4o-mini
  temperature: 0.2
tools:
  allowlist: ["web.search", "web.fetch", "system.echo"]
policy:
  autonomy: auto
  max_steps: 10
```

## ⚙️ Configuration

### Environment Variables

Flexygent supports extensive configuration through environment variables:

```bash
# Required: API Configuration
OPENROUTER_API_KEY=your_api_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional: Model Selection
OPENAI_MODEL=x-ai/grok-4-fast:free  # Default model
OPENAI_BASE_URL=https://openrouter.ai/api/v1  # For OpenRouter

# Optional: Memory Configuration
MEMORY_PATH=~/.flexygent/long_term_memory.json
MEMORY_MAX_HISTORY=50

# Optional: Logging
LOG_LEVEL=INFO
LOG_FILE=flexygent.log

# Optional: Tool Configuration
TOOL_TIMEOUT=30
MAX_TOOL_CALLS=10
PARALLEL_TOOL_CALLS=true

# Optional: Agent Configuration
DEFAULT_AUTONOMY=auto  # auto, confirm, never
MAX_STEPS=8
```

### Configuration Files

You can also configure agents using YAML files in the `config/` directory:

```yaml
# config/my_agent.yaml
type: general
name: MyCustomAgent
llm:
  provider: openrouter
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 2000
tools:
  allowlist: ["web.search", "web.fetch", "code.run"]
  resolve_objects: true
policy:
  autonomy: auto
  max_steps: 6
  max_tool_calls: 5
prompts:
  system: "You are a helpful AI assistant specialized in web research and coding."
```

## 🔧 Development

### Adding New Agents

1. **Create agent class**
   ```python
   # src/agents/my_agent.py
   from src.agents.base_agent import BaseAgent
   
   class MyAgent(BaseAgent):
       def process_task(self, task: str) -> Any:
           # Implement your agent logic
           pass
       
       def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
           # Handle tool calls
           pass
   ```

2. **Register the agent**
   ```python
   # src/agents/agent_registry.py
   from src.agents.my_agent import MyAgent
   
   def register_builtin_agents(registry: AgentRegistry) -> None:
       registry.register("my_agent", MyAgent)
   ```

3. **Create configuration**
   ```yaml
   # config/my_agent.yaml
   type: my_agent
   name: MySpecializedAgent
   # ... rest of config
   ```

### Adding New Tools

1. **Create tool class**
   ```python
   # src/tools/my_tool.py
   from src.tools.base_tool import BaseTool
   from pydantic import BaseModel, Field
   
   class MyToolInput(BaseModel):
       param1: str = Field(..., description="Description of param1")
   
   class MyToolOutput(BaseModel):
       result: str = Field(..., description="Tool result")
   
   class MyTool(BaseTool[MyToolInput, MyToolOutput]):
       name = "my.tool"
       description = "Description of what this tool does"
       input_model = MyToolInput
       output_model = MyToolOutput
       
       async def execute(self, params: MyToolInput, context: Optional[dict] = None) -> MyToolOutput:
           # Implement tool logic
           return MyToolOutput(result="Tool executed successfully")
   ```

2. **Register the tool**
   ```python
   # src/tools/builtin_loader.py
   from src.tools.my_tool import MyTool
   
   def load_builtin_tools(registry):
       # ... existing tools
       registry.register_tool(MyTool())
   ```

## 🚨 Troubleshooting

### Common Issues

#### 1. **API Key Not Found**
```
Error: No API key provided
```
**Solution:** Ensure your `.env` file contains either `OPENROUTER_API_KEY` or `OPENAI_API_KEY`

#### 2. **Module Import Errors**
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** Make sure you're running from the project root directory and have activated your virtual environment

#### 3. **Tool Execution Timeout**
```
ToolExecutionError: Tool execution timed out
```
**Solution:** Increase timeout in your configuration or check network connectivity

#### 4. **Memory Permission Errors**
```
PermissionError: [Errno 13] Permission denied: '/home/user/.flexygent'
```
**Solution:** Create the directory manually or change the `MEMORY_PATH` in your `.env` file

#### 5. **Model Not Available**
```
Error: Model 'gpt-4' not found
```
**Solution:** Check if your API key has access to the model, or try a different model like `gpt-4o-mini`

### Debug Mode

Enable debug logging for more detailed information:

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
python app.py --verbose
```

### Performance Optimization

1. **Reduce Model Costs**
   ```bash
   # Use smaller, faster models
   OPENAI_MODEL=gpt-4o-mini
   ```

2. **Limit Tool Usage**
   ```yaml
   # In agent config
   policy:
     max_tool_calls: 3
     max_steps: 5
   ```

3. **Enable Parallel Processing**
   ```yaml
   policy:
     parallel_tool_calls: true
   ```

### Getting Help

- **Check the logs**: Look for error messages in the console output
- **Verify configuration**: Ensure all required environment variables are set
- **Test with simple tasks**: Start with basic tasks like "echo hello world"
- **Check API quotas**: Verify your API key has sufficient credits/quota

## 📁 Project Structure

Understanding the Flexygent codebase:

```
flexygent/
├── src/                          # Core source code
│   ├── agents/                   # Agent implementations
│   │   ├── base_agent.py         # Abstract base class
│   │   ├── master_agent.py       # Genesis coordinator
│   │   ├── research_agent.py     # Web research specialist
│   │   ├── tool_calling_agent.py # Tool-enabled agent
│   │   └── ...                   # Other specialized agents
│   ├── llm/                      # Language model providers
│   │   ├── openrouter_provider.py # OpenRouter integration
│   │   ├── openai_provider.py    # OpenAI integration
│   │   └── provider_resolver.py  # Dynamic provider selection
│   ├── tools/                    # Tool ecosystem
│   │   ├── web/                  # Web tools (search, fetch, scrape)
│   │   ├── coding/               # Code tools (run, analyze, format)
│   │   ├── creative/             # Creative tools (ideas, content)
│   │   ├── data/                 # Data analysis tools
│   │   └── ...                   # Other tool categories
│   ├── memory/                   # Memory management
│   │   ├── stores.py             # Memory implementations
│   │   └── interfaces.py         # Memory protocols
│   ├── orchestration/            # Tool orchestration
│   │   ├── tool_call_orchestrator.py # Main orchestration engine
│   │   └── interaction_policy.py  # Policy enforcement
│   ├── rag/                      # RAG capabilities
│   │   ├── embedding.py          # Text embeddings
│   │   ├── vector_store.py       # Vector storage
│   │   └── query.py              # Query processing
│   └── utils/                    # Utilities
│       ├── config_loader.py      # Configuration management
│       └── themes.py             # UI themes
├── config/                       # Configuration files
│   ├── default.yaml              # Default settings
│   ├── genesis.yaml              # Master agent config
│   ├── coding_agent.yaml         # Coding agent config
│   └── ...                       # Other agent configs
├── examples/                     # Example scripts
│   ├── simple_agent.py           # Basic usage example
│   ├── toolcalling_agent.py      # Tool-calling example
│   └── rag_agent.py              # RAG example
├── app.py                        # Main application entry point
├── main.py                       # Alternative entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 📊 Memory System

Flexygent includes a sophisticated memory system:

- **Short-term Memory**: In-memory storage for conversation context
- **Long-term Memory**: Persistent file-based storage
- **Agent Memory**: Composite memory with automatic routing

```python
from src.memory import InMemoryShortTerm, FileLongTerm, AgentMemory

# Create memory system
short_term = InMemoryShortTerm(max_history_per_key=50)
long_term = FileLongTerm(file_path='~/.flexygent/memory.json')
memory = AgentMemory(short_term=short_term, long_term=long_term)

# Usage in agents
agent.memory.store_long("user_preference", "dark_mode", {"timestamp": "2024-01-15"})
recent_context = agent.memory.get_recent_short("conversation", 10)
```

## 🔒 Security & Policies

Flexygent includes configurable security policies:

- **Autonomy Levels**: `auto`, `confirm`, `never`
- **Tool Allowlists**: Restrict which tools agents can use
- **Execution Limits**: Maximum steps and tool calls
- **Timeout Controls**: Prevent runaway executions

## 🚀 Quick Start Checklist

New to Flexygent? Follow this checklist to get up and running:

- [ ] **Install Python 3.11+** and verify with `python --version`
- [ ] **Clone the repository** with `git clone https://github.com/yourusername/flexygent.git`
- [ ] **Create virtual environment** with `python -m venv venv`
- [ ] **Activate virtual environment** (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on macOS/Linux)
- [ ] **Install dependencies** with `pip install -r requirements.txt`
- [ ] **Get API key** from [OpenRouter.ai](https://openrouter.ai/) or [OpenAI](https://platform.openai.com/)
- [ ] **Create `.env` file** with your API key
- [ ] **Test installation** with `python -c "import src.agents; print('Success!')"`
- [ ] **Run Flexygent** with `python app.py`
- [ ] **Try your first task** like "echo hello world" or "search for AI news"

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and test them thoroughly
4. **Commit your changes** (`git commit -m 'Add amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/flexygent.git
cd flexygent

# Install development dependencies
pip install -r requirements.txt
pip install black isort pytest

# Run tests
python -m pytest

# Format code
black src/
isort src/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pydantic](https://pydantic.dev/) for robust data validation
- Uses [OpenAI API](https://openai.com/) and [OpenRouter](https://openrouter.ai/) for LLM access
- Inspired by modern AI agent frameworks and tool-calling patterns
- Thanks to the open-source community for the amazing tools and libraries

## 📞 Support & Community

- 📖 **Documentation**: Check the `docs/` directory for detailed guides
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/flexygent/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/flexygent/discussions)
- 💡 **Feature Requests**: Open an issue with the "enhancement" label
- 🤝 **Contributing**: See our [Contributing Guidelines](CONTRIBUTING.md)

## 🌟 What's Next?

- **Web Interface**: Browser-based UI for easier interaction
- **Plugin System**: Easy way to add custom tools and agents
- **Cloud Deployment**: One-click deployment to cloud platforms
- **Multi-language Support**: Agents that can work in multiple languages
- **Advanced RAG**: Enhanced retrieval with better context understanding

---

**Flexygent** - Where AI agents collaborate to achieve more! 🚀

*Built with ❤️ for the AI community*
