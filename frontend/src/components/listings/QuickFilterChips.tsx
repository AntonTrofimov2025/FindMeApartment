import type { ListingFilters } from '@/api/listings';
import { useI18n } from '@/i18n';
import type { StringKey } from '@/i18n';

// Пресеты собраны строго из полей ListingFilter (apps/listings/filters/listing_filter.py):
// property_type, city (istartswith), rooms/min_rooms/max_rooms, guests (вместимость от N, gte),
// min_price/max_price (по цене СО СКИДКОЙ: price_per_night * discount). Города и цены проверены на
// сид-данных create_initial_listings — каждый пресет что-то находит. Валюта — €, как и в аналитике.
export interface QuickFilterPreset {
  /** Ключ словаря i18n — подпись переводится в момент отрисовки */
  labelKey: StringKey;
  filters: Partial<ListingFilters>;
}

export const QUICK_FILTER_PRESETS: QuickFilterPreset[] = [
  { labelKey: 'chips.apartmentsUnder100', filters: { property_type: 'apartment', max_price: 100 } },
  { labelKey: 'chips.studios', filters: { property_type: 'studio' } },
  { labelKey: 'chips.houses3Rooms', filters: { property_type: 'house', min_rooms: 3 } },
  { labelKey: 'chips.groups6', filters: { guests: 6 } },
  { labelKey: 'chips.lofts', filters: { property_type: 'loft' } },
  { labelKey: 'chips.townhouses', filters: { property_type: 'townhouse' } },
  { labelKey: 'chips.roomsUnder60', filters: { property_type: 'room', max_price: 60 } },
  { labelKey: 'chips.munich', filters: { city: 'München' } },
  { labelKey: 'chips.hamburg', filters: { city: 'Hamburg' } },
  { labelKey: 'chips.budget80', filters: { max_price: 80 } },
];

interface QuickFilterChipsProps {
  activeIndex: number | null;
  onSelect: (preset: QuickFilterPreset, index: number) => void;
}

export function QuickFilterChips({ activeIndex, onSelect }: QuickFilterChipsProps) {
  const { t } = useI18n();
  return (
    <div className="flex flex-wrap gap-2">
      {QUICK_FILTER_PRESETS.map((preset, index) => (
        <button
          key={preset.labelKey}
          onClick={() => onSelect(preset, index)}
          className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
            activeIndex === index
              ? 'border-brand-500 bg-brand-500 text-white'
              : 'border-neutral-200 bg-white text-neutral-700 hover:border-brand-300 hover:bg-brand-50'
          }`}
        >
          {t(preset.labelKey)}
        </button>
      ))}
    </div>
  );
}
