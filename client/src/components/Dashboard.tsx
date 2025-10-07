import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface FactCheckResult {
  score: number;
  message: string;
  sources: any[];
  claim_text: string;
}

const Dashboard: React.FC = () => {
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState<FactCheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');
  const { currentUser, logout, getIdToken } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Failed to log out:', error);
    }
  };

  const handleFactCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim()) {
      setError('Please enter a claim to verify');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = await getIdToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          claim,
          api_key: apiKey || undefined
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.success) {
        setResult(data.result);
      } else {
        setError(data.error || 'Failed to verify claim');
      }
    } catch (error: any) {
      setError('Failed to verify claim: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    // Backend sends 0-100, normalize to 0-1 for comparison
    const normalizedScore = score > 1 ? score / 100 : score;
    if (normalizedScore >= 0.7) return 'text-green-600';
    if (normalizedScore >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    // Backend sends 0-100, normalize to 0-1 for comparison
    const normalizedScore = score > 1 ? score / 100 : score;
    if (normalizedScore >= 0.7) return 'bg-green-100';
    if (normalizedScore >= 0.4) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                TruthTrack Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {currentUser?.email}
              </span>
              <button
                onClick={handleLogout}
                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Fact Check Claims
              </h2>

              <form onSubmit={handleFactCheck} className="space-y-4">
                <div>
                  <label htmlFor="claim" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Enter claim to verify
                  </label>
                  <textarea
                    id="claim"
                    name="claim"
                    rows={4}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    placeholder="Enter the claim you want to fact-check..."
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    OpenAI API Key (optional - for enhanced analysis)
                  </label>
                  <input
                    type="password"
                    id="apiKey"
                    name="apiKey"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={loading}
                  />
                </div>

                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !claim.trim()}
                  className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
                >
                  {loading ? 'Verifying...' : 'Verify Claim'}
                </button>
              </form>
            </div>
          </div>

          {/* Results */}
          {result && (
            <div className="mt-6 bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Verification Results
                </h3>

                <div className={`p-4 rounded-lg ${getScoreBg(result.score)} mb-4`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Credibility Score
                    </span>
                    <span className={`text-lg font-bold ${getScoreColor(result.score)}`}>
                      {/* Backend sends 0-100, display as-is */}
                      {Math.round(result.score > 1 ? result.score : result.score)}%
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">
                    Analysis
                  </h4>
                  <p className="text-gray-700 dark:text-gray-300">
                    {result.message}
                  </p>
                </div>

                {result.sources && result.sources.length > 0 && (
                  <div>
                    <h4 className="text-md font-medium text-gray-900 dark:text-white mb-2">
                      Sources ({result.sources.length})
                    </h4>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {result.sources.slice(0, 10).map((source: any, index: number) => (
                        <div key={index} className="border-l-4 border-primary-500 pl-4 py-2 bg-gray-50 dark:bg-gray-700">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {source.title}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {source.source} • {source.published_date}
                          </p>
                          {source.relevance_score && (
                            <span className="text-xs text-primary-600">
                              Relevance: {Math.round(source.relevance_score * 100)}%
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
