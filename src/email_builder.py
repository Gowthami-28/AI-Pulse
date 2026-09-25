def build_email(ranked_articles):
    """Build the AI Pulse email from ranked Gemini analyses."""

    email_content = "AI PULSE — DAILY LEARNING UPDATE\n\n"

    for index, article in enumerate(
        ranked_articles,
        start=1
    ):
        analysis = article["analysis"]

        # -----------------------------------------------------
        # Article header
        # -----------------------------------------------------

        email_content += (
            f"{index}. {article['title']}\n"
        )

        email_content += (
            f"Score: "
            f"{analysis.get('relevance_score', '')}/10\n"
        )

        email_content += (
            f"Recommendation: "
            f"{analysis.get('recommendation', '')}\n\n"
        )

        email_content += (
            f"Read article: "
            f"{article.get('url', '')}\n\n"
        )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        summary = analysis.get(
            "summary",
            {}
        )

        if isinstance(summary, dict):
            summary_text = summary.get(
                "what_happened",
                ""
            )
        else:
            summary_text = str(summary)

        email_content += "Summary:\n"
        email_content += (
            f"{summary_text}\n\n"
        )

        # -----------------------------------------------------
        # What to Learn
        # -----------------------------------------------------

        email_content += "What to Learn:\n"

        for topic in analysis.get(
            "what_to_learn",
            []
        ):

            if isinstance(topic, dict):
                topic_text = topic.get(
                    "topic",
                    ""
                )
            else:
                topic_text = str(topic)

            if topic_text:
                email_content += (
                    f"- {topic_text}\n"
                )

        # -----------------------------------------------------
        # Why It Matters
        # -----------------------------------------------------

        email_content += (
            "\nWhy It Matters:\n"
        )

        ai_engineer_relevance = analysis.get(
            "ai_engineer_relevance",
            {}
        )

        if isinstance(
            ai_engineer_relevance,
            dict
        ):
            why_it_matters = (
                ai_engineer_relevance.get(
                    "why_it_matters",
                    ""
                )
            )
        else:
            why_it_matters = str(
                ai_engineer_relevance
            )

        email_content += (
            f"{why_it_matters}\n"
        )

        # -----------------------------------------------------
        # Separator
        # -----------------------------------------------------

        email_content += (
            "\n"
            + "-" * 50
            + "\n\n"
        )

    return email_content