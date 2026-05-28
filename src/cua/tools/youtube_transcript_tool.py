"""YouTube transcription using YouTube Transcript API with proxy rotation.

Supports up to 10 Webshare proxies to bypass cloud IP blocks on Render/Railway.
Set WEBSHARE_PROXY_LIST (comma-separated) or WEBSHARE_PROXY_URL in env vars.
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
    """Return list of proxy URLs from env vars.

    Priority:
      1. WEBSHARE_PROXY_LIST  — comma-separated list of http://user:pass@ip:port
      2. WEBSHARE_PROXY_URL   — single proxy URL
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
    """Convert a proxy URL string to a requests-style proxy dict."""
    return {"http": proxy_url, "https": proxy_url}


def _safe_proxy_label(proxy_url: str) -> str:
    """Return host:port only (no credentials) for logging."""
    return proxy_url.split("@")[-1] if "@" in proxy_url else proxy_url


# ── Input schema ──────────────────────────────────────────────────────────────

class YouTubeTranscriptInput(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL")
    language: str = Field(default="en", description="Preferred transcript language code")


# ── Tool ──────────────────────────────────────────────────────────────────────

class YouTubeTranscriptTool(BaseTool):
    """Fetches YouTube transcripts with automatic proxy rotation.

    Tries each configured Webshare proxy in order. Falls back to a direct
    (no-proxy) attempt last. This handles YouTube's cloud IP blocks on
    Render, Railway, and similar platforms.
    """

    name: str = "YouTube Transcript Tool"
    description: str = (
        "Get transcripts from YouTube videos using the free YouTube Transcript API. "
        "Automatically rotates through proxies to bypass cloud IP blocks."
    )
    args_schema: type[BaseModel] = YouTubeTranscriptInput

    def _run(self, youtube_url: str, language: str = "en") -> str:
        if not TRANSCRIPT_API_AVAILABLE:
            return "youtube-transcript-api is not installed. Run: pip install youtube-transcript-api"

        video_id = self._extract_video_id(youtube_url)
        if not video_id:
            return f"Invalid YouTube URL: {youtube_url}"

        logger.info(f"Fetching transcript for video: {video_id}")

        # Build attempt list: all proxies first, then no-proxy as last resort
        proxy_list = _get_proxy_list()
        attempt_proxies: List[Optional[str]] = list(proxy_list) + [None]

        last_error: Optional[Exception] = None

        for proxy_url in attempt_proxies:
            label = _safe_proxy_label(proxy_url) if proxy_url else "direct (no proxy)"
            try:
                logger.info(f"Trying via {label}")
                proxies = _proxy_dict(proxy_url) if proxy_url else None
                api = YouTubeTranscriptApi(proxies=proxies) if proxies else YouTubeTranscriptApi()

                try:
                    transcript_list = api.fetch(video_id, languages=[language])
                except NoTranscriptFound:
                    logger.info(f"No '{language}' transcript, falling back to any language")
                    transcript_list = api.fetch(video_id)

                full_text = " ".join(snippet.text for snippet in transcript_list)
                full_text = self._clean_transcript(full_text)
                logger.info(f"Transcript fetched ({len(full_text)} chars) via {label}")
                return full_text

            except (TranscriptsDisabled, VideoUnavailable) as e:
                # Video-level error — no point trying other proxies
                raise e

            except Exception as e:
                last_error = e
                err_lower = str(e).lower()
                is_ip_block = any(k in err_lower for k in [
                    "too many requests", "blocked", "ipblocked",
                    "requestblocked", "rate", "429",
                ])
                if is_ip_block:
                    logger.warning(f"IP blocked via {label}, trying next...")
                    time.sleep(1)
                    continue
                # Non-IP error (e.g. network timeout) — still try next proxy
                logger.warning(f"Error via {label}: {e}, trying next...")
                continue

        # All attempts failed — surface a clean error
        raise last_error or Exception("All proxy attempts failed")

    # ── Exception handlers (called by BaseTool) ───────────────────────────────

    def _handle_error(self, error: Exception) -> str:
        error_msg = str(error)
        logger.error(f"Transcript fetch failed: {error_msg}")

        if isinstance(error, TranscriptsDisabled):
            return (
                f"Transcripts are disabled for this video.\n"
                "The video owner has not provided captions/subtitles."
            )

        if isinstance(error, VideoUnavailable):
            return (
                "Video is unavailable. It may be private, deleted, or region-restricted."
            )

        err_lower = error_msg.lower()
        is_ip_block = any(k in err_lower for k in [
            "too many requests", "blocked", "ipblocked", "requestblocked", "rate", "429",
        ])

        if is_ip_block:
            proxy_list = _get_proxy_list()
            if proxy_list:
                hint = f"All {len(proxy_list)} configured proxies were blocked. Try refreshing your Webshare proxies."
            else:
                hint = (
                    "Fix: Add WEBSHARE_PROXY_LIST to your Render environment variables.\n"
                    "Format: http://user:pass@ip:port,http://user:pass@ip2:port2,..."
                )
            return (
                f"YouTube is blocking requests from this server's IP.\n\n"
                f"{hint}\n\n"
                f"Error detail: {error_msg}"
            )

        return f"Failed to fetch transcript.\n\nError: {error_msg}"

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
    return YouTubeTranscriptTool()._run(youtube_url=youtube_url, language=language)
