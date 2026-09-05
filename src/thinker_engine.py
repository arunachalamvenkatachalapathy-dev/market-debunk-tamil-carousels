"""
Market Debunk Tamil - Schematic Thinker Layer
Powered by Gemini Thinking Mode.
Performs deterministic error taxonomy, root cause analysis, automated remediation,
and repairs numerical fact mismatches or pipeline exceptions for Tamil carousels.
"""

import json
import logging
import os
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from google import genai
from google.genai import types

from src.config import settings, STATE_DIR

logger = logging.getLogger(__name__)


class ThinkerEngine:
    """
    Intelligent Diagnostic & Auto-Remediation Engine for Tamil companion pipeline.
    Uses Gemini Thinking Mode to diagnose pipeline failures and provide schematic repairs.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model = os.getenv("GEMINI_THINKER_MODEL", "gemini-3.6-flash")
        self.incident_log_path = STATE_DIR / "thinker_incident_report.json"

    def _call_thinking_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Invokes Gemini with explicit thinking budget and strict JSON response."""
        if not self.client:
            logger.warning("ThinkerEngine: GenAI client unavailable.")
            return None

        # Stage 1: Gemini Thinking Models
        models_to_try = [self.model, "gemini-3.7-flash", "gemini-flash-latest"]
        for m in models_to_try:
            try:
                cfg = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=512),
                    response_mime_type="application/json",
                    temperature=0.2
                )
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=cfg
                )
                if response.text:
                    clean_text = response.text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    return json.loads(clean_text.strip())
            except Exception as e:
                logger.warning("ThinkerEngine: Gemini model %s call failed: %s. Trying next...", m, e)

        # Stage 2: First Fallback to Gemma Models
        gemma_models = [settings.GEMMA_FALLBACK_MODEL, "gemma-4-26b-a4b-it"]
        for gm in gemma_models:
            try:
                logger.info("🤖 ThinkerEngine: Falling back to Gemma model: %s...", gm)
                response = self.client.models.generate_content(
                    model=gm,
                    contents=prompt + "\nCRITICAL: Output valid JSON only with no markdown or explanation."
                )
                if response.text:
                    clean_text = response.text.strip()
                    if "```json" in clean_text:
                        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean_text:
                        clean_text = clean_text.split("```")[1].split("```")[0].strip()
                    return json.loads(clean_text)
            except Exception as ge:
                logger.warning("ThinkerEngine: Gemma model %s call failed: %s.", gm, ge)

        return None

    def _record_incident(self, report: Dict[str, Any]) -> None:
        """Persists the diagnostic report into state/thinker_incident_report.json."""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.incident_log_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info("📝 Thinker incident recorded to: %s", self.incident_log_path)
        except Exception as err:
            logger.error("Failed to record thinker incident: %s", err)

    def diagnose_master_pkg_failure(self, path: Optional[str], error: Exception) -> Dict[str, Any]:
        """Diagnoses failure to ingest English master carousel package."""
        prompt = f"""You are the Schematic Thinker Layer for 'Market Debunk Tamil'.
Phase: MASTER_PACKAGE_INGESTION
Target Path: {path}
Exception: {str(error)}
Traceback: {traceback.format_exc()}

Analyze why the English master package could not be consumed and determine fallback.
Output JSON schema:
{{
  "timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "phase": "MASTER_INGESTION",
  "severity": "RECOVERABLE",
  "error_code": "ERR_MASTER_PKG_UNAVAILABLE",
  "root_cause_analysis": "Exact root cause",
  "reproducibility": "TRANSIENT or MISSING_ARTIFACT",
  "automated_remediation": {{
    "action": "STANDALONE_RESEARCH_SOURCING",
    "repaired_payload": null
  }},
  "operator_action_required": false,
  "actionable_instructions": ["Proceed with standalone research sourcing for Tamil carousel."]
}}"""
        res = self._call_thinking_llm(prompt)
        if not res:
            res = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "MASTER_INGESTION",
                "severity": "RECOVERABLE",
                "error_code": "ERR_MASTER_PKG_UNAVAILABLE",
                "root_cause_analysis": f"Failed to ingest master package: {error}",
                "reproducibility": "MISSING_ARTIFACT",
                "automated_remediation": {"action": "STANDALONE_RESEARCH_SOURCING", "repaired_payload": None},
                "operator_action_required": False,
                "actionable_instructions": ["Run standalone research fallback."]
            }
        self._record_incident(res)
        return res

    def diagnose_and_repair_tanglish_failure(
        self,
        topic_data: Dict[str, Any],
        failing_deck: Dict[str, Any],
        validation_report: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Diagnoses Tanglish fact-checking gate failure.
        Attempts schematic auto-repair to reconcile Tanglish slide numbers with verified topic numbers.
        Returns: (is_repaired, repaired_deck, diagnostic_report)
        """
        source_text = f"{topic_data.get('raw_text', '')} {topic_data.get('title', '')} {topic_data.get('source_snippet', '')}"
        prompt = f"""You are the Quantitative Fact-Checker & Thinker Layer for 'Market Debunk Tamil'.
Phase: TANGLISH_EDITORIAL_FACT_CHECK
Validation Error: {validation_report}

TOPIC CONTEXT & NUMBERS:
{source_text[:3000]}

FAILING 6-SLIDE TANGLISH DECK:
{json.dumps(failing_deck, indent=2)}

TASK:
1. Analyze why the Tanglish deck failed the fact-checking gate.
2. Identify the exact financial numbers (₹, %, Lakhs, Cr) from the source topic.
3. Perform an AUTO-REPAIR on the Tanglish slides, inserting the verified numbers into natural Tanglish sentences.
4. Output JSON strictly matching this schema:
{{
  "timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "phase": "TANGLISH_EDITORIAL_FACT_CHECK",
  "severity": "RECOVERABLE",
  "error_code": "ERR_TANGLISH_FACT_CHECK_MISMATCH",
  "root_cause_analysis": "Explanation of numeric mismatch",
  "reproducibility": "DETERMINISTIC",
  "automated_remediation": {{
    "action": "AUTO_REPAIR_PAYLOAD",
    "repaired_payload": {{
      "caption": "Repaired Tanglish caption...",
      "slides": [ ... 6 repaired slide objects ... ]
    }}
  }},
  "operator_action_required": false,
  "actionable_instructions": ["Automated repair applied to match verified topic numbers."]
}}"""

        diag = self._call_thinking_llm(prompt)
        if diag and diag.get("automated_remediation", {}).get("repaired_payload"):
            repaired = diag["automated_remediation"]["repaired_payload"]
            if len(repaired.get("slides", [])) == 6:
                diag["automated_remediation"]["action"] = "AUTO_REPAIR_SUCCESS"
                self._record_incident(diag)
                logger.info("✅ Tamil ThinkerEngine successfully repaired Tanglish slide deck!")
                return True, repaired, diag

        fail_diag = diag or {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "TANGLISH_EDITORIAL_FACT_CHECK",
            "severity": "CRITICAL",
            "error_code": "ERR_TANGLISH_UNREPAIRABLE",
            "root_cause_analysis": validation_report,
            "reproducibility": "DETERMINISTIC",
            "automated_remediation": {"action": "CIRCUIT_BREAKER_EVERGREEN", "repaired_payload": None},
            "operator_action_required": False,
            "actionable_instructions": ["Falling back to pre-vetted evergreen Tanglish deck."]
        }
        self._record_incident(fail_diag)
        return False, None, fail_diag

    def diagnose_render_failure(self, deck: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Diagnoses Playwright or Jinja2 template rendering errors for Tamil slides."""
        prompt = f"""You are the Schematic Thinker Layer for 'Market Debunk Tamil'.
Phase: VISUAL_RENDERING_TAMIL
Error: {str(error)}
Traceback: {traceback.format_exc()}
Slide Count: {len(deck.get('slides', []))}

Analyze if the failure is due to Playwright browser installation, HTML template formatting, or Tamil fonts.
Output JSON schema:
{{
  "timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "phase": "RENDERING",
  "severity": "CRITICAL",
  "error_code": "ERR_PLAYWRIGHT_RENDER_TAMIL",
  "root_cause_analysis": "Exact root cause",
  "reproducibility": "DETERMINISTIC or ENVIRONMENT",
  "automated_remediation": {{
    "action": "RETRY_WITH_HEADLESS_FALLBACK or ABORT",
    "repaired_payload": null
  }},
  "operator_action_required": true,
  "actionable_instructions": ["Run: python -m playwright install --with-deps chromium"]
}}"""
        res = self._call_thinking_llm(prompt)
        if not res:
            res = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "RENDERING",
                "severity": "CRITICAL",
                "error_code": "ERR_PLAYWRIGHT_RENDER_TAMIL",
                "root_cause_analysis": f"Playwright rendering failed: {error}",
                "reproducibility": "ENVIRONMENT",
                "automated_remediation": {"action": "ABORT", "repaired_payload": None},
                "operator_action_required": True,
                "actionable_instructions": ["Ensure Playwright Chromium is installed."]
            }
        self._record_incident(res)
        return res

    def diagnose_publish_failure(
        self,
        platform: str,
        error_details: Any,
        payload_meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Diagnoses Tamil publishing errors across Instagram, Facebook, and Telegram."""
        prompt = f"""You are the Schematic Thinker Layer for 'Market Debunk Tamil' Publishing.
Platform: {platform}
Error Details: {json.dumps(error_details, default=str)}
Payload Metadata: {json.dumps(payload_meta, default=str)}

Analyze the exact error:
- Meta 100 / Subcode 2207001 (URL download failure)
- Meta 190 (Expired token)
- Meta 10 (Permissions)
- Telegram 429 (Rate limit)

Output JSON strictly matching this schema:
{{
  "timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "phase": "PUBLISHING",
  "platform": "{platform}",
  "severity": "CRITICAL or RECOVERABLE",
  "error_code": "ERR_META_API or ERR_IMAGE_NOT_ACCESSIBLE or ERR_TOKEN_EXPIRED",
  "root_cause_analysis": "Exact technical root cause",
  "reproducibility": "BAD_CREDENTIALS or URL_UNAVAILABLE or RATE_LIMIT",
  "automated_remediation": {{
    "action": "ISOLATE_AND_CONTINUE_SECONDARY or RETRY_AFTER_DELAY or ABORT",
    "retry_delay_seconds": 0
  }},
  "operator_action_required": true,
  "actionable_instructions": [
    "Specific step to fix token or URL accessibility"
  ]
}}"""
        res = self._call_thinking_llm(prompt)
        if not res:
            res = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "PUBLISHING",
                "platform": platform,
                "severity": "CRITICAL",
                "error_code": f"ERR_{platform.upper()}_PUBLISH",
                "root_cause_analysis": f"Platform publish error: {error_details}",
                "reproducibility": "UNKNOWN",
                "automated_remediation": {"action": "ISOLATE_AND_CONTINUE_SECONDARY", "retry_delay_seconds": 0},
                "operator_action_required": True,
                "actionable_instructions": [f"Check {platform} API credentials and network permissions."]
            }
        self._record_incident(res)
        return res

    def diagnose_pipeline_crash(self, phase: str, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Top-level pipeline crash handler for Tamil pipeline."""
        prompt = f"""You are the Schematic Thinker Layer for 'Market Debunk Tamil'.
A CRITICAL UNHANDLED EXCEPTION stopped the Tamil pipeline.
Phase: {phase}
Error: {str(error)}
Traceback: {traceback.format_exc()}
Context: {json.dumps(context, default=str)}

Generate a complete schematic incident report in JSON:
{{
  "timestamp": "{datetime.now(timezone.utc).isoformat()}",
  "phase": "{phase}",
  "severity": "CRITICAL",
  "error_code": "ERR_PIPELINE_HALT",
  "root_cause_analysis": "Detailed diagnosis of the halting defect",
  "reproducibility": "DETERMINISTIC or TRANSIENT",
  "automated_remediation": {{
    "action": "SAFE_SHUTDOWN",
    "repaired_payload": null
  }},
  "operator_action_required": true,
  "actionable_instructions": [
    "Concrete troubleshooting step 1",
    "Concrete troubleshooting step 2"
  ]
}}"""
        res = self._call_thinking_llm(prompt)
        if not res:
            res = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": phase,
                "severity": "CRITICAL",
                "error_code": "ERR_PIPELINE_HALT",
                "root_cause_analysis": f"Unhandled exception in {phase}: {error}",
                "reproducibility": "UNKNOWN",
                "automated_remediation": {"action": "SAFE_SHUTDOWN", "repaired_payload": None},
                "operator_action_required": True,
                "actionable_instructions": [f"Inspect log traceback for phase {phase}."]
            }
        self._record_incident(res)
        return res
