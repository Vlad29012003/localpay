// src/utils/api.ts
import axios from 'axios';
import { BACKEND_API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: BACKEND_API_BASE_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;