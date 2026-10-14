// One API and data model; separate build-time visual variants for comparison.
export const isXdDesign=import.meta.env.VITE_MEDIPENCIL_DESIGN==='xd';
// This screen is built into the Sungah release only. GitHub Pages keeps its current design.
export const isSungahFamilyScreen=import.meta.env.VITE_MEDIPENCIL_SUNGAH_FAMILY_SCREEN==='1';
