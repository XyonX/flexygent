# src/tools/builtin_loader.py
from .web.fetch import FetchTool
from .web.search import SearchTool
from .system.echo import EchoTool

# Coding tools
from .coding import CodeRunTool, CodeAnalyzeTool, CodeFormatTool

# Research tools
from .research import WebSearchTool, ResearchSummarizeTool

# Writing tools
from .writing import ContentGenerateTool, GrammarCheckTool

# Data analysis tools
from .data import DataAnalyzeTool

# Project management tools
from .project import ProjectPlanTool

# Creative design tools
from .creative import CreativeIdeasTool

def load_builtin_tools(registry):
    # System tools
    registry.register_tool(FetchTool())
    registry.register_tool(SearchTool())
    registry.register_tool(EchoTool())
    
    # Coding tools
    registry.register_tool(CodeRunTool())
    registry.register_tool(CodeAnalyzeTool())
    registry.register_tool(CodeFormatTool())
    
    # Research tools
    registry.register_tool(WebSearchTool())
    registry.register_tool(ResearchSummarizeTool())
    
    # Writing tools
    registry.register_tool(ContentGenerateTool())
    registry.register_tool(GrammarCheckTool())
    
    # Data analysis tools
    registry.register_tool(DataAnalyzeTool())
    
    # Project management tools
    registry.register_tool(ProjectPlanTool())
    
    # Creative design tools
    registry.register_tool(CreativeIdeasTool())
    
    print("Builtin tool loading successful!")
