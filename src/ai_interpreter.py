"""
ai_interpreter.py  —  Natural-language → UserProfile using the Anthropic API.

This is the RAG / AI layer added in the final project.
It sends the user's free-text request plus the list of valid genres and moods
from the catalog (retrieved context) to Claude, which returns a structured
JSON profile.  The profile is then fed into the original scoring engine.
"""

import json
import logging
import os
from typing import List

from .recommender import UserProfile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid values come from the actual catalog (retrieved context = RAG)
# ---------------------------------------------------------------------------
VALID_GENRES = ["pop", "rock", "lofi", "folk", "synthwave", "electronic"]
VALID_MOODS  = ["happy", "sad", "chill", "intense"]

SYSTEM_PROMPT = """You are a music profile extractor.
The user will describe what kind of music they want in plain English.
Your job is to map their request to a structured JSON profile using ONLY these exact values:

Valid genres: {genres}
Valid moods: {moods}
Energy: a float from 0.0 (very calm) to 1.0 (very intense)
likes_acoustic: true or false

Return ONLY a raw JSON object with exactly these four keys:
  "genre", "mood", "energy", "likes_acoustic"

No explanation, no markdown, no code fences — just the JSON object.

Examples:
User: "I want something upbeat for my morning run"
Output: {{"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": false}}

User: "Something chill and acoustic for studying"
Output: {{"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": true}}
"""


def interpret_request(user_text: str) -> UserProfile:
    """
    Send the user's natural-language request to Claude.
    Returns a UserProfile parsed from the JSON response.
    Falls back to a safe default profile on any error.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set — using fallback profile.")
        return _fallback_profile()

    try:
        import anthropic as _anthropic
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return _fallback_profile()

    client = _anthropic.Anthropic(api_key=api_key)

    system = SYSTEM_PROMPT.format(
        genres=", ".join(VALID_GENRES),
        moods=", ".join(VALID_MOODS),
    )

    logger.info("Sending request to Claude: %r", user_text[:120])

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",   # fast + cheap for structured extraction
            max_tokens=256,
            system=system,
            messages=[{"role": "user", "content": user_text}],
        )
        raw = message.content[0].text.strip()
        logger.info("Claude raw response: %s", raw)
        profile = _parse_profile(raw)
        logger.info("Parsed profile: %s", profile)
        return profile

    except Exception as e:
        if "connection" in str(e).lower() or "status" in str(type(e).__name__).lower():
            logger.error("API error: %s", e)
        elif isinstance(e, (json.JSONDecodeError, KeyError, ValueError)):
            logger.error("Failed to parse Claude response: %s", e)
        else:
            logger.error("Unexpected error calling Claude: %s", e)

    return _fallback_profile()


def _parse_profile(raw_json: str) -> UserProfile:
    """Parse Claude's JSON string into a UserProfile, with validation."""
    data = json.loads(raw_json)

    genre = str(data.get("genre", "pop")).lower().strip()
    mood  = str(data.get("mood",  "happy")).lower().strip()

    if genre not in VALID_GENRES:
        logger.warning("Unknown genre %r — defaulting to 'pop'", genre)
        genre = "pop"
    if mood not in VALID_MOODS:
        logger.warning("Unknown mood %r — defaulting to 'happy'", mood)
        mood = "happy"

    energy = float(data.get("energy", 0.5))
    energy = max(0.0, min(1.0, energy))   # clamp to valid range

    likes_acoustic = bool(data.get("likes_acoustic", False))

    return UserProfile(
        genre=genre,
        mood=mood,
        energy=energy,
        likes_acoustic=likes_acoustic,
    )


def _fallback_profile() -> UserProfile:
    """Safe default used when the API is unavailable."""
    return UserProfile(genre="pop", mood="happy", energy=0.7, likes_acoustic=False)


def generate_explanation(
    user_text: str,
    song_title: str,
    artist: str,
    genre: str,
    mood: str,
    score: float,
    confidence: float,
) -> str:
    """
    Ask Claude for a one-sentence plain-English explanation of why this song
    was recommended.  Falls back to a template string on any error.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return (
            f"Recommended because it matches your request "
            f"(confidence {confidence:.0%})."
        )

    try:
        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return (
            f"Recommended because it is a {mood} {genre} track "
            f"that matches your energy level (confidence {confidence:.0%})."
        )

    prompt = (
        f"The user asked for: \"{user_text}\"\n"
        f"We recommended \"{song_title}\" by {artist} "
        f"(genre: {genre}, mood: {mood}, score: {score:.2f}/5.0, "
        f"confidence: {confidence:.0%}).\n"
        f"Write exactly one friendly sentence explaining why this song fits the request. "
        f"Be specific. Do not mention scores or numbers."
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.warning("Explanation API call failed: %s", e)
        return (
            f"Recommended because it is a {mood} {genre} track "
            f"that matches your energy level (confidence {confidence:.0%})."
        )