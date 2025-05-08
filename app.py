from flask import Flask, render_template, request, jsonify
from services.fact_check_service import FactCheckService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
fact_checker = FactCheckService()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/api/verify', methods=['POST'])
def verify_fact():
    data = request.get_json()

    if not data or 'claim' not in data:
        return jsonify({'success': False, 'error': 'No claim provided'}), 400

    claim = data['claim']

    try:
        # Use our fact checking service
        result = fact_checker.check_claim(claim)

        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.after_request
def apply_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=0) #Automatically assign a available port