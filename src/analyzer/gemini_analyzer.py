import json
import os
import time
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

MODEL = "gemini-3.5-flash-lite"


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

Score this article specifically for an aspiring AI/ML/GenAI
Engineer who is trying to learn practical technical skills.

The score must reflect the ARTICLE'S ACTUAL TECHNICAL
LEARNING VALUE.

Use an integer from 1 to 10.

Scoring criteria:

9-10:
The article contains substantial technical content that is
directly useful for AI engineering.

Examples:
- LLM architecture or implementation
- AI agent architecture
- RAG systems
- model training or fine-tuning
- inference optimization
- multimodal AI
- embeddings or vector databases
- model evaluation
- AI infrastructure
- MLOps
- deployment of AI systems
- tool/function calling
- practical AI engineering implementation

7-8:
The article contains meaningful technical AI content and
would be useful to learn, but it is not an immediate
priority or does not provide as much technical depth as
a 9-10 article.

5-6:
The article contains some relevant AI or technical
information, but the learning value is limited.

3-4:
The article mentions AI or uses AI technology, but the
article is primarily about business results, product
promotion, company news, marketing, or general technology
rather than technical learning.

1-2:
The article provides little or no useful AI/ML/GenAI
technical learning value.

IMPORTANT SCORING RULES:

1. Do NOT increase the score simply because the article
   mentions a keyword such as "AI", "LLM", "Gemini",
   "agent", "RAG", or "machine learning".

2. Do NOT increase the score because the company is
   important, popular, or well known.

3. Do NOT increase the score because the article reports
   impressive sales, revenue, adoption, productivity,
   customer growth, or business results.

4. A product announcement is NOT automatically highly
   relevant. Give a high score only when the article
   contains meaningful technical information that an
   AI Engineer could learn from.

5. A company case study should receive a high score only
   when it contains substantial technical implementation
   details.

6. If the article only mentions an AI technology without
   explaining or demonstrating meaningful technical
   concepts, give it a low score.

7. If the article appears relevant only because of a
   keyword match but its actual content is unrelated to
   AI/ML/GenAI engineering, give it a score of 1-4.

8. Base the score on the full article content, not only
   the title or description.

9. Be conservative. When uncertain between two scores,
   choose the lower score unless the article provides
   clear technical evidence.

============================================================
RECOMMENDATION
============================================================

Use exactly one of:

NOW
LATER
SKIP

Use the relevance score together with the following rules.

NOW:

Use NOW when the article has a relevance score of 9-10
AND contains technical material that is directly useful
for the user's current AI/ML/GenAI engineering learning.

LATER:

Use LATER when the article has a relevance score of 7-8
and contains genuine technical learning value, but is not
an immediate learning priority.

SKIP:

Use SKIP when the article has a relevance score of 1-6.

Also use SKIP when the article passed the keyword filter
but the full article does not contain meaningful AI/ML/GenAI
engineering learning value.

IMPORTANT:

Do not use NOW simply because the article is about a new
AI product, model, company, or announcement.

Do not use LATER simply because the article contains an
AI-related keyword.

The recommendation must reflect the article's technical
learning value for an aspiring AI Engineer.

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
# Recommendation is computed from the score, not the LLM
# ---------------------------------------------------------

def recommendation_from_score(score: int) -> str:
    if score >= 9:
        return "NOW"
    if score >= 7:
        return "LATER"
    return "SKIP"


# ---------------------------------------------------------
# Analyze one article
# ---------------------------------------------------------

def analyze_article(article: Dict[str, str]) -> Dict[str, Any]:
    """Extract an article and analyze it using Gemini."""

    article_content = extract_article_content(article["url"])

    if not article_content:
        raise ValueError(
            f"Could not extract article content: {article['url']}"
        )

    article_content = article_content[:12000]

    # replace() instead of .format() because the prompt
    # itself contains JSON braces.
    prompt = ANALYSIS_PROMPT
    prompt = prompt.replace("{title}", str(article.get("title", "")))
    prompt = prompt.replace("{source_name}", str(article.get("source_name", "")))
    prompt = prompt.replace("{publication_date}", str(article.get("publication_date", "")))
    prompt = prompt.replace("{description}", str(article.get("description", "")))
    prompt = prompt.replace("{article_content}", article_content)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
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

    response_text = (response.text or "").strip()

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as error:
        print("\nGemini returned invalid JSON:")
        print(response_text)
        raise ValueError("Gemini returned invalid JSON.") from error

    try:
        score = int(result.get("relevance_score", 1))
    except (TypeError, ValueError):
        score = 1

    result["relevance_score"] = score
    result["recommendation"] = recommendation_from_score(score)

    return result


# ---------------------------------------------------------
# Cheap pre-screen (title + description only)
# ---------------------------------------------------------

SCREEN_PROMPT = """Rate 1-10 the technical learning value of this article
for an aspiring AI/ML engineer, using ONLY the title and description.
Concepts (RAG, fine-tuning, MCP, agents, evaluation), model releases
with concrete specs, and engineering write-ups score 6+.
Funding, partnerships, events, pricing, customer stories, and generic
product news score 1-3.
Return JSON only: {"score": 1, "reason": "one sentence"}"""


def screen_article(article: Dict[str, str]) -> int:
    prompt = (
        f"{SCREEN_PROMPT}\n\n"
        f"Title: {article.get('title', '')}\n"
        f"Description: {article.get('description', '')}"
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return int(json.loads(response.text).get("score", 0))

    except Exception as error:
        text = str(error).lower()
        if "429" in text or "quota" in text or "resource_exhausted" in text:
            raise GeminiQuotaError(str(error)) from error
        print(f"Screen failed for '{article.get('title')}': {error}")
        return 0


# ---------------------------------------------------------
# Screen, analyze, and keep only good articles
# ---------------------------------------------------------

def analyze_relevant(articles, screen_min=6, keep_min=7):
    results = []

    for article in articles:
        time.sleep(8)
        try:
            screen = screen_article(article)

            if screen < screen_min:
                print(f"Screened out ({screen}): {article['title']}")
                continue

            result = analyze_article(article)

        except GeminiQuotaError as error:
            print(f"Quota hit, stopping: {error}")
            break

        except Exception as error:
            print(f"Failed '{article['title']}': {error}")
            continue

        if result["relevance_score"] < keep_min:
            print(f"Dropped ({result['relevance_score']}): {article['title']}")
            continue

        result["url"] = article["url"]
        results.append(result)

    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    return results


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def main() -> None:
    articles = fetch_articles()
    recent = filter_recent_articles(articles)
    unique = remove_duplicates(recent)
    relevant = filter_articles(unique)

    print(
        f"Collected {len(articles)} | recent {len(recent)} | "
        f"unique {len(unique)} | keyword-relevant {len(relevant)}"
    )

    if not relevant:
        print("No relevant recent articles found.")
        return

    results = analyze_relevant(relevant)

    print(f"\nKept {len(results)} articles\n")

    for r in results:
        print(f"{r['relevance_score']} {r['recommendation']} | {r['title']}")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()