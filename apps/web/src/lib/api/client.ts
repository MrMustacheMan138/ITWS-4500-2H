import { getSession } from 'next-auth/react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = new Headers(options.headers);

  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const session = await getSession();
  const accessToken = session?.accessToken;

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for session management
    });

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (!response.ok) {
      const errorData = isJson ? await response.json() : { message: response.statusText };
      throw new ApiError(
        errorData.message || errorData.detail || 'An error occurred',
        response.status,
        errorData
      );
    }

    // Return parsed JSON or null for empty responses
    if (isJson) {
      return await response.json();
    }

    return null;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network or other errors
    throw new ApiError(
      'Network error. Please check your connection and try again.',
      0
    );
  }
}
