"""
main.py  —  Applied AI Music Recommender  (Final Project)

Pipeline:
  1. Validate user input (guardrail)
  2. Send to Claude AI for natural-language → UserProfile mapping  (AI feature)
  3. Load song catalog  (RAG retrieval context)
  4. Score every song against the profile  (original engine, preserved)
  5. Compute confidence per recommendation  (reliability feature)
  6. Generate per-song AI explanations  (AI feature)
  7. Display results + log everything to logs/app.log

Usage:
  python -m src.main
  python -m src.main --demo          # runs 3 demo queries non-interactively
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from .logger_setup import setup_logging, validate_input
from .recommender  import load_catalog, recommend
from .ai_interpreter import interpret_request, generate_explanation

setup_logging()
logger = logging.getLogger(__name__)

CATALOG_PATH = Path(__file__).parent.parent / "data" / "songs.csv"
TOP_K        = 5

DEMO_QUERIES = [
    "I want something upbeat and energetic for my morning run",
    "Give me chill acoustic music for a rainy study session",
    "I'm feeling intense and want heavy electric guitar rock",
]


def run_query(user_text: str) -> None:
    """Execute the full pipeline for one user query."""

    print("\n" + "═" * 60)
    print(f"  You asked for: {user_text}")
    print("═" * 60)
    logger.info("New query received: %r", user_text)

    # ── 1. Guardrail ──────────────────────────────────────────────
    valid, cleaned = validate_input(user_text)
    if not valid:
        print(f"\n⚠  {cleaned}")
        logger.warning("Query rejected by guardrail: %s", cleaned)
        return

    # ── 2. AI interpretation (natural language → profile) ─────────
    print("\n🤖 Interpreting your request with Claude AI...")
    profile = interpret_request(cleaned)
    print(f"   Detected profile → genre: {profile.genre}, "
          f"mood: {profile.mood}, energy: {profile.energy:.0%}, "
          f"acoustic: {profile.likes_acoustic}")
    logger.info("Profile resolved: %s", profile)

    # ── 3. Load catalog (RAG retrieval) ──────────────────────────
    catalog = load_catalog(str(CATALOG_PATH))
    if not catalog:
        print("\n❌ Could not load song catalog. Check data/songs.csv.")
        return
    logger.info("Catalog loaded: %d songs", len(catalog))

    # ── 4 & 5. Score + confidence ─────────────────────────────────
    results = recommend(profile, catalog, top_k=TOP_K)
    logger.info("Scoring complete. Top result: %s (score %.2f)",
                results[0][0].title if results else "none",
                results[0][1] if results else 0)

    # ── 6. Display with AI explanations ──────────────────────────
    print(f"\n🎵 Top {TOP_K} recommendations:\n")
    for rank, (song, score, confidence) in enumerate(results, 1):
        bar = _confidence_bar(confidence)
        print(f"  {rank}. {song.title} — {song.artist}")
        print(f"     Confidence: {bar}  {confidence:.0%}")

        explanation = generate_explanation(
            user_text   = cleaned,
            song_title  = song.title,
            artist      = song.artist,
            genre       = song.genre,
            mood        = song.mood,
            score       = score,
            confidence  = confidence,
        )
        print(f"     {explanation}")
        print()
        logger.info(
            "Result %d: %s | score=%.2f | conf=%.2f",
            rank, song.title, score, confidence,
        )

    avg_conf = sum(r[2] for r in results) / len(results)
    print(f"  Average confidence across top {TOP_K}: {avg_conf:.0%}")
    logger.info("Average confidence: %.2f", avg_conf)


def _confidence_bar(conf: float, width: int = 10) -> str:
    filled = round(conf * width)
    return "█" * filled + "░" * (width - filled)


def interactive_mode() -> None:
    print("\n" + "═" * 60)
    print("  🎵 Applied AI Music Recommender")
    print("  Describe the music you want in plain English.")
    print("  Type 'quit' to exit.")
    print("═" * 60)

    while True:
        try:
            user_input = input("\nWhat kind of music are you in the mood for?\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if user_input.lower() in {"quit", "exit", "q"}:
            print("\nGoodbye!")
            break

        if user_input:
            run_query(user_input)


def demo_mode() -> None:
    print("\n" + "═" * 60)
    print("  🎵 Applied AI Music Recommender  —  DEMO MODE")
    print("═" * 60)
    for query in DEMO_QUERIES:
        run_query(query)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Music Recommender")
    parser.add_argument(
        "--demo", action="store_true",
        help="Run 3 pre-set demo queries instead of interactive mode",
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠  WARNING: ANTHROPIC_API_KEY not set.")
        print("   The AI interpretation step will use a fallback profile.")
        print("   Set it with:  export ANTHROPIC_API_KEY='sk-ant-...'")
        logger.warning("ANTHROPIC_API_KEY not set — AI features degraded.")

    if args.demo:
        demo_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()