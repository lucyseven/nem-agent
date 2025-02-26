class ConversationManager:
    def __init__(self):
        self.history = []

    def add_message(self, role: str, message: str):
        """
        Add a message to the conversation history.
        :param role: 'user' or 'assistant'
        :param message: The content of the message.
        """
        self.history.append({"role": role, "content": message})

    def get_formatted_history(self) -> str:
        """
        Returns the conversation history as a formatted string,
        with each message on a new line.
        """
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])

    def clear_history(self):
        """
        Clears the conversation history.
        """
        self.history = []
