import sys
from dotenv import load_dotenv
from src.utils.config_loader import load_config , get_llm_provider_cfg
from src.llm.openrouter_provider import OpenRouterProvider
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools
from src.utils.themes import print_banner
from src.agents.agent_registry import AgentRegistry
from src.agents.tool_calling_agent import ToolCallingAgent
from src.memory import InMemoryShortTerm, FileLongTerm, AgentMemory
# from src.policy import ToolUsePolicy, AutonomyLevel
from src.agents.agent_factory import AgentFactory
from src.orchestration.tool_call_orchestrator import ToolCallOrchestrator

class FlexygentApp:
    def __init__(self,config_path=None):

        #step 0: load env 
        load_dotenv()

        #step 1: load config
        self.cfg = load_config()

        llm_provider = get_llm_provider_cfg(self.cfg,"openai")


        #step 2:  create llm provider
        self.llm_provider = OpenRouterProvider.from_config(llm_provider)

        #step 3: create and  register tools
        self.tool_registry = ToolRegistry()
        load_builtin_tools(self.tool_registry)

        #can create list of tools and pass in bulk loader or use the spefic builtin loader
        # tools = [EchoTool(), AskUserTool(), FetchTool()]
        # self.tool_registry.bulk_register(tools)


        # step 4: create and register agent
        self.agent_registry = AgentRegistry()
        self.agent_registry.register('tool_calling', ToolCallingAgent)

        # step 5: create memory
        # short_term = InMemoryShortTerm(max_history_per_key=50)
        # long_term = FileLongTerm(file_path='~/.flexygent/long_term_memory.json')
        # self.agent_memory = AgentMemory(short_term=short_term, long_term=long_term, enable_long_term=True)

        # # Step 6: Create policy
        # self.policy = ToolUsePolicy(autonomy=AutonomyLevel.confirm, max_steps=8)

        # # Step 7: Create UI adapter
        # self.ui_adapter = NoopUIAdapter()

        # Step 8: Create agent factory
        self.agent_factory = AgentFactory(agent_registry=self.agent_registry, tool_registry=self.tool_registry)

        # Step 9: Create orchestrator
        self.orchestrator = ToolCallOrchestrator(
            llm=self.llm_provider, policy=self.policy, ui=self.ui_adapter, default_system_prompt='You are a helpful agent.'
        )


        # Step 10: Create agent instance (using factory)
        agent_config = {'type': 'tool_calling', 'name': 'MyAgent'}  # Pull from self.config if needed
        self.agent = self.agent_factory.create_from_dict(agent_config)
        # Inject dependencies if not handled by factory (e.g., memory, orchestrator)
        self.agent.memory = self.agent_memory  # Assuming BaseAgent has setters or constructor allows this
        
        # Any other init (e.g., logging setup)
        



    def run(self):
        # Step 11: Main loop for user inputs
        print("Flexygent App running. Type 'exit' to quit.")
        print_banner()

        # while True:
        #     try:
        #         user_input = input("Enter your task: ")
        #         if user_input.lower() == 'exit':
        #             break
        #         response = self.agent.process_task(user_input)
        #         print("Response:", response)
        #     except Exception as e:
        #         print(f"Error: {e}")
        #         # Optionally continue or break


        while True:
            user_input = input("Enter you task: ")
            if user_input.lower()=='exit':
                break
            else:
                print(user_input)

    def close(self):
        # Explicit cleanup if needed (e.g., for resources not auto-handled by GC)
        # E.g., if long_term has a close method: self.agent_memory.long_term.close()
        # Or save state: self.agent_memory.store('app_state', 'closing')
        print("Cleaning up Flexygent App.")