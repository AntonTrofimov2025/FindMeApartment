import { useI18n } from '@/i18n';
import { isBookingStatus, STATUS_COLORS, statusKey } from '@/types/choices';

export function StatusBadge({ status }: { status: string }) {
  const { t } = useI18n();
  // Неизвестный статус (бэк добавил новый, а фронт ещё не обновлён) показываем как есть — серым.
  const known = isBookingStatus(status);
  const color = known ? STATUS_COLORS[status] : 'bg-neutral-100 text-neutral-700';
  const label = known ? t(statusKey(status)) : status;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${color}`}>
      {label}
    </span>
  );
}
