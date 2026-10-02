import { apiClient } from '@/lib/apiClient';
import type { PaginatedResponse, Photo } from '@/types/models';

export async function fetchListingPhotos(listingId: string) {
  // ListingSerializer не отдаёт фото инлайн — тянем их отдельным запросом к /photos/?listing=<id>
  const { data } = await apiClient.get<PaginatedResponse<Photo>>('/photos/', {
    params: { listing: listingId, limit: 50, ordering: 'created_at' },
  });
  return data.results;
}

export async function uploadPhoto(listingId: string, file: File, photoNumber: number) {
  const form = new FormData();
  form.append('listing', listingId);
  form.append('photo', file);
  form.append('photo_number', String(photoNumber));
  const { data } = await apiClient.post<Photo>('/photos/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function deletePhoto(id: string) {
  await apiClient.delete(`/photos/${id}/`);
}
