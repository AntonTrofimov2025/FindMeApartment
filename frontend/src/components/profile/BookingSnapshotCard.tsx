import { Lock } from 'lucide-react';
import type { BookingSnapshot } from '@/types/models';

// snapshot_data фиксируется бэком в момент создания/изменения дат брони и больше не меняется
// (см. комментарий в Booking.save()) — показываем его как "источник правды" для финансовых логов,
// а не текущие (возможно, уже изменённые) данные листинга/пользователя.
export function BookingSnapshotCard({ snapshot }: { snapshot: BookingSnapshot }) {
  const { property_data, booking_details, Tenant, total_price } = snapshot;

  if (!property_data && !booking_details) return null;

  return (
    <div className="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-4 text-sm">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-neutral-500">
        <Lock size={12} />
        Зафиксированные данные на момент бронирования
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-neutral-700 sm:grid-cols-3">
        {property_data && (
          <>
            <Row label="Объект" value={property_data.title} />
            <Row label="Город" value={property_data.city} />
            <Row label="Тип" value={property_data.property_type} />
            <Row label="Цена / ночь" value={`${property_data.price_per_night} €`} />
          </>
        )}
        {booking_details && (
          <>
            <Row label="Ночей" value={booking_details.nights} />
            <Row label="Гостей" value={booking_details.guests_number} />
          </>
        )}
        {total_price && <Row label="Итоговая сумма" value={`${total_price} €`} />}
        {Tenant && <Row label="Арендатор" value={`${Tenant.first_name} ${Tenant.last_name}`} />}
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
