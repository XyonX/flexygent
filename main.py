from dotenv import load_dotenv
import os
import yaml

from src.llm.openrouter_provider import OpenRouterProvider
from src.utils.config_loader import load_config, get_openrouter_cfg
from src.agents.master_agent import MasterAgent
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools


registry = ToolRegistry()



def print_banner():

    banner = r"""
    ███████╗██╗     ███████╗██╗  ██╗██╗   ██╗ ██████╗ ███████╗███╗   ██╗████████╗
    ██╔════╝██║     ██╔════╝██║  ██║╚██╗ ██╔╝██╔═══██╗██╔════╝████╗  ██║╚══██╔══╝
    █████╗  ██║     █████╗  ███████║ ╚████╔╝ ██║   ██║█████╗  ██╔██╗ ██║   ██║   
    ██╔══╝  ██║     ██╔══╝  ██╔══██║  ╚██╔╝  ██║   ██║██╔══╝  ██║╚██╗██║   ██║   
    ██║     ███████╗███████╗██║  ██║   ██║   ╚██████╔╝███████╗██║ ╚████║   ██║   
    ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
    """
    print(banner)
    print("     Welcome to FlexyAgent CLI  (type 'help' for commands, 'exit' to quit)\n")


def load_yaml():
    with open("config/default.yaml") as f:
        config = yaml.safe_load(f)
        return config
        


def main():
    # print banner
    print_banner()

    # load env
    load_dotenv()

    # print 
    # print(os.getenv("CLOUDFLARE_API_KEY"))

    # load yaml
    config = load_yaml()

    # load builtin tools
    load_builtin_tools(registry)

    # extract opentouter config
    or_config=get_openrouter_cfg(config)

    # create llm

    llm=OpenRouterProvider.from_config(or_config)

    # allow tools
    allowed = ["web.search"]

    agent=MasterAgent(name="MasterAgent",config={"max_steps": 6, "temperature": 0.2},llm=llm,tools=[registry.get_tool(n) for n in allowed if registry.has_tool(n)])

    
    task = input("Enter task: ")
    result=agent.process_task(task)









if __name__ == "__main__":
    main()