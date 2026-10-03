"""Entry point for the AI Pulse pipeline."""

from src.collectors.rss_collector import fetch_articles
from src.filters.relevance_filter import filter_articles
from src.filters.recency_filter import filter_recent_articles
from src.filters.deduplication_filter import remove_duplicates
from src.analyzer.gemini_analyzer import analyze_relevant
from src.ranking.rank_articles import rank_articles
from src.email_builder import build_email
from src.email_sender import send_email


def main() -> None:
    """Fetch, filter, analyze, rank, and email articles."""

    # 1. Collect articles
    articles = fetch_articles()
    print(f"Total articles collected: {len(articles)}")

    # 2. Recency filter
    recent_articles = filter_recent_articles(articles)
    print(f"Recent articles: {len(recent_articles)}")

    # 3. Remove duplicates
    unique_articles = remove_duplicates(recent_articles)
    print(f"Unique recent articles: {len(unique_articles)}")

    # 4. Keyword filter
    relevant_articles = filter_articles(unique_articles)
    print(f"Relevant articles: {len(relevant_articles)}")

    # 5. Pre-screen + Gemini analysis + score gate
    results = analyze_relevant(relevant_articles)

    # Put each result back on its original article as article["analysis"]
    by_url = {a["url"]: a for a in relevant_articles}
    analyzed_articles = []

    for result in results:
        article = by_url.get(result.get("url"))
        if article is None:
            continue
        article["analysis"] = result
        analyzed_articles.append(article)

    print(f"\nKept after analysis: {len(analyzed_articles)}")

    # 6. Stop if nothing passed the gate
    if not analyzed_articles:
        print("No articles passed the relevance gate. No email sent.")
        return

    # 7. Rank articles
    ranked_articles = rank_articles(analyzed_articles)
    print(f"Ranked articles: {len(ranked_articles)}")

    # 8. Build email
    email_content = build_email(ranked_articles)

    # 9. Send email
    send_email(email_content)

    print("\nAI Pulse email sent successfully.")


if __name__ == "__main__":
    main()