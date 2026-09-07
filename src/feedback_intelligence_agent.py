"""
Market Debunk Tamil - Feedback Intelligence & Algorithmic Finetuning Agent
Pulls 48-hour analytics performance metrics (saves, reach, impressions, shares)
and synthesizes actionable finetuning directives for downstream generation agents.
Directly enhances the next Tamil Carousel and next Tamil Video in an automated feedback loop.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.config import STATE_DIR

logger = logging.getLogger("FeedbackIntelligenceAgentTamil")


class FeedbackIntelligenceAgent:
    """
    Dedicated agent to close the feedback loop between platform analytics and content generation for Tamil:
    1. Audits 48-hour Meta Graph analytics from the Tamil performance ledger.
    2. Identifies high-performing patterns (Save-to-Reach >= 3.5%) vs low-performing patterns (< 1.5%).
    3. Synthesizes prescriptive Tanglish directives for the next Video and next Carousel.
    4. Writes state/loop_finetuning_directive.json to guide generation agents.
    """

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.state_dir / "analytics_performance_ledger.json"
        self.history_file = self.state_dir / "upload_history.json"
        self.directive_file = self.state_dir / "loop_finetuning_directive.json"

    def audit_and_synthesize(self) -> Dict[str, Any]:
        """
        Processes Tamil ledger data to produce an actionable finetuning directive for
        both video and carousel engines.
        """
        ledger_entries = self._load_ledger()
        upload_records = self._load_upload_history()

        cat_performance = {}
        hook_performance = {}
        all_save_rates = []

        for entry in ledger_entries:
            cat = entry.get("topic_category", "GENERAL")
            hook = entry.get("hook_archetype", "tamil_angle_1")
            sr = float(entry.get("save_to_reach_pct", 0.0))
            all_save_rates.append(sr)

            cat_performance.setdefault(cat, []).append(sr)
            hook_performance.setdefault(hook, []).append(sr)

        avg_save_rate = (sum(all_save_rates) / len(all_save_rates)) if all_save_rates else 2.5

        high_save_hooks = []
        deprecated_hooks = []
        for hook, rates in hook_performance.items():
            avg = sum(rates) / len(rates)
            if avg >= 3.5:
                high_save_hooks.append({"hook": hook, "avg_save_rate": f"{avg:.2f}%", "count": len(rates)})
            elif avg < 1.5 and len(rates) >= 2:
                deprecated_hooks.append({"hook": hook, "avg_save_rate": f"{avg:.2f}%", "reason": "Low dwell & bookmark retention"})

        high_save_cats = [cat for cat, rates in cat_performance.items() if (sum(rates) / len(rates)) >= 3.0]
        low_save_cats = [cat for cat, rates in cat_performance.items() if (sum(rates) / len(rates)) < 1.5 and len(rates) >= 2]

        directive = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "channel": "TAMIL",
            "data_points_analyzed": len(ledger_entries),
            "historical_avg_save_rate_pct": round(avg_save_rate, 2),
            "prioritized_categories": high_save_cats or ["SMART_MONEY", "MARKET_TRAPS", "MUTUAL_FUNDS_TRUTH"],
            "deprecated_categories": low_save_cats,
            "high_performing_hooks": high_save_hooks,
            "deprecated_hooks": deprecated_hooks,
            "video_finetuning_directive": {
                "opening_3s_hook": (
                    "Mandatory Tanglish contrarian shock with citable rupee anchor. "
                    "Open immediately with institutional mechanism (e.g. 'Mutual Fund-ல் ₹34 Lakhs ரகசிய கசிவு!')."
                ),
                "pacing_calibration": (
                    "Introduce hard mathematical friction between seconds 4 and 10 in conversational Tanglish "
                    "(e.g. '1% fee சின்ன விஷயம்னு நினைப்பீங்க, ஆனா 20 வருஷத்துல...')."
                ),
                "visual_friction": "Tamil typography with high contrast highlight box; photoreal amber-teal lighting.",
                "retention_cta": "End with Tanglish bookmark trigger: 'அடுத்த trade-க்கு முன் இந்த checklist-ஐ Save பண்ணி வச்சுக்கோங்க.'"
            },
            "carousel_finetuning_directive": {
                "slide_1_hook_bias": "Tanglish contrarian curiosity gap with exactly one <span class='highlight-box'>...</span> tag.",
                "slide_2_3_mechanism": "Lead with the exact citable mathematical formula or institutional orderflow disparity on Slide 2.",
                "slide_8_dual_cta": "Separate personal saving from peer sharing (Save & Share)."
            },
            "prompt_injection_snippet": (
                f"TAMIL ALGORITHMIC REINFORCEMENT DIRECTIVE: Historical performance shows Tamil audiences respond to institutional order flow "
                f"and hidden fee debunks with an average save rate of {avg_save_rate:.1f}%. "
                f"Prioritize topics covering {', '.join(high_save_cats or ['Smart Money', 'Market Traps'])}. "
                f"Ensure opening 3s / Slide 1 deliver immediate contrarian friction in natural conversational Tanglish."
            )
        }

        self._save_directive(directive)
        logger.info(
            "✓ FeedbackIntelligenceAgentTamil: Synthesized loop finetuning directive (Analyzed %d posts | Avg Save: %.2f%%).",
            len(ledger_entries), avg_save_rate
        )
        return directive

    def get_prompt_injection(self) -> str:
        """Returns the dynamic prompt injection snippet for downstream LLM agents."""
        if self.directive_file.exists():
            try:
                with open(self.directive_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("prompt_injection_snippet", "")
            except Exception:
                pass
        return (
            "TAMIL ALGORITHMIC REINFORCEMENT: Frame every insight around institutional liquidity mechanics "
            "vs retail investor traps in conversational Tanglish to optimize algorithmic dwell and bookmark save rates."
        )

    def _load_ledger(self) -> List[Dict[str, Any]]:
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Could not read analytics ledger: %s", e)
        return []

    def _load_upload_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("uploads", []) if isinstance(data, dict) else data
            except Exception as e:
                logger.warning("Could not read upload history: %s", e)
        return []

    def _save_directive(self, directive: Dict[str, Any]):
        try:
            with open(self.directive_file, "w", encoding="utf-8") as f:
                json.dump(directive, f, indent=2, ensure_ascii=False)
            logger.info("✓ Saved loop finetuning directive to: %s", self.directive_file)
        except Exception as e:
            logger.error("Failed to save finetuning directive: %s", e)
