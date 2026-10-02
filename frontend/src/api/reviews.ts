import { apiClient } from '@/lib/apiClient';
import type { PaginatedResponse, Review, ReviewCreatePayload } from '@/types/models';

export async function fetchReviewsForListing(listingId: string) {
  const { data } = await apiClient.get<PaginatedResponse<Review>>('/reviews/', {
    params: { 'booking__listing': listingId, limit: 25, ordering: '-created_at' },
  });
  return data;
}

// ReviewViewSet.filterset_fields теперь включает 'booking': ['exact'] — можно узнать,
// есть ли уже отзыв на конкретную бронь, одним запросом, без session-only трекинга.
// OneToOne на booking гарантирует не более одного результата.
export async function fetchReviewByBooking(bookingId: string): Promise<Review | null> {
  const { data } = await apiClient.get<PaginatedResponse<Review>>('/reviews/', {
    params: { booking: bookingId, limit: 1 },
  });
  return data.results[0] ?? null;
}

export async function createReview(payload: ReviewCreatePayload) {
  // Бэк дополнительно проверит: booking.user === request.user, booking.booking_status === COMPLETED,
  // и что отзыва на этот booking ещё не существует (строгий OneToOne) — все три ошибки прилетят
  // как generic 400 с attr=null, см. parseApiError().
  const { data } = await apiClient.post<Review>('/reviews/', payload);
  return data;
}

export async function updateReview(id: string, payload: Partial<ReviewCreatePayload>) {
  // Разрешено объект-level пермишеном IsReviewAuthorOrAdmin: автор отзыва (booking.user) или staff.
  const { data } = await apiClient.patch<Review>(`/reviews/${id}/`, payload);
  return data;
}

export async function deleteReview(id: string) {
  await apiClient.delete(`/reviews/${id}/`);
}
