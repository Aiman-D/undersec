import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getActivity = (limit = 50) => apiClient.get(`/activity?limit=${limit}`);
export const getAlerts = (limit = 50) => apiClient.get(`/alerts?limit=${limit}`);
export const sendTestQuery = (query, user = "admin") => apiClient.post('/query', { query, user });