"""
test_recommender.py  —  Test suite for the Applied AI Music Recommender.

Covers:
  - Original scoring engine (unit tests, preserved from Module 3)
  - Confidence scoring
  - Catalog loading (happy path + edge cases)
  - Input guardrails
  - AI interpreter profile parsing (no API call required — uses internal parser)
  - End-to-end recommend() pipeline
"""

import csv
import os
import sys
import tempfile
import pytest

# Allow running from repo root: pytest tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender   import (
    Song, UserProfile, score_song, compute_confidence,
    recommend, load_catalog, MAX_SCORE,
)
from src.logger_setup  import validate_input
from src.ai_interpreter import _parse_profile, _fallback_profile


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def make_song(**kwargs) -> Song:
    defaults = dict(
        title="Test Song", artist="Test Artist",
        genre="pop", mood="happy",
        energy=0.7, tempo_bpm=120,
        valence=0.8, danceability=0.75,
        acousticness=0.2,
    )
    defaults.update(kwargs)
    return Song(**defaults)


def make_profile(**kwargs) -> UserProfile:
    defaults = dict(genre="pop", mood="happy", energy=0.7, likes_acoustic=False)
    defaults.update(kwargs)
    return UserProfile(**defaults)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Scoring engine — original logic
# ──────────────────────────────────────────────────────────────────────────────

class TestScoringEngine:

    def test_perfect_match_scores_maximum(self):
        song    = make_song(genre="pop", mood="happy", energy=0.7, acousticness=0.9)
        profile = make_profile(genre="pop", mood="happy", energy=0.7, likes_acoustic=True)
        assert score_song(song, profile) == pytest.approx(MAX_SCORE, abs=0.001)

    def test_genre_mismatch_loses_genre_points(self):
        song    = make_song(genre="rock", mood="happy", energy=0.7)
        profile = make_profile(genre="pop", mood="happy", energy=0.7)
        score   = score_song(song, profile)
        assert score < MAX_SCORE - 1.9   # lost genre points

    def test_mood_mismatch_loses_mood_points(self):
        song    = make_song(genre="pop", mood="sad", energy=0.7)
        profile = make_profile(genre="pop", mood="happy", energy=0.7)
        score   = score_song(song, profile)
        assert score < MAX_SCORE - 0.9   # lost mood points

    def test_energy_distance_penalised(self):
        song_close = make_song(energy=0.71)
        song_far   = make_song(energy=0.1)
        profile    = make_profile(energy=0.7)
        assert score_song(song_close, profile) > score_song(song_far, profile)

    def test_acoustic_bonus_only_when_high_acousticness(self):
        song_acoustic    = make_song(acousticness=0.8)
        song_not_acoustic = make_song(acousticness=0.3)
        profile          = make_profile(likes_acoustic=True)
        assert score_song(song_acoustic, profile) > score_song(song_not_acoustic, profile)

    def test_acoustic_bonus_not_awarded_when_user_dislikes(self):
        song    = make_song(acousticness=0.9)
        profile = make_profile(likes_acoustic=False)
        no_bonus = score_song(song, profile)
        profile2 = make_profile(likes_acoustic=True)
        with_bonus = score_song(song, profile2)
        assert with_bonus > no_bonus

    def test_score_never_negative(self):
        song    = make_song(genre="folk", mood="sad", energy=1.0, acousticness=0.0)
        profile = make_profile(genre="pop", mood="happy", energy=0.0)
        assert score_song(song, profile) >= 0.0

    def test_score_never_exceeds_max(self):
        song    = make_song(genre="pop", mood="happy", energy=0.7, acousticness=0.95)
        profile = make_profile(genre="pop", mood="happy", energy=0.7, likes_acoustic=True)
        assert score_song(song, profile) <= MAX_SCORE + 0.001


# ──────────────────────────────────────────────────────────────────────────────
# 2. Confidence scoring
# ──────────────────────────────────────────────────────────────────────────────

class TestConfidenceScoring:

    def test_max_score_gives_confidence_one(self):
        assert compute_confidence(MAX_SCORE) == pytest.approx(1.0)

    def test_zero_score_gives_confidence_zero(self):
        assert compute_confidence(0.0) == 0.0

    def test_confidence_clamped_at_one(self):
        assert compute_confidence(MAX_SCORE * 2) == pytest.approx(1.0)

    def test_mid_score_confidence_in_range(self):
        conf = compute_confidence(MAX_SCORE / 2)
        assert 0.0 < conf < 1.0


# ──────────────────────────────────────────────────────────────────────────────
# 3. Catalog loading
# ──────────────────────────────────────────────────────────────────────────────

class TestCatalogLoading:

    def _write_csv(self, rows, tmp_path):
        path = os.path.join(tmp_path, "songs.csv")
        fieldnames = ["title","artist","genre","mood","energy",
                      "tempo_bpm","valence","danceability","acousticness"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        return path

    def test_loads_valid_csv(self, tmp_path):
        path = self._write_csv([
            dict(title="Song A", artist="A", genre="pop", mood="happy",
                 energy=0.7, tempo_bpm=120, valence=0.8, danceability=0.7, acousticness=0.2)
        ], str(tmp_path))
        songs = load_catalog(path)
        assert len(songs) == 1
        assert songs[0].title == "Song A"

    def test_missing_file_returns_empty(self):
        songs = load_catalog("/nonexistent/path/songs.csv")
        assert songs == []

    def test_malformed_row_skipped(self, tmp_path):
        path = self._write_csv([
            dict(title="Good", artist="A", genre="pop", mood="happy",
                 energy=0.7, tempo_bpm=120, valence=0.8, danceability=0.7, acousticness=0.2),
            dict(title="Bad",  artist="B", genre="pop", mood="happy",
                 energy="NOT_A_FLOAT", tempo_bpm=120, valence=0.8, danceability=0.7, acousticness=0.2),
        ], str(tmp_path))
        songs = load_catalog(path)
        assert len(songs) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 4. Input guardrails
# ──────────────────────────────────────────────────────────────────────────────

class TestGuardrails:

    def test_valid_input_passes(self):
        ok, text = validate_input("Something chill for studying")
        assert ok is True
        assert "chill" in text

    def test_too_short_rejected(self):
        ok, msg = validate_input("hi")
        assert ok is False

    def test_too_long_rejected(self):
        ok, msg = validate_input("a" * 600)
        assert ok is False

    def test_non_string_rejected(self):
        ok, msg = validate_input(12345)   # type: ignore
        assert ok is False

    def test_whitespace_stripped(self):
        ok, text = validate_input("   happy pop music   ")
        assert ok is True
        assert text == "happy pop music"

    def test_empty_string_rejected(self):
        ok, msg = validate_input("")
        assert ok is False


# ──────────────────────────────────────────────────────────────────────────────
# 5. AI profile parser (no API call)
# ──────────────────────────────────────────────────────────────────────────────

class TestProfileParser:

    def test_valid_json_parsed_correctly(self):
        raw = '{"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": true}'
        profile = _parse_profile(raw)
        assert profile.genre == "lofi"
        assert profile.mood  == "chill"
        assert profile.energy == pytest.approx(0.3)
        assert profile.likes_acoustic is True

    def test_invalid_genre_defaults_to_pop(self):
        raw = '{"genre": "jazz", "mood": "happy", "energy": 0.5, "likes_acoustic": false}'
        profile = _parse_profile(raw)
        assert profile.genre == "pop"

    def test_energy_clamped_above_one(self):
        raw = '{"genre": "pop", "mood": "happy", "energy": 2.5, "likes_acoustic": false}'
        profile = _parse_profile(raw)
        assert profile.energy <= 1.0

    def test_energy_clamped_below_zero(self):
        raw = '{"genre": "pop", "mood": "happy", "energy": -0.5, "likes_acoustic": false}'
        profile = _parse_profile(raw)
        assert profile.energy >= 0.0

    def test_fallback_profile_is_valid(self):
        p = _fallback_profile()
        assert p.genre in ["pop", "rock", "lofi", "folk", "synthwave", "electronic"]
        assert p.mood  in ["happy", "sad", "chill", "intense"]


# ──────────────────────────────────────────────────────────────────────────────
# 6. End-to-end recommend() pipeline
# ──────────────────────────────────────────────────────────────────────────────

class TestRecommendPipeline:

    @pytest.fixture
    def catalog(self):
        return [
            make_song(title="Pop Hit",   genre="pop",  mood="happy", energy=0.8),
            make_song(title="Rock Song", genre="rock", mood="intense", energy=0.9),
            make_song(title="Lofi Vibe", genre="lofi", mood="chill", energy=0.3),
            make_song(title="Folk Tale", genre="folk", mood="sad",   energy=0.2),
            make_song(title="Pop Bop",   genre="pop",  mood="happy", energy=0.75),
        ]

    def test_returns_top_k_results(self, catalog):
        profile = make_profile(genre="pop", mood="happy", energy=0.8)
        results = recommend(profile, catalog, top_k=3)
        assert len(results) == 3

    def test_top_result_is_best_match(self, catalog):
        profile = make_profile(genre="pop", mood="happy", energy=0.8)
        results = recommend(profile, catalog, top_k=5)
        assert results[0][0].title == "Pop Hit"

    def test_results_sorted_descending(self, catalog):
        profile = make_profile()
        results = recommend(profile, catalog, top_k=5)
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_empty_catalog_returns_empty(self):
        results = recommend(make_profile(), [], top_k=5)
        assert results == []

    def test_confidence_values_in_range(self, catalog):
        profile = make_profile()
        results = recommend(profile, catalog, top_k=5)
        for _, _, conf in results:
            assert 0.0 <= conf <= 1.0