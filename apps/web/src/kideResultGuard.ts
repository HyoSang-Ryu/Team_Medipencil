// Provider text fields must contain prose, never serialized payloads or code blocks.
// Structured objects such as metrics are still valid; this checks their text leaves.
export function hasSerializedText(value:unknown):boolean{
 if(typeof value==='string'){try{const parsed=JSON.parse(value);if(parsed&&typeof parsed==='object')return true;}catch{/* Ordinary prose. */}return /(?:^|\n)\s*(?:```(?:json)?\s*|[\[{]\s*(?:[\[{]|"[^"]+"\s*:))/.test(value);}
 if(Array.isArray(value))return value.some(hasSerializedText);
 return !!value&&typeof value==='object'&&Object.values(value).some(hasSerializedText);
}
export function requireReadableResult(value:unknown){
 if(hasSerializedText(value))throw new Error('KIDE_UNREADABLE_RESULT');
 return value;
}
