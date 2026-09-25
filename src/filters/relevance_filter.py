from typing import Dict, List


RELEVANCE_KEYWORDS = [
    # Core AI
    "artificial intelligence",
    "generative ai",
    "genai",
    "ai model",
    "foundation model",
    "machine learning",
    "deep learning",

    # LLMs
    "llm",
    "large language model",
    "language model",
    "transformer",

    # AI models and ecosystem
    "openai",
    "gemini",
    "gpt",
    "chatgpt",
    "claude",
    "llama",
    "gemma",
    "mistral",
    "qwen",
    "deepmind",
    "hugging face",

    # AI model types and research
    "multimodal",
    "vision-language",
    "vision language",
    "vision-language model",
    "vlm",
    "computer vision",
    "natural language processing",
    "nlp",
    "diffusion model",
    "reinforcement learning",
    "fine-tuning",
    "fine tuning",
    "model training",
    "model inference",
    "inference",
    "moe",
    "mixture of experts",

    # AI agents
    "ai agent",
    "ai agents",
    "agentic ai",
    "agentic",
    "tool calling",
    "function calling",
    "mcp",
    "model context protocol",

    # RAG
    "rag",
    "retrieval augmented generation",
    "retrieval-augmented generation",
    "embedding",
    "embeddings",
    "vector database",
    "vector db",

    # AI engineering
    "mlops",
    "llmops",
    "ai engineering",
    "machine learning engineering",
    "ai developer",
    "ai framework",
    "ai sdk",
    "ai compute",
    "ai workload",
    "ai workloads",
    "ai infrastructure",

    # AI applications
    "robotics",

    # Open-source AI
    "open source model",
    "open-source model",
]


def filter_articles(
    articles: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Keep articles that contain at least one relevant keyword."""

    relevant_articles = []

    for article in articles:
        text = (
            f"{article['title']} {article['description']}"
        ).lower()

        matched_keywords = [
            keyword
            for keyword in RELEVANCE_KEYWORDS
            if keyword in text
        ]

        if matched_keywords:
            article["matched_keywords"] = ", ".join(matched_keywords)
            relevant_articles.append(article)

    return relevant_articles


if __name__ == "__main__":
    from src.collectors.rss_collector import fetch_articles
    from src.filters.recency_filter import filter_recent_articles
    from src.filters.deduplication_filter import remove_duplicates

    articles = fetch_articles()

    recent_articles = filter_recent_articles(articles)

    unique_articles = remove_duplicates(recent_articles)

    relevant_articles = filter_articles(unique_articles)

    print(f"Total articles collected: {len(articles)}")
    print(f"Recent articles: {len(recent_articles)}")
    print(f"Unique recent articles: {len(unique_articles)}")
    print(f"Relevant articles: {len(relevant_articles)}")

    for article in relevant_articles:
        print(
            f"\n{article['title']}"
            f"\nSource: {article['source_name']}"
            f"\nMatched keywords: {article['matched_keywords']}"
        )           