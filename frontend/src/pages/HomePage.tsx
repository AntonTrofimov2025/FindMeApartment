import { useEffect, useState } from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';
import type { Listing } from '@/types/models';
import { fetchListings, type ListingFilters } from '@/api/listings';
import { ListingGrid } from '@/components/listings/ListingGrid';
import { QuickFilterChips, type QuickFilterPreset } from '@/components/listings/QuickFilterChips';
import { PROPERTY_TYPES, COUNTRIES, ROOM_COUNTS, MAX_GUESTS_OPTIONS } from '@/types/choices';

const ORDERING_OPTIONS = [
  { value: '-created_at', label: 'Сначала новые' },
  { value: 'price_per_night', label: 'Цена: по возрастанию' },
  { value: '-price_per_night', label: 'Цена: по убыванию' },
  { value: 'rooms', label: 'Комнаты: сначала меньше' },
];

export function HomePage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [count, setCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);

  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<ListingFilters>({ ordering: '-created_at', limit: 12, offset: 0 });
  const [activeChip, setActiveChip] = useState<number | null>(null);

  async function load(nextFilters: ListingFilters) {
    setIsLoading(true);
    try {
      const data = await fetchListings(nextFilters);
      setListings(data.results);
      setCount(data.count);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFilters((f) => ({ ...f, search: search || undefined, offset: 0 }));
  }

  function updateFilter<K extends keyof ListingFilters>(key: K, value: ListingFilters[K]) {
    setFilters((f) => ({ ...f, [key]: value || undefined, offset: 0 }));
    setActiveChip(null); // ручное изменение фильтра снимает подсветку быстрого чипа
  }

  // Повторный клик по уже активному чипу сбрасывает его — возвращаемся к базовым
  // структурным фильтрам, не трогая ordering и текстовый поиск.
  function handleQuickFilterSelect(preset: QuickFilterPreset, index: number) {
    if (activeChip === index) {
      setFilters((f) => ({
        search: f.search,
        ordering: f.ordering,
        limit: f.limit,
        offset: 0,
      }));
      setActiveChip(null);
      return;
    }

    setFilters((f) => ({
      search: f.search,
      ordering: f.ordering,
      limit: f.limit,
      offset: 0,
      ...preset.filters,
    }));
    setActiveChip(index);
  }

  const totalPages = Math.max(1, Math.ceil(count / (filters.limit ?? 12)));
  const currentPage = Math.floor((filters.offset ?? 0) / (filters.limit ?? 12)) + 1;

  return (
    <div className="space-y-8">
      {/* Hero: тёмно-синяя секция с поисковой карточкой, наплывающей на нижний край — как на Booking.com */}
      <section className="-mx-4 -mt-6 bg-brand-900 px-4 pb-16 pt-8 sm:-mx-6 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <h1 className="text-2xl font-bold text-white sm:text-3xl">Найдите следующее жильё для отдыха</h1>
          <p className="mt-1 text-brand-100">Квартиры, дома и студии — с моментальным бронированием</p>
        </div>
      </section>

      <div className="-mt-16 space-y-4 rounded-xl2 border border-neutral-200 bg-white p-5 shadow-card-hover sm:mx-0">
        <form onSubmit={handleSearchSubmit} className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search size={18} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Город, район, название объявления..."
              className="input pl-10"
            />
          </div>
          <button type="submit" className="btn-primary">
            Найти
          </button>
          <button type="button" onClick={() => setShowFilters((s) => !s)} className="btn-secondary">
            <SlidersHorizontal size={16} className="mr-2" />
            Фильтры
          </button>
        </form>

        <QuickFilterChips activeIndex={activeChip} onSelect={handleQuickFilterSelect} />

        {showFilters && (
          <div className="grid grid-cols-2 gap-3 border-t border-neutral-100 pt-4 sm:grid-cols-3 lg:grid-cols-7">
            <select
              className="input"
              defaultValue=""
              onChange={(e) => updateFilter('property_type', e.target.value || undefined)}
            >
              <option value="">Тип жилья</option>
              {PROPERTY_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>

            <select
              className="input"
              defaultValue=""
              onChange={(e) => updateFilter('country', e.target.value ? Number(e.target.value) : undefined)}
            >
              <option value="">Страна</option>
              {COUNTRIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>

            <select
              className="input"
              defaultValue=""
              onChange={(e) => updateFilter('rooms', e.target.value ? Number(e.target.value) : undefined)}
            >
              <option value="">Комнат (точно)</option>
              {ROOM_COUNTS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>

            <select
              className="input"
              defaultValue=""
              onChange={(e) => updateFilter('guests', e.target.value ? Number(e.target.value) : undefined)}
            >
              <option value="">Гостей</option>
              {MAX_GUESTS_OPTIONS.map((n) => (
                <option key={n} value={n}>
                  от {n} {n === 1 ? 'гостя' : 'гостей'}
                </option>
              ))}
            </select>

            <input
              type="number"
              placeholder="Цена от"
              className="input"
              onChange={(e) => updateFilter('min_price', e.target.value ? Number(e.target.value) : undefined)}
            />
            <input
              type="number"
              placeholder="Цена до"
              className="input"
              onChange={(e) => updateFilter('max_price', e.target.value ? Number(e.target.value) : undefined)}
            />
            <select className="input" value={filters.ordering} onChange={(e) => updateFilter('ordering', e.target.value)}>
              {ORDERING_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between">
        <h2 className="text-xl font-semibold text-neutral-900">
          {isLoading ? 'Ищем варианты...' : `Найдено объявлений: ${count}`}
        </h2>
      </div>

      <ListingGrid listings={listings} isLoading={isLoading} />

      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => setFilters((f) => ({ ...f, offset: (page - 1) * (f.limit ?? 12) }))}
              className={`h-9 w-9 rounded-lg text-sm font-medium transition-colors ${
                page === currentPage ? 'bg-brand-500 text-white' : 'bg-white text-neutral-600 hover:bg-neutral-100'
              }`}
            >
              {page}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
