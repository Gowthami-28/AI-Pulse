from collectors.rss_collector import fetch_articles
from filters.relevance_filter import filter_articles
from collectors.article_extractor import extract_article_content


# Test 1: Valid URL
articles = fetch_articles()
relevant_articles = filter_articles(articles)
article = relevant_articles[0]

print("TITLE:", article["title"])
print("URL:", article["url"])

full_content = extract_article_content(article["url"])

print("\nFULL ARTICLE CONTENT:\n")

if full_content:
    print(full_content[:2000])
else:
    print("No content extracted.")


# Test 2: Invalid URL
print("\n" + "=" * 50)
print("TESTING INVALID URL")

invalid_content = extract_article_content(
    "https://invalid-example-url-12345.com"
)

if invalid_content is None:
    print("Invalid URL handled correctly.")
else:
    print("Unexpected content extracted.")