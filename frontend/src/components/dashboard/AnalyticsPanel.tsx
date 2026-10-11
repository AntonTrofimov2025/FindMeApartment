import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Euro, CalendarCheck, Home, Clock, ChevronRight } from 'lucide-react';
import { fetchLandlordAnalytics, type LandlordAnalytics } from '@/api/bookings';
import { fetchAllMyListings } from '@/api/listings';
import { useAuth } from '@/hooks/useAuth';
import { Spinner } from '@/components/ui/Spinner';
import { useI18n } from '@/i18n';

export function AnalyticsPanel() {
  const { user } = useAuth();
  const { t, money } = useI18n();
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
          label={t('analytics.earned')}
          value={money(data.financials.total_earnings, data.financials.currency || 'EUR')}
        />
        <StatCard icon={<CalendarCheck size={18} />} label={t('analytics.totalBookings')} value={String(data.counters.total_bookings)} />
        <StatCard icon={<Home size={18} />} label={t('analytics.propertiesWithBookings')} value={String(data.performance.active_properties_count)} />
        <StatCard icon={<Clock size={18} />} label={t('analytics.awaiting')} value={String(data.counters.pending)} />
      </div>

      <div className="card p-5">
        <h3 className="mb-3 font-semibold">{t('analytics.byStatus')}</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatusMini label={t('analytics.pending')} value={data.counters.pending} />
          <StatusMini label={t('analytics.confirmed')} value={data.counters.confirmed} />
          <StatusMini label={t('analytics.checkedIn')} value={data.counters.checked_in} />
          <StatusMini label={t('analytics.completed')} value={data.counters.completed} />
          <StatusMini label={t('analytics.cancelled')} value={data.counters.cancelled} />
          <StatusMini label={t('analytics.total')} value={data.counters.total_bookings} />
        </div>
      </div>

      <div className="card p-5">
        <h3 className="mb-1 font-semibold">{t('analytics.propertiesTitle')}</h3>
        <p className="mb-3 text-xs text-neutral-400">{t('analytics.propertiesHint')}</p>
        {data.performance.properties_ids.length === 0 ? (
          <p className="text-sm text-neutral-400">{t('analytics.noProperties')}</p>
        ) : (
          <ul className="divide-y divide-neutral-100">
            {data.performance.properties_ids.map((id) =>
              // Удалённого объявления нет среди "моих" (менеджер objects его скрывает) —
              // ссылку на него не даём: страница всё равно ответит 404.
              titleById[id] ? (
                <li key={id}>
                  <Link
                    to={`/listings/${id}`}
                    className="group flex items-center justify-between gap-3 py-2 text-sm hover:text-brand-600"
                  >
                    <span className="font-medium text-neutral-800 group-hover:text-brand-600">{titleById[id]}</span>
                    <ChevronRight size={16} className="shrink-0 text-neutral-300 group-hover:text-brand-500" />
                  </Link>
                </li>
              ) : (
                <li key={id} className="flex items-center justify-between gap-3 py-2 text-sm">
                  <span className="italic text-neutral-400">{t('analytics.listingDeleted')}</span>
                  <span className="font-mono text-xs text-neutral-300">{id.slice(0, 8)}</span>
                </li>
              ),
            )}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
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
