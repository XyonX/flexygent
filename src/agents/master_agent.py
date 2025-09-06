from .base_agent import BaseAgent ,LLMProvider, MemoryStore
from typing import Any, Dict, List, Optional
from ..tools.base_tool import BaseTool

class MasterAgent(BaseAgent):
    """
    Master agent that coordinates tasks between specialized agents.
    Can delegate tasks to appropriate agents and aggregate results.
    """
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[MemoryStore] = None,):
        super().__init__(name=name,config=config,llm=llm,tools=tools,memory=memory)


    def process_task(self, task: str):
        print("task process complete")

    
    async def _process_task_async(self,task):
        

    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        pass

    # tool = next((t for t in self.tools if t.name == tool_name), registry.get_tool(tool_name))
    # return self._run_sync(tool(payload))



