interface RatingBadgeProps {
  /** overall_rating приходит с бэка как strict float в шкале 1..5 (0.0, если отзывов ещё нет) */
  rating: number;
  reviewsCount?: number;
  size?: 'sm' | 'lg';
}

function descriptor(rating: number): string {
  if (rating <= 0) return 'Новое';
  if (rating >= 4.5) return 'Превосходно';
  if (rating >= 4) return 'Очень хорошо';
  if (rating >= 3) return 'Хорошо';
  if (rating >= 2) return 'Неплохо';
  return 'Так себе';
}

function pluralizeReviews(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return 'отзыв';
  if ([2, 3, 4].includes(mod10) && ![12, 13, 14].includes(mod100)) return 'отзыва';
  return 'отзывов';
}

export function RatingBadge({ rating, reviewsCount, size = 'sm' }: RatingBadgeProps) {
  const hasRating = rating > 0;
  const boxSize = size === 'lg' ? 'h-11 w-11 text-base' : 'h-8 w-8 text-sm';

  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex ${boxSize} items-center justify-center rounded-md font-bold text-white ${
          hasRating ? 'bg-brand-700' : 'bg-neutral-400'
        }`}
      >
        {hasRating ? rating.toFixed(1) : '—'}
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold text-neutral-900">{descriptor(rating)}</p>
        {typeof reviewsCount === 'number' && reviewsCount > 0 && (
          <p className="text-xs text-neutral-500">
            {reviewsCount} {pluralizeReviews(reviewsCount)}
          </p>
        )}
      </div>
    </div>
  );
}
