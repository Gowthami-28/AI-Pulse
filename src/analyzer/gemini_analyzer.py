import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.collectors.article_extractor import extract_article_content
from src.collectors.rss_collector import fetch_articles
from src.filters.recency_filter import filter_recent_articles
from src.filters.deduplication_filter import remove_duplicates
from src.filters.relevance_filter import filter_articles


# ---------------------------------------------------------
# Environment setup
# ---------------------------------------------------------

load_dotenv()


class GeminiQuotaError(Exception):
    """Raised when Gemini API quota is exhausted."""


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the environment."
    )


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# Gemini analysis prompt
# ---------------------------------------------------------

ANALYSIS_PROMPT = """
You are the analysis engine for AI Pulse, a personal AI/ML
learning digest.

Your job is to turn one technology article into a factual,
useful, beginner-friendly learning analysis.

============================================================
SOURCE PRIORITY
============================================================

1. The full article content is the primary source.

2. The title, source, publication date, and description provide
   supporting context.

3. Never invent facts, benchmarks, features, capabilities,
   limitations, or technical details.

4. If the article does not support a field, return an empty
   string or empty list.

============================================================
SUMMARY
============================================================

- Explain what actually happened in the article.
- Explain why it matters based on the article.
- Give one concise main takeaway.
- Do not turn marketing claims into independently verified facts.
- Preserve important qualifiers when the article attributes
  information to a company or another source.

============================================================
MAIN TECHNOLOGY
============================================================

Identify ONE primary technology, method, product, model, or
technical approach that is central to the article.

IMPORTANT:

- Do not list multiple technologies in the "name" field.
- Choose the technology that is most central to the article.
- Supporting technologies can be mentioned in "how_it_works"
  or "key_concepts".
- Define the primary technology using information supported
  by the article.
- Explain how it works only to the level supported by the
  article.
- Do not add technical details from general knowledge if the
  article does not provide them.
- If the article is mainly a company/product story and no
  single technical technology is central, identify the central
  technical concept or product.

============================================================
KEY CONCEPTS
============================================================

- Include 2 to 5 important technical concepts when available.
- Each concept must be supported by the article.
- Explain each concept simply and clearly.
- Do not add generic AI concepts merely because they are related
  to the article.
- Do not repeat the same concept using different wording.

============================================================
ARTICLE FACTS
============================================================

Include concrete facts explicitly stated in the article.

Examples:

- numbers
- measurements
- benchmarks
- capabilities
- product features
- technical details
- examples
- reported results

IMPORTANT:

If a result or statement comes from a company, preserve that
context.

For example:

"According to the company, the system reduced processing time
by 40%."

Do NOT rewrite that as:

"The system objectively reduced processing time by 40%."

Do not turn claims into independently verified facts.

============================================================
ADVANTAGES
============================================================

Include advantages only when supported by the article.

Do not invent advantages.

If the article does not provide enough evidence for advantages,
return:

[]

============================================================
LIMITATIONS
============================================================

Include limitations only when supported by the article.

Do not invent limitations just to fill the field.

If the article does not discuss limitations, return:

[]

============================================================
PRACTICAL EXAMPLE
============================================================

Give one simple hypothetical example showing how the central
technology could be used.

The example must:

- be clearly labeled "Hypothetical example"
- help a beginner understand the technology
- not be presented as something that actually happened
  in the article

============================================================
AI ENGINEER RELEVANCE
============================================================

Explain the concrete technical relevance of the article to an
AI/ML/GenAI engineer.

Focus on things such as:

- AI agent development
- LLM integration
- model inference
- RAG
- embeddings
- vector databases
- model training
- fine-tuning
- evaluation
- MLOps
- AI infrastructure
- workflow automation
- computer vision
- NLP
- multimodal systems
- tool calling
- APIs
- deployment

Only include skills that are genuinely connected to the article.

Do not use generic items such as:

- AI
- technology
- innovation
- problem solving

============================================================
WHAT TO LEARN
============================================================

Give 1 to 4 specific learning topics based on the article.

Each topic must include:

- the topic
- why learning it would help understand or reproduce
  the technical ideas in the article

Do not recommend unrelated learning topics.

============================================================
RELEVANCE SCORE
============================================================

Score the article for the AI Pulse user's AI/ML learning goals.

Use an integer from 1 to 10.

10 = directly useful for current AI/ML/GenAI engineering learning.

1 = little or no useful technical learning value.

Base the score on the article's actual technical content.

Do not score the article based on:

- company popularity
- product popularity
- sales performance
- media attention
- general business success

============================================================
RECOMMENDATION
============================================================

Use exactly one of:

NOW
LATER
SKIP

Definitions:

NOW:
Directly useful and worth learning now.

LATER:
Technically useful but not an immediate learning priority.

SKIP:
Little useful learning value for the user's AI/ML learning goals.

Do not use the recommendation to judge the company,
product, or business success.

============================================================
OUTPUT RULES
============================================================

Return only valid JSON.

Do not use markdown fences.

Do not include explanations outside the JSON object.

Return exactly this structure:

{
  "title": "",
  "source": "",
  "publication_date": "",
  "summary": {
    "what_happened": "",
    "why_it_matters": "",
    "main_takeaway": ""
  },
  "main_technology": {
    "name": "",
    "definition": "",
    "how_it_works": ""
  },
  "key_concepts": [
    {
      "concept": "",
      "explanation": ""
    }
  ],
  "article_facts": [],
  "advantages": [],
  "limitations": [],
  "practical_example": {
    "type": "Hypothetical example",
    "example": ""
  },
  "ai_engineer_relevance": {
    "why_it_matters": "",
    "skills_involved": []
  },
  "what_to_learn": [
    {
      "topic": "",
      "why": ""
    }
  ],
  "relevance_score": 1,
  "recommendation": "NOW"
}

============================================================
ARTICLE METADATA
============================================================

Title: {title}

Source: {source_name}

Publication date: {publication_date}

Description: {description}

============================================================
FULL ARTICLE CONTENT
============================================================

{article_content}
"""


# ---------------------------------------------------------
# Analyze one article
# ---------------------------------------------------------

def analyze_article(article: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract an article and analyze it using Gemini.
    """

    # Extract article content
    article_content = extract_article_content(
        article["url"]
    )

    if not article_content:
        raise ValueError(
            f"Could not extract article content: {article['url']}"
        )

    # Limit article size sent to Gemini
    article_content = article_content[:12000]

    # -----------------------------------------------------
    # Build prompt safely
    #
    # We use replace() instead of .format() because the
    # prompt itself contains JSON braces.
    # -----------------------------------------------------

    prompt = ANALYSIS_PROMPT

    prompt = prompt.replace(
        "{title}",
        article.get("title", "")
    )

    prompt = prompt.replace(
        "{source_name}",
        article.get("source_name", "")
    )

    prompt = prompt.replace(
        "{publication_date}",
        article.get("publication_date", "")
    )

    prompt = prompt.replace(
        "{description}",
        article.get("description", "")
    )

    prompt = prompt.replace(
        "{article_content}",
        article_content
    )

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

    except Exception as error:

        error_text = str(error).lower()

        if (
            "resource_exhausted" in error_text
            or "429" in error_text
            or "quota" in error_text
        ):
            raise GeminiQuotaError(
                f"Gemini quota exhausted: {error}"
            ) from error

        raise

    # -----------------------------------------------------
    # Validate response
    # -----------------------------------------------------

    response_text = response.text.strip()

    if not response_text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:

        result = json.loads(response_text)

    except json.JSONDecodeError as error:

        print("\nGemini returned invalid JSON:")
        print(response_text)

        raise ValueError(
            "Gemini returned invalid JSON."
        ) from error

    return result


# ---------------------------------------------------------
# Main test pipeline
# ---------------------------------------------------------

def main() -> None:
    """
    Run the AI Pulse article analysis pipeline.
    """

    # -----------------------------------------------------
    # 1. Collect articles
    # -----------------------------------------------------

    articles = fetch_articles()

    # -----------------------------------------------------
    # 2. Recency filter
    # -----------------------------------------------------

    recent_articles = filter_recent_articles(
        articles
    )

    # -----------------------------------------------------
    # 3. Remove duplicate URLs
    # -----------------------------------------------------

    unique_articles = remove_duplicates(
        recent_articles
    )

    # -----------------------------------------------------
    # 4. AI relevance filter
    # -----------------------------------------------------

    relevant_articles = filter_articles(
        unique_articles
    )

    # -----------------------------------------------------
    # 5. Stop if nothing relevant was found
    # -----------------------------------------------------

    if not relevant_articles:

        print(
            "No relevant recent articles found."
        )

        return

    # -----------------------------------------------------
    # 6. Select first article for testing
    # -----------------------------------------------------

    test_article = relevant_articles[0]

    print(
        f"Testing article: {test_article['title']}"
    )

    print(
        f"Source: {test_article['source_name']}"
    )

    print(
        f"URL: {test_article['url']}"
    )

    print(
        "\nAnalyzing article...\n"
    )

    # -----------------------------------------------------
    # 7. Analyze with Gemini
    # -----------------------------------------------------

    try:

        result = analyze_article(
            test_article
        )

        # -------------------------------------------------
        # 8. Display structured result
        # -------------------------------------------------

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

    except GeminiQuotaError as error:

        print(
            f"Gemini quota error: {error}"
        )

    except Exception as error:

        print(
            f"Analysis failed: {error}"
        )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()