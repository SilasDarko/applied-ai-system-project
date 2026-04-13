"""
main.py — Command-line runner for the Music Recommender Simulation.

Run with:
    python main.py
"""

from recommender import load_songs, recommend_songs

SONGS_PATH = "songs.csv"

# ---------------------------------------------------------------------------
# User profiles for testing
# ---------------------------------------------------------------------------

PROFILES = {
    "Happy Pop Fan": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "likes_acoustic": False,
    },
    "Chill Lofi Listener": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
    },
    "Intense Rock Head": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
    "Moody Synthwave Driver": {
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.72,
        "likes_acoustic": False,
    },
    "Acoustic Folk Sunday": {
        "genre": "folk",
        "mood": "relaxed",
        "energy": 0.30,
        "likes_acoustic": True,
    },
}


def print_recommendations(profile_name: str, recs: list) -> None:
    """Pretty-print a recommendation list."""
    print(f"\n{'='*55}")
    print(f"  Profile : {profile_name}")
    print(f"{'='*55}")
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        print(f"  {rank}. {song['title']} — {song['artist']}")
        print(f"     Score   : {score:.2f}")
        print(f"     Because : {explanation}")
    print()


def main() -> None:
    songs = load_songs(SONGS_PATH)

    for profile_name, user_prefs in PROFILES.items():
        recs = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(profile_name, recs)


if __name__ == "__main__":
    main()