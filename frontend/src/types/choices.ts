/**
 * Зеркало `apps/core/models.py`: PropertyType / RoomCount / MaxGuests / StatusChoices / Countries.
 * Здесь хранятся только ЗНАЧЕНИЯ — они должны 1-в-1 совпадать с бэкендом. Подписи на нужном
 * языке берутся из словарей i18n (ключи строят функции *Key ниже), названия стран — из
 * Intl.DisplayNames по ISO-коду.
 */

export const PROPERTY_TYPES = ['apartment', 'studio', 'house', 'townhouse', 'room', 'loft'] as const;
export type PropertyType = (typeof PROPERTY_TYPES)[number];
export const propertyTypeKey = (type: PropertyType) => `propertyType.${type}` as const;

// property_type, для которых apartment_number ОБЯЗАТЕЛЕН (см. Listing.clean())
export const APARTMENT_NUMBER_REQUIRED: PropertyType[] = ['apartment', 'room'];
// property_type, для которых apartment_number ЗАПРЕЩЁН
export const APARTMENT_NUMBER_FORBIDDEN: PropertyType[] = ['house', 'studio'];

export const ROOM_COUNTS = [0, 1, 2, 3, 4, 5] as const;
export type RoomCount = (typeof ROOM_COUNTS)[number];
export const roomOptionKey = (rooms: RoomCount) => `rooms.option.${rooms}` as const;

export const MAX_GUESTS_OPTIONS = Array.from({ length: 10 }, (_, i) => i + 1); // 1..10

export const BOOKING_STATUSES = ['pending', 'confirmed', 'checked_in', 'completed', 'cancelled', 'rejected'] as const;
export type BookingStatus = (typeof BOOKING_STATUSES)[number];
export const statusKey = (status: BookingStatus) => `status.${status}` as const;

export function isBookingStatus(value: string): value is BookingStatus {
  return (BOOKING_STATUSES as readonly string[]).includes(value);
}

export const STATUS_COLORS: Record<BookingStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  confirmed: 'bg-emerald-100 text-emerald-800',
  checked_in: 'bg-sky-100 text-sky-800',
  completed: 'bg-neutral-200 text-neutral-800',
  cancelled: 'bg-red-100 text-red-700',
  rejected: 'bg-red-100 text-red-700',
};

// Countries(IntegerChoices) хранит числовые коды ISO 3166-1; для Intl.DisplayNames нужен alpha-2.
export const COUNTRY_ISO: Record<number, string> = {
  31: 'AZ', 51: 'AM', 156: 'CN', 268: 'GE', 356: 'IN', 360: 'ID', 376: 'IL', 392: 'JP',
  398: 'KZ', 417: 'KG', 458: 'MY', 410: 'KR', 158: 'TW', 762: 'TJ', 764: 'TH', 792: 'TR',
  795: 'TM', 784: 'AE', 860: 'UZ', 704: 'VN',
  40: 'AT', 112: 'BY', 56: 'BE', 100: 'BG', 196: 'CY', 203: 'CZ', 208: 'DK', 246: 'FI',
  250: 'FR', 276: 'DE', 300: 'GR', 348: 'HU', 372: 'IE', 380: 'IT', 498: 'MD', 528: 'NL',
  578: 'NO', 616: 'PL', 620: 'PT', 642: 'RO', 643: 'RU', 688: 'RS', 724: 'ES', 752: 'SE',
  756: 'CH', 804: 'UA', 826: 'GB',
  32: 'AR', 76: 'BR', 124: 'CA', 484: 'MX', 840: 'US',
  36: 'AU', 818: 'EG', 554: 'NZ', 710: 'ZA',
};

export const COUNTRY_CODES: number[] = Object.keys(COUNTRY_ISO).map(Number);
export const DEFAULT_COUNTRY = 276; // Countries.GERMANY — значение по умолчанию на бэке
