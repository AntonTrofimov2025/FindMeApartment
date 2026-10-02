import type { BookingStatus, PropertyType } from './choices';

/** === users/serializers/users.py === */

// UserListSerializer — то, что отдаёт GET /users/me/ и /users/{id}/
export interface User {
  id: string; // UUID
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  birth_date: string | null; // 'YYYY-MM-DD'
  avatar: string | null; // абсолютный/относительный URL до /media/...
  bookings: string[]; // UUID-ы связанных бронирований (reverse FK, read-only)
  listings: string[]; // UUID-ы связанных объявлений (reverse FK, read-only)
  phone: string | null;
  last_login: string | null;
  date_joined: string;
  updated_at: string;
  is_deleted: boolean;
  deleted_at: string | null;
}

// Payload для PATCH /users/me/ — только то, что реально разрешает RegisterUserSerializer,
// БЕЗ password/re_password: этот путь на бэке меняет пароль без проверки текущего
// (RegisterUserSerializer.update() просто делает instance.set_password(value)) и не
// инвалидирует старые сессии — использовать его для смены пароля небезопасно. Настоящая
// смена пароля — через changePassword() (POST /users/me/, ChangePasswordSerializer).
export interface ProfileUpdatePayload {
  username?: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string | null;
  phone?: string | null;
  avatar?: File | null;
}

// ChangePasswordSerializer (apps/users/serializers/users.py) — POST /users/me/.
// Требует текущий пароль и текущий refresh (который сервер тут же блэклистит и заменяет
// на новую пару токенов — старые сессии по этому refresh больше не восстановить).
export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
  re_new_password: string;
  refresh: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  re_password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  birth_date?: string | null; // валидируется validate_birth_date_age: 18..120 лет
  phone?: string | null; // либо null, либо строго /^\+\d{10,75}$/
}

/** === listings/serializers/listings.py === */

// ListingSerializer — GET /listings/, GET /listings/{id}/ (с рассчитанными полями)
export interface Listing {
  id: string;
  title: string;
  user: string; // UUID владельца (landlord)
  description: string;
  country: number; // код из Countries(IntegerChoices)
  district: string;
  city: string;
  street: string;
  house_number: string;
  property_type: PropertyType;
  discount: string; // Decimal как строка, напр. "0.85" (0.85 = скидка 15%)
  overall_rating: number; // strict float, читай core-контракт: Round(Avg(...), 2) или 0.0
  apartment_number: string | null;
  max_guests: number;
  price_per_night: string; // Decimal-строка
  final_price_per_night: string; // Decimal-строка, ТОЛЬКО в ListingSerializer (не в create/update!)
  rooms: number;
  // ListingSerializer теперь встраивает фото инлайн (PhotoSerializer(many=True, read_only=True))
  // через reverse-related manager Photo.objects (с учётом soft-delete) — отдельный запрос
  // к /photos/?listing=<id> для отображения больше не нужен, он остаётся только для CRUD
  // (загрузка/удаление) в дашборде лендлорда.
  photos: Photo[];
  // Теперь в ListingSerializer.fields (раньше отсутствовало) — но всё ещё read_only и в
  // ListingSerializer, и в ListingCreateUpdateSerializer: менять можно только через
  // POST /listings/{id}/toggle/, напрямую в payload create/update отправлять нельзя.
  is_active: boolean;
  is_deleted: boolean;
  deleted_at: string | null;
}

// ListingCreateUpdateSerializer — payload для POST/PUT/PATCH /listings/
// ВАЖНО: final_price_per_night тут нет — это read-only calculated property,
// её не отправляем и не ждём в ответе на create/update.
export interface ListingCreateUpdatePayload {
  title: string;
  description: string;
  country: number;
  district: string;
  city: string;
  street: string;
  house_number: string;
  property_type: PropertyType;
  discount: string;
  apartment_number?: string | null;
  max_guests: number;
  price_per_night: string;
  rooms: number;
}

/** === listings/serializers/photos.py === */

export interface Photo {
  id: string;
  listing: string;
  photo: string; // URL к файлу в /media/listings/<id>/...
  photo_number: number;
  is_deleted: boolean;
  deleted_at: string | null;
}

/** === bookings/serializers/bookings.py === */

// birth_date из снапшота убран на бэке (Booking.save()) — хозяину дата рождения гостя не нужна.
export interface SnapshotTenant {
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
}

export interface SnapshotProperty {
  title: string;
  country: string;
  district: string;
  city: string;
  street: string;
  house_number: string;
  apartment_number: string;
  max_guests: string;
  property_type: string;
  price_per_night: string;
  discount: string;
  rooms: string;
}

export interface SnapshotBookingDetails {
  date_from: string;
  date_to: string;
  nights: string;
  guests_number: string;
}

// Иммутабельный снимок, зафиксированный в Booking.save() на момент создания/изменения дат.
export interface BookingSnapshot {
  Tenant?: SnapshotTenant;
  property_data?: SnapshotProperty;
  booking_details?: SnapshotBookingDetails;
  total_price?: string;
}

export interface Booking {
  id: string;
  listing: string; // UUID
  user: string; // UUID
  date_from: string;
  date_to: string;
  booking_status: BookingStatus;
  guests_number: number;
  snapshot_data: BookingSnapshot;
  total_price: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  deleted_at: string | null;
}

// BookingCreateUpdateSerializer — на практике используется только под create
// (update/partial_update на бэке защищены IsAdminUser, обычный юзер их не может дёргать —
// изменение бронирования идёт через /approve /reject /cancel /check_in).
export interface BookingCreatePayload {
  listing: string;
  date_from: string; // 'YYYY-MM-DD'
  date_to: string;
  guests_number: number;
}

/** === reviews/serializers/reviews.py === */

export interface Review {
  id: string;
  booking: string; // UUID, строго OneToOne
  property_rating: number; // 1..5
  location_rating: number; // 1..5
  text: string;
  created_at: string;
  is_deleted: boolean;
  deleted_at: string | null;
}

export interface ReviewCreatePayload {
  booking: string;
  property_rating: number;
  location_rating: number;
  text: string;
}

/** Пагинация: apps/core/paginators/common.py — LimitOffsetPagination, лимит по умолчанию 10, максимум 25 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
