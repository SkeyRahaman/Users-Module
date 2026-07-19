import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth.js';
import { usersApi } from '../api/users.js';
import { safeStorage } from '../api/client.js';
import { SESSION_KEYS, AUTH_CHANNEL } from '../utils/constants.js';

const AuthContext = createContext(null);

const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: true,
  isAuthenticated: false,
};

function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGOUT':
      return { ...initialState, isLoading: false };
    case 'UPDATE_USER':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // On mount: restore session from storage (safeStorage handles Brave blocking)
  useEffect(() => {
    const accessToken = safeStorage.getItem(SESSION_KEYS.ACCESS_TOKEN);
    const refreshToken = safeStorage.getItem(SESSION_KEYS.REFRESH_TOKEN);
    const userStr = safeStorage.getItem(SESSION_KEYS.USER);

    if (accessToken && userStr) {
      try {
        const user = JSON.parse(userStr);
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user, accessToken, refreshToken },
        });
      } catch {
        // Corrupted user JSON — clear and treat as logged out
        safeStorage.removeItem(SESSION_KEYS.ACCESS_TOKEN);
        safeStorage.removeItem(SESSION_KEYS.REFRESH_TOKEN);
        safeStorage.removeItem(SESSION_KEYS.USER);
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  // Listen for logout/login events from other tabs via BroadcastChannel
  useEffect(() => {
    let channel;
    try {
      channel = new BroadcastChannel(AUTH_CHANNEL);
      channel.onmessage = (event) => {
        if (event.data?.type === 'LOGOUT') {
          dispatch({ type: 'LOGOUT' });
        }
        if (event.data?.type === 'LOGIN' && event.data.payload) {
          dispatch({ type: 'LOGIN_SUCCESS', payload: event.data.payload });
        }
      };
    } catch { /* BroadcastChannel not supported (Brave strict mode) */ }
    return () => channel?.close();
  }, []);

  const login = useCallback(async ({ username, password }) => {
    // 1. Get tokens
    const data = await authApi.login({ username, password });

    // 2. Persist tokens BEFORE fetching /users/me so the request interceptor
    //    attaches the Authorization header correctly
    safeStorage.setItem(SESSION_KEYS.ACCESS_TOKEN, data.access_token);
    safeStorage.setItem(SESSION_KEYS.REFRESH_TOKEN, data.refresh_token);

    // 3. Fetch user profile (access token is now in storage)
    const user = await usersApi.getMe();
    safeStorage.setItem(SESSION_KEYS.USER, JSON.stringify(user));

    dispatch({
      type: 'LOGIN_SUCCESS',
      payload: { user, accessToken: data.access_token, refreshToken: data.refresh_token },
    });

    // 4. Broadcast login to other tabs (best-effort)
    try {
      const channel = new BroadcastChannel(AUTH_CHANNEL);
      channel.postMessage({
        type: 'LOGIN',
        payload: { user, accessToken: data.access_token, refreshToken: data.refresh_token },
      });
      channel.close();
    } catch { /* ignore */ }

    return user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch { /* ignore errors during logout */ }
    safeStorage.removeItem(SESSION_KEYS.ACCESS_TOKEN);
    safeStorage.removeItem(SESSION_KEYS.REFRESH_TOKEN);
    safeStorage.removeItem(SESSION_KEYS.USER);
    dispatch({ type: 'LOGOUT' });
    try {
      const channel = new BroadcastChannel(AUTH_CHANNEL);
      channel.postMessage({ type: 'LOGOUT' });
      channel.close();
    } catch { /* ignore */ }
  }, []);

  const register = useCallback(async (userData) => {
    const user = await usersApi.createUser(userData);
    return user;
  }, []);

  const updateUser = useCallback((updatedUser) => {
    safeStorage.setItem(SESSION_KEYS.USER, JSON.stringify(updatedUser));
    dispatch({ type: 'UPDATE_USER', payload: updatedUser });
  }, []);

  const value = {
    ...state,
    login,
    logout,
    register,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
