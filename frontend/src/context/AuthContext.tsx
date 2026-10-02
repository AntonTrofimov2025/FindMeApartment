import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { AxiosError } from 'axios';
import * as authApi from '@/api/auth';
import * as usersApi from '@/api/users';
import { fetchLandlordAnalytics } from '@/api/bookings';
import { tokenStorage } from '@/lib/apiClient';
import type { RegisterPayload, User } from '@/types/models';
import type { BecomeLandlordResponse } from '@/api/users';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  /** Реальная роль с бэка (группа Landlord или staff), а не эвристика по числу объявлений. */
  isLandlord: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  becomeLandlord: () => Promise<BecomeLandlordResponse>;
  deleteAccount: () => Promise<{ msg: string }>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// UserListSerializer не отдаёт группы пользователя, поэтому роль проверяем через эндпоинт,
// защищённый IsLandLord: 200 — лендлорд (или staff), 403 — арендатор. Любая другая ошибка
// (сеть, 5xx) трактуется как "не лендлорд", чтобы не показывать дашборд по ошибке — сервер
// в любом случае не пустит арендатора к лендлорд-эндпоинтам.
async function probeLandlordRole(): Promise<boolean> {
  try {
    await fetchLandlordAnalytics();
    return true;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.status === 403) return false;
    return false;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLandlord, setIsLandlord] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const clearLocalSession = useCallback(() => {
    setUser(null);
    setIsLandlord(false);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!tokenStorage.getAccess()) {
      clearLocalSession();
      return;
    }
    try {
      const [me, landlord] = await Promise.all([usersApi.getMe(), probeLandlordRole()]);
      setUser(me);
      setIsLandlord(landlord);
    } catch {
      clearLocalSession();
    }
  }, [clearLocalSession]);

  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false));
  }, [refreshUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      await authApi.login(email, password);
      await refreshUser();
    },
    [refreshUser],
  );

  const register = useCallback(async (payload: RegisterPayload) => {
    await authApi.register(payload);
  }, []);

  const logout = useCallback(async () => {
    await authApi.logout();
    clearLocalSession();
  }, [clearLocalSession]);

  const becomeLandlord = useCallback(async () => {
    // Токены не меняются: группы не хранятся в JWT, права сверяются с БД на каждый запрос.
    const res = await usersApi.becomeLandlord();
    await refreshUser();
    return res;
  }, [refreshUser]);

  const deleteAccount = useCallback(async () => {
    // Soft-delete на бэке: is_active=False + deleted_at, а у лендлорда заодно мягко удаляются
    // все его объявления. JWTAuthentication ищет пользователя через User.objects (без удалённых),
    // так что оставшиеся токены сразу перестают работать — чистим сессию локально.
    const res = await usersApi.deleteMe();
    tokenStorage.clear();
    clearLocalSession();
    return res;
  }, [clearLocalSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      isLandlord,
      login,
      register,
      logout,
      refreshUser,
      becomeLandlord,
      deleteAccount,
    }),
    [user, isLoading, isLandlord, login, register, logout, refreshUser, becomeLandlord, deleteAccount],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
