"""
Market Debunk Tamil - Evolutionary Strategy Memory
Manages the living playbook (state/evolutionary_playbook.json) for continuous
improvement of Tamil/Tanglish financial carousels.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.config import STATE_DIR

logger = logging.getLogger("TamilEvolutionaryMemory")

DEFAULT_PLAYBOOK: Dict[str, Any] = {
    "version": "2.0.0",
    "total_cycles_recorded": 0,
    "archetype_weights": {
        "SHOCKING_MYTH": 1.3,
        "MATH_BREAKDOWN": 1.3,
        "INSTITUTIONAL_SECRET": 1.1,
    },
    "learned_rules": [
        "Use phonetic Tamil Unicode for financial loanwords: 'மியூச்சுவல் ஃபண்ட்', 'ரிட்டர்ன்ஸ்', 'டிவிடெண்ட்', 'போர்ட்ஃபோலியோ'.",
        "Slide 1 hook must be strictly 5-8 words in punchy spoken Tanglish rhythm.",
        "Lead with exact rupee figures: '₹34 லட்சம் இழப்பு', '1% கட்டணம்'.",
        "Final slide must end with: 'முழு 8-Slide விளக்கமும் நம்ம Profile-ல இருக்கு. இப்போவே பாருங்க!'"
    ],
    "cycle_history": []
}


class TamilEvolutionaryMemory:
    """Persistent evolutionary memory layer for Tamil carousels."""

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.playbook_file = self.state_dir / "evolutionary_playbook.json"
        self._ensure_playbook()

    def _ensure_playbook(self):
        if not self.playbook_file.exists():
            try:
                with open(self.playbook_file, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_PLAYBOOK, f, indent=2, ensure_ascii=False)
                logger.info("Initialized Tamil evolutionary playbook at: %s", self.playbook_file)
            except Exception as e:
                logger.error("Failed to initialize Tamil evolutionary playbook: %s", e)

    def load_playbook(self) -> Dict[str, Any]:
        if not self.playbook_file.exists():
            return DEFAULT_PLAYBOOK.copy()
        try:
            with open(self.playbook_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Could not read Tamil evolutionary playbook: %s", e)
            return DEFAULT_PLAYBOOK.copy()

    def get_prompt_directives(self) -> str:
        playbook = self.load_playbook()
        rules = playbook.get("learned_rules", [])
        weights = playbook.get("archetype_weights", {})
        rules_formatted = "\n".join(f"  • {r}" for r in rules[-6:])
        archetype_ranking = ", ".join(f"{k}: {v:.1f}" for k, v in weights.items())

        return (
            "\n═══ TAMIL CONTINUOUS EVOLUTIONARY INTELLIGENCE ═══\n"
            f"Archetype Weights: {archetype_ranking}\n"
            "Learned Spoken Tanglish Rules:\n"
            f"{rules_formatted}\n"
            "═══════════════════════════════════════════════════\n"
        )

    def record_cycle(
        self,
        winning_archetype: str,
        critic_score: float,
        visual_score: float,
        topic_title: str,
        key_learning: Optional[str] = None
    ):
        playbook = self.load_playbook()
        playbook["total_cycles_recorded"] = playbook.get("total_cycles_recorded", 0) + 1

        weights = playbook.get("archetype_weights", {})
        current_w = weights.get(winning_archetype, 1.0)
        combined_score = (critic_score + visual_score) / 2.0
        delta = 0.05 if combined_score >= 8.5 else (0.02 if combined_score >= 7.5 else -0.02)
        weights[winning_archetype] = round(max(0.5, min(2.5, current_w + delta)), 2)
        playbook["archetype_weights"] = weights

        if key_learning and key_learning not in playbook.get("learned_rules", []):
            playbook.setdefault("learned_rules", []).append(key_learning)
            if len(playbook["learned_rules"]) > 12:
                playbook["learned_rules"] = playbook["learned_rules"][-12:]

        record = {
            "cycle": playbook["total_cycles_recorded"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic_title[:80],
            "winning_archetype": winning_archetype,
            "critic_score": round(critic_score, 1),
            "visual_score": round(visual_score, 1),
            "key_learning": key_learning or "Executed spoken Tanglish friction angle."
        }
        playbook.setdefault("cycle_history", []).append(record)
        playbook["cycle_history"] = playbook["cycle_history"][-50:]

        try:
            with open(self.playbook_file, "w", encoding="utf-8") as f:
                json.dump(playbook, f, indent=2, ensure_ascii=False)
            logger.info("✓ Tamil evolutionary memory updated (Cycle #%d | %s | Critic: %.1f | Vision: %.1f)",
                        record["cycle"], winning_archetype, critic_score, visual_score)
        except Exception as e:
            logger.error("Failed to save Tamil evolutionary memory: %s", e)