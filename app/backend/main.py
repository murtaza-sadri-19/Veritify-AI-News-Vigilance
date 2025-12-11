import os
from flask import Flask, request, jsonify
from flask_cors import CORS # <--- NEW IMPORT
from dotenv import load_dotenv
from services import FactCheckService

# Load environment variables from .env
load_dotenv()

# ── Flask App Setup ───────────────────────────────────────────────
app = Flask(__name__)
CORS(app) # <--- Enable CORS for the React frontend
fact_check_service = FactCheckService()


# ── API Routes ────────────────────────────────────────────────────
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


# ── App Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # It's generally best practice to use 'production' for FLASK_ENV in a deployment setting
    debug_mode = os.getenv("FLASK_ENV") != "production" 
    app.run(host="0.0.0.0", port=port, debug=debug_mode)