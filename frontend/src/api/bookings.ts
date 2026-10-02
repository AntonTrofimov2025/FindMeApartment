import { apiClient } from '@/lib/apiClient';
import type { Booking, BookingCreatePayload, PaginatedResponse } from '@/types/models';

export interface BookingFilters {
  booking_status?: string;
  listing?: string;
  ordering?: string;
  limit?: number;
  offset?: number;
}

export async function fetchMyBookings(filters: BookingFilters = {}) {
  // get_queryset() в BookingViewSet сам сужает выборку до "свои" (tenant) / "по своим листингам" (landlord)
  const { data } = await apiClient.get<PaginatedResponse<Booking>>('/bookings/', { params: filters });
  return data;
}

export async function fetchBooking(id: string) {
  const { data } = await apiClient.get<Booking>(`/bookings/${id}/`);
  return data;
}

// Только create — update/partial_update на бэке заперты под IsAdminUser (BookingViewSet.get_permissions),
// поэтому "изменение" бронирования обычным пользователем на фронте всегда идёт через action-эндпоинты ниже.
export async function createBooking(payload: BookingCreatePayload) {
  const { data } = await apiClient.post<Booking>('/bookings/', payload);
  return data;
}

export async function approveBooking(id: string) {
  const { data } = await apiClient.post<{ msg: string }>(`/bookings/${id}/approve/`);
  return data;
}

export async function rejectBooking(id: string) {
  const { data } = await apiClient.post<{ msg: string }>(`/bookings/${id}/reject/`);
  return data;
}

export async function cancelBooking(id: string) {
  const { data } = await apiClient.post<{ msg: string }>(`/bookings/${id}/cancel/`);
  return data;
}

export async function checkInBooking(id: string) {
  const { data } = await apiClient.post<{ msg: string }>(`/bookings/${id}/check_in/`);
  return data;
}

export interface LandlordAnalytics {
  // total_earnings — сумма total_price по CONFIRMED + CHECKED_IN + COMPLETED
  financials: { total_earnings: number; currency: string };
  counters: {
    total_bookings: number;
    pending: number;
    confirmed: number;
    checked_in: number;
    completed: number;
    cancelled: number;
  };
  // Несмотря на название, active_properties_count на бэке — это число объектов, по которым была
  // хотя бы одна бронь (distinct listing в бронированиях), а не число активных объявлений.
  performance: { active_properties_count: number; properties_ids: string[] };
}

// Эндпоинт защищён IsLandLord (группа Landlord или staff), поэтому он же служит надёжной
// проверкой роли: 200 — лендлорд, 403 — нет. UserListSerializer группы не отдаёт.
export async function fetchLandlordAnalytics() {
  const { data } = await apiClient.get<LandlordAnalytics>('/bookings/analytics/');
  return data;
}
