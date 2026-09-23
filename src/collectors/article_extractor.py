import trafilatura


def extract_article_content(url: str) -> str | None:
    """Fetch and extract the main content from an article webpage."""

    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            print(f"Could not download article: {url}")
            return None

        content = trafilatura.extract(downloaded)

        if content is None:
            print(f"Could not extract article content: {url}")
            return None

        return content

    except Exception as error:
        print(f"Article extraction failed: {error}")
        return None