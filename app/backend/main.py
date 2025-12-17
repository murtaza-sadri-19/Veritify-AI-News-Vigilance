import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS 
from dotenv import load_dotenv
from services import FactCheckService

# Load environment variables from .env
load_dotenv()

# ── Flask App Setup ───────────────────────────────────────────────
# Flask will automatically look for 'templates' and 'static' folders 
# in the same directory as this file (app/backend/)
app = Flask(__name__)
CORS(app) 
fact_check_service = FactCheckService()


# ── UI Routes (These were missing) ────────────────────────────────
@app.route("/")
def index():
    """Render the homepage"""
    return render_template("index.html")

@app.route("/about")
def about():
    """Render the about page"""
    return render_template("about.html")


# ── API Routes ────────────────────────────────────────────────────
@app.route("/api/verify", methods=["POST"])
def verify_claim():
    """Main API endpoint for fact verification"""
    try:
        data = request.get_json()
        if not data or "claim" not in data:
            return jsonify({"error": "Missing 'claim' field"}), 400

        claim = data["claim"].strip()
        if not claim:
            return jsonify({"error": "Claim cannot be empty"}), 400

        result = fact_check_service.check_claim(claim)
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error processing claim: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TruthTrack Fact-Check API",
        "version": "1.0.0"
    })


# ── App Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # It's generally best practice to use 'production' for FLASK_ENV in a deployment setting
    debug_mode = os.getenv("FLASK_ENV") != "production" 
    app.run(host="0.0.0.0", port=port, debug=debug_mode)