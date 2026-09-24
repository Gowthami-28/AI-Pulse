"""Entry point for the AI Pulse content-collection demo."""

from collectors.rss_collector import fetch_articles
from filters.relevance_filter import filter_articles
from filters.freshness_filter import filter_fresh_articles
from analyzer.gemini_analyzer import analyze_article, GeminiQuotaError
from ranking.rank_articles import rank_articles
from email_builder import build_email
from email_sender import send_email



def main() -> None:
    """Fetch, filter, analyze, and rank articles."""
    articles = fetch_articles()
    articles = filter_fresh_articles(articles)

    print(f"Total articles collected: {len(articles)}")

    relevant_articles = filter_articles(articles)

    print(f"Relevant articles: {len(relevant_articles)}")

    analyzed_articles = []

    for article in relevant_articles:
        try:
            analysis = analyze_article(article)
            article["analysis"] = analysis
            analyzed_articles.append(article)

        except GeminiQuotaError as error:
            print("\nGemini API quota exceeded.")
            print(f"Error: {error}")
            print("Stopping further API requests.")
            break

        except Exception as error:
            print(f"\nCould not analyze: {article['title']}")
            print(f"Error: {error}")
            continue

    print(f"\nSuccessfully analyzed: {len(analyzed_articles)}")

    if not analyzed_articles:
        print("No articles were successfully analyzed.")
        return

    
    ranked_articles = rank_articles(analyzed_articles)
    email_content = build_email(ranked_articles)
    send_email(email_content)

    for article in ranked_articles:
        analysis = article["analysis"]

        print(f"\n{'=' * 60}")
        print(f"TITLE: {article['title']}")
        print(f"SCORE: {analysis['relevance_score']}")
        print(f"RECOMMENDATION: {analysis['recommendation']}")

        print("\nSUMMARY:")
        print(analysis["summary"])

        print("\nDEFINITION:")
        print(analysis["definition"])

        print("\nKEY CONCEPTS:")
        for concept in analysis["key_concepts"]:
            print(f"- {concept}")

        print("\nADVANTAGES:")
        for advantage in analysis["advantages"]:
            print(f"- {advantage}")

        print("\nDISADVANTAGES / LIMITATIONS:")
        for disadvantage in analysis["disadvantages"]:
            print(f"- {disadvantage}")

        print("\nPRACTICAL EXAMPLE:")
        print(analysis["practical_example"])

        print("\nWHAT TO LEARN:")
        for topic in analysis["what_to_learn"]:
            print(f"- {topic}")

        print("\nWHY IT MATTERS:")
        print(analysis["why_it_matters"])


if __name__ == "__main__":
    main()