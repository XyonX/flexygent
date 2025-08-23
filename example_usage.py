# example_usage.py
import asyncio
from tools.tool_registry import registry
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from config.config import Config
from utils.llm import llm_client

config = Config()
short_memory = ShortTermMemory()
long_memory = LongTermMemory(config)

async def main():
    session_id = "session_001"

    # Step 1: User sends a message
    user_message = "Hello! Can you echo this message using your tool?"
    print(f"User: {user_message}")

    # Add to short-term memory
    short_memory.add_message(session_id, {"role": "user", "content": user_message})

    # Step 2: Decide tool usage (simplified simulation)
    # Let's say we detect user wants to use the "echo" tool
    tool_name = "echo"
    tool_input = user_message

    # Step 3: Execute the tool via the registry
    tool_output = registry.execute(tool_name, tool_input)
    print(f"Tool Output: {tool_output}")

    # Step 4: Add tool output as assistant message in short-term memory
    short_memory.add_message(session_id, {"role": "assistant", "content": tool_output})

    # Step 5: Query LLM to optionally respond based on history
    history = short_memory.get_history(session_id)
    response = await llm_client.chat.completions.create(
        model="openrouter/auto",
        messages=history
    )

    assistant_msg = response.choices[0].message
    # assistant_text = assistant_msg["content"]
    assistant_text = assistant_msg.content  # ✅ correct


    # Add LLM response to memory
    short_memory.add_message(session_id, {"role": "assistant", "content": assistant_text})

    print(f"Assistant (LLM): {assistant_text}")

# Run the async main
asyncio.run(main())
