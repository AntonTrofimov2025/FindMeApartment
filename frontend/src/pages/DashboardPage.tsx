import { useState } from 'react';
import type { ReactNode } from 'react';
import { useI18n } from '@/i18n';
import { useAuth } from '@/hooks/useAuth';
import { AnalyticsPanel } from '@/components/dashboard/AnalyticsPanel';
import { ListingManager } from '@/components/dashboard/ListingManager';
import { BookingManager } from '@/components/dashboard/BookingManager';
import { BecomeLandlordButton } from '@/components/profile/BecomeLandlordButton';

type Tab = 'analytics' | 'listings' | 'bookings';

export function DashboardPage() {
  const { isLandlord } = useAuth();
  const [tab, setTab] = useState<Tab>('analytics');
  const { t } = useI18n();

  // Роль определяется AuthContext'ом по ответу IsLandLord-эндпоинта; бэк в любом случае вернёт 403
  // арендатору, это лишь защита от показа пустого/ломающегося дашборда.
  if (!isLandlord) {
    return (
      <div className="mx-auto max-w-md py-16 text-center">
        <h1 className="text-xl font-bold">{t('dashboard.title')}</h1>
        <p className="mt-2 text-neutral-500">{t('dashboard.becomeHint')}</p>
        <div className="mt-5 flex justify-center">
          <BecomeLandlordButton className="btn-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t('dashboard.title')}</h1>

      <div className="flex gap-1 border-b border-neutral-200">
        <TabButton active={tab === 'analytics'} onClick={() => setTab('analytics')}>
          {t('dashboard.tabAnalytics')}
        </TabButton>
        <TabButton active={tab === 'listings'} onClick={() => setTab('listings')}>
          {t('dashboard.tabListings')}
        </TabButton>
        <TabButton active={tab === 'bookings'} onClick={() => setTab('bookings')}>
          {t('dashboard.tabBookings')}
        </TabButton>
      </div>

      {tab === 'analytics' && <AnalyticsPanel />}
      {tab === 'listings' && <ListingManager />}
      {tab === 'bookings' && <BookingManager />}
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
  children: ReactNode;
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
