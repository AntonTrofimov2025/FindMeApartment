import { Link } from 'react-router-dom';
import { ImageOff } from 'lucide-react';
import type { Listing } from '@/types/models';
import { RatingBadge } from '@/components/ui/RatingBadge';
import { PriceTag } from '@/components/ui/PriceTag';
import { countryLabel, PROPERTY_TYPES } from '@/types/choices';

export function ListingCard({ listing }: { listing: Listing }) {
  // ListingSerializer теперь встраивает photos инлайн — отдельный запрос к /photos/ на
  // каждую карточку каталога больше не нужен (раньше это был N+1: одна карточка = один запрос).
  const coverUrl = [...listing.photos].sort((a, b) => a.photo_number - b.photo_number)[0]?.photo ?? null;

  const typeLabel = PROPERTY_TYPES.find((t) => t.value === listing.property_type)?.label ?? listing.property_type;

  return (
    <Link to={`/listings/${listing.id}`} className="card group block overflow-hidden">
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-neutral-100">
        {coverUrl ? (
          <img
            src={coverUrl}
            alt={listing.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-neutral-300">
            <ImageOff size={32} />
            <span className="text-xs">Нет фото</span>
          </div>
        )}
        {!listing.is_deleted && (
          <span className="absolute left-3 top-3 rounded-md bg-white/90 px-2.5 py-1 text-xs font-medium text-neutral-700 shadow-sm">
            {typeLabel}
          </span>
        )}
        {!listing.is_active && (
          <span className="absolute right-3 top-3 rounded-md bg-neutral-900/80 px-2.5 py-1 text-xs font-medium text-white">
            Скрыто
          </span>
        )}
      </div>

      <div className="space-y-1.5 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="line-clamp-1 font-semibold text-neutral-900">{listing.title}</h3>
        </div>
        <p className="line-clamp-1 text-sm text-neutral-500">
          {listing.city}, {countryLabel(listing.country)}
        </p>
        <div className="flex items-center justify-between gap-2 pt-1">
          <PriceTag
            pricePerNight={listing.price_per_night}
            finalPricePerNight={listing.final_price_per_night}
            discount={listing.discount}
          />
        </div>
        <RatingBadge rating={listing.overall_rating} />
      </div>
    </Link>
  );
}
