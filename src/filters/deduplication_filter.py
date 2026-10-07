from typing import Dict, List


def remove_duplicates(
    articles: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Remove duplicate articles based on their URL."""

    seen_urls = set()
    unique_articles = []

    for article in articles:
        url = article.get("url", "").strip()

        if not url:
            unique_articles.append(article)
            continue

        if url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    return unique_articles

