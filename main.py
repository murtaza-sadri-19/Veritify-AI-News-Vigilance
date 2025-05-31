import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class ClaimRequest(BaseModel):
    claim: str

@app.post("/api/verify")
async def verify_claim(request: ClaimRequest):
    claim = request.claim.strip()
    truncated_claim = claim[:99]

    newsdata_api_key = os.getenv("NEWSDATA_API_KEY")
    if not newsdata_api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    newsdata_url = "https://newsdata.io/api/1/latest"
    params = {
        "apikey": newsdata_api_key,
        "q": truncated_claim,
        "language": "en"
    }

    try:
        newsdata_response = requests.get(newsdata_url, params=params, timeout=10)
        newsdata_response.raise_for_status()
        newsdata_json = newsdata_response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")

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

@app.get("/")
async def root():
    return {"message": "News verification API is running"}
