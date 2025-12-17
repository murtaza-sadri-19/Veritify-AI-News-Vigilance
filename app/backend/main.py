import os
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from services.utils import make_json_safe

from services import FactCheckService

# Load environment variables from .env
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("VeritifyAPI")


@dataclass
class RequestContext:
    """
    Per-request context used across the pipeline.
    Holds all intermediate computations for transparency and reuse.
    """
    claim_text: str
    claim_type: str = "FACTUAL"  # FACTUAL | OPINION | PREDICTIVE
    lexical_scores: Optional[List[float]] = None
    semantic_scores: Optional[List[float]] = None
    semantic_threshold: Optional[float] = None
    candidate_indices: Optional[List[int]] = None

    # Entailment
    entailment_labels: Optional[List[str]] = None  # ENTAILMENT / CONTRADICTION / NEUTRAL
    entailment_confidences: Optional[List[float]] = None
    entailment_threshold: Optional[float] = None

    # Aggregated verdict
    verdict: Optional[str] = None  # TRUE / FALSE / PARTIALLY FALSE / INSUFFICIENT
    confidence: Optional[float] = None

    # Dynamic thresholds, distributions, debug info
    thresholds: Dict[str, Any] = field(default_factory=dict)
    distributions: Dict[str, Any] = field(default_factory=dict)
    debug: Dict[str, Any] = field(default_factory=dict)


# ── Flask App Setup ───────────────────────────────────────────────

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static",
    template_folder="templates",
)
CORS(app)  # Enable CORS for all routes

# Instantiate core service ONCE; heavy models are loaded inside services/scorer/etc.
fact_check_service = FactCheckService()


# ── API Routes ────────────────────────────────────────────────

@app.route("/api/verify", methods=["POST"])
def verify_claim():
    """
    Main API endpoint for fact verification.
    Creates a RequestContext and passes it through the pipeline.
    """
    try:
        data = request.get_json(silent=True)
        if not data or "claim" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'claim' field in request",
            }), 400

        claim = (data["claim"] or "").strip()
        if not claim:
            return jsonify({
                "success": False,
                "error": "Claim cannot be empty",
            }), 400

        logger.info("Received claim verification request")

        # Initialize per-request context
        context = RequestContext(claim_text=claim)

        # The FactCheckService must accept and populate this context
        result = fact_check_service.check_claim(claim, context)

        # Make sure context debug is included if caller wants transparency
        response_payload = {
            "success": True,
            "result": result,
            "context": {
                "claim_type": context.claim_type,
                "thresholds": context.thresholds,
                "distributions": context.distributions,
                "debug": context.debug,
            },
        }
        
        response_payload = make_json_safe(response_payload)
        return jsonify(response_payload), 200

    except Exception:
        logger.exception("Unhandled error in /api/verify")
        return jsonify({
            "success": False,
            "error": "Internal server error occurred",
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Veritify Fact-Check API",
        "version": "2.0.0",
    }), 200


@app.route("/")
def root():
    """Serve the main HTML interface."""
    return render_template("index.html")


@app.route("/about")
def about():
    """Serve the about page."""
    return render_template("about.html")


@app.route("/demo")
def demo():
    """Serve the dashboard demo page."""
    return render_template("dashboard_demo.html")


# ── App Entry Point ───────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    env = os.getenv("FLASK_ENV", "development")
    debug_mode = env != "production"

    logger.info(
        f"Starting Veritify API | env={env} | port={port} | debug={debug_mode}"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode,
    )