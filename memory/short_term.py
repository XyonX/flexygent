# memory/short_term.py

class ShortTermMemory:
    def __init__(self):
        # Stores history as {session_id: [message_dict, ...]}
        self.history = {}

    def add_message(self, session_id: str, message: dict):
        """Add a message (with 'role' and 'content') to the session history."""
        self.history.setdefault(session_id, []).append(message)

    def get_history(self, session_id: str) -> list:
        """Retrieve the chat history for a session."""
        return self.history.get(session_id, [])
