import { useEffect, useState } from 'react';
import { Trash2, Upload, ImageOff } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Photo } from '@/types/models';
import { fetchListingPhotos, uploadPhoto, deletePhoto } from '@/api/photos';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';

export function PhotoManager({ listingId }: { listingId: string }) {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    try {
      const data = await fetchListingPhotos(listingId);
      // PhotoViewSet.get_queryset() строится от Photo.all_objects и фильтрует только
      // listing__deleted_at, но не deleted_at самой фотографии — удалённые фото всё ещё приходят
      // в ответе. Отсекаем их здесь, иначе удаление выглядит как "не сработало".
      setPhotos(data.filter((p) => !p.is_deleted).sort((a, b) => a.photo_number - b.photo_number));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listingId]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;

    setError(null);
    setIsUploading(true);
    try {
      // photo_number должен быть уникален в рамках листинга (constraint unique_listing_photo_number,
      // максимум 50) — просто берём следующий свободный номер по порядку.
      // Photo.clean() проверяет уникальность номера только среди НЕудалённых фото (Photo.objects),
      // так что берём максимум среди видимых фото, а не среди всех когда-либо загруженных.
      const nextNumber = Math.max(0, ...photos.map((p) => p.photo_number)) + 1;
      const photo = await uploadPhoto(listingId, file, nextNumber);
      setPhotos((prev) => [...prev, photo]);
      toast.success('Фото загружено');
    } catch (err) {
      setError(parseApiError(err).message);
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deletePhoto(id);
      setPhotos((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      toast.error(parseApiError(err).message);
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-4">
        {photos.map((photo) => (
          <div key={photo.id} className="group relative aspect-square overflow-hidden rounded-lg bg-neutral-100">
            <img src={photo.photo} alt="" className="h-full w-full object-cover" />
            <button
              onClick={() => handleDelete(photo.id)}
              className="absolute right-1.5 top-1.5 rounded-full bg-white/90 p-1.5 text-red-600 opacity-0 shadow-sm transition-opacity group-hover:opacity-100"
              aria-label="Удалить фото"
            >
              <Trash2 size={14} />
            </button>
            <span className="absolute bottom-1.5 left-1.5 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-white">
              #{photo.photo_number}
            </span>
          </div>
        ))}

        {photos.length === 0 && (
          <div className="col-span-full flex flex-col items-center gap-2 py-6 text-neutral-300">
            <ImageOff size={28} />
            <span className="text-xs text-neutral-400">Фото пока нет</span>
          </div>
        )}
      </div>

      <ErrorAlert message={error} />

      <label className="btn-secondary inline-flex cursor-pointer !px-3 !py-2 text-sm">
        <Upload size={16} className="mr-2" />
        {isUploading ? 'Загрузка...' : 'Добавить фото'}
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp,image/heic,image/heif"
          onChange={handleUpload}
          disabled={isUploading || photos.length >= 50}
          className="hidden"
        />
      </label>
      <p className="text-xs text-neutral-400">До 2 МБ на файл, максимум 50 фото на объявление.</p>
    </div>
  );
}
