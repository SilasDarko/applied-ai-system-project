# 🎵 Applied AI Music Recommender

> A natural-language music recommendation system built on Claude AI, RAG retrieval, confidence scoring, and structured logging — extended from a Module 3 rule-based recommender.

---

## 🎬 Demo Walkthrough

> 📹 **[Loom video link — add yours here after recording]**

---

## 📌 Base Project

**Original project:** `ai110-module3show-musicrecommendersimulation-starter`

The original system was a pure rule-based, content-based music recommender. Given a hardcoded user profile (favourite genre, preferred mood, target energy level, and acoustic preference), it scored every song in a 20-track CSV catalog using a weighted formula and returned the top-K most relevant tracks with plain-English explanations. There was no AI, no API, and no natural-language input — the profile had to be defined directly in code.

---

## 🚀 What This System Does

This final project extends the original recommender into a full applied AI pipeline. A user types a natural-language request — anything from *"upbeat music for my morning run"* to *"something melancholy and acoustic for a rainy evening"* — and the system:

1. **Validates** the input through a guardrail layer
2. **Interprets** the request using Claude AI, extracting a structured music profile
3. **Retrieves** candidate songs from the catalog (RAG)
4. **Scores** every song using the original weighted algorithm
5. **Generates** a confidence score and a personalized AI explanation for each recommendation
6. **Logs** every step to `logs/app.log` for reliability auditing

---

## 🏗 Architecture

```
User input (natural language)
        │
        ▼
┌─────────────────────┐
│   Input guardrail   │  ← validates length, characters, sanitizes
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Claude AI (Haiku)  │  ← maps text → {genre, mood, energy, likes_acoustic}
│  (ai_interpreter)   │    (AI feature #1 — natural language understanding)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   RAG Retriever     │  ← loads songs.csv as retrieval context
│   (recommender)     │    (AI feature #2 — retrieval-augmented generation)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Scoring Engine     │  ← original weighted rule system (preserved)
│  (recommender)      │    genre +2.0 | mood +1.0 | energy 0-1.5 | acoustic +0.5
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Confidence Scoring │  ← normalised 0–1 score per recommendation
│  + AI Explanation   │    (reliability feature + AI feature #3)
└────────┬────────────┘
         │
         ▼
  Top-K results + per-song explanations
         │
         └──► logs/app.log  (every step logged at DEBUG/INFO/WARNING)
```

![System architecture diagram](assets/architecture.png)

---

## ✨ AI Features

| Feature | Implementation |
|---|---|
| **RAG** | `songs.csv` catalog is loaded and passed as retrieval context; Claude selects from real catalog values (genre, mood) only |
| **Natural Language AI** | Claude Haiku maps free-text → structured profile via a strict JSON system prompt |
| **AI Explanations** | Claude generates a one-sentence personalised reason for each recommended song |
| **Confidence Scoring** | Each result includes a normalised 0–1 score showing how well it matches the profile |

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.11 or higher
- An Anthropic API key (free tier works) — get one at [console.anthropic.com](https://console.anthropic.com)

### Step 1 — Clone and enter the repo

```bash
git clone https://github.com/SilasDarko/applied-ai-system-project.git
cd applied-ai-system-project
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set your API key

```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

> 💡 Add this line to your `~/.zshrc` or `~/.bash_profile` to avoid repeating it every session.

### Step 5 — Run the app

**Interactive mode** (recommended):
```bash
python -m src.main
```

**Demo mode** (3 pre-set queries, no typing needed):
```bash
python -m src.main --demo
```

### Step 6 — Run the test suite

```bash
pytest tests/ -v
```

---

## 💬 Sample Interactions

### Example 1 — Morning run energy

```
You asked for: I want something upbeat and energetic for my morning run

🤖 Interpreting your request with Claude AI...
   Detected profile → genre: pop, mood: happy, energy: 90%, acoustic: False

🎵 Top 5 recommendations:

  1. Gym Hero — PowerBeats
     Confidence: ██████████  97%
     This high-energy pop track perfectly matches your upbeat workout vibe.

  2. Sunflower Fields — The Bloom
     Confidence: █████████░  88%
     A feel-good pop anthem with the bright energy to keep your pace up.

  3. Pop Confetti — Glitter Lane
     Confidence: ████████░░  81%
     Upbeat and danceable, ideal for staying motivated on a run.
```

### Example 2 — Rainy study session

```
You asked for: chill acoustic music for a rainy study session

🤖 Interpreting your request with Claude AI...
   Detected profile → genre: folk, mood: chill, energy: 30%, acoustic: True

🎵 Top 5 recommendations:

  1. Mountain Echo — Pine & Stone
     Confidence: ██████████  98%
     A gentle acoustic folk track that creates the perfect calm study atmosphere.

  2. Porch Swing Summer — Maple Row
     Confidence: █████████░  91%
     Soft, warm acoustic guitar perfectly suited for a focused, unhurried session.

  3. River Song — Hollow Reed
     Confidence: ████████░░  83%
     A melancholy acoustic track that pairs well with quiet, rainy afternoons.
```

### Example 3 — Invalid input (guardrail demo)

```
You asked for: 

⚠  Please describe what you want to hear (at least 3 characters).
```

---

## 🔍 Design Decisions

**Why Claude Haiku for interpretation?**  
Haiku is fast (sub-second) and cheap — perfect for structured extraction tasks where we just need JSON back, not a long response. The system prompt constrains the output to valid catalog values, so the model has very little room to hallucinate.

**Why preserve the original scoring engine?**  
The weighted rule system is transparent and debuggable, which is valuable in a learning context. The AI layer handles the hard part (understanding messy human language) while the rule engine handles the easy part (deterministic ranking). Separating them also means tests can cover the scoring logic without any API calls.

**Why RAG over fine-tuning?**  
The catalog has only 20 songs — far too few to fine-tune on. RAG lets the AI reference real catalog data at inference time, which guarantees the AI only recommends genres and moods that actually exist in the catalog.

**Trade-offs made:**
- The catalog is still small (20 songs), so genre over-representation remains a bias
- Energy is the only continuous feature used in scoring; valence and danceability are loaded but unused
- Explanations are generated per song, which adds ~1 second of latency per result

---

## 🧪 Testing Summary

Run with: `pytest tests/ -v`

| Test class | Tests | Focus |
|---|---|---|
| `TestScoringEngine` | 8 | Original weighted scoring logic |
| `TestConfidenceScoring` | 4 | Normalisation and clamping |
| `TestCatalogLoading` | 3 | CSV parsing, missing files, malformed rows |
| `TestGuardrails` | 6 | Input validation edge cases |
| `TestProfileParser` | 5 | JSON parsing, invalid values, energy clamping |
| `TestRecommendPipeline` | 5 | End-to-end ranking and confidence range |

**Total: 31 tests**

Results: All 31 tests pass without an API key. AI-specific paths (interpretation, explanation generation) fall back gracefully and are covered by parser unit tests.

Key findings:
- Confidence averages ~0.85 when genre matches; drops to ~0.45 when no genre match exists
- The guardrail correctly blocks empty strings, overly long inputs, and non-text types
- Malformed CSV rows are skipped without crashing the pipeline

---

## 🤔 Reflection and Ethics

### Limitations and biases
- Genre carries the highest fixed weight (2.0), meaning genre-rich parts of the catalog dominate results even when other songs are a better fit on energy or mood
- The catalog has only 20 songs, so some genres (e.g. folk) are underrepresented
- Claude's interpretation of ambiguous requests (e.g. "something sad but danceable") may vary between runs
- The system has no memory — it cannot learn that a user always skips a specific artist

### Misuse potential and prevention
- The AI generates free-text explanations, which could theoretically be prompted to produce inappropriate content; the system prompt tightly constrains output format
- The guardrail layer rejects unusual characters and very long inputs, reducing prompt injection risk

### What surprised me during testing
- Claude Haiku was remarkably consistent at mapping natural language to valid JSON profiles, even for creative or unusual phrasing
- Confidence scores below 0.5 were logged as warnings and often corresponded to cases where the user's described genre had zero matches in the catalog
- Removing the mood scoring weight (as in the original experiments) barely changed the top result but noticeably reshuffled positions 2–5

### AI collaboration
- **Helpful suggestion:** Claude suggested separating the AI interpretation layer (`ai_interpreter.py`) from the scoring engine (`recommender.py`) as distinct modules — this made the codebase much easier to test because the scoring unit tests require zero API calls
- **Flawed suggestion:** Claude initially suggested using `claude-opus-4-6` for the structured JSON extraction step. In practice, Haiku is faster, cheaper, and equally accurate for this constrained task; Opus would add unnecessary latency and cost

---

## 📁 Repository Structure

```
applied-ai-system-project/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point — full pipeline
│   ├── recommender.py       # Original scoring engine (preserved)
│   ├── ai_interpreter.py    # Claude AI — NL → profile + explanations
│   └── logger_setup.py      # Logging config + input guardrails
├── data/
│   └── songs.csv            # 20-song catalog
├── tests/
│   └── test_recommender.py  # 31 pytest tests
├── assets/
│   └── architecture.png     # System diagram
├── logs/                    # app.log written here at runtime
├── requirements.txt
├── .gitignore
├── model_card.md
└── README.md
```

---

## 👤 About

Built by Silas Darko as a final project for CodePath AI110.  
Extended from Module 3: `ai110-module3show-musicrecommendersimulation-starter`.