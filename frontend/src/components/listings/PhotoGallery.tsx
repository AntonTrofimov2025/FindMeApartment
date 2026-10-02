import { useState } from 'react';
import { ImageOff, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Photo } from '@/types/models';

export function PhotoGallery({ photos }: { photos: Photo[] }) {
  const sorted = [...photos].sort((a, b) => a.photo_number - b.photo_number);
  const [active, setActive] = useState(0);

  if (!sorted.length) {
    return (
      <div className="flex aspect-[16/9] w-full items-center justify-center rounded-xl2 bg-neutral-100 text-neutral-300">
        <ImageOff size={40} />
      </div>
    );
  }

  const go = (delta: number) => setActive((prev) => (prev + delta + sorted.length) % sorted.length);

  return (
    <div className="space-y-3">
      <div className="relative aspect-[16/9] w-full overflow-hidden rounded-xl2 bg-neutral-100">
        <img
          src={sorted[active].photo}
          alt={`Фото ${active + 1}`}
          className="h-full w-full object-cover transition-opacity duration-300"
        />
        {sorted.length > 1 && (
          <>
            <button
              onClick={() => go(-1)}
              className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md hover:bg-white"
              aria-label="Предыдущее фото"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              onClick={() => go(1)}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md hover:bg-white"
              aria-label="Следующее фото"
            >
              <ChevronRight size={18} />
            </button>
          </>
        )}
      </div>
      {sorted.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {sorted.map((photo, i) => (
            <button
              key={photo.id}
              onClick={() => setActive(i)}
              className={`h-16 w-24 shrink-0 overflow-hidden rounded-lg border-2 transition-colors ${
                i === active ? 'border-brand-500' : 'border-transparent opacity-70 hover:opacity-100'
              }`}
            >
              <img src={photo.photo} alt="" className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
