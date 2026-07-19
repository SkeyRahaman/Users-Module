import axios from 'axios';
import { API_BASE_URL, SESSION_KEYS, AUTH_CHANNEL } from '../utils/constants.js';

// ─── Safe Storage ────────────────────────────────────────────────────────────
// Brave (and some strict privacy browsers) block sessionStorage silently.
// This wrapper falls back to an in-memory store so the session works for the
// tab lifetime even when the native API is unavailable.
const _memoryStore = new Map();

export const safeStorage = {
  getItem(key) {
    try {
      const val = sessionStorage.getItem(key);
      // sessionStorage may return null even after setItem in Brave strict mode
      // so also check memory as secondary source
      return val ?? _memoryStore.get(key) ?? null;
    } catch {
      return _memoryStore.get(key) ?? null;
    }
  },
  setItem(key, value) {
    try {
      sessionStorage.setItem(key, value);
    } catch { /* blocked */ }
    _memoryStore.set(key, value);
  },
  removeItem(key) {
    try {
      sessionStorage.removeItem(key);
    } catch { /* blocked */ }
    _memoryStore.delete(key);
  },
};

// Create the Axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Track if a token refresh is in progress (prevents multiple refresh calls)
let isRefreshing = false;
let refreshSubscribers = [];

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb) {
  refreshSubscribers.push(cb);
}

// ---- REQUEST INTERCEPTOR: Inject access token ----
apiClient.interceptors.request.use(
  (config) => {
    const token = safeStorage.getItem(SESSION_KEYS.ACCESS_TOKEN);
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---- RESPONSE INTERCEPTOR: Handle 401 with token refresh ----
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip 401 handling for the login/token endpoint itself — prevents
    // the interceptor from firing during the initial login call and
    // causing a redirect loop (especially in Brave).
    const isAuthEndpoint =
      originalRequest?.url?.includes('/auth/token') ||
      originalRequest?.url?.includes('/auth/logout');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      const refreshToken = safeStorage.getItem(SESSION_KEYS.REFRESH_TOKEN);

      // No refresh token — force logout
      if (!refreshToken) {
        handleLogout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue the request until refresh is done
        return new Promise((resolve, reject) => {
          addRefreshSubscriber((newToken) => {
            if (newToken) {
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
              resolve(apiClient(originalRequest));
            } else {
              reject(error);
            }
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const params = new URLSearchParams();
        params.append('refresh_token', refreshToken);

        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh`, params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const { access_token, refresh_token: newRefreshToken } = response.data;

        safeStorage.setItem(SESSION_KEYS.ACCESS_TOKEN, access_token);
        if (newRefreshToken) {
          safeStorage.setItem(SESSION_KEYS.REFRESH_TOKEN, newRefreshToken);
        }

        // Notify subscribers & retry queued requests
        onRefreshed(access_token);
        isRefreshing = false;

        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        onRefreshed(null);
        handleLogout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Clear storage and broadcast logout to other tabs.
 * Guards against redirecting if already on /login (prevents loops in Brave).
 */
function handleLogout() {
  safeStorage.removeItem(SESSION_KEYS.ACCESS_TOKEN);
  safeStorage.removeItem(SESSION_KEYS.REFRESH_TOKEN);
  safeStorage.removeItem(SESSION_KEYS.USER);
  try {
    const channel = new BroadcastChannel(AUTH_CHANNEL);
    channel.postMessage({ type: 'LOGOUT' });
    channel.close();
  } catch { /* BroadcastChannel not supported (Brave strict mode) */ }

  // Only redirect if not already on the login page — prevents infinite loops
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login';
  }
}

export { handleLogout };
export default apiClient;
