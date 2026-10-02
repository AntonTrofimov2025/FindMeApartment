import { useState } from 'react';
import toast from 'react-hot-toast';
import { changePassword } from '@/api/users';
import { tokenStorage } from '@/lib/apiClient';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';

// UserMeView.post() -> ChangePasswordSerializer — единственный безопасный путь смены пароля:
// требует текущий пароль (old_password) и текущий refresh, который сервер тут же блэклистит.
// Обычный PATCH /users/me/ пароль больше не принимает вовсе (см. ProfileUpdatePayload).
export function PasswordForm() {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [reNewPassword, setReNewPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    if (newPassword !== reNewPassword) {
      setFieldErrors({ re_new_password: 'Пароли не совпадают.' });
      return;
    }

    const refresh = tokenStorage.getRefresh();
    if (!refresh) {
      setError('Сессия истекла, пожалуйста, войдите заново.');
      return;
    }

    setIsSaving(true);
    try {
      await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        re_new_password: reNewPassword,
        refresh,
      });
      toast.success('Пароль изменён');
      setOldPassword('');
      setNewPassword('');
      setReNewPassword('');
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.generalMessage);
      setFieldErrors(parsed.fieldErrors);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-6">
      <h2 className="text-lg font-semibold">Смена пароля</h2>

      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Текущий пароль</label>
        <input
          type="password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          autoComplete="current-password"
          className={`input ${fieldErrors.old_password ? 'border-red-400' : ''}`}
        />
        {fieldErrors.old_password && <p className="mt-1 text-xs text-red-600">{fieldErrors.old_password}</p>}
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Новый пароль</label>
        <input
          type="password"
          value={newPassword}
          minLength={8}
          maxLength={128}
          onChange={(e) => setNewPassword(e.target.value)}
          autoComplete="new-password"
          className={`input ${fieldErrors.new_password ? 'border-red-400' : ''}`}
        />
        {fieldErrors.new_password && <p className="mt-1 text-xs text-red-600">{fieldErrors.new_password}</p>}
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Повторите новый пароль</label>
        <input
          type="password"
          value={reNewPassword}
          minLength={8}
          maxLength={128}
          onChange={(e) => setReNewPassword(e.target.value)}
          autoComplete="new-password"
          className={`input ${fieldErrors.re_new_password ? 'border-red-400' : ''}`}
        />
        {fieldErrors.re_new_password && <p className="mt-1 text-xs text-red-600">{fieldErrors.re_new_password}</p>}
      </div>

      <ErrorAlert message={error} />

      <button type="submit" disabled={isSaving || !oldPassword || !newPassword} className="btn-secondary">
        {isSaving ? 'Сохранение...' : 'Изменить пароль'}
      </button>
    </form>
  );
}
