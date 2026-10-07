from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List

DEFAULT_RECENCY_HOURS = 48


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
    """Keep articles newer than each source's max_age_hours."""

    now = datetime.now(timezone.utc)
    recent_articles = []

    for article in articles:
        hours = article.get("max_age_hours", DEFAULT_RECENCY_HOURS)
        cutoff = now - timedelta(hours=hours)
        raw_date = (
            article.get("published_iso")
            or article.get("publication_date", "")
        )

        try:
            published = parse_publication_date(raw_date)
        except ValueError:
            print(f"Skipping (bad date): {article.get('title')} | '{raw_date}'")
            continue

        if cutoff <= published <= now + timedelta(hours=1):
            recent_articles.append(article)

    return recent_articles


