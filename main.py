from dotenv import load_dotenv
import os
import yaml

from src.llm.openrouter_provider import OpenRouterProvider
from src.utils.config_loader import load_config, get_openrouter_cfg
from src.agents.master_agent import MasterAgent
from src.tools.registry import ToolRegistry
from src.tools.builtin_loader import load_builtin_tools
import logging


# Configure logging once (you can tweak formatting and level)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


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


def load_yaml(path="config/default.yaml"):
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
            logging.info(f"✅ Successfully loaded YAML from {path}")
            return config
    except Exception as e:
        logging.error(f"❌ YAML loading failed for {path}: {type(e).__name__} - {e}")
        raise

        


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