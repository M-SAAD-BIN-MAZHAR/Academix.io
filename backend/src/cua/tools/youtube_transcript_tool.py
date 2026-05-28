"""YouTube transcription using YouTube Transcript API with proxy rotation.

Supports up to 10 Webshare proxies to bypass cloud IP blocks on Render/Railway.
Set WEBSHARE_PROXY_LIST (comma-separated) or WEBSHARE_PROXY_URL in env vars.

Error returns are prefixed with "TRANSCRIPT_ERROR:" so callers can detect them.
"""

import os
import logging
import re
import time
from typing import Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger("Academix.YouTubeTranscript")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    logger.warning("youtube-transcript-api not installed.")


# ── Proxy helpers ─────────────────────────────────────────────────────────────

def _get_proxy_list() -> List[str]:
    """Return list of proxy URLs.

    Reads WEBSHARE_PROXY_LIST (comma-separated) first, then WEBSHARE_PROXY_URL.
    Format: http://user:pass@ip:port
    """
    multi = os.environ.get("WEBSHARE_PROXY_LIST", "").strip()
    if multi:
        proxies = [p.strip() for p in multi.split(",") if p.strip()]
        if proxies:
            return proxies

    single = os.environ.get("WEBSHARE_PROXY_URL", "").strip()
    if single:
        return [single]

    return []


def _proxy_dict(proxy_url: str) -> dict:
    return {"http": proxy_url, "https": proxy_url}


def _safe_label(proxy_url: str) -> str:
    """Return host:port only (strips credentials for logging)."""
    return proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url


# ── Input schema ──────────────────────────────────────────────────────────────

class YouTubeTranscriptInput(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL")
    language: str = Field(default="en", description="Preferred transcript language code")


# ── Tool ──────────────────────────────────────────────────────────────────────

class YouTubeTranscriptTool(BaseTool):
    """Fetches YouTube transcripts with automatic proxy rotation.

    Tries each configured Webshare proxy in order, then falls back to direct.
    Returns a string prefixed with "TRANSCRIPT_ERROR:" on failure so callers
    can detect errors without catching exceptions.
    """

    name: str = "YouTube Transcript Tool"
    description: str = (
        "Get transcripts from YouTube videos using the free YouTube Transcript API. "
        "Automatically rotates through proxies to bypass cloud IP blocks."
    )
    args_schema: type[BaseModel] = YouTubeTranscriptInput

    def _run(self, youtube_url: str, language: str = "en") -> str:
        if not TRANSCRIPT_API_AVAILABLE:
            return "TRANSCRIPT_ERROR: youtube-transcript-api is not installed."

        video_id = self._extract_video_id(youtube_url)
        if not video_id:
            return f"TRANSCRIPT_ERROR: Invalid YouTube URL: {youtube_url}"

        logger.info(f"Fetching transcript for video: {video_id}")

        proxy_list = _get_proxy_list()
        if proxy_list:
            logger.info(f"Proxy rotation enabled: {len(proxy_list)} proxies available")
        else:
            logger.warning("No proxies configured — direct request (likely to be blocked on cloud)")

        # Try each proxy, then fall back to direct (no proxy)
        attempt_proxies: List[Optional[str]] = list(proxy_list) + [None]
        last_error: Optional[Exception] = None

        for proxy_url in attempt_proxies:
            label = _safe_label(proxy_url) if proxy_url else "direct (no proxy)"
            try:
                logger.info(f"Trying transcript via {label}")
                proxies = _proxy_dict(proxy_url) if proxy_url else None
                api = YouTubeTranscriptApi(proxies=proxies) if proxies else YouTubeTranscriptApi()

                try:
                    transcript_list = api.fetch(video_id, languages=[language])
                except NoTranscriptFound:
                    logger.info(f"No '{language}' transcript, trying any available language")
                    transcript_list = api.fetch(video_id)

                full_text = " ".join(snippet.text for snippet in transcript_list)
                full_text = self._clean_transcript(full_text)
                logger.info(f"Transcript fetched successfully ({len(full_text)} chars) via {label}")
                return full_text

            except TranscriptsDisabled:
                return "TRANSCRIPT_ERROR: Transcripts are disabled for this video."

            except VideoUnavailable:
                return "TRANSCRIPT_ERROR: Video is unavailable (private, deleted, or region-restricted)."

            except Exception as e:
                last_error = e
                err_lower = str(e).lower()
                is_ip_block = any(k in err_lower for k in [
                    "too many requests", "blocked", "ipblocked",
                    "requestblocked", "rate", "429",
                ])
                if is_ip_block:
                    logger.warning(f"IP blocked via {label}, rotating to next proxy...")
                    time.sleep(1)
                else:
                    logger.warning(f"Non-IP error via {label}: {e}, trying next proxy...")
                continue

        # All proxies exhausted
        proxy_count = len(proxy_list)
        if proxy_count > 0:
            hint = f"All {proxy_count} proxies were blocked. Refresh your Webshare proxies."
        else:
            hint = "Set WEBSHARE_PROXY_LIST on Render with your Webshare proxy URLs (comma-separated)."
        logger.error(f"All proxy attempts failed. Last error: {last_error}")
        return f"TRANSCRIPT_ERROR: YouTube is blocking all requests from this server. {hint}"

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        return None

    def _clean_transcript(self, transcript: str) -> str:
        transcript = re.sub(r'\s+', ' ', transcript)
        transcript = re.sub(r'\[.*?\]', '', transcript)
        transcript = re.sub(r'\(.*?\)', '', transcript)
        return transcript.strip()

    def get_available_languages(self, youtube_url: str) -> List[str]:
        if not TRANSCRIPT_API_AVAILABLE:
            return []
        try:
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                return []
            proxy_list = _get_proxy_list()
            proxies = _proxy_dict(proxy_list[0]) if proxy_list else None
            api = YouTubeTranscriptApi(proxies=proxies) if proxies else YouTubeTranscriptApi()
            return [t.language_code for t in api.list(video_id)]
        except Exception as e:
            logger.error(f"Failed to get available languages: {e}")
            return []


# ── Convenience function ──────────────────────────────────────────────────────

def get_youtube_transcript(youtube_url: str, language: str = "en") -> str:
    """Returns transcript text, or a string starting with 'TRANSCRIPT_ERROR:' on failure."""
    return YouTubeTranscriptTool()._run(youtube_url=youtube_url, language=language)
