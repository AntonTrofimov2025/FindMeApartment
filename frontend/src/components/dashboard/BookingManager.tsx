import { useEffect, useState } from 'react';
import { format, parseISO, isBefore, startOfDay } from 'date-fns';
import { ru } from 'date-fns/locale';
import toast from 'react-hot-toast';
import type { Booking } from '@/types/models';
import type { BookingStatus } from '@/types/choices';
import { fetchMyBookings, approveBooking, rejectBooking, cancelBooking, checkInBooking } from '@/api/bookings';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Spinner } from '@/components/ui/Spinner';
import { BOOKING_STATUSES } from '@/types/choices';
import { parseApiError } from '@/lib/errors';
import { useAuth } from '@/hooks/useAuth';

type FilterValue = BookingStatus | 'all';

export function BookingManager() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<FilterValue>('all');
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);

  async function load(status: FilterValue) {
    setIsLoading(true);
    try {
      // Для лендлорда get_queryset() возвращает Q(listing__user=user) | Q(user=user) из
      // Booking.all_objects: брони гостей по его объектам + его собственные поездки + удалённые.
      // Здесь нужны только брони гостей: свою бронь на свой же объект создать нельзя
      // (Booking.clean()), так что "гость != я" надёжно отделяет брони гостей от своих поездок.
      const data = await fetchMyBookings({
        ordering: '-created_at',
        limit: 25,
        booking_status: status === 'all' ? undefined : status,
      });
      setBookings(data.results.filter((b) => b.user !== user?.id && !b.is_deleted));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load(filter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function runAction(id: string, action: () => Promise<{ msg: string }>) {
    setPendingActionId(id);
    try {
      const res = await action();
      toast.success(res.msg);
      load(filter);
    } catch (err) {
      toast.error(parseApiError(err).message);
    } finally {
      setPendingActionId(null);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Бронирования по моим объектам</h2>

      <div className="flex flex-wrap gap-2">
        <FilterChip active={filter === 'all'} onClick={() => setFilter('all')} label="Все" />
        {BOOKING_STATUSES.map((s) => (
          <FilterChip key={s.value} active={filter === s.value} onClick={() => setFilter(s.value)} label={s.label} />
        ))}
      </div>

      {isLoading ? (
        <div className="flex h-40 items-center justify-center">
          <Spinner />
        </div>
      ) : bookings.length === 0 ? (
        <p className="py-10 text-center text-neutral-400">Бронирований с таким статусом нет.</p>
      ) : (
        <div className="space-y-3">
          {bookings.map((booking) => {
            const tenant = booking.snapshot_data.Tenant;
            const propertyTitle = booking.snapshot_data.property_data?.title ?? 'Объект';
            const isBusy = pendingActionId === booking.id;
            // booking_check_in: заселить можно с даты заезда включительно и до даты выезда
            // не включительно (timezone.localdate() < date_to).
            const today = startOfDay(new Date());
            const checkInOpen =
              !isBefore(today, startOfDay(parseISO(booking.date_from))) &&
              isBefore(today, startOfDay(parseISO(booking.date_to)));
            const canCheckIn = booking.booking_status === 'confirmed' && checkInOpen;
            // booking_approve отклоняет заявку только если date_from < сегодня: бронь "день в день"
            // подтвердить можно. Просроченные PENDING ночью отменяет close_expired_bookings.
            const isExpiredRequest =
              booking.booking_status === 'pending' && isBefore(startOfDay(parseISO(booking.date_from)), today);

            return (
              <div key={booking.id} className="card space-y-3 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h3 className="font-semibold">{propertyTitle}</h3>
                    <p className="text-sm text-neutral-500">
                      {format(parseISO(booking.date_from), 'd MMM yyyy', { locale: ru })} —{' '}
                      {format(parseISO(booking.date_to), 'd MMM yyyy', { locale: ru })} · {booking.guests_number} гостей
                    </p>
                    {tenant && (
                      <p className="text-sm text-neutral-500">
                        Арендатор: {tenant.first_name} {tenant.last_name} · {tenant.email}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold">{Number(booking.total_price).toFixed(2)} €</span>
                    <StatusBadge status={booking.booking_status} />
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {booking.booking_status === 'pending' && (
                    <>
                      <ActionButton
                        label="Подтвердить"
                        onClick={() => runAction(booking.id, () => approveBooking(booking.id))}
                        disabled={isBusy || isExpiredRequest}
                        title={
                          isExpiredRequest
                            ? 'Заявка просрочена: дата заезда уже прошла. Ночью она будет отменена автоматически.'
                            : undefined
                        }
                      />
                      <ActionButton
                        label="Отклонить"
                        danger
                        onClick={() => runAction(booking.id, () => rejectBooking(booking.id))}
                        disabled={isBusy}
                      />
                    </>
                  )}
                  {booking.booking_status === 'confirmed' && (
                    <>
                      <ActionButton
                        label="Заселить"
                        onClick={() => runAction(booking.id, () => checkInBooking(booking.id))}
                        disabled={isBusy || !canCheckIn}
                        title={
                          canCheckIn
                            ? undefined
                            : `Заселение доступно с ${booking.date_from} и до ${booking.date_to} (не включая дату выезда)`
                        }
                      />
                      <ActionButton
                        label="Отменить"
                        danger
                        onClick={() => runAction(booking.id, () => cancelBooking(booking.id))}
                        disabled={isBusy}
                      />
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function FilterChip({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
        active ? 'border-brand-500 bg-brand-500 text-white' : 'border-neutral-200 text-neutral-600 hover:bg-neutral-100'
      }`}
    >
      {label}
    </button>
  );
}

function ActionButton({
  label,
  onClick,
  disabled,
  danger,
  title,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
  title?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
        danger ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-brand-50 text-brand-600 hover:bg-brand-100'
      }`}
    >
      {label}
    </button>
  );
}
