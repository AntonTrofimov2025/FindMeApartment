import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Users, BedDouble, Home as HomeIcon, Lock } from 'lucide-react';
import type { Listing, Review } from '@/types/models';
import { fetchListing } from '@/api/listings';
import { fetchReviewsForListing } from '@/api/reviews';
import { PhotoGallery } from '@/components/listings/PhotoGallery';
import { BookingWidget } from '@/components/booking/BookingWidget';
import { RatingBadge } from '@/components/ui/RatingBadge';
import { Spinner } from '@/components/ui/Spinner';
import { propertyTypeKey } from '@/types/choices';
import { useI18n } from '@/i18n';

export function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [listing, setListing] = useState<Listing | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const { t, tn, country } = useI18n();

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setIsLoading(true);
    setNotFound(false);

    // Фото теперь приходят вложенными в сам листинг (ListingSerializer.photos) —
    // отдельный запрос к /photos/?listing=<id> для отображения больше не нужен.
    Promise.all([fetchListing(id), fetchReviewsForListing(id)])
      .then(([listingData, reviewsData]) => {
        if (cancelled) return;
        setListing(listingData);
        // fetchReviewsForListing уже отсёк мягко удалённые отзывы (их видит только staff)
        setReviews(reviewsData.results);
      })
      .catch((err) => {
        if (!cancelled && err?.response?.status === 404) setNotFound(true);
      })
      .finally(() => !cancelled && setIsLoading(false));

    return () => {
      cancelled = true;
    };
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spinner size={36} />
      </div>
    );
  }

  if (notFound || !listing) {
    return (
      <div className="py-24 text-center">
        <p className="text-lg font-medium text-neutral-600">{t('detail.notFound')}</p>
        {/* Сюда же попадают переходы из брони на объявление, которое хозяин скрыл/удалил:
            ListingViewSet отдаёт арендатору только активные объекты. */}
        <p className="mt-1 text-sm text-neutral-400">{t('detail.notFoundHint')}</p>
        <Link to="/" className="btn-primary mt-4 inline-flex">
          {t('detail.backHome')}
        </Link>
      </div>
    );
  }

  const typeLabel = t(propertyTypeKey(listing.property_type));
  // ListingSerializer.to_representation() скрывает точный адрес от всех, кроме владельца, staff
  // и гостей с CONFIRMED/CHECKED_IN бронью: street -> "Hidden until booking confirmation",
  // house_number/apartment_number -> "X". Город и район остаются видны всем.
  // Проверяем по строке-маркеру в street, а не по "X" в номере дома — реальный дом тоже может быть "X".
  const isAddressHidden = listing.street === 'Hidden until booking confirmation';
  const addressLine = [listing.street, listing.house_number, listing.apartment_number && t('detail.apartmentShort', { n: listing.apartment_number })]
    .filter(Boolean)
    .join(', ');

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">{listing.title}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-neutral-500">
            <RatingBadge rating={listing.overall_rating} reviewsCount={reviews.length} />
            <span className="flex items-center gap-1">
              <MapPin size={14} />
              {listing.city}, {country(listing.country)}
            </span>
          </div>
        </div>

        <PhotoGallery photos={listing.photos} />

        <div className="flex flex-wrap gap-4 rounded-xl2 bg-white p-4 shadow-card">
          <InfoChip icon={<HomeIcon size={16} />} label={typeLabel} />
          <InfoChip icon={<BedDouble size={16} />} label={t('rooms.short', { n: listing.rooms })} />
          <InfoChip icon={<Users size={16} />} label={tn('guests.upTo', listing.max_guests)} />
        </div>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold">{t('detail.about')}</h2>
          <p className="whitespace-pre-line text-neutral-700">{listing.description}</p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold">{t('detail.address')}</h2>
          <p className="text-neutral-700">
            {country(listing.country)}, {listing.city}, {listing.district}
            {!isAddressHidden && `, ${addressLine}`}
          </p>
          {isAddressHidden && (
            <p className="flex items-center gap-1.5 text-sm text-neutral-500">
              <Lock size={14} />
              {t('detail.addressHidden')}
            </p>
          )}
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">
            {t('detail.reviews')} {reviews.length > 0 && `(${reviews.length})`}
          </h2>
          {reviews.length === 0 ? (
            <p className="text-neutral-400">{t('detail.noReviews')}</p>
          ) : (
            <div className="space-y-3">
              {reviews.map((review) => (
                <div key={review.id} className="rounded-xl border border-neutral-200 p-4">
                  <div className="mb-1 flex items-center gap-3 text-sm text-neutral-500">
                    <span className="font-medium text-neutral-800">{t('detail.reviewProperty', { n: review.property_rating })}</span>
                    <span>{t('detail.reviewLocation', { n: review.location_rating })}</span>
                  </div>
                  <p className="text-neutral-700">{review.text}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <div>
        <BookingWidget listing={listing} />
      </div>
    </div>
  );
}

function InfoChip({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full bg-neutral-100 px-3 py-1.5 text-sm text-neutral-700">
      {icon}
      {label}
    </span>
  );
}
