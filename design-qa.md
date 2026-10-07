# Dashboard chart reference review — 2026-10-07

final result: passed

Scope: the user asked to **reference** the supplied mobile image while adding a six-area hexagon and seven-day graph to the existing application. This is an adaptation, not a pixel-identical recreation or a new mobile app. Existing login, roles, consent and navigation remain the product constraints.

- Source visual: `/var/folders/4_/phnbk0312kz78clxwhsnnj4h0000gn/T/codex-clipboard-d5052cc2-c5e2-4d87-9c29-4825dd4ae423.png` (944×1582 including phone bezel).
- Implementation: `/tmp/care-charts-390.png`, `/tmp/care-charts-360.png`, `/tmp/care-charts-1280.png`; screenshots of the chart section at 390/360/1280 CSS viewport widths, device scale 1. In-app Browser preview: `http://127.0.0.1:5179/family/residents/aino`.
- Reference and mobile/desktop implementation images opened together in the same comparison tool result. The reference phone frame is excluded conceptually; typography is evaluated in the chart section, not against bezel size. Different languages and record values are intentional. No 1:1 pixel fidelity claim.
- Focused comparison: topic cards (colored icon, soft fill, round ends), hexagon labels and daily axis. The supplied image has 3-day dots; the user explicitly requested 7 days and a polygon, so both are implemented as data graphics.

## Findings and iteration history

1. P2: initial mobile chart labels shrank with SVG width and were too small. Increased mobile radar label sizes and line-chart labels, reduced mobile date labels to alternate days while preserving all seven points and the complete data table. Removed fractional middle tick when the maximum is one. Re-captured all three widths; no remaining overlap or viewport overflow.
2. No remaining P0/P1/P2 findings. Horizontal scrolling is confined to the optional numeric table, where seven date columns remain readable.

## Required surfaces

- Typography: existing IBM Plex/system family retained; readable bold topic labels and distinct numeric values. Mobile graph labels enlarged after review.
- Layout: stacked colored cards and charts on mobile; 3×2 topic grid and side-by-side charts on desktop. Rounded 22–24px surfaces follow the reference rhythm.
- Colors: warm off-white background; orange meals, blue medication, green movement/outdoors, purple sleep, pink contact. Data totals never use color alone to communicate availability.
- Assets: Phosphor fill icons from the installed package. No fabricated portraits, decorative sun, or claims of identity; those reference assets are outside the requested visualization scope. SVG is used for functional data charts, not replacement illustration artwork.
- Content: actual approved/shared record counts, never inferred health improvement. Plans included and explicitly explained. Zero, not-shared, loading and connection failure states are distinct. fi/ko/en labels and manuals updated.

## Interaction and data checks

- In-app Browser: signed in as Liisa, six categories populated from 21 independent synthetic records created through the local API; selected outdoors and observed the changed line graph/selected card. Browser console errors: none.
- Repository E2E: filters, table, seven columns, 1280/390/360 widths, restricted Mikko scope and offline masking passed. Preview fixtures live only in temporary local DB, never deployed or passed off as real care activity.
- API tests: Helsinki date boundary, seven-day limits, approval/publication gating, current consent, role separation and invalidated evidence.

## Follow-up polish

None required for this scoped adaptation. Clinical scoring and generated daily summaries remain outside scope.
