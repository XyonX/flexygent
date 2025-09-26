"""
Demo script showing how to use the enhanced provider resolver
with different model selection strategies and agent types.
"""

import os
from src.llm.provider_resolver import get_enhanced_provider_resolver, EnhancedProviderResolver
from src.agents.agent_factory import AgentFactory
from src.agents.agent_registry import AgentRegistry, register_builtin_agents
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools


def demo_model_selection():
    """Demonstrate different model selection strategies."""
    print("=== Enhanced Provider Resolver Demo ===\n")
    
    # Initialize the resolver
    resolver = get_enhanced_provider_resolver()
    
    # 1. Show available models
    print("1. Available Models:")
    for provider_name, models in resolver.get_available_models().items():
        print(f"\n{provider_name.upper()}:")
        for model in models:
            print(f"  - {model.name}")
            print(f"    Cost: ${model.cost_per_1k_tokens:.4f}/1k tokens")
            print(f"    Performance: {model.performance_tier.value}")
            print(f"    Max tokens: {model.max_tokens:,}")
            print(f"    Capabilities: {', '.join(model.capabilities)}")
    
    # 2. Demonstrate model selection for different agent types
    print("\n\n2. Model Selection by Agent Type:")
    
    agent_configs = [
        {
            'name': 'research_agent',
            'type': 'research',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'research',
                'strategy': 'performance_optimized'
            }
        },
        {
            'name': 'coding_agent',
            'type': 'coding',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'coding',
                'strategy': 'balanced'
            }
        },
        {
            'name': 'cost_effective_agent',
            'type': 'general',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'general',
                'strategy': 'cost_optimized'
            }
        }
    ]
    
    for config in agent_configs:
        print(f"\n{config['name']}:")
        try:
            provider = resolver.resolve_provider(config['llm'])
            print(f"  Selected model: {provider.model}")
            print(f"  Provider: {config['llm']['provider']}")
            print(f"  Strategy: {config['llm']['strategy']}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 3. Demonstrate task-specific model selection
    print("\n\n3. Task-Specific Model Selection:")
    
    task_configs = [
        {
            'name': 'long_document_analysis',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'research',
                'strategy': 'task_specific',
                'task_requirements': {
                    'min_context_length': 100000,
                    'capabilities': ['analysis', 'reasoning']
                }
            }
        },
        {
            'name': 'creative_writing',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'creative',
                'strategy': 'task_specific',
                'task_requirements': {
                    'capabilities': ['creative'],
                    'use_cases': ['creative_writing']
                }
            }
        },
        {
            'name': 'cost_effective_coding',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'coding',
                'strategy': 'cost_optimized',
                'task_requirements': {
                    'capabilities': ['coding']
                }
            }
        }
    ]
    
    for config in task_configs:
        print(f"\n{config['name']}:")
        try:
            provider = resolver.resolve_provider(config['llm'])
            print(f"  Selected model: {provider.model}")
            print(f"  Requirements: {config['llm']['task_requirements']}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 4. Show model suggestions
    print("\n\n4. Model Suggestions:")
    
    suggestions = resolver.suggest_models(
        agent_type='research',
        task_requirements={
            'capabilities': ['reasoning', 'analysis'],
            'min_context_length': 50000
        },
        max_cost=0.01  # Max $0.01 per 1k tokens
    )
    
    print("Research agents with reasoning+analysis, 50k+ context, <$0.01/1k:")
    for provider_name, model_name, model_info in suggestions[:5]:  # Top 5
        print(f"  - {provider_name}/{model_name}")
        print(f"    Cost: ${model_info.cost_per_1k_tokens:.4f}/1k")
        print(f"    Performance: {model_info.performance_tier.value}")
        print(f"    Max tokens: {model_info.max_tokens:,}")


def demo_agent_creation():
    """Demonstrate creating agents with the enhanced resolver."""
    print("\n\n=== Agent Creation Demo ===\n")
    
    # Set up agent factory with enhanced resolver
    agent_registry = AgentRegistry()
    register_builtin_agents(agent_registry)
    
    tool_registry = ToolRegistry()
    load_builtin_tools(tool_registry)
    
    from src.llm.provider_resolver import create_enhanced_resolver_function
    provider_resolver = create_enhanced_resolver_function()
    
    agent_factory = AgentFactory(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        provider_resolver=provider_resolver
    )
    
    # Create different types of agents
    agent_configs = [
        {
            'name': 'ResearchAgent',
            'type': 'research',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'research',
                'strategy': 'performance_optimized',
                'temperature': 0.3
            },
            'tools': {
                'allowlist': ['web.search', 'web.fetch', 'research.summarize'],
                'resolve_objects': True
            }
        },
        {
            'name': 'CodingAgent',
            'type': 'coding',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'coding',
                'strategy': 'balanced',
                'temperature': 0.2
            },
            'tools': {
                'allowlist': ['code.analyze', 'code.format', 'code.run'],
                'resolve_objects': True
            }
        },
        {
            'name': 'CostEffectiveAgent',
            'type': 'general',
            'llm': {
                'provider': 'openrouter',
                'agent_type': 'general',
                'strategy': 'cost_optimized',
                'temperature': 0.4
            },
            'tools': {
                'allowlist': ['system.echo'],
                'resolve_objects': True
            }
        }
    ]
    
    for config in agent_configs:
        print(f"Creating {config['name']}...")
        try:
            agent = agent_factory.from_config(config)
            print(f"  ✓ Created successfully")
            print(f"  Model: {agent.llm.model if hasattr(agent.llm, 'model') else 'Unknown'}")
            print(f"  Tools: {len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 'Unknown'}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv('OPENROUTER_API_KEY'):
        print("Warning: OPENROUTER_API_KEY not set. Some demos may fail.")
        print("Set the environment variable to test with real API calls.\n")
    
    try:
        demo_model_selection()
        demo_agent_creation()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
