/**
 * Зеркало `apps/core/models.py`: Countries / PropertyType / RoomCount / MaxGuests / StatusChoices.
 * Значения (числовые коды стран, коды статусов и т.д.) должны 1-в-1 совпадать с бэкендом,
 * иначе выбор в форме улетит на сервер как невалидный choice.
 */

export const PROPERTY_TYPES = [
  { value: 'apartment', label: 'Апартаменты' },
  { value: 'studio', label: 'Студия' },
  { value: 'house', label: 'Дом' },
  { value: 'townhouse', label: 'Таунхаус' },
  { value: 'room', label: 'Комната' },
  { value: 'loft', label: 'Лофт' },
] as const;

export type PropertyType = (typeof PROPERTY_TYPES)[number]['value'];

// property_type, для которых apartment_number ОБЯЗАТЕЛЕН (см. Listing.clean())
export const APARTMENT_NUMBER_REQUIRED: PropertyType[] = ['apartment', 'room'];
// property_type, для которых apartment_number ЗАПРЕЩЁН
export const APARTMENT_NUMBER_FORBIDDEN: PropertyType[] = ['house', 'studio'];

export const ROOM_COUNTS = [
  { value: 0, label: '0 комнат (студия/лофт)' },
  { value: 1, label: '1 комната' },
  { value: 2, label: '2 комнаты' },
  { value: 3, label: '3 комнаты' },
  { value: 4, label: '4 комнаты' },
  { value: 5, label: '5+ комнат' },
] as const;

export const MAX_GUESTS_OPTIONS = Array.from({ length: 10 }, (_, i) => i + 1); // 1..10

export const BOOKING_STATUSES = [
  { value: 'pending', label: 'Ожидает подтверждения', color: 'bg-amber-100 text-amber-800' },
  { value: 'confirmed', label: 'Подтверждено', color: 'bg-emerald-100 text-emerald-800' },
  { value: 'checked_in', label: 'Заселение состоялось', color: 'bg-sky-100 text-sky-800' },
  { value: 'completed', label: 'Завершено', color: 'bg-neutral-200 text-neutral-800' },
  { value: 'cancelled', label: 'Отменено', color: 'bg-red-100 text-red-700' },
  { value: 'rejected', label: 'Отклонено', color: 'bg-red-100 text-red-700' },
] as const;

export type BookingStatus = (typeof BOOKING_STATUSES)[number]['value'];

export function bookingStatusMeta(status: string) {
  return (
    BOOKING_STATUSES.find((s) => s.value === status) ?? {
      value: status,
      label: status,
      color: 'bg-neutral-100 text-neutral-700',
    }
  );
}

// Полный список стран из Countries(IntegerChoices) в apps/core/models.py.
export const COUNTRIES: { value: number; label: string }[] = [
  { value: 31, label: 'Азербайджан' },
  { value: 51, label: 'Армения' },
  { value: 156, label: 'Китай' },
  { value: 268, label: 'Грузия' },
  { value: 356, label: 'Индия' },
  { value: 360, label: 'Индонезия' },
  { value: 376, label: 'Израиль' },
  { value: 392, label: 'Япония' },
  { value: 398, label: 'Казахстан' },
  { value: 417, label: 'Киргизия' },
  { value: 458, label: 'Малайзия' },
  { value: 410, label: 'Южная Корея' },
  { value: 158, label: 'Тайвань' },
  { value: 762, label: 'Таджикистан' },
  { value: 764, label: 'Таиланд' },
  { value: 792, label: 'Турция' },
  { value: 795, label: 'Туркменистан' },
  { value: 784, label: 'ОАЭ' },
  { value: 860, label: 'Узбекистан' },
  { value: 704, label: 'Вьетнам' },
  { value: 40, label: 'Австрия' },
  { value: 112, label: 'Беларусь' },
  { value: 56, label: 'Бельгия' },
  { value: 100, label: 'Болгария' },
  { value: 196, label: 'Кипр' },
  { value: 203, label: 'Чехия' },
  { value: 208, label: 'Дания' },
  { value: 246, label: 'Финляндия' },
  { value: 250, label: 'Франция' },
  { value: 276, label: 'Германия' },
  { value: 300, label: 'Греция' },
  { value: 348, label: 'Венгрия' },
  { value: 372, label: 'Ирландия' },
  { value: 380, label: 'Италия' },
  { value: 498, label: 'Молдова' },
  { value: 528, label: 'Нидерланды' },
  { value: 578, label: 'Норвегия' },
  { value: 616, label: 'Польша' },
  { value: 620, label: 'Португалия' },
  { value: 642, label: 'Румыния' },
  { value: 643, label: 'Россия' },
  { value: 688, label: 'Сербия' },
  { value: 724, label: 'Испания' },
  { value: 752, label: 'Швеция' },
  { value: 756, label: 'Швейцария' },
  { value: 804, label: 'Украина' },
  { value: 826, label: 'Великобритания' },
  { value: 32, label: 'Аргентина' },
  { value: 76, label: 'Бразилия' },
  { value: 124, label: 'Канада' },
  { value: 484, label: 'Мексика' },
  { value: 840, label: 'США' },
  { value: 36, label: 'Австралия' },
  { value: 818, label: 'Египет' },
  { value: 554, label: 'Новая Зеландия' },
  { value: 710, label: 'ЮАР' },
];

export function countryLabel(code: number): string {
  return COUNTRIES.find((c) => c.value === code)?.label ?? `Страна #${code}`;
}
