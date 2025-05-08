# TruthTrack AI News Vigilance

TruthTrack AI News Vigilance is a web application designed to combat misinformation by allowing users to verify claims against reputable fact-checking sources. The platform provides trustworthiness scores and links to original fact-check sources to help users make informed judgments about the information they encounter.

![TruthTrack Logo](static/img/logo.png)

## Features

- Verify claims against multiple fact-checking sources
- Get trustworthiness scores on a 0-100 scale
- View detailed assessment with source information
- Clean, responsive user interface
- Real-time claim processing
- Fallback mechanisms when no fact-checks are found

## Technologies Used

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: RapidAPI (Fact-Checker, Google News, Media Bias, Real-Time News)
- **Database**: MongoDB (configured but optional)
- **Environment**: python-dotenv for configuration

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (optional, for persistence)
- RapidAPI subscription with access to fact-checking APIs

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Truthtrack-AI-News-Vigilance.git
cd Truthtrack-AI-News-Vigilance 
```

2. **Create a virtual evironment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

- Copy the example environment file and update it with your API keys:

```bash
cp .env.example .env
nano .env  # Edit with your preferred editor
```

5. **Run the application**

The application will be available at http://localhost:5000 (or another port if configured differently).

## Configuration

- Create a .env file in the project root with the following variables:

```py
# App configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DEBUG=True

# MongoDB configuration (optional)
MONGODB_URI=mongodb://localhost:27017/truthtrack
MONGODB_DB=truthtrack

# API Keys for fact checking services
RAPIDAPI_KEY=your_rapid_api_key_here
NEWS_API_KEY=your_news_api_key_here

# RapidAPI hosts
REAL_TIME_NEWS_HOST=real-time-news-data.p.rapidapi.com
MEDIA_BIAS_HOST=media-bias-fact-check-ratings-api2.p.rapidapi.com
FACT_CHECKER_HOST=fact-checker.p.rapidapi.com
GOOGLE_NEWS_HOST=google-news13.p.rapidapi.com
```
## Usage

### Verifying Claims
1. Navigate to the homepage
2. Enter a claim in the input field
3. Click "Verify Claim"
4. View the results, including:
    - Trustworthiness score
    - Assessment message
    - Source information
    - Example Claims to Test
    
- Try verifying these sample claims:

"Drinking water cures cancer."
"The Earth is flat."
"COVID-19 vaccines contain microchips."
"Exercise is good for heart health."
"The United States presidential election was held in 2020."

## API Documentation

- Endpoints

POST /api/verify

- Verifies a claim using fact-checking services.

Request Body: 
```json
{
  "claim": "The claim text to verify"
}
```

Response: 

```json
{
  "result": {
    "score": 75,
    "message": "This claim appears to be mostly accurate.",
    "sources": [
      {
        "name": "Fact-Check Source Name",
        "url": "https://source-url.com/article",
        "date": "2023-05-15"
      }
    ],
    "claim_text": "The original claim text"
  }
}
```

### Status Codes:

1. 200 OK: Verification completed successfully
2. 400 Bad Request: Missing or invalid claim
3. 500 Internal Server Error: Error during verification process

### Trustworthiness Scoring System

TruthTrack uses a 0-100 scoring system to indicate the trustworthiness of claims:

- 80-100: Claim appears to be mostly true
- 60-79: Claim contains some truth but may have inaccuracies
- 40-59: Claim has mixed truthfulness
- 20-39: Claim appears to be mostly false
- 0-19: Claim is disputed or labeled as false

The scoring is determined by analyzing fact-check results from multiple sources and applying a weighted algorithm that considers the reputation of the source, the specificity of the fact-check, and other factors.

### Error Handling

When fact-checking APIs are unavailable or return no results, the system implements a fallback mechanism:

1. First attempts to use the dedicated fact-checking API
2. If no results, tries Google News search for context
3. If all else fails, provides a contextual assessment based on claim content
4. Always indicates to the user when results are based on fallback mechanisms

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- RapidAPI for providing fact-checking APIs
- All the fact-checking organizations that make their data available