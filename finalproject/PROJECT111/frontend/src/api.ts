import axios from 'axios';

// Create Axios instance
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

// Request interceptor to add the access token to headers
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Any status code that lie within the range of 2xx cause this function to trigger
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Check if the error is 401 and it's not a retry request
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark this request as a retry

      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          // Attempt to refresh the token
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken,
          });

          const newAccessToken = response.data.access;

          // Store the new token
          localStorage.setItem('accessToken', newAccessToken);

          // Update the Authorization header for the original request and the global axios instance
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

          // Retry the original request
          return apiClient(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          // If refresh fails, logout the user
          // This could be done by redirecting or calling a logout function from AuthContext
          // For now, we'll just clear the tokens and headers
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          delete apiClient.defaults.headers.common['Authorization'];
          // Optionally, redirect to login page
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    // For any other errors, just reject the promise
    return Promise.reject(error);
  }
);

export default apiClient;

// Moved Project interface definition to individual components to bypass import issues

interface PaginatedProjectsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: any[]; // Use any[] here as Project is defined elsewhere
}

export const getMatchedProjects = async (): Promise<any[]> => {
  const response = await apiClient.get<PaginatedProjectsResponse>('/projects/matched/');
  return response.data.results;
};

export const getProjectDetail = async (projectId: number): Promise<any> => {
  const response = await apiClient.get<any>(`/projects/${projectId}/`);
  return response.data;
};

export const getRecommendedProjects = async (): Promise<any[]> => {
    const response = await apiClient.get<any[]>('/projects/recommended/');
    return response.data;
};
