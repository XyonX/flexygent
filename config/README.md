# Flexygent Agent Configurations

This document provides an overview of all available agent configurations in the Flexygent system.

## 🎯 Master Agent

### Genesis (`config/genesis.yaml`)
- **Type**: `master`
- **Purpose**: Master coordinator that delegates to specialized agents
- **Capabilities**: Task analysis, agent selection, result synthesis
- **Team**: Manages a team of specialized agents

## 🔧 Specialized Agents

### 1. Coding Assistant (`config/coding_agent.yaml`)
- **Type**: `general`
- **Purpose**: Code development, debugging, and programming assistance
- **Tools**: 
  - `code.run` - Execute code snippets safely
  - `code.analyze` - Analyze code quality and provide suggestions
  - `code.format` - Format code according to style guidelines
  - `web.search` - Search for documentation and solutions
  - `web.fetch` - Fetch web content for reference
  - `system.echo` - Basic system interaction
- **Temperature**: 0.2 (deterministic)
- **Policy**: Auto (can execute code directly)

### 2. General Purpose (`config/general_purpose.yaml`)
- **Type**: `general`
- **Purpose**: Daily assistance and general tasks
- **Tools**: `web_search`, `code_run`, `calendar`, `notepad`, `email_send`
- **Temperature**: 0.3
- **Policy**: Assisted

### 3. Research Assistant (`config/research_agent.yaml`)
- **Type**: `research`
- **Purpose**: Information gathering, web searches, and research
- **Tools**: 
  - `web.search` - Comprehensive web search
  - `web.fetch` - Fetch specific URLs
  - `research.summarize` - Summarize research findings
  - `system.echo` - Basic system interaction
- **Temperature**: 0.3 (balanced)
- **Policy**: Auto (can search automatically)
- **Max Steps**: 12 (thorough research)

### 4. Writing Assistant (`config/writing_agent.yaml`)
- **Type**: `general`
- **Purpose**: Content creation, writing, and text generation
- **Tools**: 
  - `content.generate` - Generate various types of content
  - `writing.grammar_check` - Check grammar and style
  - `web.search` - Research for writing
  - `web.fetch` - Gather reference materials
  - `system.echo` - Basic system interaction
- **Temperature**: 0.7 (high creativity)
- **Policy**: Auto
- **Specialties**: Creative writing, technical writing, business writing, academic writing

### 5. Data Analyst (`config/data_analyst.yaml`)
- **Type**: `reasoning`
- **Purpose**: Data analysis, statistics, and analytical reasoning
- **Tools**: 
  - `data.analyze` - Analyze data and provide insights
  - `web.search` - Research data sources
  - `web.fetch` - Fetch datasets or reports
  - `system.echo` - Basic system interaction
- **Temperature**: 0.1 (precise analysis)
- **Policy**: Auto
- **Max Steps**: 15 (complex analysis)
- **Specialties**: Statistical analysis, pattern recognition, risk assessment

### 6. Project Manager (`config/project_manager.yaml`)
- **Type**: `adaptive`
- **Purpose**: Project planning, coordination, and task management
- **Tools**: 
  - `project.plan` - Create project plans and timelines
  - `web.search` - Research best practices
  - `web.fetch` - Gather project templates
  - `system.echo` - Basic system interaction
- **Temperature**: 0.4 (balanced)
- **Policy**: Assisted (asks for confirmation on major decisions)
- **Max Steps**: 12
- **Specialties**: Project planning, timeline management, resource allocation

### 7. Creative Designer (`config/creative_designer.yaml`)
- **Type**: `general`
- **Purpose**: Creative design, brainstorming, and innovative solutions
- **Tools**: 
  - `creative.ideas` - Generate creative ideas and concepts
  - `web.search` - Research design trends and inspiration
  - `web.fetch` - Gather design references
  - `system.echo` - Basic system interaction
- **Temperature**: 0.8 (high creativity)
- **Policy**: Auto
- **Specialties**: Brainstorming, design thinking, innovation, concept development

## 🎮 Usage Examples

### Single Agent Tasks
```bash
# Coding task
"Write a Python function to sort a list"
→ Genesis delegates to: coding_assistant

# Research task
"Research the latest AI developments"
→ Genesis delegates to: research_assistant

# Writing task
"Write a blog post about renewable energy"
→ Genesis delegates to: writing_assistant

# Analysis task
"Analyze the sales data trends"
→ Genesis delegates to: data_analyst

# Project task
"Create a project plan for launching a new product"
→ Genesis delegates to: project_manager

# Creative task
"Brainstorm ideas for a mobile app"
→ Genesis delegates to: creative_designer
```

### Multi-Agent Tasks
```bash
# Complex task
"Research renewable energy trends and create a presentation"
→ Genesis coordinates: research_assistant → writing_assistant

# Full project
"Plan and execute a marketing campaign"
→ Genesis coordinates: project_manager → creative_designer → writing_assistant
```

## 🔧 Configuration Schema

All agents follow this standard configuration schema:

```yaml
name: "agent_name"              # Unique identifier
type: "agent_type"              # Must be registered in AgentRegistry
description: "Agent description" # Optional description

llm:                            # LLM configuration
  provider: "openrouter"        # LLM provider
  model: "anthropic/claude-3-opus" # Model to use
  temperature: 0.7              # Creativity level (0.0-1.0)
  max_tokens: 3000              # Max response length

tools:                          # Tool configuration
  allowlist: ["tool1", "tool2"] # Allowed tools
  resolve_objects: true         # Resolve tool instances

policy:                         # Execution policy
  autonomy: "auto"              # auto/confirm/never
  max_steps: 8                  # Max reasoning steps

prompts:                        # Prompt configuration
  system: "You are a..."        # System prompt

config:                         # Agent-specific config
  max_tokens: 2000
  temperature: 0.3

reasoning:                      # Optional reasoning parameters
  mode: "plan-act-reflect"
  plan_depth: 2
  reflection: true
```

## 🚀 Adding New Agents

To add a new agent:

1. Create a new YAML file in `config/` directory
2. Follow the configuration schema above
3. Choose appropriate `type` from available types:
   - `general` - General purpose agent
   - `reasoning` - Advanced reasoning agent
   - `adaptive` - Adaptive behavior agent
   - `research` - Research specialist
   - `rag` - Retrieval-augmented generation
   - `master` - Master coordinator

4. The agent will be automatically available to Genesis

## 📊 Current Team Status

Genesis currently has **6 specialized agents** in its team:
- ✅ general_assistant
- ✅ reasoning_assistant  
- ✅ writing_assistant
- ✅ data_analyst
- ✅ project_manager
- ✅ creative_designer
- ❌ research_assistant (failed to create due to constructor issue)

## 🎯 Next Steps

1. **Fix Research Agent**: Resolve constructor issue for research_assistant
2. **Add More Tools**: Expand tool registry with more specialized tools
3. **Enhanced Selection**: Improve Genesis's agent selection logic
4. **Multi-Agent Coordination**: Implement complex multi-agent workflows
5. **Custom Configurations**: Allow users to create custom agent configs
