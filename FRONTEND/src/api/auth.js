import axios from 'axios';
import apiClient from './client.js';
import { API_BASE_URL } from '../utils/constants.js';

export const authApi = {
  /** POST /auth/token — Login */
  login: async ({ username, password }) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const response = await axios.post(`${API_BASE_URL}/auth/token`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  /** POST /auth/logout — Logout */
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },

  /** POST /auth/token/refresh — Refresh access token */
  refreshToken: async (refreshToken) => {
    const params = new URLSearchParams();
    params.append('refresh_token', refreshToken);
    const response = await axios.post(`${API_BASE_URL}/auth/token/refresh`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  /** POST /auth/password-reset/request */
  requestPasswordReset: async ({ email }) => {
    const response = await axios.post(`${API_BASE_URL}/auth/password-reset/request`, { email });
    return response.data;
  },

  /** POST /auth/password-reset/confirm */
  confirmPasswordReset: async ({ token, new_password }) => {
    const response = await axios.post(`${API_BASE_URL}/auth/password-reset/confirm`, {
      token,
      new_password,
    });
    return response.data;
  },
};
