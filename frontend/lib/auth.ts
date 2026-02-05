/**
 * Simple JWT-based authentication utilities
 */

/**
 * Login user and get JWT token from API
 */
export async function loginUser(username: string): Promise<{ token: string; userId: string }> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }

  return response.json();
}

/**
 * Store auth token in both localStorage and cookie
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
    // Also set as cookie for middleware
    document.cookie = `auth_token=${token}; path=/; max-age=86400`; // 24 hours
  }
}

/**
 * Get auth token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
}

/**
 * Remove auth token from localStorage and cookies
 */
export function clearAuthToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    // Remove cookie
    document.cookie = 'auth_token=; path=/; max-age=0';
  }
}

/**
 * Store user ID
 */
export function setUserId(userId: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user_id', userId);
  }
}

/**
 * Get user ID
 */
export function getUserId(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('user_id');
  }
  return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}
