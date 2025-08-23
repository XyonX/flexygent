# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from utils.llm import llm_client
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from config.config import Config
from tools.tool_registry import registry

config = Config()
app = FastAPI(title="AI Agent Server")

# Initialize memory handlers
memory = ShortTermMemory()
long_memory = LongTermMemory(config)

# Request/Response models
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Add user message to short-term memory
    memory.add_message(request.session_id, {"role": "user", "content": request.message})

    # (Optional) Retrieve long-term context or tool info here

    # Call the LLM (OpenRouter) for a response
    # Using the accumulated history as context, consistent with chat completion APIs
    history = memory.get_history(request.session_id)
    response = await llm_client.chat.completions.create(
        model="qwen/qwen3-coder:free",  # Let OpenRouter auto-select model
        messages=history  # Use the full short-term chat history
    )
    # Extract the assistant's reply
    assistant_msg = response.choices[0].message  # Assuming response follows OpenAI schema
    assistant_text = assistant_msg["content"]

    # Store the assistant's message in memory
    memory.add_message(request.session_id, {"role": "assistant", "content": assistant_text})

    return ChatResponse(reply=assistant_text)
