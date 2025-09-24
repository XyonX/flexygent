import sys
from dotenv import load_dotenv
from src.utils.config_loader import load_config , get_llm_provider_cfg
from src.llm.openrouter_provider import OpenRouterProvider
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools
from src.utils.themes import print_banner

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