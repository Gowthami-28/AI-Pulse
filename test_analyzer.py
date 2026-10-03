import json
from src.collectors.rss_collector import fetch_articles
from src.analyzer.gemini_analyzer import analyze_article

articles = fetch_articles()

article = next(a for a in articles if "Chatham" in a["title"])
print("Testing:", article["title"])
print("URL:", article["url"])

result = analyze_article(article)
print(json.dumps(result, indent=2, ensure_ascii=False))