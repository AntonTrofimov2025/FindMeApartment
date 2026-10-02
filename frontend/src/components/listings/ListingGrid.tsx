import type { Listing } from '@/types/models';
import { ListingCard } from './ListingCard';
import { Spinner } from '@/components/ui/Spinner';

interface ListingGridProps {
  listings: Listing[];
  isLoading: boolean;
}

export function ListingGrid({ listings, isLoading }: ListingGridProps) {
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner size={36} />
      </div>
    );
  }

  // Защита на случай аномального ответа (например, сеть отдала не тот Content-Type) —
  // чтобы не ронять всё дерево белым экраном, а просто показать пустое состояние.
  if (!listings?.length) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-2 text-neutral-400">
        <p className="text-lg font-medium">Ничего не найдено</p>
        <p className="text-sm">Попробуйте изменить параметры фильтра</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {listings.map((listing) => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </div>
  );
}
