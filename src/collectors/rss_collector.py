"""Collect AI articles from multiple official RSS feeds."""

import calendar
import gzip
import html
import re
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List

import feedparser

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Pulse feed reader)"}

# max_age_hours: 48 for news-style feeds, 168 for slower blogs
RSS_SOURCES = {
    "Google AI Blog": {"url": "https://blog.google/technology/ai/rss/", "max_age_hours": 48},
    "OpenAI": {"url": "https://openai.com/news/rss.xml", "max_age_hours": 48},
    "Google DeepMind": {"url": "https://deepmind.google/blog/feed/basic/", "max_age_hours": 168},
    "Hugging Face": {"url": "https://huggingface.co/blog/feed.xml", "max_age_hours": 168},
    "NVIDIA Developer Blog": {"url": "https://developer.nvidia.com/blog/feed/", "max_age_hours": 168},
}


def _fetch_feed(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    return feedparser.parse(data)


def _clean(text: str, limit: int = 600) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _iso_date(entry) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return ""
    ts = calendar.timegm(parsed)  # struct_time from feedparser is UTC
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def fetch_articles() -> List[Dict[str, str]]:
    articles = []

    for source_name, cfg in RSS_SOURCES.items():
        print(f"Collecting articles from: {source_name}")

        try:
            feed = _fetch_feed(cfg["url"])
        except Exception as error:
            print(f"  Failed to fetch {source_name}: {error}")
            continue

        if feed.bozo and not feed.entries:
            print(f"  Could not read {source_name}: {feed.bozo_exception}")
            continue

        print(f"  {len(feed.entries)} entries")

        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue

            articles.append({
                "title": entry.get("title", "Untitled article"),
                "url": url,
                "publication_date": entry.get("published", entry.get("updated", "")),
                "published_iso": _iso_date(entry),
                "description": _clean(entry.get("summary", entry.get("description", ""))),
                "source_name": source_name,
                "max_age_hours": cfg["max_age_hours"],
            })

    return articles