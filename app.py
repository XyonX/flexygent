import sys
from dotenv import load_dotenv
from src.utils.config_loader import load_config , get_llm_provider_cfg
from src.llm.openrouter_provider import OpenRouterProvider
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools
from src.utils.themes import print_banner
from src.agents.agent_registry import AgentRegistry, register_builtin_agents
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


        # step 4: create and register agents
        self.agent_registry = AgentRegistry()
        register_builtin_agents(self.agent_registry)  # Register all built-in agent types

        # step 5: create memory
        # short_term = InMemoryShortTerm(max_history_per_key=50)
        # long_term = FileLongTerm(file_path='~/.flexygent/long_term_memory.json')
        # self.agent_memory = AgentMemory(short_term=short_term, long_term=long_term, enable_long_term=True)

        # # Step 6: Create policy
        # self.policy = ToolUsePolicy(autonomy=AutonomyLevel.confirm, max_steps=8)

        # # Step 7: Create UI adapter
        # self.ui_adapter = NoopUIAdapter()

        # Step 8: Create resolver functions
        def llm_provider_resolver(llm_cfg):
            return OpenRouterProvider.from_config(llm_cfg)
        
        def memory_resolver(mem_cfg):
            # TODO: Implement memory resolver based on config
            return None
        
        def ui_resolver(ui_cfg):
            # TODO: Implement UI resolver based on config
            return None

        # Step 9: Create agent factory
        self.agent_factory = AgentFactory(
            agent_registry=self.agent_registry,
            tool_registry=self.tool_registry,
            provider_resolver=llm_provider_resolver,
            memory_resolver=memory_resolver,
            ui_resolver=ui_resolver
        )

        # Step 10: Create orchestrator (commented out for now - will be created per agent)
        # self.orchestrator = ToolCallOrchestrator(
        #     llm=self.llm_provider, policy=self.policy, ui=self.ui_adapter, default_system_prompt='You are a helpful agent.'
        # )

        # Step 11: Create Genesis master agent instance (using factory)
        genesis_config = {
            'type': 'master', 
            'name': 'Genesis',
            'llm': llm_provider,  # Pass the LLM config
            'tools': {
                'allowlist': ['echo', 'fetch'],  # Genesis can use basic tools
                'resolve_objects': True
            },
            'policy': {
                'autonomy': 'auto',
                'max_steps': 10  # Genesis can take more steps for coordination
            },
            'prompts': {
                'system': 'You are Genesis, the master AI coordinator. Analyze tasks and delegate to appropriate agents.'
            }
        }
        self.agent = self.agent_factory.from_config(genesis_config)
        
        # Any other init (e.g., logging setup)
        



    def run(self):
        # Step 12: Main loop for user inputs
        print("Genesis Master Agent is running. Type 'exit' to quit.")
        print_banner()
        
        print(f"Available agent types: {self.agent_registry.list_agent_types()}")
        print(f"Available tools: {self.tool_registry.list_tool_names()}")
        print(f"Genesis team members: {self.agent.list_available_agents()}")

        while True:
            try:
                user_input = input("Enter your task for Genesis: ")
                if user_input.lower() == 'exit':
                    break
                print(f"\nGenesis is analyzing: '{user_input}'")
                response = self.agent.process_task(user_input)
                print("\n=== Genesis Response ===")
                print(f"Strategy: {response.get('strategy', {}).get('reasoning', 'Unknown')}")
                print(f"Result: {response.get('final_response', 'No result')}")
                print("=" * 50)
            except Exception as e:
                print(f"Error: {e}")
                # Optionally continue or break

    def close(self):
        # Explicit cleanup if needed (e.g., for resources not auto-handled by GC)
        # E.g., if long_term has a close method: self.agent_memory.long_term.close()
        # Or save state: self.agent_memory.store('app_state', 'closing')
        print("Cleaning up Flexygent App.")