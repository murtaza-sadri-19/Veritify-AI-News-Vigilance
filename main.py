import os
from flask import Flask, request, jsonify, render_template
from pyngrok import ngrok, conf, exception
from dotenv import load_dotenv
from services import FactCheckService

# Load environment variables
load_dotenv()

# ── 1) NGROK CONFIG ──────────────────────────────────────────────────
# Only configure ngrok path if running locally and ngrok is available
if os.getenv("FLASK_ENV") != "production":
    try:
        # Try different common ngrok paths
        ngrok_paths = [
            r"C:\ProgramData\chocolatey\bin\ngrok.exe",  # Windows Chocolatey
            "/usr/local/bin/ngrok",  # macOS Homebrew
            "/usr/bin/ngrok",  # Linux system install
            "ngrok"  # PATH-based
        ]

        for path in ngrok_paths:
            if (path == "ngrok") or os.path.exists(path):
                conf.get_default().ngrok_path = path
                break
    except Exception:
        pass  # Ngrok not available, will skip tunnel creation

# ── 2) FLASK APP ─────────────────────────────────────────────────────
app = Flask(__name__)
fact_check_service = FactCheckService()


@app.route("/api/verify", methods=["POST"])
def verify_claim():
    """Main API endpoint for fact verification"""
    try:
        data = request.get_json()
        if not data or "claim" not in data:
            return jsonify({"error": "Missing 'claim' field in request"}), 400

        claim = data["claim"].strip()
        if not claim:
            return jsonify({"error": "Claim cannot be empty"}), 400

        # Use the fact check service
        result = fact_check_service.check_claim(claim)

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        app.logger.error(f"Error in verify_claim: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error occurred"
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TruthTrack Fact-Check API",
        "version": "1.0.0"
    })


@app.route("/")
def root():
    """Serve the main HTML interface"""
    return render_template("index.html")


@app.route("/about")
def about():
    """Serve the about page"""
    return render_template("about.html")


# ── 3) NGROK TUNNEL FUNCTION ────────────────────────────────────────
def start_ngrok(port: int = 5000) -> None:
    """Open an ngrok tunnel and print the public URL (local dev only)"""
    if os.getenv("FLASK_ENV") == "production":
        return  # Skip ngrok in production

    try:
        # Set ngrok auth token if provided
        auth_token = os.getenv("NGROK_AUTHTOKEN")
        if auth_token:
            ngrok.set_auth_token(auth_token)

        tunnel = ngrok.connect(port, "http")
        print(f"\n★ Public URL: {tunnel.public_url}\n")
        os.environ["PUBLIC_URL"] = tunnel.public_url

    except exception.PyngrokNgrokError as e:
        if "ERR_NGROK_108" in str(e):
            print("\n[ERROR] Your ngrok account is limited to 1 simultaneous session.")
            print("Go to https://dashboard.ngrok.com/agents to close existing sessions.")
        else:
            print(f"[WARNING] Ngrok failed: {e}")
    except Exception as e:
        print(f"[WARNING] Could not start ngrok: {e}")


# ── 4) MAIN ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))

    # Start ngrok tunnel for local development
    if os.getenv("FLASK_ENV") != "production":
        start_ngrok(port)

    try:
        debug_mode = os.getenv("FLASK_ENV") != "production"
        app.run(host="0.0.0.0", port=port, debug=debug_mode)
    except KeyboardInterrupt:
        print("Shutting down...")
        if os.getenv("FLASK_ENV") != "production":
            ngrok.kill()