from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List

RECENCY_HOURS = 48


def parse_publication_date(date_string: str) -> datetime:
    """Parse common RSS publication date formats."""

    # Try ISO 8601 format first
    try:
        parsed_date = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )

        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)

        return parsed_date.astimezone(timezone.utc)

    except ValueError:
        pass

    # Try RFC 822 / RSS date format
    try:
        parsed_date = parsedate_to_datetime(date_string)

        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)

        return parsed_date.astimezone(timezone.utc)

    except (TypeError, ValueError):
        raise ValueError(
            f"Unsupported publication date format: {date_string}"
        )


def filter_recent_articles(
    articles: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Keep only articles published within the last 48 hours."""

    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=RECENCY_HOURS)

    recent_articles = []

    for article in articles:
        publication_date = article.get("publication_date", "")

        try:
            published_time = parse_publication_date(publication_date)

            if published_time >= cutoff_time:
                recent_articles.append(article)

        except ValueError:
            print(
                f"Could not parse publication date: "
                f"{publication_date}"
            )

    return recent_articles


if __name__ == "__main__":
    from src.collectors.rss_collector import fetch_articles

    articles = fetch_articles()

    recent_articles = filter_recent_articles(articles)

    print(f"Total articles collected: {len(articles)}")
    print(f"Recent articles: {len(recent_articles)}")

    for article in recent_articles:
        print(
            article["title"],
            "|",
            article["publication_date"]
        )