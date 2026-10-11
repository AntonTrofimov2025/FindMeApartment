import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import { format, parseISO, differenceInCalendarDays } from 'date-fns';
import toast from 'react-hot-toast';
import type { Booking, Review } from '@/types/models';
import { fetchMyBookings, cancelBooking } from '@/api/bookings';
import { fetchReviewByBooking, deleteReview } from '@/api/reviews';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { BookingSnapshotCard } from './BookingSnapshotCard';
import { ReviewForm } from './ReviewForm';
import { Spinner } from '@/components/ui/Spinner';
import { parseApiError } from '@/lib/errors';
import { useAuth } from '@/hooks/useAuth';
import { useI18n } from '@/i18n';

export function BookingHistory({ highlightId }: { highlightId?: string | null }) {
  const { user, isLandlord } = useAuth();
  const { t, tn, money, dateLocale } = useI18n();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [reviewFormFor, setReviewFormFor] = useState<string | null>(null);
  const [pendingActionId, setPendingActionId] = useState<string | null>(null);
  // ReviewViewSet.filterset_fields теперь включает 'booking': ['exact'] — статус "уже есть
  // отзыв" читаем напрямую с бэка (GET /reviews/?booking=<id>), а не держим только в рамках сессии.
  const [myReviews, setMyReviews] = useState<Record<string, Review>>({});

  async function load() {
    setIsLoading(true);
    try {
      const data = await fetchMyBookings({ ordering: '-created_at', limit: 25 });
      // Для лендлорда BookingViewSet.get_queryset() отдаёт Q(listing__user=user) | Q(user=user):
      // и брони гостей по его объектам, и его собственные поездки времён роли Tenant. В профиле
      // показываем только поездки, где он сам гость; брони гостей — в дашборде. Удалённые
      // (is_deleted) тоже отсекаем — для лендлорда бэк берёт Booking.all_objects.
      const trips = data.results.filter((b) => b.user === user?.id && !b.is_deleted);
      setBookings(trips);

      const completed = trips.filter((b) => b.booking_status === 'completed');
      const reviews = await Promise.all(completed.map((b) => fetchReviewByBooking(b.id)));
      const reviewsMap: Record<string, Review> = {};
      completed.forEach((b, i) => {
        const review = reviews[i];
        if (review) reviewsMap[b.id] = review;
      });
      setMyReviews(reviewsMap);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCancel(booking: Booking) {
    setPendingActionId(booking.id);
    try {
      const res = await cancelBooking(booking.id);
      toast.success(res.msg);
      load();
    } catch (err) {
      toast.error(parseApiError(err).message);
    } finally {
      setPendingActionId(null);
    }
  }

  async function handleDeleteReview(bookingId: string) {
    const review = myReviews[bookingId];
    if (!review) return;
    try {
      await deleteReview(review.id);
      setMyReviews((prev) => {
        const next = { ...prev };
        delete next[bookingId];
        return next;
      });
      toast.success(t('history.reviewDeleted'));
    } catch (err) {
      toast.error(parseApiError(err).message);
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!bookings.length) {
    return (
      <p className="py-10 text-center text-neutral-400">
        {isLandlord ? t('history.emptyLandlord') : t('history.empty')}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {bookings.map((booking) => {
        const isHighlighted = booking.id === highlightId;
        const propertyTitle = booking.snapshot_data.property_data?.title ?? t('snapshot.property');
        // Booking.clean(): отмену уже подтверждённой (CONFIRMED) брони бэк отклонит меньше чем
        // за 2 дня до заезда — подсказываем это на кнопке, но финальное решение всегда за сервером.
        const nightsToStart = differenceInCalendarDays(parseISO(booking.date_from), new Date());
        const tooLateToCancelConfirmed = booking.booking_status === 'confirmed' && nightsToStart < 2;
        const canCancel = booking.booking_status === 'pending' || booking.booking_status === 'confirmed';
        const canReview = booking.booking_status === 'completed';
        const myReview = myReviews[booking.id];
        const isBusy = pendingActionId === booking.id;

        return (
          <div
            key={booking.id}
            className={`card space-y-3 p-5 ${isHighlighted ? 'ring-2 ring-brand-500' : ''}`}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                {/* Название ведёт на страницу объявления — параметры объекта можно посмотреть прямо из брони */}
                <h3 className="font-semibold">
                  <Link to={`/listings/${booking.listing}`} className="hover:text-brand-600 hover:underline">
                    {propertyTitle}
                  </Link>
                </h3>
                <p className="text-sm text-neutral-500">
                  {format(parseISO(booking.date_from), 'd MMM yyyy', { locale: dateLocale })} —{' '}
                  {format(parseISO(booking.date_to), 'd MMM yyyy', { locale: dateLocale })} ·{' '}
                  {tn('guests.count', booking.guests_number)}
                </p>
              </div>
              <StatusBadge status={booking.booking_status} />
            </div>

            <div className="flex items-center justify-between text-sm">
              <span className="text-neutral-500">{t('history.total')}</span>
              <span className="font-semibold">{money(Number(booking.total_price))}</span>
            </div>

            <BookingSnapshotCard snapshot={booking.snapshot_data} />

            <div className="flex flex-wrap items-center gap-2 pt-1">
              <Link
                to={`/listings/${booking.listing}`}
                className="btn-secondary inline-flex items-center gap-1.5 !px-3 !py-1.5 text-xs"
              >
                <ExternalLink size={14} />
                {t('history.openListing')}
              </Link>

              {canCancel && (
                <button
                  onClick={() => handleCancel(booking)}
                  disabled={isBusy}
                  title={tooLateToCancelConfirmed ? t('history.cancelHint') : undefined}
                  className="btn-secondary border-red-200 !px-3 !py-1.5 text-xs text-red-600 hover:bg-red-50"
                >
                  {isBusy ? t('history.cancelling') : t('history.cancel')}
                </button>
              )}

              {canReview && !myReview && reviewFormFor !== booking.id && (
                <button onClick={() => setReviewFormFor(booking.id)} className="btn-secondary !px-3 !py-1.5 text-xs">
                  {t('history.leaveReview')}
                </button>
              )}

              {/* ReviewViewSet: update/partial_update доступны только IsAdminUser, destroy — автору.
                  Поэтому автор не редактирует отзыв, а удаляет и пишет заново: perform_create
                  восстанавливает удалённый отзыв с новыми данными (OneToOne с бронью сохраняется). */}
              {canReview && myReview && reviewFormFor !== booking.id && (
                <button
                  onClick={() => handleDeleteReview(booking.id)}
                  className="btn-secondary border-red-200 !px-3 !py-1.5 text-xs text-red-600 hover:bg-red-50"
                >
                  {t('history.deleteReview')}
                </button>
              )}
            </div>

            {myReview && (
              <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-3 text-sm">
                <p className="mb-1 text-xs font-medium text-neutral-500">
                  {t('history.yourReview', { p: myReview.property_rating, l: myReview.location_rating })}
                </p>
                <p className="whitespace-pre-line text-neutral-700">{myReview.text}</p>
              </div>
            )}

            {tooLateToCancelConfirmed && canCancel && (
              <p className="text-xs text-neutral-400">{t('history.cancelHint')}</p>
            )}

            {reviewFormFor === booking.id && (
              <ReviewForm
                bookingId={booking.id}
                onSubmitted={(review) => {
                  setMyReviews((prev) => ({ ...prev, [booking.id]: review }));
                  setReviewFormFor(null);
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
