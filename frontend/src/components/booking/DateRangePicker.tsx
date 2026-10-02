import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { addYears } from 'date-fns';

interface DateRangePickerProps {
  dateFrom: Date | null;
  dateTo: Date | null;
  onChange: (dateFrom: Date | null, dateTo: Date | null) => void;
}

// Отражает бэковые границы из Booking.clean(): не в прошлом, не дальше 1 года вперёд,
// максимум 30 ночей за одно бронирование.
export function DateRangePicker({ dateFrom, dateTo, onChange }: DateRangePickerProps) {
  const today = new Date();
  const maxDate = addYears(today, 1);

  return (
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Заезд</label>
        <DatePicker
          selected={dateFrom}
          onChange={(date) => onChange(date, dateTo)}
          selectsStart
          startDate={dateFrom}
          endDate={dateTo}
          minDate={today}
          maxDate={maxDate}
          dateFormat="dd.MM.yyyy"
          placeholderText="Выберите дату"
          className="input"
        />
      </div>
      <div>
        <label className="mb-1 block text-xs font-medium text-neutral-500">Выезд</label>
        <DatePicker
          selected={dateTo}
          onChange={(date) => onChange(dateFrom, date)}
          selectsEnd
          startDate={dateFrom}
          endDate={dateTo}
          minDate={dateFrom ?? today}
          maxDate={maxDate}
          dateFormat="dd.MM.yyyy"
          placeholderText="Выберите дату"
          className="input"
        />
      </div>
    </div>
  );
}
