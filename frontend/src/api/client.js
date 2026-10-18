import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Overview & Multi-Layer Status
export const getOverviewStatus = () => apiClient.get('/overview/status');
export const getIncidentSummary = () => apiClient.get('/incidents/summary');
export const summarizeCustomIncidents = (incidents) => apiClient.post('/incidents/summarize', { incidents });

// Layer 1: PostgreSQL Wire Protocol DPI & Queries
export const getActivity = (limit = 50) => apiClient.get(`/activity?limit=${limit}`);
export const getAlerts = (limit = 50) => apiClient.get(`/alerts?limit=${limit}`);
export const sendTestQuery = (query, user = "showroom_kiosk") => apiClient.post('/query', { query, user });
export const getSettings = () => apiClient.get('/settings');
export const updateSettings = (settings) => apiClient.put('/settings', settings);

// Layer 2: Panasonic Showroom Hardware Health Telemetry
export const getShowroomFleet = () => apiClient.get('/health/showroom/fleet');
export const getShowroomDisplay = (displayId) => apiClient.get(`/health/showroom/display/${displayId}`);
export const injectShowroomFault = (displayId, faultType, duration = 30) => 
    apiClient.post('/health/showroom/fault', { display_id: displayId, fault_type: faultType, duration_seconds: duration });
export const clearShowroomFault = (displayId) => apiClient.post(`/health/showroom/clear/${displayId}`);
export const clearAllShowroomFaults = () => apiClient.post('/health/showroom/clear-all');
export const getSystemHealth = () => apiClient.get('/health/metrics');

// Layer 3: YOLOv8 CCTV Zone-Intrusion Engine
export const getCCTVFeed = () => apiClient.get('/cctv/feed');
export const getCCTVZones = () => apiClient.get('/cctv/zones');
export const triggerCCTVIntrusion = (zoneId = "ZONE-01-CONCEPT", duration = 10) => 
    apiClient.post('/cctv/trigger', { zone_id: zoneId, duration_seconds: duration });
export const clearCCTVIntrusion = () => apiClient.post('/cctv/clear');
export const CCTV_FRAME_URL = `${API_BASE_URL}/cctv/frame`;

// Layer 4: Real-Time XGBoost Phishing Detector
export const analyzePhishing = (url) => apiClient.post('/phishing/analyze', { url });
export const getRecentPhishingScans = () => apiClient.get('/phishing/recent');