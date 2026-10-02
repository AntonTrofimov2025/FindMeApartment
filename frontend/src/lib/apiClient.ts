import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

// Весь бэкенд теперь смонтирован под /api/ (config/urls.py), а nginx.conf отправляет в Django
// только ^/(api|admin)/ — всё остальное уходит в контейнер фронтенда. Поэтому baseURL строго
// заканчивается на /api, а пути в api/*.ts пишутся БЕЗ этого префикса: '/listings/' ->
// итоговый запрос '/api/listings/'. VITE_API_BASE_URL задаётся только если фронт и API живут
// на разных доменах (например, https://api.example.com); по умолчанию — относительный путь.
const apiOrigin = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
const baseURL = `${apiOrigin}/api`;

const ACCESS_KEY = 'fma_access_token';
const REFRESH_KEY = 'fma_refresh_token';

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  setTokens: (access: string, refresh?: string) => {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export const apiClient = axios.create({ baseURL });

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// SIMPLE_JWT: ACCESS_TOKEN_LIFETIME=5m, ROTATE_REFRESH_TOKENS=True, BLACKLIST_AFTER_ROTATION=True.
// Значит при рефреше сервер ротирует и старый refresh моментально попадёт в blacklist —
// новый refresh_token из ответа обязательно нужно сохранить, иначе следующий рефреш 401-нёт.
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) throw new Error('No refresh token available');

  const { data } = await axios.post(`${baseURL}/auth/refresh/`, { refresh });
  tokenStorage.setTokens(data.access, data.refresh);
  return data.access as string;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    const isAuthEndpoint = original?.url?.includes('/auth/');
    if (error.response?.status === 401 && original && !original._retry && !isAuthEndpoint) {
      original._retry = true;
      try {
        refreshPromise = refreshPromise ?? refreshAccessToken();
        const newAccess = await refreshPromise;
        refreshPromise = null;
        original.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(original);
      } catch (refreshError) {
        refreshPromise = null;
        tokenStorage.clear();
        window.location.assign('/login');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);
