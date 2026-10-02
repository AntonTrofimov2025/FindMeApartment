import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AnalyticsPanel } from '@/components/dashboard/AnalyticsPanel';
import { ListingManager } from '@/components/dashboard/ListingManager';
import { BookingManager } from '@/components/dashboard/BookingManager';
import { BecomeLandlordButton } from '@/components/profile/BecomeLandlordButton';

type Tab = 'analytics' | 'listings' | 'bookings';

export function DashboardPage() {
  const { isLandlord } = useAuth();
  const [tab, setTab] = useState<Tab>('analytics');

  // Роль определяется AuthContext'ом по ответу IsLandLord-эндпоинта; бэк в любом случае вернёт 403
  // арендатору, это лишь защита от показа пустого/ломающегося дашборда.
  if (!isLandlord) {
    return (
      <div className="mx-auto max-w-md py-16 text-center">
        <h1 className="text-xl font-bold">Панель арендодателя</h1>
        <p className="mt-2 text-neutral-500">
          Чтобы размещать объекты и управлять бронированиями, сначала станьте арендодателем.
        </p>
        <div className="mt-5 flex justify-center">
          <BecomeLandlordButton className="btn-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Панель арендодателя</h1>

      <div className="flex gap-1 border-b border-neutral-200">
        <TabButton active={tab === 'analytics'} onClick={() => setTab('analytics')}>
          Аналитика
        </TabButton>
        <TabButton active={tab === 'listings'} onClick={() => setTab('listings')}>
          Объявления
        </TabButton>
        <TabButton active={tab === 'bookings'} onClick={() => setTab('bookings')}>
          Бронирования
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
