import { useMemo, useSyncExternalStore } from 'react';
import { registerLocale } from 'react-datepicker';
import { de as dfDe, enGB as dfEn, ru as dfRu } from 'date-fns/locale';
import type { Locale } from 'date-fns';
import { ru } from './messages/ru';
import { en } from './messages/en';
import { de } from './messages/de';
import type { Messages, PluralForms, PluralKey, StringKey, Vars } from './types';
import { COUNTRY_ISO } from '@/types/choices';

/**
 * Лёгкая i18n без внешних зависимостей (не нужно трогать package-lock.json).
 * Язык хранится в модуле, а не только в React-контексте, потому что он нужен и вне компонентов:
 * axios-перехватчик шлёт его в Accept-Language (Django LocaleMiddleware переводит ответы API),
 * а parseApiError() подбирает язык сообщений об ошибках.
 */
export const LANGUAGES = ['ru', 'de', 'en'] as const;
export type Lang = (typeof LANGUAGES)[number];

const STORAGE_KEY = 'fma_lang';
const DICTIONARIES: Record<Lang, Messages> = { ru, en, de };
const INTL_LOCALE: Record<Lang, string> = { ru: 'ru-RU', de: 'de-DE', en: 'en-GB' };
const DATE_LOCALE: Record<Lang, Locale> = { ru: dfRu, de: dfDe, en: dfEn };

// react-datepicker берёт названия месяцев и дней недели из зарегистрированных локалей date-fns.
registerLocale('ru', dfRu);
registerLocale('de', dfDe);
registerLocale('en', dfEn);

function isLang(value: unknown): value is Lang {
  return typeof value === 'string' && (LANGUAGES as readonly string[]).includes(value);
}

function detectInitialLang(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (isLang(saved)) return saved;
  } catch {
    /* localStorage может быть недоступен (приватный режим) — просто идём дальше */
  }
  const browser = (navigator.language || '').slice(0, 2).toLowerCase();
  // Бэкенд по умолчанию отдаёт английский (LANGUAGE_CODE = 'en-us'), поэтому и тут fallback — en.
  return isLang(browser) ? browser : 'en';
}

let currentLang: Lang = detectInitialLang();
document.documentElement.lang = currentLang;
const listeners = new Set<() => void>();

export function getLang(): Lang {
  return currentLang;
}

export function setLang(lang: Lang) {
  if (lang === currentLang) return;
  currentLang = lang;
  document.documentElement.lang = lang;
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* без сохранения язык просто сбросится при перезагрузке */
  }
  listeners.forEach((notify) => notify());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function interpolate(template: string, vars?: Vars): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name: string) => (name in vars ? String(vars[name]) : match));
}

export function translate(key: StringKey, vars?: Vars, lang: Lang = currentLang): string {
  const value = (DICTIONARIES[lang][key] ?? ru[key]) as string;
  return interpolate(value, vars);
}

export function translatePlural(key: PluralKey, n: number, vars?: Vars, lang: Lang = currentLang): string {
  const forms = DICTIONARIES[lang][key] as PluralForms;
  const category = new Intl.PluralRules(INTL_LOCALE[lang]).select(n);
  const template = (forms as unknown as Record<string, string | undefined>)[category] ?? forms.other;
  return interpolate(template, { n, ...vars });
}

export function formatMoney(value: number, currency = 'EUR', lang: Lang = currentLang): string {
  return new Intl.NumberFormat(INTL_LOCALE[lang], {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

const regionNamesCache = new Map<Lang, Intl.DisplayNames | null>();

// Названия стран берём из самого браузера (Intl.DisplayNames по ISO-коду), а не держим
// 56 × 3 переводов вручную. Если браузер не умеет DisplayNames — показываем ISO-код.
export function countryName(numericCode: number, lang: Lang = currentLang): string {
  const iso = COUNTRY_ISO[numericCode];
  if (!iso) return `#${numericCode}`;
  if (!regionNamesCache.has(lang)) {
    try {
      regionNamesCache.set(lang, new Intl.DisplayNames([INTL_LOCALE[lang]], { type: 'region' }));
    } catch {
      regionNamesCache.set(lang, null);
    }
  }
  return regionNamesCache.get(lang)?.of(iso) ?? iso;
}

/** Хук подписывает компонент на смену языка; всё, что зависит от языка, берётся отсюда. */
export function useI18n() {
  const lang = useSyncExternalStore(subscribe, getLang, getLang);
  return useMemo(
    () => ({
      lang,
      setLang,
      t: (key: StringKey, vars?: Vars) => translate(key, vars, lang),
      tn: (key: PluralKey, n: number, vars?: Vars) => translatePlural(key, n, vars, lang),
      money: (value: number, currency?: string) => formatMoney(value, currency, lang),
      country: (numericCode: number) => countryName(numericCode, lang),
      dateLocale: DATE_LOCALE[lang],
      intlLocale: INTL_LOCALE[lang],
    }),
    [lang],
  );
}

export type { StringKey, PluralKey };
