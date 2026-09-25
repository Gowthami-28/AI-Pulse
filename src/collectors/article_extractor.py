import requests
import trafilatura


def extract_article_content(url: str) -> str | None:
    """Fetch and extract the main content from an article webpage."""

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20,
        )

        response.raise_for_status()

        downloaded = response.text

        content = trafilatura.extract(downloaded)

        if content is None:
            print(f"Could not extract article content: {url}")
            return None

        return content

    except requests.RequestException as error:
        print(f"Could not download article: {url}")
        print(f"Download error: {error}")
        return None

    except Exception as error:
        print(f"Article extraction failed: {error}")
        return None