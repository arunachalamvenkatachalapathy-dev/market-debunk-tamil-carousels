"""
Market Debunk Tamil - Creative Darwinism & Critic Agent
Generates 3 distinct Tanglish narrative angles, scores them on cultural & financial impact,
and selects the definitive winning candidate.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from src.config import settings

logger = logging.getLogger("TamilCreativeCriticAgent")


class TamilCreativeCriticAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.models = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"]

    def _call_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        for m in self.models:
            try:
                cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7)
                if "3.7" in m:
                    cfg.thinking_config = types.ThinkingConfig(thinking_budget=512)
                res = self.client.models.generate_content(model=m, contents=prompt, config=cfg)
                if res.text:
                    clean = res.text.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:]
                    if clean.endswith("```"):
                        clean = clean[:-3]
                    return json.loads(clean.strip())
            except Exception as e:
                logger.warning("TamilCreativeCriticAgent (%s) attempt failed: %s", m, e)
                continue
        return None

    def generate_and_evaluate(self, topic_data: Dict[str, Any], evolutionary_directives: str = "") -> Dict[str, Any]:
        title = topic_data.get("title", "")
        summary = topic_data.get("summary", "") or topic_data.get("context", "")

        prompt = f"""You are an elite Tamil Financial Analyst and Viral Carousel Critic.
Topic: "{title}"
Context: {summary[:1200]}

{evolutionary_directives}

TASK:
1. Generate THREE distinct conversational Spoken Tanglish carousel angles:
   - Candidate A (Archetype: SHOCKING_MYTH): Expose a dangerous misconception retail investors blindly believe.
   - Candidate B (Archetype: MATH_BREAKDOWN): Break down the exact rupee loss caused by hidden costs/fees.
   - Candidate C (Archetype: INSTITUTIONAL_SECRET): Expose what smart money institutions do while retail traders panic.

2. Act as a critical editor. Score each candidate (0-10):
   - curiosity_gap: Will a Tamil speaker immediately swipe?
   - retail_actionability: Clear money defense?
   - data_density: Exact rupee/percentage numbers cited?
   - tanglish_rhythm: Natural spoken rhythm without bookish Tamil?

Return JSON strictly:
{{
  "candidates": [
    {{
      "id": "A",
      "archetype": "SHOCKING_MYTH",
      "headline_hook": "...",
      "highlight_word": "1-2 words for <span class='highlight-box'>",
      "scores": {{"total": 35.0}},
      "critic_critique": "..."
    }},
    {{
      "id": "B",
      "archetype": "MATH_BREAKDOWN",
      "headline_hook": "...",
      "highlight_word": "...",
      "scores": {{"total": 36.0}},
      "critic_critique": "..."
    }},
    {{
      "id": "C",
      "archetype": "INSTITUTIONAL_SECRET",
      "headline_hook": "...",
      "highlight_word": "...",
      "scores": {{"total": 34.0}},
      "critic_critique": "..."
    }}
  ],
  "winning_candidate_id": "B",
  "selection_rationale": "...",
  "final_editorial_directive": "Tanglish copywriting instructions."
}}"""

        result = self._call_llm(prompt)
        if not result or not result.get("candidates"):
            return {
                "winning_candidate": {
                    "id": "A",
                    "archetype": "SHOCKING_MYTH",
                    "headline_hook": f"{title[:40]} - நீங்கள் அறியாத உண்மை",
                    "highlight_word": "அறியாத உண்மை",
                    "scores": {"total": 34.0}
                },
                "critic_score": 8.5,
                "archetype": "SHOCKING_MYTH",
                "selection_rationale": "Fallback Tanglish anchor."
            }

        candidates = result.get("candidates", [])
        winner_id = result.get("winning_candidate_id", "A")
        winner = next((c for c in candidates if c.get("id") == winner_id), candidates[0])
        total_score = winner.get("scores", {}).get("total", 34.0)
        normalized_score = round(total_score / 4.0, 1)

        logger.info("🏆 Tamil Creative Darwinism: Selected %s (%s) score: %.1f/10",
                    winner.get("id"), winner.get("archetype"), normalized_score)

        return {
            "winning_candidate": winner,
            "critic_score": normalized_score,
            "archetype": winner.get("archetype", "SHOCKING_MYTH"),
            "selection_rationale": result.get("selection_rationale", ""),
            "final_editorial_directive": result.get("final_editorial_directive", "")
        }