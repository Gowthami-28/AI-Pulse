from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List


FRESHNESS_HOURS = 48


def filter_fresh_articles(articles: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Keep only articles published within the last 48 hours."""

    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=FRESHNESS_HOURS)

    fresh_articles = []

    for article in articles:
        publication_date = article.get("publication_date", "")

        try:
            published_time = parsedate_to_datetime(publication_date)

            if published_time >= cutoff_time:
                fresh_articles.append(article)

        except (TypeError, ValueError):
            print(
                f"Could not parse publication date: "
                f"{publication_date}"
            )

    return fresh_articles


if __name__ == "__main__":
    from collectors.rss_collector import fetch_articles

    articles = fetch_articles()

    fresh_articles = filter_fresh_articles(articles)

    print(f"Total articles: {len(articles)}")
    print(f"Fresh articles: {len(fresh_articles)}")

    for article in fresh_articles:
        print(
            article["title"],
            "|",
            article["publication_date"]
        ) 