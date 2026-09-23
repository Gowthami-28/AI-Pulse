from typing import Dict, List #tells python we are working with dict and lists


RELEVANCE_KEYWORDS = [
    "artificial intelligence",
    "generative ai",
    "genai",
    "llm",
    "large language model",
    "gemini",
    "claude",
    "openai",
    "ai model",
    "foundation model",
    "ai agent",
    "agents",
    "agentic",
    "rag",
    "retrieval augmented generation",
    "mcp",
    "model context protocol",
    "api",
    "embedding",
    "vector database",
    "vector db",
    "inference",
    "developer tools",
    "ai developer",
    "machine learning",
    "deep learning",
    "open source model",
]


def filter_articles(articles: List[Dict[str, str]]) -> List[Dict[str, str]]:  #Take a list of article dictionaries → return a list of article dictionaries.
    """Keep articles that contain at least one relevant keyword."""

    relevant_articles = []

    for article in articles:
        text = f"{article['title']} {article['description']}".lower()

        if any(keyword in text for keyword in RELEVANCE_KEYWORDS):
            relevant_articles.append(article)

    return relevant_articles           