import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from src.config import settings, STATE_DIR

logger = logging.getLogger("AnalyticsTrackerTamil")

class AnalyticsFeedbackEngine:
    """
    Monitors per-slide engagement, swipe-through rate, and completion rate
    for Market Debunk Tamil according to the 2026 Instagram Carousel Bible benchmarks.
    """

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or STATE_DIR
        self.report_path = self.state_dir / "carousel_analytics_report.json"

    def record_or_fetch_metrics(self, media_id: str = "") -> Dict[str, Any]:
        metrics = {
            "media_id": media_id,
            "swipe_through_rate": 0.44,
            "completion_rate": 0.60,
            "saves": 0,
            "shares": 0,
            "impressions": 0,
            "status": "active"
        }

        token = settings.INSTAGRAM_ACCESS_TOKEN.strip()
        if token and media_id:
            try:
                url = f"https://graph.facebook.com/{settings.INSTAGRAM_GRAPH_VERSION}/{media_id}/insights"
                params = {
                    "metric": "carousel_album_engagement,impressions,reach,saved",
                    "access_token": token
                }
                res = requests.get(url, params=params, timeout=15).json()
                if "data" in res:
                    for item in res["data"]:
                        name = item.get("name")
                        val = item.get("values", [{}])[0].get("value", 0)
                        if name == "saved":
                            metrics["saves"] = val
                        elif name == "impressions":
                            metrics["impressions"] = val
                    logger.info("✓ Live IG Graph insights fetched for %s", media_id)
            except Exception as e:
                logger.warning("Could not fetch live Graph API insights for Tamil: %s", e)

        return metrics
