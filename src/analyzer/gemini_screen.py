import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiScreenQuotaError(Exception):
    """Raised when the Gemini screening API quota is exceeded."""


def _parse_json_response(text):
    """
    Parse a Gemini response that should contain JSON.

    Handles plain JSON and JSON wrapped in a markdown code block.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return json.loads(text)


def screen_articles(articles):
    """
    Batch-screen multiple articles in a single Gemini request.

    Uses only title and description.
    Returns one screening result for each article.
    """

    if not articles:
        return []

    article_blocks = []

    for index, article in enumerate(articles):

        article_blocks.append(
            f"""
ARTICLE {index}

TITLE:
{article.get("title", "")}

DESCRIPTION:
{article.get("description", "")}
"""
        )

    articles_text = "\n".join(article_blocks)

    prompt = f"""
You are the first-stage relevance screener for an AI Engineer
learning digest.

Your job is NOT to decide whether the article contains enough
technical detail to fully understand it.

Your job is to identify articles that LOOK PROMISING enough
to justify fetching and performing a full analysis.

Evaluate ONLY the article title and description.

A promising article may be:

- AI/ML/GenAI engineering
- LLMs or multimodal models
- AI agents or agentic systems
- RAG and retrieval systems
- model training or fine-tuning
- inference or model serving
- evaluation or benchmarking
- deployment
- MLOps or LLMOps
- AI infrastructure
- practical AI engineering tools, frameworks, APIs,
  architectures, or techniques

Important:

The title or description does NOT need to contain detailed
implementation information.

If the topic itself strongly suggests that the full article
could contain useful technical information, give it a higher
score and allow the full analyzer to investigate it.

For example, these topics can be promising even when the
description is brief:

- fine-tuning a model
- tracing AI agents
- runtime controls for agents
- deploying AI systems
- RAG improvements
- model evaluation
- inference optimization
- computer-use agents
- agent architectures
- AI development tools

However, do NOT give a high score simply because an article
mentions AI, ChatGPT, Gemini, OpenAI, or another AI product.

Lower scores should be used for:

- purely promotional announcements
- business/customer stories
- vague AI news with no apparent engineering relevance
- unrelated infrastructure or hardware news
- general company news

Articles:

{articles_text}

Return ONLY valid JSON.

The response must be a JSON array containing exactly one
object for each article.

Example:

[
    {{
        "article_index": 0,
        "screen_score": 8,
        "is_relevant": true,
        "reason": "The topic is strongly related to practical AI agent engineering."
    }},
    {{
        "article_index": 1,
        "screen_score": 3,
        "is_relevant": false,
        "reason": "Primarily a business announcement with little apparent engineering value."
    }}
]

Rules:

1. article_index must match the ARTICLE number provided.
2. screen_score must be an integer from 1 to 10.
3. is_relevant must be true or false.
4. Use only the title and description.
5. Do not invent article facts.
6. A score of 7 or higher means the article looks promising
   enough to receive full article analysis.
7. A score below 7 means it should be skipped.
8. Do not require detailed technical information in the
   title or description to give a score of 7 or higher.
9. Keep the reason concise.
10. Return exactly one result for every article.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        results = _parse_json_response(
            response.text
        )

        if not isinstance(results, list):
            raise ValueError(
                "Gemini screening response must be a JSON list."
            )

        if len(results) != len(articles):
            raise ValueError(
                f"Expected {len(articles)} screening results, "
                f"but received {len(results)}."
            )

        validated_results = []

        for result in results:

            if not isinstance(result, dict):
                raise ValueError(
                    "Each screening result must be a JSON object."
                )

            index = result.get("article_index")
            score = result.get("screen_score")
            is_relevant = result.get("is_relevant")
            reason = result.get("reason")

            if not isinstance(index, int):
                raise ValueError(
                    "Invalid article_index returned by Gemini."
                )

            if not 0 <= index < len(articles):
                raise ValueError(
                    "article_index is outside the valid range."
                )

            if not isinstance(score, int) or not 1 <= score <= 10:
                raise ValueError(
                    "Invalid screen_score returned by Gemini."
                )

            if not isinstance(is_relevant, bool):
                raise ValueError(
                    "Invalid is_relevant returned by Gemini."
                )

            if not isinstance(reason, str):
                raise ValueError(
                    "Invalid reason returned by Gemini."
                )

            validated_results.append(result)

        return validated_results

    except Exception as error:

        error_message = str(error)

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
        ):
            raise GeminiScreenQuotaError(
                "Gemini API quota exceeded during batch screening."
            ) from error

        raise