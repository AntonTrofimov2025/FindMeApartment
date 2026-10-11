import { useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import type { Listing, ListingCreateUpdatePayload } from '@/types/models';
import { createListing, updateListing } from '@/api/listings';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { parseApiError } from '@/lib/errors';
import {
  APARTMENT_NUMBER_FORBIDDEN,
  APARTMENT_NUMBER_REQUIRED,
  COUNTRY_CODES,
  DEFAULT_COUNTRY,
  MAX_GUESTS_OPTIONS,
  PROPERTY_TYPES,
  ROOM_COUNTS,
  propertyTypeKey,
  roomOptionKey,
  type PropertyType,
} from '@/types/choices';
import { useI18n } from '@/i18n';

interface ListingFormProps {
  listing?: Listing; // если передан — режим редактирования (PATCH), иначе создание (POST)
  onSaved: (listing: Listing) => void;
}

type FormState = {
  title: string;
  description: string;
  country: number;
  district: string;
  city: string;
  street: string;
  house_number: string;
  apartment_number: string;
  property_type: PropertyType;
  discount: string;
  max_guests: number;
  price_per_night: string;
  rooms: number;
};

function initialState(listing?: Listing): FormState {
  return {
    title: listing?.title ?? '',
    description: listing?.description ?? '',
    country: listing?.country ?? DEFAULT_COUNTRY, // Germany по умолчанию, как и на бэке (Countries.GERMANY)
    district: listing?.district ?? '',
    city: listing?.city ?? '',
    street: listing?.street ?? '',
    house_number: listing?.house_number ?? '',
    apartment_number: listing?.apartment_number ?? '',
    property_type: listing?.property_type ?? 'apartment',
    discount: listing?.discount ?? '1',
    max_guests: listing?.max_guests ?? 2,
    price_per_night: listing?.price_per_night ?? '',
    rooms: listing?.rooms ?? 1,
  };
}

export function ListingForm({ listing, onSaved }: ListingFormProps) {
  const [form, setForm] = useState<FormState>(initialState(listing));
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const { t, country, intlLocale } = useI18n();

  // Страны сортируем по названию на текущем языке, иначе список выглядит случайным.
  const countryOptions = useMemo(
    () =>
      COUNTRY_CODES.map((code) => ({ code, name: country(code) })).sort((a, b) =>
        a.name.localeCompare(b.name, intlLocale),
      ),
    [country, intlLocale],
  );

  const apartmentRequired = APARTMENT_NUMBER_REQUIRED.includes(form.property_type);
  const apartmentForbidden = APARTMENT_NUMBER_FORBIDDEN.includes(form.property_type);

  function set<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    // Зеркалим Listing.clean(): для apartment/room номер квартиры обязателен,
    // для house/studio — запрещён. Проверяем на клиенте, чтобы не гонять запрос впустую,
    // но финальное слово всё равно за full_clean() на бэке.
    if (apartmentRequired && !form.apartment_number.trim()) {
      setFieldErrors({ apartment_number: t('listingForm.apartmentRequiredError') });
      return;
    }

    setIsSaving(true);
    try {
      const payload: ListingCreateUpdatePayload = {
        title: form.title,
        description: form.description,
        country: form.country,
        district: form.district,
        city: form.city,
        street: form.street,
        house_number: form.house_number,
        apartment_number: apartmentForbidden ? null : form.apartment_number || null,
        property_type: form.property_type,
        discount: form.discount,
        max_guests: form.max_guests,
        price_per_night: form.price_per_night,
        rooms: form.rooms,
      };

      const saved = listing ? await updateListing(listing.id, payload) : await createListing(payload);
      toast.success(listing ? t('listingForm.updated') : t('listingForm.created'));
      onSaved(saved);
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.generalMessage);
      setFieldErrors(parsed.fieldErrors);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field label={t('listingForm.title')} value={form.title} error={fieldErrors.title} onChange={(v) => set('title', v)} required />

      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.description')}</label>
        <textarea
          value={form.description}
          onChange={(e) => set('description', e.target.value)}
          rows={3}
          required
          className="input resize-none"
        />
        {fieldErrors.description && <p className="mt-1 text-xs text-red-600">{fieldErrors.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.propertyType')}</label>
          <select
            value={form.property_type}
            onChange={(e) => set('property_type', e.target.value as PropertyType)}
            className="input"
          >
            {PROPERTY_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(propertyTypeKey(type))}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.rooms')}</label>
          <select value={form.rooms} onChange={(e) => set('rooms', Number(e.target.value))} className="input">
            {ROOM_COUNTS.map((r) => (
              <option key={r} value={r}>
                {t(roomOptionKey(r))}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.country')}</label>
          <select value={form.country} onChange={(e) => set('country', Number(e.target.value))} className="input">
            {countryOptions.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <Field label={t('listingForm.city')} value={form.city} error={fieldErrors.city} onChange={(v) => set('city', v)} required />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field label={t('listingForm.district')} value={form.district} error={fieldErrors.district} onChange={(v) => set('district', v)} required />
        <Field label={t('listingForm.street')} value={form.street} error={fieldErrors.street} onChange={(v) => set('street', v)} required />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field label={t('listingForm.houseNumber')} value={form.house_number} error={fieldErrors.house_number}
          onChange={(v) => set('house_number', v)} required />
        <div>
          <Field
            label={
              t('listingForm.apartmentNumber') +
              t(
                apartmentRequired
                  ? 'listingForm.apartmentRequired'
                  : apartmentForbidden
                    ? 'listingForm.apartmentForbidden'
                    : 'listingForm.apartmentOptional',
              )
            }
            value={form.apartment_number}
            error={fieldErrors.apartment_number}
            disabled={apartmentForbidden}
            onChange={(v) => set('apartment_number', v)}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Field label={t('listingForm.price')} type="number" value={form.price_per_night} error={fieldErrors.price_per_night}
          onChange={(v) => set('price_per_night', v)} required />
        <div>
          <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.discount')}</label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            max="1"
            value={form.discount}
            onChange={(e) => set('discount', e.target.value)}
            className={`input ${fieldErrors.discount ? 'border-red-400' : ''}`}
          />
          <p className="mt-1 text-xs text-neutral-400">{t('listingForm.discountHint')}</p>
          {fieldErrors.discount && <p className="mt-1 text-xs text-red-600">{fieldErrors.discount}</p>}
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-neutral-500">{t('listingForm.maxGuests')}</label>
          <select value={form.max_guests} onChange={(e) => set('max_guests', Number(e.target.value))} className="input">
            {MAX_GUESTS_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </div>
      </div>

      <ErrorAlert message={error} />

      <button type="submit" disabled={isSaving} className="btn-primary w-full">
        {isSaving ? t('listingForm.saving') : listing ? t('listingForm.save') : t('listingForm.create')}
      </button>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  error,
  type = 'text',
  required,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  type?: string;
  required?: boolean;
  disabled?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-neutral-500">{label}</label>
      <input
        type={type}
        required={required}
        disabled={disabled}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`input ${error ? 'border-red-400' : ''} ${disabled ? 'bg-neutral-100 text-neutral-400' : ''}`}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
