
import json
import os

from dotenv import load_dotenv
from collectors.article_extractor import extract_article_content
from google import genai

class GeminiQuotaError(Exception):
    """Raised when the Gemini API quota is exceeded."""

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_article(article):
    full_content = extract_article_content(article["url"])

    if full_content is None:
        raise ValueError("Article content could not be extracted.")

    max_characters = 12000
    full_content = full_content[:max_characters]
    

    
    prompt = f"""
Analyze the following AI-related article and create a detailed
learning brief for an aspiring AI Engineer.

Title:
{article["title"]}

Description:
{article["description"]}

Full Article Content:
{full_content}

Return your answer as JSON with exactly these fields:

{{
    "summary": "A detailed explanation based only on the provided article information.",
    "definition": "Define the main technology or concept. Clearly label general background knowledge.",
    "key_concepts": [
        "Important concept explained clearly"
    ],
    "advantages": [
        "Advantage supported by the article or clearly labeled general consideration"
    ],
    "disadvantages": [
        "Limitation supported by the article or clearly labeled general consideration"
    ],
    "practical_example": "Give a practical example. Clearly label it as hypothetical if it is not mentioned in the article.",
    "what_to_learn": [
        "Relevant learning topic"
    ],
    "why_it_matters": "Explain its relevance to an aspiring AI Engineer without making unsupported claims.",
    "relevance_score": 1,
    "recommendation": "NOW"
}}

Rules:

1. Return ONLY valid JSON. Do not use markdown or ```json.
2. relevance_score must be an integer from 1 to 10.
3. recommendation must be exactly one of: NOW, LATER, SKIP.
4. Use the article title and description as the primary source.
5. Never treat an image, title, or guess as confirmed article information.
6. Do not invent features, statistics, product capabilities, or technical details.
7. If the description does not contain enough information, say:
   "The provided description does not contain enough information."
8. Separate information into:
   - Confirmed information from the article.
   - General educational explanation.
   - Hypothetical practical examples.
9. Label general information as:
   "General consideration:" or "General explanation:"
10. Label hypothetical examples as:
    "Hypothetical example:"
11. Do not invent disadvantages just to fill the field.
    If none are supported, explain that specific limitations
    are not mentioned in the provided information.
12. Keep the content detailed but relevant.
13. Use simple, beginner-friendly English.
14. Connect the topic to AI Engineering only when the connection
    is relevant and explainable.
15. Do not assume that an article uses RAG, edge AI, computer
    vision, or any other architecture unless the source supports it.
16. Use the full article content as the primary source.
17. Use the title and description only as supporting information.
18. Do not invent information that is not present in the article content.    
"""

    try:
        response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    except Exception as error:
        error_message = str(error)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise GeminiQuotaError(
                "Gemini API quota exceeded. Please try again later."
            ) from error

        raise

    return json.loads(response.text)


if __name__ == "__main__":
    test_article = {
        "title": "Gemini API Managed Agents",
        "description": (
            "Google introduces new capabilities for building "
            "AI agents using the Gemini API."
        ),
    }

    result = analyze_article(test_article)

    print(json.dumps(result, indent=4))