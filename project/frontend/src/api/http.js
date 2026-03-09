import axios from "axios";

const ACCESS_TOKEN_KEY = "tcm_access_token";
const REFRESH_TOKEN_KEY = "tcm_refresh_token";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};
    const status = error.response?.status;

    if (status === 401 && !originalRequest.__retried) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) {
        return Promise.reject(error);
      }

      originalRequest.__retried = true;
      try {
        const refreshResponse = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || ""}/api/auth/refresh/`,
          { refresh: refreshToken },
        );
        const nextAccess = refreshResponse.data?.access;
        const nextRefresh = refreshResponse.data?.refresh;
        if (!nextAccess) {
          return Promise.reject(error);
        }
        localStorage.setItem(ACCESS_TOKEN_KEY, nextAccess);
        if (nextRefresh) {
          localStorage.setItem(REFRESH_TOKEN_KEY, nextRefresh);
        }
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${nextAccess}`;
        return http(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

export function extractErrorMessage(error, fallback = "请求失败，请稍后重试。") {
  const payload = error?.response?.data;
  if (payload?.message) return payload.message;
  if (payload?.detail) return payload.detail;
  if (typeof payload === "string") return payload;
  return fallback;
}

export { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY };
export default http;
