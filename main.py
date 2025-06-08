import os
import requests
from flask import Flask, request, jsonify, render_template
from pyngrok import ngrok, conf, exception

# ── 1)  NGROK CONFIG ──────────────────────────────────────────────────
conf.get_default().ngrok_path = r"C:\ProgramData\chocolatey\bin\ngrok.exe"
conf.get_default().auth_token = os.getenv("NGROK_AUTHTOKEN")  # Set your authtoken in env var

# ── 2)  FLASK APP ─────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/api/verify", methods=["POST"])
def verify_claim():
    data = request.get_json()
    if not data or "claim" not in data:
        return jsonify({"error": "Missing 'claim' field in request"}), 400

    claim = data["claim"].strip()[:99]
    newsdata_api_key = os.getenv("NEWSDATA_API_KEY")

    if not newsdata_api_key:
        return jsonify({"error": "API key not configured"}), 500

    try:
        r = requests.get(
            "https://newsdata.io/api/1/latest",
            params={"apikey": newsdata_api_key, "q": claim, "language": "en"},
            timeout=10,
        )
        r.raise_for_status()
        articles = r.json().get("results", [])
    except requests.RequestException as e:
        return jsonify({"error": f"External API error: {e}"}), 502

    if articles:
        return jsonify({
            "score": 50,
            "message": "No definitive fact-check found, but relevant news articles are available.",
            "sources": [
                {"name": a.get("title", "News"),
                 "url": a.get("link", ""),
                 "date": a.get("pubDate", "")}
                for a in articles[:3]
            ],
            "claim_text": claim,
        })

    return jsonify({
        "score": None,
        "message": "No fact-check or relevant news found for this claim.",
        "sources": [],
        "claim_text": claim,
    })


@app.route("/")
def root():
    return render_template("index.html")   # Serve your existing template

# ── 3)  NGROK TUNNEL FUNCTION ────────────────────────────────────────
def start_ngrok(port: int = 5000) -> None:
    """Open an ngrok tunnel and print the public URL."""
    try:
        tunnel = ngrok.connect(port, "http")
        print(f"\n★ Public URL: {tunnel.public_url}\n")
        os.environ["PUBLIC_URL"] = tunnel.public_url
    except exception.PyngrokNgrokError as e:
        # Handle ngrok session limit error (ERR_NGROK_108)
        if "ERR_NGROK_108" in str(e):
            print("\n[ERROR] Your ngrok account is limited to 1 simultaneous agent session.")
            print("Go to https://dashboard.ngrok.com/agents to close existing sessions, or upgrade your plan.")
            exit(1)
        else:
            raise

# ── 4)  MAIN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_ngrok(5000)  # Create tunnel
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Running stop")
        ngrok.kill()