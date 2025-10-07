import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
from services import FactCheckService

# Load environment variables from .env
load_dotenv()

# ── Firebase Setup ────────────────────────────────────────────────
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json:
                try:
                    service_account_info = json.loads(service_account_json)
                    cred = credentials.Certificate(service_account_info)
                except json.JSONDecodeError:
                    print("Warning: Invalid Firebase service account JSON")
                    return None
            else:
                print("Warning: Firebase credentials not configured")
                return None
        
        firebase_admin.initialize_app(cred)
    
    return True

# Initialize Firebase
firebase_initialized = initialize_firebase()

# ── Flask App Setup ───────────────────────────────────────────────
app = Flask(__name__, static_folder='client/build/static', template_folder='client/build')
CORS(app, origins=["http://localhost:3000"])

# PERFORMANCE FIX: Initialize FactCheckService once at startup
# This pre-loads the semantic model, making all subsequent requests fast
print("🚀 Initializing Fact Check Service...")
fact_check_service = FactCheckService()
print("✅ Fact Check Service ready - semantic model loaded")

# ── Authentication Middleware ─────────────────────────────────────
def verify_firebase_token(f):
    """Decorator to verify Firebase ID token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_initialized:
            return jsonify({"error": "Firebase not configured"}), 500
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            request.user = decoded_token
            return f(*args, **kwargs)
        except FirebaseError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        except Exception as e:
            return jsonify({"error": "Token verification failed"}), 401
    
    return decorated_function


# ── API Routes ────────────────────────────────────────────────────
@app.route("/api/verify", methods=["POST"])
@verify_firebase_token
def verify_claim():
    """Main API endpoint for fact verification - requires Firebase authentication"""
    try:
        data = request.get_json()
        if not data or "claim" not in data:
            return jsonify({"error": "Missing 'claim' field in request"}), 400

        claim = data["claim"].strip()
        if not claim:
            return jsonify({"error": "Claim cannot be empty"}), 400

        # Process claim
        result = fact_check_service.check_claim(claim)

        return jsonify({
            "success": True,
            "result": result,
            "user_id": request.user.get('uid')
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
        "version": "2.0.0",
        "firebase_enabled": firebase_initialized,
        "model_loaded": True
    })


# ── React Frontend Routes ─────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app for all non-API routes"""
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        try:
            return render_template('index.html')
        except:
            return render_template('index.html', react_mode=False)


@app.route("/about")
def about():
    """Serve the about page"""
    try:
        return render_template('index.html')
    except:
        return render_template("about.html")


# ── App Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") != "production"
    
    print(f"""
    ╔════════════════════════════════════════════╗
    ║   TruthTrack Fact-Check API Server        ║
    ║   Running on port {port}                      ║
    ║   Semantic model: LOADED ✓                ║
    ║   Firebase auth: {'ENABLED ✓' if firebase_initialized else 'DISABLED ✗'}           ║
    ╚════════════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)