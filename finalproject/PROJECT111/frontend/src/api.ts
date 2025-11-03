// src/api.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
});

// Request: add access token
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response: refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest: any = error.config;

    if (error?.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refreshToken");
      if (refreshToken) {
        try {
          const resp = await axios.post("http://127.0.0.1:8000/api/token/refresh/", {
            refresh: refreshToken,
          });

          const newAccessToken = resp.data.access;
          localStorage.setItem("accessToken", newAccessToken);

          apiClient.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
          originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;

          return apiClient(originalRequest);
        } catch (e) {
          // refresh 실패 → 토큰 제거 후 로그인 페이지
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");
          delete apiClient.defaults.headers.common["Authorization"];
          window.location.href = "/login";
          return Promise.reject(e);
        }
      }
    }
    return Promise.reject(error);
  }
);

// ✅ 기본 내보내기 (이게 없어서 계속 난 에러)
export default apiClient;


// ======= 아래는 필요한 API 함수들 (선택) =======

interface PaginatedProjectsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: any[];
}

export const getMatchedProjects = async (): Promise<any[]> => {
  const response = await apiClient.get<PaginatedProjectsResponse>("/projects/matched/");
  return response.data.results;
};

export const getProject = async (projectId: string): Promise<any> => {
  const response = await apiClient.get<any>(`/projects/${projectId}/`);
  return response.data;
};

export const updateProject = async (projectId: string, data: any): Promise<any> => {
  const response = await apiClient.patch(`/projects/${projectId}/`, data);
  return response.data;
};

// 프로젝트별 지원자 조회
export const getApplicantsByProject = async (projectId: number) => {
  const response = await apiClient.get(`/projects/${projectId}/applicants/`);
  return response.data;
};

// ✅ 내 프로젝트 조회 API
export const getMyProjects = async () => {
  try {
    const response = await apiClient.get("/projects/my/");
    return response.data;
  } catch (error) {
    console.error("❌ 프로젝트 목록을 불러오는 중 오류 발생:", error);
    throw error;
  }
};

// ✅ AI 추천 프로젝트 조회 API (추가)
export const getRecommendedProjects = async () => {
  try {
    const response = await apiClient.get("/projects/recommended/");
    return response.data;
  } catch (error) {
    console.error("❌ 추천 프로젝트 목록을 불러오는 중 오류 발생:", error);
    throw error;
  }
};

// ✅ AI 추천 팀원 조회 API (추가)
export const getRecommendedTeammates = async (projectId: number) => {
  try {
    const response = await apiClient.get(`/projects/${projectId}/recommend-teammates/`);
    return response.data;
  } catch (error) {
    console.error(`❌ 추천 팀원 목록을 불러오는 중 오류 발생 (Project ID: ${projectId}):`, error);
    throw error;
  }
};

// ✅ 프로젝트 참여 제안 API (추가)
export const proposeToProject = async (projectId: number, userId: number) => {
  try {
    const response = await apiClient.post(`/projects/${projectId}/propose/`, { user_id: userId });
    return response.data;
  } catch (error) {
    console.error(`❌ 프로젝트 참여 제안 중 오류 발생 (Project ID: ${projectId}, User ID: ${userId}):`, error);
    throw error;
  }
};

// ✅ 알림 목록 조회 API (추가)
export const getNotifications = async () => {
  try {
    const response = await apiClient.get('/notifications/');
    return response.data;
  } catch (error) {
    console.error('❌ 알림 목록을 불러오는 중 오류 발생:', error);
    throw error;
  }
};

// ✅ 알림 읽음 처리 API (추가)
export const markNotificationAsRead = async (notificationId: number) => {
  try {
    const response = await apiClient.post(`/notifications/${notificationId}/read/`);
    return response.data;
  } catch (error) {
    console.error(`❌ 알림을 읽음 처리하는 중 오류 발생 (Notification ID: ${notificationId}):`, error);
    throw error;
  }
};

// ✅ 지원자 상태 변경 API (추가)
export const updateApplicantStatus = async (applicantId: number, status: string) => {
  try {
    const response = await apiClient.patch(`/project-applicants/${applicantId}/status/`, { status });
    return response.data;
  } catch (error) {
    console.error(`❌ 지원자 상태 변경 중 오류 발생 (Applicant ID: ${applicantId}):`, error);
    throw error;
  }
};

// ✅ 프로젝트 삭제 API (추가)
export const deleteProject = async (projectId: number) => {
  try {
    const response = await apiClient.delete(`/projects/${projectId}/`);
    return response.data;
  } catch (error) {
    console.error(`❌ 프로젝트 삭제 중 오류 발생 (Project ID: ${projectId}):`, error);
    throw error;
  }
};