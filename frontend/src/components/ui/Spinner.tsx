import { useI18n } from '@/i18n';

export function Spinner({ size = 28 }: { size?: number }) {
  const { t } = useI18n();
  return (
    <div
      className="animate-spin rounded-full border-2 border-neutral-200 border-t-brand-500"
      style={{ width: size, height: size }}
      role="status"
      aria-label={t('common.loading')}
    />
  );
}
