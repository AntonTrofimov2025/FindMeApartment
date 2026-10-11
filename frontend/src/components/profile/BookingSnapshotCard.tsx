import { Lock } from 'lucide-react';
import type { BookingSnapshot } from '@/types/models';
import { useI18n } from '@/i18n';

// Бэк пишет "No data" вместо пустых полей снимка — показываем это как прочерк.
const NO_DATA = 'No data';
const show = (value?: string | number | null) => (value === undefined || value === null || value === NO_DATA || value === '' ? '—' : value);

// snapshot_data фиксируется бэком в момент создания/изменения дат брони и больше не меняется
// (см. комментарий в Booking.save()) — показываем его как "источник правды" для финансовых логов,
// а не текущие (возможно, уже изменённые) данные листинга/пользователя.
// ВАЖНО: тип жилья и страна в снимке — уже готовые подписи (get_*_display()) на языке запроса,
// которым бронь создавалась, поэтому они не переключаются вместе с языком интерфейса.
export function BookingSnapshotCard({ snapshot }: { snapshot: BookingSnapshot }) {
  const { t, money } = useI18n();
  const { property_data, booking_details, Tenant, total_price } = snapshot;

  if (!property_data && !booking_details) return null;

  const asMoney = (value?: string) => {
    const n = Number(value);
    return value && value !== NO_DATA && Number.isFinite(n) ? money(n) : '—';
  };

  return (
    <div className="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-4 text-sm">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-neutral-500">
        <Lock size={12} />
        {t('snapshot.title')}
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-neutral-700 sm:grid-cols-3">
        {property_data && (
          <>
            <Row label={t('snapshot.property')} value={show(property_data.title)} />
            <Row label={t('snapshot.city')} value={show(property_data.city)} />
            <Row label={t('snapshot.type')} value={show(property_data.property_type)} />
            <Row label={t('snapshot.pricePerNight')} value={asMoney(property_data.price_per_night)} />
          </>
        )}
        {booking_details && (
          <>
            <Row label={t('snapshot.nights')} value={show(booking_details.nights)} />
            <Row label={t('snapshot.guests')} value={show(booking_details.guests_number)} />
          </>
        )}
        {total_price && <Row label={t('snapshot.total')} value={asMoney(total_price)} />}
        {Tenant && (
          <Row
            label={t('snapshot.tenant')}
            value={[Tenant.first_name, Tenant.last_name].filter((part) => part && part !== NO_DATA).join(' ') || '—'}
          />
        )}
      </dl>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt className="text-xs text-neutral-400">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}
