/**
 * Axios HTTP client — attaches Telegram initData auth header to every request.
 */
import axios from 'axios';
import { API_BASE_URL } from '@/config/constants';
import { getInitData } from '@/lib/telegram';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach initData header before every request
client.interceptors.request.use((config) => {
  const initData = getInitData();
  if (initData) {
    config.headers['X-Init-Data'] = initData;
  }
  return config;
});

// Normalize error responses
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail =
      error.response?.data?.detail ?? error.message ?? 'An error occurred';
    return Promise.reject(new Error(detail));
  }
);

export default client;
