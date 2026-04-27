import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY_1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def chat_reply(message: str, history: list[dict] | None = None) -> str:
    """
    message: latest user message to send to model
    history: list of previous messages
    """
    contents: list[dict] = []

    # Adds previous messages if provided
    if history:
        for turn in history:
            contents.append(
                {
                    "role": turn["role"],
                    "parts": [{"text": turn["content"]}],
                }
            )

    # Adds user's final message 
    contents.append(
        {
            "role": "user",
            "parts": [{"text": message}],
        }
    )

    # Send request
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
    )

    # Return output or message if returned nothing
    return response.text or "The information can't be found"