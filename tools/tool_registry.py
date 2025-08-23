# tools/tool_registry.py

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func):
        """Register a tool function by name."""
        self.tools[name] = func

    def execute(self, name: str, *args, **kwargs):
        """Execute a registered tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' is not registered")
        return self.tools[name](*args, **kwargs)

# Example: define a simple tool function
def echo_tool(text: str) -> str:
    """A trivial tool that echoes the input text."""
    return f"Echo: {text}"

# Register the example tool
registry = ToolRegistry()
registry.register("echo", echo_tool)
