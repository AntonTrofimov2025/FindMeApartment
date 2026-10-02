import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { LayoutDashboard } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { ProfileForm } from '@/components/profile/ProfileForm';
import { PasswordForm } from '@/components/profile/PasswordForm';
import { BookingHistory } from '@/components/profile/BookingHistory';
import { DangerZone } from '@/components/profile/DangerZone';
import { BecomeLandlordButton } from '@/components/profile/BecomeLandlordButton';
import { Spinner } from '@/components/ui/Spinner';

type Tab = 'info' | 'bookings' | 'security';

export function ProfilePage() {
  const { user, isLoading, isLandlord } = useAuth();
  const [searchParams] = useSearchParams();
  const initialTab = (searchParams.get('tab') as Tab) ?? 'info';
  const [tab, setTab] = useState<Tab>(initialTab === 'bookings' ? 'bookings' : initialTab);
  const highlightId = searchParams.get('highlight');

  if (isLoading || !user) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner size={36} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Личный кабинет</h1>
          <p className="text-sm text-neutral-500">{user.email}</p>
        </div>
        {isLandlord ? (
          <Link to="/dashboard" className="btn-secondary">
            <LayoutDashboard size={16} className="mr-2" />
            Панель арендодателя
          </Link>
        ) : (
          <BecomeLandlordButton />
        )}
      </div>

      <div className="flex gap-1 border-b border-neutral-200">
        <TabButton active={tab === 'info'} onClick={() => setTab('info')}>
          Личные данные
        </TabButton>
        <TabButton active={tab === 'bookings'} onClick={() => setTab('bookings')}>
          Мои бронирования
        </TabButton>
        <TabButton active={tab === 'security'} onClick={() => setTab('security')}>
          Безопасность
        </TabButton>
      </div>

      {tab === 'info' && <ProfileForm user={user} />}
      {tab === 'bookings' && <BookingHistory highlightId={highlightId} />}
      {tab === 'security' && (
        <div className="space-y-5">
          <PasswordForm />
          <DangerZone />
        </div>
      )}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
        active ? 'border-brand-500 text-brand-600' : 'border-transparent text-neutral-500 hover:text-neutral-800'
      }`}
    >
      {children}
    </button>
  );
}
