import { auth } from './firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Interface for fact-check request
 */
export interface FactCheckRequest {
  claim: string;
  api_key?: string;
}

/**
 * Interface for fact-check result
 */
export interface FactCheckResult {
  success: boolean;
  result?: {
    claim: string;
    credibility_score: number;
    verdict: string;
    summary: string;
    sources: Array<{
      title: string;
      url: string;
      published_date?: string;
      relevance_score?: number;
    }>;
    analysis: {
      strengths: string[];
      weaknesses: string[];
      context: string;
    };
  };
  error?: string;
  user_id?: string;
}

/**
 * Interface for health check response
 */
export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  firebase_enabled: boolean;
}

/**
 * Get the Firebase ID token for authenticated requests
 */
const getAuthToken = async (): Promise<string | null> => {
  const user = auth.currentUser;
  if (!user) {
    throw new Error('User not authenticated');
  }
  return await user.getIdToken();
};

/**
 * Make an authenticated API request
 */
const authenticatedRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = await getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return response;
};

/**
 * Check a claim for factual accuracy
 */
export const verifyClaimAPI = async (
  claim: string,
  apiKey?: string
): Promise<FactCheckResult> => {
  try {
    const response = await authenticatedRequest('/api/verify', {
      method: 'POST',
      body: JSON.stringify({
        claim: claim.trim(),
        api_key: apiKey,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to verify claim');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error verifying claim:', error);
    throw error;
  }
};

/**
 * Check API health status
 */
export const checkHealthAPI = async (): Promise<HealthCheckResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

/**
 * Error handler for API errors
 */
export const handleAPIError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export default {
  verifyClaimAPI,
  checkHealthAPI,
  handleAPIError,
};
