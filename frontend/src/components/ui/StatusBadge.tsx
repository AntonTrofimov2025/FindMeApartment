import { bookingStatusMeta } from '@/types/choices';

export function StatusBadge({ status }: { status: string }) {
  const meta = bookingStatusMeta(status);
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${meta.color}`}>
      {meta.label}
    </span>
  );
}
