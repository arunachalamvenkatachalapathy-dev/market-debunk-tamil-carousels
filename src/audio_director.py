import random
import logging
from typing import Dict, Any

logger = logging.getLogger("AudioDirectorTamil")

TRENDING_FINANCE_TRACKS_TAMIL = [
    {
        "title": "Cornfield Chase (Interstellar Tension)",
        "artist": "Hans Zimmer / Dorian Marko",
        "bpm": 100,
        "vibe": "Cinematic Tension & Deep Focus",
        "reels_boost_tier": "High Velocity",
        "search_query": "Hans Zimmer Cornfield Chase Dorian Marko"
    },
    {
        "title": "Time (Institutional Minimalist Mix)",
        "artist": "Hans Zimmer",
        "bpm": 124,
        "vibe": "Deep Mathematical Compounding",
        "reels_boost_tier": "Top Tier",
        "search_query": "Hans Zimmer Time Inception"
    },
    {
        "title": "Master The Blaster (Instrumental Flow)",
        "artist": "Anirudh Ravichander",
        "bpm": 115,
        "vibe": "High Energy Capital Momentum",
        "reels_boost_tier": "Viral Regional",
        "search_query": "Master The Blaster Instrumental Anirudh"
    },
    {
        "title": "Azhagiya Theeye (Acoustic Minimal)",
        "artist": "Harris Jayaraj / Classical Touch",
        "bpm": 108,
        "vibe": "Calm Rational Thinking",
        "reels_boost_tier": "High Retention",
        "search_query": "Harris Jayaraj Instrumental Acoustic"
    },
    {
        "title": "Experience (Ludovico Instrumental)",
        "artist": "Ludovico Einaudi",
        "bpm": 95,
        "vibe": "Compounding Breakthrough",
        "reels_boost_tier": "Top Tier",
        "search_query": "Ludovico Einaudi Experience"
    }
]


class AudioDirector:
    """
    Curates high-retention audio tracks for Market Debunk Tamil carousels
    to activate the Instagram algorithm's Reels surface recommendation engine.
    """
    def __init__(self):
        self.tracks = TRENDING_FINANCE_TRACKS_TAMIL

    def select_audio_recommendation(self, archetype: str = "") -> Dict[str, Any]:
        track = random.choice(self.tracks)
        logger.info("🎵 Curated trending audio recommendation for Tamil: %s by %s", track["title"], track["artist"])
        return track
