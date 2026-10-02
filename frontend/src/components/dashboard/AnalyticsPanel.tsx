import { useEffect, useState } from 'react';
import { Euro, CalendarCheck, Home, Clock } from 'lucide-react';
import { fetchLandlordAnalytics, type LandlordAnalytics } from '@/api/bookings';
import { fetchAllMyListings } from '@/api/listings';
import { useAuth } from '@/hooks/useAuth';
import { Spinner } from '@/components/ui/Spinner';

export function AnalyticsPanel() {
  const { user } = useAuth();
  const [data, setData] = useState<LandlordAnalytics | null>(null);
  const [titleById, setTitleById] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    Promise.all([fetchLandlordAnalytics(), fetchAllMyListings(user.id)])
      .then(([analytics, listings]) => {
        setData(analytics);
        setTitleById(Object.fromEntries(listings.map((l) => [l.id, l.title])));
      })
      .finally(() => setIsLoading(false));
  }, [user]);

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          icon={<Euro size={18} />}
          label="Заработано (подтверждено, заселено, завершено)"
          value={new Intl.NumberFormat('ru-RU', { style: 'currency', currency: data.financials.currency || 'EUR' }).format(
            data.financials.total_earnings,
          )}
        />
        <StatCard icon={<CalendarCheck size={18} />} label="Всего бронирований" value={String(data.counters.total_bookings)} />
        <StatCard icon={<Home size={18} />} label="Объектов с бронированиями" value={String(data.performance.active_properties_count)} />
        <StatCard icon={<Clock size={18} />} label="Ожидают подтверждения" value={String(data.counters.pending)} />
      </div>

      <div className="card p-5">
        <h3 className="mb-3 font-semibold">Бронирования по статусам</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatusMini label="Ожидает" value={data.counters.pending} />
          <StatusMini label="Подтверждено" value={data.counters.confirmed} />
          <StatusMini label="Заселены" value={data.counters.checked_in} />
          <StatusMini label="Завершено" value={data.counters.completed} />
          <StatusMini label="Отменено" value={data.counters.cancelled} />
          <StatusMini label="Всего" value={data.counters.total_bookings} />
        </div>
      </div>

      <div className="card p-5">
        <h3 className="mb-1 font-semibold">Объекты, по которым уже были бронирования</h3>
        <p className="mb-3 text-xs text-neutral-400">
          Список ID объектов из <code>performance.properties_ids</code>, сопоставленных с названиями ваших объявлений.
        </p>
        {data.performance.properties_ids.length === 0 ? (
          <p className="text-sm text-neutral-400">Пока нет бронирований ни по одному объекту.</p>
        ) : (
          <ul className="divide-y divide-neutral-100">
            {data.performance.properties_ids.map((id) => (
              <li key={id} className="flex items-center justify-between py-2 text-sm">
                <span className="font-medium text-neutral-800">{titleById[id] ?? 'Объявление удалено'}</span>
                <span className="font-mono text-xs text-neutral-400">{id}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="card space-y-2 p-4">
      <div className="flex items-center gap-2 text-brand-500">{icon}</div>
      <p className="text-2xl font-bold text-neutral-900">{value}</p>
      <p className="text-xs text-neutral-500">{label}</p>
    </div>
  );
}

function StatusMini({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-brand-50 p-3 text-center">
      <p className="text-lg font-bold text-brand-900">{value}</p>
      <p className="text-xs text-neutral-500">{label}</p>
    </div>
  );
}
