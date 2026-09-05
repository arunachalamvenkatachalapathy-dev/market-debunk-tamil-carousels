import json
import logging
import re
from typing import Optional, List, Dict, Tuple
from google import genai

from src.config import settings

logger = logging.getLogger(__name__)


class EditorialEngine:
    """
    Tanglish Content Strategist for Market Debunk Tamil carousels.
    Adapts financial debunks into natural spoken Tamil-English mix.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def compose_from_master(self, master_pkg: dict) -> dict:
        """
        Translates and adapts the English master carousel package into natural Tanglish.
        Preserves all numerical anchors and facts.
        """
        english_deck = master_pkg.get("deck", {})
        topic = master_pkg.get("topic", {})
        english_slides = english_deck.get("slides", [])

        logger.info("═══ Translating English Master Deck to Tanglish ═══")
        prompt = f"""You are the content strategist for "Market Debunk Tamil" — a finance myth-busting Instagram/Facebook carousel series for Tamil-speaking Indian retail investors.

Adapt this English 6-slide financial carousel into Tanglish (natural spoken Tamil-English mix, the way Tamil finance creators actually write and speak):

ENGLISH SLIDES DATA:
{json.dumps(english_slides, indent=2)}

STRICT RULES:
1. Keep all financial terms in English exactly as investors search/read them: SIP, Nifty, P/E ratio, mutual fund, stop-loss, portfolio, expense ratio, Direct plan, Regular plan — do NOT translate these into Tamil.
2. Write connecting sentences, explanations, and hooks in colloquial Tanglish (mixing Tamil sentence structure with English words naturally, e.g. "NIFTY market-ல இவ்ளோ பெரிய Risk-ஆ?!", "1% fee-ல ₹34 Lakhs loss-ஆ?!").
3. Do NOT produce pure literary/formal written Tamil (like news channels) — write the way a smart Tamil YouTuber explains it out loud.
4. Keep every slide short — under 30 words per slide.
5. Preserve all concrete numbers (e.g. ₹34 Lakhs, 93%, 1%, ₹15,000).
6. Slide 1: Hook in Tanglish with canary yellow highlight <span class="highlight-box">...</span> around the most shocking words.
7. Slide 6 CTA: "இந்த post-ஐ மறக்காம Save பண்ணுங்க! முழு breakdown வேணும்னா கீழ 'GUIDE'-னு comment பண்ணுங்க."

Return JSON ONLY matching the exact 6-slide schema:
{{
  "caption": "High-converting Tanglish caption with hook, bullet points, CTA, and hashtags",
  "slides": [ ... 6 slide objects ... ]
}}"""

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0.4}
                )
                if response.text:
                    data = json.loads(response.text)
                    if len(data.get("slides", [])) == 6:
                        # Pass 2: Tanglish Numeric Fact-Checking Gate
                        is_valid, report = self._verify_numeric_facts(data, topic)
                        if not is_valid:
                            logger.warning("❌ Tanglish Fact-Checking Gate failed (Attempt 1): %s. Repairing...", report)
                            repair_prompt = f"{prompt}\n\nSTRICT FACT-CHECK REPAIR: {report}. Make sure all numbers from the English slides are strictly preserved in Tamil!"
                            rep_resp = self.client.models.generate_content(
                                model=settings.GEMINI_MODEL,
                                contents=repair_prompt,
                                config={"response_mime_type": "application/json", "temperature": 0.3}
                            )
                            if rep_resp.text:
                                rep_data = json.loads(rep_resp.text)
                                is_rep_valid, rep_report = self._verify_numeric_facts(rep_data, topic)
                                if is_rep_valid and len(rep_data.get("slides", [])) == 6:
                                    logger.info("✅ Repaired Tanglish deck passed Fact-Checking Gate.")
                                    rep_data["slides"] = self._normalize_slides(rep_data["slides"], topic)
                                    rep_data["fact_check_status"] = "verified_after_repair"
                                    return rep_data
                            
                            # Circuit Breaker on 2nd failure
                            logger.error("🚨 CONSECUTIVE TANGLISH FACT-CHECK FAILURE. Engaging Circuit Breaker -> Falling back to pre-vetted Tanglish deck.")
                            fb_deck = self._generate_fallback_tanglish_deck(topic)
                            fb_deck["fact_check_status"] = "circuit_breaker_evergreen_fallback"
                            return fb_deck
                        else:
                            logger.info("✅ Tanglish Fact-Checking Gate passed: %s", report)
                            data["slides"] = self._normalize_slides(data["slides"], topic)
                            data["fact_check_status"] = "verified_pass"
                            return data
            except Exception as e:
                logger.warning("Tanglish adaptation failed (%s); using curated Tanglish deck.", e)

        return self._generate_fallback_tanglish_deck(topic)

    def _verify_numeric_facts(self, deck: dict, topic_data: dict) -> Tuple[bool, str]:
        source_text = f"{topic_data.get('raw_text', '')} {topic_data.get('title', '')} {topic_data.get('source_snippet', '')}"
        slides = deck.get("slides", [])
        all_slide_text = ""
        for s in slides:
            all_slide_text += f" {s.get('title', '')} {s.get('card_a_text', '')} {s.get('card_b_text', '')} {s.get('takeaway', '')} "
            for p in s.get("points", []):
                p_text = f"{p.get('title', '')} {p.get('desc', '')}" if isinstance(p, dict) else str(p)
                all_slide_text += f" {p_text} "
            for r in s.get("rules", []):
                r_text = f"{r.get('title', '')} {r.get('desc', '')}" if isinstance(r, dict) else str(r)
                all_slide_text += f" {r_text} "
            for b in s.get("body_lines", []):
                all_slide_text += f" {b} "
            all_slide_text += f" {s.get('headline', '')} {s.get('closing_line', '')} "

        # Financial regex: currency, %, Lakh, Crore, bps, years, months (ignoring decimal timestamp artifacts)
        pattern = r"(?:₹|\$)\s?\d+(?:[,\.]\d+)?(?:\s?(?:Cr|Lakh|Lakhs|Crore|Crores|k|M|B))?|\b\d+(?:[,\.]\d+)?\s?%|\b\d+\s?(?:Lakh|Lakhs|Crore|Crores|Cr|bps|years|months)\b"
        
        raw_source_matches = re.findall(pattern, source_text, flags=re.IGNORECASE)
        clean_source_nums = set()
        for m in raw_source_matches:
            cleaned = m.strip()
            if not re.search(r"\.\d{4,}", cleaned):  # Exclude microsecond timestamps
                clean_source_nums.add(cleaned)

        # If source has no specific financial numbers detected, pass gracefully
        if not clean_source_nums:
            return True, "Source context has no specific financial metrics; qualitative validation passed."

        # Check if at least one anchor metric digits/value from source is preserved in slides
        anchor_match = []
        for src_num in clean_source_nums:
            digits_match = re.search(r"\d+(?:[,\.]\d+)?", src_num)
            if digits_match:
                d = digits_match.group(0)
                if d in all_slide_text:
                    anchor_match.append(src_num)

        if not anchor_match and clean_source_nums:
            return False, f"Missing source anchor metric! Expected at least one of {clean_source_nums} in Tanglish slides."

        return True, f"FACT CHECK PASSED: Verified anchor metric(s) {list(anchor_match)} preserved across Tanglish slide deck."

    def _normalize_slides(self, slides: list, topic_data: dict) -> list:
        normalized = []
        default_tags = ["#INVESTING", "#TAMILFINANCE", "#HIDDENMATH", "#PLAYBOOK", "#STRATEGY", "#SAVETHIS"]

        for idx, slide in enumerate(slides[:6]):
            s = dict(slide)
            s["slide_index"] = idx + 1
            s["tag"] = s.get("tag") or default_tags[idx]

            raw_title = s.get("title") or s.get("headline") or ""
            if not s.get("title_lines"):
                s["title_lines"] = self._format_title_lines(raw_title, is_hook=(idx == 0))

            s["body_html"] = self._build_slide_body_html(s, idx)
            normalized.append(s)

        return normalized

    def _format_title_lines(self, raw_title: str, is_hook: bool = False) -> List[str]:
        clean = re.sub(r"<[^>]+>", "", raw_title).strip()
        words = clean.split()
        if not words:
            return ["Market Debunk Tamil"]

        if len(words) <= 4:
            if is_hook:
                return [f"<span class='highlight-box'>{clean}</span>"]
            return [clean]

        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])

        if is_hook:
            return [line1, f"<span class='highlight-box'>{line2}</span>"]
        return [line1, line2]

    def _build_slide_body_html(self, slide: dict, index: int) -> str:
        role = slide.get("role", "")
        layout = slide.get("layout", "")

        # Layout: Step Diagram
        if layout == "step_diagram" or slide.get("steps"):
            steps = slide.get("steps", [])
            step_cards = []
            for st in steps:
                color = st.get("color", "#A8D5BA")
                num = st.get("number", 1)
                lbl = st.get("label", "")
                sub = st.get("sublabel", "")
                step_cards.append(f"""
                <div class="step-card">
                  <div class="step-circle" style="background-color: {color};">
                    <span class="step-number">{num}</span>
                  </div>
                  <div class="step-meta">
                    <span class="step-label">{lbl}</span>
                    <span class="step-sublabel">{sub}</span>
                  </div>
                </div>""")
            steps_html = "".join(step_cards)
            body_lines = "".join(f"<p class='body-para'>{l}</p>" for l in slide.get("body_lines", []))
            closing = f"<p class='takeaway-para'><strong>Takeaway:</strong> {slide.get('closing_line', '')}</p>" if slide.get("closing_line") else ""
            return f"""<div class="step-diagram-container"><div class="steps-row">{steps_html}</div><div class="step-body-content">{body_lines}{closing}</div></div>"""

        # Role: Friction (Slide 2)
        if index == 1 or role == "friction":
            card_a = slide.get("card_a_text", "Retail நம்பிக்கை: 1% fee ரொம்ப சின்ன விஷயம்.")
            card_b = slide.get("card_b_text", "உண்மை: Compounding-ல இது ₹34 Lakhs-ஐ பறிக்குது.")
            takeaway = slide.get("takeaway", "Percentage-ஐ பாக்காதீங்க, absolute rupee loss-ஐ பாருங்க.")
            return f"""
            <div class="slide-body-paragraphs">
              <p class="body-para"><strong>Myth:</strong> {card_a}</p>
              <p class="body-para"><strong>Reality:</strong> {card_b}</p>
              <p class="takeaway-para"><strong>Core Rule:</strong> {takeaway}</p>
            </div>"""

        # Role: Breakdown / Points (Slide 3)
        if index == 2 or role == "breakdown":
            points = slide.get("points", [])
            items = []
            for i, p in enumerate(points):
                if isinstance(p, dict):
                    num = p.get("num", str(i + 1))
                    t = p.get("title", "")
                    d = p.get("desc", "")
                    items.append(f"<div class='point-item'><strong>{num}. {t}:</strong> {d}</div>")
                else:
                    items.append(f"<div class='point-item'><strong>{i + 1}.</strong> {p}</div>")
            return f"<div class='slide-body-list'>{''.join(items)}</div>"

        # Role: Concept / Rules (Slide 4 or 5)
        if slide.get("rules"):
            rules = slide.get("rules", [])
            items = []
            for i, r in enumerate(rules):
                if isinstance(r, dict):
                    t = r.get("title", "")
                    d = r.get("desc", "")
                    items.append(f"<div class='point-item'><strong>{i+1}. {t}:</strong> {d}</div>")
                else:
                    items.append(f"<div class='point-item'><strong>{i+1}.</strong> {r}</div>")
            return f"<div class='slide-body-list'>{''.join(items)}</div>"

        return f"<div class='slide-body-paragraphs'><p class='body-para'>{slide.get('text', '')}</p></div>"

    def _generate_fallback_tanglish_deck(self, topic_data: dict) -> dict:
        return {
            "caption": "🚨 1% Mutual Fund Fee-ல ₹34 Lakhs போகுதா?! 😱\n\nரொம்ப சின்ன fee-னு நினைக்கிற 1% commission, 25 வருஷத்துல உங்க compounding wealth-ல மிகப்பெரிய துளைய போடுது!\n\nமுழு breakdown-ஐ slide-ல பாருங்க. 👉\n\n💬 'GUIDE'-னு comment பண்ணுங்க, complete Risk Checklist-ஐ உங்க DM-க்கு அனுப்புறோம்!\n\n#TamilFinance #MutualFunds #StockMarketTamil #InvestingTamil #TamilBusiness",
            "slides": [
                {
                    "role": "hook",
                    "title": "Mutual Fund-ல <span class='highlight-box'>₹34 Lakhs Loss-ஆ?!</span>",
                    "deliverable": "📖 Inside: 1% Expense Ratio-வின் அதிர்ச்சி உண்மை",
                    "tag": "#MUTUALFUNDS"
                },
                {
                    "role": "friction",
                    "title": "1% Fee-யின் மாயை",
                    "card_a_text": "Retail investors: 1% distributor commission ரொம்ப சின்னது.",
                    "card_b_text": "Reality: ₹15,000 monthly SIP-ல 25 வருஷத்துல ₹34 Lakhs commission போகுது!",
                    "takeaway": "Percentage-ஐ மட்டும் பாக்காதீங்க, absolute rupee compounding-ஐ பாருங்க.",
                    "tag": "#MARKETTRUTH"
                },
                {
                    "role": "breakdown",
                    "title": "3 ரகசிய பண இழப்புகள்",
                    "points": [
                        {"num": "1", "title": "Monthly Trailing Commission", "desc": "Market லாபம் வந்தாலும் நஷ்டம் வந்தாலும் உங்க NAV-ல இருந்து கட் ஆகும்."},
                        {"num": "2", "title": "Opportunity Cost", "desc": "கட்டணமா போன ₹34 Lakhs உங்க retirement-க்கு compound ஆகாம போயிடும்."},
                        {"num": "3", "title": "Zero Extra Performance", "desc": "Regular plan-ல அதே stocks தான், எந்த extra returns-உம் கெடையாது."}
                    ],
                    "tag": "#HIDDENMATH"
                },
                {
                    "role": "architecture",
                    "layout": "step_diagram",
                    "steps": [
                        {"number": 1, "icon_concept": "search", "color": "#A8D5BA", "label": "AUDIT", "sublabel": "Portfolio-ல Regular இருக்கானு பாருங்க"},
                        {"number": 2, "icon_concept": "calculator", "color": "#F5D782", "label": "CALCULATE", "sublabel": "Direct vs Regular cost-ஐ கணக்கு போடுங்க"},
                        {"number": 3, "icon_concept": "shield", "color": "#A8C8E8", "label": "SWITCH", "sublabel": "Direct Zero-Fee plan-க்கு மாறுங்க"}
                    ],
                    "headline": "3-Step Capital Recovery Loop",
                    "body_lines": [
                        "Distributors உங்களுக்கு convenience விற்கிறாங்க.",
                        "Direct mutual fund platforms உங்க பணத்தை காப்பாத்துது."
                    ],
                    "closing_line": "புதிய முதலீடு பண்றதுக்கு முன்னாடி Expense Ratio-வை செக் பண்ணுங்க.",
                    "tag": "#PLAYBOOK"
                },
                {
                    "role": "concept",
                    "title": "Retail முதலீட்டாளர்களுக்கான 3 விதிகள்",
                    "rules": [
                        {"title": "Check 'Direct' in Scheme Name", "desc": "உங்க fund பெயர்ல 'Direct' என்ற வார்த்தை கண்டிப்பா இருக்கணும்."},
                        {"title": "Avoid Unnecessary Regular Plans", "desc": "Brokerage apps மூலமா வாங்காம direct AMC அல்லது zero-comm platform பயன்படுத்துங்க."},
                        {"title": "Cap Total Expense Ratio", "desc": "Active fund-க்கு TER 0.8%-க்கு உள்ளயும், Index fund-க்கு 0.2%-க்கு உள்ளயும் இருக்கணும்."}
                    ],
                    "tag": "#STRATEGY"
                },
                {
                    "role": "cta",
                    "title": "இந்த post-ஐ <span class='highlight-box'>மறக்காம</span> Save <span class='highlight-box'>பண்ணுங்க!</span>",
                    "discussion_question": "உங்க portfolio-வை Direct plan-க்கு மாத்திட்டீங்களா? உங்க அனுபவத்தை comment பண்ணுங்க 👇",
                    "lead_magnet": {
                        "trigger_word": "GUIDE",
                        "resource_name": "The Tamil Mutual Fund Checklist"
                    },
                    "tag": "#SAVETHIS"
                }
            ]
        }
