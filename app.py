import sys
from dotenv import load_dotenv
from src.utils.config_loader import load_config , get_llm_provider_cfg
from src.llm.openrouter_provider import OpenRouterProvider

class FlexygentApp:
    def __init__(self,config_path=None):

        #00 load env 
        load_dotenv()

        #01 load config
        self.cfg = load_config()

        llm_provider = get_llm_provider_cfg(self.cfg,"openai")


        #02 create llm provider
        self.llm_provider = OpenRouterProvider.from_config(llm_provider)

    def run(self):
        # Step 11: Main loop for user inputs
        print("Flexygent App running. Type 'exit' to quit.")
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

    def close(self):
        # Explicit cleanup if needed (e.g., for resources not auto-handled by GC)
        # E.g., if long_term has a close method: self.agent_memory.long_term.close()
        # Or save state: self.agent_memory.store('app_state', 'closing')
        print("Cleaning up Flexygent App.")