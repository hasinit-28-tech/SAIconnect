
import os
import json
import logging
import httpx

from src.ai.knowledge_base import (
    UNIVERSITY,
    SCHOOLS,
    PROGRAMS,
    UNIVERSITY_FACTS
)

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)


# Detect user's language
def detect_language(message):
    if any("\u0C00" <= char <= "\u0C7F" for char in message):
        return "Telugu"

    roman_telugu = [
        "namaskaram", "cheppandi", "kavali",
        "undi", "entha", "enti", "cheppu"
    ]

    if any(word in message.lower() for word in roman_telugu):
        return "Romanized Telugu"

    return "English"


# Prepare university information
def get_university_context():
    return {
        "university": UNIVERSITY,
        "schools": SCHOOLS,
        "programs": PROGRAMS,
        "facts": UNIVERSITY_FACTS
    }


# Generate AI response using Ollama
def get_ollama_response(message, language):

    context = get_university_context()

    system_prompt = f"""
You are SAIConnect, the friendly virtual receptionist
of Sai University, Chennai, India.

UNIVERSITY INFORMATION:
{json.dumps(context, ensure_ascii=False, indent=2)}

RESPONSE STYLE:
- Keep every answer short and brief (1-3 sentences).
- Answer the exact question directly.
- Use simple, natural language.
- Avoid long paragraphs.
- Use bullet points only when necessary.
- Be friendly, polite and professional.
- Do not repeat information unnecessarily.
- Reply in the user's language.

ACCURACY:
- Use only the university information provided.
- Never invent courses, fees, deadlines or eligibility.
- If information is unavailable, say so briefly.
- Never provide an unverified course count.
- Never mention Srigitam or another institution.

Detected language: {language}
"""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=120.0
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get(
            "message", {}
        ).get("content", "").strip()

        if answer:
            return answer

        return "Sorry, I couldn't find an answer. Please try again."

    except httpx.ConnectError:
        logger.exception("Ollama connection error")
        return "My AI service is unavailable. Please try again."

    except httpx.TimeoutException:
        logger.exception("Ollama timeout")
        return "Please try again. The response took too long."

    except Exception:
        logger.exception("AI response error")
        return "Sorry, something went wrong. Please try again."


# Main chatbot function
def generate_reply(message):

    if not isinstance(message, str) or not message.strip():
        return "Please enter a message."

    message = message.strip()
    language = detect_language(message)

    logger.info("Received message in %s", language)

    # Short greeting responses
    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if message.lower() in greetings:

        if language == "Telugu":
            return "నమస్కారం! సాయి యూనివర్సిటీకి స్వాగతం. నేను మీకు ఎలా సహాయం చేయగలను?"

        if language == "Romanized Telugu":
            return "Namaskaram! Sai University ki welcome. Meeku ela help cheyyagalanu?"

        return (
            "Hello! Welcome to Sai University! 😊 "
            "How can I help you today?"
        )

    # Generate answer using Ollama
    return get_ollama_response(message, language)
