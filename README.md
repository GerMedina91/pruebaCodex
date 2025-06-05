# PruebaCodex

This repository provides a FastAPI service that accepts a PDF encoded in base64, extracts invoice data with GPT-4 (representing GPT-4.1 mini), and returns an Excel file encoded in base64. The service demonstrates how to use language models for structured data extraction from complex invoices.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Set the `OPENAI_API_KEY` environment variable before running to enable calls to the OpenAI API.
