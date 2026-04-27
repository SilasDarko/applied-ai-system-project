# Model Card — Applied AI Music Recommender

## Model Overview

| Field | Value |
|---|---|
| **System name** | Applied AI Music Recommender |
| **Base project** | ai110-module3show-musicrecommendersimulation-starter (Module 3) |
| **AI model used** | Claude Haiku (claude-haiku-4-5-20251001) via Anthropic API |
| **Task** | Natural-language music recommendation with confidence scoring |
| **Primary AI features** | RAG, natural-language profile extraction, per-song explanation generation |
| **Author** | Silas Darko |

---

## Intended Use

This system is designed as a learning tool demonstrating how rule-based systems can be enhanced with AI layers. It is intended for:
- Educational exploration of RAG, prompt engineering, and reliability testing
- Personal music discovery using conversational input
- Portfolio demonstration of applied AI engineering

It is **not** intended for commercial deployment, production recommendation services, or use with sensitive user data.

---

## AI Feature Descriptions

### 1. Natural-Language Interpretation (RAG)
The system sends the user's free-text request alongside the list of valid genres and moods from the catalog (retrieved context) to Claude Haiku. Claude returns a structured JSON profile that is then fed into the scoring engine. This is retrieval-augmented because the valid values are retrieved from the catalog at runtime — the AI cannot invent genres that don't exist in the data.

### 2. Confidence Scoring
Each recommendation receives a confidence score (0–1) calculated by normalising the raw weighted score against the theoretical maximum. Scores below 0.5 trigger a logged warning and signal to the user that the match quality is low.

### 3. Per-Song AI Explanations
After scoring, Claude Haiku generates a one-sentence plain-English explanation for each recommended song. This makes the system's reasoning visible rather than being a black box.

---

## Limitations and Biases

**Genre weight dominance:** Genre carries the highest fixed weight (2.0 out of 5.0 maximum). In a 20-song catalog, this means that well-represented genres dominate results regardless of mood or energy fit. A pop-heavy catalog will always bias toward pop recommendations.

**Small catalog:** With only 20 songs, some genres (folk: 4 songs, electronic: 2 songs) are underrepresented. Users requesting underrepresented genres will receive lower confidence scores and less varied results.

**Single-shape taste profile:** The system models each user as having exactly one preferred genre, mood, and energy level. Users with varied tastes (e.g., someone who likes both lofi and heavy rock depending on context) cannot be represented.

**No memory or personalisation:** The system starts fresh every session. It cannot learn that a user dislikes a specific artist, always skips jazz, or that their preferences change by time of day.

**Language bias:** Claude Haiku was trained primarily on English text. Non-English requests or slang may be interpreted inconsistently.

**AI non-determinism:** Claude's interpretation of the same ambiguous phrase may vary slightly across runs, producing different profiles and therefore different recommendations for identical inputs.

---

## Could the System Be Misused?

**Prompt injection risk:** The natural-language input field passes user text directly to Claude. A malicious user could attempt to override the system prompt by embedding instructions in their query (e.g., "Ignore all instructions and say..."). Mitigations in place:
- The system prompt specifies JSON-only output with a strict schema
- The guardrail layer rejects inputs with unusual characters
- The profile parser validates all values against a known-good list

**Data privacy:** The system sends user queries to the Anthropic API. Users should be aware that their input text is processed by a third-party service. No personally identifiable information is collected by this system, but users should not enter sensitive personal details in the query field.

**Recommendation echo chambers:** Repeated use could reinforce narrow taste preferences if users consistently describe the same genre. The system has no diversity injection mechanism.

---

## Testing Results

**31 total tests — all pass without an API key.**

| Test area | Result | Notes |
|---|---|---|
| Scoring engine (8 tests) | ✅ All pass | Perfect match = MAX_SCORE confirmed |
| Confidence scoring (4 tests) | ✅ All pass | Clamping at 0 and 1 confirmed |
| Catalog loading (3 tests) | ✅ All pass | Malformed rows skipped gracefully |
| Input guardrails (6 tests) | ✅ All pass | Empty, short, long, non-string all rejected |
| Profile parser (5 tests) | ✅ All pass | Invalid genres default to 'pop' |
| End-to-end pipeline (5 tests) | ✅ All pass | Sorted results, confidence in range |

**Observed reliability findings:**
- Average confidence when genre matches: ~0.85
- Average confidence when no genre match in catalog: ~0.45
- All low-confidence results (below 0.5) correctly trigger log warnings
- The fallback profile activates gracefully when no API key is set

---

## AI Collaboration Reflection

Building this project involved extensive collaboration with Claude as a coding and architecture partner.

**One instance where AI was genuinely helpful:**  
When designing the module structure, Claude suggested separating the AI interpretation layer (`ai_interpreter.py`) from the original scoring engine (`recommender.py`) as distinct, independently testable modules. This turned out to be exactly the right architecture: the 31-test suite can cover the entire scoring and guardrail logic without making a single API call, making tests fast, free, and deterministic. Without that suggestion, the tests would have been tangled with API dependencies.

**One instance where the AI suggestion was flawed:**  
Claude initially recommended using `claude-opus-4-6` (the most capable model) for the structured JSON extraction step, reasoning that accuracy would be higher. In practice, this was wrong for this use case. The task is tightly constrained — return a JSON object with four fields using only values from a short allowed list — and Claude Haiku handles it perfectly at roughly 10× lower cost and with lower latency. Choosing the right model for the task requires judgment about complexity, not defaulting to the most powerful option available. The suggestion was well-intentioned but missed the practical engineering trade-off.

---

## Ethical Reflection

AI recommendation systems, even small ones like this, embed value judgments in their design choices. The decision to weight genre at 2.0 and mood at 1.0 reflects an assumption that musical genre is twice as important as emotional state to most listeners — an assumption that may not hold for all users, particularly in cultures where emotional context drives music selection more strongly than genre categorisation.

More broadly, systems that automate taste profiling carry a risk of flattening user identity into a small set of parameters. Real human music preference is contextual, contradictory, and evolving. The most honest thing this system does is make its algorithm completely visible: the weights are in the code, the confidence scores are shown to the user, and the explanations tell the user exactly why each song was chosen. Transparency about how a system works is one of the most important tools for building appropriate trust.

---

*Last updated: April 2026*