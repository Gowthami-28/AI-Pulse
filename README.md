# AI Pulse

AI Pulse is a personal AI/ML assistant designed to help me keep up with relevant developments in artificial intelligence and machine learning.

The current version collects articles from the official Google AI Blog RSS feed, filters them for relevance, analyzes them using Google Gemini, ranks them based on relevance, and sends the results to my email.

> 🚧 **Status: In Development**
>
> AI Pulse currently uses one article source: the Google AI Blog RSS feed.
> Multiple sources, freshness filtering, deduplication, automation, Docker, and Azure deployment are planned.

## Features

- Collects articles from the Google AI Blog RSS feed
- Filters articles based on AI/ML relevance
- Extracts article content
- Analyzes articles using Google Gemini
- Generates summaries and learning recommendations
- Assigns relevance scores
- Ranks articles by relevance
- Builds a personalized email update
- Sends the update using Resend
- Includes links to the original articles

## Pipeline

```text
Google AI Blog RSS
        ↓
Article Collection
        ↓
Relevance Filtering
        ↓
Article Extraction
        ↓
Gemini Analysis
        ↓
Relevance Ranking
        ↓
Email Builder
        ↓
Resend
        ↓
Personal Email Update

```

## Project Structure

```text

AI-Pulse/
│
├── src/
│   ├── main.py
│   ├── article_extractor.py
│   ├── gemini_analyzer.py
│   ├── relevance_filter.py
│   ├── rank_articles.py
│   ├── email_builder.py
│   ├── email_sender.py
│   │
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── rss_collector.py
│   │
│   └── test_extractor.py
│
├── data/
├── .gitignore
├── requirements.txt
└── README.md

```

## Setup

1. Create a virtual environment

```text

   python -m venv .venv
```

2. Activate the virtual environment
   ```text 

   .\.venv\Scripts\Activate.ps1

   ```

4. Install dependencies

```text
   python -m pip install -r requirements.txt
```

5. Configure environment variables

   Create a .env file:
```text

   GEMINI_API_KEY=your_gemini_api_key
   RESEND_API_KEY=your_resend_api_key
```

7. Run AI Pulse
```text

   python src/main.py
```

## Current Limitations  

```text
 
-Currently uses only the Google AI Blog RSS feed.
-Does not yet have strict freshness filtering.
-Does not yet track previously processed articles.
-Currently runs manually.
-Email formatting is currently plain text.
-Not yet deployed to the cloud.

```

## Planned Improvements

```text

-Add multiple trusted AI/ML sources.
-Add freshness and date filtering.
-Add duplicate detection.
-Add persistent article history.
-Improve error handling and retry mechanisms.
-Add daily automated execution.
-Dockerize the application.
-Deploy to Azure.
-Add logging and monitoring.

```

## Goal

```text

The long-term goal of AI Pulse is to become a personal AI/ML assistant that automatically discovers important AI developments, analyzes them, determines what is worth my attention, and helps me keep learning without having to manually search through AI news every day.
```
