"""Collect AI articles from multiple official RSS feeds."""

from typing import Dict, List
import gzip
import urllib.request

import feedparser


RSS_SOURCES = {
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/feed/basic/",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "NVIDIA Developer Blog": "https://developer.nvidia.com/blog/feed/",
}


def fetch_articles() -> List[Dict[str, str]]:
    """Fetch articles from all configured RSS sources."""

    articles = []

    for source_name, rss_url in RSS_SOURCES.items():
        print(f"Collecting articles from: {source_name}")

        if source_name == "Google DeepMind":
            with urllib.request.urlopen(rss_url) as response:
                feed_content = response.read()

            if feed_content.startswith(b"\x1f\x8b"):
                feed_content = gzip.decompress(feed_content)

            feed = feedparser.parse(feed_content.decode("utf-8"))
        else:
            feed = feedparser.parse(rss_url)

        if feed.bozo:
            print(
                f"Could not read {source_name} RSS feed: "
                f"{feed.bozo_exception}"
            )
            continue

        for entry in feed.entries:
            article = {
                "title": entry.get("title", "Untitled article"),
                "url": entry.get("link", ""),
                "publication_date": entry.get(
                    "published",
                    entry.get("updated", "Publication date unavailable")
                ),
                "description": entry.get(
                    "summary",
                    entry.get("description", "")
                ),
                "source_name": source_name,
            }

            articles.append(article)

    return articles


def print_articles(articles: List[Dict[str, str]]) -> None:
    """Print article details in a readable format."""

    if not articles:
        print("No articles were found.")
        return

    for number, article in enumerate(articles, start=1):
        print(f"\n{number}. {article['title']}")
        print(f"   Source: {article['source_name']}")
        print(f"   Published: {article['publication_date']}")
        print(f"   URL: {article['url']}")
        print(f"   Description: {article['description']}")


if __name__ == "__main__":
    articles = fetch_articles()

    print(f"\nTotal articles collected: {len(articles)}")

    print_articles(articles)