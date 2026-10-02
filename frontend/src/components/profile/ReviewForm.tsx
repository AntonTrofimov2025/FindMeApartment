import { useState } from 'react';
import { Star } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Review } from '@/types/models';
import { createReview, fetchReviewByBooking, updateReview } from '@/api/reviews';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';

interface ReviewFormProps {
  bookingId: string;
  /** Режим редактирования (PATCH). Сейчас на бэке PATCH отзыва доступен только администратору,
   *  поэтому в кабинете арендатора форма используется только для создания. */
  existingReview?: Review;
  onSubmitted: (review: Review) => void;
}

export function ReviewForm({ bookingId, existingReview, onSubmitted }: ReviewFormProps) {
  const [propertyRating, setPropertyRating] = useState(existingReview?.property_rating ?? 5);
  const [locationRating, setLocationRating] = useState(existingReview?.location_rating ?? 5);
  const [text, setText] = useState(existingReview?.text ?? '');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSaving(true);
    try {
      // Бэк дополнительно валидирует: booking.user === request.user и (на создании) отсутствие
      // уже существующего отзыва (строгий OneToOne). Редактирование/удаление своего отзыва теперь
      // разрешено объект-level пермишеном IsReviewAuthorOrAdmin.
      let review = existingReview
        ? await updateReview(existingReview.id, { property_rating: propertyRating, location_rating: locationRating, text })
        : await createReview({ booking: bookingId, property_rating: propertyRating, location_rating: locationRating, text });
      // ReviewViewSet.perform_create() при восстановлении ранее удалённого отзыва сохраняет старую
      // запись и выходит без serializer.instance — тогда ответ приходит без id. Перечитываем отзыв
      // по брони, чтобы дальнейшие PATCH/DELETE шли на реальный id.
      if (!review.id) {
        review = (await fetchReviewByBooking(bookingId)) ?? review;
      }
      toast.success(existingReview ? 'Отзыв обновлён' : 'Спасибо за отзыв!');
      onSubmitted(review);
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-3 space-y-3 rounded-xl border border-neutral-200 bg-white p-4">
      <StarPicker label="Оценка объекта" value={propertyRating} onChange={setPropertyRating} />
      <StarPicker label="Оценка расположения" value={locationRating} onChange={setLocationRating} />
      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Комментарий</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={1500}
          rows={3}
          required
          className="input resize-none"
          placeholder="Поделитесь впечатлениями о проживании..."
        />
      </div>
      <ErrorAlert message={error} />
      <button type="submit" disabled={isSaving} className="btn-primary !px-4 !py-2 text-sm">
        {isSaving ? 'Отправка...' : existingReview ? 'Сохранить изменения' : 'Оставить отзыв'}
      </button>
    </form>
  );
}

function StarPicker({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-neutral-500">{label}</label>
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} type="button" onClick={() => onChange(n)} aria-label={`${n} из 5`}>
            <Star size={22} className={n <= value ? 'fill-brand-500 text-brand-500' : 'fill-neutral-200 text-neutral-200'} />
          </button>
        ))}
      </div>
    </div>
  );
}
