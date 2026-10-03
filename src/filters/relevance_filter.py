import re
from typing import Dict, List

STRONG = [
    "llm", "large language model", "fine-tuning", "fine tuning",
    "rag", "retrieval-augmented generation", "retrieval augmented generation",
    "vector database", "model context protocol", "mcp",
    "tool calling", "function calling", "ai agent", "ai agents",
    "agentic ai", "mlops", "llmops", "vlm", "vision-language model",
    "mixture of experts", "diffusion model", "reinforcement learning",
    "foundation model", "multimodal", "model training", "quantization",
    "agent", "agents", "agentic", "computer-use", "computer use",
    "text-to-speech", "speech", "recommender", "tabular",
    "tensorrt", "nemotron", "triton", "nemo", "training data",
    "benchmark", "open-source model", "open-sourcing", "open source",
    "leaderboard", "evaluation", "sdk", "inference", "embedding", "embeddings",
]

WEAK = [
    "gemini", "claude", "openai", "gpt", "chatgpt", "llama", "gemma",
    "mistral", "qwen", "deepmind", "hugging face",
    "transformer", "machine learning", "deep learning", "computer vision",
    "nlp", "robotics", "artificial intelligence", "generative ai",
]

NEGATIVE = [
    "funding", "raises", "series a", "series b", "partnership",
    "partners with", "webinar", "event", "conference", "keynote",
    "customer story", "case study", "pricing", "earnings",
    "we're hiring", "join us", "now available in",
    "with openai", "reimagining", "scales its", "transforms",
    "news we announced", "customer", "is using",
]

MODEL_RELEASE_RE = re.compile(
    r"\b(gpt-?\d|gemini \d|claude \d|llama ?\d|gemma ?\d|qwen ?\d|"
    r"mistral|model guide)\b",
    re.IGNORECASE,
)


def _compile(terms):
    return re.compile(
        r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b",
        re.IGNORECASE,
    )


STRONG_RE = _compile(STRONG)
WEAK_RE = _compile(WEAK)
NEG_RE = _compile(NEGATIVE)


def filter_articles(
    articles: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Keep articles that pass the strong/weak/negative keyword rules."""

    kept = []

    for a in articles:
        title = a.get("title", "")
        text = f"{title} {a.get('description', '')}"

        strong = set(m.lower() for m in STRONG_RE.findall(text))
        weak = set(m.lower() for m in WEAK_RE.findall(text))
        model_release = bool(MODEL_RELEASE_RE.search(title))
        neg_in_title = bool(NEG_RE.search(title))

        passes = bool(strong) or len(weak) >= 2 or model_release

        if neg_in_title and not strong and not model_release:
            passes = False

        if passes:
            a["matched_keywords"] = ", ".join(sorted(strong | weak))
            kept.append(a)
        else:
            print(f"Rejected by keywords: {title}")

    return kept


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
            f"\nMatched keywords: {article.get('matched_keywords', '')}"
        )