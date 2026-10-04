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
You are the first-stage relevance screener for an
AI Engineer learning digest.

Your job is NOT to decide whether an article is merely
related to AI.

Your job is to decide whether an AI Engineer would gain
meaningful, transferable technical learning from the article.

Evaluate ONLY the title and description provided.
Do not invent information that is not present.

ARTICLES:

{articles_text}

Evaluate each article using the following criteria.

HIGH-VALUE TECHNICAL LEARNING includes:

- LLM or GenAI engineering
- AI agents or agentic architectures
- RAG, retrieval, embeddings, or vector databases
- model training or fine-tuning
- inference or model serving
- model evaluation
- prompt engineering when technically meaningful
- AI application architecture
- MLOps or LLMOps
- deployment and production engineering
- AI reliability, observability, or testing
- practical AI engineering tools, frameworks, APIs, or architectures
- concrete engineering methods that can transfer to other projects

IMPORTANT DISTINCTION:

An article being about an AI product does NOT automatically
make it valuable.

An article mentioning agents, LLMs, AI, NVIDIA, OpenAI,
Gemini, or another AI company does NOT automatically
deserve a high score.

The article should provide evidence of something an AI Engineer
could actually learn, such as:

- a technical method
- an architecture
- an implementation approach
- an engineering technique
- an evaluation methodology
- a deployment approach
- a model-training or inference technique
- a practical framework, API, or tool

LOW-VALUE CONTENT:

Strongly reduce the score when the article is primarily:

- a business announcement
- a company or customer success story
- a product launch with little technical detail
- marketing or promotional material
- a general AI announcement
- a vague discussion of AI
- a hardware announcement without useful AI engineering insight
- a highly specialized infrastructure announcement with little
  transferable value
- an article whose title sounds technical but whose description
  provides no evidence of technical learning

SCORING RUBRIC:

9-10:
Exceptional learning value.
Clearly provides important, transferable AI engineering
knowledge or a strong technical method/architecture.

7-8:
Strong learning value.
Clearly relevant to AI engineering and provides enough
technical evidence to justify further analysis.

5-6:
Some AI/technical relevance, but limited learning value,
limited evidence, or too specialized.

3-4:
Mostly announcement, marketing, business, product, or
general AI content with little technical learning.

1-2:
Not meaningfully useful for an AI Engineer learning digest.

IMPORTANT:

A score of 7 or higher should be given ONLY when the title
and description provide reasonable evidence of meaningful
technical learning value.

If the description is empty or extremely vague, do not infer
technical details from the title alone.

For each article, determine:

1. screen_score
2. is_relevant
3. concise reason

is_relevant must be TRUE only when the article provides
meaningful technical learning value for an AI Engineer.

Return ONLY valid JSON.

The response must be a JSON array containing exactly one
object for every article.

Example:

[
    {{
        "article_index": 0,
        "screen_score": 8,
        "is_relevant": true,
        "reason": "Provides a concrete approach to improving RAG retrieval."
    }},
    {{
        "article_index": 1,
        "screen_score": 3,
        "is_relevant": false,
        "reason": "Primarily a product announcement with little technical detail."
    }}
]

RULES:

1. article_index must match the ARTICLE number.
2. screen_score must be an integer from 1 to 10.
3. is_relevant must be true or false.
4. Use ONLY the title and description.
5. Do not invent article facts.
6. Score 7 or higher only when meaningful technical learning
   is supported by the available information.
7. is_relevant must be false when the article lacks enough
   evidence of useful technical learning.
8. Keep the reason concise.
9. Return exactly one result for every article.
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