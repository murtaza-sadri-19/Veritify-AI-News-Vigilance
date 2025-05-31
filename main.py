import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

# Optional: import your own utils if needed
# from .utils import sanitize_text, extract_entities

app = FastAPI()

class ClaimRequest(BaseModel):
    claim: str

@app.post("/api/verify")
async def verify_claim(request: ClaimRequest):
    claim = request.claim.strip()
    # Truncate claim for NewsData.io
    truncated_claim = claim[:99]
    newsdata_api_key = os.getenv("NEWSDATA_API_KEY")
    newsdata_url = "https://newsdata.io/api/1/latest"
    params = {
        "apikey": newsdata_api_key,
        "q": truncated_claim,
        "language": "en"
    }
    newsdata_response = requests.get(newsdata_url, params=params)
    newsdata_json = newsdata_response.json()
    articles = newsdata_json.get("results", [])
    if articles:
        sources = [
            {
                "name": article.get("title", "News Article"),
                "url": article.get("link", ""),
                "date": article.get("pubDate", "")
            }
            for article in articles[:3]
        ]
        return {
            "score": 50,
            "message": "No definitive fact check found, but relevant news articles are available.",
            "sources": sources,
            "claim_text": claim
        }
    else:
        return {
            "score": None,
            "message": "No fact check or relevant news found for this claim.",
            "sources": [],
            "claim_text": claim
        }
