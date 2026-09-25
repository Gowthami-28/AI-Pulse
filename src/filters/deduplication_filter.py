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

if __name__ == "__main__":
    from src.collectors.rss_collector import fetch_articles
    from src.filters.recency_filter import filter_recent_articles

    articles = fetch_articles()
    recent_articles = filter_recent_articles(articles)
    unique_articles = remove_duplicates(recent_articles)

    print(f"Total articles collected: {len(articles)}")
    print(f"Recent articles: {len(recent_articles)}")
    print(f"Unique recent articles: {len(unique_articles)}")    