// Only an explicit wake-name + terminal command ends a session. Never a partial hypothesis.
const endCommand=/(?:kide|키데|키드)[,，:!\s]*(?:정리해\s*줘|정리해\s*주세요|summari[sz]e(?:\s+please)?|tee\s+yhteenveto)[.!?\s]*$/i;
export function hasKideCommand(text:string){return endCommand.test(text.trim());}
export function removeKideCommand(text:string){return text.trim().replace(endCommand,'').trim();}
