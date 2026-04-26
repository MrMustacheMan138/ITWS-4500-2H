from typing import List, Dict
from integrations.ai.client import chat_reply

# Chatbot wrapper function
async def chatbot (
    message: str,
    history: List[Dict[str, str]] | None = None,
) -> str:
    """
    Generate a chatbot response with Gemini.
    """
    # Use empty list if no history if provided 
    reply = await chat_reply(message=message, history=history or [])

    # Return generated response
    return reply
