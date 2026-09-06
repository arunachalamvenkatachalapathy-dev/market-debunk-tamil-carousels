import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "src" / "templates"
DATA_DIR = ROOT_DIR / "data"
STATE_DIR = ROOT_DIR / "state"
FONTS_DIR = ROOT_DIR / "assets" / "fonts"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    # ── Slide & Visual Specifications ─────────────────────────────────────────
    EXPECTED_SLIDE_COUNT: int = 8
    SLIDE_WIDTH: int = 1080
    SLIDE_HEIGHT: int = 1350
    PDF_DPI: int = 300

    # ── Strict Reference Design Tokens ────────────────────────────────────────
    BG_COLOR: str = "#f8f8f9"
    BRAND_GREEN: str = "#16a34a"
    CARD_GREEN: str = "#15803d"
    TEXT_WHITE: str = "#ffffff"
    TEXT_MUTED: str = "#333333"
    BRAND_URL: str = "www.marketdebunk.com"
    # ── AI Keys ─────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    GEMMA_FALLBACK_MODEL: str = os.getenv("GEMMA_FALLBACK_MODEL", "gemma-4-31b-it")

    # ── News / Market Sourcing ──────────────────────────────────────────────
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    MARKETAUX_API_TOKEN: str = os.getenv("MARKETAUX_API_TOKEN", "bZ1PVR803PweIGinKuMa1r6Zk4kPn4v8xikQvUkC")
    INDIAN_API_KEY: str = os.getenv("INDIAN_API_KEY", "sk-live-Ca1EJj4XFo61nRpchb93tlGrs0IyVEC5cl4A6iF5")

    # ── Meta (Instagram & Facebook) ─────────────────────────────────────────
    INSTAGRAM_USER_ID: str = os.getenv("INSTAGRAM_USER_ID", "17841436821575762")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_GRAPH_VERSION: str = os.getenv("INSTAGRAM_GRAPH_VERSION", "v21.0")

    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "1297757220087165")
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")

    # ── Telegram ────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ── LinkedIn (Strictly disabled for Tamil companion) ────────────────────
    ENABLE_LINKEDIN: bool = False
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_ORGANIZATION_URN: str = ""

    # ── Feature Flags ───────────────────────────────────────────────────────
    ENABLE_INSTAGRAM: bool = os.getenv("ENABLE_INSTAGRAM", "true").lower() == "true"
    ENABLE_FACEBOOK: bool = os.getenv("ENABLE_FACEBOOK", "true").lower() == "true"
    ENABLE_TELEGRAM: bool = os.getenv("ENABLE_TELEGRAM", "true").lower() == "true"

    # ── Branding ────────────────────────────────────────────────────────────
    BRAND_NAME: str = "Market Debunk Tamil"
    BRAND_SUBTITLE: str = "பங்குச் சந்தை உண்மைகள் & நிதி விழிப்புணர்வு"
    BRAND_HANDLE: str = "@marketdebunk_tamil"

settings = Settings()
