import { useState } from 'react';
import toast from 'react-hot-toast';
import type { User } from '@/types/models';
import { updateMe } from '@/api/users';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';
import { useAuth } from '@/hooks/useAuth';

export function ProfileForm({ user }: { user: User }) {
  const { refreshUser } = useAuth();
  const [form, setForm] = useState({
    username: user.username,
    first_name: user.first_name,
    last_name: user.last_name,
    birth_date: user.birth_date ?? '',
    phone: user.phone ?? '',
  });
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(user.avatar);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  function handleAvatarChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null;
    setAvatarFile(file);
    if (file) setAvatarPreview(URL.createObjectURL(file));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setIsSaving(true);
    try {
      // Телефон опционален (null=True на бэке) — пустую строку превращаем в null,
      // иначе провалится regex-валидатор validate_phone.
      await updateMe({
        username: form.username,
        first_name: form.first_name,
        last_name: form.last_name,
        birth_date: form.birth_date || null,
        phone: form.phone.trim() === '' ? null : form.phone.trim(),
        avatar: avatarFile,
      });
      await refreshUser();
      toast.success('Профиль обновлён');
      setAvatarFile(null);
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.generalMessage);
      setFieldErrors(parsed.fieldErrors);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-5 p-6">
      <h2 className="text-lg font-semibold">Личные данные</h2>

      <div className="flex items-center gap-4">
        <div className="h-20 w-20 overflow-hidden rounded-full bg-neutral-100">
          {avatarPreview ? (
            <img src={avatarPreview} alt="" className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-neutral-300">Нет фото</div>
          )}
        </div>
        <div>
          <label className="btn-secondary cursor-pointer !px-3 !py-2 text-sm">
            Загрузить аватар
            <input type="file" accept="image/png,image/jpeg,image/webp,image/heic,image/heif" onChange={handleAvatarChange} className="hidden" />
          </label>
          <p className="mt-1 text-xs text-neutral-400">До 2 МБ, PNG/JPEG/WEBP/HEIC</p>
          {fieldErrors.avatar && <p className="mt-1 text-xs text-red-600">{fieldErrors.avatar}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Имя" value={form.first_name} error={fieldErrors.first_name}
          onChange={(v) => setForm((f) => ({ ...f, first_name: v }))} />
        <Field label="Фамилия" value={form.last_name} error={fieldErrors.last_name}
          onChange={(v) => setForm((f) => ({ ...f, last_name: v }))} />
        <Field label="Имя пользователя" value={form.username} error={fieldErrors.username}
          onChange={(v) => setForm((f) => ({ ...f, username: v }))} />
        <Field label="Дата рождения" type="date" value={form.birth_date} error={fieldErrors.birth_date}
          onChange={(v) => setForm((f) => ({ ...f, birth_date: v }))} />
        <div className="sm:col-span-2">
          <Field
            label="Телефон"
            placeholder="+491701234567"
            value={form.phone}
            error={fieldErrors.phone}
            onChange={(v) => setForm((f) => ({ ...f, phone: v }))}
          />
          <p className="mt-1 text-xs text-neutral-400">Необязательно. Формат: +[код][номер], 10–75 символов.</p>
        </div>
      </div>

      <ErrorAlert message={error} />

      <button type="submit" disabled={isSaving} className="btn-primary">
        {isSaving ? 'Сохранение...' : 'Сохранить изменения'}
      </button>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  error,
  type = 'text',
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  type?: string;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-neutral-500">{label}</label>
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className={`input ${error ? 'border-red-400' : ''}`}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
