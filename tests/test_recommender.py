"""
test_recommender.py — Tests for the OOP Recommender interface.
Run with: pytest test_recommender.py
"""

from recommender import Song, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # The pop/happy/high-energy song should rank first
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_genre_match_scores_higher_than_no_match():
    """A song that matches genre should outscore one that does not."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    pop_song  = rec.songs[0]   # genre == "pop"
    lofi_song = rec.songs[1]   # genre == "lofi"

    score_pop,  _ = rec._score(user, pop_song)
    score_lofi, _ = rec._score(user, lofi_song)

    assert score_pop > score_lofi


def test_acoustic_bonus_applied():
    """A user who likes acoustic music should get a bonus for acoustic tracks."""
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    user_no_acoustic = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    lofi_song = rec.songs[1]   # acousticness == 0.9

    score_with, _    = rec._score(user, lofi_song)
    score_without, _ = rec._score(user_no_acoustic, lofi_song)

    assert score_with > score_without


def test_recommend_k_limits_results():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    assert len(rec.recommend(user, k=1)) == 1
    assert len(rec.recommend(user, k=2)) == 2