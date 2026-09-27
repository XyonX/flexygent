# client.py
from pydantic import BaseModel
from flexygent.mcp.config import MCPServerConfig
import requests
import json


class MCPClient():
    def __init__(self,config:MCPServerConfig):
        self.config=config
        self.url=config.url
        self.headers = {
            "Content-Type":"application/json",
            "Accept" : "text/event-stream",
            **config.headers #merge auth headers
        }
        self.rpc_id=1
        self.initialized = False

    def _send_request(self,method:str,params:dict = None,is_notification: bool = False ):


        payload = {"jsonrpc":"2.0","method":method}

        if not is_notification:
            payload["id"]=self.rpc_id
            self.rpc_id+=1

        if params:
            payload["params"]= params

        response = requests.post(self.url,json=payload,headers = self.headers,stream=True)

        # Parse SSE Stream

        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                json_str = line[6:]
                rpc_response = json.loads(json_str)
                if "result" in rpc_response:
                    return rpc_response["result"]
                elif "error" in rpc_response:
                    return f"MCP Error: {rpc_response['error']}"
                
        return None
    
    def initialize(self):
        # lifecycle initialize
        params = {
            "protocolVersion":"2026-07-28",
            "capabilities":{},
            "clientInfo":{"name":"Flexygent", "version":"1.0.0"}
        }
        result = self._send_request(method="initialize",params=params)
        self._send_request("notifications/initialized", is_notification=True)
        self.initialized=True
        return result
    
    def list_tools(self):
        result = self._send_request("tools/list")
        return result.get("tools",[])
    
    def call_tool(self,tool_name:str,arguments:dict):
        params = {"name":tool_name,"arguments":arguments}
        result = self._send_request("tools/call",params)

        if result and "content" in result:
            texts = [item["text"] for item in result["content"] if item["type"] == "text"]
            return " ".join(texts)
        return "Error: No result from MCP server."




    









