import type { ListingFilters } from '@/api/listings';

// Пресеты собраны строго из полей ListingFilter (apps/listings/filters/listing_filter.py):
// property_type, city (istartswith), rooms/min_rooms/max_rooms, guests (вместимость от N, gte),
// min_price/max_price (по цене СО СКИДКОЙ: price_per_night * discount). Города и цены проверены на
// сид-данных create_initial_listings — каждый пресет что-то находит. Валюта — €, как и в аналитике.
export interface QuickFilterPreset {
  label: string;
  filters: Partial<ListingFilters>;
}

export const QUICK_FILTER_PRESETS: QuickFilterPreset[] = [
  { label: 'Апартаменты до 100 €', filters: { property_type: 'apartment', max_price: 100 } },
  { label: 'Студии', filters: { property_type: 'studio' } },
  { label: 'Дома от 3 комнат', filters: { property_type: 'house', min_rooms: 3 } },
  { label: 'Для компании от 6 гостей', filters: { guests: 6 } },
  { label: 'Лофты', filters: { property_type: 'loft' } },
  { label: 'Таунхаусы', filters: { property_type: 'townhouse' } },
  { label: 'Комнаты до 60 €', filters: { property_type: 'room', max_price: 60 } },
  { label: 'Жильё в Мюнхене', filters: { city: 'München' } },
  { label: 'Жильё в Гамбурге', filters: { city: 'Hamburg' } },
  { label: 'Бюджетно: до 80 €/ночь', filters: { max_price: 80 } },
];

interface QuickFilterChipsProps {
  activeIndex: number | null;
  onSelect: (preset: QuickFilterPreset, index: number) => void;
}

export function QuickFilterChips({ activeIndex, onSelect }: QuickFilterChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUICK_FILTER_PRESETS.map((preset, index) => (
        <button
          key={preset.label}
          onClick={() => onSelect(preset, index)}
          className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
            activeIndex === index
              ? 'border-brand-500 bg-brand-500 text-white'
              : 'border-neutral-200 bg-white text-neutral-700 hover:border-brand-300 hover:bg-brand-50'
          }`}
        >
          {preset.label}
        </button>
      ))}
    </div>
  );
}
