# manager.py
from flexygent.tools.base import Tool, ToolRegistry
from flexygent.mcp.config import MCPServerConfig
from flexygent.mcp.client import MCPClient



def make_mcp_caller(client:MCPClient,tool_name:str):
    def caller (params:dict):
        return client.call_tool(tool_name,params)
    return caller


def register_mcp_server(registry:ToolRegistry,config:MCPServerConfig):
    print(f"[MCP] Connecting to {config.name} at {config.url}...")


    # 01 inititalize cleint
    client = MCPClient(config)
    client.initialize()

    #02 fetch tools
    mcp_tools = client.list_tools()
    print(f"[MCP] Discovered {len(mcp_tools)} tools from {config.name} server  ")

    # 03 translate and register
    for mcp_tool in mcp_tools:
        tool_name = mcp_tool["name"]
        tool_desc = mcp_tool.get("description","")

        
        parameter_allowed = mcp_tool.get("inputSchema",{}).get("properties",{})

        # create proxy function
        proxy_function = make_mcp_caller(client,tool_name)

        # creatre standerd flexygent tool
        flexygent_tool = Tool(name=tool_name,
                              description=tool_desc,
                              parameter_allowed=parameter_allowed,
                              function=proxy_function)
        
        # add to registry
        registry.add_tool(flexygent_tool)
        

    
