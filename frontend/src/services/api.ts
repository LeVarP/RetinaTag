/**
 * API client for OCT B-Scan Labeler backend.
 * Provides typed methods for all REST endpoints.
 */

import axios, { AxiosInstance } from 'axios';
import type {
  Scan, ScanStats, BScan, BScanLabelUpdate, GlobalStats,
  AuthStatus, LoginCredentials, RegisterCredentials, PasswordChangeRequest,
  User, UserSettings, UserSettingsUpdate,
} from '@/types';

/**
 * Base API URL.
 * In development, Vite proxy forwards /api to backend.
 * In production, adjust as needed.
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/**
 * Axios instance with default configuration.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  withCredentials: true, // Send httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept 401 responses to signal auth expiry
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);

/**
 * API client with all endpoints.
 */
export const api = {
  /**
   * List all scans with embedded statistics.
   */
  getScans: async (): Promise<Scan[]> => {
    const response = await apiClient.get<Scan[]>('/scans');
    return response.data;
  },

  /**
   * Get statistics for a specific scan.
   */
  getScanStats: async (scanId: string): Promise<ScanStats> => {
    const response = await apiClient.get<ScanStats>(`/scans/${scanId}/stats`);
    return response.data;
  },

  /**
   * Get a B-scan by scan ID and index.
   */
  getBScan: async (scanId: string, bscanIndex: number): Promise<BScan> => {
    const response = await apiClient.get<BScan>(
      `/scans/${scanId}/bscans/${bscanIndex}`
    );
    return response.data;
  },

  /**
   * Get the preview image URL for a B-scan.
   * Returns the full URL that can be used in <img> src.
   */
  getPreviewUrl: (scanId: string, bscanIndex: number): string => {
    return `${API_BASE_URL}/scans/${scanId}/bscans/${bscanIndex}/preview`;
  },

  /**
   * Update the label of a B-scan.
   */
  updateLabel: async (
    bscanId: number,
    labelUpdate: BScanLabelUpdate
  ): Promise<BScan> => {
    const response = await apiClient.post<BScan>(
      `/bscans/${bscanId}/label`,
      labelUpdate
    );
    return response.data;
  },

  /**
   * Clear the label of a B-scan (set to unlabeled).
   */
  clearLabel: async (bscanId: number): Promise<BScan> => {
    const response = await apiClient.delete<BScan>(`/bscans/${bscanId}/label`);
    return response.data;
  },

  /**
   * Get a B-scan by its database ID.
   */
  getBScanById: async (bscanId: number): Promise<BScan> => {
    const response = await apiClient.get<BScan>(`/bscans/${bscanId}`);
    return response.data;
  },

  /**
   * Get global statistics across all scans.
   */
  getGlobalStats: async (): Promise<GlobalStats> => {
    const response = await apiClient.get<GlobalStats>('/stats');
    return response.data;
  },

  /**
   * Get summary of all scans.
   */
  getScansSummary: async (): Promise<any> => {
    const response = await apiClient.get('/stats/summary');
    return response.data;
  },

  // ===== AUTH =====

  login: async (credentials: LoginCredentials): Promise<User> => {
    const response = await apiClient.post<User>('/auth/login', credentials);
    return response.data;
  },

  register: async (credentials: RegisterCredentials): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getAuthStatus: async (): Promise<AuthStatus> => {
    const response = await apiClient.get<AuthStatus>('/auth/me');
    return response.data;
  },

  // ===== USER SETTINGS =====

  getMySettings: async (): Promise<UserSettings> => {
    const response = await apiClient.get<UserSettings>('/users/me/settings');
    return response.data;
  },

  updateMySettings: async (updates: UserSettingsUpdate): Promise<UserSettings> => {
    const response = await apiClient.put<UserSettings>('/users/me/settings', updates);
    return response.data;
  },

  changePassword: async (data: PasswordChangeRequest): Promise<void> => {
    await apiClient.post('/users/me/password', data);
  },
};

/**
 * Export axios instance for custom requests if needed.
 */
export { apiClient };
