import { useI18n } from '@/i18n';

interface PriceTagProps {
  /** Decimal-строки, как их отдаёт DRF */
  pricePerNight: string;
  finalPricePerNight: string;
  discount: string;
  size?: 'sm' | 'lg';
}

export function PriceTag({ pricePerNight, finalPricePerNight, discount, size = 'sm' }: PriceTagProps) {
  const { t, money } = useI18n();
  const original = Number(pricePerNight);
  const final = Number(finalPricePerNight);
  // discount — коэффициент (0.01..1.00), а не проценты: скидка есть только если < 1.00
  const hasDiscount = Number(discount) < 1 && final < original;
  const percentOff = hasDiscount ? Math.round((1 - Number(discount)) * 100) : 0;

  const priceClass = size === 'lg' ? 'text-2xl font-semibold' : 'text-base font-semibold';

  return (
    <div className="flex items-baseline gap-2">
      {hasDiscount && <span className="text-sm text-neutral-400 line-through">{money(original)}</span>}
      <span className={priceClass}>{money(final)}</span>
      <span className="text-sm font-normal text-neutral-500">{t('common.perNight')}</span>
      {hasDiscount && (
        <span className="rounded-md bg-emerald-50 px-1.5 py-0.5 text-xs font-semibold text-emerald-700">
          −{percentOff}%
        </span>
      )}
    </div>
  );
}
