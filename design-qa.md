# Adobe XD local adaptation QA — 2026-10-12

Scope: apply the supplied visual system to the existing working care-loop PoC, local only. This is not a pixel-identical reproduction or a new production deployment.

## Visual evidence
- Source visual truth: https://xd.adobe.com/view/286725f5-3afb-4089-b35c-8e906ed53f58-7d34/ — all seven artboards opened and captured in the in-app browser (CUA tab 7). Main, family/staff login, family overview, today detail, evidence modal, period detail.
- Implementation: http://127.0.0.1:8778/ (CUA tab 8). Browser screenshots captured in this task for desktop login, staff login, overview, detail, modal, history and mobile. Captures are inline conversation evidence; no standalone screenshot files were exported.
- Reference artboard is 1920px wide, displayed at 51.7% (approximately 993px wide) within the 1280×720 XD viewer. Implementation checked at 1280×720, 1920×1080 and 390×844 CSS viewports. Source image and implementation screenshots were returned together for main/login and history comparisons. Compared artboard content after accounting for viewer padding and 0.517 scaling, not surrounding Adobe chrome. No pixel-diff or exact font measurement claimed.
- Same Finnish navigation states used for source comparison. Implementation data is current-day synthetic, source is older-day synthetic: availability/status and comparison expansion differ intentionally. Korean mobile view also checked.

## Findings and iterations
- P1 fixed: legacy profile crop enlarged standalone portraits. Reset standalone image to object-fit cover inside circular slot.
- P2 fixed: staff login secondary text too dark on charcoal. Set explicit light foreground.
- P2 fixed: publication-language control squeezed detail tabs into remaining width. Position beside profile and clear tabs to full width; mobile returns to normal flow.
- P2 fixed: legacy summary/accordion spacing overwhelmed period view. Period comparison replaces today's lead; compact accordion rows, period selector and day cards appear before topic entries.
- Main comparison: same centered 1000px content, full-width pale living-room photo, left resident card, adjacent sky-blue/charcoal login panels, white header/footer.
- Detail comparison: blue navigation strip, four tabs, white resident card, pale-blue status/comparison, two-column records, gray outline source button, centered white source modal.
- Focused checks: text on both login panels, source-modal body/close button, portrait crop, tabs/date selector alignment. Icons use existing Phosphor library.
- Colors: #4cb3ef accent, #3d474d staff panel, #e8f6fd info. Dark text on blue retained for readability instead of low-contrast small white text.
- Typography: Arial/system Korean fallback, preserving live translated copy. No external font loaded.
- Imagery: generated replacement hero (xd-care-hero.png), source background original unavailable. Existing persona portraits retained. This is an explicit local-preview adaptation, not original XD asset extraction.

## Interactions / verification
- Real local API + isolated SQLite: staff login → synthetic EMR import → direct/manual draft → simulated reviewer check → approve → publish → logout → guardian login → published records visible. No real AI used; not Finnish expert review.
- Guardian overview/detail navigation, 7-day period selection (2026-10-06 through 2026-10-12), family-confirmation tab and source modal opened; Escape closes dialog and native dialog restores focus.
- Mobile 390px Korean detail and Finnish login: no horizontal overflow (document width 390). Default 1280px also no overflow.
- Browser console error query returned none. TypeScript PASS, Vitest 19 PASS, production build PASS (existing bundler directives warnings).
- Full Playwright CLI suite not run for this visual iteration; browser verification performed through CUA. Backend/permissions unchanged.

## Follow-up polish
- P3: replace generated hero with designer-provided original if supplied; exact XD font/asset export would improve fidelity.
- Preserve visible PoC provenance, translation labels and actual data states even where static XD omits them.

final result: passed
