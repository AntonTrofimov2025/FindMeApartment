import { useId } from 'react';
import type { ComponentType } from 'react';
import { LANGUAGES, useI18n } from '@/i18n';
import type { Lang } from '@/i18n';

/**
 * Флаги нарисованы inline-SVG, а не эмодзи: Windows не рендерит эмодзи-флаги (вместо 🇩🇪
 * показывает буквы «DE»), а картинки-файлы — лишние запросы. Все флаги в одной системе
 * координат 60×30 (пропорции британского флага), чтобы кнопки были одинаковыми.
 */
function FlagRu() {
  return (
    <>
      <rect width="60" height="10" fill="#fff" />
      <rect y="10" width="60" height="10" fill="#0039a6" />
      <rect y="20" width="60" height="10" fill="#d52b1e" />
    </>
  );
}

function FlagDe() {
  return (
    <>
      <rect width="60" height="10" fill="#000" />
      <rect y="10" width="60" height="10" fill="#dd0000" />
      <rect y="20" width="60" height="10" fill="#ffce00" />
    </>
  );
}

function FlagGb() {
  // useId нужен, потому что clipPath ищется по id во всём документе: два одинаковых id
  // (например, если переключатель отрисован дважды) ломают отрисовку диагоналей.
  const uid = useId().replace(/:/g, '');
  const outer = `gb-outer-${uid}`;
  const inner = `gb-inner-${uid}`;
  return (
    <>
      <defs>
        <clipPath id={outer}>
          <path d="M0,0 v30 h60 v-30 z" />
        </clipPath>
        <clipPath id={inner}>
          <path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${outer})`}>
        <path d="M0,0 v30 h60 v-30 z" fill="#012169" />
        <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" strokeWidth="6" />
        <path d="M0,0 L60,30 M60,0 L0,30" clipPath={`url(#${inner})`} stroke="#C8102E" strokeWidth="4" />
        <path d="M30,0 v30 M0,15 h60" stroke="#fff" strokeWidth="10" />
        <path d="M30,0 v30 M0,15 h60" stroke="#C8102E" strokeWidth="6" />
      </g>
    </>
  );
}

const FLAGS: Record<Lang, { title: string; flag: ComponentType }> = {
  // Название языка пишем на нём самом — так его узнает человек, не понимающий текущий язык UI.
  ru: { title: 'Русский', flag: FlagRu },
  de: { title: 'Deutsch', flag: FlagDe },
  en: { title: 'English (UK)', flag: FlagGb },
};

export function LanguageSwitcher() {
  const { lang, setLang, t } = useI18n();

  return (
    <div role="group" aria-label={t('common.language')} className="flex items-center gap-1">
      {LANGUAGES.map((code) => {
        const { title, flag: Flag } = FLAGS[code];
        const active = code === lang;
        return (
          <button
            key={code}
            type="button"
            onClick={() => setLang(code)}
            title={title}
            aria-label={title}
            aria-pressed={active}
            className={`rounded-[3px] p-0.5 transition ${
              active ? 'ring-2 ring-white' : 'opacity-60 hover:opacity-100 focus-visible:opacity-100'
            }`}
          >
            <svg viewBox="0 0 60 30" className="block h-4 w-8 rounded-[2px] shadow-sm" aria-hidden="true">
              <Flag />
            </svg>
          </button>
        );
      })}
    </div>
  );
}
