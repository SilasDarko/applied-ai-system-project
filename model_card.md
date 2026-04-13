# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeFinder 1.0 — A content-based music recommendation simulator.

---

## 2. Intended Use  

VibeFinder is designed to suggest songs from a small catalog that match a user's stated taste preferences: favorite genre, preferred mood, target energy level, and acoustic preference. It is built for classroom exploration only — to make the inner logic of a recommendation algorithm visible and inspectable, not for use in a real product. It assumes the user can describe their preferences in advance and that those preferences stay constant across a listening session. 

---

## 3. How the Model Works  

The model reads a list of songs from a spreadsheet. Each song has a genre (like "pop" or "rock"), a mood (like "happy" or "intense"), and several 0–1 numbers measuring energy, acousticness, and danceability.
When a user profile is provided, the system goes through every single song and gives it a score:

+2.0 points if the song's genre matches the user's favorite genre.
+1.0 point if the song's mood matches the user's preferred mood.
Up to +1.5 points based on how close the song's energy is to the user's target. A perfect match gives the full 1.5; a song at the opposite end of the energy scale gives 0.
+0.5 bonus if the user likes acoustic music and the song is highly acoustic (score ≥ 0.7).

Once every song has a number, the list is sorted from highest to lowest and the top results are returned along with a plain-English explanation of why each song scored well.
No machine learning is involved. The weights are hand-crafted rules, not learned from data.


## 4. Data  

The catalog is songs.csv, which contains 20 songs after expansion from the original 10. Genres represented include: pop, lofi, rock, metal, r&b, electronic, country, synthwave, folk, hip-hop, jazz, indie pop, and ambient. Moods include: happy, chill, intense, relaxed, moody, focused, dreamy, nostalgic, and melancholy.
The data was created synthetically for this project and does not represent real listener behavior or real songs. Numerical features (energy, valence, danceability, acousticness) are on a 0.0–1.0 scale. Tempo is in BPM.
Gaps in the data: There are no songs representing classical, reggae, blues, or world music. There is no data on lyrics, language, or cultural context. Popularity and release year are not included.

## 5. Strengths  

- When a user's preferred genre is well-represented in the catalog, the top result is almost always an intuitive match (e.g., "pop + happy + high energy" reliably surfaces Sunrise City).
- The energy proximity score means the system avoids recommending songs that are technically the right genre but completely the wrong vibe (e.g., a chill pop song for someone who wants high-energy pop).
- Every recommendation includes a plain-English explanation, making it easy to understand and debug why a result appeared.
- The acoustic bonus rewards users with a specific texture preference, not just genre and mood. 

---

## 6. Limitations and Bias 

Genre dominance: Genre carries a fixed 2.0-point reward — the highest of any single factor. In a catalog with only 1–3 songs per genre, this means the top results are almost always dominated by whichever genre the user specified. Songs from other genres rarely break into the top 3, even if they are a better mood or energy fit.

Small catalog problem: With 20 songs, some genres appear only once (e.g., "metal," "folk," "country"). A user who prefers those genres will receive a single genre match and then be padded with songs from completely different genres. This would not happen in a real platform with millions of tracks.

Single-taste assumption: The system assumes every user has exactly one favorite genre and one favorite mood. Real listeners often enjoy multiple genres or shift preferences by time of day. There is no way to express "I want pop OR indie pop" or to weight two moods simultaneously.

Unused features: Valence, danceability, and tempo_bpm are loaded from the CSV but never used in scoring. A song with very low valence (sadness) will score identically to a high-valence song if their genre, mood, and energy are the same.

Filter bubble risk: Because genre is weighted so heavily, users will consistently receive recommendations within a narrow genre slice. They will rarely be exposed to music from genres they did not specify, even if those songs fit their energy and mood profile perfectly. 

---

## 7. Evaluation  

Five distinct user profiles were tested:

Happy Pop Fan (genre: pop, mood: happy, energy: 0.80, likes_acoustic: false) — Results felt very accurate. Sunrise City ranked first with a near-perfect score of 4.47, which matched intuition. Gym Hero ranked second despite being "intense" rather than "happy," because pop genre + high energy still produced a strong score.

Chill Lofi Listener (genre: lofi, mood: chill, energy: 0.38, likes_acoustic: true) — Results were excellent. The top 3 were all lofi or acoustic-leaning tracks. The acoustic bonus noticeably separated lofi tracks from non-acoustic alternatives.

Intense Rock Head (genre: rock, mood: intense, energy: 0.92, likes_acoustic: false) — Worked well for positions 1–2 (both Voltline rock tracks). Positions 3–5 drifted to pop and metal because there are only 2 rock songs in the catalog — a direct consequence of the small dataset.

Moody Synthwave Driver (genre: synthwave, mood: moody, energy: 0.72, likes_acoustic: false) — Positions 1–2 were near-tied (4.46 each) between the two synthwave songs. Positions 3–5 were generic energy matches with no genre or mood alignment, which felt weak.

Acoustic Folk Sunday (genre: folk, mood: relaxed, energy: 0.30, likes_acoustic: true) — The single folk song (Sunday Porch) scored an almost-perfect 4.99. The rest of the list was filled with acoustic songs from other genres, which was reasonable but underlined the small-catalog problem.

Experiment: Doubling MAX_ENERGY_POINTS to 3.0 and halving GENRE_MATCH_POINTS to 1.0 caused the Happy Pop profile to recommend metal and electronic songs over mood-matched pop songs. This confirmed that genre is the most important human signal and should retain its higher weight.


---

## 8. Future Work  

- Use valence and danceability in scoring. These features are already in the CSV and would help distinguish between a "happy but calm" song and a "happy and danceable" song — a meaningful difference that the current model ignores.
- Add a diversity penalty. If the same artist or genre appears more than once in the top 5, apply a small score reduction to the duplicate. This would produce more varied and surprising recommendations.
- Support multi-genre and multi-mood profiles. Allow users to specify two genres or moods with individual weights (e.g., "70% pop, 30% indie pop"). This would better represent real listener taste.
- Expand the catalog. 20 songs is too small for any genre to be meaningfully represented. A catalog of 200+ songs with balanced genre distribution would make the results far more interesting and reveal whether the scoring logic holds up at scale.



## 9. Personal Reflection  

Building VibeFinder made clear how much work a few simple numbers are doing in real recommendation systems. The gap between "this algorithm makes mathematical sense" and "this recommendation feels right" is surprisingly large — the first version of the energy score rewarded high-energy songs unconditionally, which caused chill lofi fans to get gym workout playlists. Switching to a proximity score (rewarding closeness rather than magnitude) fixed it immediately.

The most interesting discovery was how the genre weight controls the entire character of the system. Raise it and the recommender feels like a genre-sorting machine. Lower it and recommendations become chaotic. The "right" weight is not a math problem — it is a design opinion about what music discovery should feel like.

Real apps like Spotify almost certainly do not hard-code weights like this. They learn them from millions of skips, replays, and playlist adds. But seeing the weights written out explicitly made it much easier to reason about what the system is actually optimizing for — and where it could quietly go wrong for users whose taste doesn't match the majority of the training data. That transparency is something worth preserving even in more complex systems.
