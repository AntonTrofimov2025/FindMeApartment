import { AxiosError } from 'axios';

/**
 * Формат ответа CustomDRFStandardizedErrorsExceptionHandler (apps/core/exceptions.py) —
 * подкласс ExceptionHandler из drf-standardized-errors, переопределяющий только
 * convert_known_exceptions() для перехвата Django ValidationError из full_clean(). Итоговый
 * JSON-контракт не изменился:
 * {
 *   "type": "validation_error" | "client_error" | "server_error",
 *   "errors": [
 *     { "code": "invalid", "detail": "Unfortunately the selected dates are already booked.", "attr": null }
 *   ]
 * }
 * "attr" может указывать на конкретное поле (напр. "date_from"), либо быть null для
 * ошибок общей валидации (clean()/full_clean() на уровне модели — как раз наш overlap-кейс).
 */
export interface StandardizedApiError {
  code: string;
  detail: string;
  attr: string | null;
}

export interface StandardizedErrorResponse {
  type: 'validation_error' | 'client_error' | 'server_error';
  errors: StandardizedApiError[];
}

const NON_FIELD_ATTRS = new Set(['__all__', 'non_field_errors', 'detail']);

export interface ParsedApiError {
  /** Всегда непустое сообщение — годится для toast'а. */
  message: string;
  /** Только общие (не привязанные к полю) ошибки — для ErrorAlert над кнопкой формы. */
  generalMessage: string | null;
  fieldErrors: Record<string, string>;
}

export function parseApiError(error: unknown): ParsedApiError {
  const fallbackMessage = 'Что-то пошло не так. Попробуйте ещё раз.';
  const simple = (message: string): ParsedApiError => ({ message, generalMessage: message, fieldErrors: {} });

  if (!(error instanceof AxiosError)) return simple(fallbackMessage);

  const data = error.response?.data as StandardizedErrorResponse | undefined;
  if (!data?.errors?.length) {
    if (!error.response) return simple('Сервер недоступен. Проверьте подключение к сети.');
    if (error.response.status === 401) return simple('Сессия истекла. Пожалуйста, войдите снова.');
    if (error.response.status === 403) return simple('Недостаточно прав для этого действия.');
    if (error.response.status === 404) return simple('Ресурс не найден.');
    return simple(fallbackMessage);
  }

  const fieldErrors: Record<string, string> = {};
  const generalMessages: string[] = [];

  for (const e of data.errors) {
    // Ошибки из Model.clean(), поднятые строкой (а не словарём), после full_clean() приходят
    // как {'__all__': [...]} -> attr="__all__"; ошибки validate() сериализатора без поля —
    // как attr="non_field_errors". Это общие ошибки формы, а не ошибки конкретного поля.
    if (e.attr && !NON_FIELD_ATTRS.has(e.attr)) {
      // attr может быть вложенным (напр. "tenant.phone") — берём последний сегмент
      const key = e.attr.includes('.') ? e.attr.split('.').pop()! : e.attr;
      fieldErrors[key] = e.detail;
    } else {
      generalMessages.push(e.detail);
    }
  }

  const generalMessage = generalMessages.length ? generalMessages.join(' ') : null;
  const message = generalMessage ?? data.errors[0]?.detail ?? fallbackMessage;

  return { message, generalMessage, fieldErrors };
}
