import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Scoring weights  (tweak these to experiment)
# ---------------------------------------------------------------------------

GENRE_MATCH_POINTS   = 2.0
MOOD_MATCH_POINTS    = 1.0
MAX_ENERGY_POINTS    = 1.5   # awarded when energy gap == 0
ACOUSTIC_BONUS       = 0.5   # bonus when user likes acoustic AND song is acoustic


# ---------------------------------------------------------------------------
# OOP interface (required by test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP wrapper around the scoring logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a Song dataclass against a UserProfile."""
        score = 0.0
        reasons: List[str] = []

        # Genre match
        if song.genre.lower() == user.favorite_genre.lower():
            score += GENRE_MATCH_POINTS
            reasons.append(f"genre match (+{GENRE_MATCH_POINTS})")

        # Mood match
        if song.mood.lower() == user.favorite_mood.lower():
            score += MOOD_MATCH_POINTS
            reasons.append(f"mood match (+{MOOD_MATCH_POINTS})")

        # Energy proximity  (closer = higher score, max MAX_ENERGY_POINTS)
        energy_gap = abs(song.energy - user.target_energy)
        energy_points = round(MAX_ENERGY_POINTS * (1 - energy_gap), 3)
        score += energy_points
        reasons.append(f"energy proximity (+{energy_points:.2f})")

        # Acoustic bonus
        if user.likes_acoustic and song.acousticness >= 0.7:
            score += ACOUSTIC_BONUS
            reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS})")

        return round(score, 3), reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by score (highest first)."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        _, reasons = self._score(user, song)
        if not reasons:
            return "No strong match found, but included for variety."
        return ", ".join(reasons)


# ---------------------------------------------------------------------------
# Functional interface (required by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed values."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"]           = int(row["id"])
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song dict against a user preferences dict.

    user_prefs keys: genre, mood, energy, likes_acoustic (optional bool)
    Returns: (score: float, reasons: list[str])
    """
    score = 0.0
    reasons: List[str] = []

    # Genre match
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS})")

    # Mood match
    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS})")

    # Energy proximity
    energy_gap    = abs(song.get("energy", 0.5) - user_prefs.get("energy", 0.5))
    energy_points = round(MAX_ENERGY_POINTS * (1 - energy_gap), 3)
    score        += energy_points
    reasons.append(f"energy proximity (+{energy_points:.2f})")

    # Acoustic bonus
    if user_prefs.get("likes_acoustic", False) and song.get("acousticness", 0) >= 0.7:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic bonus (+{ACOUSTIC_BONUS})")

    return round(score, 3), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Rank all songs by score and return the top-k results.

    Returns a list of (song_dict, score, explanation_string) tuples.
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    # sorted() keeps the original list intact; sort descending by score
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, ", ".join(reasons)) for song, score, reasons in ranked[:k]]