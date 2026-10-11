import { useI18n } from '@/i18n';
import type { StringKey } from '@/i18n';

interface RatingBadgeProps {
  /** overall_rating приходит с бэка как strict float в шкале 1..5 (0.0, если отзывов ещё нет) */
  rating: number;
  reviewsCount?: number;
  size?: 'sm' | 'lg';
}

function descriptorKey(rating: number): StringKey {
  if (rating <= 0) return 'rating.new';
  if (rating >= 4.5) return 'rating.superb';
  if (rating >= 4) return 'rating.veryGood';
  if (rating >= 3) return 'rating.good';
  if (rating >= 2) return 'rating.fair';
  return 'rating.poor';
}

export function RatingBadge({ rating, reviewsCount, size = 'sm' }: RatingBadgeProps) {
  const { t, tn, intlLocale } = useI18n();
  const hasRating = rating > 0;
  const boxSize = size === 'lg' ? 'h-11 w-11 text-base' : 'h-8 w-8 text-sm';
  // 4.5 / 4,5 — десятичный разделитель зависит от языка
  const formatted = hasRating
    ? rating.toLocaleString(intlLocale, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
    : '—';

  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex ${boxSize} items-center justify-center rounded-md font-bold text-white ${
          hasRating ? 'bg-brand-700' : 'bg-neutral-400'
        }`}
      >
        {formatted}
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold text-neutral-900">{t(descriptorKey(rating))}</p>
        {typeof reviewsCount === 'number' && reviewsCount > 0 && (
          <p className="text-xs text-neutral-500">{tn('reviews.count', reviewsCount)}</p>
        )}
      </div>
    </div>
  );
}
