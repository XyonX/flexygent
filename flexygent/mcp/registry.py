from typing import Dict,List
from pydantic import BaseModel,Field
from flexygent.mcp.client import MCPClient
from flexygent.mcp.config import MCPServerConfig
from flexygent.tools.base import Tool, ToolRegistry
from flexygent.mcp.manager import make_mcp_caller

class MCPRegistry(BaseModel):
    # Tracks connected mcp and their tools 
    clients : Dict [str,MCPClient]=Field(default_factory=dict)
    server_tool_map :Dict[str,List[str]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True # Allow MCPClient type

    def connect(self,config:MCPServerConfig,registry:ToolRegistry):

        print(f"Connecting to {config.name} at {config.url} ...")

        client = MCPClient(config)
        client.initialize()

        self.clients[config.name]=client

        # fetch tools
        mcp_tools=client.list_tools()
        tool_names = []

        for mcp_tool in mcp_tools:
            tool_name = mcp_tool["name"]
            tool_desc = mcp_tool.get("description","")
            parameter_allowed =mcp_tool.get("inputSchema",{}).get("properties",{})

            proxy_function = make_mcp_caller(client,tool_name)


            flexygent_tool = Tool(
                name=tool_name,
                description=tool_desc,
                parameter_allowed=parameter_allowed,
                function=proxy_function
            )

            registry.add_tool(flexygent_tool)
            tool_names.append(tool_name)
            print(f"  ↳ Registered: {tool_name}")

        self.server_tool_map[config.name]=tool_names
        print(f"[MCP] Discovered {len(tool_names)} tools from {config.name}")

    def get_tool_for_server(self,server_name:str)->List[str]:
        return self.server_tool_map.get(server_name,[])
    
    def get_all_tools(self)->List[str]:
        all_tools=[]
        for tools in self.server_tool_map.values():
            all_tools.extend(tools)
        return all_tools







