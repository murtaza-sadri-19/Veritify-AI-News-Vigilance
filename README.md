# TruthTrack - AI-Powered Fact Verification System

A full-stack web application that combines Flask backend with React frontend, featuring Firebase authentication and AI-powered news verification capabilities.

## 🚀 Features

- **Firebase Authentication**: Secure user registration, login, and password reset
- **AI Fact Checking**: Advanced claim verification using multiple news sources
- **Modern React Frontend**: Responsive UI with TailwindCSS styling
- **Real-time News Analysis**: Integration with news APIs for current information
- **Contextual Scoring**: Advanced relevance scoring with semantic analysis
- **Protected API Endpoints**: JWT-based authentication for secure access

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with Firebase Admin SDK
- **Authentication**: Firebase ID token verification
- **APIs**: RESTful endpoints for fact checking
- **Services**: Modular fact-checking and news analysis services

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS for modern, responsive design
- **Authentication**: Firebase Auth SDK integration
- **Routing**: React Router for SPA navigation
- **State Management**: React Context API

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Firebase Project (with Authentication enabled)
- News API Key (RapidAPI)

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Truthtrack-AI-News-Vigilance
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Firebase Configuration (Choose one method)
# Method 1: Service Account Key File Path
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/serviceAccountKey.json

# Method 2: Service Account JSON (for production/Vercel)
FIREBASE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "your-project"}

# News API Configuration
NEWS_API_KEY=your-rapidapi-key-here
NEWS_API_HOST=real-time-news-data.p.rapidapi.com
NEWS_API_LIMIT=50
NEWS_API_COUNTRY=US
NEWS_API_LANG=en
NEWS_RELEVANCE_THRESHOLD=0.25
NEWS_SAMPLE_LIMIT=5

# React App Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abc123
```

### 3. Frontend Setup

#### Install React Dependencies
```bash
cd client
npm install
```

#### Build React App
```bash
npm run build
```

### 4. Firebase Configuration

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication with Email/Password
4. Generate service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

#### Configure Firebase Authentication
1. In Firebase Console, go to Authentication > Settings
2. Add your domain to authorized domains
3. Configure sign-in methods (Email/Password)

## 🚀 Running the Application

### Development Mode

#### Start React Development Server
```bash
cd client
npm start
```
React app will run on `http://localhost:3000`

#### Start Flask Backend
```bash
python main.py
```
Flask app will run on `http://localhost:5000`

### Production Mode

#### Build and Serve with Flask
```bash
# Build React app
cd client
npm run build
cd ..

# Start Flask server (serves React build)
python main.py
```
Application will be available on `http://localhost:5000`

## 📡 API Endpoints

### Authentication Required Endpoints
All API endpoints require Firebase ID token in Authorization header:
```
Authorization: Bearer <firebase-id-token>
```

### Available Endpoints

#### POST `/api/verify`
Verify a claim against news sources
```json
{
  "claim": "The claim to fact-check",
  "api_key": "optional-openai-key"
}
```

#### GET `/api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "service": "TruthTrack Fact-Check API",
  "version": "2.0.0",
  "firebase_enabled": true
}
```

## 🎯 Usage

1. **Register/Login**: Create account or sign in with Firebase Auth
2. **Verify Claims**: Enter claims in the dashboard to fact-check
3. **Review Results**: Get credibility scores and source analysis
4. **API Key**: Optionally provide OpenAI API key for enhanced analysis

## 🔧 Configuration Options

### News API Settings
- `NEWS_API_LIMIT`: Maximum number of articles to fetch (default: 50)
- `NEWS_RELEVANCE_THRESHOLD`: Minimum relevance score (0.0-1.0)
- `NEWS_SAMPLE_LIMIT`: Number of sample articles to log

### Scoring Weights
The system uses weighted scoring:
- Semantic relevance: 65%
- Recency: 25%
- Keywords: 5%
- Named entities: 5%

## 🚀 Deployment

### Vercel Deployment (Recommended)
1. Build React app: `npm run build` in client directory
2. Configure environment variables in Vercel dashboard
3. Deploy Flask app with Vercel
4. Set `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable

### Traditional Hosting
1. Build React app for production
2. Configure reverse proxy (nginx) to serve React and proxy API calls
3. Set up production environment variables
4. Deploy Flask app with gunicorn

## 🛡️ Security

- Firebase ID tokens for authentication
- CORS configuration for cross-origin requests
- Environment variable protection
- Input validation and sanitization

## 📝 Development

### Project Structure
```
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── client/                # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── services/      # Firebase services
│   │   └── config/        # Configuration files
│   └── package.json       # Node.js dependencies
├── services/              # Backend services
│   ├── fact_check_service.py
│   ├── News_trace.py
│   └── utils.py
└── static/                # Legacy static files
```

### Adding New Features
1. Backend: Add routes in `main.py`, implement services in `services/`
2. Frontend: Add components in `client/src/components/`
3. Update authentication as needed for new endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**
   - Verify Firebase configuration in `.env`
   - Check service account key permissions
   - Ensure Authentication is enabled in Firebase Console

2. **CORS Errors**
   - Verify CORS configuration in Flask app
   - Check allowed origins in production

3. **Build Errors**
   - Ensure Node.js and Python versions are compatible
   - Clear npm/pip cache if needed

### Getting Help
- Check the GitHub issues for known problems
- Review Firebase documentation
- Verify API key configurations

---

Built with ❤️ using Flask, React, and Firebase
