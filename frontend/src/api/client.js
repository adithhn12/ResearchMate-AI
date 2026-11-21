import axios from 'axios';

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    let url = import.meta.env.VITE_API_URL.replace(/\/+$/, '');
    if (!url.endsWith('/api/v1')) {
      url += '/api/v1';
    }
    return url;
  }
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Attach Authorization header if token exists
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('researchmate_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect if trying to login or check auth
      if (!error.config.url.includes('/auth/login') && !error.config.url.includes('/auth/register')) {
        localStorage.removeItem('researchmate_token');
        localStorage.removeItem('researchmate_user');
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email, password) => apiClient.post('/auth/login', { email, password }),
  register: (email, password, full_name) => apiClient.post('/auth/register', { email, password, full_name }),
  demoLogin: () => apiClient.post('/auth/demo-login'),
  getMe: () => apiClient.get('/auth/me'),
};

export const projectsApi = {
  list: () => apiClient.get('/projects'),
  create: (name, description) => apiClient.post('/projects', { name, description }),
  get: (id) => apiClient.get(`/projects/${id}`),
  update: (id, data) => apiClient.put(`/projects/${id}`, data),
  delete: (id) => apiClient.delete(`/projects/${id}`),
};

export const papersApi = {
  upload: (projectId, formData) => apiClient.post('/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  listByProject: (projectId, params = {}) => apiClient.get(`/papers/project/${projectId}`, { params }),
  get: (id) => apiClient.get(`/papers/${id}`),
  delete: (id) => apiClient.delete(`/papers/${id}`),
};

export const chatApi = {
  getSessions: (projectId) => apiClient.get(`/chat/sessions/${projectId}`),
  createSession: (projectId, title) => apiClient.post('/chat/sessions', null, { params: { project_id: projectId, title } }),
  getMessages: (sessionId) => apiClient.get(`/chat/sessions/${sessionId}/messages`),
  sendMessage: (content, sessionId, paperIds) => apiClient.post('/chat/message', {
    content,
    session_id: sessionId,
    paper_ids: paperIds && paperIds.length > 0 ? paperIds : null,
  }),
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),
};

export const compareApi = {
  generate: (projectId, paperIds, title) => apiClient.post('/compare/generate', {
    project_id: projectId,
    paper_ids: paperIds,
    title,
  }),
  getHistory: (projectId) => apiClient.get(`/compare/history/${projectId}`),
  get: (id) => apiClient.get(`/compare/${id}`),
  delete: (id) => apiClient.delete(`/compare/${id}`),
};

export const gapsApi = {
  analyze: (projectId, paperIds, title) => apiClient.post('/gaps/analyze', {
    project_id: projectId,
    paper_ids: paperIds,
    title,
  }),
  getHistory: (projectId) => apiClient.get(`/gaps/history/${projectId}`),
  get: (id) => apiClient.get(`/gaps/${id}`),
  delete: (id) => apiClient.delete(`/gaps/${id}`),
};

export const reviewsApi = {
  generate: (projectId, paperIds, title, researchFocus) => apiClient.post('/reviews/generate', {
    project_id: projectId,
    paper_ids: paperIds,
    title,
    research_focus: researchFocus,
  }),
  listByProject: (projectId) => apiClient.get(`/reviews/project/${projectId}`),
  get: (id) => apiClient.get(`/reviews/${id}`),
  update: (id, data) => apiClient.put(`/reviews/${id}`, data),
  delete: (id) => apiClient.delete(`/reviews/${id}`),
  exportDocxUrl: (id) => `${API_BASE_URL}/reviews/${id}/export/docx`,
  exportPdfUrl: (id) => `${API_BASE_URL}/reviews/${id}/export/pdf`,
};

export const analyticsApi = {
  getDashboard: (projectId) => apiClient.get('/analytics/dashboard', {
    params: projectId ? { project_id: projectId } : {},
  }),
};

export default apiClient;
