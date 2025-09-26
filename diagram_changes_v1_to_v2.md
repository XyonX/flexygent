# Flexygent Diagram Changes: v1 to v2

## Overview
This document outlines the key changes between the v1 and v2 class and sequence diagrams, reflecting the evolution of the Flexygent codebase architecture.

## Major Architectural Changes

### 1. Enhanced Agent Hierarchy
**v1**: Simple hierarchy with `BaseAgent` and `ToolCallingAgent`
**v2**: Expanded hierarchy with multiple specialized agent types:

- **BaseAgent** (unchanged)
- **ToolCallingAgent** (enhanced with more features)
- **LLMToolAgent** (new - simple LLM-based agent)
- **ReasoningToolAgent** (new - enhanced reasoning capabilities)
- **AdaptiveToolAgent** (new - learns from tool usage patterns)
- **GeneralToolAgent** (new - general-purpose agent with pragmatic defaults)
- **ResearchAgent** (new - specialized for web research tasks)
- **RAGAgent** (new - retrieval-augmented generation)
- **MasterAgent** (new - coordinates multiple agents)

### 2. Enhanced LLM Provider System
**v1**: Basic `OpenRouterProvider` and `SimpleLLMProvider`
**v2**: Added `EnhancedProviderResolver` for:
- Multiple provider support (OpenRouter, Cloudflare, Vercel)
- Model selection based on cost, performance, or task requirements
- Intelligent model selection strategies
- Fallback mechanisms

### 3. Expanded Tool Ecosystem
**v1**: Basic tools (Echo, AskUser, Fetch)
**v2**: Comprehensive tool categories:

#### System Tools
- `EchoTool` (unchanged)

#### Web Tools
- `FetchTool` (unchanged)
- `SearchTool` (new)
- `ScraperTool` (new)

#### Coding Tools
- `CodeRunTool` (new)
- `CodeAnalyzeTool` (new)
- `CodeFormatTool` (new)

#### Research Tools
- `WebSearchTool` (new)
- `ResearchSummarizeTool` (new)

#### Writing Tools
- `ContentGenerateTool` (new)
- `GrammarCheckTool` (new)

#### Data Tools
- `DataAnalyzeTool` (new)

#### Project Tools
- `ProjectPlanTool` (new)

#### Creative Tools
- `CreativeIdeasTool` (new)

#### RAG Tools
- `RagIndexTool` (new)
- `RagQueryTool` (new)

#### UI Tools
- `AskUserTool` (unchanged)

### 4. RAG (Retrieval-Augmented Generation) System
**v1**: Not present
**v2**: Complete RAG infrastructure:
- `EmbeddingProvider` for text embeddings
- `LocalNumpyVectorStore` for vector storage
- `SearchResult` for query results
- `RagIndexTool` for indexing documents
- `RagQueryTool` for querying indexed content

### 5. Enhanced Memory System
**v1**: Basic memory with `InMemoryShortTerm` and `FileLongTerm`
**v2**: Enhanced memory system with:
- Improved `AgentMemory` composite class
- Better key prefix handling (`short:` vs `long:`)
- Enhanced serialization/deserialization
- More robust error handling

### 6. Improved Orchestration
**v1**: Basic `ToolCallOrchestrator`
**v2**: Enhanced orchestration with:
- Better tool filtering and policy enforcement
- Improved error handling and recovery
- Enhanced UI adapter integration
- More sophisticated tool execution flow

## Sequence Diagram Changes

### 1. Agent Factory Initialization
**v1**: Simple agent creation
**v2**: Enhanced initialization with:
- `EnhancedProviderResolver` for LLM selection
- More sophisticated tool resolution
- Better memory initialization

### 2. Specialized Agent Processing
**v1**: Generic tool calling flow
**v2**: Agent-specific processing flows:

#### ToolCallingAgent & Specialized Agents
- Enhanced tool orchestration
- Better policy enforcement
- Improved error handling

#### ResearchAgent
- Web search → scraping → summarization flow
- Async tool execution
- Memory-based result storage

#### RAGAgent
- Vector store querying
- Contextualized prompting
- Embedding-based retrieval

#### MasterAgent
- Task analysis and delegation
- Multi-agent coordination
- Result aggregation

#### AdaptiveToolAgent
- Tool performance tracking
- Dynamic tool prioritization
- Learning from outcomes

#### ReasoningToolAgent
- Enhanced reasoning modes (react, plan-act, plan-act-reflect)
- Reflection capabilities
- Constraint-based reasoning

### 3. RAG Indexing Flow
**v1**: Not present
**v2**: Complete RAG indexing workflow:
- Document loading and chunking
- Embedding generation
- Vector store population
- Index management

## Key Benefits of v2

### 1. Modularity
- Clear separation of concerns
- Specialized agents for specific tasks
- Comprehensive tool ecosystem

### 2. Scalability
- Enhanced provider resolution
- Better resource management
- Improved concurrency handling

### 3. Intelligence
- RAG capabilities for knowledge retrieval
- Adaptive learning from tool usage
- Enhanced reasoning capabilities

### 4. Flexibility
- Multiple agent types for different use cases
- Configurable tool selection
- Policy-based execution control

### 5. Maintainability
- Clear inheritance hierarchies
- Well-defined interfaces
- Comprehensive error handling

## Migration Considerations

### For Developers
1. **Agent Selection**: Choose appropriate agent type based on task requirements
2. **Tool Configuration**: Leverage new tool categories for specific domains
3. **Provider Configuration**: Use `EnhancedProviderResolver` for optimal model selection
4. **Memory Management**: Utilize enhanced memory features for better persistence

### For Users
1. **Agent Types**: Understand different agent capabilities and use cases
2. **Tool Access**: Leverage specialized tools for domain-specific tasks
3. **RAG Features**: Utilize retrieval-augmented generation for knowledge-intensive tasks
4. **Configuration**: Take advantage of enhanced configuration options

## Future Enhancements

The v2 architecture provides a solid foundation for future enhancements:
- Additional specialized agents
- More sophisticated tool categories
- Enhanced RAG capabilities
- Better integration with external systems
- Improved performance optimization

## Conclusion

The v2 architecture represents a significant evolution from v1, providing:
- **8x more agent types** (2 → 9)
- **10x more tool categories** (3 → 30+)
- **Complete RAG system** (0 → full implementation)
- **Enhanced provider resolution** (basic → intelligent)
- **Better memory management** (basic → advanced)

This evolution makes Flexygent more capable, flexible, and suitable for a wider range of applications while maintaining the core principles of modularity and extensibility.
