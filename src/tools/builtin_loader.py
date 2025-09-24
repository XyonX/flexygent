# src/tools/builtin_loader.py
from .web.fetch import FetchTool
from .web.search import SearchTool
from .system.echo import EchoTool

def load_builtin_tools(registry):
    registry.register_tool(FetchTool())
    registry.register_tool(SearchTool())
    registry.register_tool(EchoTool())
    print("Builting tool loading successfull !!")
