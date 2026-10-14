const HANGUL = /[\u1100-\u11ff\u3130-\u318f\uac00-\ud7af]/;
export const MISSING_FINNISH = 'Suomenkielinen teksti puuttuu. Luo luonnos uudelleen ennen hyväksymistä.';

export function containsHangul(value: unknown): boolean {
 return typeof value === 'string' && HANGUL.test(value);
}

export function finnishResultText(value: string | null | undefined): string {
 return value && containsHangul(value)
  ? MISSING_FINNISH
  : value ?? '';
}

export function FinnishResultText({text}:{text:string}) {
 return <span lang="fi">{finnishResultText(text)}</span>;
}
