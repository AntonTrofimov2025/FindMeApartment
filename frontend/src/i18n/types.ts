import type { ru } from './messages/ru';

/**
 * Формы множественного числа по категориям Intl.PluralRules.
 * Русскому нужны one / few / many (1 ночь, 2 ночи, 5 ночей); немецкому и английскому
 * хватает one / other, поэтому few и many необязательны — при их отсутствии берётся other.
 */
export interface PluralForms {
  one: string;
  few?: string;
  many?: string;
  other: string;
}

type Source = typeof ru;

/** Русский словарь — эталон: в en и de обязаны быть ровно те же ключи (проверяет TypeScript). */
export type Messages = { [K in keyof Source]: Source[K] extends string ? string : PluralForms };

export type StringKey = { [K in keyof Source]: Source[K] extends string ? K : never }[keyof Source];
export type PluralKey = Exclude<keyof Source, StringKey>;

export type Vars = Record<string, string | number>;
