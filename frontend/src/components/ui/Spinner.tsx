export function Spinner({ size = 28 }: { size?: number }) {
  return (
    <div
      className="animate-spin rounded-full border-2 border-neutral-200 border-t-brand-500"
      style={{ width: size, height: size }}
      role="status"
      aria-label="Загрузка"
    />
  );
}
