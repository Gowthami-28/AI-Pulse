def build_email(ranked_articles):
    """Build the email content from ranked AI Pulse articles."""

    email_content = "AI PULSE — DAILY LEARNING UPDATE\n\n"

    for index, article in enumerate(ranked_articles, start=1):
        analysis = article["analysis"]

        email_content += f"{index}. {article['title']}\n"
        email_content += f"Score: {analysis['relevance_score']}/10\n"
        email_content += f"Recommendation: {analysis['recommendation']}\n\n"
        email_content += f"Read article: {article['url']}\n\n"

        email_content += "Summary:\n"
        email_content += f"{analysis['summary']}\n\n"

        email_content += "What to Learn:\n"
        for topic in analysis["what_to_learn"]:
            email_content += f"- {topic}\n"

        email_content += "\nWhy It Matters:\n"
        email_content += f"{analysis['why_it_matters']}\n"

        email_content += "\n" + "-" * 50 + "\n\n"

    return email_content