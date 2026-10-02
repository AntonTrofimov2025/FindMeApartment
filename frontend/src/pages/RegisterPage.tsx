import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '@/hooks/useAuth';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';

export function RegisterPage() {
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: '',
    password: '',
    re_password: '',
    first_name: '',
    last_name: '',
    birth_date: '',
    phone: '',
  });
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setIsSubmitting(true);
    try {
      await register({
        email: form.email,
        password: form.password,
        re_password: form.re_password,
        first_name: form.first_name,
        last_name: form.last_name,
        // birth_date опционален (null=True), но если указан — validate_birth_date_age
        // на бэке требует возраст строго 18..120 лет
        birth_date: form.birth_date || null,
        phone: form.phone.trim() === '' ? null : form.phone.trim(),
      });
      await login(form.email, form.password);
      toast.success('Добро пожаловать в FindMeApartment!');
      navigate('/');
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.generalMessage);
      setFieldErrors(parsed.fieldErrors);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-md py-10">
      <div className="card space-y-5 p-8">
        <h1 className="text-xl font-bold">Создать аккаунт</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Имя" value={form.first_name} error={fieldErrors.first_name}
              onChange={(v) => setForm((f) => ({ ...f, first_name: v }))} />
            <Field label="Фамилия" value={form.last_name} error={fieldErrors.last_name}
              onChange={(v) => setForm((f) => ({ ...f, last_name: v }))} />
          </div>
          <Field label="Email" type="email" required value={form.email} error={fieldErrors.email}
            onChange={(v) => setForm((f) => ({ ...f, email: v }))} />
          <Field label="Дата рождения" type="date" value={form.birth_date} error={fieldErrors.birth_date}
            onChange={(v) => setForm((f) => ({ ...f, birth_date: v }))} />
          <div>
            <Field label="Телефон" placeholder="+491701234567" value={form.phone} error={fieldErrors.phone}
              onChange={(v) => setForm((f) => ({ ...f, phone: v }))} />
            <p className="mt-1 text-xs text-neutral-400">Необязательно.</p>
          </div>
          <Field label="Пароль" type="password" required value={form.password} error={fieldErrors.password}
            onChange={(v) => setForm((f) => ({ ...f, password: v }))} />
          <Field label="Повторите пароль" type="password" required value={form.re_password} error={fieldErrors.re_password}
            onChange={(v) => setForm((f) => ({ ...f, re_password: v }))} />

          <ErrorAlert message={error} />

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? 'Создание...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="text-center text-sm text-neutral-500">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="font-semibold text-brand-600">
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  error,
  type = 'text',
  placeholder,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-neutral-500">{label}</label>
      <input
        type={type}
        required={required}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`input ${error ? 'border-red-400' : ''}`}
        minLength={type === 'password' ? 8 : undefined}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
