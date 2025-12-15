import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS # <--- NEW IMPORT
from dotenv import load_dotenv
from services import FactCheckService

# Load environment variables from .env
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("TruthTrackAPI")

# ── Flask App Setup ───────────────────────────────────────────────
app = Flask(__name__)
CORS(app) # <--- Enable CORS for the React frontend
fact_check_service = FactCheckService()

    # ── API Routes ────────────────────────────────────────────────
    @app.route("/api/verify", methods=["POST", "GET"])
    def verify_claim():
        """
        Main API endpoint for fact verification
        """
        try:
            data = request.get_json(silent=True)

            if not data or "claim" not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing 'claim' field in request"
                }), 400

            claim = data["claim"].strip()
            if not claim:
                return jsonify({
                    "success": False,
                    "error": "Claim cannot be empty"
                }), 400

            logger.info("Received claim verification request")
            result = fact_check_service.check_claim(claim)

            return jsonify({
                "success": True,
                "result": result
            }), 200

        except Exception as e:
            logger.exception("Unhandled error in /api/verify")
            return jsonify({
                "success": False,
                "error": "Internal server error occurred"
            }), 500

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint
        """
        return jsonify({
            "status": "healthy",
            "service": "TruthTrack Fact-Check API",
            "version": "1.0.0"
        }), 200

    return app


# ── App Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    env = os.getenv("FLASK_ENV", "development")
    debug_mode = env != "production"

    app = create_app()

    logger.info(
        f"Starting TruthTrack API | env={env} | port={port} | debug={debug_mode}"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )