"""
Market Debunk Tamil - Editorial Engine
Produces authoritative 8-slide Tanglish carousels strictly matching the reference layout:
Slide 1: Hook Headline (1 highlight box)
Slides 2-7: Value Slides (Headline with 1 highlight box + exactly ONE solid green card)
Slide 8: Bookmark Save CTA
"""

import json
import logging
import re
from typing import Optional, List, Dict, Tuple
from google import genai

from src.config import settings
from src.thinker_engine import ThinkerEngine

logger = logging.getLogger(__name__)


class EditorialEngine:
    """
    Independent Tanglish Scripting & Editorial Engine for Market Debunk Tamil carousels.
    Autonomously crafts native spoken Tamil-English breakdowns strictly formatted for
    the authoritative 8-slide Instagram carousel layout.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.thinker = ThinkerEngine(api_key=self.api_key)

    def compose_from_master(self, master_pkg: dict) -> dict:
        """
        Independently scripts and structures a complete 8-slide Tanglish carousel
        from the underlying market topic and financial plan.
        Preserves verified citable numerical metrics.
        """
        topic = master_pkg.get("topic", {})
        plan = master_pkg.get("plan", {})

        title = topic.get("title", "Market Debunk")
        source = topic.get("source", "")
        raw_text = topic.get("raw_text", "")
        numbers = topic.get("numbers_detected", [])
        core_thesis = plan.get("hidden_reality") or plan.get("core_thesis", "")
        retail_trap = plan.get("core_illusion") or plan.get("retail_trap", "")
        citable_metric = plan.get("citable_metric") or (numbers[0] if numbers else "")
        actionable_rule = plan.get("actionable_rule", "")
        lead_magnet = plan.get("lead_magnet", {})
        trigger = lead_magnet.get("trigger_word", "DEBUNK")
        resource = lead_magnet.get("resource_name", "The Tamil Risk Checklist")

        winning_hook = topic.get("headline_hook") or (topic.get("news_analysis", {}).get("headline_hook") if isinstance(topic.get("news_analysis"), dict) else None)
        editorial_directive = topic.get("editorial_directive") or (topic.get("news_analysis", {}).get("editorial_directive") if isinstance(topic.get("news_analysis"), dict) else "")

        logger.info("═══ Autonomous Tanglish Scripting Agent: Sourcing Concept '%s' ═══", title)
        prompt = f"""You are the Lead Financial Scripting Agent for "Market Debunk Tamil" — an educational Instagram carousel series for Tamil-speaking retail investors.

Do NOT translate word-for-word. Craft an ORIGINAL 8-slide sequential breakdown in conversational Tanglish (natural spoken Tamil mixed with English financial terms: SIP, Nifty, mutual fund, stop-loss, portfolio, expense ratio, P/E, IPO, Direct plan, etc.).

FINANCIAL CONCEPT & EVIDENCE:
- Topic: {title}
- Source: {source}
- Context: {raw_text}
- Winning Critic Angle/Hook: {winning_hook or 'N/A'}
- Editorial Directive: {editorial_directive or 'N/A'}
- The Retail Illusion / Trap: {retail_trap}
- The Institutional Reality / Thesis: {core_thesis}
- Available verified metric, if source-supported: {citable_metric}
- Golden Actionable Rule: {actionable_rule}

ADAPTIVE 8-SLIDE STORY:
Slide 1 starts with no warm-up: choose an actual named person + exact surprising
number ONLY when both are in this source and relevant; otherwise a documented
familiar assumption versus reality, or a concrete money-decision question.
These are alternative hooks, not one formula. Never imply Arun interviewed the
person or lived the story. Do not invent a name, number or counter-thesis. Use natural
spoken Tanglish as a Tamil friend would explain it to a first-time investor.
For example an EMI or chit-fund situation ONLY if the source actually covers it.
Slides 2-7 build a clear before/after, consequence, caveat, or practical choice
based on this story. Give the reader a specific check they can use or screenshot;
no fabricated calculations or characters. Last slide's cta_detail must summarize
that useful check before inviting a save/share, not a generic pre-trade audit.
Caption: name the money dilemma, offer the main takeaway, end with one specific question about THIS money decision (not a generic கருத்து என்ன?),
use 3-5 topic-specific Tamil/English hashtags, and do not promise a guide or DM
resource that this pipeline cannot deliver. No repeated broad hashtag padding.
Keep exactly 8 slides for the publishing layout, but choose the story flow from THIS source. Hook, then six distinct topic-specific insights in a natural order, then a meaningful save/share CTA. Do not force every story into a myth, penalty, institutional trap, stat, or checklist. A news development may need timeline -> why it happened -> who is affected -> what is uncertain -> practical takeaway. A fee comparison may need real comparable costs and caveats. Use an exact stat_data metric only when it exists in the source. Never invent a number, implied return, or trading rule. Give each slide a distinct fact or clear inference tied to the article.
Supported visual structures for slides 2-7: comparison_data {"myth":"...", "reality":"..."}, stat_data {"metric":"...", "label":"...", "context":"..."}, flowchart_data [{"text":"..."}], checklist_data [{"status":"pass", "text":"..."}], or card_text. Select what best fits each point and vary the layouts; no required sequence of archetypes. role is value_1 through value_6 by position. For every slide use a topic-specific title and concise Tanglish copy. Preserve Tamil glyphs and conversational tone. The final slide has role bookmark_save and a topic-specific CTA.

RULES FOR CONTENT:
- Concise, high-velocity reading: 2 to 3 sentences max for card texts or contexts.
- Bold essential numbers and key phrases using <strong>...</strong> (e.g. <strong>{citable_metric}</strong>).
- Conversational, engaging Tanglish (colloquial Tamil blended with financial terms).

Return valid JSON only with "caption" and "slides" (exactly 8 slide objects). Each slide has role, title, and one supported body structure; the hook needs title, and last slide needs title and cta_detail. Use real topic content, not the template examples.
"""

        models_to_try = [
            settings.GEMINI_MODEL,
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
        ]
        candidate_models = []
        for m in models_to_try:
            if m and m not in candidate_models:
                candidate_models.append(m)

        deck = None
        if self.client:
            for model_name in candidate_models:
                try:
                    logger.info("Attempting Tanglish drafting with model %s...", model_name)
                    config = {"temperature": 0.3, "response_mime_type": "application/json"}
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )
                    if response.text:
                        clean_text = response.text.strip()
                        if clean_text.startswith("```json"):
                            clean_text = clean_text[7:]
                        if clean_text.endswith("```"):
                            clean_text = clean_text[:-3]
                        parsed = json.loads(clean_text.strip())
                        if len(parsed.get("slides", [])) == settings.EXPECTED_SLIDE_COUNT:
                            deck = parsed
                            logger.info("✓ Model %s successfully generated Tanglish draft with %d slides.", model_name, len(deck.get("slides", [])))
                            break
                except Exception as e:
                    logger.warning("Model %s Tanglish draft failed: %s", model_name, e)
                    import time
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        logger.info("Encountered 429 quota throttle on %s; cooling down 2.5s...", model_name)
                        time.sleep(2.5)

        if not deck:
            logger.warning("Primary Tanglish drafting unverified; falling back to evergreen topic deck.")
            raise ValueError("Tamil draft unavailable; refusing generic fallback carousel")

        if len(deck.get("slides", [])) != settings.EXPECTED_SLIDE_COUNT:
            raise ValueError("Tamil draft needs exactly eight topic-specific slides")
        # Normalize to strictly 8 slides
        deck["slides"] = self._normalize_slides(deck.get("slides", []), topic)

        # Verify numeric facts
        is_valid, report = self._verify_numeric_facts(deck, topic)
        if is_valid:
            logger.info("✅ Tanglish Fact-Checking Gate passed: %s", report)
            deck["fact_check_status"] = "verified_pass"
        else:
            raise ValueError(f"Tamil numeric fact check failed: {report}")

        return deck

    def _verify_numeric_facts(self, deck: dict, topic_data: dict) -> Tuple[bool, str]:
        """Reject financial metrics in the deck that are absent from source evidence.

        Exclude layout counters and hashtags; compare whole metric tokens, including
        currency and units, to avoid treating 15% as evidence for 15 crore.
        """
        from src.numeric_evidence import extract_metrics, collect_slide_copy

        source = " ".join(str(topic_data.get(k) or "") for k in
                          ("raw_text", "title", "source_snippet", "evidence_snapshot"))
        source_metrics = extract_metrics(source)
        deck_metrics = extract_metrics(collect_slide_copy(deck.get("slides", [])) + " " + str(deck.get("caption", "")))
        unsupported = deck_metrics - source_metrics
        if unsupported:
            return False, f"Unsupported deck metrics: {sorted(unsupported)}; source metrics: {sorted(source_metrics)}"
        return True, f"Verified {len(deck_metrics)} deck metrics against source text."

    def _normalize_slides(self, slides: list, topic_data: dict) -> list:
        normalized = []
        expected_count = settings.EXPECTED_SLIDE_COUNT

        for idx in range(expected_count):
            if idx < len(slides):
                s = dict(slides[idx])
            else:
                s = {}

            s["slide_index"] = idx + 1
            s["tag"] = "#MARKETDEBUNK"

            if idx == 0:
                s["role"] = "hook"
                raw_title = s.get("title") or s.get("headline") or topic_data.get("title", "Market Debunk Tamil")
                # Strip all websites, domains, quotes, and legal boilerplate
                raw_title = re.sub(r"\s*[-|–—]\s*(?:indianexpress\.com|moneycontrol|economic times|ndtv profit|reuters|bloomberg|livemint|[a-zA-Z0-9.-]+\.(?:com|in|org|net)).*$", "", str(raw_title), flags=re.I)
                raw_title = re.sub(r"https?://\S+", "", raw_title)
                raw_title = re.sub(r"\b[a-zA-Z0-9.-]+\.(?:com|in|org|net)\b", "", raw_title, flags=re.I)
                raw_title = re.sub(r"^[‘'\"“]+|[’'\"”]+$", "", raw_title)
                raw_title = re.sub(r"^[‘'\"“][^:’'\"]+[:’'\"]\s*", "", raw_title)
                s["title_lines"] = self._format_title_lines(raw_title, is_hook=True, slide_index=1)
                s["card_text"] = ""
            elif idx == expected_count - 1:
                s["role"] = "bookmark_save"
                raw_title = s.get("title") or "இந்த money முடிவுக்கு முன் check பண்ணுங்க"
                s["title_lines"] = self._format_title_lines(str(raw_title), slide_index=idx + 1)
                s["card_text"] = ""
                if not s.get("cta_detail"):
                    raise ValueError("Tamil final slide needs a topic-specific, useful takeaway")
            else:
                s["role"] = s.get("role") or f"value_{idx}"
                raw_title = s.get("title") or s.get("headline")
                if not raw_title or "Institutional Reality" in str(raw_title):
                    raise ValueError(f"Tamil slide {idx + 1} needs a topic-specific headline")
                # Strip trailing numbers like #1, #2
                raw_title = re.sub(r"\s*#\d+\b", "", str(raw_title)).strip()
                s["title_lines"] = self._format_title_lines(raw_title, is_hook=False, slide_index=idx + 1)

                # Preserve polymorphic archetype structures
                if s.get("comparison_data") and isinstance(s["comparison_data"], dict):
                    comp = s["comparison_data"]
                    comp["myth"] = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", str(comp.get("myth", "")))
                    comp["reality"] = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", str(comp.get("reality", "")))
                elif s.get("stat_data") and isinstance(s["stat_data"], dict):
                    stat = s["stat_data"]
                    stat["context"] = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", str(stat.get("context", "")))
                    stat["metric"] = str(stat.get("metric", ""))
                    stat["label"] = str(stat.get("label", ""))
                elif s.get("flowchart_data") and isinstance(s["flowchart_data"], list):
                    for step in s["flowchart_data"]:
                        if isinstance(step, dict):
                            step["text"] = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", str(step.get("text", "")))
                elif s.get("checklist_data") and isinstance(s["checklist_data"], list):
                    for item in s["checklist_data"]:
                        if isinstance(item, dict):
                            item["text"] = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", str(item.get("text", "")))
                else:
                    card_text = s.get("card_text") or s.get("card_b_text") or s.get("takeaway") or ""
                    if not card_text:
                        raise ValueError(f"Tamil slide {idx + 1} has no topic-specific body")
                    card_text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", card_text)
                    s["card_text"] = card_text

            normalized.append(s)

        return normalized

    def _format_title_lines(self, raw_title: str, is_hook: bool = False, slide_index: int = 1) -> List[str]:
        if "highlight-box" in raw_title:
            if slide_index == 1 or is_hook:
                m = re.search(r"<span class=['\"]highlight-box['\"]>([^<]+)</span>", raw_title)
                if m:
                    hl_words = m.group(1).strip().split()
                    hl_text = " ".join(hl_words[:2]) if len(hl_words) > 2 else " ".join(hl_words)
                    before = re.sub(r"<[^>]+>", "", raw_title[:m.start()]).strip()
                    after = re.sub(r"<[^>]+>", "", raw_title[m.end():]).strip()
                    lines = []
                    if before:
                        b_words = before.split()
                        if len(b_words) > 2:
                            lines.append(" ".join(b_words[:2]))
                            lines.append(" ".join(b_words[2:4]))
                        else:
                            lines.append(" ".join(b_words))
                    lines.append(f"<span class='highlight-box'>{hl_text}</span>")
                    if after:
                        a_words = after.split()
                        lines.append(" ".join(a_words[:2]))
                    return [l for l in lines if l.strip()]

            lines = [l.strip() for l in re.split(r"<br\s*/?>|\n", raw_title) if l.strip()]
            filtered = [l for l in lines if not re.match(r"^#?\d+[\.\)]?$", l)]
            if len(filtered) > 1:
                return filtered

        clean = re.sub(r"<[^>]+>", "", raw_title).strip()
        clean = re.sub(r"\s*#\d+\b", "", clean).strip()
        words = clean.split()
        if not words:
            return ["Market Debunk"]

        if slide_index == 1 or is_hook:
            words = words[:6]
            if len(words) <= 3:
                return [" ".join(words[:1]), f"<span class='highlight-box'>{' '.join(words[1:])}</span>"]
            elif len(words) == 4:
                return [" ".join(words[:2]), f"<span class='highlight-box'>{' '.join(words[2:])}</span>"]
            elif len(words) == 5:
                return [" ".join(words[:2]), f"<span class='highlight-box'>{' '.join(words[2:4])}</span>", words[4]]
            else:
                return [" ".join(words[:2]), f"<span class='highlight-box'>{' '.join(words[2:4])}</span>", " ".join(words[4:])]

        words = [w for w in words if not re.match(r"^#?\d+$", w)]
        if len(words) <= 3:
            return [f"<span class='highlight-box'>{' '.join(words[:2])}</span>", " ".join(words[2:])] if len(words) > 2 else [f"<span class='highlight-box'>{' '.join(words)}</span>"]

        mid = min(2, len(words) // 2)
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:mid+2])
        rest = " ".join(words[mid+2:])

        res = [line1, f"<span class='highlight-box'>{line2}</span>"]
        if rest:
            res.append(rest)
        return [r for r in res if r.strip()]

    def _generate_fallback_tanglish_deck(self, topic_data: dict, plan: Optional[dict] = None) -> dict:
        """
        Dynamically scripts a native 8-slide Tanglish deck directly from the
        actual sourced market news headline, snippet, and financial plan.
        NEVER falls back to static hardcoded Mutual Fund templates!
        """
        plan = plan or {}
        title = topic_data.get("title", "Market Volatility & Institutional Reality")
        clean_title = re.sub(r"\s*[-|–—]\s*(?:indianexpress\.com|moneycontrol|economic times|ndtv profit|reuters|bloomberg|livemint|[a-zA-Z0-9.-]+\.(?:com|in|org|net)).*$", "", title, flags=re.I).strip()
        clean_title = re.sub(r"^[‘'\"“]+|[’'\"”]+$", "", clean_title).strip()
        words = clean_title.split()
        short_title = " ".join(words[:5]) if len(words) > 5 else clean_title

        detected_nums = topic_data.get("numbers_detected", [])
        citable_metric = plan.get("citable_metric") or (detected_nums[0] if detected_nums else "முக்கிய levels")
        source_name = topic_data.get("source", "Financial Press")

        analysis = topic_data.get("news_analysis", {})
        retail_trap = plan.get("core_illusion") or analysis.get("retail_illusion") or f"{short_title} செய்தி வந்தவுடன் retail investors அவசரப்பட்டு வாங்குகிறார்கள். ஆனால் underlying volume மற்றும் institutional data-வை பார்ப்பதில்லை."
        inst_reality = plan.get("hidden_reality") or analysis.get("institutional_reality") or f"Smart Money மற்றும் big institutions இந்த headline liquidity-ஐ பயன்படுத்தி risk hedge செய்கிறார்கள். Retail traders உச்சத்தில் மாட்டிக் கொள்கிறார்கள்."
        action_rule = plan.get("actionable_rule") or analysis.get("actionable_retail_rule") or f"Headline hype-ஐ பார்த்து trade செய்யாதீர்கள். Price confirmation வரும் வரை காத்திருந்து, strict stop-loss உடன் மட்டுமே முதலீடு செய்யுங்கள்."

        return {
            "caption": (
                f"🚨 {short_title} - Institutional Reality என்ன? 📊\n\n"
                f"சந்தை செய்திகளை பார்த்து அவசரப்பட்டு முடிவெடுக்காதீர்கள்! Institutions எப்படி இந்த நகர்வை அணுகுகிறார்கள் என்பதை புரிந்து கொள்ளுங்கள்.\n\n"
                f"முழு 8-slide Tanglish breakdown-ஐ பாருங்கள். 👉\n\n"
                f"📌 உங்க அடுத்த trade-க்கு முன் இந்த பதிவை Save செய்து வையுங்கள்.\n"
                f"📤 F&O மற்றும் stocks trade செய்யும் உங்க நண்பர்களுக்கு Share பண்ணுங்க.\n\n"
                f"💬 நீங்க இந்த மாதிரி headline hype-ல் மாட்டிக்கிட்டது உண்டா? கமெண்ட்ல சொல்லுங்க 👇\n\n"
                f"#TamilFinance #StockMarketTamil #NiftyTamil #InvestingTamil #PersonalFinance"
            ),
            "slides": [
                {
                    "role": "hook",
                    "title": f"{short_title} <span class='highlight-box'>உண்மை என்ன?</span>",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_1",
                    "title": "Retail முதலீட்டாளர்களின் <span class='highlight-box'>மாயை & உண்மை</span>",
                    "card_text": f"{retail_trap}",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_2",
                    "title": "சந்தையின் எண்கள் <span class='highlight-box'>கூறும் ரகசியம்</span>",
                    "card_text": f"{source_name} தகவலின்படி, முக்கிய கவனம் <strong>{citable_metric}</strong> மீது உள்ளது. சந்தை ஏற்ற இறக்கங்களின் போது institutions தங்கள் positions-ஐ அமைதியாக மாற்றுகிறார்கள்.",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_3",
                    "title": "Smart Money <span class='highlight-box'>Liquidity-ஐ எப்படி</span> பயன்படுத்துகிறது?",
                    "card_text": f"{inst_reality}",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_4",
                    "title": "FOMO வாங்குதலின் <span class='highlight-box'>Compounding இழப்பு</span>",
                    "card_text": "உறுதிப்படுத்தப்படாத செய்திகளை நம்பி முதலீடு செய்வது பெரிய capital drawdown-ஐ ஏற்படுத்தும். Capital-ஐ பாதுகாப்பதே நீண்டகால செல்வ உருவாக்கத்தின் முதல் விதி.",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_5",
                    "title": "முதலீட்டை <span class='highlight-box'>பாதுகாக்கும் முக்கிய</span> விதி",
                    "card_text": f"{action_rule}",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "value_6",
                    "title": "Pre-Trade <span class='highlight-box'>3-Point Capital</span> தணிக்கை",
                    "card_text": "1) செய்தியை விட actual volume-ஐ கவனியுங்கள். 2) Entry எடுக்கும் முன்பே non-negotiable stop-loss வையுங்கள். 3) ஒரே trade-ல் <strong>2%-க்கு மேல்</strong> capital risk செய்யாதீர்கள்.",
                    "tag": "#MARKETDEBUNK"
                },
                {
                    "role": "bookmark_save",
                    "title_lines": ["இந்த பதிவை உங்க", "<span class='highlight-box'>F&O நண்பருக்கு</span>", "இப்போவே Share", "பண்ணுங்க!"],
                    "cta_detail": "இந்த institutional checkpoints-ஐ உங்கள் அடுத்த trade-க்கு முன் review செய்ய Bookmark செய்யுங்கள்.",
                    "tag": "#MARKETDEBUNK"
                }
            ]
        }
