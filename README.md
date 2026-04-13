# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommendation system. Given a user's taste profile — favorite genre, preferred mood, target energy level, and whether they enjoy acoustic music, the system scores every song in a catalog and returns the top-k most relevant tracks along with a plain-English explanation for each recommendation.
The system is intentionally simple: no machine learning, no user-behavior data. It is designed to make the inner logic of a recommender completely visible and debuggable, which is what makes it a useful learning tool.

## How The System Works

Real-world recommenders like Spotify use two broad approaches. Collaborative filtering finds users whose listening history looks like yours and suggests what they enjoyed. Content-based filtering ignores other users entirely — it just compares the features of songs (tempo, energy, genre) directly to a profile of your stated preferences. This project implements content-based filtering.
Each song in songs.csv has six numeric or categorical attributes: genre, mood, energy, tempo_bpm, valence, danceability, and acousticness. A user profile stores four preferences: genre, mood, energy, and likes_acoustic.

Algorithm Recipe:
Rule                                                                 Points
Genre matches user's favorite genre                                  +2.0
Mood matches user's favorite mood                                    +1.0
Energy closeness (max when gap = 0)                                  0 – 1.5
Acoustic bonus (if user likes acoustic and song ≥ 0.7)               +0.5

Energy is scored as 1.5 × (1 − |song_energy − target_energy|), rewarding closeness rather than just high or low values. Songs are then ranked by total score, highest first.
Potential bias note: Genre carries the highest fixed weight (2.0). If a user's favorite genre is well-represented in the catalog, results will be dominated by that genre even when other songs are a better energy or mood fit.

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Experiment 1 — Default weights, five profiles
Running five profiles (Happy Pop, Chill Lofi, Intense Rock, Moody Synthwave, Acoustic Folk) produced intuitively correct results in every case. The top result for each profile matched genre + mood exactly and scored around 4.5–5.0 out of a theoretical max of 5.0.
Observation: The genre weight (2.0) is strong enough that songs without a genre match rarely crack the top 3 unless their energy is very close to the user's target.

Experiment 2 — Genre weight halved (1.0 → 0.5 effectively, energy doubled)
When MAX_ENERGY_POINTS was raised to 3.0 and GENRE_MATCH_POINTS lowered to 1.0, the Happy Pop profile started recommending high-energy non-pop songs like Gym Hero and Thunderstruck Revival above genre matches with lower energy. The list felt less intuitive — genre is a stronger human signal than raw energy.
Conclusion: The default weights (genre 2.0, mood 1.0, energy 0–1.5) strike a better balance.

Experiment 3 — Mood removed
Commenting out the mood check barely changed the top result but reshuffled positions 2–5. Mood is a useful tiebreaker but not a primary driver in the current dataset.

## Limitations and Risks

- The catalog has only 20 songs. With so few tracks, genre over-representation is inevitable (e.g., 3 lofi tracks vs. 1 folk track).
- Energy is the only numerical feature used for scoring. Valence, danceability, and tempo_bpm are loaded but ignored, leaving significant signal on the table.
- The system has no memory — it cannot learn that a user always skips jazz or replays a specific song.
- All users are treated as having a single "taste shape." A user who likes both chill lofi AND intense metal cannot be represented.



---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---