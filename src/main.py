from src.collectors.rss_collector import fetch_articles
from src.collectors.article_extractor import extract_article_content
from src.filters.relevance_filter import filter_articles
from src.filters.recency_filter import filter_recent_articles
from src.filters.deduplication_filter import remove_duplicates

from src.analyzer.gemini_analyzer import (
    analyze_article,
    GeminiQuotaError,
)

from src.analyzer.gemini_screen import (
    screen_articles,
    GeminiScreenQuotaError,
)

from src.ranking.rank_articles import rank_articles

from src.email_builder import build_email
from src.email_sender import send_email


SCREEN_THRESHOLD = 8


def main() -> None:
    """Fetch, screen, analyze, rank, and email AI Pulse articles."""

    # ---------------------------------------------------------
    # 1. Collect articles
    # ---------------------------------------------------------

    articles = fetch_articles()

    print(
        f"Total articles collected: {len(articles)}"
    )

    # ---------------------------------------------------------
    # 2. Recency filter
    # ---------------------------------------------------------

    recent_articles = filter_recent_articles(
        articles
    )

    print(
        f"Recent articles: {len(recent_articles)}"
    )

    # ---------------------------------------------------------
    # 3. Remove duplicates
    # ---------------------------------------------------------

    unique_articles = remove_duplicates(
        recent_articles
    )

    print(
        f"Unique recent articles: {len(unique_articles)}"
    )

    # ---------------------------------------------------------
    # 4. Lightweight keyword filter
    # ---------------------------------------------------------

    relevant_articles = filter_articles(
        unique_articles
    )

    print(
        f"Keyword candidates: {len(relevant_articles)}"
    )

    # ---------------------------------------------------------
    # 5. Stop if no candidates exist
    # ---------------------------------------------------------

    if not relevant_articles:

        print(
            "No keyword candidates found."
        )

        return

    # ---------------------------------------------------------
    # 6. Batch Gemini relevance screening
    # ---------------------------------------------------------

    try:

        screen_results = screen_articles(
            relevant_articles
        )

    except GeminiScreenQuotaError as error:

        print(
            "\nGemini screening quota exceeded."
        )

        print(
            f"Error: {error}"
        )

        print(
            "Stopping further API requests."
        )

        return

    except Exception as error:

        print(
            "\nCould not complete Gemini screening."
        )

        print(
            f"Error: {error}"
        )

        return

    # ---------------------------------------------------------
    # 7. Keep only high-potential articles
    # ---------------------------------------------------------

    screened_articles = []

    for result in screen_results:

        index = result["article_index"]

        score = result["screen_score"]

        article = relevant_articles[index]

        article["screening"] = result

        print(
            f"\nScreened: {article['title']}"
        )

        print(
            f"Screen score: {score}/10"
        )

        print(
            f"Reason: {result['reason']}"
        )

        if score >= SCREEN_THRESHOLD:

            screened_articles.append(
                article
            )

            print(
                "Decision: PASS"
            )

        else:

            print(
                "Decision: SKIP"
            )

    print(
        f"\nPassed screening: "
        f"{len(screened_articles)}"
    )

    # ---------------------------------------------------------
    # 8. Stop if nothing passed screening
    # ---------------------------------------------------------

    if not screened_articles:

        print(
            "No articles passed the Gemini relevance screen."
        )

        return

    # ---------------------------------------------------------
    # 9. Full Gemini analysis
    # ---------------------------------------------------------

    analyzed_articles = []

    for article in screened_articles:

        try:

            analysis = analyze_article(
                article
            )

            article["analysis"] = analysis

            analyzed_articles.append(
                article
            )

        except GeminiQuotaError as error:

            print(
                "\nGemini API quota exceeded "
                "during full analysis."
            )

            print(
                f"Error: {error}"
            )

            print(
                "Stopping further API requests."
            )

            break

        except Exception as error:

            print(
                f"\nCould not analyze: "
                f"{article['title']}"
            )

            print(
                f"Error: {error}"
            )

            continue

    # ---------------------------------------------------------
    # 10. Analysis result
    # ---------------------------------------------------------

    print(
        f"\nSuccessfully analyzed: "
        f"{len(analyzed_articles)}"
    )

    # ---------------------------------------------------------
    # 11. Stop if nothing was analyzed
    # ---------------------------------------------------------

    if not analyzed_articles:

        print(
            "No articles were successfully analyzed."
        )

        return

    # ---------------------------------------------------------
    # 12. Rank articles
    # ---------------------------------------------------------

    ranked_articles = rank_articles(
        analyzed_articles
    )

    print(
        f"Ranked articles: "
        f"{len(ranked_articles)}"
    )

    # ---------------------------------------------------------
    # 13. Build email
    # ---------------------------------------------------------

    email_content = build_email(
        ranked_articles
    )

    # ---------------------------------------------------------
    # 14. Send email
    # ---------------------------------------------------------

    send_email(
        email_content
    )

    # ---------------------------------------------------------
    # 15. Print final results
    # ---------------------------------------------------------

    for article in ranked_articles:

        analysis = article["analysis"]

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"TITLE: {article['title']}"
        )

        print(
            f"SCORE: "
            f"{analysis['relevance_score']}"
        )

        print(
            f"RECOMMENDATION: "
            f"{analysis['recommendation']}"
        )


if __name__ == "__main__":
    main()