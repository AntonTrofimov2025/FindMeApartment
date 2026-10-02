import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Info } from 'lucide-react';
import { differenceInCalendarDays, format } from 'date-fns';
import toast from 'react-hot-toast';
import type { Listing } from '@/types/models';
import { DateRangePicker } from './DateRangePicker';
import { PriceTag } from '@/components/ui/PriceTag';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { useAuth } from '@/hooks/useAuth';
import { createBooking } from '@/api/bookings';
import { parseApiError } from '@/lib/errors';

const ISO = (d: Date) => format(d, 'yyyy-MM-dd');

export function BookingWidget({ listing }: { listing: Listing }) {
  const { isAuthenticated, isLandlord, user } = useAuth();
  const navigate = useNavigate();
  // Booking.clean() запрещает бронировать своё же объявление и неактивные объявления, а по карте
  // ролей у Landlord нет bookings.add_booking. Показываем причину заранее, вместо формы, которая
  // всё равно упадёт на сервере (или, для лендлорда, пройдёт мимо бизнес-правила — см. README).
  const isOwner = !!user && listing.user === user.id;
  const blockedReason = isOwner
    ? 'Это ваше объявление — бронировать собственный объект нельзя.'
    : isLandlord
      ? 'Арендодатели не могут бронировать жильё. Бронирование доступно только аккаунтам арендаторов.'
      : !listing.is_active
        ? 'Объявление сейчас скрыто владельцем и не принимает бронирования.'
        : null;

  const [dateFrom, setDateFrom] = useState<Date | null>(null);
  const [dateTo, setDateTo] = useState<Date | null>(null);
  const [guests, setGuests] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nights = dateFrom && dateTo ? Math.max(0, differenceInCalendarDays(dateTo, dateFrom)) : 0;
  const estimatedTotal = useMemo(
    () => (nights > 0 ? nights * Number(listing.final_price_per_night) : 0),
    [nights, listing.final_price_per_night],
  );

  const canSubmit = isAuthenticated && dateFrom && dateTo && nights > 0 && nights <= 30 && guests >= 1;

  async function handleSubmit() {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!dateFrom || !dateTo) return;

    setError(null);
    setIsSubmitting(true);
    try {
      const booking = await createBooking({
        listing: listing.id,
        date_from: ISO(dateFrom),
        date_to: ISO(dateTo),
        guests_number: guests,
      });
      toast.success('Бронирование создано и ожидает подтверждения арендодателя.');
      navigate(`/profile?tab=bookings&highlight=${booking.id}`);
    } catch (err) {
      // Сюда прилетит, в частности, "Unfortunately the selected dates are already booked."
      // как стандартизированная 400-ошибка (errors[0].detail) из Booking.clean().
      const { message } = parseApiError(err);
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (blockedReason) {
    return (
      <div className="card sticky top-24 space-y-4 p-5">
        <PriceTag
          pricePerNight={listing.price_per_night}
          finalPricePerNight={listing.final_price_per_night}
          discount={listing.discount}
          size="lg"
        />
        <div className="flex gap-2.5 rounded-lg border border-brand-100 bg-brand-50 p-3.5 text-sm text-brand-900">
          <Info size={18} className="mt-0.5 shrink-0 text-brand-500" />
          <span>{blockedReason}</span>
        </div>
        {isOwner && (
          <Link to="/dashboard" className="btn-secondary w-full">
            Управлять объявлением
          </Link>
        )}
      </div>
    );
  }

  return (
    <div className="card sticky top-24 space-y-4 p-5">
      <PriceTag
        pricePerNight={listing.price_per_night}
        finalPricePerNight={listing.final_price_per_night}
        discount={listing.discount}
        size="lg"
      />

      <DateRangePicker dateFrom={dateFrom} dateTo={dateTo} onChange={(f, t) => { setDateFrom(f); setDateTo(t); setError(null); }} />

      {nights > 30 && (
        <p className="text-xs text-red-600">Максимум — 30 ночей за одно бронирование.</p>
      )}

      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Количество гостей</label>
        <select
          value={guests}
          onChange={(e) => setGuests(Number(e.target.value))}
          className="input"
        >
          {Array.from({ length: listing.max_guests }, (_, i) => i + 1).map((n) => (
            <option key={n} value={n}>
              {n} {n === 1 ? 'гость' : 'гостей'}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-neutral-400">Максимум для этого объекта: {listing.max_guests}</p>
      </div>

      <ErrorAlert message={error} />

      <button onClick={handleSubmit} disabled={!canSubmit || isSubmitting} className="btn-primary w-full">
        {isSubmitting ? 'Отправка...' : isAuthenticated ? 'Забронировать' : 'Войдите, чтобы забронировать'}
      </button>

      {nights > 0 && (
        <div className="space-y-1 border-t border-neutral-100 pt-3 text-sm text-neutral-600">
          <div className="flex justify-between">
            <span>
              {nights} {nights === 1 ? 'ночь' : nights < 5 ? 'ночи' : 'ночей'} ×{' '}
              {Number(listing.final_price_per_night).toFixed(2)} €
            </span>
            <span>{estimatedTotal.toFixed(2)} €</span>
          </div>
          <div className="flex justify-between font-semibold text-neutral-900">
            <span>Итого (ориентировочно)</span>
            <span>{estimatedTotal.toFixed(2)} €</span>
          </div>
          <p className="text-xs text-neutral-400">
            Точная сумма фиксируется сервером в момент подтверждения бронирования.
          </p>
        </div>
      )}
    </div>
  );
}
