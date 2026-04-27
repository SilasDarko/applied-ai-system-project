"""
recommender.py  —  Original weighted-rule scoring engine (preserved from Module 3).

This module is intentionally unchanged from the base project so the extension
can be measured against it. All new AI features are layered on top in main.py.
"""

import csv
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights (same as original project)
# ---------------------------------------------------------------------------
GENRE_MATCH_POINTS   = 2.0
MOOD_MATCH_POINTS    = 1.0
MAX_ENERGY_POINTS    = 1.5
ACOUSTIC_BONUS       = 0.5
MAX_SCORE            = GENRE_MATCH_POINTS + MOOD_MATCH_POINTS + MAX_ENERGY_POINTS + ACOUSTIC_BONUS


@dataclass
class Song:
    title:        str
    artist:       str
    genre:        str
    mood:         str
    energy:       float
    tempo_bpm:    float
    valence:      float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    genre:        str
    mood:         str
    energy:       float   # 0.0 – 1.0
    likes_acoustic: bool


def load_catalog(path: str) -> List[Song]:
    """Load songs from CSV file. Returns empty list on file error."""
    songs = []
    if not os.path.exists(path):
        logger.error("Catalog file not found: %s", path)
        return songs
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    songs.append(Song(
                        title        = row["title"].strip(),
                        artist       = row["artist"].strip(),
                        genre        = row["genre"].strip().lower(),
                        mood         = row["mood"].strip().lower(),
                        energy       = float(row["energy"]),
                        tempo_bpm    = float(row["tempo_bpm"]),
                        valence      = float(row["valence"]),
                        danceability = float(row["danceability"]),
                        acousticness = float(row["acousticness"]),
                    ))
                except (KeyError, ValueError) as e:
                    logger.warning("Skipping malformed row %s: %s", row, e)
        logger.info("Loaded %d songs from catalog", len(songs))
    except OSError as e:
        logger.error("Could not read catalog: %s", e)
    return songs


def score_song(song: Song, profile: UserProfile) -> float:
    """
    Return a relevance score for one song against a user profile.

    Scoring breakdown:
      Genre match       +2.0
      Mood match        +1.0
      Energy closeness  0 – 1.5  (linear, penalises distance)
      Acoustic bonus    +0.5     (only if user likes acoustic AND song >= 0.7)
    """
    score = 0.0

    if song.genre == profile.genre.lower():
        score += GENRE_MATCH_POINTS

    if song.mood == profile.mood.lower():
        score += MOOD_MATCH_POINTS

    energy_gap = abs(song.energy - profile.energy)
    score += MAX_ENERGY_POINTS * (1.0 - energy_gap)

    if profile.likes_acoustic and song.acousticness >= 0.7:
        score += ACOUSTIC_BONUS

    return round(score, 4)


def compute_confidence(score: float) -> float:
    """
    Normalise raw score to a 0–1 confidence value.
    Scores near MAX_SCORE map to confidence near 1.0.
    """
    return round(min(score / MAX_SCORE, 1.0), 3)


def recommend(
    profile: UserProfile,
    catalog: List[Song],
    top_k: int = 5,
) -> List[Tuple[Song, float, float]]:
    """
    Return top_k songs as (song, raw_score, confidence) tuples, highest first.
    Logs a warning when confidence is below 0.5 for every result.
    """
    if not catalog:
        logger.warning("Catalog is empty — cannot produce recommendations.")
        return []

    scored = []
    for song in catalog:
        raw   = score_song(song, profile)
        conf  = compute_confidence(raw)
        scored.append((song, raw, conf))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = scored[:top_k]

    low_conf = [s[0].title for s in results if s[2] < 0.5]
    if low_conf:
        logger.warning("Low-confidence recommendations: %s", low_conf)

    return results