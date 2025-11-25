# Web Scraping with an LLM-driven Agent

A compact example showing how to automate web scraping and structured extraction using an LLM-driven Agent, Pydantic schemas, a small fetch tool (httpx + BeautifulSoup), and Azure OpenAI (via a pydantic_ai wrapper).

## Overview

This repository contains a single runnable script, `web_scrapping.py`, which demonstrates a pattern:
- A `fetch_html_text` tool retrieves page content.
- An Agent (LLM) consumes that content and returns structured JSON matching a Pydantic schema.
- Pydantic validates the output and the script writes results to a CSV.

The goal is to show how agents and typed schemas can simplify extraction from pages with varied HTML structures.

## Requirements

- Python 3.10+
- Packages used in the example:
  - httpx
  - beautifulsoup4
  - pandas
  - pydantic
  - python-dotenv
  - openai (Azure-compatible client)
  - pydantic_ai

Install the main packages (PowerShell example):

```powershell
pip install httpx beautifulsoup4 pandas pydantic python-dotenv openai pydantic-ai
```

## Environment

Create a `.env` file in the project directory with these variables (Azure + model info):

```
OPENAI_ENDPOINT=<your-azure-openai-endpoint>
OPENAI_API_KEY=<your-api-key>
API_VERSION=<api-version>
OPENAI_MODEL=<model-name>
```

## Usage

Run the script (PowerShell):

```powershell
python web_scrapping.py
```

By default the script calls a sample URL defined at the bottom of `web_scrapping.py`. It will save validated results to a timestamped CSV file in the working directory and write a `soup.txt` debug file from the fetched page.

## What the code does (short)

- Initializes an Azure OpenAI client and wraps it in a `pydantic_ai` model.
- Defines Pydantic models:
  - `Product` with `brand_name`, `product_name`, `price`, and `rating_count`.
  - `Results` containing `dataset: list[Product]`.
- Declares an `Agent` with a strict system prompt that instructs the model to return exact JSON matching `Results`.
- Adds a tool `fetch_html_text(url)` that uses `httpx` and `BeautifulSoup` to retrieve and simplify page text.
- Runs the agent, sanitizes the model output (strips markdown fences), parses JSON, validates with Pydantic, and writes a CSV.

## Files

- `web_scrapping.py` — main script and example implementation.

## Limitations & recommended improvements

- fetch_html_text currently returns page text (soup.get_text()) and thus loses HTML structure such as classes and nested tags. Returning raw HTML or specific product-card element HTML improves extraction reliability.
- No robots.txt checking, rate limiting, or politeness delays — add these for ethical scraping.
- Minimal network error handling and backoff; wrap requests with retries and exponential backoff.
- The agent may emit markdown fences or extra text — the script strips common fences but consider stricter prompt constraints and post-validators.
- Add logging, monitoring of token usage, unit tests, and CI for production readiness.

## Ethical & legal

Always respect website terms of service and robots.txt. Do not scrape private or personal data. Use polite crawling intervals, caching, and follow legal/regulatory requirements (GDPR/CCPA where applicable).

## Troubleshooting

- If JSON parsing fails, inspect `soup.txt` and the raw model output; the model may include extra text or markdown fences.
- If network requests fail, verify environment variables and internet connectivity.
- If the model fails, confirm the model name and API version are correct for your Azure/OpenAI account.

## Next steps (suggestions you can implement)

1. Change `fetch_html_text` to return raw HTML or HTML fragments for product cards.
2. Add `robots.txt` checks and a rate-limiting decorator for the tool.
3. Add unit tests for fetching and parsing flows (mock httpx + sample HTML fixtures).
4. Add logging and token-usage monitoring to control costs.

---
