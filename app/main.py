from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
from typing import Any, Dict
import os

from pdfminer.high_level import extract_text
import openai
import pandas as pd
import json

app = FastAPI()


# Request model
class PDFRequest(BaseModel):
    pdf_base64: str


# Response model
class XLSResponse(BaseModel):
    xls_base64: str


# Helper to call OpenAI API
async def extract_invoice_data(text: str) -> Dict[str, Any]:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    prompt = (
        "You are an assistant that extracts key fields from complex international "
        "trade invoices. Parse the following text and return a JSON object with "
        "structured data. Respond only with the JSON object.\n\n" + text
    )

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",  # using gpt-4 as a placeholder for gpt-4.1-mini
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception as e:
        raise ValueError(
            f"Failed to parse JSON from model response: {content}"
        ) from e
    return data


@app.post("/extract", response_model=XLSResponse)
async def extract(pdf_request: PDFRequest):
    try:
        pdf_bytes = base64.b64decode(pdf_request.pdf_base64)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Invalid base64 data"
        ) from e

    with io.BytesIO(pdf_bytes) as f:
        text = extract_text(f)

    try:
        data = await extract_invoice_data(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    df = pd.DataFrame([data])
    out_buffer = io.BytesIO()
    with pd.ExcelWriter(out_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    xls_base64 = base64.b64encode(out_buffer.getvalue()).decode()
    return {"xls_base64": xls_base64}
