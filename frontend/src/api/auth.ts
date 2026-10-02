import { apiClient, tokenStorage } from '@/lib/apiClient';
import type { RegisterPayload, User } from '@/types/models';

export async function login(email: string, password: string) {
  const { data } = await apiClient.post('/auth/login/', { email, password });
  tokenStorage.setTokens(data.access, data.refresh);
  return data as { access: string; refresh: string };
}

export async function register(payload: RegisterPayload) {
  const { data } = await apiClient.post<User>('/auth/register/', payload);
  return data;
}

export async function logout() {
  const refresh = tokenStorage.getRefresh();
  try {
    if (refresh) await apiClient.post('/auth/logout/', { refresh });
  } finally {
    tokenStorage.clear();
  }
}
