import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { addYears } from 'date-fns';
import { useI18n } from '@/i18n';

interface DateRangePickerProps {
  dateFrom: Date | null;
  dateTo: Date | null;
  onChange: (dateFrom: Date | null, dateTo: Date | null) => void;
}

// Формат даты в поле ввода под язык интерфейса (локали date-fns зарегистрированы в src/i18n).
const DATE_FORMAT = { ru: 'dd.MM.yyyy', de: 'dd.MM.yyyy', en: 'dd/MM/yyyy' } as const;

// Отражает бэковые границы из Booking.clean(): не в прошлом, не дальше 1 года вперёд,
// максимум 30 ночей за одно бронирование.
export function DateRangePicker({ dateFrom, dateTo, onChange }: DateRangePickerProps) {
  const { t, lang } = useI18n();
  const today = new Date();
  const maxDate = addYears(today, 1);

  return (
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">{t('dates.checkIn')}</label>
        <DatePicker
          selected={dateFrom}
          onChange={(date) => onChange(date, dateTo)}
          selectsStart
          startDate={dateFrom}
          endDate={dateTo}
          minDate={today}
          maxDate={maxDate}
          locale={lang}
          dateFormat={DATE_FORMAT[lang]}
          placeholderText={t('dates.placeholder')}
          className="input"
        />
      </div>
      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">{t('dates.checkOut')}</label>
        <DatePicker
          selected={dateTo}
          onChange={(date) => onChange(dateFrom, date)}
          selectsEnd
          startDate={dateFrom}
          endDate={dateTo}
          minDate={dateFrom ?? today}
          maxDate={maxDate}
          locale={lang}
          dateFormat={DATE_FORMAT[lang]}
          placeholderText={t('dates.placeholder')}
          className="input"
        />
      </div>
    </div>
  );
}
