# config.py
from typing import Optional
from pydantic import BaseModel,Field

class MCPServerConfig(BaseModel):
    # name of the mcp server
    name:str
    # sse ir stdio
    transport :str
    # for remote mcp
    url : Optional[str]
    headers:Optional[dict]


class McpConfig(BaseModel):
    servers: list[MCPServerConfig] = Field(default_factory=list)


mcp_config = McpConfig(servers=[MCPServerConfig(name="bad-calculator",
                                                transport ="sse",
                                                url="http://localhost:8000/mcp",
                                                headers={"Authorization":"Bearer AIFNAWFAW"})])
