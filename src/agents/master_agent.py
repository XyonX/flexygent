from .base_agent import BaseAgent, LLMProvider, MemoryStore
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from ..tools.base_tool import BaseTool
from ..orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel
from ..orchestration.tool_call_orchestrator import ToolCallOrchestrator, UIAdapter

if TYPE_CHECKING:
    from .agent_factory import AgentFactory
    from .agent_registry import AgentRegistry


class MasterAgent(BaseAgent):
    """
    Master agent (Genesis) that coordinates tasks between pre-existing specialized agents.
    
    Capabilities:
    - Analyzes tasks and determines which existing agents to delegate to
    - Uses pre-created agents from a provided list
    - Coordinates multi-agent workflows
    - Aggregates results from multiple agents
    - Manages communication between agents
    """
    
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[MemoryStore] = None,
        *,
        available_agents: Optional[Dict[str, BaseAgent]] = None,
        policy: Optional[ToolUsePolicy] = None,
        ui: Optional[UIAdapter] = None,
        system_prompt: Optional[str] = None,
    ):
        super().__init__(name=name, config=config, llm=llm, tools=tools, memory=memory)
        
        # Store available agents that Genesis can delegate to
        self._available_agents = available_agents or {}
        self._system_prompt = system_prompt or self._get_default_system_prompt()
        
        # Create orchestrator for Genesis's own tool usage
        default_policy = ToolUsePolicy(
            autonomy=AutonomyLevel.auto,
            max_steps=int(config.get("max_steps", 10)),
        )
        self._orchestrator = ToolCallOrchestrator(
            llm=self.llm,  # type: ignore[arg-type]
            policy=policy or default_policy,
            ui=ui,
            default_system_prompt=self._system_prompt,
        )

    def _get_default_system_prompt(self) -> str:
        """Default system prompt for Genesis master agent."""
        available_agent_names = list(self._available_agents.keys())
        return f"""You are Genesis, the master AI coordinator. Your role is to:

1. ANALYZE incoming tasks and determine the best approach
2. DELEGATE tasks to appropriate specialized agents from your available team
3. COORDINATE multi-agent workflows when needed
4. AGGREGATE results from multiple agents
5. PROVIDE comprehensive final responses

Available agents in your team: {available_agent_names}

When you receive a task:
- First analyze what type of work is needed
- Determine which agent(s) from your team should handle it
- Delegate to appropriate agents
- Coordinate their work if multiple agents are needed
- Synthesize their results into a final response

Always explain your reasoning and strategy."""

    def process_task(self, task: str) -> Dict[str, Any]:
        """Process a task by analyzing and delegating to appropriate existing agents."""
        return self._run_sync(self._process_task_async(task))

    async def _process_task_async(self, task: str) -> Dict[str, Any]:
        """Async task processing with agent delegation."""
        try:
            # Step 1: Analyze the task
            analysis = await self._analyze_task(task)
            
            # Step 2: Determine strategy
            strategy = await self._determine_strategy(task, analysis)
            
            # Step 3: Execute strategy (delegate to existing agents)
            results = await self._execute_strategy(task, strategy)
            
            # Step 4: Synthesize results
            final_response = await self._synthesize_results(task, results)
            
            return {
                "strategy": strategy,
                "results": results,
                "final_response": final_response,
                "agents_used": list(results.keys())
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "strategy": {"reasoning": "Failed to process task"},
                "final_response": f"Genesis encountered an error: {e}"
            }

    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze the task to understand requirements."""
        analysis_prompt = f"""
Analyze this task and determine:
1. What type of work is required?
2. What skills/knowledge are needed?
3. How complex is it?
4. Can it be handled by a single agent or needs coordination?

Task: {task}

Respond with a JSON analysis.
"""
        
        # Use orchestrator for analysis
        response = await self._orchestrator.run(
            user_message=analysis_prompt,
            tool_names=[],  # No tools needed for analysis
            system_prompt="You are Genesis analyzing a task. Provide a structured analysis."
        )
        
        return {
            "task": task,
            "analysis": response.get("final_response", "Analysis failed"),
            "timestamp": "now"
        }

    async def _determine_strategy(self, task: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine which existing agents to use and how to coordinate them."""
        available_agent_names = list(self._available_agents.keys())
        
        strategy_prompt = f"""
Based on this task analysis, determine the best strategy:

Task: {task}
Analysis: {analysis['analysis']}
Available agents: {available_agent_names}

Determine:
1. Which agent(s) should handle this task?
2. Should multiple agents work together?
3. What's the execution order?
4. How should results be combined?

Respond with a JSON strategy.
"""
        
        response = await self._orchestrator.run(
            user_message=strategy_prompt,
            tool_names=[],
            system_prompt="You are Genesis planning strategy. Provide a structured strategy."
        )
        
        return {
            "reasoning": response.get("final_response", "Strategy planning failed"),
            "available_agents": available_agent_names,
            "coordination_needed": len(available_agent_names) > 1
        }

    async def _execute_strategy(self, task: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the strategy by delegating to existing agents."""
        results = {}
        
        # Select appropriate agent based on task type
        selected_agent_name = self._select_agent_for_task(task)
        
        if selected_agent_name in self._available_agents:
            agent = self._available_agents[selected_agent_name]
            
            # Delegate the task to the selected agent
            result = agent.process_task(task)
            results[selected_agent_name] = result
            
        else:
            # Fallback: try to use any available agent
            if self._available_agents:
                first_agent_name = list(self._available_agents.keys())[0]
                agent = self._available_agents[first_agent_name]
                result = agent.process_task(task)
                results[first_agent_name] = result
            else:
                results["error"] = "No agents available for delegation"
            
        return results

    def _select_agent_for_task(self, task: str) -> str:
        """Select appropriate agent based on task content."""
        task_lower = task.lower()
        available_names = list(self._available_agents.keys())
        
        # Enhanced heuristic for better agent selection
        if any(word in task_lower for word in ['research', 'search', 'find', 'investigate', 'look up', 'gather information']):
            # Look for research agent
            for name in available_names:
                if 'research' in name.lower():
                    return name
                    
        elif any(word in task_lower for word in ['write', 'content', 'article', 'blog', 'story', 'document', 'text', 'copy']):
            # Look for writing agent
            for name in available_names:
                if 'writing' in name.lower():
                    return name
                    
        elif any(word in task_lower for word in ['analyze', 'analysis', 'data', 'statistics', 'metrics', 'trends', 'report']):
            # Look for data analyst
            for name in available_names:
                if 'data_analyst' in name.lower() or 'analyst' in name.lower():
                    return name
                    
        elif any(word in task_lower for word in ['project', 'plan', 'manage', 'coordinate', 'timeline', 'schedule', 'task']):
            # Look for project manager
            for name in available_names:
                if 'project_manager' in name.lower() or 'manager' in name.lower():
                    return name
                    
        elif any(word in task_lower for word in ['design', 'creative', 'brainstorm', 'innovate', 'concept', 'idea', 'visual']):
            # Look for creative designer
            for name in available_names:
                if 'creative' in name.lower() or 'designer' in name.lower():
                    return name
                    
        elif any(word in task_lower for word in ['code', 'program', 'debug', 'develop', 'software', 'function', 'algorithm']):
            # Look for coding agent
            for name in available_names:
                if any(word in name.lower() for word in ['code', 'reasoning', 'general']):
                    return name
                    
        elif any(word in task_lower for word in ['reason', 'think', 'logic', 'solve', 'problem', 'calculate']):
            # Look for reasoning agent
            for name in available_names:
                if 'reasoning' in name.lower():
                    return name
        
        # Default: return first available agent
        return available_names[0] if available_names else ""

    async def _synthesize_results(self, task: str, results: Dict[str, Any]) -> str:
        """Synthesize results from multiple agents into final response."""
        synthesis_prompt = f"""
Synthesize these agent results into a comprehensive final response:

Original Task: {task}
Agent Results: {results}

Provide a clear, comprehensive response that addresses the original task.
"""
        
        response = await self._orchestrator.run(
            user_message=synthesis_prompt,
            tool_names=[],
            system_prompt="You are Genesis synthesizing results. Provide a comprehensive final response."
        )
        
        return response.get("final_response", "Synthesis failed")

    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        """Handle tool calls for Genesis itself."""
        # Genesis can use tools directly if needed
        if self.tools:
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                return tool(payload)
        return f"Tool {tool_name} not available to Genesis"

    def add_agent(self, name: str, agent: BaseAgent) -> None:
        """Add an agent to Genesis's available team."""
        self._available_agents[name] = agent

    def remove_agent(self, name: str) -> None:
        """Remove an agent from Genesis's available team."""
        if name in self._available_agents:
            del self._available_agents[name]

    def list_available_agents(self) -> List[str]:
        """List names of available agents."""
        return list(self._available_agents.keys())

    def _run_sync(self, coro):
        """Run async coroutine synchronously."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        return loop.run_until_complete(coro)



