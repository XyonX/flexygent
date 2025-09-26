"""
Enhanced LLM Provider Resolver with model selection capabilities.

This resolver allows agents to:
1. Choose from multiple providers (OpenRouter, Cloudflare, Vercel)
2. Select models based on cost, performance, or task requirements
3. Use intelligent model selection strategies
4. Fallback to cost-effective options when needed
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import yaml
except ImportError:
    yaml = None

from .openrouter_provider import OpenRouterProvider
from .openai_provider import OpenRouterProvider as OpenAIOpenRouterProvider  # Alias for clarity


class PerformanceTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SelectionStrategy(Enum):
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    TASK_SPECIFIC = "task_specific"


@dataclass
class ModelInfo:
    """Information about a specific model."""
    name: str
    provider: str
    cost_per_1k_tokens: float
    performance_tier: PerformanceTier
    max_tokens: int
    capabilities: List[str]
    use_cases: List[str]


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""
    name: str
    api_key_env: str
    base_url: str
    headers: Dict[str, str]
    models: Dict[str, ModelInfo]


class EnhancedProviderResolver:
    """
    Enhanced provider resolver that supports:
    - Multiple providers (OpenRouter, Cloudflare, Vercel)
    - Model selection based on cost/performance
    - Intelligent fallback strategies
    - Task-specific model recommendations
    """
    
    def __init__(self, models_config_path: str = "config/models.yaml"):
        self.models_config_path = models_config_path
        self.providers: Dict[str, ProviderConfig] = {}
        self.selection_strategies: Dict[str, Dict[str, Any]] = {}
        self.agent_defaults: Dict[str, Dict[str, Any]] = {}
        self._load_models_config()
    
    def _load_models_config(self):
        """Load the models configuration from YAML file."""
        if not yaml:
            raise ImportError("PyYAML is required for loading models configuration")
        
        if not os.path.exists(self.models_config_path):
            raise FileNotFoundError(f"Models config not found: {self.models_config_path}")
        
        with open(self.models_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Load providers and their models
        for provider_name, provider_data in config.get('providers', {}).items():
            models = {}
            for model_name, model_data in provider_data.get('models', {}).items():
                models[model_name] = ModelInfo(
                    name=model_name,
                    provider=provider_name,
                    cost_per_1k_tokens=model_data.get('cost_per_1k_tokens', 0.0),
                    performance_tier=PerformanceTier(model_data.get('performance_tier', 'low')),
                    max_tokens=model_data.get('max_tokens', 32000),
                    capabilities=model_data.get('capabilities', []),
                    use_cases=model_data.get('use_cases', [])
                )
            
            self.providers[provider_name] = ProviderConfig(
                name=provider_name,
                api_key_env=self._get_api_key_env(provider_name),
                base_url=self._get_base_url(provider_name),
                headers=self._get_headers(provider_name),
                models=models
            )
        
        # Load selection strategies
        self.selection_strategies = config.get('selection_strategies', {})
        
        # Load agent defaults
        self.agent_defaults = config.get('agent_defaults', {})
    
    def _get_api_key_env(self, provider_name: str) -> str:
        """Get the environment variable name for the provider's API key."""
        env_map = {
            'openrouter': 'OPENROUTER_API_KEY',
            'cloudflare': 'CLOUDFLARE_API_KEY',
            'vercel': 'VERCEL_API_KEY'
        }
        return env_map.get(provider_name, f'{provider_name.upper()}_API_KEY')
    
    def _get_base_url(self, provider_name: str) -> str:
        """Get the base URL for the provider."""
        url_map = {
            'openrouter': 'https://openrouter.ai/api/v1',
            'cloudflare': 'https://api.cloudflare.com/client/v4/accounts/c7606f2dbb6168312265ed635bf0db48/ai/v1',
            'vercel': 'https://api.vercel.com/v1'
        }
        return url_map.get(provider_name, '')
    
    def _get_headers(self, provider_name: str) -> Dict[str, str]:
        """Get default headers for the provider."""
        return {
            'X-Title': 'FlexyGent'
        }
    
    def resolve_provider(self, llm_cfg: Dict[str, Any]) -> Any:
        """
        Resolve and create an LLM provider instance based on configuration.
        
        Args:
            llm_cfg: LLM configuration dictionary containing:
                - provider: Provider name (openrouter, cloudflare, vercel)
                - model: Specific model name (optional, will be selected if not provided)
                - strategy: Selection strategy (cost_optimized, performance_optimized, etc.)
                - agent_type: Agent type for default model selection
                - task_requirements: Task-specific requirements
                - ... other provider-specific config
        
        Returns:
            LLM provider instance
        """
        provider_name = llm_cfg.get('provider', 'openrouter')
        agent_type = llm_cfg.get('agent_type', 'general')
        
        # Get provider configuration
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(self.providers.keys())}")
        
        provider_config = self.providers[provider_name]
        
        # Select model if not specified
        model_name = llm_cfg.get('model')
        if not model_name:
            model_name = self._select_model(
                provider_name=provider_name,
                agent_type=agent_type,
                strategy=llm_cfg.get('strategy'),
                task_requirements=llm_cfg.get('task_requirements', {}),
                preferred_models=llm_cfg.get('preferred_models', [])
            )
        
        # Get model info
        if model_name not in provider_config.models:
            raise ValueError(f"Unknown model '{model_name}' for provider '{provider_name}'")
        
        model_info = provider_config.models[model_name]
        
        # Create provider configuration
        provider_cfg = {
            'api_key_env': provider_config.api_key_env,
            'base_url': provider_config.base_url,
            'model': model_name,
            'headers': {**provider_config.headers, **llm_cfg.get('headers', {})},
            **{k: v for k, v in llm_cfg.items() if k not in ['provider', 'model', 'strategy', 'agent_type', 'task_requirements', 'preferred_models']}
        }
        
        # Create provider instance
        return self._create_provider_instance(provider_name, provider_cfg)
    
    def _select_model(
        self,
        provider_name: str,
        agent_type: str,
        strategy: Optional[str] = None,
        task_requirements: Optional[Dict[str, Any]] = None,
        preferred_models: Optional[List[str]] = None
    ) -> str:
        """
        Select the best model based on strategy and requirements.
        
        Args:
            provider_name: Name of the provider
            agent_type: Type of agent (research, coding, creative, etc.)
            strategy: Selection strategy
            task_requirements: Task-specific requirements
            preferred_models: List of preferred model names
        
        Returns:
            Selected model name
        """
        provider_config = self.providers[provider_name]
        available_models = list(provider_config.models.values())
        
        # Get agent defaults
        agent_defaults = self.agent_defaults.get(agent_type, {})
        default_strategy = agent_defaults.get('strategy', 'balanced')
        default_preferred = agent_defaults.get('preferred_models', [])
        min_performance = agent_defaults.get('min_performance_tier', 'low')
        
        # Use provided strategy or default
        strategy = strategy or default_strategy
        
        # Filter models by performance tier
        min_tier = PerformanceTier(min_performance)
        filtered_models = [
            m for m in available_models 
            if self._performance_tier_value(m.performance_tier) >= self._performance_tier_value(min_tier)
        ]
        
        if not filtered_models:
            # Fallback to any available model
            filtered_models = available_models
        
        # Apply preferred models filter
        if preferred_models or default_preferred:
            preferred = preferred_models or default_preferred
            preferred_filtered = [m for m in filtered_models if m.name in preferred]
            if preferred_filtered:
                filtered_models = preferred_filtered
        
        # Apply task-specific filtering
        if task_requirements:
            filtered_models = self._filter_by_task_requirements(filtered_models, task_requirements)
        
        # Select model based on strategy
        return self._apply_selection_strategy(filtered_models, strategy)
    
    def _filter_by_task_requirements(self, models: List[ModelInfo], requirements: Dict[str, Any]) -> List[ModelInfo]:
        """Filter models based on task requirements."""
        filtered = models
        
        # Filter by required capabilities
        required_capabilities = requirements.get('capabilities', [])
        if required_capabilities:
            filtered = [
                m for m in filtered 
                if any(cap in m.capabilities for cap in required_capabilities)
            ]
        
        # Filter by use cases
        required_use_cases = requirements.get('use_cases', [])
        if required_use_cases:
            filtered = [
                m for m in filtered 
                if any(use_case in m.use_cases for use_case in required_use_cases)
            ]
        
        # Filter by minimum context length
        min_context = requirements.get('min_context_length', 0)
        if min_context > 0:
            filtered = [m for m in filtered if m.max_tokens >= min_context]
        
        return filtered if filtered else models
    
    def _apply_selection_strategy(self, models: List[ModelInfo], strategy: str) -> str:
        """Apply the selection strategy to choose the best model."""
        if not models:
            raise ValueError("No models available for selection")
        
        strategy_config = self.selection_strategies.get(strategy, {})
        priority = strategy_config.get('priority', ['performance_tier', 'cost_per_1k_tokens'])
        
        # Sort models based on priority
        def sort_key(model: ModelInfo) -> Tuple:
            key_parts = []
            for criterion in priority:
                if criterion == 'cost_per_1k_tokens':
                    key_parts.append(model.cost_per_1k_tokens)  # Lower is better
                elif criterion == 'performance_tier':
                    key_parts.append(-self._performance_tier_value(model.performance_tier))  # Higher is better
                elif criterion == 'max_tokens':
                    key_parts.append(-model.max_tokens)  # Higher is better
                elif criterion == 'capabilities':
                    key_parts.append(-len(model.capabilities))  # More capabilities is better
                elif criterion == 'use_cases':
                    key_parts.append(-len(model.use_cases))  # More use cases is better
            
            return tuple(key_parts)
        
        sorted_models = sorted(models, key=sort_key)
        return sorted_models[0].name
    
    def _performance_tier_value(self, tier: PerformanceTier) -> int:
        """Convert performance tier to numeric value for comparison."""
        tier_values = {
            PerformanceTier.LOW: 1,
            PerformanceTier.MEDIUM: 2,
            PerformanceTier.HIGH: 3
        }
        return tier_values.get(tier, 1)
    
    def _create_provider_instance(self, provider_name: str, provider_cfg: Dict[str, Any]) -> Any:
        """Create a provider instance based on the provider name."""
        if provider_name == 'openrouter':
            return OpenRouterProvider.from_config(provider_cfg)
        elif provider_name == 'cloudflare':
            # TODO: Implement CloudflareProvider
            raise NotImplementedError("CloudflareProvider not yet implemented")
        elif provider_name == 'vercel':
            # TODO: Implement VercelProvider
            raise NotImplementedError("VercelProvider not yet implemented")
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def get_available_models(self, provider_name: Optional[str] = None) -> Dict[str, List[ModelInfo]]:
        """Get available models for a provider or all providers."""
        if provider_name:
            if provider_name not in self.providers:
                raise ValueError(f"Unknown provider: {provider_name}")
            return {provider_name: list(self.providers[provider_name].models.values())}
        
        return {
            name: list(config.models.values()) 
            for name, config in self.providers.items()
        }
    
    def get_model_info(self, provider_name: str, model_name: str) -> ModelInfo:
        """Get information about a specific model."""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        if model_name not in self.providers[provider_name].models:
            raise ValueError(f"Unknown model '{model_name}' for provider '{provider_name}'")
        
        return self.providers[provider_name].models[model_name]
    
    def suggest_models(
        self,
        agent_type: str,
        task_requirements: Optional[Dict[str, Any]] = None,
        max_cost: Optional[float] = None
    ) -> List[Tuple[str, str, ModelInfo]]:
        """
        Suggest models for a given agent type and task requirements.
        
        Returns:
            List of tuples: (provider_name, model_name, model_info)
        """
        suggestions = []
        
        for provider_name, provider_config in self.providers.items():
            for model_name, model_info in provider_config.models.items():
                # Apply filters
                if max_cost and model_info.cost_per_1k_tokens > max_cost:
                    continue
                
                if task_requirements:
                    if not self._model_matches_requirements(model_info, task_requirements):
                        continue
                
                suggestions.append((provider_name, model_name, model_info))
        
        # Sort by cost and performance
        suggestions.sort(key=lambda x: (x[2].cost_per_1k_tokens, -self._performance_tier_value(x[2].performance_tier)))
        
        return suggestions
    
    def _model_matches_requirements(self, model_info: ModelInfo, requirements: Dict[str, Any]) -> bool:
        """Check if a model matches the given requirements."""
        # Check capabilities
        required_capabilities = requirements.get('capabilities', [])
        if required_capabilities:
            if not any(cap in model_info.capabilities for cap in required_capabilities):
                return False
        
        # Check use cases
        required_use_cases = requirements.get('use_cases', [])
        if required_use_cases:
            if not any(use_case in model_info.use_cases for use_case in required_use_cases):
                return False
        
        # Check minimum context length
        min_context = requirements.get('min_context_length', 0)
        if min_context > 0 and model_info.max_tokens < min_context:
            return False
        
        return True


# Global instance for easy access
_global_resolver: Optional[EnhancedProviderResolver] = None


def get_enhanced_provider_resolver() -> EnhancedProviderResolver:
    """Get the global enhanced provider resolver instance."""
    global _global_resolver
    if _global_resolver is None:
        _global_resolver = EnhancedProviderResolver()
    return _global_resolver


def create_enhanced_resolver_function() -> callable:
    """Create a resolver function compatible with the existing AgentFactory."""
    resolver = get_enhanced_provider_resolver()
    return resolver.resolve_provider
