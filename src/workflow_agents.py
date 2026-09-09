"""
Workflow coordination agents for Market Debunk Tamil carousels.
Transforms real-time financial market news and deep comprehension into structured briefs.
"""
import json
import logging
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import settings, STATE_DIR

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Builds a structured financial debunk plan for an 8-slide carousel."""

    def __init__(self, llm_client=None):
        self.llm = llm_client

    def plan(self, topic_data: dict) -> dict:
        news_analysis = topic_data.get("news_analysis")
        if news_analysis and news_analysis.get("headline_hook") and news_analysis.get("citable_metrics"):
            metrics = news_analysis.get("citable_metrics", [])
            primary_metric = metrics[0] if metrics else "5%"
            return {
                "hook_headline": news_analysis.get("headline_hook"),
                "core_illusion": news_analysis.get("retail_illusion"),
                "hidden_reality": news_analysis.get("institutional_reality"),
                "citable_metric": primary_metric,
                "all_metrics": metrics,
                "actionable_rule": news_analysis.get("actionable_retail_rule"),
                "breaking_event": news_analysis.get("breaking_event_summary"),
                "lead_magnet": news_analysis.get("lead_magnet", {
                    "trigger_word": "GUIDE",
                    "resource_name": "The Retail Risk Checklist"
                }),
                "banned_phrases": ["guaranteed wealth", "quick money", "easy passive income", "get rich quick"]
            }

        title = topic_data.get("title", "")
        source = topic_data.get("source", "")
        raw_text = topic_data.get("raw_text", "")

        if self.llm:
            prompt = f"""Act as a senior quantitative financial editor for 'Market Debunk Tamil' creating an 8-slide educational Instagram carousel.
A financial market event occurred in India in the last 48 hours.

Breaking News: {title}
Source: {source}
Context: {raw_text[:2500]}

Rules:
1. Do not report breaking news like a news channel. Debunk the underlying mechanism or hidden math for retail investors.
2. Provide at least one concrete citable number (e.g., fee %, ₹ amount lost, percentage of traders losing).
3. The carousel must deliver actionable risk management advice.

Return JSON ONLY:
{{
  "hook_headline": "Punchy contrarian 1-line hook headline (max 10 words)",
  "core_illusion": "What retail investors falsely believe",
  "hidden_reality": "The institutional math / hidden deductions",
  "citable_metric": "Exact key number or percentage present in the context",
  "actionable_rule": "The golden rule for retail investors",
  "lead_magnet": {{
    "trigger_word": "GUIDE or RULE or CHECK",
    "resource_name": "A specific, ownable deliverable name (e.g. 'The Retail Trap Checklist')"
  }},
  "banned_phrases": ["game changer", "skyrocket", "guaranteed returns", "passive income secret"]
}}"""
            try:
                response = self.llm.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                if response.text:
                    plan = json.loads(response.text)
                    if plan.get("hook_headline") and plan.get("citable_metric"):
                        return plan
            except Exception as e:
                logger.warning("LLM planning failed (%s); using deterministic financial plan.", e)

        detected = topic_data.get("numbers_detected", ["₹34 Lakhs"])
        metric = detected[0] if detected else "₹34 Lakhs"
        return {
            "hook_headline": f"The Real Risk Behind {title[:40]}",
            "core_illusion": "Retail investors assume headline market moves represent easy momentum.",
            "hidden_reality": "Institutional order flows leverage volatility to offload risk to retail.",
            "citable_metric": metric,
            "actionable_rule": "Audit volume distribution, delivery percentages, and underlying leverage before entering.",
            "lead_magnet": {
                "trigger_word": "GUIDE",
                "resource_name": "The Retail Risk Checklist"
            },
            "banned_phrases": ["guaranteed wealth", "quick money", "easy passive income"]
        }


class PromptEngineer:
    """Converts the plan into an editorial brief for the two-pass slide composer."""

    def build_brief(self, plan: dict) -> str:
        lead_magnet = plan.get("lead_magnet", {})
        trigger = lead_magnet.get("trigger_word", "GUIDE")
        resource = lead_magnet.get("resource_name", "The Retail Risk Checklist")

        return (
            f"HOOK HEADLINE: {plan.get('hook_headline', '')}\n"
            f"BREAKING EVENT SUMMARY: {plan.get('breaking_event', '')}\n"
            f"CORE ILLUSION (THE TRAP): {plan.get('core_illusion', '')}\n"
            f"HIDDEN REALITY (INSTITUTIONAL TRUTH): {plan.get('hidden_reality', '')}\n"
            f"MANDATORY CITABLE METRIC: {plan.get('citable_metric', '')}\n"
            f"ACTIONABLE RULE: {plan.get('actionable_rule', '')}\n"
            f"LEAD MAGNET TRIGGER: Comment '{trigger}' for '{resource}'\n"
            f"AVOID: {', '.join(plan.get('banned_phrases', []))}"
        )


class GrammarAgent:
    """
    Grammar & Stylistic Verification Agent for Market Debunk Tamil:
    1. Cross-checks spelling, grammar, punctuation, and sentence flow across all slides.
    2. Strips any leaked markdown artifacts (e.g. raw '**', '#', leading numbers inside text).
    3. Intelligently selects punchy words/phrases to wrap with '<span class="highlight-box">...</span>'.
    4. Ensures vertical density and clarity without forcing or rushing content.
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client

    def sanitize_text(self, text: str) -> str:
        """Removes markdown syntax, website URLs/domains, leaked publish dates, and messy quotes."""
        if not text:
            return ""
        t = str(text)
        t = re.sub(r"\s*[-|–—]\s*(?:indianexpress\.com|moneycontrol|economic times|ndtv profit|reuters|bloomberg|livemint|[a-zA-Z0-9.-]+\.(?:com|in|org|net)).*$", "", t, flags=re.I)
        t = re.sub(r"https?://\S+", "", t)
        t = re.sub(r"\b[a-zA-Z0-9.-]+\.(?:com|in|org|net)\b", "", t, flags=re.I)
        t = re.sub(r"Published:\s*\d{4}-\d{2}-\d{2}\s*[-—:]*\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"^[‘'\"“]+|[’'\"”]+$", "", t)
        t = re.sub(r"^[‘'\"“][^:’'\"]+[:’'\"]\s*", "", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
        t = re.sub(r"\*([^*]+)\*", r"\1", t)
        t = re.sub(r"`([^`]+)`", r"\1", t)
        t = re.sub(r":([^\s])", r": \1", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def clean_text(self, text: str) -> str:
        return self.sanitize_text(text)

    def review_and_polish_deck(self, deck: dict, topic_data: Optional[dict] = None) -> dict:
        """
        AI-Powered Grammar & Sentence Formation Gate for Tanglish:
        1. Formulates a concise 4-6 word hook (NOT huge, zero websites).
        2. Ensures Slides 2-7 have contextual 3-5 word titles (NO '#1' on a separate line).
        3. Fills Slide 8 with complete takeaway text.
        """
        topic_data = topic_data or {}
        topic_title = self.sanitize_text(topic_data.get("title", ""))
        slides = deck.get("slides", [])

        if self.llm and slides:
            try:
                prompt = f"""You are the Lead Editorial Grammar & Sentence Formation Agent for 'Market Debunk Tamil'.
Refine the Tanglish headlines and titles for this 8-slide Instagram carousel to ensure premium editorial flow.

TOPIC: {topic_title}
SLIDES OVERVIEW:
{json.dumps([{"role": s.get("role"), "title": s.get("title"), "card_text": s.get("card_text", "")[:120]} for s in slides], indent=2)}

STRICT RULES:
1. Slide 1 (hook): Must be punchy and concise (4 to 6 words MAXIMUM). NEVER huge, NEVER include website names, URLs, or news domains. Include exactly ONE <span class="highlight-box">...</span> around 1-2 powerful words.
2. Slides 2 to 7 (value): Titles must be 3 to 5 words MAXIMUM in Tanglish. Contextual to the card content. NEVER use numbers like '#1', '#2'.
3. Slide 8 (save CTA): Provide 'cta_detail' (20-30 words) in Tanglish explaining WHY investors must save this framework for their next trade review.

Return JSON ONLY:
{{
  "slide_1_hook": "Mutual Fund-ல் <span class='highlight-box'>₹34 Lakhs Loss-ஆ?!</span>",
  "slide_titles": [
    "1% Fee-யின் <span class='highlight-box'>மாயை & உண்மை</span>",
    "Trailing Commission <span class='highlight-box'>ரகசிய கசிவு</span>",
    "Compounding <span class='highlight-box'>இழப்பின் தாக்கம்</span>",
    "Regular Plans <span class='highlight-box'>கூடுதல் லாபம் தராது</span>",
    "முதலீட்டை <span class='highlight-box'>பாதுகாக்கும் விதி</span>",
    "Pre-Trade <span class='highlight-box'>Capital தணிக்கை</span>"
  ],
  "slide_8_cta_detail": "இந்த institutional risk checkpoints-ஐ உங்கள் அடுத்த trade-க்கு முன் review செய்ய save செய்து கொள்ளுங்கள்."
}}"""
                resp = self.llm.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0.2}
                )
                if resp.text:
                    refined = json.loads(resp.text)
                    if refined.get("slide_1_hook"):
                        slides[0]["title"] = refined["slide_1_hook"]
                    titles = refined.get("slide_titles", [])
                    for i, t in enumerate(titles):
                        if i + 1 < len(slides) - 1:
                            slides[i + 1]["title"] = t
                    if refined.get("slide_8_cta_detail") and len(slides) >= 8:
                        slides[-1]["cta_detail"] = refined["slide_8_cta_detail"]
            except Exception as e:
                logger.warning("Tamil LLM sentence formation fallback to deterministic: %s", e)

        for i, s in enumerate(slides):
            raw_title = s.get("title", "")
            cleaned = self.sanitize_text(raw_title)
            cleaned = re.sub(r"\s*#\d+\b", "", cleaned).strip()
            if cleaned:
                s["title"] = cleaned

            if "card_text" in s:
                ct = str(s["card_text"])
                ct = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", ct)
                ct = re.sub(r"`([^`]+)`", r"\1", ct)
                s["card_text"] = ct.strip()

            if i == len(slides) - 1 and not s.get("cta_detail"):
                s["cta_detail"] = "இந்த institutional risk checkpoints-ஐ உங்கள் அடுத்த trade-க்கு முன் review செய்ய save செய்து கொள்ளுங்கள்."
        return deck

    def format_converting_caption(self, deck: dict, topic_data: dict, audio_track: Optional[dict] = None) -> str:
        """
        Formats a high-converting, organically diverse Tanglish caption based on the 2026 Algorithmic Directive:
        1. Curiosity Hook (rotates across 5 distinct opening archetypes in Tanglish)
        2. Progressive Value Preview (3 slide teasers)
        3. Double Algorithmic Engagement Signal: Bookmark Save + DM Share CTA
        4. Lead Magnet keyword comment trigger
        5. Rotating non-repetitive hashtag cluster (anti-spam diversity)
        """
        title = topic_data.get("title", "")
        slides = deck.get("slides", [])
        hook_text = slides[0].get("title", title) if slides else title
        clean_hook = re.sub(r"<[^>]+>", "", hook_text).strip()
        clean_hook = re.sub(r"\s*[-|]\s*(Bloomberg(\.com)?|Reuters|Mint|Moneycontrol|The Economic Times|NDTV Profit|CNBC-TV18|Business Standard|Financial Express).*", "", clean_hook, flags=re.IGNORECASE).strip()

        trigger = "GUIDE"
        bullets = []
        for s in slides[1:4]:
            t = s.get("title") or ""
            t_clean = re.sub(r"<[^>]+>", "", t).strip()
            if t_clean:
                bullets.append(f"📌 {t_clean}")
        if not bullets:
            bullets = [
                "📌 செய்திகளுக்கு பின்னால் உள்ள Institutional எதார்த்தம்",
                "📌 Institutional vs Retail அணுகுமுறை",
                "📌 உங்கள் முதலீட்டை பாதுகாக்கும் முக்கிய விதி"
            ]

        # ── 1. Rotate Dynamic Curiosity-Driven Opening Hooks (Tanglish) ───────
        opening_angles = [
            "சந்தையில் வரும் செய்திகளை மட்டும் நம்பி முதலீடு செய்வது எப்படி institutional trap-ல் சிக்க வைக்கும் என்பதை பாருங்கள்.",
            "இந்த நகர்வின் பின்னணியில் உள்ள உண்மை நிதி கணக்கீடுகள், டிவி செய்திகள் சொல்வதை விட முற்றிலும் மாறுபட்டவை.",
            "அடுத்த trade எடுக்கும் முன், Smart Money மற்றும் நிறுவனங்கள் உண்மையில் என்ன செய்கிறார்கள் என்பதை கவனியுங்கள்.",
            "சாதாரண முதலீட்டாளர்கள் இந்த breakout-ஐ துரத்தும் போது, பெரிய நிறுவனங்கள் தங்கள் ரிஸ்க்கை அமைதியாக hedge செய்கின்றன.",
            "FOMO அவசரம் உங்கள் முதலீட்டு வளர்ச்சியை எப்படி பாதிக்கிறது? இந்த முக்கிய data-வை உடனே audit செய்யுங்கள்."
        ]

        # ── 2. Rotate Across 5 Diverse Tamil Thematic Hashtag Clusters ────────
        hashtag_clusters = [
            ["#TamilFinance", "#StockMarketTamil", "#TamilTrading", "#TamilInvestors", "#MarketDebunk"],
            ["#TamilShareMarket", "#NiftyTamil", "#InvestmentTamil", "#TradingTamil", "#ShareMarketTamil"],
            ["#TamilWealth", "#PersonalFinanceTamil", "#TamilBusiness", "#MoneyTamil", "#TamilSavings"],
            ["#MarketDebunkTamil", "#StockTipsTamil", "#TradingStrategyTamil", "#RiskTamil", "#TamilKnowledge"],
            ["#TamilStockMarket", "#IndianEconomyTamil", "#WealthBuildingTamil", "#FinancialLiteracyTamil", "#Tamil"]
        ]

        # Inspect last upload history to guarantee zero back-to-back cluster or angle repetition
        last_cluster_id = None
        last_angle_id = None
        try:
            from src.config import STATE_DIR
            history_file = STATE_DIR / "upload_history.json"
            if history_file.exists():
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    uploads = data.get("uploads", []) if isinstance(data, dict) else data
                    if uploads:
                        last_cluster_id = uploads[-1].get("hashtag_cluster")
                        last_angle_id = uploads[-1].get("hook_archetype")
        except Exception:
            pass

        available_angle_indices = [i for i in range(len(opening_angles)) if f"tamil_angle_{i+1}" != last_angle_id]
        angle_idx = random.choice(available_angle_indices) if available_angle_indices else random.randint(0, len(opening_angles) - 1)
        chosen_opening = opening_angles[angle_idx]

        available_cluster_indices = [i for i in range(len(hashtag_clusters)) if f"tamil_cluster_{i+1}" != last_cluster_id]
        cluster_idx = random.choice(available_cluster_indices) if available_cluster_indices else random.randint(0, len(hashtag_clusters) - 1)
        chosen_hashtags = " ".join(hashtag_clusters[cluster_idx])

        deck["hashtag_cluster_id"] = f"tamil_cluster_{cluster_idx + 1}"
        deck["hook_archetype_id"] = f"tamil_angle_{angle_idx + 1}"

        caption = (
            f"🚨 {clean_hook}\n\n"
            f"{chosen_opening}\n\n"
            f"முழு 8-slide Tanglish breakdown-ஐ படிக்க swipe செய்யுங்கள். 👉\n"
            f"{chr(10).join(bullets)}\n\n"
            f"📌 உங்கள் அடுத்த trade-க்கு முன் பார்க்க இந்த பதிவை Save செய்து கொள்ளுங்கள்.\n"
            f"✈️ உங்கள் முதலீட்டாளர் நண்பர்களுக்கு Share செய்து அவர்களின் Capital-ஐ பாதுகாக்கவும்.\n\n"
            f"💬 Follow @marketdebunk_tamil மற்றும் '{trigger}'-னு கீழே comment பண்ணுங்க — complete detailed Investor Playbook & Risk Checklist PDF-ஐ உங்க DM-க்கு உடனே அனுப்புறோம்!\n\n"
            f"{chosen_hashtags}"
        )
        return caption
