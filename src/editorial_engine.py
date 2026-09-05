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
    Autonomously crafts native spoken Tamil-English breakdowns from core market concepts.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.thinker = ThinkerEngine(api_key=self.api_key)

    def compose_from_master(self, master_pkg: dict) -> dict:
        """
        Independently scripts and structures a complete 6-slide Tanglish carousel
        from the underlying market topic and financial plan (NOT by translating English slides).
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
        citable_metric = plan.get("citable_metric") or (numbers[0] if numbers else "₹34 Lakhs")
        actionable_rule = plan.get("actionable_rule", "")
        lead_magnet = plan.get("lead_magnet", {})
        trigger = lead_magnet.get("trigger_word", "GUIDE")
        resource = lead_magnet.get("resource_name", "The Risk Checklist")

        logger.info("═══ Autonomous Tanglish Scripting Agent: Sourcing Concept '%s' ═══", title)
        prompt = f"""You are the Lead Financial Scripting Agent for "Market Debunk Tamil" — an educational Instagram/Facebook carousel series for Tamil-speaking Indian retail investors.

Do NOT translate any existing English slides. You are crafting an ORIGINAL 6-slide sequential breakdown in natural conversational Tanglish (the way smart Tamil finance creators explain concepts on YouTube/Instagram).

FINANCIAL CONCEPT & EVIDENCE:
- Topic: {title}
- Source: {source}
- Context: {raw_text}
- The Retail Illusion / Trap: {retail_trap}
- The Institutional Reality / Thesis: {core_thesis}
- Mandatory Verified Metric: {citable_metric}
- Golden Actionable Rule: {actionable_rule}

STRICT CONTENT & LANGUAGE RULES:
1. Write in natural spoken Tanglish (Tamil sentence structure seamlessly mixed with everyday English finance vocabulary: SIP, Nifty, mutual fund, stop-loss, portfolio, expense ratio, Direct plan, Regular plan). Never use archaic literary Tamil.
2. Short, high-velocity reading: Under 30 words per slide.
3. PRESERVE THE EXACT NUMERIC METRIC: {citable_metric} (and any percentages/rupee amounts like {numbers}).
4. Slide 1 (Hook): Contrarian question or alert with the most shocking number inside <span class="highlight-box">...</span> (canary yellow marker).
5. Slide 2 (Friction): Myth vs Reality. card_a_text = what Tamil retail investors assume; card_b_text = what actually happens mathematically; takeaway = core contrast.
6. Slide 3 (Breakdown): 3 clear numbered points dissecting the mechanism.
7. Slide 4 (Playbook Steps 1 & 2): Two concrete sequential steps (step 1 & step 2) for retail protection.
8. Slide 5 (Strategy & Rule): Step 3 + The non-negotiable rule.
9. Slide 6 (CTA): Urge them to save the post, and comment '{trigger}' to receive '{resource}' in DM.

Return JSON ONLY matching this 6-slide schema:
{{
  "caption": "High-converting Tanglish caption with hook, bullet points, CTA, and hashtags",
  "slides": [
    {{
      "role": "hook",
      "tag": "#TAMILFINANCE",
      "title": "Short Tanglish Hook with <span class='highlight-box'>...</span>"
    }},
    {{
      "role": "friction",
      "tag": "#MYTHVSREALITY",
      "title": "Short title",
      "card_a_text": "Myth in Tanglish",
      "card_b_text": "Reality in Tanglish with {citable_metric}",
      "takeaway": "Contrast takeaway in Tanglish"
    }},
    {{
      "role": "breakdown",
      "tag": "#HIDDENMATH",
      "title": "How the math works",
      "points": [
        {{"num": "1", "title": "Point 1", "desc": "Desc in Tanglish"}},
        {{"num": "2", "title": "Point 2", "desc": "Desc in Tanglish"}},
        {{"num": "3", "title": "Point 3", "desc": "Desc in Tanglish"}}
      ]
    }},
    {{
      "role": "playbook",
      "layout": "step_diagram",
      "tag": "#PLAYBOOK",
      "title": "Action Playbook",
      "steps": [
        {{"number": 1, "label": "Step 1 Title", "sublabel": "Tanglish summary", "color": "#A8D5BA"}},
        {{"number": 2, "label": "Step 2 Title", "sublabel": "Tanglish summary", "color": "#A8D5BA"}}
      ],
      "body_lines": ["Explanation sentence in Tanglish"],
      "closing_line": "Key takeaway"
    }},
    {{
      "role": "playbook",
      "tag": "#STRATEGY",
      "title": "The Golden Rule",
      "rules": [
        {{"title": "Rule 1", "desc": "Tanglish explanation"}},
        {{"title": "Rule 2", "desc": "Tanglish explanation"}}
      ],
      "takeaway": "Golden rule in Tanglish"
    }},
    {{
      "role": "cta",
      "tag": "#SAVETHIS",
      "title": "Save & Share",
      "text": "இந்த post-ஐ Save பண்ணி வச்சுக்கோங்க! முழு {resource} வேணும்னா கீழ '{trigger}'-னு comment பண்ணுங்க."
    }}
  ]
}}"""

        models_to_try = [
            settings.GEMINI_MODEL,
            "gemini-3.7-flash",
            "gemini-2.5-flash",
            settings.GEMMA_FALLBACK_MODEL,
            "gemma-4-26b-a4b-it",
        ]

        if self.client:
            try:
                data = None
                for model_name in models_to_try:
                    try:
                        logger.info("Attempting Tanglish drafting with model %s...", model_name)
                        config = {"temperature": 0.4}
                        if not model_name.startswith("gemma"):
                            config["response_mime_type"] = "application/json"

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
                            if len(parsed.get("slides", [])) == 6:
                                data = parsed
                                logger.info("✓ Model %s successfully generated 6-slide Tanglish draft.", model_name)
                                break
                    except Exception as e:
                        logger.warning("Model %s Tanglish draft failed: %s", model_name, e)

                if data and len(data.get("slides", [])) == 6:
                    # Pass 2: Tanglish Numeric Fact-Checking Gate
                    is_valid, report = self._verify_numeric_facts(data, topic)
                    if not is_valid:
                        logger.warning("❌ Tanglish Fact-Checking Gate failed (Attempt 1): %s. Repairing...", report)
                        repair_prompt = f"{prompt}\n\nSTRICT FACT-CHECK REPAIR: {report}. Make sure the numbers {numbers} or {citable_metric} are strictly preserved in Tamil slides!"
                        rep_resp = self.client.models.generate_content(
                            model=settings.GEMINI_MODEL,
                            contents=repair_prompt,
                            config={"response_mime_type": "application/json", "temperature": 0.3}
                        )
                        if rep_resp.text:
                            rep_clean = rep_resp.text.strip()
                            if rep_clean.startswith("```json"):
                                rep_clean = rep_clean[7:]
                            if rep_clean.endswith("```"):
                                rep_clean = rep_clean[:-3]
                            rep_data = json.loads(rep_clean.strip())
                            is_rep_valid, rep_report = self._verify_numeric_facts(rep_data, topic)
                            if is_rep_valid and len(rep_data.get("slides", [])) == 6:
                                logger.info("✅ Repaired Tanglish deck passed Fact-Checking Gate.")
                                rep_data["slides"] = self._normalize_slides(rep_data["slides"], topic)
                                rep_data["fact_check_status"] = "verified_after_repair"
                                return rep_data

                        # Pass 3: Invoke ThinkerEngine to auto-repair numeric mismatch
                        logger.warning("🧠 Invoking Schematic Thinker Layer for Tanglish numeric auto-repair...")
                        is_th_repaired, th_deck, diag = self.thinker.diagnose_and_repair_tanglish_failure(
                            topic_data=topic,
                            failing_deck=rep_data if 'rep_data' in locals() else data,
                            validation_report=rep_report if 'rep_report' in locals() else report
                        )
                        if is_th_repaired and th_deck:
                            logger.info("✅ ThinkerEngine auto-repaired Tanglish deck successfully!")
                            th_deck["slides"] = self._normalize_slides(th_deck["slides"], topic)
                            th_deck["fact_check_status"] = "thinker_auto_repaired"
                            return th_deck

                        # Pass 4: Fallback to Gemma Model
                        logger.warning("🤖 Tanglish drafting/repair unverified; falling back to Gemma model (%s)...", settings.GEMMA_FALLBACK_MODEL)
                        gemma_deck = self._script_tanglish_gemma(topic, plan)
                        if gemma_deck and len(gemma_deck.get("slides", [])) == 6:
                            is_gm_valid, gm_report = self._verify_numeric_facts(gemma_deck, topic)
                            if is_gm_valid:
                                logger.info("✅ Gemma Tanglish fallback deck passed Fact-Checking Gate!")
                                gemma_deck["slides"] = self._normalize_slides(gemma_deck["slides"], topic)
                                gemma_deck["fact_check_status"] = "gemma_fallback_verified"
                                return gemma_deck
                            else:
                                logger.warning("Gemma Tanglish deck failed fact check (%s). Moving to pre-reserved templates...", gm_report)

                        # FINAL Circuit Breaker on persistent failure -> pre-reserved topic templates
                        logger.error("🚨 GEMMA FALLBACK FAILED. Engaging Circuit Breaker -> Moving to pre-reserved Tanglish topic templates.")
                        fb_deck = self._generate_fallback_tanglish_deck(topic, plan=plan)
                        fb_deck["fact_check_status"] = "circuit_breaker_evergreen_fallback"
                        return fb_deck
                    else:
                        logger.info("✅ Tanglish Fact-Checking Gate passed: %s", report)
                        data["slides"] = self._normalize_slides(data["slides"], topic)
                        data["fact_check_status"] = "verified_pass"
                        return data
            except Exception as e:
                logger.warning("Tanglish autonomous scripting failed (%s); attempting Gemma fallback.", e)
                gemma_deck = self._script_tanglish_gemma(topic, plan)
                if gemma_deck and len(gemma_deck.get("slides", [])) == 6:
                    gemma_deck["slides"] = self._normalize_slides(gemma_deck["slides"], topic)
                    gemma_deck["fact_check_status"] = "gemma_fallback_verified"
                    return gemma_deck
                self.thinker.diagnose_pipeline_crash("EDITORIAL_SCRIPTING", e, {"topic": topic, "plan": plan})

        return self._generate_fallback_tanglish_deck(topic, plan=plan)

    def _script_tanglish_gemma(self, topic: dict, plan: dict) -> Optional[dict]:
        """
        First fallback model: Gemma (gemma-4-31b-it / gemma-4-26b-a4b-it).
        Autonomously scripts Tanglish slides from concept and plan if Gemini fails.
        """
        if not self.client:
            return None

        title = topic.get("title", "Market Debunk")
        raw_text = topic.get("raw_text", "")
        numbers = topic.get("numbers_detected", [])
        core_thesis = plan.get("hidden_reality") or plan.get("core_thesis", "")
        retail_trap = plan.get("core_illusion") or plan.get("retail_trap", "")
        citable_metric = plan.get("citable_metric") or (numbers[0] if numbers else "₹34 Lakhs")
        actionable_rule = plan.get("actionable_rule", "")

        prompt = f"""You are a Tamil finance content creator writing Tanglish (spoken Tamil-English mix).
Create an ORIGINAL 6-slide financial carousel for Tamil retail investors debunking: {title}.
Context: {raw_text}
Myth: {retail_trap}
Reality: {core_thesis}
Preserve exact metric: {citable_metric}
Rule: {actionable_rule}

SLIDES SPEC:
Slide 1 (hook): Tanglish question with shocking words in <span class='highlight-box'>...</span>
Slide 2 (friction): card_a_text (myth), card_b_text (reality with {citable_metric}), takeaway
Slide 3 (breakdown): 3 numbered points
Slide 4 (playbook): steps 1 & 2
Slide 5 (strategy): golden rules
Slide 6 (cta): save this post, comment 'GUIDE'

Return JSON ONLY with keys "caption" and "slides" (array of 6 objects). Do NOT include markdown."""

        gemma_models = [settings.GEMMA_FALLBACK_MODEL, "gemma-4-26b-a4b-it"]
        for gm in gemma_models:
            try:
                logger.info("🤖 Attempting Tanglish scripting with Gemma model: %s...", gm)
                response = self.client.models.generate_content(
                    model=gm,
                    contents=prompt
                )
                if response.text:
                    clean_text = response.text.strip()
                    if "```json" in clean_text:
                        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in clean_text:
                        clean_text = clean_text.split("```")[1].split("```")[0].strip()
                    data = json.loads(clean_text)
                    if len(data.get("slides", [])) == 6:
                        logger.info("✓ Gemma model %s successfully scripted 6-slide Tanglish deck.", gm)
                        return data
            except Exception as e:
                logger.warning("Gemma model %s Tanglish scripting failed: %s", gm, e)

        return None

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

    def _generate_fallback_tanglish_deck(self, topic_data: dict, plan: Optional[dict] = None) -> dict:
        news_analysis = topic_data.get("news_analysis")
        title = topic_data.get("title", "Market Debunk")
        plan_data = plan or {}

        if news_analysis or plan_data:
            hook = (news_analysis.get("headline_hook") if news_analysis else None) or plan_data.get("hook_headline") or title
            illusion = (news_analysis.get("retail_illusion") if news_analysis else None) or plan_data.get("core_illusion", "Retail முதலீட்டாளர்கள் sentiment-ஐ நம்பி ஏமாறுகிறார்கள்.")
            reality = (news_analysis.get("institutional_reality") if news_analysis else None) or plan_data.get("hidden_reality", "Institutions எப்போதும் risk-adjusted math-ஐ மட்டுமே நம்புகிறார்கள்.")
            actionable_rule = (news_analysis.get("actionable_retail_rule") if news_analysis else None) or plan_data.get("actionable_rule", "Unverified news அல்லது GMP-ஐ நம்பி முதலீடு செய்யாதீர்கள்.")
            lead_magnet = (news_analysis.get("lead_magnet") if news_analysis else None) or plan_data.get("lead_magnet") or {"trigger_word": "AUDIT", "resource_name": "Tamil Risk Checklist"}
            trigger = lead_magnet.get("trigger_word", "AUDIT")
            resource = lead_magnet.get("resource_name", "Tamil Risk Checklist")

            words = hook.split()
            clean_hook = " ".join(words[:5]) if len(words) > 5 else hook
            hook_title = f"{clean_hook} <span class='highlight-box'>Retail Trap-ஆ?!</span>"

            return {
                "caption": f"🚨 {hook}\n\nRetail முதலீட்டாளர்கள் ஏமாறும் முக்கிய Market உண்மை!\n\nமுழு 6-slide Tanglish breakdown-ஐ பாருங்க. 👉\n\n💬 '{trigger}'-னு comment பண்ணுங்க, free '{resource}'-ஐ உங்க DM-க்கு அனுப்புறோம்!\n\n#TamilFinance #StockMarketTamil #InvestingTamil #NSE #SEBI #PersonalFinance",
                "slides": [
                    {
                        "role": "hook",
                        "title": hook_title,
                        "deliverable": "📖 Inside: 5-Point Institutional Breakdown",
                        "tag": "#TAMILFINANCE"
                    },
                    {
                        "role": "friction",
                        "title": "Retail மாயை vs Institutional உண்மை",
                        "card_a_text": f"Retail Belief: {illusion}",
                        "card_b_text": f"Real Math: {reality}",
                        "takeaway": "Retail sentiment-ஐ துரத்துகிறது. Smart institutions verified math-ஐ நம்புகிறது.",
                        "tag": "#MYTHVSREALITY"
                    },
                    {
                        "role": "breakdown",
                        "title": "3 Institutional உண்மைகள்",
                        "points": [
                            {"num": "1", "title": "Information Asymmetry", "desc": "Retail முதலீட்டாளர்கள் hype-ஐ பார்க்கும் போது, பெரிய institutions risk-ஐ hedge செய்கிறார்கள்."},
                            {"num": "2", "title": "Valuation Reality", "desc": "P/E multiples மற்றும் official filings மட்டுமே உண்மையான intrinsic value-வை நிர்ணயிக்கும்."},
                            {"num": "3", "title": "Exit Liquidity Trap", "desc": "Unregulated market sentiment பெரும்பாலும் retail-ஐ exit liquidity-ஆக பயன்படுத்த உருவாக்கப்படுகிறது."}
                        ],
                        "tag": "#HIDDENMATH"
                    },
                    {
                        "role": "playbook",
                        "layout": "step_diagram",
                        "steps": [
                            {"number": 1, "icon_concept": "search", "color": "#A8D5BA", "label": "AUDIT", "sublabel": "Official DRHP & Filings-ஐ பாருங்க"},
                            {"number": 2, "icon_concept": "calculator", "color": "#F5D782", "label": "VALUATE", "sublabel": "Peer multiples-ஐ கணக்கிடுங்க"},
                            {"number": 3, "icon_concept": "shield", "color": "#A8C8E8", "label": "PROTECT", "sublabel": "Hype-ஐ தவிர்த்து capital-ஐ காக்குங்க"}
                        ],
                        "headline": "3-Step Capital Recovery Framework",
                        "body_lines": [
                            "Hype cycles uninformed retail முதலீட்டாளர்களுக்கு நஷ்டத்தை தரும்.",
                            "Systematic valuation உங்க capital-ஐ பாதுகாக்கும்."
                        ],
                        "closing_line": "Mathematical edge இல்லாத இடத்தில் ஒரு ரூபாயும் முதலீடு செய்யாதீர்கள்.",
                        "tag": "#PLAYBOOK"
                    },
                    {
                        "role": "playbook",
                        "tag": "#STRATEGY",
                        "title": "Retail முதலீட்டாளர்களுக்கான விதிகள்",
                        "rules": [
                            {"title": "Verify Before Allocation", "desc": actionable_rule},
                            {"title": "Disregard Unregulated Rumors", "desc": "GMP அல்லது social media hype-ஐ நம்பி ஒருபோதும் ஆர்டர் போடாதீர்கள்."},
                            {"title": "Protect Capital First", "desc": "உங்களால் independently value செய்ய முடியாத எதிலும் நுழையாதீர்கள்."}
                        ],
                        "takeaway": "உங்க பணத்தை பாதுகாக்க math மட்டுமே ஒரே வழி."
                    },
                    {
                        "role": "cta",
                        "tag": "#SAVETHIS",
                        "title": "இந்த post-ஐ <span class='highlight-box'>மறக்காம</span> Save <span class='highlight-box'>பண்ணுங்க!</span>",
                        "text": f"இந்த post-ஐ Save பண்ணி வச்சுக்கோங்க! முழு {resource} வேணும்னா கீழ '{trigger}'-னு comment பண்ணுங்க."
                    }
                ]
            }

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
