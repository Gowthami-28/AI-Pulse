def rank_articles(articles):
    """Sort articles from highest to lowest relevance score."""

    return sorted(
        articles,
        key=lambda article: article["analysis"]["relevance_score"],
        reverse=True,
    )