"""Collect articles from the official Google AI Blog RSS feed."""

from typing import Dict, List

import feedparser


GOOGLE_AI_RSS_URL = "https://blog.google/technology/ai/rss/"
SOURCE_NAME = "Google AI Blog"


def fetch_articles() -> List[Dict[str, str]]:
    """Fetch the RSS feed and return its articles as simple dictionaries."""
    feed = feedparser.parse(GOOGLE_AI_RSS_URL)

    if feed.bozo:
        raise RuntimeError(f"Could not read the RSS feed: {feed.bozo_exception}")

    source_name = feed.feed.get("title", SOURCE_NAME)
    articles = []
    for entry in feed.entries:
        article = {
            "title": entry.get("title", "Untitled article"),
            "url": entry.get("link", ""),
            "publication_date": entry.get("published", "Publication date unavailable"),
            "description": entry.get("summary", entry.get("description", "")),
            "source_name": source_name,
        }
        articles.append(article)

    return articles


def print_articles(articles: List[Dict[str, str]]) -> None:
    """Print article details in a readable format."""
    if not articles:
        print("No articles were found in the RSS feed.")
        return

    for number, article in enumerate(articles, start=1):
        print(f"\n{number}. {article['title']}")
        print(f"   Source: {article['source_name']}")
        print(f"   Published: {article['publication_date']}")
        print(f"   URL: {article['url']}")
        print(f"   Description: {article['description']}")
