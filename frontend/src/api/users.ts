import { apiClient, tokenStorage } from '@/lib/apiClient';
import type { ChangePasswordPayload, ProfileUpdatePayload, User } from '@/types/models';

export async function getMe() {
  const { data } = await apiClient.get<User>('/users/me/');
  return data;
}

// UserMeView.patch() -> RegisterUserSerializer(partial=True). ProfileUpdatePayload больше
// не содержит password/re_password — этот путь никогда не должен менять пароль (см.
// changePassword ниже для единственного безопасного способа).
export async function updateMe(payload: ProfileUpdatePayload) {
  const hasAvatarFile = payload.avatar instanceof File;

  if (hasAvatarFile) {
    const form = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      if (value === undefined) return;
      if (value === null) {
        form.append(key, '');
        return;
      }
      form.append(key, value as string | Blob);
    });
    const { data } = await apiClient.patch<User>('/users/me/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  // avatar не трогаем -> убираем поле, чтобы не затереть текущую аватарку null'ом
  const { avatar, ...rest } = payload;
  void avatar;
  const { data } = await apiClient.patch<User>('/users/me/', rest);
  return data;
}

export interface ChangePasswordResponse {
  msg: string;
  tokens: { access: string; refresh: string };
}

// UserMeView.post() -> ChangePasswordSerializer: единственный безопасный путь смены пароля —
// требует текущий пароль (old_password) и текущий refresh (который сервер блэклистит и
// заменяет новой парой). Токены нужно сразу перезаписать в хранилище, иначе следующий
// запрос улетит со старым (уже отозванным) access и точно так же не пройдёт по refresh.
export async function changePassword(payload: ChangePasswordPayload) {
  const { data } = await apiClient.post<ChangePasswordResponse>('/users/me/', payload);
  tokenStorage.setTokens(data.tokens.access, data.tokens.refresh);
  return data;
}

// UserBecomeLandlordView больше не выдаёт новые токены: группы не входят в JWT claims, права
// проверяются по БД на каждый запрос, поэтому смена роли действует мгновенно и без релогина.
// Внимание: одновременно пользователь удаляется из группы Tenant — бронировать жильё он больше
// не сможет (осознанное бизнес-правило), фронт предупреждает об этом перед подтверждением.
export interface BecomeLandlordResponse {
  msg?: string;
  detail?: string;
}

export async function becomeLandlord() {
  const { data } = await apiClient.post<BecomeLandlordResponse>('/users/me/become-landlord/');
  return data;
}

// UserMeView.delete() — мягкое удаление (is_active=False, deleted_at проставляется),
// аккаунт не восстановить самостоятельно через UI, только по данным auth-эндпоинт перестанет
// принимать эти учётные данные после выхода.
export async function deleteMe() {
  const { data } = await apiClient.delete<{ msg: string }>('/users/me/');
  return data;
}
