// Firebase configuration
// Your actual Firebase project credentials
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyB80mdq9WqVKEk6eFzlre8TXRlX7yHJmfY",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "truthtell-b2bc3.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "truthtell-b2bc3",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "truthtell-b2bc3.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "307435455445",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:307435455445:web:9ffae01fce173f901ff35c",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-914VCX9S8T"
};

export default firebaseConfig;
