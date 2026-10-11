import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Pencil, ImagePlus, Trash2, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Listing } from '@/types/models';
import { fetchAllMyListings, deleteListing, toggleListingActive } from '@/api/listings';
import { useAuth } from '@/hooks/useAuth';
import { Spinner } from '@/components/ui/Spinner';
import { Modal } from '@/components/ui/Modal';
import { PriceTag } from '@/components/ui/PriceTag';
import { RatingBadge } from '@/components/ui/RatingBadge';
import { ListingForm } from './ListingForm';
import { PhotoManager } from './PhotoManager';
import { parseApiError } from '@/lib/errors';
import { useI18n } from '@/i18n';

export function ListingManager() {
  const { user } = useAuth();
  const { t, tn } = useI18n();
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formTarget, setFormTarget] = useState<Listing | 'new' | null>(null);
  const [photoTarget, setPhotoTarget] = useState<Listing | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Listing | null>(null);

  async function load() {
    if (!user) return;
    setIsLoading(true);
    try {
      const mine = await fetchAllMyListings(user.id);
      setListings(mine);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  async function handleToggleActive(listing: Listing) {
    try {
      const res = await toggleListingActive(listing.id);
      // is_active теперь есть в ListingSerializer, но точечно обновляем и локальное
      // состояние из ответа toggle/, чтобы не делать лишний перезапрос списка целиком.
      setListings((prev) => prev.map((l) => (l.id === listing.id ? { ...l, is_active: res.is_active } : l)));
      toast.success(res.msg);
    } catch (err) {
      toast.error(parseApiError(err).message);
    }
  }

  async function handleDelete() {
    if (!confirmDelete) return;
    try {
      await deleteListing(confirmDelete.id);
      toast.success(t('listings.deleted'));
      setListings((prev) => prev.filter((l) => l.id !== confirmDelete.id));
      setConfirmDelete(null);
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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{t('listings.title', { n: listings.length })}</h2>
        <button onClick={() => setFormTarget('new')} className="btn-primary !px-4 !py-2 text-sm">
          <Plus size={16} className="mr-1.5" />
          {t('listings.new')}
        </button>
      </div>

      {listings.length === 0 ? (
        <p className="py-10 text-center text-neutral-400">{t('listings.empty')}</p>
      ) : (
        <div className="space-y-3">
          {listings.map((listing) => (
            <div key={listing.id} className="card flex flex-wrap items-center gap-4 p-4">
              <div className="min-w-[220px] flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">
                    <Link to={`/listings/${listing.id}`} className="hover:text-brand-600 hover:underline">
                      {listing.title}
                    </Link>
                  </h3>
                  {!listing.is_active && (
                    <span className="rounded-md bg-neutral-200 px-2 py-0.5 text-xs text-neutral-600">{t('card.hidden')}</span>
                  )}
                </div>
                <p className="text-sm text-neutral-500">
                  {listing.city} · {t('rooms.short', { n: listing.rooms })} · {tn('guests.upTo', listing.max_guests)}
                </p>
                <div className="mt-2 flex items-center gap-3">
                  <PriceTag
                    pricePerNight={listing.price_per_night}
                    finalPricePerNight={listing.final_price_per_night}
                    discount={listing.discount}
                  />
                  <RatingBadge rating={listing.overall_rating} />
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <IconButton icon={<Pencil size={14} />} label={t('listings.edit')} onClick={() => setFormTarget(listing)} />
                <IconButton icon={<ImagePlus size={14} />} label={t('listings.photos')} onClick={() => setPhotoTarget(listing)} />
                <IconButton
                  icon={listing.is_active ? <EyeOff size={14} /> : <Eye size={14} />}
                  label={listing.is_active ? t('listings.hide') : t('listings.show')}
                  onClick={() => handleToggleActive(listing)}
                />
                <IconButton
                  icon={<Trash2 size={14} />}
                  label={t('listings.delete')}
                  danger
                  onClick={() => setConfirmDelete(listing)}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {formTarget && (
        <Modal
          title={formTarget === 'new' ? t('listings.newTitle') : t('listings.editTitle')}
          onClose={() => setFormTarget(null)}
          widthClass="max-w-2xl"
        >
          <ListingForm
            listing={formTarget === 'new' ? undefined : formTarget}
            onSaved={() => {
              setFormTarget(null);
              load();
            }}
          />
        </Modal>
      )}

      {photoTarget && (
        <Modal title={t('listings.photosTitle', { title: photoTarget.title })} onClose={() => setPhotoTarget(null)} widthClass="max-w-xl">
          <PhotoManager listingId={photoTarget.id} />
        </Modal>
      )}

      {confirmDelete && (
        <Modal title={t('listings.deleteTitle')} onClose={() => setConfirmDelete(null)}>
          <p className="mb-4 text-sm text-neutral-600">{t('listings.deleteText', { title: confirmDelete.title })}</p>
          <div className="flex justify-end gap-2">
            <button onClick={() => setConfirmDelete(null)} className="btn-secondary !px-4 !py-2 text-sm">
              {t('common.cancel')}
            </button>
            <button onClick={handleDelete} className="btn-primary !bg-red-600 !px-4 !py-2 text-sm hover:!bg-red-700">
              {t('listings.delete')}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

function IconButton({
  icon,
  label,
  onClick,
  danger,
}: {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  danger?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors ${
        danger
          ? 'border-red-200 text-red-600 hover:bg-red-50'
          : 'border-neutral-200 text-brand-700 hover:bg-brand-50'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
