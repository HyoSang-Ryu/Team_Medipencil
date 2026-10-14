import type {Language} from './UiLanguage';

/** Format date-only UI labels without changing API dates or their timezone. */
export function displayDate(value: unknown, language: Language): string {
 const text = value == null || value === '' ? '—' : String(value);
 const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
 return language === 'fi' && match ? `${match[3]}-${match[2]}-${match[1]}` : text;
}
