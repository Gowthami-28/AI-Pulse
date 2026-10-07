# AI Pulse

AI Pulse is a personal AI/ML learning assistant that discovers recent AI developments, filters relevant articles, analyzes promising content using Gemini, ranks articles by technical learning value, and sends a personalized daily AI/ML learning update by email.

## Status

Production-ready local pipeline. Docker and Azure deployment are the next steps.


## Features

- Collects AI/ML articles from multiple official RSS sources
- Applies source-specific recency filtering
- Removes duplicate articles using URLs
- Filters articles using local AI/ML relevance keywords
- Uses Gemini for batch relevance screening
- Performs detailed Gemini analysis on promising articles
- Ranks articles by relevance and learning value
- Builds a personalized email update
- Sends the daily AI/ML learning update using Resend
- Handles individual article failures without stopping the entire pipeline
- Optimizes Gemini API usage with batch screening and controlled input/output sizes


## How It Works

RSS Sources
↓
Article Collection
↓
Recency Filtering
↓
Duplicate Removal
↓
Keyword Relevance Filtering
↓
Gemini Relevance Screening
↓
Articles scoring 8/10 or higher
↓
Article Content Extraction
↓
Gemini Full Analysis
↓
Ranking
↓
Email Builder
↓
Resend
↓
Daily AI/ML Learning Update

## RSS Sources

AI Pulse currently collects articles from:

| Source | Recency Window |
|---|---:|
| Google AI Blog | 48 hours |
| OpenAI | 48 hours |
| Google DeepMind | 7 days |
| Hugging Face | 7 days |
| NVIDIA Developer Blog | 7 days |


## Filtering

AI Pulse uses multiple filtering stages to reduce unnecessary processing:

1. **Recency filtering** — keeps articles within the configured source-specific time window.
2. **Duplicate removal** — removes duplicate articles using their URLs.
3. **Keyword filtering** — identifies articles related to AI/ML using predefined relevance keywords.
4. **Gemini screening** — scores keyword candidates from 1–10 and only sends articles scoring **8 or higher** for full analysis.

## Gemini Screening

After local filtering, AI Pulse uses Gemini to evaluate the remaining articles in batches.

Each article receives a screening score from 1–10. Articles scoring **8 or higher** are passed to the full analysis stage.


## Article Analysis

For articles that pass Gemini screening, AI Pulse:

- Extracts the main article content from the webpage
- Sends the content to Gemini for detailed analysis
- Identifies the primary technology and key concepts
- Generates a structured summary
- Explains why the article matters for an AI engineer
- Suggests topics worth learning
- Assigns a final relevance score and recommendation


## Ranking

After full analysis, AI Pulse ranks articles from highest to lowest based on their final relevance score.

This helps prioritize the articles with the highest technical learning value.


## Recommendations

AI Pulse assigns a recommendation based on the final relevance score:

| Score | Recommendation |
|---|---|
| 9–10 | NOW |
| 7–8 | LATER |
| 1–6 | SKIP |



## Email Update

The final results are formatted into a plain-text email containing:

- Article title
- Relevance score
- Recommendation
- Original article URL
- Summary
- What to learn
- Why it matters

The email is sent using Resend.


## API Optimization

AI Pulse reduces unnecessary Gemini API usage by:

- Filtering articles locally before using Gemini
- Screening multiple articles in a single Gemini request
- Sending only articles that pass screening for full analysis
- Limiting article content sent for analysis to 8,000 characters
- Limiting Gemini analysis output to 1,500 tokens


## Error Handling

AI Pulse is designed to keep individual failures from stopping the entire pipeline.

- If an RSS source fails, the remaining sources continue.
- If article content cannot be extracted, that article is skipped.
- Invalid or empty Gemini responses are detected and handled safely.
- Gemini quota errors stop further API requests safely.
- Gemini screening results are validated before articles are passed to full analysis.

## Project Structure

```text
AI-Pulse/
├── data/
├── src/
│   ├── analyzer/
│   │   ├── gemini_analyzer.py
│   │   └── gemini_screen.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── rss_collector.py
│   │   └── article_extractor.py
│   ├── filters/
│   │   ├── recency_filter.py
│   │   ├── relevance_filter.py
│   │   └── deduplication_filter.py
│   ├── ranking/
│   │   └── rank_articles.py
│   ├── email_builder.py
│   ├── email_sender.py
│   └── main.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Technologies Used

- Python
- Google Gemini API
- Feedparser
- Trafilatura
- Requests
- Resend
- python-dotenv

## Setup

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Gowthami-28/AI-Pulse.git
cd AI-Pulse

python -m venv .venv

```

## Environment Variables

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
RESEND_API_KEY=your_resend_api_key

Keep your API keys private and do not commit `.env` to GitHub.
```

## Running the Project

Run the complete AI Pulse pipeline from the project root:

```bash
python -m src.main
```

The pipeline collects articles, filters and screens them, performs full analysis, ranks the results, builds the email, and sends the daily AI/ML learning update.


## Current Status

- Core AI Pulse pipeline completed
- Multi-source RSS collection implemented
- Recency, deduplication, and relevance filtering implemented
- Gemini screening and full article analysis implemented
- Article ranking implemented
- Email delivery through Resend implemented
- Local end-to-end pipeline tested successfully
- Docker and Azure deployment planned next

## Future Improvements

- Dockerize the application
- Deploy the scheduled pipeline using Azure Container Apps Jobs
- Add further monitoring and reliability improvements

