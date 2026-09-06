"""
Market Debunk Tamil 7:15 PM Financial Carousel Engine
Main Orchestrator
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import settings, STATE_DIR
from src.research_engine import ResearchEngine
from src.editorial_engine import EditorialEngine
from src.image_director import ImageDirector
from src.publisher import Publisher
from src.thinker_engine import ThinkerEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("market_debunk_tamil_carousel")


def run_pipeline(dry_run: bool = False, master_pkg_path: str = None, override_query: str = None) -> bool:
    logger.info("=" * 60)
    logger.info("🚀 MARKET DEBUNK TAMIL FINANCIAL CAROUSEL ENGINE (7:15 PM DAILY)")
    logger.info("   Mode: %s", "DRY RUN (No live publishing)" if dry_run else "LIVE PRODUCTION")
    logger.info("=" * 60)

    thinker = ThinkerEngine()

    try:
        editorial_engine = EditorialEngine()
        topic_data = None
        deck = None

        # ── Phase 1: Load English Master Package or Sourced Topic ─────────────
        if master_pkg_path and os.path.isfile(master_pkg_path):
            logger.info("═══ Phase 1: Consuming English Master Carousel Package ═══")
            try:
                with open(master_pkg_path, "r", encoding="utf-8") as f:
                    master_pkg = json.load(f)
                topic_data = master_pkg.get("topic", {})
                deck = editorial_engine.compose_from_master(master_pkg)
                logger.info("✓ Independently scripted Tanglish deck from English concept: '%s'!", topic_data.get("title"))
            except Exception as e:
                logger.warning("Failed to parse master package (%s); invoking Thinker Layer.", e)
                thinker.diagnose_master_pkg_failure(master_pkg_path, e)

        if not deck:
            logger.info("═══ Phase 1: Standalone 48h Market News Sourcing ═══")
            research_engine = ResearchEngine()
            topic_data = research_engine.fetch_fresh_market_news(max_age_hours=48, override_query=override_query)
            try:
                from src.news_comprehension_agent import NewsComprehensionAgent
                from src.workflow_agents import PlannerAgent
                nca = NewsComprehensionAgent()
                topic_data["news_analysis"] = nca.analyze_news_item(topic_data)
                planner = PlannerAgent(llm_client=editorial_engine.client)
                plan = planner.plan(topic_data)
            except Exception as pe:
                logger.warning("News analysis error in Tamil standalone: %s", pe)
                plan = {"hidden_reality": topic_data.get("title")}

            mock_master = {"topic": topic_data, "plan": plan}
            deck = editorial_engine.compose_from_master(mock_master)

        slides = deck.get("slides", [])
        from src.validator import CarouselValidator
        is_valid, content_report = CarouselValidator.validate_content(deck)
        if not is_valid:
            raise ValueError(f"Deck failed content validation gate: {content_report}")
        logger.info("✅ %s", content_report)
        logger.info("✓ Prepared %d Tanglish slides.", len(slides))

        # Audio Automation: Select trending Reels audio track for Tamil
        from src.audio_director import AudioDirector
        audio_director = AudioDirector()
        audio_track = audio_director.select_audio_recommendation()
        deck["audio_recommendation"] = audio_track

        # Caption Engineering: Apply Tanglish 4-part formula with audio note and GUIDE trigger
        from src.workflow_agents import GrammarAgent
        grammar_agent = GrammarAgent()
        deck["caption"] = grammar_agent.format_converting_caption(deck, topic_data, audio_track)

        # ── Phase 2: Playwright Visual Rendering & PDF Compilation ─────────────
        logger.info("═══ Phase 2: Playwright 1080x1350 (4:5) Retina Rendering (Tamil) ═══")
        image_director = ImageDirector()
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        visual_pkg = image_director.render_carousel(deck, run_id=run_id)
        slide_paths = visual_pkg["slide_paths"]
        pdf_path = visual_pkg["pdf_path"]

        # ── Phase 2b: Mandatory Per-Slide and PDF Validation Gate ────────────
        logger.info("═══ Phase 2b: Automated Render & Dimension Quality Gate ═══")
        for sp in slide_paths:
            is_png_valid, png_report = CarouselValidator.validate_slide_png(sp)
            if not is_png_valid:
                raise ValueError(f"Slide PNG validation failed: {png_report}")
            logger.info("✓ %s", png_report)

        is_pdf_valid, pdf_report = CarouselValidator.validate_pdf(pdf_path)
        if not is_pdf_valid:
            raise ValueError(f"Multi-page PDF validation failed: {pdf_report}")
        logger.info("✅ %s", pdf_report)

        # ── Phase 3: Prepare Direct Raw Image URLs for Instagram ───────────────
        repo_owner = "arunachalamvenkatachalapathy-dev"
        repo_name = "market-debunk-tamil-carousels"
        image_urls = [
            f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/state/carousel_slides/slide_{i+1}_{run_id}.png"
            for i in range(len(slide_paths))
        ]

        # In CI, if live production run, pre-push slides so raw GitHub URLs are accessible
        if not dry_run and os.getenv("GITHUB_ACTIONS") == "true":
            logger.info("🚀 Pre-pushing Tamil slides to GitHub master before live publishing...")
            os.system("git config --global user.name 'github-actions[bot]'")
            os.system("git config --global user.email 'github-actions[bot]@users.noreply.github.com'")
            os.system("git add state/carousel_slides/ state/latest_carousel.pdf")
            os.system('git commit -m "chore: pre-push tamil slides for live publishing [skip ci]" || true')
            for attempt in range(1, 4):
                os.system("git pull origin master --rebase -X ours || true")
                push_status = os.system("git push origin master")
                if push_status == 0:
                    logger.info("✓ Tamil slides successfully pre-pushed to GitHub master (attempt %d).", attempt)
                    break
                logger.warning("⚠️ Pre-push attempt %d failed; retrying after rebase...", attempt)
                import time
                time.sleep(2)
            import time
            time.sleep(4)

        # ── Phase 4: Multi-Platform Publishing ────────────────────────────────
        logger.info("═══ Phase 4: Multi-Platform Distribution (Tamil) ═══")
        publisher = Publisher()
        results = publisher.publish_all(
            image_urls=image_urls,
            slide_paths=slide_paths,
            pdf_path=pdf_path,
            caption=deck.get("caption", ""),
            title=topic_data.get("title", "Market Debunk Tamil"),
            dry_run=dry_run
        )

        logger.info("📢 Publishing Results: %s", json.dumps(results, indent=2))
        logger.info("=" * 60)
        logger.info("🎉 TAMIL CAROUSEL WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.critical("💥 Tamil pipeline halted by unhandled exception: %s", e, exc_info=True)
        thinker.diagnose_pipeline_crash(
            phase="TAMIL_PIPELINE_ORCHESTRATION",
            error=e,
            context={"dry_run": dry_run, "master_pkg_path": master_pkg_path, "override_query": override_query}
        )
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Market Debunk Tamil Carousel Engine")
    parser.add_argument("--dry-run", action="store_true", help="Generate visuals and PDF without publishing")
    parser.add_argument("--master-pkg", type=str, default=None, help="Path to English master carousel package")
    parser.add_argument("--query", type=str, default=None, help="Override search query for market topic")
    args = parser.parse_args()

    success = run_pipeline(dry_run=args.dry_run, master_pkg_path=args.master_pkg, override_query=args.query)
    sys.exit(0 if success else 1)
