// One API and data model; separate build-time visual variants for comparison.
export const isXdDesign=import.meta.env.VITE_MEDIPENCIL_DESIGN==='xd';
// The XD family dashboard is enabled in both release builds; the flag preserves baseline local tests.
export const isSungahFamilyScreen=import.meta.env.VITE_MEDIPENCIL_SUNGAH_FAMILY_SCREEN==='1';
