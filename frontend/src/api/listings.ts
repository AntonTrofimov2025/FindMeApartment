import { apiClient } from '@/lib/apiClient';
import type { Listing, ListingCreateUpdatePayload, PaginatedResponse } from '@/types/models';

export interface ListingFilters {
  search?: string;
  city?: string;
  country?: number;
  property_type?: string;
  district?: string;
  // min_price/max_price считаются по цене со скидкой (price_per_night * discount)
  min_price?: number;
  max_price?: number;
  min_rooms?: number;
  max_rooms?: number;
  rooms?: number;
  // ListingFilter.guests — ChoiceFilter по MaxGuests с lookup 'gte': объекты, вмещающие НЕ МЕНЕЕ N гостей
  guests?: number;
  ordering?: string; // 'price_per_night' | '-price_per_night' | 'rooms' | 'created_at' | '-created_at'
  limit?: number;
  offset?: number;
}

export async function fetchListings(filters: ListingFilters = {}) {
  const { data } = await apiClient.get<PaginatedResponse<Listing>>('/listings/', { params: filters });
  return data;
}

export async function fetchListing(id: string) {
  const { data } = await apiClient.get<Listing>(`/listings/${id}/`);
  return data;
}

// ListingFilter (django-filter) не объявляет поле 'user' — отфильтровать "мои объявления" одним
// запросом нельзя. Зато get_queryset() у ListingViewSet для лендлорда и так возвращает
// Q(user=own) | Q(is_active=True), то есть все свои (включая скрытые) + чужие активные.
// Поэтому просто листаем страницы (лимит пагинатора — максимум 25) и фильтруем по user_id на клиенте.
export async function fetchAllMyListings(userId: string): Promise<Listing[]> {
  const mine: Listing[] = [];
  let offset = 0;
  const limit = 25;
  // защитный потолок в 10 страниц (250 объявлений на одного лендлорда с запасом)
  for (let page = 0; page < 10; page++) {
    const data = await fetchListings({ limit, offset, ordering: '-created_at' });
    mine.push(...data.results.filter((l) => l.user === userId));
    if (!data.next) break;
    offset += limit;
  }
  return mine;
}

export async function createListing(payload: ListingCreateUpdatePayload) {
  const { data } = await apiClient.post<Listing>('/listings/', payload);
  return data;
}

export async function updateListing(id: string, payload: Partial<ListingCreateUpdatePayload>) {
  const { data } = await apiClient.patch<Listing>(`/listings/${id}/`, payload);
  return data;
}

export async function deleteListing(id: string) {
  await apiClient.delete(`/listings/${id}/`);
}

export async function toggleListingActive(id: string) {
  const { data } = await apiClient.post<{ id: string; is_active: boolean; msg: string }>(`/listings/${id}/toggle/`);
  return data;
}
