import { Link, useNavigate } from 'react-router-dom';
import { Building2, User as UserIcon, LogOut, LayoutDashboard } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useI18n } from '@/i18n';
import { LanguageSwitcher } from './LanguageSwitcher';

export function Header() {
  const { user, isAuthenticated, isLandlord, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useI18n();

  return (
    <header className="sticky top-0 z-40 bg-brand-900">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2 text-white">
          <Building2 size={24} className="text-white" />
          <span className="hidden text-lg font-bold tracking-tight sm:inline">FindMeApartment</span>
        </Link>

        <nav className="flex items-center gap-2">
          <LanguageSwitcher />
          <span className="mx-1 hidden h-5 w-px bg-white/20 sm:block" aria-hidden="true" />
          {isAuthenticated ? (
            <>
              {isLandlord && (
                <Link
                  to="/dashboard"
                  title={t('header.dashboard')}
                  aria-label={t('header.dashboard')}
                  className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-white/90 hover:bg-white/10"
                >
                  <LayoutDashboard size={16} />
                  <span className="hidden sm:inline">{t('header.dashboard')}</span>
                </Link>
              )}
              <Link
                to="/profile"
                className="flex items-center gap-2 rounded-lg border border-white/25 px-3 py-1.5 text-sm font-medium text-white hover:bg-white/10"
              >
                {user?.avatar ? (
                  <img src={user.avatar} alt="" className="h-6 w-6 rounded-full object-cover" />
                ) : (
                  <UserIcon size={18} />
                )}
                <span className="hidden max-w-[10rem] truncate sm:inline">{user?.first_name || user?.email}</span>
              </Link>
              <button
                onClick={async () => {
                  await logout();
                  navigate('/');
                }}
                className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-medium text-white/80 hover:bg-white/10"
                aria-label={t('header.logout')}
                title={t('header.logout')}
              >
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-lg px-3.5 py-2 text-sm font-semibold text-white hover:bg-white/10"
              >
                {t('header.login')}
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-white px-3.5 py-2 text-sm font-semibold text-brand-700 shadow-sm hover:bg-brand-50"
              >
                {t('header.register')}
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
